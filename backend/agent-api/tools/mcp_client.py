"""
MCP Client Helper
Manages connections to native MCP servers (GitHub, Drive, etc.)
"""

import os
import asyncio
import httpx
from typing import Dict, Optional, Any
from contextlib import asynccontextmanager

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("[MCP Client] WARNING: MCP library not installed. Install with: pip install mcp")

# Import configuration from Secrets Manager
try:
    from config import CONFIG
    USE_SECRETS_MANAGER = True
except ImportError:
    CONFIG = {}
    USE_SECRETS_MANAGER = False
    print("[MCP Client] WARNING: Could not import CONFIG, using environment variables only")

# Company MCP Server URL for OAuth token retrieval
MCP_URL = CONFIG.get('MCP_URL') or os.getenv('MCP_URL', 'http://mcp-server.aap.local:8001')


async def get_user_oauth_token(user_id: str, provider: str, max_retries: int = 3) -> Optional[str]:
    """
    Get OAuth token for user from Company MCP Server with retry logic

    Args:
        user_id: User identifier (email or sub)
        provider: Provider name ('github', 'jira', 'drive')
        max_retries: Maximum number of retry attempts

    Returns:
        OAuth token if found, None otherwise
    """
    import httpx

    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Map provider names: frontend uses 'drive' but API uses 'google_drive'
                api_provider = 'drive' if provider == 'google_drive' else provider
                response = await client.get(
                    f"{MCP_URL}/integrations/{user_id}/{api_provider}/token"
                )
                if response.status_code == 200:
                    data = response.json()
                    token = data.get('access_token')
                    if token:
                        print(f"[MCP Client] Successfully retrieved {provider} token for user {user_id}")
                        return token
                    else:
                        print(f"[MCP Client] Token data missing access_token field for {provider}")
                        return None
                elif response.status_code == 404:
                    print(f"[MCP Client] {provider.title()} not connected for user {user_id}. Please connect in Settings > Integrations.")
                    return None
                else:
                    print(f"[MCP Client] Token fetch failed with status {response.status_code} for {provider}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(0.5 * (attempt + 1))  # Exponential backoff
                        continue
                    return None
        except httpx.TimeoutException:
            print(f"[MCP Client] Timeout fetching {provider} token (attempt {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                await asyncio.sleep(0.5 * (attempt + 1))
                continue
            return None
        except Exception as e:
            print(f"[MCP Client] Error fetching {provider} token (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(0.5 * (attempt + 1))
                continue
            return None

    return None


@asynccontextmanager
async def get_github_mcp_session(user_id: Optional[str] = None):
    """
    Get GitHub MCP server session (using Python wrapper)

    This uses a pure Python wrapper for GitHub API (like Jira) instead of spawning
    external Node.js processes. This ensures consistent architecture and eliminates
    external dependencies (npx, Docker).

    Args:
        user_id: User ID to get per-user OAuth token

    Yields:
        ClientSession for GitHub MCP server
    """
    if not MCP_AVAILABLE:
        raise RuntimeError("MCP library not available. Install with: pip install mcp")

    # Get GitHub OAuth token from Company MCP Server
    github_token = await get_user_oauth_token(user_id, 'github')
    if not github_token:
        raise ValueError(f"GitHub not connected for user {user_id}. Please connect in Settings > Integrations.")

    # Use Python MCP server wrapper for GitHub (same pattern as Jira)
    from .github_mcp_wrapper import get_github_mcp_wrapper_session
    async with get_github_mcp_wrapper_session(user_id, github_token) as session:
        yield session


async def call_github_mcp_tool(tool_name: str, arguments: Dict[str, Any], user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Call a GitHub MCP tool with enhanced error handling

    Args:
        tool_name: Name of the MCP tool to call
        arguments: Tool arguments
        user_id: Optional user ID for per-user token

    Returns:
        Tool result as dictionary

    Raises:
        RuntimeError: If MCP client is not available
        ValueError: If token is missing
        Exception: For other tool execution errors
    """
    try:
        async with get_github_mcp_session(user_id) as session:
            result = await asyncio.wait_for(
                session.call_tool(tool_name, arguments),
                timeout=30.0  # 30 second timeout
            )
            print(f"[MCP Client] Successfully called GitHub tool: {tool_name}")
            return result
    except asyncio.TimeoutError:
        error_msg = f"GitHub MCP tool '{tool_name}' timed out after 30 seconds"
        print(f"[MCP Client] {error_msg}")
        raise Exception(error_msg)
    except ValueError as e:
        # Token or configuration error
        print(f"[MCP Client] Configuration error for GitHub tool {tool_name}: {e}")
        raise
    except RuntimeError as e:
        # MCP library not available
        print(f"[MCP Client] Runtime error for GitHub tool {tool_name}: {e}")
        raise
    except Exception as e:
        error_msg = f"Error calling GitHub tool '{tool_name}': {str(e)}"
        print(f"[MCP Client] {error_msg}")
        raise Exception(error_msg)


@asynccontextmanager
async def get_drive_mcp_session(user_id: str):
    """
    Get Google Drive MCP server session (using Python wrapper)

    This uses a pure Python wrapper for Google Drive API (like Jira/GitHub) instead
    of spawning external Node.js processes. This ensures consistent architecture across
    all integrations and eliminates external dependencies (Node.js, npm, npx).

    Args:
        user_id: User ID to get OAuth token

    Yields:
        ClientSession for Drive MCP server
    """
    if not MCP_AVAILABLE:
        raise RuntimeError("MCP library not available. Install with: pip install mcp")

    # Get Drive OAuth token from Company MCP Server
    drive_token = await get_user_oauth_token(user_id, 'google_drive')
    if not drive_token:
        raise ValueError(f"Google Drive not connected for user {user_id}. Please connect in Settings > Integrations.")

    # Use Python MCP server wrapper for Drive (same pattern as Jira/GitHub)
    from .drive_mcp_wrapper import get_drive_mcp_wrapper_session
    async with get_drive_mcp_wrapper_session(user_id, drive_token) as session:
        yield session


async def call_drive_mcp_tool(tool_name: str, arguments: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """
    Call a Google Drive MCP tool with enhanced error handling

    Args:
        tool_name: Name of the MCP tool to call
        arguments: Tool arguments
        user_id: User ID for OAuth token

    Returns:
        Tool result as dictionary

    Raises:
        RuntimeError: If MCP client is not available
        ValueError: If token is missing
        Exception: For other tool execution errors
    """
    try:
        async with get_drive_mcp_session(user_id) as session:
            result = await asyncio.wait_for(
                session.call_tool(tool_name, arguments),
                timeout=30.0  # 30 second timeout
            )
            print(f"[MCP Client] Successfully called Drive tool: {tool_name}")
            return result
    except asyncio.TimeoutError:
        error_msg = f"Drive MCP tool '{tool_name}' timed out after 30 seconds"
        print(f"[MCP Client] {error_msg}")
        raise Exception(error_msg)
    except ValueError as e:
        # Token or configuration error
        print(f"[MCP Client] Configuration error for Drive tool {tool_name}: {e}")
        raise
    except RuntimeError as e:
        # MCP library not available
        print(f"[MCP Client] Runtime error for Drive tool {tool_name}: {e}")
        raise
    except Exception as e:
        error_msg = f"Error calling Drive tool '{tool_name}': {str(e)}"
        print(f"[MCP Client] {error_msg}")
        raise Exception(error_msg)


# Jira MCP Client (Custom wrapper since no official MCP server exists)
@asynccontextmanager
async def get_jira_mcp_session(user_id: str):
    """
    Get Jira MCP server session (using custom Python wrapper)
    
    Args:
        user_id: User ID to get OAuth token
    
    Yields:
        ClientSession for Jira MCP server
    """
    if not MCP_AVAILABLE:
        raise RuntimeError("MCP library not available. Install with: pip install mcp")
    
    # Get Jira OAuth token from Company MCP Server
    jira_token = await get_user_oauth_token(user_id, 'jira')
    if not jira_token:
        raise ValueError(f"Jira not connected for user {user_id}. Please connect in Settings > Integrations.")
    
    # Get Jira cloudId and instance URL from Company MCP Server metadata
    jira_cloud_id = None
    jira_instance_url = None

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{MCP_URL}/integrations/user/{user_id}")
            if response.status_code == 200:
                data = response.json()
                integrations = data.get('integrations', [])
                jira_integration = next((i for i in integrations if i.get('provider') == 'jira'), None)
                if jira_integration and jira_integration.get('metadata'):
                    # Extract cloudId and instance_url from metadata
                    metadata = jira_integration.get('metadata', {})
                    if isinstance(metadata, str):
                        import json
                        metadata = json.loads(metadata)
                    jira_cloud_id = metadata.get('cloudId')
                    jira_instance_url = metadata.get('instance_url') or metadata.get('site_url')

                    if jira_cloud_id:
                        print(f"[MCP Client] Using Jira cloudId: {jira_cloud_id}")
                    if jira_instance_url:
                        print(f"[MCP Client] Using Jira instance URL: {jira_instance_url}")
    except Exception as e:
        print(f"[MCP Client] Could not get Jira metadata from Company MCP Server: {e}")

    # Fallback to environment variables if metadata not available
    if not jira_instance_url:
        jira_instance_url = CONFIG.get('JIRA_INSTANCE_URL') or os.getenv('JIRA_INSTANCE_URL', 'https://your-domain.atlassian.net')
        print(f"[MCP Client] WARNING: No cloudId found, using fallback instance URL: {jira_instance_url}")

    # Use custom Python MCP server wrapper for Jira
    from .jira_mcp_wrapper import get_jira_mcp_wrapper_session
    async with get_jira_mcp_wrapper_session(user_id, jira_token, jira_instance_url, jira_cloud_id) as session:
        yield session


async def call_jira_mcp_tool(tool_name: str, arguments: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """
    Call a Jira MCP tool with enhanced error handling

    Args:
        tool_name: Name of the MCP tool to call
        arguments: Tool arguments
        user_id: User ID for OAuth token

    Returns:
        Tool result as dictionary

    Raises:
        RuntimeError: If MCP client is not available
        ValueError: If token is missing
        Exception: For other tool execution errors
    """
    try:
        async with get_jira_mcp_session(user_id) as session:
            result = await asyncio.wait_for(
                session.call_tool(tool_name, arguments),
                timeout=30.0  # 30 second timeout
            )
            print(f"[MCP Client] Successfully called Jira tool: {tool_name}")
            return result
    except asyncio.TimeoutError:
        error_msg = f"Jira MCP tool '{tool_name}' timed out after 30 seconds"
        print(f"[MCP Client] {error_msg}")
        raise Exception(error_msg)
    except ValueError as e:
        # Token or configuration error
        print(f"[MCP Client] Configuration error for Jira tool {tool_name}: {e}")
        raise
    except RuntimeError as e:
        # MCP library not available
        print(f"[MCP Client] Runtime error for Jira tool {tool_name}: {e}")
        raise
    except Exception as e:
        error_msg = f"Error calling Jira tool '{tool_name}': {str(e)}"
        print(f"[MCP Client] {error_msg}")
        raise Exception(error_msg)

