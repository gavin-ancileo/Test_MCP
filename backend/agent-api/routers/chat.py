"""
Chat router
API endpoints for chat functionality
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from datetime import datetime
from services.auth_service import get_current_user
from services.chat_service import process_chat

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    conversationId: str = "default"


class ChatResponse(BaseModel):
    message: str
    conversationId: str
    timestamp: str
    source: str = "openai"


@router.post("/agentcore/run", response_model=ChatResponse)
@router.post("/run", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    user: dict = Depends(get_current_user)
):
    """Main chat endpoint with function calling"""
    result = await process_chat(request.message, request.conversationId, user)
    return ChatResponse(**result)

