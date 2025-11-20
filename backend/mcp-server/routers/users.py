"""
Users router
API endpoints for user management
"""

from fastapi import APIRouter, Header, HTTPException
from typing import Optional
from pydantic import BaseModel
from services.users_service import (
    user_login,
    list_users,
    update_user_roles,
    delete_user,
    set_admin_user
)

router = APIRouter(tags=["users"])


class UserLogin(BaseModel):
    email: str
    name: Optional[str] = None


class UserUpdate(BaseModel):
    roles: list
    is_admin: bool = False


@router.post("/users/login")
@router.post("/mcp-server/users/login")
def user_login_endpoint(request: UserLogin):
    """Get or create user on SSO login"""
    return user_login(request.email, request.name)


@router.get("/users")
@router.get("/mcp-server/users")
def list_users_endpoint(
    authorization: Optional[str] = Header(None),
    user_email: Optional[str] = Header(None, alias="X-User-Email")
):
    """List all users (admin only)"""
    return list_users(authorization, user_email)


@router.put("/users/{email}")
@router.put("/mcp-server/users/{email}")
def update_user_roles_endpoint(
    email: str,
    request: UserUpdate,
    user_email: Optional[str] = Header(None, alias="X-User-Email")
):
    """Update user roles (admin only)"""
    return update_user_roles(email, request.roles, request.is_admin, user_email)


@router.delete("/users/{email}")
@router.delete("/mcp-server/users/{email}")
def delete_user_endpoint(
    email: str,
    user_email: Optional[str] = Header(None, alias="X-User-Email")
):
    """Delete user (admin only)"""
    return delete_user(email, user_email)


@router.post("/admin/set-admin/{email}")
@router.post("/mcp-server/admin/set-admin/{email}")
def set_admin_user_endpoint(
    email: str,
    admin_key: Optional[str] = Header(None)
):
    """Set user as admin (requires admin key)"""
    return set_admin_user(email, admin_key)

