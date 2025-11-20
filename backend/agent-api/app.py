"""
AAP Agent API - OpenAI with Function Calling + DynamoDB
Refactored to use modular services and routers
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import oauth_integrations
from oauth_integrations import router as oauth_router
import os

# Import configuration
from config import CONFIG

# Import routers
from routers import prompts, sessions, chat, health, n8n, user_workflows

# Import services for startup
from services.auth_service import COGNITO_KEYS, refresh_cognito_keys, get_current_user
from tools.definitions import OPENAI_TOOLS

# ============================================
# DEPENDENCY INJECTION
# ============================================

# Inject CONFIG secrets into os.environ for oauth_integrations module
for key, value in CONFIG.items():
    if isinstance(value, str):
        os.environ[key] = value
    elif isinstance(value, bool):
        os.environ[key] = str(value).lower()
    elif value is not None:
        os.environ[key] = str(value)

# CRITICAL: Inject get_current_user into oauth_integrations callable wrapper
# This MUST happen BEFORE app.include_router(oauth_router) to ensure FastAPI
# sees the correct function signature instead of the wrapper's *args, **kwargs
oauth_integrations.get_current_user.set_func(get_current_user)

# ============================================
# FASTAPI APP
# ============================================

app = FastAPI(title="AAP Agent API - OpenAI with Tools")

# Include routers (dependency already injected above)
app.include_router(oauth_router)
app.include_router(prompts.router)
app.include_router(sessions.router)
app.include_router(chat.router)
app.include_router(health.router)
app.include_router(n8n.router)
app.include_router(user_workflows.router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    print("\n" + "="*50)
    print("[Start] AAP Agent API Starting...")
    print(f"[Env] Environment: {os.getenv('ENVIRONMENT', 'local')}")
    
    MCP_URL = os.getenv('MCP_URL', 'http://mcp-server.aap.local:8001')
    print(f"[Link] MCP Server: {MCP_URL}")
    print(f"[AI] Using: OpenAI with Function Calling")
    print(f"[DB] Conversations: DynamoDB ({CONFIG.get('DYNAMODB_TABLE')})")

    # Validate Cognito configuration
    cognito_pool_id = CONFIG.get('COGNITO_USER_POOL_ID', '')
    cognito_region = CONFIG.get('COGNITO_REGION', 'ap-southeast-2')
    if cognito_pool_id:
        print(f"[Auth] Cognito User Pool ID: {cognito_pool_id}")
        print(f"[Auth] Cognito Region: {cognito_region}")
        
        # Verify Cognito keys are loaded
        if COGNITO_KEYS:
            available_kids = [k.get('kid') for k in COGNITO_KEYS]
            print(f"[Auth] Cognito Keys Loaded: {len(COGNITO_KEYS)} key(s) available")
            print(f"[Auth] Available Key IDs: {available_kids}")
        else:
            print(f"[Auth] WARNING: No Cognito keys loaded! Attempting to refresh...")
            refresh_cognito_keys(force=True)
            if COGNITO_KEYS:
                available_kids = [k.get('kid') for k in COGNITO_KEYS]
                print(f"[Auth] Cognito Keys Loaded: {len(COGNITO_KEYS)} key(s) available after refresh")
                print(f"[Auth] Available Key IDs: {available_kids}")
            else:
                print(f"[Auth] ERROR: Failed to load Cognito keys! Authentication may fail.")
    else:
        print(f"[Auth] WARNING: COGNITO_USER_POOL_ID not configured! Authentication will fail.")

    # Validate OAuth configuration
    oauth_providers = []
    if os.getenv("GITHUB_CLIENT_ID") and os.getenv("GITHUB_CLIENT_SECRET"):
        oauth_providers.append("GitHub")
    if os.getenv("JIRA_CLIENT_ID") and os.getenv("JIRA_CLIENT_SECRET"):
        oauth_providers.append("Jira")
    if os.getenv("GOOGLE_CLIENT_ID") and os.getenv("GOOGLE_CLIENT_SECRET"):
        oauth_providers.append("Google Drive")

    if oauth_providers:
        print(f"[Auth] OAuth Providers: {', '.join(oauth_providers)}")
    else:
        print("WARNING:  No OAuth providers configured")

    # Validate N8N configuration
    print("\n" + "="*50)
    N8N_URL = os.getenv('N8N_URL', 'http://aap-n8n.aap.local:5678')
    N8N_API_KEY = os.getenv('N8N_API_KEY', '')

    print(f"[N8N] N8N URL: {N8N_URL}")
    if N8N_API_KEY:
        print(f"[N8N] API Key configured: Yes (key: {N8N_API_KEY[:20]}...)")
    else:
        print(f"[N8N] WARNING: N8N_API_KEY not configured! Workflow operations may fail.")

    # Test N8N connectivity
    print("[N8N] Testing connectivity to N8N server...")
    try:
        import httpx
        headers = {}
        if N8N_API_KEY:
            headers["X-N8N-API-KEY"] = N8N_API_KEY

        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{N8N_URL}/api/v1/workflows", headers=headers)
            if response.status_code == 200:
                workflows_count = len(response.json().get('data', []))
                print(f"[N8N] SUCCESS: Connected ({workflows_count} workflows found)")
            elif response.status_code == 401:
                print(f"[N8N] ERROR: Authentication failed! Check N8N_API_KEY.")
            else:
                print(f"[N8N] WARNING: Connected but returned status {response.status_code}")
    except Exception as e:
        print(f"[N8N] ERROR: Connection failed: {e}")

    # Test MCP server connectivity
    print("\n" + "="*50)
    print("[MCP] Testing connectivity to MCP server...")
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{MCP_URL}/health")
            if response.status_code == 200:
                print(f"[MCP] SUCCESS: Connected successfully")
            else:
                print(f"[MCP] WARNING: Connected but returned status {response.status_code}")
    except Exception as e:
        print(f"[MCP] ERROR: Connection failed: {e}")

    # Auto-import workflow templates on startup
    print("\n" + "="*50)
    print("[N8N] Auto-importing workflow templates...")
    try:
        from routers.n8n import import_workflow_templates
        result = await import_workflow_templates()
        templates_imported = result.get("templates_imported", [])
        templates_updated = result.get("templates_updated", [])

        if templates_imported:
            print(f"[N8N] SUCCESS: Imported {len(templates_imported)} new template(s)")
            for template in templates_imported:
                print(f"[N8N]   - {template['name']} (ID: {template['id']})")

        if templates_updated:
            print(f"[N8N] SUCCESS: Updated {len(templates_updated)} template(s)")
            for template in templates_updated:
                print(f"[N8N]   - {template['name']} (ID: {template['id']})")

        if not templates_imported and not templates_updated:
            print(f"[N8N] All templates already up to date")
    except Exception as e:
        print(f"[N8N] WARNING: Failed to auto-import templates: {e}")
        print(f"[N8N] Templates can be imported manually via /admin/import-templates")

    print(f"\n[Tools] Available OpenAI tools: {len(OPENAI_TOOLS)}")
    print("="*50 + "\n")


if __name__ == "__main__":
    import uvicorn
    print("[Start] Starting Agent API with OpenAI Function Calling...")
    uvicorn.run(app, host="0.0.0.0", port=8080)
