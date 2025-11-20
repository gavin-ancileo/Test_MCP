"""
Authentication service
Handles Cognito JWT token verification and user authentication
"""

import requests
import time
import httpx
from typing import Dict, Optional
from fastapi import HTTPException, Header
from jose import jwt, JWTError
from config import CONFIG

# Global variable to cache keys
COGNITO_KEYS = []
COGNITO_KEYS_LAST_REFRESH = None
COGNITO_KEYS_REFRESH_INTERVAL = 300  # Refresh every 5 minutes

# Token cache to avoid re-verifying same token multiple times
# Format: {token_hash: (user_dict, expiry_timestamp)}
TOKEN_CACHE = {}
TOKEN_CACHE_TTL = 300  # Cache tokens for 5 minutes


def get_cognito_keys_for_pool(user_pool_id: str = None):
    """Get Cognito keys for a specific User Pool ID"""
    region = CONFIG.get('COGNITO_REGION')
    pool_id = user_pool_id or CONFIG.get('COGNITO_USER_POOL_ID')
    if not pool_id:
        return []
    keys_url = f"https://cognito-idp.{region}.amazonaws.com/{pool_id}/.well-known/jwks.json"
    try:
        response = requests.get(keys_url, timeout=5)
        response.raise_for_status()
        keys = response.json().get('keys', [])
        print(f"[get_cognito_keys_for_pool] Loaded {len(keys)} keys from User Pool: {pool_id}")
        return keys
    except Exception as e:
        print(f"[get_cognito_keys_for_pool] Error loading keys for pool {pool_id}: {e}")
        return []


def get_cognito_keys():
    """Get Cognito keys from configured User Pool ID"""
    return get_cognito_keys_for_pool()


def refresh_cognito_keys(force: bool = False):
    """Refresh Cognito keys from JWKS endpoint"""
    global COGNITO_KEYS, COGNITO_KEYS_LAST_REFRESH
    current_time = time.time()
    
    # Only refresh if last refresh was more than 5 minutes ago (unless forced)
    if not force and COGNITO_KEYS_LAST_REFRESH and (current_time - COGNITO_KEYS_LAST_REFRESH) < COGNITO_KEYS_REFRESH_INTERVAL:
        print(f"[refresh_cognito_keys] Skipping refresh - last refresh was {(current_time - COGNITO_KEYS_LAST_REFRESH):.0f}s ago")
        return
    
    print(f"[refresh_cognito_keys] Refreshing Cognito keys... (force={force})")
    user_pool_id = CONFIG.get('COGNITO_USER_POOL_ID', '')
    print(f"[refresh_cognito_keys] Loading keys for User Pool: {user_pool_id}")
    new_keys = get_cognito_keys()
    if new_keys:
        COGNITO_KEYS = new_keys
        COGNITO_KEYS_LAST_REFRESH = current_time
        print(f"[refresh_cognito_keys] Keys refreshed successfully - {len(COGNITO_KEYS)} keys available")
        print(f"[refresh_cognito_keys] Available kids: {[k.get('kid') for k in COGNITO_KEYS]}")
    else:
        print(f"[refresh_cognito_keys] Failed to refresh keys, keeping existing keys")


def verify_jwt_token(token: str) -> Dict:
    """Verify JWT token and return user info"""
    global COGNITO_KEYS
    try:
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get('kid')

        # Decode token without verification to check issuer
        token_user_pool_id = None
        try:
            unverified_payload = jwt.decode(token, key="", options={"verify_signature": False})
            token_issuer = unverified_payload.get('iss', '')
            token_user_pool_id = token_issuer.split('/')[-1] if '/' in token_issuer else ''
            configured_user_pool_id = CONFIG.get('COGNITO_USER_POOL_ID', '')

            if token_user_pool_id and configured_user_pool_id and token_user_pool_id != configured_user_pool_id:
                # Load keys from token's User Pool
                keys_from_token_pool = get_cognito_keys_for_pool(token_user_pool_id)
                if keys_from_token_pool:
                    COGNITO_KEYS = keys_from_token_pool
        except Exception:
            pass  # Silently continue with configured pool
        
        if not kid:
            print(f"[verify_jwt_token] No kid in token header")
            raise HTTPException(status_code=401, detail="Token missing 'kid' in header")
        
        key = next((k for k in COGNITO_KEYS if k.get('kid') == kid), None)
        if not key:
            # Try loading from token's pool or refresh
            if token_user_pool_id:
                keys_from_token_pool = get_cognito_keys_for_pool(token_user_pool_id)
                if keys_from_token_pool:
                    COGNITO_KEYS = keys_from_token_pool
                    key = next((k for k in COGNITO_KEYS if k.get('kid') == kid), None)

            if not key:
                refresh_cognito_keys(force=True)
                key = next((k for k in COGNITO_KEYS if k.get('kid') == kid), None)

            if not key:
                raise HTTPException(status_code=401, detail="Invalid token key")

        # Verify audience matches the App Client ID
        payload = jwt.decode(
            token,
            key,
            algorithms=['RS256'],
            audience=CONFIG.get('COGNITO_CLIENT_ID'),
            options={"verify_at_hash": False}
        )
        
        return {
            'sub': payload.get('sub'),
            'email': payload.get('email'),
            'username': payload.get('cognito:username'),
            'groups': payload.get('cognito:groups', []),
            'role': 'admin' if 'admins' in payload.get('cognito:groups', []) else 'user'
        }
    except HTTPException:
        raise
    except JWTError as e:
        print(f"[verify_jwt_token] JWTError: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        print(f"[verify_jwt_token] Unexpected error: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")


async def get_current_user(authorization: Optional[str] = Header(None)) -> Dict:
    """
    Get current user from JWT token and query database for admin status
    Returns user with admin status from database (RBAC)
    REQUIRES: Valid JWT token from Cognito
    """
    import os
    import hashlib
    global TOKEN_CACHE

    MCP_URL = os.getenv('MCP_URL', 'http://mcp-server.aap.local:8001')

    # Require authorization header
    if not authorization:
        raise HTTPException(status_code=401, detail="Authentication required")

    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")

    token = authorization[7:]

    # Check token cache first (use hash to save memory)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    current_time = time.time()

    if token_hash in TOKEN_CACHE:
        cached_user, expiry = TOKEN_CACHE[token_hash]
        if current_time < expiry:
            # Cache hit - return cached user without verification
            return cached_user
        else:
            # Cache expired - remove from cache
            del TOKEN_CACHE[token_hash]
    
    # Require Cognito configuration
    if not CONFIG.get('COGNITO_USER_POOL_ID') or not COGNITO_KEYS:
        print(f"[get_current_user] Cognito not configured - COGNITO_USER_POOL_ID: {CONFIG.get('COGNITO_USER_POOL_ID')}, COGNITO_KEYS: {len(COGNITO_KEYS) if COGNITO_KEYS else 0} keys")
        raise HTTPException(status_code=500, detail="Authentication service not configured. Please contact administrator")
    
    # Cache miss - verify JWT token
    try:
        cognito_user = verify_jwt_token(token)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")
    user_email = cognito_user.get('email')
    user_sub = cognito_user.get('sub')
    
    if not user_email:
        raise HTTPException(status_code=401, detail="User email not found in token")
    
    # Query MCP server to get user admin status from database
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Get user info from database (includes is_admin)
            login_response = await client.post(
                f"{MCP_URL}/users/login",
                json={
                    'email': user_email,
                    'name': cognito_user.get('username', user_email.split('@')[0])
                }
            )
            
            if login_response.status_code == 200:
                db_user = login_response.json()
                is_admin = db_user.get('is_admin', False)
                roles = db_user.get('roles', [])

                # Set role based on is_admin flag
                role = 'admin' if is_admin else 'user'

                user_dict = {
                    'sub': user_sub,
                    'email': user_email,
                    'username': cognito_user.get('username', user_email.split('@')[0]),
                    'groups': cognito_user.get('groups', []),
                    'role': role,
                    'is_admin': is_admin,
                    'roles': roles
                }

                # Cache the verified user (with TTL)
                TOKEN_CACHE[token_hash] = (user_dict, current_time + TOKEN_CACHE_TTL)
                return user_dict
            else:
                # If MCP server fails, return Cognito user with default role
                user_dict = {
                    **cognito_user,
                    'role': 'user',
                    'is_admin': False
                }
                # Cache even if MCP fails (shorter TTL)
                TOKEN_CACHE[token_hash] = (user_dict, current_time + 60)
                return user_dict
    except Exception as e:
        # If query fails, return Cognito user with default role
        user_dict = {
            **cognito_user,
            'role': 'user',
            'is_admin': False
        }
        # Cache even if query fails (shorter TTL)
        TOKEN_CACHE[token_hash] = (user_dict, current_time + 60)
        return user_dict


def require_admin(user: Dict) -> Dict:
    """Require admin role"""
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


# Initialize keys on module import
COGNITO_KEYS = get_cognito_keys()

