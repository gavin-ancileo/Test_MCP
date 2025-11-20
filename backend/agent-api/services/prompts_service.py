"""
Prompts service
Handles prompt template management
"""

import httpx
import json
from typing import Dict, Optional
from fastapi import HTTPException
import os

MCP_URL = os.getenv('MCP_URL', 'http://mcp-server.aap.local:8001')


async def create_prompt(prompt: dict) -> Dict:
    """Create new prompt - forward to MCP server"""
    try:
        print(f"[Note] [POST /api/prompts] Creating prompt: {prompt.get('code', 'unknown')}")
        print(f"[Note] [POST /api/prompts] Full prompt data: {json.dumps(prompt, indent=2)}")
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(f"{MCP_URL}/prompts", json=prompt)
            print(f"[Note] [POST /api/prompts] MCP server response: {response.status_code}")
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"[Note] [POST /api/prompts] Success: {result}")
                return result
            error_text = response.text[:200] if response.text else "No error message"
            print(f"[WARN] [POST /api/prompts] MCP server error: {response.status_code} - {error_text}")
            raise HTTPException(status_code=response.status_code, detail=f"MCP server returned {response.status_code}: {error_text}")
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: [POST /api/prompts] Failed to create prompt: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


async def get_prompts(user_email: Optional[str] = None) -> Dict:
    """Get prompts from MCP server with role-based filtering"""
    import json
    try:
        # Forward user_email to MCP server for role-based filtering
        params = {}
        if user_email:
            params['user_email'] = user_email

        print(f"[MCP] [Loading] Attempting to connect to MCP server...")
        print(f"[MCP] URL: {MCP_URL}/prompts")
        print(f"[MCP] Params: {params}")

        async with httpx.AsyncClient(timeout=10.0) as client:
            print(f"[MCP] [Request] Sending GET request...")
            response = await client.get(f"{MCP_URL}/prompts", params=params)
            print(f"[MCP] [OK] Response received: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"[MCP] [OK] Successfully fetched {data.get('count', 0)} prompts")
                return data
            else:
                print(f"[MCP] [WARNING] Non-200 status: {response.status_code}")
                return {"prompts": [], "count": 0}
    except httpx.ConnectError as e:
        print(f"[MCP] [ERROR] CONNECTION ERROR: Cannot connect to MCP server at {MCP_URL}")
        print(f"[MCP] [ERROR] Error details: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"prompts": [], "count": 0, "error": f"Connection failed: {str(e)}"}
    except httpx.TimeoutException as e:
        print(f"[MCP] [ERROR] TIMEOUT ERROR: MCP server did not respond within 10s")
        print(f"[MCP] [ERROR] Error details: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"prompts": [], "count": 0, "error": f"Timeout: {str(e)}"}
    except Exception as e:
        print(f"[MCP] [ERROR] UNEXPECTED ERROR: Failed to get prompts")
        print(f"[MCP] [ERROR] Error type: {type(e).__name__}")
        print(f"[MCP] [ERROR] Error details: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"prompts": [], "count": 0, "error": str(e)}


async def update_prompt(code: str, prompt: dict) -> Dict:
    """Update prompt - forward to MCP server"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.put(f"{MCP_URL}/prompts/{code}", json=prompt)
            if response.status_code in [200, 201]:
                return response.json()
            return {"success": False, "error": f"MCP server returned {response.status_code}"}
    except Exception as e:
        print(f"ERROR: Failed to update prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def delete_prompt(code: str) -> Dict:
    """Delete prompt - forward to MCP server"""
    try:
        print(f"[Note] [DELETE /api/prompts/{code}] Deleting prompt: {code}")
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.delete(f"{MCP_URL}/prompts/{code}")
            print(f"[Note] [DELETE /api/prompts/{code}] MCP server response: {response.status_code}")
            if response.status_code in [200, 204]:
                result = response.json() if response.text else {"success": True, "message": "Prompt deleted"}
                print(f"[Note] [DELETE /api/prompts/{code}] Success: {result}")
                return result
            error_text = response.text[:200] if response.text else "No error message"
            print(f"[WARN] [DELETE /api/prompts/{code}] MCP server error: {response.status_code} - {error_text}")
            raise HTTPException(status_code=response.status_code, detail=f"MCP server returned {response.status_code}: {error_text}")
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: [DELETE /api/prompts/{code}] Failed to delete prompt: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
