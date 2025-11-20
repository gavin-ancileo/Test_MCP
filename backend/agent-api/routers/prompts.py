"""
Prompts router
API endpoints for prompt template management
"""

from fastapi import APIRouter, Depends, Query
from typing import Optional
from services.auth_service import get_current_user
from services.prompts_service import create_prompt, get_prompts, update_prompt, delete_prompt

router = APIRouter(prefix="/api", tags=["prompts"])


@router.post("/prompts")
@router.post("/agentcore/prompts")
async def create_prompt_endpoint(
    prompt: dict,
    user: dict = Depends(get_current_user)
):
    """Create new prompt - forward to MCP server"""
    return await create_prompt(prompt)


@router.get("/prompts")
@router.get("/agentcore/prompts")
async def get_prompts_endpoint(
    user: dict = Depends(get_current_user),
    user_email: Optional[str] = Query(None)
):
    """Get prompts from MCP server with role-based filtering"""
    # Use provided user_email or fallback to user's email
    email = user_email or user.get('email')
    return await get_prompts(email)


@router.put("/prompts/{code}")
@router.put("/agentcore/prompts/{code}")
async def update_prompt_endpoint(
    code: str,
    prompt: dict,
    user: dict = Depends(get_current_user)
):
    """Update prompt - forward to MCP server"""
    return await update_prompt(code, prompt)


@router.delete("/prompts/{code}")
@router.delete("/agentcore/prompts/{code}")
async def delete_prompt_endpoint(
    code: str,
    user: dict = Depends(get_current_user)
):
    """Delete prompt - forward to MCP server"""
    return await delete_prompt(code)

