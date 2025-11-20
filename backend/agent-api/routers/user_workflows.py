"""
User Workflows Router
Handles user-facing workflow management (browse, enable/disable, trigger, history)
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Optional
from datetime import datetime
import asyncio
import os
import logging
from services.auth_service import get_current_user
from services.workflow_cloner import clone_workflow_for_user, delete_cloned_workflow
import httpx

# Logging setup
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agentcore/user-workflows", tags=["User Workflows"])

# N8N configuration
N8N_URL = os.getenv("N8N_URL", "http://aap-n8n.aap.local:5678")
N8N_API_KEY = os.getenv("N8N_API_KEY", "")
N8N_BASIC_AUTH_USER = os.getenv("N8N_BASIC_AUTH_USER", "")
N8N_BASIC_AUTH_PASSWORD = os.getenv("N8N_BASIC_AUTH_PASSWORD", "")
MCP_URL = os.getenv("MCP_URL", "http://mcp-server.aap.local:8001")

# Validate N8N_API_KEY at startup
if not N8N_API_KEY:
    logger.warning("[User Workflows] [WARNING] No N8N_API_KEY configured - n8n requests may fail")

def get_n8n_headers() -> Dict:
    """Get headers for n8n API requests"""
    headers = {}
    if N8N_API_KEY:
        headers["X-N8N-API-KEY"] = N8N_API_KEY
    return headers

def get_n8n_auth():
    """Get basic auth for n8n API if configured"""
    if N8N_BASIC_AUTH_USER and N8N_BASIC_AUTH_PASSWORD:
        return httpx.BasicAuth(N8N_BASIC_AUTH_USER, N8N_BASIC_AUTH_PASSWORD)
    return None

# PostgreSQL connection for user workflow subscriptions
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    from config import CONFIG

    # MCP Server PostgreSQL connection - use CONFIG loaded from Secrets Manager
    DB_CONFIG = {
        'host': CONFIG.get('DB_HOST'),
        'port': int(CONFIG.get('DB_PORT', '5432')),
        'database': CONFIG.get('DB_NAME'),
        'user': CONFIG.get('DB_USER'),
        'password': CONFIG.get('DB_PASSWORD')
    }

    def get_db_connection():
        return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

    # Initialize database schema on startup
    def init_user_workflows_schema():
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Check for old schema (workflow_id column instead of template_workflow_id)
            cursor.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name='user_workflow_subscriptions'
                AND column_name='workflow_id'
            """)
            old_schema_detected = cursor.fetchone()

            if old_schema_detected:
                print("[WARNING]  [User Workflows] Old schema detected (workflow_id column found)")
                print("    Dropping old table to recreate with correct schema...")
                cursor.execute("DROP TABLE IF EXISTS user_workflow_subscriptions CASCADE")
                conn.commit()
                print("[OK]  [User Workflows] Old table dropped, will recreate with correct schema")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_workflow_subscriptions (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL,
                    template_workflow_id VARCHAR(255) NOT NULL,
                    cloned_workflow_id VARCHAR(255),
                    webhook_url TEXT,
                    trigger_type VARCHAR(50) DEFAULT 'manual',
                    enabled BOOLEAN DEFAULT true,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, template_workflow_id)
                );

                CREATE INDEX IF NOT EXISTS idx_user_workflows ON user_workflow_subscriptions(user_id);
                CREATE INDEX IF NOT EXISTS idx_workflow_users ON user_workflow_subscriptions(template_workflow_id);
                CREATE INDEX IF NOT EXISTS idx_cloned_workflows ON user_workflow_subscriptions(cloned_workflow_id);
            """)

            # Migration: Add trigger_type column if it doesn't exist
            cursor.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'user_workflow_subscriptions'
                AND column_name = 'trigger_type'
            """)
            if not cursor.fetchone():
                print("    Adding trigger_type column...")
                cursor.execute("""
                    ALTER TABLE user_workflow_subscriptions
                    ADD COLUMN trigger_type VARCHAR(50) DEFAULT 'manual'
                """)
                conn.commit()
                print("[OK]  [User Workflows] Added trigger_type column")

            conn.commit()
            cursor.close()
            conn.close()
            print("[OK] User workflow subscriptions schema initialized")
        except Exception as e:
            print(f"[ERROR] Failed to initialize user workflow schema: {e}")

    # Run schema initialization
    init_user_workflows_schema()

except Exception as e:
    print(f"WARNING: PostgreSQL connection failed: {e}")
    get_db_connection = None


@router.get("")
async def list_user_workflows(user: Dict = Depends(get_current_user)):
    """
    List all workflows with user's subscription status
    Returns: List of workflows with enabled/disabled status for current user
    """
    try:
        user_id = user.get('email')
        if not user_id:
            raise HTTPException(status_code=401, detail="User email not found")

        # Get all workflows from N8N API
        try:
            logger.info(f"[User Workflows] Fetching workflows from {N8N_URL}")
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{N8N_URL}/api/v1/workflows",
                    headers=get_n8n_headers(),
                    auth=get_n8n_auth()  # Add basic auth support
                )
                response.raise_for_status()
                response_data = response.json()
                # n8n API returns {data: [], nextCursor: null}, extract the data array
                all_workflows = response_data.get('data', []) if isinstance(response_data, dict) else response_data
                logger.info(f"[User Workflows] Successfully retrieved {len(all_workflows)} workflows")
        except httpx.ConnectError as e:
            error_str = str(e)
            if "Name or service not known" in error_str or "[Errno -2]" in error_str:
                logger.error(f"[User Workflows] DNS resolution failed for {N8N_URL}: {error_str}")
                raise HTTPException(
                    status_code=503,
                    detail=f"Service unavailable: Cannot resolve n8n hostname. Please check service discovery configuration."
                )
            else:
                logger.error(f"[User Workflows] Connection failed to {N8N_URL}: {error_str}")
                raise HTTPException(
                    status_code=503,
                    detail=f"Service unavailable: Cannot connect to n8n service."
                )
        except httpx.TimeoutException as e:
            logger.error(f"[User Workflows] Timeout connecting to {N8N_URL}: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Service unavailable: Connection timeout to n8n service."
            )
        except httpx.HTTPStatusError as e:
            # HTTP error (401, 403, 404, 500, etc) - don't silently fail!
            status_code = e.response.status_code
            logger.error(f"[User Workflows] HTTP {status_code} error from N8N: {e.response.text[:500]}")

            if status_code == 401:
                raise HTTPException(
                    status_code=503,
                    detail="N8N authentication failed. Please check N8N_API_KEY configuration."
                )
            elif status_code == 403:
                raise HTTPException(
                    status_code=503,
                    detail="N8N authorization failed. API key may not have sufficient permissions."
                )
            else:
                raise HTTPException(
                    status_code=503,
                    detail=f"N8N service error (HTTP {status_code}). Please try again later."
                )
        except httpx.HTTPError as e:
            logger.error(f"[User Workflows] Unexpected HTTP error from N8N: {e}")
            raise HTTPException(
                status_code=503,
                detail="Failed to communicate with n8n service. Please try again later."
            )

        if not get_db_connection:
            # Fallback: return workflows without subscription info
            for workflow in all_workflows:
                workflow['user_enabled'] = False
            return {"workflows": all_workflows, "count": len(all_workflows)}

        # Filter to show only template workflows (marked with [TEMPLATE] prefix)
        template_workflows = [
            w for w in all_workflows
            if w.get('name', '').startswith('[TEMPLATE]')
        ]

        # Get user's subscriptions
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT template_workflow_id, cloned_workflow_id, webhook_url, trigger_type, enabled FROM user_workflow_subscriptions WHERE user_id = %s",
            (user_id,)
        )
        subscriptions = {row['template_workflow_id']: row for row in cursor.fetchall()}
        cursor.close()
        conn.close()

        # Merge subscription status into workflows
        for workflow in template_workflows:
            sub = subscriptions.get(workflow['id'])
            if sub:
                workflow['user_enabled'] = sub['enabled']
                workflow['webhook_url'] = sub['webhook_url']
                workflow['cloned_workflow_id'] = sub['cloned_workflow_id']
                workflow['trigger_type'] = sub.get('trigger_type', 'manual')
            else:
                workflow['user_enabled'] = False
                workflow['webhook_url'] = None
                workflow['cloned_workflow_id'] = None
                workflow['trigger_type'] = 'manual'

        return {"workflows": template_workflows, "count": len(template_workflows)}

    except HTTPException:
        raise  # Re-raise HTTP exceptions (503, etc) from above
    except Exception as e:
        logger.error(f"[User Workflows] ERROR: Failed to list user workflows: {e}", exc_info=True)

        # Provide helpful error message for common database issues
        error_msg = str(e)
        if "column" in error_msg and "does not exist" in error_msg:
            raise HTTPException(
                status_code=500,
                detail="Database schema error. Please restart the agent-api service to reinitialize the schema."
            )
        elif "relation" in error_msg and "does not exist" in error_msg:
            raise HTTPException(
                status_code=500,
                detail="Database table missing. Please restart the agent-api service to create the schema."
            )
        else:
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


def get_workflow_required_oauth(workflow_name: str) -> Optional[str]:
    """
    Determine which OAuth provider is required for a workflow based on its name
    Returns provider name ('google_drive', 'github', 'jira') or None if no OAuth needed
    """
    workflow_lower = workflow_name.lower()
    if 'drive' in workflow_lower or 'google' in workflow_lower:
        return 'google_drive'
    elif 'github' in workflow_lower:
        return 'github'
    elif 'jira' in workflow_lower:
        return 'jira'
    return None


async def check_oauth_connection(user_id: str, provider: str) -> bool:
    """
    Check if user has connected OAuth provider
    Returns True if token exists and is valid, False otherwise
    """
    try:
        logger.info(f"[OAuth Check] Checking {provider} for {user_id}")
        logger.info(f"[OAuth Check] URL: {MCP_URL}/integrations/{user_id}/{provider}/token")

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{MCP_URL}/integrations/{user_id}/{provider}/token")

            logger.info(f"[OAuth Check] Response status: {response.status_code}")
            logger.info(f"[OAuth Check] Response body: {response.text[:200]}")

            if response.status_code == 200:
                data = response.json()
                has_token = bool(data.get('access_token'))
                logger.info(f"[OAuth Check] Has access_token: {has_token}")
                return has_token
            else:
                logger.warning(f"[OAuth Check] Non-200 status: {response.status_code}")
                return False
    except Exception as e:
        logger.error(f"[OAuth Check] Failed to check {provider} for {user_id}: {e}", exc_info=True)
    return False


@router.post("/{workflow_id}/toggle")
async def toggle_workflow(workflow_id: str, user: Dict = Depends(get_current_user)):
    """
    Toggle workflow subscription for current user (enable/disable)
    When enabling: Clones template workflow for user with unique webhook URL
    When disabling: Deletes cloned workflow

    Validates OAuth connection before enabling workflows that require it.
    """
    try:
        user_id = user.get('email')
        if not user_id:
            raise HTTPException(status_code=401, detail="User email not found")

        # Get Cognito sub for OAuth checks (integrations are stored by sub, not email)
        cognito_sub = user.get('sub')
        if not cognito_sub:
            raise HTTPException(status_code=401, detail="User sub not found in token")

        if not get_db_connection:
            raise HTTPException(status_code=503, detail="Database not available")

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check current status
        cursor.execute(
            "SELECT enabled, cloned_workflow_id FROM user_workflow_subscriptions WHERE user_id = %s AND template_workflow_id = %s",
            (user_id, workflow_id)
        )
        result = cursor.fetchone()

        if result:
            # Toggle existing subscription
            current_status = result['enabled']
            new_status = not current_status
            cloned_workflow_id = result.get('cloned_workflow_id')

            if new_status and not cloned_workflow_id:
                # Re-enabling: Clone workflow again
                logger.info(f"[Toggle] Re-enabling workflow {workflow_id} for user {user_id}")

                # Get workflow name to check required OAuth
                async with httpx.AsyncClient(timeout=10.0) as client:
                    try:
                        wf_response = await client.get(
                            f"{N8N_URL}/api/v1/workflows/{workflow_id}",
                            headers=get_n8n_headers(),
                            auth=get_n8n_auth()
                        )
                        wf_response.raise_for_status()
                        workflow_data = wf_response.json()
                        workflow_name = workflow_data.get('name', '')
                    except Exception as e:
                        logger.error(f"[Toggle] Failed to get workflow name: {e}")
                        workflow_name = ''

                # Check if OAuth is required and user is connected
                required_oauth = get_workflow_required_oauth(workflow_name)
                if required_oauth:
                    is_connected = await check_oauth_connection(cognito_sub, required_oauth)
                    if not is_connected:
                        cursor.close()
                        conn.close()

                        # Provide friendly error message based on provider
                        provider_names = {
                            'google_drive': 'Google Drive',
                            'github': 'GitHub',
                            'jira': 'Jira'
                        }
                        provider_display = provider_names.get(required_oauth, required_oauth)

                        raise HTTPException(
                            status_code=400,
                            detail=f"Please connect your {provider_display} account first. Go to Settings → Integrations to connect {provider_display}."
                        )

                # Get OAuth tokens
                oauth_tokens = {}
                async with httpx.AsyncClient(timeout=10.0) as client:
                    for provider in ['github', 'jira', 'google_drive']:
                        try:
                            response = await client.get(f"{MCP_URL}/integrations/{cognito_sub}/{provider}/token")
                            if response.status_code == 200:
                                data = response.json()
                                oauth_tokens[provider] = data.get('access_token')
                        except Exception as e:
                            logger.warning(f"Could not get {provider} token: {e}")

                # Clone workflow
                cloned_id, webhook_url, trigger_type = await clone_workflow_for_user(
                    workflow_id, user_id, oauth_tokens
                )

                # Update database with new cloned workflow info
                cursor.execute(
                    """UPDATE user_workflow_subscriptions
                       SET enabled = %s, cloned_workflow_id = %s, webhook_url = %s, trigger_type = %s, updated_at = CURRENT_TIMESTAMP
                       WHERE user_id = %s AND template_workflow_id = %s""",
                    (True, cloned_id, webhook_url, trigger_type, user_id, workflow_id)
                )
                conn.commit()

                return {
                    "workflow_id": workflow_id,
                    "enabled": True,
                    "webhook_url": webhook_url,
                    "cloned_workflow_id": cloned_id,
                    "message": "Workflow cloned and activated successfully"
                }

            elif not new_status and cloned_workflow_id:
                # Disabling: Delete cloned workflow
                logger.info(f"[Toggle] Disabling workflow {workflow_id} for user {user_id}, deleting clone {cloned_workflow_id}")

                try:
                    await delete_cloned_workflow(cloned_workflow_id)
                except Exception as e:
                    logger.error(f"Failed to delete cloned workflow: {e}")
                    # Continue anyway to update database

                # Update database
                cursor.execute(
                    """UPDATE user_workflow_subscriptions
                       SET enabled = %s, cloned_workflow_id = NULL, webhook_url = NULL, updated_at = CURRENT_TIMESTAMP
                       WHERE user_id = %s AND template_workflow_id = %s""",
                    (False, user_id, workflow_id)
                )
                conn.commit()

                return {
                    "workflow_id": workflow_id,
                    "enabled": False,
                    "message": "Workflow disabled and deleted successfully"
                }
            else:
                # Simple toggle without clone/delete
                cursor.execute(
                    "UPDATE user_workflow_subscriptions SET enabled = %s, updated_at = CURRENT_TIMESTAMP WHERE user_id = %s AND template_workflow_id = %s",
                    (new_status, user_id, workflow_id)
                )
                conn.commit()

                return {
                    "workflow_id": workflow_id,
                    "enabled": new_status,
                    "message": f"Workflow {'enabled' if new_status else 'disabled'} successfully"
                }

        else:
            # Create new subscription (enabled by default) - clone workflow
            logger.info(f"[Toggle] Enabling workflow {workflow_id} for user {user_id} for the first time")

            # Get workflow name to check required OAuth
            async with httpx.AsyncClient(timeout=10.0) as client:
                try:
                    wf_response = await client.get(
                        f"{N8N_URL}/api/v1/workflows/{workflow_id}",
                        headers=get_n8n_headers(),
                        auth=get_n8n_auth()
                    )
                    wf_response.raise_for_status()
                    workflow_data = wf_response.json()
                    workflow_name = workflow_data.get('name', '')
                except Exception as e:
                    logger.error(f"[Toggle] Failed to get workflow name: {e}")
                    workflow_name = ''

            # Check if OAuth is required and user is connected
            required_oauth = get_workflow_required_oauth(workflow_name)
            if required_oauth:
                is_connected = await check_oauth_connection(cognito_sub, required_oauth)
                if not is_connected:
                    cursor.close()
                    conn.close()

                    # Provide friendly error message based on provider
                    provider_names = {
                        'google_drive': 'Google Drive',
                        'github': 'GitHub',
                        'jira': 'Jira'
                    }
                    provider_display = provider_names.get(required_oauth, required_oauth)

                    raise HTTPException(
                        status_code=400,
                        detail=f"Please connect your {provider_display} account first. Go to Settings → Integrations to connect {provider_display}."
                    )

            # Get OAuth tokens
            oauth_tokens = {}
            async with httpx.AsyncClient(timeout=10.0) as client:
                for provider in ['github', 'jira', 'google_drive']:
                    try:
                        response = await client.get(f"{MCP_URL}/integrations/{cognito_sub}/{provider}/token")
                        if response.status_code == 200:
                            data = response.json()
                            oauth_tokens[provider] = data.get('access_token')
                    except Exception as e:
                        logger.warning(f"Could not get {provider} token: {e}")

            # Clone workflow
            cloned_id, webhook_url, trigger_type = await clone_workflow_for_user(
                workflow_id, user_id, oauth_tokens
            )

            # Insert new subscription
            cursor.execute(
                """INSERT INTO user_workflow_subscriptions
                   (user_id, template_workflow_id, cloned_workflow_id, webhook_url, trigger_type, enabled)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (user_id, workflow_id, cloned_id, webhook_url, trigger_type, True)
            )
            conn.commit()

            return {
                "workflow_id": workflow_id,
                "enabled": True,
                "webhook_url": webhook_url,
                "cloned_workflow_id": cloned_id,
                "message": "Workflow cloned and activated successfully"
            }

        cursor.close()
        conn.close()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ERROR: Failed to toggle workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{workflow_id}/trigger")
async def trigger_workflow(workflow_id: str, payload: Optional[Dict] = None, user: Dict = Depends(get_current_user)):
    """
    Manually trigger a workflow for current user
    Only works if workflow is enabled for user
    """
    try:
        user_id = user.get('email')
        if not user_id:
            raise HTTPException(status_code=401, detail="User email not found")

        # Get Cognito sub for OAuth token fetching
        cognito_sub = user.get('sub')
        if not cognito_sub:
            raise HTTPException(status_code=401, detail="User sub not found in token")

        # Check if workflow is enabled for user and get cloned workflow ID + webhook URL
        cloned_workflow_id = workflow_id
        webhook_url = None
        trigger_type = "manual"

        if get_db_connection:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT enabled, cloned_workflow_id, webhook_url, trigger_type FROM user_workflow_subscriptions WHERE user_id = %s AND template_workflow_id = %s",
                (user_id, workflow_id)
            )
            result = cursor.fetchone()
            cursor.close()
            conn.close()

            if not result or not result['enabled']:
                raise HTTPException(
                    status_code=403,
                    detail="Workflow is not enabled for your account. Please enable it first."
                )

            # Use cloned workflow ID if available
            if result.get('cloned_workflow_id'):
                cloned_workflow_id = result['cloned_workflow_id']

            # Get webhook URL and trigger type
            webhook_url = result.get('webhook_url')
            trigger_type = result.get('trigger_type', 'manual')

        # Only webhook-based workflows can be manually triggered
        if trigger_type == "schedule":
            raise HTTPException(
                status_code=400,
                detail="This workflow uses a schedule trigger and cannot be manually triggered. It will run automatically according to its schedule."
            )
        elif trigger_type == "manual":
            raise HTTPException(
                status_code=400,
                detail="This workflow uses a manual trigger and can only be executed from the n8n UI."
            )
        elif trigger_type != "webhook":
            raise HTTPException(
                status_code=400,
                detail=f"This workflow cannot be triggered via API (trigger type: {trigger_type})."
            )

        # Get user's OAuth tokens from MCP Server
        oauth_tokens = {}
        async with httpx.AsyncClient(timeout=10.0) as client:
            for provider in ['github', 'jira', 'google_drive']:
                try:
                    response = await client.get(f"{MCP_URL}/integrations/{cognito_sub}/{provider}/token")
                    if response.status_code == 200:
                        data = response.json()
                        oauth_tokens[provider] = data.get('access_token')
                except Exception as e:
                    print(f"WARNING: Failed to get {provider} token: {e}")

        # Enhanced payload with user context + OAuth tokens
        trigger_payload = payload or {}
        enhanced_payload = {
            **trigger_payload,
            "user_id": user_id,
            "oauth_tokens": oauth_tokens
        }

        # Trigger N8N webhook using stored webhook URL
        logger.info(f"[User Workflows] Triggering workflow {cloned_workflow_id} (template: {workflow_id}) for user {user_id}")
        logger.info(f"[User Workflows] Webhook URL: {webhook_url}")
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    webhook_url,  # Use full webhook URL from database
                    json=enhanced_payload
                )
                response.raise_for_status()
                result = response.json() if response.text else {"success": True}
                logger.info(f"[User Workflows] Successfully triggered workflow {cloned_workflow_id}")
        except httpx.ConnectError as e:
            error_str = str(e)
            if "Name or service not known" in error_str or "[Errno -2]" in error_str:
                logger.error(f"[User Workflows] DNS resolution failed: {error_str}")
                raise HTTPException(
                    status_code=503,
                    detail="Service unavailable: Cannot resolve n8n hostname."
                )
            else:
                logger.error(f"[User Workflows] Connection failed: {error_str}")
                raise HTTPException(
                    status_code=503,
                    detail="Service unavailable: Cannot connect to n8n service."
                )
        except httpx.TimeoutException as e:
            logger.error(f"[User Workflows] Timeout: {e}")
            raise HTTPException(
                status_code=503,
                detail="Service unavailable: Connection timeout."
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"[User Workflows] HTTP {e.response.status_code} error: {e}")
            if e.response.status_code == 404:
                raise HTTPException(status_code=404, detail="Workflow webhook not found")
            raise HTTPException(status_code=500, detail="Failed to trigger workflow")

        return {
            "workflow_id": workflow_id,
            "triggered": True,
            "user_id": user_id,
            "result": result
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: Failed to trigger workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{workflow_id}/executions")
async def get_workflow_executions(
    workflow_id: str,
    limit: int = 20,
    user: Dict = Depends(get_current_user)
):
    """
    Get execution history for a workflow (filtered by current user)
    Queries N8N PostgreSQL database directly
    """
    try:
        user_id = user.get('email')
        if not user_id:
            raise HTTPException(status_code=401, detail="User email not found")

        # N8N PostgreSQL connection - use CONFIG loaded from Secrets Manager
        n8n_db_config = {
            'host': CONFIG.get('N8N_DB_HOST', CONFIG.get('DB_HOST')),
            'port': int(CONFIG.get('N8N_DB_PORT', CONFIG.get('DB_PORT', '5432'))),
            'database': CONFIG.get('N8N_DB_NAME', 'n8n'),
            'user': CONFIG.get('N8N_DB_USER', CONFIG.get('DB_USER')),
            'password': CONFIG.get('N8N_DB_PASSWORD', CONFIG.get('DB_PASSWORD'))
        }

        import psycopg2
        from psycopg2.extras import RealDictCursor

        conn = psycopg2.connect(**n8n_db_config, cursor_factory=RealDictCursor)
        cursor = conn.cursor()

        # Query execution_entity table
        # N8N stores executions with workflowId and data (which should contain our user_id)
        cursor.execute("""
            SELECT
                id,
                "workflowId",
                finished,
                mode,
                "retryOf",
                "retrySuccessId",
                "startedAt",
                "stoppedAt",
                "waitTill"
            FROM execution_entity
            WHERE "workflowId" = %s
            ORDER BY "startedAt" DESC
            LIMIT %s
        """, (workflow_id, limit))

        executions = cursor.fetchall()
        cursor.close()
        conn.close()

        # Format executions
        formatted_executions = []
        for exe in executions:
            # Calculate duration if both times exist
            duration = None
            if exe.get('startedAt') and exe.get('stoppedAt'):
                start = exe['startedAt']
                stop = exe['stoppedAt']
                duration = (stop - start).total_seconds()

            # Determine status
            status = "running"
            if exe.get('finished'):
                status = "success" if exe.get('finished') else "failed"

            formatted_executions.append({
                "id": exe['id'],
                "workflow_id": exe['workflowId'],
                "status": status,
                "started_at": exe['startedAt'].isoformat() if exe.get('startedAt') else None,
                "stopped_at": exe['stoppedAt'].isoformat() if exe.get('stoppedAt') else None,
                "duration_seconds": duration,
                "mode": exe.get('mode')
            })

        return {
            "workflow_id": workflow_id,
            "executions": formatted_executions,
            "count": len(formatted_executions)
        }

    except Exception as e:
        print(f"ERROR: Failed to get workflow executions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{workflow_id}/status")
async def get_workflow_status(workflow_id: str, user: Dict = Depends(get_current_user)):
    """
    Get workflow subscription status for current user
    """
    try:
        user_id = user.get('email')
        if not user_id:
            raise HTTPException(status_code=401, detail="User email not found")

        if not get_db_connection:
            return {"workflow_id": workflow_id, "enabled": False}

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT enabled, cloned_workflow_id, webhook_url, created_at, updated_at FROM user_workflow_subscriptions WHERE user_id = %s AND template_workflow_id = %s",
            (user_id, workflow_id)
        )
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if not result:
            return {"workflow_id": workflow_id, "enabled": False}

        return {
            "workflow_id": workflow_id,
            "enabled": result['enabled'],
            "cloned_workflow_id": result.get('cloned_workflow_id'),
            "webhook_url": result.get('webhook_url'),
            "subscribed_at": result['created_at'].isoformat() if result.get('created_at') else None,
            "updated_at": result['updated_at'].isoformat() if result.get('updated_at') else None
        }

    except Exception as e:
        print(f"ERROR: Failed to get workflow status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
