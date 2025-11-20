"""
Prompts router
API endpoints for prompt template management
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from pydantic import BaseModel
from services.prompts_service import (
    get_prompts,
    get_prompt,
    create_prompt,
    update_prompt,
    delete_prompt,
    search_prompts_by_intent,
    validate_prompt_variables
)
from validation import fill_template, validate_all_fields, extract_variables

router = APIRouter(tags=["prompts"])


class PromptCreate(BaseModel):
    code: str
    name: str
    categories: list
    content: str
    output_folder: Optional[str] = ""


@router.get("/prompts")
def get_prompts_endpoint(user_email: Optional[str] = Query(None)):
    """List all prompts (filtered by user roles if user_email provided)"""
    return get_prompts(user_email)


@router.get("/prompts/{code}")
def get_prompt_endpoint(code: str):
    """Get single prompt by code"""
    return get_prompt(code)


@router.post("/prompts")
def create_prompt_endpoint(prompt: PromptCreate):
    """Create new prompt"""
    return create_prompt(prompt.dict())


@router.put("/prompts/{code}")
def update_prompt_endpoint(code: str, prompt: PromptCreate):
    """Update existing prompt"""
    return update_prompt(code, prompt.dict())


@router.delete("/prompts/{code}")
def delete_prompt_endpoint(code: str):
    """Delete prompt"""
    return delete_prompt(code)


@router.get("/mcp-server/prompts/search/intent")
def search_prompts_by_intent_endpoint(query: str = Query(...)):
    """Search prompts by user intent/query"""
    return search_prompts_by_intent(query)


@router.get("/mcp-server/prompts/{code}/validate")
def validate_prompt_variables_endpoint(code: str):
    """Validate prompt variables and return user-friendly message"""
    return validate_prompt_variables(code)

