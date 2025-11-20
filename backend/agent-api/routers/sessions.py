"""
Sessions router
API endpoints for chat session management
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from services.auth_service import get_current_user
from services.sessions_service import (
    create_session,
    list_sessions,
    get_session_messages,
    update_session_title,
    delete_session
)

router = APIRouter(prefix="/agentcore", tags=["sessions"])


class SessionCreate(BaseModel):
    title: str = "New Chat"


class SessionResponse(BaseModel):
    session_id: str
    title: str
    created_at: int
    updated_at: int
    message_count: int


@router.post("/sessions", response_model=SessionResponse)
async def create_session_endpoint(
    request: SessionCreate,
    user: dict = Depends(get_current_user)
):
    """Create a new chat session"""
    result = await create_session(request.title, user)
    return SessionResponse(**result)


@router.get("/sessions")
async def list_sessions_endpoint(user: dict = Depends(get_current_user)):
    """List all sessions for current user"""
    return await list_sessions(user)


@router.get("/sessions/{session_id}/messages")
async def get_session_messages_endpoint(
    session_id: str,
    user: dict = Depends(get_current_user)
):
    """Get messages for a session"""
    return await get_session_messages(session_id, user)


@router.put("/sessions/{session_id}/title")
async def update_session_title_endpoint(
    session_id: str,
    title: str,
    user: dict = Depends(get_current_user)
):
    """Update session title"""
    return await update_session_title(session_id, title, user)


@router.delete("/sessions/{session_id}")
async def delete_session_endpoint(
    session_id: str,
    user: dict = Depends(get_current_user)
):
    """Delete a session"""
    return await delete_session(session_id, user)

