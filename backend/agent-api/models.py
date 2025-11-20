"""
Pydantic models for Agent API request/response schemas
"""

from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str
    conversationId: str = "default"

class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    message: str
    conversationId: str
    timestamp: str
    source: str = "openai"

class SessionCreate(BaseModel):
    """Request model for creating a new session"""
    title: str = "New Conversation"

class SessionResponse(BaseModel):
    """Response model for session operations"""
    session_id: str
    title: str
    created_at: int
    updated_at: int
    message_count: int = 0

