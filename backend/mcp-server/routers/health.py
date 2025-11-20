"""
Health check router
"""

from fastapi import APIRouter
from config import CONFIG
import os

router = APIRouter(tags=["health"])


@router.get("/health")
@router.get("/healthz")
@router.get("/mcp-server/health")
def health():
    """Health check endpoint"""
    return {"status": "ok", "service": "mcp-server"}


@router.get("/mcp/health")
@router.get("/agentcore/health")
def health_with_prefix():
    """Health check endpoint with prefix"""
    return {"status": "ok", "service": "mcp-server"}


@router.get("/debug/config")
def debug_config():
    """Show current configuration (for debugging)"""
    return {
        "db_host": CONFIG['DB_HOST'],
        "db_port": CONFIG['DB_PORT'],
        "db_name": CONFIG['DB_NAME'],
        "db_user": CONFIG['DB_USER'],
        "environment": os.getenv("ENVIRONMENT", "local")
    }

