"""
Pydantic models for MCP Server request/response schemas
"""

from pydantic import BaseModel
from typing import List, Optional, Dict

class PromptCreate(BaseModel):
    """Request model for creating/updating a prompt"""
    code: str
    name: str
    categories: List[str]
    content: str
    output_folder: Optional[str] = ""

class TestPromptRequest(BaseModel):
    """Request model for testing a prompt with variables"""
    prompt_code: str
    variables: Dict
    generate_document: bool = False

class UserLogin(BaseModel):
    """Request model for user login"""
    email: str
    name: Optional[str] = None

class UserUpdate(BaseModel):
    """Request model for updating user roles"""
    roles: List[str]
    is_admin: bool = False

class MigrationRequest(BaseModel):
    """Request model for database migration (admin only)"""
    sql_content: str
    admin_key: str = "MIGRATE_2025_SECRET"

class ClaimHubQuery(BaseModel):
    """Request model for ClaimHub database queries"""
    query: str
    user_id: str

