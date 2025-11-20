"""
AAP MCP Server - Refactored with modular services and routers
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
import json

# Import configuration and database
from config import CONFIG
from database import get_db

# Import validation utilities
from validation import extract_variables, validate_all_fields, fill_template, humanize_var_name

# Import routers
from routers import prompts, users, oauth, claimhub, insurance, health

# ============================================
# MODELS
# ============================================

class PromptCreate(BaseModel):
    code: str
    name: str
    categories: List[str]
    content: str
    output_folder: Optional[str] = ""

class TestPromptRequest(BaseModel):
    prompt_code: str
    variables: Dict
    generate_document: bool = False

class UserLogin(BaseModel):
    email: str
    name: Optional[str] = None

class UserUpdate(BaseModel):
    roles: List[str]
    is_admin: bool = False

# ============================================
# FASTAPI APP
# ============================================

app = FastAPI(
    title="AAP MCP Server",
    description="Prompt Management & Orchestration with strict validation",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(prompts.router)
app.include_router(users.router)
app.include_router(oauth.router)
app.include_router(claimhub.router)
app.include_router(insurance.router)
app.include_router(health.router)

# ============================================
# DATABASE CONNECTION CHECK
# ============================================

@app.on_event("startup")
async def startup():
    """Check database connection and seed prompts if empty"""
    try:
        conn = get_db()
        cur = conn.cursor()

        # Check prompt count
        cur.execute("SELECT COUNT(*) as count FROM prompts")
        count = cur.fetchone()['count']

        # We want exactly 40 prompts
        if count < 40:
            if count > 0:
                print(f"Found only {count} prompts (expected 40). Clearing and re-seeding...")
                cur.execute("TRUNCATE TABLE prompts RESTART IDENTITY CASCADE")
                conn.commit()

            print("Auto-seeding 40 prompts...")
            try:
                # Try to load from SQL file first
                sql_file = '/app/40-prompts.sql'
                if os.path.exists(sql_file):
                    print(f"Loading prompts from {sql_file}")
                    with open(sql_file, 'r', encoding='utf-8') as f:
                        sql_content = f.read()
                    cur.execute(sql_content)
                    conn.commit()
                    print("Executed 40-prompts.sql successfully")
                else:
                    print(f"SQL file not found at {sql_file}")
                    # Try Python import as fallback
                    try:
                        from prompts_data import PROMPTS_DATA
                        print(f"Using prompts_data.py with {len(PROMPTS_DATA)} prompts")
                        for code, name, categories, content in PROMPTS_DATA:
                            cur.execute("""
                                INSERT INTO prompts (code, name, categories, content)
                                VALUES (%s, %s, %s, %s)
                            """, (code, name, categories, content))
                        conn.commit()
                        print("Seeded prompts from prompts_data.py")
                    except ImportError:
                        print("Could not import prompts_data.py")
            except Exception as seed_error:
                print(f"Error seeding prompts: {seed_error}")
                import traceback
                traceback.print_exc()

        # Verify final count
        cur.execute("SELECT COUNT(*) as count FROM prompts")
        final_count = cur.fetchone()['count']
        print(f"OK: Database connected - {final_count} prompts available")
        conn.close()
    except Exception as e:
        print(f"ERROR: Database connection failed: {e}")
        import traceback
        traceback.print_exc()

# ============================================
# ADDITIONAL ENDPOINTS (Not in routers)
# ============================================

@app.post("/test-prompt")
@app.post("/agentcore/test-prompt")
def test_prompt(request: TestPromptRequest):
    """
    Test prompt with STRICT VALIDATION
    All required fields must be provided and valid (no placeholders)
    """
    try:
        from services.prompts_service import get_prompt
        
        # Get prompt
        prompt = get_prompt(request.prompt_code)
        
        # Extract required variables
        variables = extract_variables(prompt['content'])
        required = [v['name'] for v in variables if v.get('required', True)]
        
        # STRICT VALIDATION
        is_valid, missing = validate_all_fields(request.variables, required)
        
        if not is_valid:
            missing_readable = [humanize_var_name(f) for f in missing]
            return {
                "success": False,
                "error": "Missing required fields",
                "missing_fields": missing_readable,
                "message": f"Please provide: {', '.join(missing_readable)}"
            }
        
        # Fill template
        filled = fill_template(prompt['content'], request.variables)
        
        return {
            "success": True,
            "prompt_name": prompt['name'],
            "filled_content": filled,
            "variables_used": list(request.variables.keys()),
            "ai_response": f"OK: Generated: {prompt['name']}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: Error testing prompt: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/admin/seed-3-test-prompts")
@app.post("/admin/seed-3-test-prompts")
def seed_3_test_prompts():
    """Quick seed 3 test prompts for testing"""
    try:
        conn = get_db()
        cur = conn.cursor()
        
        # Clear existing test prompts
        cur.execute("DELETE FROM prompts WHERE code LIKE 'test_%'")
        conn.commit()
        
        # 3 test prompts
        test_prompts = [
            ('test_1', 'Test Prompt 1', '["test"]', 'Test content 1 with {{variable1}}'),
            ('test_2', 'Test Prompt 2', '["test"]', 'Test content 2 with {{variable2}}'),
            ('test_3', 'Test Prompt 3', '["test"]', 'Test content 3 with {{variable3}}')
        ]
        
        # Insert 3 test prompts
        for code, name, categories, content in test_prompts:
            cur.execute("""
                INSERT INTO prompts (code, name, categories, content)
                VALUES (%s, %s, %s, %s)
            """, (code, name, categories, content))
        
        conn.commit()
        
        # Verify
        cur.execute("SELECT COUNT(*) as count FROM prompts WHERE code LIKE 'test_%'")
        test_count = cur.fetchone()['count']
        
        cur.execute("SELECT COUNT(*) as count FROM prompts")
        total_count = cur.fetchone()['count']
        
        conn.close()
        return {
            "success": True,
            "message": f"Seeded {test_count} test prompts successfully",
            "test_count": test_count,
            "total_count": total_count
        }
    except Exception as e:
        print(f"Error seeding test prompts: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

# ============================================
# N8N WORKFLOW ENDPOINTS
# ============================================

@app.post("/n8n/workflow/{workflow_id}/trigger")
@app.post("/mcp-server/n8n/workflow/{workflow_id}/trigger")
async def trigger_n8n_workflow(workflow_id: str, payload: dict):
    """Trigger n8n workflow"""
    try:
        n8n_url = CONFIG.get('N8N_URL', os.getenv('N8N_URL', 'http://localhost:5678'))
        import httpx
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{n8n_url}/webhook/{workflow_id}",
                json=payload
            )
            if response.status_code in [200, 201]:
                return {
                    "success": True,
                    "workflow_id": workflow_id,
                    "response": response.json() if response.text else {}
                }
            else:
                return {
                    "success": False,
                    "error": f"Workflow returned status {response.status_code}: {response.text}"
                }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/tools/n8n/trigger")
async def api_n8n_trigger_workflow(request: dict):
    """Trigger n8n workflow (MCP tool interface)"""
    workflow_id = request.get('workflow_id') or request.get('workflowId')
    payload = request.get('payload', {})
    
    if not workflow_id:
        return {
            "success": False,
            "error": "workflow_id is required"
        }
    
    return await trigger_n8n_workflow(workflow_id, payload)

# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    import uvicorn
    print("[Start] Starting MCP Server...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
