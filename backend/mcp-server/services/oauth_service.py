"""
OAuth service
Handles OAuth integrations and state management
"""

import json
import os
import base64
import httpx
from typing import Dict, Optional, List
from fastapi import HTTPException
from database import get_db
import psycopg2


def save_integration(integration: Dict) -> Dict:
    """Save OAuth integration to database"""
    try:
        print(f"[save_integration] Received integration save request")
        print(f"[save_integration] Payload keys: {list(integration.keys())}")
        
        provider = integration['provider']
        user_id = integration.get('user_id')
        user_email = integration.get('user_email')
        user_info = integration.get('provider_user_info', {})
        
        print(f"[save_integration] Saving integration for user_id={user_id}, user_email={user_email}, provider={provider}")

        # Map provider names: frontend uses 'drive' but database stores 'google_drive'
        # Normalize provider name to database format
        if provider == 'drive':
            db_provider = 'google_drive'
        else:
            db_provider = provider
        
        # Extract provider-specific username/email
        if provider == 'github' or db_provider == 'github':
            # Try 'username' first (from our API), fallback to 'login' (GitHub API)
            provider_username = user_info.get('username') or user_info.get('login')
            provider_user_id = str(user_info.get('id'))
        elif provider == 'jira' or db_provider == 'jira':
            provider_username = user_info.get('email') or user_info.get('displayName')
            provider_user_id = user_info.get('accountId')
        elif provider == 'drive' or db_provider == 'google_drive':
            provider_username = user_info.get('email') or user_info.get('username')
            provider_user_id = str(user_info.get('id'))
        else:
            provider_username = user_info.get('email') or user_info.get('name')
            provider_user_id = user_info.get('id')

        conn = get_db()
        cur = conn.cursor()
        # Log token preview for verification (first 10 chars only)
        token_preview = integration['access_token'][:10] + "..." if len(integration['access_token']) > 10 else integration['access_token']
        print(f"[save_integration] Storing token for user_id={user_id}, provider={db_provider} (token preview: {token_preview})")
        
        cur.execute("""
            INSERT INTO oauth_integrations
            (user_id, user_email, provider, access_token, refresh_token,
             provider_user_id, provider_user_email, scope, metadata, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, true)
            ON CONFLICT (user_id, provider)
            DO UPDATE SET
                access_token = EXCLUDED.access_token,
                refresh_token = EXCLUDED.refresh_token,
                provider_user_id = EXCLUDED.provider_user_id,
                provider_user_email = EXCLUDED.provider_user_email,
                scope = EXCLUDED.scope,
                metadata = EXCLUDED.metadata,
                is_active = true,
                updated_at = NOW()
        """, (
            integration['user_id'],
            integration['user_email'],
            db_provider,  # Use normalized provider name for database
            integration['access_token'],
            integration.get('refresh_token'),
            provider_user_id,
            provider_username,
            integration.get('scope'),
            json.dumps(user_info)
        ))
        conn.commit()
        conn.close()
        
        print(f"[save_integration] Successfully saved integration for user_id={user_id}, provider={db_provider}")
        return {"success": True, "message": f"Integration saved for {db_provider}"}
    except Exception as e:
        import traceback
        print(f"[save_integration] ERROR saving integration: {e}")
        print(f"[save_integration] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


def get_user_integrations(user_id: str) -> Dict:
    """Get all integrations for a user"""
    try:
        # Use regular cursor, not RealDictCursor
        from config import CONFIG
        conn = psycopg2.connect(
            host=CONFIG['DB_HOST'],
            port=CONFIG['DB_PORT'],
            database=CONFIG['DB_NAME'],
            user=CONFIG['DB_USER'],
            password=CONFIG['DB_PASSWORD']
        )
        cur = conn.cursor()
        cur.execute("""
            SELECT provider, user_email, provider_user_email, provider_user_id,
                   access_token, refresh_token, scope, created_at, is_active, metadata
            FROM oauth_integrations
            WHERE user_id = %s AND is_active = true
        """, (user_id,))
        results = cur.fetchall()
        cur.close()
        conn.close()

        integrations = []
        for row in results:
            # Use provider_user_email if available, otherwise user_email
            username = row[2] if row[2] else row[1]  # provider_user_email or user_email
            integrations.append({
                "provider": row[0],
                "username": username,
                "provider_user_id": row[3],
                "provider_user_email": row[2],
                "scope": row[6],
                "created_at": row[7].isoformat() if row[7] else None,
                "connected": True,
                "metadata": row[9]  # Add metadata column
            })

        return {"integrations": integrations}
    except Exception as e:
        import traceback
        print(f"ERROR getting user integrations: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


def get_integration_token(user_id: str, provider: str) -> Dict:
    """Get access token for a specific integration"""
    try:
        # Map provider names: API uses 'drive' but database stores 'google_drive'
        db_provider = 'google_drive' if provider == 'drive' else provider

        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT access_token FROM oauth_integrations
            WHERE user_id = %s AND provider = %s AND is_active = true
        """, (user_id, db_provider))
        result = cur.fetchone()
        conn.close()

        if not result:
            raise HTTPException(status_code=404, detail="Integration not found")

        return {"access_token": result['access_token']}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def delete_integration(user_id: str, provider: str) -> Dict:
    """
    Delete integration and revoke access token
    FIXED: Now revokes access token (GitHub, Google Drive, Jira) before deleting from database
    This ensures providers show consent screen when reconnecting
    """
    try:
        # Map provider names: API uses 'drive' but database stores 'google_drive'
        db_provider = 'google_drive' if provider == 'drive' else provider
        
        conn = get_db()
        cur = conn.cursor()
        
        # Get access token before deleting (for revocation)
        cur.execute("""
            SELECT access_token FROM oauth_integrations
            WHERE user_id = %s AND provider = %s AND is_active = true
        """, (user_id, db_provider))
        result = cur.fetchone()
        access_token = result['access_token'] if result else None
        
        # Revoke access token based on provider
        if access_token:
            try:
                if db_provider == "github":
                    # GitHub API: DELETE /applications/{client_id}/token
                    github_client_id = os.getenv('GITHUB_CLIENT_ID', '')
                    github_client_secret = os.getenv('GITHUB_CLIENT_SECRET', '')
                    
                    if github_client_id and github_client_secret:
                        auth_string = f"{github_client_id}:{github_client_secret}"
                        auth_bytes = auth_string.encode('ascii')
                        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
                        
                        with httpx.Client(timeout=10.0) as client:
                            revoke_response = client.delete(
                                f"https://api.github.com/applications/{github_client_id}/token",
                                headers={
                                    "Authorization": f"Basic {auth_b64}",
                                    "Accept": "application/vnd.github+json"
                                },
                                json={"access_token": access_token}
                            )
                            
                            if revoke_response.status_code in [204, 200]:
                                print(f"OK: GitHub access token revoked for user {user_id}")
                            else:
                                print(f"WARNING: Failed to revoke GitHub token: {revoke_response.status_code} - {revoke_response.text}")
                
                elif db_provider == "google_drive":
                    # Google OAuth revoke: POST https://oauth2.googleapis.com/revoke
                    with httpx.Client(timeout=10.0) as client:
                        revoke_response = client.post(
                            "https://oauth2.googleapis.com/revoke",
                            params={"token": access_token},
                            headers={"Content-Type": "application/x-www-form-urlencoded"}
                        )
                        
                        if revoke_response.status_code in [200, 204]:
                            print(f"OK: Google Drive access token revoked for user {user_id}")
                        else:
                            print(f"WARNING: Failed to revoke Google token: {revoke_response.status_code} - {revoke_response.text}")
                
                elif db_provider == "jira":
                    # Jira/Atlassian OAuth revoke: POST https://auth.atlassian.com/oauth/revoke_token
                    # Note: Jira uses refresh token for revocation, but we can try with access token
                    jira_client_id = os.getenv('JIRA_CLIENT_ID', '')
                    jira_client_secret = os.getenv('JIRA_CLIENT_SECRET', '')
                    
                    if jira_client_id and jira_client_secret:
                        # Get refresh token from database if available
                        cur.execute("""
                            SELECT refresh_token FROM oauth_integrations
                            WHERE user_id = %s AND provider = %s AND is_active = true
                        """, (user_id, db_provider))
                        refresh_result = cur.fetchone()
                        refresh_token = refresh_result['refresh_token'] if refresh_result else None
                        
                        # Try to revoke with refresh token (preferred) or access token
                        token_to_revoke = refresh_token if refresh_token else access_token
                        
                        with httpx.Client(timeout=10.0) as client:
                            revoke_response = client.post(
                                "https://auth.atlassian.com/oauth/revoke_token",
                                auth=(jira_client_id, jira_client_secret),
                                data={
                                    "token": token_to_revoke,
                                    "token_type_hint": "refresh_token" if refresh_token else "access_token"
                                },
                                headers={"Content-Type": "application/x-www-form-urlencoded"}
                            )
                            
                            if revoke_response.status_code in [200, 204]:
                                print(f"OK: Jira access token revoked for user {user_id}")
                            else:
                                print(f"WARNING: Failed to revoke Jira token: {revoke_response.status_code} - {revoke_response.text}")
                
            except Exception as revoke_error:
                # Log error but continue with deletion
                print(f"WARNING: Error revoking {db_provider} token: {revoke_error}")
        
        # Delete from database (set is_active = false)
        cur.execute("""
            UPDATE oauth_integrations SET is_active = false
            WHERE user_id = %s AND provider = %s
        """, (user_id, db_provider))
        conn.commit()
        conn.close()
        return {"success": True}
    except Exception as e:
        import traceback
        print(f"ERROR in delete_integration: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        # Rollback transaction if connection exists
        try:
            if 'conn' in locals():
                conn.rollback()
                conn.close()
        except:
            pass
        raise HTTPException(status_code=500, detail=str(e))


def save_oauth_state(state_data: Dict) -> Dict:
    """Save OAuth state to database for persistent storage"""
    try:
        conn = get_db()
        cur = conn.cursor()
        
        # Set expiration to 15 minutes from now
        # Use database NOW() function directly to avoid timezone issues
        cur.execute("""
            INSERT INTO oauth_states (state, user_id, user_email, provider, expires_at)
            VALUES (%s, %s, %s, %s, NOW() + INTERVAL '15 minutes')
            ON CONFLICT (state) DO UPDATE SET 
                expires_at = NOW() + INTERVAL '15 minutes',
                user_id = EXCLUDED.user_id,
                user_email = EXCLUDED.user_email,
                provider = EXCLUDED.provider,
                created_at = NOW()
        """, (
            state_data['state'],
            state_data['user_id'],
            state_data['user_email'],
            state_data['provider']
        ))
        conn.commit()
        conn.close()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save OAuth state: {str(e)}")


def get_oauth_state(state: str) -> Dict:
    """Get OAuth state from database"""
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT state, user_id, user_email, provider, expires_at
            FROM oauth_states
            WHERE state = %s AND expires_at > NOW()
        """, (state,))
        result = cur.fetchone()
        conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="OAuth state not found or expired")
        
        return {
            "state": result['state'],
            "user_id": result['user_id'],
            "user_email": result['user_email'],
            "provider": result['provider'],
            "expires_at": result['expires_at'].isoformat() if result['expires_at'] else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def delete_oauth_state(state: str) -> Dict:
    """Delete OAuth state from database"""
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM oauth_states WHERE state = %s", (state,))
        conn.commit()
        conn.close()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def cleanup_expired_oauth_states() -> Dict:
    """Clean up expired OAuth states"""
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM oauth_states WHERE expires_at < NOW()")
        deleted_count = cur.rowcount
        conn.commit()
        conn.close()
        return {"success": True, "deleted_count": deleted_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

