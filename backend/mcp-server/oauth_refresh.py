"""
OAuth Token Refresh Helper
Handles automatic token refresh for GitHub, Jira, and Google Drive
"""

import httpx
import psycopg2
from typing import Optional, Dict
import os
import json

def load_oauth_config():
    """Load OAuth client credentials from environment or AWS Secrets"""
    try:
        import boto3
        environment = os.getenv('ENVIRONMENT', 'uat')
        client = boto3.client('secretsmanager', region_name='ap-southeast-2')
        response = client.get_secret_value(SecretId=f'AAP/{environment}/mcp-server')
        secrets = json.loads(response['SecretString'])

        return {
            'github': {
                'client_id': secrets.get('GITHUB_CLIENT_ID'),
                'client_secret': secrets.get('GITHUB_CLIENT_SECRET')
            },
            'jira': {
                'client_id': secrets.get('JIRA_CLIENT_ID'),
                'client_secret': secrets.get('JIRA_CLIENT_SECRET')
            },
            'google_drive': {
                'client_id': secrets.get('GOOGLE_CLIENT_ID'),
                'client_secret': secrets.get('GOOGLE_CLIENT_SECRET')
            }
        }
    except Exception as e:
        print(f"[oauth_refresh] Failed to load OAuth config: {e}")
        # Fallback to env vars
        return {
            'github': {
                'client_id': os.getenv('GITHUB_CLIENT_ID'),
                'client_secret': os.getenv('GITHUB_CLIENT_SECRET')
            },
            'jira': {
                'client_id': os.getenv('JIRA_CLIENT_ID'),
                'client_secret': os.getenv('JIRA_CLIENT_SECRET')
            },
            'google_drive': {
                'client_id': os.getenv('GOOGLE_CLIENT_ID'),
                'client_secret': os.getenv('GOOGLE_CLIENT_SECRET')
            }
        }

OAUTH_CONFIG = load_oauth_config()

async def refresh_github_token(refresh_token: str) -> Optional[Dict]:
    """Refresh GitHub access token"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://github.com/login/oauth/access_token",
                headers={"Accept": "application/json"},
                data={
                    "client_id": OAUTH_CONFIG['github']['client_id'],
                    "client_secret": OAUTH_CONFIG['github']['client_secret'],
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token"
                }
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "access_token": data.get("access_token"),
                    "refresh_token": data.get("refresh_token", refresh_token),
                    "expires_in": data.get("expires_in")
                }
    except Exception as e:
        print(f"[refresh_github_token] Error: {e}")
    return None

async def refresh_jira_token(refresh_token: str) -> Optional[Dict]:
    """Refresh Jira access token"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://auth.atlassian.com/oauth/token",
                headers={"Content-Type": "application/json"},
                json={
                    "grant_type": "refresh_token",
                    "client_id": OAUTH_CONFIG['jira']['client_id'],
                    "client_secret": OAUTH_CONFIG['jira']['client_secret'],
                    "refresh_token": refresh_token
                }
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "access_token": data.get("access_token"),
                    "refresh_token": data.get("refresh_token", refresh_token),
                    "expires_in": data.get("expires_in")
                }
    except Exception as e:
        print(f"[refresh_jira_token] Error: {e}")
    return None

async def refresh_google_token(refresh_token: str) -> Optional[Dict]:
    """Refresh Google Drive access token"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": OAUTH_CONFIG['google_drive']['client_id'],
                    "client_secret": OAUTH_CONFIG['google_drive']['client_secret'],
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token"
                }
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "access_token": data.get("access_token"),
                    "expires_in": data.get("expires_in")
                }
    except Exception as e:
        print(f"[refresh_google_token] Error: {e}")
    return None

def update_access_token_in_db(user_id: str, provider: str, new_access_token: str, new_refresh_token: Optional[str], db_config: Dict):
    """Update access token in database"""
    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        if new_refresh_token:
            cur.execute("""
                UPDATE oauth_integrations
                SET access_token = %s, refresh_token = %s, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s AND provider = %s
            """, (new_access_token, new_refresh_token, user_id, provider))
        else:
            cur.execute("""
                UPDATE oauth_integrations
                SET access_token = %s, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s AND provider = %s
            """, (new_access_token, user_id, provider))

        conn.commit()
        cur.close()
        conn.close()

        print(f"[update_access_token_in_db] Updated token for user_id='{user_id}', provider='{provider}'")
        return True
    except Exception as e:
        print(f"[update_access_token_in_db] Error: {e}")
        return False

async def get_or_refresh_token(user_id: str, provider: str, db_config: Dict) -> Optional[str]:
    """
    Get access token from database, refresh if expired/invalid
    Returns: access_token or None
    """
    try:
        # Map provider names
        provider_mapping = {
            'drive': 'google_drive',
            'github': 'github',
            'jira': 'jira'
        }
        db_provider = provider_mapping.get(provider, provider)

        # Get token and refresh_token from database
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        cur.execute("""
            SELECT access_token, refresh_token FROM oauth_integrations
            WHERE user_id = %s AND provider = %s AND is_active = true
        """, (user_id, db_provider))

        result = cur.fetchone()
        cur.close()
        conn.close()

        if not result:
            print(f"[get_or_refresh_token] No integration found for user_id='{user_id}', provider='{db_provider}'")
            return None

        access_token, refresh_token = result

        if not access_token:
            print(f"[get_or_refresh_token] No access token found, trying to refresh...")
            if not refresh_token:
                print(f"[get_or_refresh_token] No refresh token available")
                return None

            # Try to refresh
            new_tokens = None
            if db_provider == 'github':
                new_tokens = await refresh_github_token(refresh_token)
            elif db_provider == 'jira':
                new_tokens = await refresh_jira_token(refresh_token)
            elif db_provider == 'google_drive':
                new_tokens = await refresh_google_token(refresh_token)

            if new_tokens and new_tokens.get('access_token'):
                # Update database
                update_access_token_in_db(
                    user_id,
                    db_provider,
                    new_tokens['access_token'],
                    new_tokens.get('refresh_token'),
                    db_config
                )
                return new_tokens['access_token']
            else:
                print(f"[get_or_refresh_token] Failed to refresh token")
                return None

        return access_token

    except Exception as e:
        print(f"[get_or_refresh_token] Error: {e}")
        return None
