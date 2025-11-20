"""
OAuth router
API endpoints for OAuth integrations and state management
"""

from fastapi import APIRouter
from services.oauth_service import (
    save_integration,
    get_user_integrations,
    get_integration_token,
    delete_integration,
    save_oauth_state,
    get_oauth_state,
    delete_oauth_state,
    cleanup_expired_oauth_states
)

router = APIRouter(tags=["oauth"])


@router.post("/integrations/save")
@router.post("/mcp-server/integrations/save")
def save_integration_endpoint(integration: dict):
    """Save OAuth integration to database"""
    return save_integration(integration)


@router.get("/integrations/user/{user_id}")
@router.get("/mcp-server/integrations/user/{user_id}")
def get_user_integrations_endpoint(user_id: str):
    """Get all integrations for a user"""
    return get_user_integrations(user_id)


@router.get("/integrations/{user_id}/{provider}/token")
@router.get("/mcp-server/integrations/{user_id}/{provider}/token")
def get_integration_token_endpoint(user_id: str, provider: str):
    """Get access token for a specific integration"""
    return get_integration_token(user_id, provider)


@router.delete("/integrations/{user_id}/{provider}")
@router.delete("/mcp-server/integrations/{user_id}/{provider}")
def delete_integration_endpoint(user_id: str, provider: str):
    """Delete integration and revoke access token"""
    return delete_integration(user_id, provider)


@router.post("/oauth/state/save")
@router.post("/mcp-server/oauth/state/save")
def save_oauth_state_endpoint(state_data: dict):
    """Save OAuth state to database for persistent storage"""
    return save_oauth_state(state_data)


@router.get("/oauth/state/{state}")
@router.get("/mcp-server/oauth/state/{state}")
def get_oauth_state_endpoint(state: str):
    """Get OAuth state from database"""
    return get_oauth_state(state)


@router.delete("/oauth/state/{state}")
@router.delete("/mcp-server/oauth/state/{state}")
def delete_oauth_state_endpoint(state: str):
    """Delete OAuth state from database"""
    return delete_oauth_state(state)


@router.post("/oauth/state/cleanup")
@router.post("/mcp-server/oauth/state/cleanup")
def cleanup_expired_oauth_states_endpoint():
    """Clean up expired OAuth states"""
    return cleanup_expired_oauth_states()

