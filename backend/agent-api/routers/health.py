"""
Health check router
"""

from fastapi import APIRouter
from config import CONFIG
import os

router = APIRouter(tags=["health"])


@router.get("/api/config")
async def get_public_config():
    """Get public configuration (no auth required)"""
    MCP_URL = os.getenv('MCP_URL', 'http://mcp-server.aap.local:8001')
    return {
        "cognitoDomain": CONFIG.get('COGNITO_DOMAIN'),
        "cognitoClientId": CONFIG.get('COGNITO_CLIENT_ID'),
        "cognitoUserPoolId": CONFIG.get('COGNITO_USER_POOL_ID'),
        "cognitoRegion": CONFIG.get('COGNITO_REGION', 'ap-southeast-2'),
        "cognitoRedirectUri": CONFIG.get('COGNITO_REDIRECT_URI'),
        "cognitoScopes": "openid email profile",
        "apiBaseUrl": CONFIG.get('API_BASE_URL', ''),
        "agentcoreUrl": CONFIG.get('AGENTCORE_URL', ''),
        "mcpUrl": CONFIG.get('MCP_URL', MCP_URL),
        "environment": CONFIG.get('ENVIRONMENT', 'production')
    }


@router.get("/healthz")
@router.get("/health")
@router.get("/agentcore/healthz")
async def health():
    """Health check endpoint"""
    from tools.definitions import OPENAI_TOOLS
    from datetime import datetime
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "agent-api-openai-tools",
        "features": ["function_calling", "dynamodb_memory"],
        "tools_available": len(OPENAI_TOOLS)
    }

