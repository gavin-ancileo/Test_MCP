"""
OAuth Integrations for AAP Platform - FIXED VERSION
Supports: GitHub, Jira, Google Drive
Features:
- Persistent state storage (PostgreSQL)
- User authentication (Cognito)
- Dynamic redirect URIs based on environment
- Proper error handling and logging
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Header
from fastapi.responses import RedirectResponse
import httpx
import os
from typing import Dict, Optional
from datetime import datetime
import secrets
import json
import logging
import inspect

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/integrations", tags=["integrations"])

# ============================================
# OAUTH CONFIGURATIONS
# ============================================

OAUTH_CONFIGS = {
    "github": {
        "client_id": os.getenv("GITHUB_CLIENT_ID", ""),
        "client_secret": os.getenv("GITHUB_CLIENT_SECRET", ""),
        "authorize_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "redirect_uri": "https://internal.assistant.leacare.ai/integrations/callback/github" if os.getenv('ENVIRONMENT') in ['prod', 'uat'] else "http://localhost/integrations/callback/github",
        "scopes": ["repo", "user", "read:org", "write:org"],  # Full repo access + org read/write access
        "user_info_url": "https://api.github.com/user"
    },
    "jira": {
        "client_id": os.getenv("JIRA_CLIENT_ID", ""),
        "client_secret": os.getenv("JIRA_CLIENT_SECRET", ""),
        "authorize_url": "https://auth.atlassian.com/authorize",
        "token_url": "https://auth.atlassian.com/oauth/token",
        "redirect_uri": "https://internal.assistant.leacare.ai/integrations/callback/jira" if os.getenv('ENVIRONMENT') in ['prod', 'uat'] else "http://localhost/integrations/callback/jira",
        # Classic scopes - Jira API automatically enforces user permissions when using user's token
        # If user tokens are used correctly, these scopes respect end-user's access level
        # Granular scopes (read:issue:jira, write:issue:jira, etc.) are optional but provide finer-grained control
        "scopes": ["read:jira-work", "write:jira-work", "read:jira-user"],
        "user_info_url": "https://api.atlassian.com/me"
    },
    "google_drive": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET", ""),
        "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "redirect_uri": "https://internal.assistant.leacare.ai/integrations/callback/google" if os.getenv('ENVIRONMENT') in ['prod', 'uat'] else "http://localhost/integrations/callback/google",
        "scopes": [
            "https://www.googleapis.com/auth/drive",  # Full access: read + write + shared
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile"
        ],
        "user_info_url": "https://www.googleapis.com/oauth2/v2/userinfo"
    }
}

# MCP Server URL
# Local: http://mcp-server:8001 (Docker Compose)
# ECS: http://mcp-server.aap.local:8001 (Service Discovery - namespace: aap.local)
# Use same MCP_URL as app.py for consistency
MCP_URL = os.getenv('MCP_URL', 'http://mcp-server.aap.local:8001')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'local')
print(f"[OAuth-MCP] MCP Server URL: {MCP_URL}")
print(f"[OAuth-MCP] Environment: {ENVIRONMENT}")

# Lazy import get_current_user to avoid circular import
# Use callable wrapper to resolve dependency at runtime, not decoration time
class GetCurrentUserDependency:
    """
    Callable wrapper for get_current_user dependency.
    Resolves the actual function at runtime, not at decorator evaluation time.
    This fixes the issue where Depends(get_current_user) would capture None.

    IMPORTANT: The __call__ method signature MUST MATCH the injected function's signature
    so that FastAPI can properly inject dependencies (like Header).
    """
    def __init__(self):
        self._func = None

    def set_func(self, func):
        """Called by app.py to inject the actual get_current_user function"""
        self._func = func
        # Copy the signature from the injected function so FastAPI can inspect it
        self.__signature__ = inspect.signature(func)

    async def __call__(self, *args, **kwargs) -> Dict:
        """
        FastAPI calls this at runtime to resolve the dependency.
        We accept *args/**kwargs and pass them through to the injected function.
        This allows FastAPI to inject Header() and other dependencies properly.
        """
        if self._func is None:
            raise RuntimeError("get_current_user dependency not injected by app.py")
        return await self._func(*args, **kwargs)

# Create instance that will be used in Depends()
get_current_user = GetCurrentUserDependency()

# ============================================
# HELPER FUNCTIONS
# ============================================

async def save_oauth_state(state: str, user_id: str, user_email: str, provider: str) -> bool:
    """Save OAuth state to database"""
    try:
        print(f"[OAuth-MCP] [Loading] Saving OAuth state for {provider}...")
        print(f"[OAuth-MCP] URL: {MCP_URL}/oauth/state/save")
        print(f"[OAuth-MCP] User: {user_email}")

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{MCP_URL}/oauth/state/save",
                json={
                    'state': state,
                    'user_id': user_id,
                    'user_email': user_email,
                    'provider': provider
                }
            )

            if response.status_code == 200:
                print(f"[OAuth-MCP] [OK] OAuth state saved successfully")
                return True
            else:
                print(f"[OAuth-MCP] [WARNING] Failed to save OAuth state: {response.status_code}")
                return False

    except httpx.ConnectError as e:
        logger.error(f"[OAuth-MCP] [ERROR] CONNECTION ERROR: Cannot connect to MCP server at {MCP_URL}")
        logger.error(f"[OAuth-MCP] [ERROR] Error details: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    except httpx.TimeoutException as e:
        logger.error(f"[OAuth-MCP] [ERROR] TIMEOUT ERROR: MCP server did not respond within 10s")
        logger.error(f"[OAuth-MCP] [ERROR] Error details: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        logger.error(f"[OAuth-MCP] [ERROR] Failed to save OAuth state: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

async def get_oauth_state(state: str) -> Optional[Dict]:
    """Get OAuth state from database (DO NOT delete - let callback delete after successful token exchange)"""
    try:
        print(f"[OAuth-MCP] [Loading] Retrieving OAuth state...")
        print(f"[OAuth-MCP] URL: {MCP_URL}/oauth/state/{state[:20]}...")

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{MCP_URL}/oauth/state/{state}")

            if response.status_code == 200:
                print(f"[OAuth-MCP] [OK] OAuth state retrieved successfully")
                # DO NOT delete here - state will be deleted in callback after successful token exchange
                # This prevents race condition where state is deleted before callback completes
                return response.json()
            elif response.status_code == 404:
                logger.warning(f"[OAuth-MCP] [WARNING] OAuth state not found or expired: {state[:20]}...")
                return None
            else:
                logger.error(f"[OAuth-MCP] [WARNING] Failed to get OAuth state: {response.status_code} - {response.text}")
                return None

    except httpx.ConnectError as e:
        logger.error(f"[OAuth-MCP] [ERROR] CONNECTION ERROR: Cannot connect to MCP server at {MCP_URL}")
        logger.error(f"[OAuth-MCP] [ERROR] Error details: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
    except httpx.TimeoutException as e:
        logger.error(f"[OAuth-MCP] [ERROR] TIMEOUT ERROR: MCP server did not respond within 10s")
        logger.error(f"[OAuth-MCP] [ERROR] Error details: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
    except Exception as e:
        logger.error(f"[OAuth-MCP] [ERROR] Failed to get OAuth state: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None

async def get_provider_user_info(provider: str, access_token: str) -> Dict:
    """Get user info from OAuth provider"""
    config = OAUTH_CONFIGS.get(provider)
    if not config:
        return {}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {"Authorization": f"Bearer {access_token}"}

            # Special handling for Jira - skip the /me endpoint, use accessible-resources directly
            if provider == "jira":
                # First get accessible resources to find cloudId
                resources_response = await client.get(
                    "https://api.atlassian.com/oauth/token/accessible-resources",
                    headers=headers
                )

                if resources_response.status_code != 200:
                    logger.error(f"Failed to get Jira resources: {resources_response.status_code} - {resources_response.text}")
                    return {}

                resources = resources_response.json()
                if not resources:
                    logger.error("No accessible Jira resources found")
                    return {}

                # Use first resource (site)
                cloud_id = resources[0].get('id')
                instance_url = resources[0].get('url')  # e.g., "https://ancileo.atlassian.net"
                site_name = resources[0].get('name')    # e.g., "Ancileo"

                # Get current user from that site
                myself_response = await client.get(
                    f"https://api.atlassian.com/ex/jira/{cloud_id}/rest/api/3/myself",
                    headers=headers
                )

                if myself_response.status_code != 200:
                    logger.error(f"Failed to get Jira user: {myself_response.status_code} - {myself_response.text}")
                    return {}

                user_data = myself_response.json()
                return {
                    'id': user_data.get('accountId'),
                    'email': user_data.get('emailAddress'),
                    'name': user_data.get('displayName'),
                    'username': user_data.get('displayName', '').split()[0] if user_data.get('displayName') else user_data.get('emailAddress', '').split('@')[0],
                    # Add Jira instance metadata
                    'cloudId': cloud_id,
                    'instance_url': instance_url,
                    'site_url': instance_url,  # Alias for compatibility
                    'site_name': site_name
                }

            # For other providers, call the user_info_url
            response = await client.get(config['user_info_url'], headers=headers)

            if response.status_code != 200:
                logger.error(f"{provider} user info failed: {response.status_code} - {response.text}")
                return {}

            data = response.json()

            # Normalize response based on provider
            if provider == "github":
                return {
                    'id': str(data.get('id')),
                    'email': data.get('email'),
                    'name': data.get('name'),
                    'username': data.get('login')
                }
            elif provider == "google_drive":
                return {
                    'id': data.get('id'),
                    'email': data.get('email'),
                    'name': data.get('name'),
                    'username': data.get('email', '').split('@')[0]
                }

            return data
    except Exception as e:
        logger.error(f"Error getting {provider} user info: {e}")
        return {}

# ============================================
# OAUTH ENDPOINTS
# ============================================

@router.get("/connect/{provider}")
async def connect_integration(provider: str, user: Dict = Depends(get_current_user)):
    """
    Initiate OAuth flow for a provider
    FIXED: Now requires authentication and uses consistent user_id
    """
    # Map frontend provider names to backend provider names
    provider_mapping = {"drive": "google_drive"}
    actual_provider = provider_mapping.get(provider, provider)

    if actual_provider not in OAUTH_CONFIGS:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")

    config = OAUTH_CONFIGS[actual_provider]

    # Validate config
    if not config['client_id'] or not config['client_secret']:
        raise HTTPException(
            status_code=500,
            detail=f"{provider} OAuth credentials not configured. Please set environment variables."
        )

    # CRITICAL: Ensure user_id is consistent
    # Use the user_id from get_current_user (which handles FORCE_ADMIN_MODE)
    user_id = user['sub']
    user_email = user['email']
    
    logger.info(f"OAuth connect initiated for provider={provider}, user_id={user_id}, user_email={user_email}")

    # Generate secure state token
    state = secrets.token_urlsafe(32)

    # Save state to database (persistent, not in-memory)
    saved = await save_oauth_state(
        state=state,
        user_id=user_id,
        user_email=user_email,
        provider=actual_provider
    )

    if not saved:
        raise HTTPException(
            status_code=500,
            detail="Failed to initialize OAuth flow. Please try again."
        )

    # Build authorization URL with proper parameters
    params = {
        'client_id': config['client_id'],
        'redirect_uri': config['redirect_uri'],
        'state': state,
        'response_type': 'code',
    }

    # Provider-specific parameters
    if actual_provider == "github":
        params['scope'] = ' '.join(config['scopes'])
        # GitHub OAuth behavior:
        # - If user already authorized this app, GitHub auto-approves without showing screen
        # - GitHub doesn't support prompt=consent like Google OAuth
        # - When disconnect is called, we now revoke the access token, so next connect will show consent screen
        # - This ensures users can re-authorize with organization access if needed
        # Note: We revoke token on disconnect, so next connect will show consent screen for re-authorization
    elif actual_provider == "jira":
        params['audience'] = 'api.atlassian.com'
        params['scope'] = ' '.join(config['scopes'])
        params['prompt'] = 'consent'
    elif actual_provider == "google_drive":
        params['scope'] = ' '.join(config['scopes'])
        params['access_type'] = 'offline'
        params['prompt'] = 'consent'

    # Build query string
    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    auth_url = f"{config['authorize_url']}?{query_string}"

    logger.info(f"OAuth flow initiated for {actual_provider} by user {user['email']}")

    return {
        "authorization_url": auth_url,
        "state": state,
        "provider": provider
    }


@router.get("/callback/{provider}")
async def oauth_callback(
    provider: str,
    code: str = Query(...),
    state: str = Query(...),
    error: Optional[str] = Query(None),
    error_description: Optional[str] = Query(None)
):
    """
    OAuth callback endpoint
    FIXED: Uses persistent state storage and proper error handling
    """
    logger.info(f"OAuth callback received for provider: {provider}, state: {state[:20]}..., error: {error}")
    
    # Map callback provider names to config provider names
    # Google redirects to /callback/google but we use google_drive internally
    provider_mapping = {"google": "google_drive"}
    actual_provider = provider_mapping.get(provider, provider)
    logger.info(f"Mapped provider '{provider}' to actual provider '{actual_provider}'")

    # Check for OAuth errors
    if error:
        logger.error(f"OAuth error for {actual_provider}: {error} - {error_description}")
        # Extract base URL from redirect_uri (remove /integrations/callback/...)
        base_url = OAUTH_CONFIGS[actual_provider]['redirect_uri'].replace('/integrations/callback/', '/')
        return RedirectResponse(
            url=f"{base_url}?integration={provider}&status=error&error={error}"
        )

    # Validate and retrieve state
    state_data = await get_oauth_state(state)

    if not state_data:
        logger.error(f"Invalid or expired OAuth state for {actual_provider}: {state[:20]}...")
        raise HTTPException(status_code=400, detail="Invalid or expired OAuth state")

    user_id = state_data.get('user_id')
    user_email = state_data.get('user_email')
    logger.info(f"OAuth state validated for user_id: {user_id}, user_email: {user_email}")
    
    # Delete state AFTER successful token exchange to prevent race condition
    # Don't delete here - delete after token exchange succeeds
    # This prevents state from being deleted before callback completes

    config = OAUTH_CONFIGS[actual_provider]

    # Exchange authorization code for access token
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            token_data = {
                'client_id': config['client_id'],
                'client_secret': config['client_secret'],
                'code': code,
                'redirect_uri': config['redirect_uri'],
                'grant_type': 'authorization_code'
            }

            headers = {'Accept': 'application/json'}

            response = await client.post(config['token_url'], data=token_data, headers=headers)

            if response.status_code != 200:
                logger.error(f"Token exchange failed for {actual_provider}: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Token exchange failed: {response.text[:200]}"
                )

            token_response = response.json()
            
            # Delete state AFTER successful token exchange
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    delete_response = await client.delete(f"{MCP_URL}/oauth/state/{state}")
                    if delete_response.status_code in [200, 204]:
                        logger.info(f"OAuth state deleted after successful token exchange: {state[:20]}...")
                    else:
                        logger.warning(f"Failed to delete OAuth state (non-critical): {delete_response.status_code}")
            except Exception as e:
                logger.warning(f"Failed to delete OAuth state (non-critical): {e}")
                
    except httpx.TimeoutException:
        logger.error(f"Timeout during token exchange for {actual_provider}")
        raise HTTPException(status_code=504, detail="OAuth provider timeout")
    except Exception as e:
        logger.error(f"Token exchange error for {actual_provider}: {e}")
        raise HTTPException(status_code=500, detail=f"Token exchange failed: {str(e)}")

    access_token = token_response.get('access_token')
    refresh_token = token_response.get('refresh_token')

    if not access_token:
        logger.error(f"No access token received from {actual_provider}")
        raise HTTPException(status_code=500, detail="No access token received from provider")

    logger.info(f"Successfully received access token from {actual_provider} (token length: {len(access_token) if access_token else 0})")

    # Get provider user info
    provider_user_info = await get_provider_user_info(actual_provider, access_token)

    if not provider_user_info:
        logger.warning(f"Could not retrieve user info from {actual_provider}")
    else:
        logger.info(f"Got provider user info for {actual_provider}: {provider_user_info}")

    # Save integration to database
    logger.info(f"Attempting to save integration to MCP server at {MCP_URL}/integrations/save")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            save_payload = {
                'user_id': user_id,
                'user_email': user_email,
                'provider': actual_provider,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'scope': token_response.get('scope'),  # Save granted scope
                'provider_user_info': provider_user_info
            }
            logger.info(f"Saving integration with payload: user_id={user_id}, provider={actual_provider}, user_email={user_email}")
            
            save_response = await client.post(
                f"{MCP_URL}/integrations/save",
                json=save_payload
            )

            logger.info(f"MCP server response status: {save_response.status_code}")
            if save_response.status_code != 200:
                logger.error(f"Failed to save integration: {save_response.status_code} - {save_response.text}")
                raise HTTPException(status_code=500, detail=f"Failed to save integration: {save_response.text[:200]}")
            
            logger.info(f"Successfully saved integration to MCP server")
    except httpx.TimeoutException:
        logger.error(f"Timeout connecting to MCP server at {MCP_URL}")
        raise HTTPException(status_code=504, detail="Timeout saving integration to MCP server")
    except Exception as e:
        logger.error(f"Error saving integration: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to save integration: {str(e)}")

    logger.info(f"Successfully connected {actual_provider} for user {user_email}")

    # Redirect back to dashboard with success message
    # Map internal provider name back to frontend name
    display_provider = "drive" if actual_provider == "google_drive" else actual_provider
    
    # Use correct base URL based on environment
    if ENVIRONMENT in ['prod', 'uat']:
        base_url = "https://internal.assistant.leacare.ai"
    else:
        base_url = "http://localhost"
    
    redirect_url = f"{base_url}/chat?integration={display_provider}&status=success"
    logger.info(f"Redirecting to: {redirect_url}")

    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=redirect_url, status_code=302)


@router.get("/status")
async def get_integration_status(user: Dict = Depends(get_current_user)):
    """
    Get user's connected integrations
    FIXED: Now returns actual data from database
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{MCP_URL}/integrations/user/{user['sub']}")

            if response.status_code == 200:
                data = response.json()
                # Convert list to dict keyed by provider
                integrations_dict = {}
                for integration in data.get("integrations", []):
                    provider = integration.get("provider")
                    # Map google_drive -> drive for frontend compatibility
                    if provider == "google_drive":
                        provider = "drive"
                        integration["provider"] = "drive"
                    integrations_dict[provider] = integration

                return {"integrations": integrations_dict}
            else:
                logger.error(f"Failed to get integrations: {response.status_code}")
                return {"integrations": {}}
    except Exception as e:
        logger.error(f"Error getting integration status: {e}")
        return {"integrations": {}}


@router.delete("/{provider}")
async def disconnect_integration(provider: str, user: Dict = Depends(get_current_user)):
    """
    Disconnect an integration
    FIXED: Uses real user_id from authentication + Revokes GitHub token to force re-authorization
    """
    # Map frontend provider names to backend provider names
    provider_mapping = {"drive": "google_drive"}
    actual_provider = provider_mapping.get(provider, provider)

    try:
        # STEP 1: Get current integration to retrieve access token (needed for revocation)
        async with httpx.AsyncClient(timeout=10.0) as client:
            get_response = await client.get(f"{MCP_URL}/integrations/{user['sub']}/{actual_provider}")

            access_token = None
            if get_response.status_code == 200:
                integration_data = get_response.json()
                access_token = integration_data.get('access_token')
                logger.info(f"Retrieved access token for {actual_provider} revocation")
            else:
                logger.warning(f"Could not retrieve integration data for revocation: {get_response.status_code}")

        # STEP 2: Revoke token at provider (GitHub only for now)
        if actual_provider == "github" and access_token:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    config = OAUTH_CONFIGS["github"]
                    # GitHub OAuth Apps: DELETE /applications/{client_id}/token
                    # https://docs.github.com/en/rest/apps/oauth-applications#delete-an-app-token
                    revoke_response = await client.delete(
                        f"https://api.github.com/applications/{config['client_id']}/token",
                        auth=(config['client_id'], config['client_secret']),
                        json={"access_token": access_token}
                    )

                    if revoke_response.status_code in [204, 200]:
                        logger.info(f"✅ Successfully revoked GitHub token for user {user['email']}")
                    else:
                        logger.warning(f"⚠️ GitHub token revocation returned {revoke_response.status_code}: {revoke_response.text}")
            except Exception as revoke_error:
                # Non-critical: Continue with disconnect even if revocation fails
                logger.warning(f"⚠️ Failed to revoke GitHub token (non-critical): {revoke_error}")

        # STEP 3: Delete integration from database
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.delete(f"{MCP_URL}/integrations/{user['sub']}/{actual_provider}")

            if response.status_code == 200:
                logger.info(f"Disconnected {provider} for user {user['email']}")
                return {"success": True, "provider": provider}
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to disconnect")
    except Exception as e:
        logger.error(f"Error disconnecting {provider}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to disconnect: {str(e)}")


@router.get("/health")
async def integration_health():
    """Health check endpoint for OAuth integration service"""
    configured_providers = [
        provider for provider, config in OAUTH_CONFIGS.items()
        if config['client_id'] and config['client_secret']
    ]

    return {
        "status": "healthy",
        "environment": ENVIRONMENT,
        "configured_providers": configured_providers,
        "mcp_url": MCP_URL
    }
