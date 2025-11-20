"""
N8N Workflows REST API Router
Provides direct REST endpoints for n8n workflow management
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Optional, Any
import httpx
import os
import logging
from datetime import datetime

from services.auth_service import get_current_user

router = APIRouter(prefix="/agentcore/n8n", tags=["n8n"])

N8N_URL = os.getenv("N8N_URL", "http://aap-n8n.aap.local:5678")
N8N_API_KEY = os.getenv("N8N_API_KEY", "")
N8N_BASIC_AUTH_USER = os.getenv("N8N_BASIC_AUTH_USER", "")
N8N_BASIC_AUTH_PASSWORD = os.getenv("N8N_BASIC_AUTH_PASSWORD", "")

# Logging setup
logger = logging.getLogger(__name__)
logger.info(f"[N8N Router] Initialized with N8N_URL: {N8N_URL}")
logger.info(f"[N8N Router] Authentication: DISABLED (internal VPC access)")

def get_n8n_headers() -> Dict[str, str]:
    """Get headers for n8n API requests, including API key if configured"""
    headers = {}
    if N8N_API_KEY:
        headers["X-N8N-API-KEY"] = N8N_API_KEY
        logger.debug("[N8N] Using API Key authentication")
    else:
        logger.warning("[N8N] [WARNING] No API key configured - n8n requires X-N8N-API-KEY header")
    return headers

def get_n8n_auth() -> Optional[tuple]:
    """Get basic auth credentials if configured"""
    if N8N_BASIC_AUTH_USER and N8N_BASIC_AUTH_PASSWORD:
        logger.debug("[N8N] Using Basic Auth")
        return (N8N_BASIC_AUTH_USER, N8N_BASIC_AUTH_PASSWORD)
    return None


def handle_n8n_error(e: Exception, operation: str) -> HTTPException:
    """
    Handle n8n connection errors and return appropriate HTTP status codes.
    
    Args:
        e: The exception that occurred
        operation: Description of the operation being performed
        
    Returns:
        HTTPException with appropriate status code and error message
    """
    error_str = str(e)
    timestamp = datetime.utcnow().isoformat()
    
    # Check for DNS resolution errors
    if "Name or service not known" in error_str or "Name resolution" in error_str or "[Errno -2]" in error_str:
        logger.error(f"[N8N] DNS resolution failed for {N8N_URL} at {timestamp}: {error_str}")
        return HTTPException(
            status_code=503,
            detail=f"Service unavailable: Cannot resolve n8n hostname. Please check service discovery configuration. Error: {error_str}"
        )
    
    # Check for connection errors
    if isinstance(e, httpx.ConnectError) or "Connection" in error_str or "connect" in error_str.lower():
        logger.error(f"[N8N] Connection failed to {N8N_URL} at {timestamp}: {error_str}")
        return HTTPException(
            status_code=503,
            detail=f"Service unavailable: Cannot connect to n8n service at {N8N_URL}. Error: {error_str}"
        )
    
    # Check for timeout errors
    if isinstance(e, httpx.TimeoutException) or "timeout" in error_str.lower():
        logger.error(f"[N8N] Timeout connecting to {N8N_URL} at {timestamp}: {error_str}")
        return HTTPException(
            status_code=503,
            detail=f"Service unavailable: Connection timeout to n8n service. Error: {error_str}"
        )
    
    # Check for HTTP status errors
    if isinstance(e, httpx.HTTPStatusError):
        status_code = e.response.status_code
        logger.error(f"[N8N] HTTP {status_code} error at {timestamp}: {error_str}")
        if status_code == 401:
            return HTTPException(
                status_code=503,
                detail=f"n8n authentication failed. Please configure N8N_API_KEY or N8N_BASIC_AUTH_USER/PASSWORD. Error: {error_str}"
            )
        elif status_code == 404:
            return HTTPException(status_code=404, detail=f"Resource not found: {error_str}")
        elif status_code >= 500:
            return HTTPException(
                status_code=503,
                detail=f"n8n service error (HTTP {status_code}): {error_str}"
            )
        else:
            return HTTPException(
                status_code=status_code,
                detail=f"n8n API error: {error_str}"
            )
    
    # Generic error
    logger.error(f"[N8N] Error during {operation} at {timestamp}: {error_str}")
    return HTTPException(
        status_code=500,
        detail=f"Failed to {operation}: {error_str}"
    )


@router.get("/workflows", response_model=List[Dict[str, Any]])
async def list_workflows(user: Dict = Depends(get_current_user)):
    """List all n8n workflows"""
    logger.info(f"[N8N] Listing workflows from {N8N_URL}")
    
    try:
        headers = get_n8n_headers()
        auth = get_n8n_auth()
        logger.info(f"[N8N] Request headers: {list(headers.keys())}")
        if 'X-N8N-API-KEY' in headers:
            logger.info(f"[N8N] API Key being sent: {headers['X-N8N-API-KEY'][:30]}...")
        logger.info(f"[N8N] Using auth: {'Yes' if auth else 'No'}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            logger.info(f"[N8N] Attempting to connect to {N8N_URL}/api/v1/workflows")
            response = await client.get(
                f"{N8N_URL}/api/v1/workflows",
                headers=headers,
                auth=auth
            )
            logger.info(f"[N8N] Response status: {response.status_code}")
            response.raise_for_status()
            response_data = response.json()
            # n8n API returns {data: [], nextCursor: null}, extract the data array
            workflows = response_data.get('data', []) if isinstance(response_data, dict) else response_data
            logger.info(f"[N8N] Successfully retrieved {len(workflows)} workflows")
            return workflows
    except httpx.HTTPStatusError as e:
        logger.error(f"[N8N] HTTP Status Error: {e.response.status_code} - {e.response.text[:200]}")
        raise handle_n8n_error(e, "list workflows")
    except httpx.ConnectError as e:
        logger.error(f"[N8N] Connection Error: {type(e).__name__} - {str(e)}")
        raise handle_n8n_error(e, "list workflows")
    except Exception as e:
        logger.error(f"[N8N] Unexpected Error: {type(e).__name__} - {str(e)}")
        import traceback
        logger.error(f"[N8N] Traceback: {traceback.format_exc()}")
        raise handle_n8n_error(e, "list workflows")


@router.get("/workflows/{workflow_id}", response_model=Dict[str, Any])
async def get_workflow(workflow_id: str, user: Dict = Depends(get_current_user)):
    """Get a specific n8n workflow by ID"""
    logger.info(f"[N8N] Getting workflow {workflow_id} from {N8N_URL}")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{N8N_URL}/api/v1/workflows/{workflow_id}",
                headers=get_n8n_headers(),
                auth=get_n8n_auth()
            )
            response.raise_for_status()
            logger.info(f"[N8N] Successfully retrieved workflow {workflow_id}")
            return response.json()
    except Exception as e:
        raise handle_n8n_error(e, f"get workflow {workflow_id}")


@router.post("/workflows", response_model=Dict[str, Any])
async def create_workflow(workflow_data: Dict[str, Any], user: Dict = Depends(get_current_user)):
    """Create a new n8n workflow"""
    workflow_name = workflow_data.get('name', 'unknown')
    logger.info(f"[N8N] Creating workflow '{workflow_name}' at {N8N_URL}")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{N8N_URL}/api/v1/workflows",
                json=workflow_data,
                headers=get_n8n_headers(),
                auth=get_n8n_auth()
            )

            # Log response details for debugging
            if response.status_code >= 400:
                logger.error(f"[N8N] HTTP {response.status_code} error creating workflow")
                logger.error(f"[N8N] Response body: {response.text[:500]}")

            response.raise_for_status()
            result = response.json()
            logger.info(f"[N8N] Successfully created workflow '{workflow_name}'")
            return result
    except httpx.HTTPStatusError as e:
        logger.error(f"[N8N] Failed to create workflow: {e.response.text[:500]}")
        raise handle_n8n_error(e, f"create workflow '{workflow_name}'")
    except Exception as e:
        raise handle_n8n_error(e, f"create workflow '{workflow_name}'")


# DISABLED: N8N API v1 does not support updating workflows via PUT
# - The 'active' field is read-only and causes 400 Bad Request
# - Other computed fields (createdAt, updatedAt) cannot be modified via API
# - Use POST /workflows/{workflow_id}/activate for activation
# - Import/export workflows via UI for content changes
#
# @router.put("/workflows/{workflow_id}", response_model=Dict[str, Any])
# async def update_workflow(
#     workflow_id: str,
#     workflow_data: Dict[str, Any],
#     user: Dict = Depends(get_current_user)
# ):
#     """Update an existing n8n workflow - DISABLED (use database for activation)"""
#     raise HTTPException(
#         status_code=501,
#         detail="Workflow updates via API are not supported. Use activate/deactivate endpoints or n8n UI."
#     )


@router.delete("/workflows/{workflow_id}")
async def delete_workflow(workflow_id: str, user: Dict = Depends(get_current_user)):
    """Delete an n8n workflow"""
    logger.info(f"[N8N] Deleting workflow {workflow_id} at {N8N_URL}")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.delete(
                f"{N8N_URL}/api/v1/workflows/{workflow_id}",
                headers=get_n8n_headers(),
                auth=get_n8n_auth()
            )
            response.raise_for_status()
            logger.info(f"[N8N] Successfully deleted workflow {workflow_id}")
            return {"message": f"Workflow {workflow_id} deleted successfully"}
    except Exception as e:
        raise handle_n8n_error(e, f"delete workflow {workflow_id}")


@router.post("/workflows/{workflow_id}/activate")
async def activate_workflow(
    workflow_id: str,
    active: bool = True,
    user: Dict = Depends(get_current_user)
):
    """
    Activate or deactivate an n8n workflow via database

    N8n API v1 does not support activation via REST API:
    - PUT requires full workflow but 'active' is read-only
    - PATCH method not allowed

    Solution: Update database directly
    """
    action = "activate" if active else "deactivate"
    logger.info(f"[N8N] {action.capitalize()}ing workflow {workflow_id} via database")

    try:
        import psycopg2
        from config import CONFIG

        # N8N PostgreSQL connection
        conn = psycopg2.connect(
            host=CONFIG.get('DB_HOST'),
            port=int(CONFIG.get('DB_PORT', '5432')),
            database='n8n',  # n8n database
            user=CONFIG.get('DB_USER'),
            password=CONFIG.get('DB_PASSWORD')
        )
        cursor = conn.cursor()

        # Update workflow active status in database
        cursor.execute(
            'UPDATE workflow_entity SET active = %s, "updatedAt" = NOW() WHERE id = %s',
            (active, workflow_id)
        )

        affected = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()

        if affected == 0:
            raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")

        logger.info(f"[N8N] Successfully {action}d workflow {workflow_id}")

        return {
            "id": workflow_id,
            "active": active,
            "message": f"Workflow {action}d successfully",
            "note": "Changes applied directly to database. Restart n8n or wait for cache refresh."
        }

    except Exception as e:
        logger.error(f"[N8N] Failed to {action} workflow: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to {action} workflow. Error: {str(e)}"
        )


@router.put("/workflows/{workflow_id}/edit-db")
async def edit_workflow_database(
    workflow_id: str,
    workflow_data: Dict[str, Any],
    user: Dict = Depends(get_current_user)
):
    """
    Edit workflow in database directly (bypass n8n API v1 limitations)

    N8N API v1 doesn't support PUT updates due to read-only fields.
    This endpoint updates the database directly for admin operations.

    Note: Changes are applied to database immediately but n8n service
    may need restart or cache refresh to reflect changes in UI.
    """
    logger.info(f"[N8N] Editing workflow {workflow_id} via database")

    try:
        import psycopg2
        from config import CONFIG
        import json

        # Connect to n8n database
        conn = psycopg2.connect(
            host=CONFIG.get('DB_HOST'),
            port=int(CONFIG.get('DB_PORT', '5432')),
            database='n8n',
            user=CONFIG.get('DB_USER'),
            password=CONFIG.get('DB_PASSWORD')
        )
        cursor = conn.cursor()

        # Only allow updating safe fields (not computed/system fields)
        update_parts = []
        update_values = []

        # Update name if provided
        if 'name' in workflow_data:
            update_parts.append('"name" = %s')
            update_values.append(workflow_data['name'])

        # Update nodes if provided
        if 'nodes' in workflow_data:
            update_parts.append('"nodes" = %s')
            update_values.append(json.dumps(workflow_data['nodes']))

        # Update connections if provided
        if 'connections' in workflow_data:
            update_parts.append('"connections" = %s')
            update_values.append(json.dumps(workflow_data['connections']))

        # Update settings if provided
        if 'settings' in workflow_data:
            update_parts.append('"settings" = %s')
            update_values.append(json.dumps(workflow_data['settings']))

        # Skip tags - n8n uses separate taggings table, not a column in workflow_entity
        # Tags are managed through n8n API, not direct database updates

        if not update_parts:
            raise HTTPException(status_code=400, detail="No valid fields to update")

        # Always update timestamp
        update_parts.append('"updatedAt" = NOW()')
        update_values.append(workflow_id)

        # Build and execute UPDATE query
        query = f'UPDATE workflow_entity SET {", ".join(update_parts)} WHERE id = %s'
        cursor.execute(query, update_values)

        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")

        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"[N8N] Successfully updated workflow {workflow_id} in database")

        return {
            "id": workflow_id,
            "message": "Workflow updated successfully in database",
            "note": "Changes applied to database. N8N service may need restart to reflect changes in UI."
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[N8N] Failed to edit workflow in database: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update workflow in database. Error: {str(e)}"
        )


@router.post("/workflows/{workflow_id}/trigger")
async def trigger_workflow(
    workflow_id: str,
    payload: Optional[Dict[str, Any]] = None,
    user: Dict = Depends(get_current_user)
):
    """Trigger an n8n workflow execution"""
    logger.info(f"[N8N] Triggering workflow {workflow_id} at {N8N_URL}")
    try:
        if payload is None:
            payload = {}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{N8N_URL}/webhook/{workflow_id}",
                json=payload,
                headers=get_n8n_headers(),
                auth=get_n8n_auth()
            )
            response.raise_for_status()
            logger.info(f"[N8N] Successfully triggered workflow {workflow_id}")
            return response.json()
    except Exception as e:
        raise handle_n8n_error(e, f"trigger workflow {workflow_id}")


@router.get("/health")
async def health_check():
    """
    Health check endpoint to test n8n connectivity and diagnose connection issues.
    Returns diagnostic information about n8n service connectivity.
    """
    diagnostics = {
        "n8n_url": N8N_URL,
        "timestamp": datetime.utcnow().isoformat(),
        "status": "unknown",
        "dns_resolution": "unknown",
        "http_connection": "unknown",
        "error": None
    }
    
    try:
        # Test DNS resolution and HTTP connection
        logger.info(f"[N8N Health] Testing connectivity to {N8N_URL}")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Try to connect to n8n health endpoint or root
            try:
                response = await client.get(
                    f"{N8N_URL}/healthz",
                    follow_redirects=True,
                    headers=get_n8n_headers(),
                    auth=get_n8n_auth()
                )
                diagnostics["http_connection"] = "success"
                diagnostics["http_status"] = response.status_code
                diagnostics["status"] = "healthy" if response.status_code == 200 else "degraded"
            except httpx.ConnectError as e:
                error_str = str(e)
                diagnostics["http_connection"] = "failed"
                diagnostics["status"] = "unavailable"
                
                # Check if it's a DNS error
                if "Name or service not known" in error_str or "[Errno -2]" in error_str:
                    diagnostics["dns_resolution"] = "failed"
                    diagnostics["error"] = "DNS resolution failed. Service discovery may not be configured."
                else:
                    diagnostics["dns_resolution"] = "success"
                    diagnostics["error"] = f"Connection failed: {error_str}"
            except httpx.TimeoutException:
                diagnostics["http_connection"] = "timeout"
                diagnostics["status"] = "unavailable"
                diagnostics["error"] = "Connection timeout"
            except Exception as e:
                diagnostics["http_connection"] = "error"
                diagnostics["status"] = "error"
                diagnostics["error"] = str(e)
        
        # If we got here, DNS likely works
        if diagnostics["dns_resolution"] == "unknown":
            diagnostics["dns_resolution"] = "success"
            
    except Exception as e:
        diagnostics["status"] = "error"
        diagnostics["error"] = str(e)
        logger.error(f"[N8N Health] Health check failed: {e}")
    
    # Return appropriate status code
    status_code = 200 if diagnostics["status"] == "healthy" else 503

    return diagnostics


@router.post("/admin/import-templates")
async def import_workflow_templates(user: Dict = Depends(get_current_user)):
    """
    Import workflow templates from n8n-workflow-templates/ folder into n8n

    Admin-only endpoint to bulk import template workflows.
    Reads all *.json files from the templates folder and creates workflows in n8n.
    Skips templates that already exist (by name match).

    Returns:
        - imported: List of successfully imported templates
        - skipped: List of templates that already exist
        - failed: List of templates that failed to import
    """
    import json
    from pathlib import Path

    logger.info("[N8N Admin] Starting template import")

    # Path to templates folder
    templates_dir = Path(__file__).parent.parent.parent / "n8n-workflow-templates"

    if not templates_dir.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Templates directory not found: {templates_dir}"
        )

    # Find all JSON files
    template_files = list(templates_dir.glob("*.json"))

    if not template_files:
        return {
            "message": "No template files found",
            "imported": [],
            "skipped": [],
            "failed": []
        }

    imported = []
    skipped = []
    failed = []

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Get existing workflows to check for duplicates
            logger.info("[N8N Admin] Fetching existing workflows")
            list_response = await client.get(
                f"{N8N_URL}/api/v1/workflows",
                headers=get_n8n_headers(),
                auth=get_n8n_auth()
            )
            list_response.raise_for_status()

            # Extract workflow names
            response_data = list_response.json()
            existing_workflows = response_data.get('data', []) if isinstance(response_data, dict) else response_data
            existing_names = {w.get('name') for w in existing_workflows}

            logger.info(f"[N8N Admin] Found {len(existing_workflows)} existing workflows")

            # Import each template
            for template_file in template_files:
                try:
                    logger.info(f"[N8N Admin] Processing {template_file.name}")

                    # Read template JSON
                    with open(template_file, 'r', encoding='utf-8') as f:
                        template_data = json.load(f)

                    workflow_name = template_data.get('name', 'Unnamed Workflow')

                    # Check if already exists
                    if workflow_name in existing_names:
                        logger.info(f"[N8N Admin] Skipping existing workflow: {workflow_name}")
                        skipped.append({
                            "file": template_file.name,
                            "name": workflow_name,
                            "reason": "Already exists"
                        })
                        continue

                    # Create workflow in n8n
                    create_response = await client.post(
                        f"{N8N_URL}/api/v1/workflows",
                        headers=get_n8n_headers(),
                        auth=get_n8n_auth(),
                        json=template_data
                    )
                    create_response.raise_for_status()

                    created_workflow = create_response.json()
                    workflow_id = created_workflow.get('id')

                    logger.info(f"[N8N Admin] Successfully imported: {workflow_name} (ID: {workflow_id})")
                    imported.append({
                        "file": template_file.name,
                        "name": workflow_name,
                        "id": workflow_id
                    })

                except json.JSONDecodeError as e:
                    logger.error(f"[N8N Admin] Invalid JSON in {template_file.name}: {e}")
                    failed.append({
                        "file": template_file.name,
                        "error": f"Invalid JSON: {str(e)}"
                    })

                except httpx.HTTPStatusError as e:
                    error_detail = e.response.text[:200] if hasattr(e.response, 'text') else str(e)
                    logger.error(f"[N8N Admin] HTTP error importing {template_file.name}: {error_detail}")
                    failed.append({
                        "file": template_file.name,
                        "error": f"HTTP {e.response.status_code}: {error_detail}"
                    })

                except Exception as e:
                    logger.error(f"[N8N Admin] Error importing {template_file.name}: {e}")
                    failed.append({
                        "file": template_file.name,
                        "error": str(e)
                    })

            # Summary
            result = {
                "message": f"Processed {len(template_files)} template(s)",
                "imported": imported,
                "skipped": skipped,
                "failed": failed,
                "summary": {
                    "total": len(template_files),
                    "imported_count": len(imported),
                    "skipped_count": len(skipped),
                    "failed_count": len(failed)
                }
            }

            logger.info(f"[N8N Admin] Import complete: {result['summary']}")
            return result

    except httpx.HTTPStatusError as e:
        logger.error(f"[N8N Admin] Failed to fetch existing workflows: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Failed to connect to n8n: {e.response.status_code}"
        )
    except Exception as e:
        logger.error(f"[N8N Admin] Template import failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Template import failed: {str(e)}"
        )


@router.get("/admin/debug-oauth/{user_email}")
async def debug_oauth_integration(user_email: str, user: Dict = Depends(get_current_user)):
    """
    Debug OAuth integrations for a specific user
    Admin-only endpoint to check database state
    """
    if not user.get('is_admin'):
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        from config import CONFIG

        conn = psycopg2.connect(
            host=CONFIG.get('DB_HOST'),
            port=int(CONFIG.get('DB_PORT', '5432')),
            database='prompts',  # MCP Server database
            user=CONFIG.get('DB_USER'),
            password=CONFIG.get('DB_PASSWORD'),
            cursor_factory=RealDictCursor
        )
        cursor = conn.cursor()

        # Check if oauth_integrations table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'oauth_integrations'
            );
        """)
        table_exists = cursor.fetchone()[0]

        if not table_exists:
            cursor.close()
            conn.close()
            return {
                "error": "oauth_integrations table does not exist",
                "user_email": user_email,
                "table_exists": False
            }

        # Get all integrations for this user
        cursor.execute("""
            SELECT user_id, provider, is_active, created_at, updated_at,
                   CASE WHEN access_token IS NOT NULL THEN true ELSE false END as has_token,
                   CASE WHEN refresh_token IS NOT NULL THEN true ELSE false END as has_refresh_token
            FROM oauth_integrations
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (user_email,))
        user_integrations = cursor.fetchall()

        # Get all google_drive integrations (to see if user email is different)
        cursor.execute("""
            SELECT user_id, is_active, created_at,
                   CASE WHEN access_token IS NOT NULL THEN true ELSE false END as has_token
            FROM oauth_integrations
            WHERE provider = 'google_drive'
            ORDER BY created_at DESC
            LIMIT 10
        """)
        all_drive_integrations = cursor.fetchall()

        # Check for similar emails (case-insensitive partial match)
        cursor.execute("""
            SELECT DISTINCT user_id, provider, is_active
            FROM oauth_integrations
            WHERE user_id ILIKE %s
            ORDER BY user_id
        """, (f"%{user_email.split('@')[0]}%",))
        similar_users = cursor.fetchall()

        cursor.close()
        conn.close()

        return {
            "user_email": user_email,
            "table_exists": True,
            "user_integrations": [dict(i) for i in user_integrations],
            "user_integrations_count": len(user_integrations),
            "all_google_drive_integrations": [dict(i) for i in all_drive_integrations],
            "similar_user_emails": [dict(i) for i in similar_users],
            "diagnosis": {
                "has_integrations": len(user_integrations) > 0,
                "has_google_drive": any(i['provider'] == 'google_drive' for i in user_integrations),
                "google_drive_active": any(
                    i['provider'] == 'google_drive' and i['is_active']
                    for i in user_integrations
                ),
                "google_drive_has_token": any(
                    i['provider'] == 'google_drive' and i['has_token']
                    for i in user_integrations
                )
            }
        }

    except Exception as e:
        logger.error(f"[Debug OAuth] Failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Debug OAuth failed: {str(e)}"
        )
