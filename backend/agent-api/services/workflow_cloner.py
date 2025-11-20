"""
Workflow Cloner Service
Handles cloning template workflows for individual users with OAuth credential injection
"""

import httpx
import hashlib
import os
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

N8N_URL = os.getenv("N8N_URL", "http://aap-n8n.aap.local:5678")
N8N_API_KEY = os.getenv("N8N_API_KEY", "")

def get_n8n_headers() -> Dict[str, str]:
    """Get headers for n8n API requests"""
    headers = {}
    if N8N_API_KEY:
        headers["X-N8N-API-KEY"] = N8N_API_KEY
    return headers


def generate_user_hash(user_email: str) -> str:
    """Generate short hash from user email for unique identifiers"""
    return hashlib.md5(user_email.encode()).hexdigest()[:8]


async def clone_workflow_for_user(
    template_workflow_id: str,
    user_email: str,
    oauth_tokens: Dict[str, str]
) -> tuple[str, Optional[str], str]:
    """
    Clone a template workflow for a specific user

    Args:
        template_workflow_id: ID of the template workflow to clone
        user_email: User's email address
        oauth_tokens: Dict of {provider: access_token} for OAuth integrations

    Returns:
        Tuple of (cloned_workflow_id, webhook_url, trigger_type)
        - webhook_url will be None for schedule/manual workflows
        - trigger_type: 'webhook', 'schedule', or 'manual'
    """
    try:
        user_hash = generate_user_hash(user_email)

        async with httpx.AsyncClient(timeout=30.0) as client:
            # Get template workflow
            logger.info(f"[Clone] Fetching template workflow {template_workflow_id}")
            response = await client.get(
                f"{N8N_URL}/api/v1/workflows/{template_workflow_id}",
                headers=get_n8n_headers()
            )
            response.raise_for_status()
            template = response.json()

            # Prepare cloned workflow - only include fields that n8n accepts for creation
            # DO NOT include: id, active, createdAt, updatedAt, versionId (read-only fields)
            template_name = template.get("name", "Workflow")

            # Build clean payload with only required/accepted fields
            cloned_workflow = {
                "name": f"{template_name} - {user_email}",
                "nodes": template.get("nodes", []),
                "connections": template.get("connections", {})
            }

            # Only add settings if they exist and are valid (some settings fields are read-only)
            if template.get("settings"):
                # Copy settings but exclude any read-only fields
                settings = template.get("settings", {})
                # Filter out any potential read-only fields in settings
                safe_settings = {
                    k: v for k, v in settings.items()
                    if k not in ['id', 'createdAt', 'updatedAt']
                }
                if safe_settings:
                    cloned_workflow["settings"] = safe_settings

            # Tags must be array of tag IDs (not objects) or simple strings
            # Skip tags for now to avoid format issues
            # cloned_workflow["tags"] = []

            # Detect trigger type from workflow nodes
            trigger_type = "manual"  # Default to manual if no trigger found
            has_webhook = False
            original_path = "webhook"  # Default fallback

            for node in cloned_workflow["nodes"]:
                node_type = node.get("type", "")
                if node_type == "n8n-nodes-base.webhook":
                    trigger_type = "webhook"
                    has_webhook = True
                elif node_type == "n8n-nodes-base.scheduleTrigger":
                    trigger_type = "schedule"
                elif node_type == "n8n-nodes-base.manualTrigger":
                    trigger_type = "manual"

            logger.info(f"[Clone] Detected trigger type: {trigger_type}")

            # Update webhook path to be user-specific and inject user context
            webhook_path_suffix = f"{user_hash}"

            for node in cloned_workflow["nodes"]:
                # Handle webhook nodes - make path unique per user
                if node.get("type") == "n8n-nodes-base.webhook":
                    original_path = node.get("parameters", {}).get("path", "webhook")
                    node["parameters"]["path"] = f"{original_path}-{webhook_path_suffix}"

                # Handle HTTP Request nodes - inject user_id for MCP calls
                elif node.get("type") == "n8n-nodes-base.httpRequest":
                    if "parameters" not in node:
                        node["parameters"] = {}

                    # Inject user_id into body parameters for MCP tool calls
                    if "bodyParametersJson" not in node["parameters"]:
                        node["parameters"]["bodyParametersJson"] = f'{{"user_id": "{user_email}"}}'
                    else:
                        # Parse existing JSON and add user_id
                        try:
                            import json
                            existing_params = json.loads(node["parameters"]["bodyParametersJson"])
                            existing_params["user_id"] = user_email
                            node["parameters"]["bodyParametersJson"] = json.dumps(existing_params)
                        except:
                            node["parameters"]["bodyParametersJson"] = f'{{"user_id": "{user_email}"}}'

                # Handle Email Send nodes - set recipient to user's email
                elif node.get("type") == "n8n-nodes-base.emailSend":
                    if "parameters" not in node:
                        node["parameters"] = {}
                    node["parameters"]["toEmail"] = user_email

                    # Also inject user_email into fromEmail if not set
                    if "fromEmail" not in node["parameters"]:
                        node["parameters"]["fromEmail"] = "noreply@ancileo.com"

            # Create cloned workflow
            logger.info(f"[Clone] Creating cloned workflow for {user_email}")
            logger.debug(f"[Clone] Payload keys: {list(cloned_workflow.keys())}")
            logger.debug(f"[Clone] Payload name: {cloned_workflow.get('name')}")
            logger.debug(f"[Clone] Payload has {len(cloned_workflow.get('nodes', []))} nodes")

            try:
                create_response = await client.post(
                    f"{N8N_URL}/api/v1/workflows",
                    json=cloned_workflow,
                    headers=get_n8n_headers()
                )
                create_response.raise_for_status()
                cloned = create_response.json()
            except httpx.HTTPStatusError as e:
                # Log detailed error for 400 Bad Request
                logger.error(f"[Clone] HTTP {e.response.status_code} error from n8n")
                logger.error(f"[Clone] Response body: {e.response.text[:1000]}")
                logger.error(f"[Clone] Request payload keys: {list(cloned_workflow.keys())}")
                raise

            cloned_id = cloned.get("id")

            # Activate the cloned workflow via API
            logger.info(f"[Clone] Activating workflow {cloned_id}")
            try:
                activate_response = await client.post(
                    f"{N8N_URL}/api/v1/workflows/{cloned_id}/activate",
                    headers=get_n8n_headers()
                )
                activate_response.raise_for_status()
                logger.info(f"[Clone] Successfully activated workflow {cloned_id} via API")
            except httpx.HTTPStatusError as e:
                logger.warning(f"[Clone] Failed to activate via API (HTTP {e.response.status_code}): {e.response.text[:500]}")
                # Fallback to database activation
                logger.info(f"[Clone] Falling back to database activation")
                import psycopg2
                from config import CONFIG

                conn = psycopg2.connect(
                    host=CONFIG.get('DB_HOST'),
                    port=int(CONFIG.get('DB_PORT', '5432')),
                    database='n8n',
                    user=CONFIG.get('DB_USER'),
                    password=CONFIG.get('DB_PASSWORD')
                )
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE workflow_entity SET active = %s WHERE id = %s',
                    (True, cloned_id)
                )
                conn.commit()
                cursor.close()
                conn.close()
                logger.info(f"[Clone] Successfully activated via database")

            # Generate webhook URL only for webhook-based workflows
            webhook_url = None
            if trigger_type == "webhook" and has_webhook:
                webhook_url = f"{N8N_URL}/webhook/{original_path}-{webhook_path_suffix}"
                logger.info(f"[Clone] Webhook URL: {webhook_url}")
            else:
                logger.info(f"[Clone] No webhook URL (trigger type: {trigger_type})")

            logger.info(f"[Clone] Successfully cloned workflow {template_workflow_id} -> {cloned_id}")

            return cloned_id, webhook_url, trigger_type

    except Exception as e:
        logger.error(f"[Clone] Failed to clone workflow: {e}")
        raise


async def delete_cloned_workflow(cloned_workflow_id: str):
    """Delete a user's cloned workflow with graceful shutdown"""
    try:
        logger.info(f"[Clone] Deleting cloned workflow {cloned_workflow_id}")
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Step 1: Deactivate workflow first to stop new executions
            try:
                logger.info(f"[Clone] Deactivating workflow {cloned_workflow_id} before deletion")
                deactivate_response = await client.post(
                    f"{N8N_URL}/api/v1/workflows/{cloned_workflow_id}/deactivate",
                    headers=get_n8n_headers()
                )
                deactivate_response.raise_for_status()
                logger.info(f"[Clone] Workflow deactivated successfully")
            except httpx.HTTPStatusError as e:
                # Workflow may already be inactive, that's OK
                logger.warning(f"[Clone] Deactivate returned HTTP {e.response.status_code} (may already be inactive)")
            except Exception as e:
                logger.warning(f"[Clone] Failed to deactivate (continuing anyway): {e}")

            # Step 2: Wait for in-flight executions to complete
            logger.info(f"[Clone] Waiting 2 seconds for in-flight executions to complete...")
            import asyncio
            await asyncio.sleep(2)

            # Step 3: Delete the workflow
            logger.info(f"[Clone] Deleting workflow {cloned_workflow_id}")
            response = await client.delete(
                f"{N8N_URL}/api/v1/workflows/{cloned_workflow_id}",
                headers=get_n8n_headers()
            )
            response.raise_for_status()
            logger.info(f"[Clone] Successfully deleted workflow {cloned_workflow_id}")
    except Exception as e:
        logger.error(f"[Clone] Failed to delete workflow: {e}")
        raise
