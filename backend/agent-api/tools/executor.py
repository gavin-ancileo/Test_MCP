"""
Tool execution functions
Handles execution of all OpenAI function calling tools
"""

import httpx
import json
import asyncio
from typing import Dict
from fastapi import HTTPException
import os

# Import configuration
from config import CONFIG

# Import MCP client for native MCP servers
try:
    from .mcp_client import call_github_mcp_tool, call_drive_mcp_tool, call_jira_mcp_tool
    MCP_CLIENT_AVAILABLE = True
except ImportError:
    MCP_CLIENT_AVAILABLE = False
    print("[Executor] WARNING: MCP client not available. Using HTTP fallback.")

# MCP Server URL (Company MCP Server for prompts, DB, OAuth)
MCP_URL = os.getenv('MCP_URL', 'http://mcp-server.aap.local:8001')
N8N_URL = os.getenv('N8N_URL', 'http://aap-n8n.aap.local:5678')


async def retry_request(func, max_retries=3, base_delay=1.0):
    """
    Retry a request with exponential backoff.

    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds (will be multiplied for each retry)

    Returns:
        Response from the function

    Raises:
        Last exception if all retries fail
    """
    last_exception = None

    for attempt in range(max_retries):
        try:
            return await func()
        except (httpx.TimeoutException, httpx.ConnectError, httpx.RemoteProtocolError) as e:
            last_exception = e
            if attempt < max_retries - 1:  # Don't sleep on last attempt
                delay = base_delay * (2 ** attempt)  # Exponential backoff
                print(f"[RETRY] Attempt {attempt + 1} failed: {str(e)[:100]}. Retrying in {delay}s...")
                await asyncio.sleep(delay)
            else:
                print(f"[RETRY] All {max_retries} attempts failed")

    raise last_exception


async def execute_tool(tool_name: str, arguments: Dict, user: Dict) -> str:
    """Execute a tool and return result"""

    try:
        if tool_name == "get_prompts_list":
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{MCP_URL}/prompts")
                if response.status_code == 200:
                    data = response.json()
                    prompts = data.get('prompts', [])
                    count = data.get('count', 0)
                    
                    # Format response
                    result = f"We have {count} prompt templates available:\n\n"
                    for p in prompts[:10]:  # Show first 10
                        result += f"- {p.get('name', 'Unknown')} (Code: {p.get('code', 'N/A')})\n"
                    
                    if count > 10:
                        result += f"\n... and {count - 10} more prompts."
                    
                    return result
                else:
                    return f"Error fetching prompts: Status {response.status_code}"
        
        elif tool_name == "get_prompt_details":
            prompt_code = arguments.get('prompt_code')
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{MCP_URL}/prompts")
                if response.status_code == 200:
                    data = response.json()
                    prompts = data.get('prompts', [])
                    
                    # Find prompt by code
                    prompt = next((p for p in prompts if p.get('code') == prompt_code), None)
                    
                    if prompt:
                        result = f"Prompt: {prompt.get('name', 'Unknown')}\n"
                        result += f"Code: {prompt.get('code', 'N/A')}\n"
                        result += f"Categories: {', '.join(prompt.get('categories', []))}\n"
                        
                        variables = prompt.get('variables', {})
                        if variables:
                            result += f"Variables: {', '.join(variables.keys())}\n"
                        
                        return result
                    else:
                        return f"Prompt with code '{prompt_code}' not found."
                else:
                    return f"Error fetching prompt details: Status {response.status_code}"
        
        elif tool_name == "search_prompts_by_category":
            keyword = arguments.get('keyword', '').lower()
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{MCP_URL}/prompts")
                if response.status_code == 200:
                    data = response.json()
                    prompts = data.get('prompts', [])
                    
                    # Filter by keyword
                    filtered = [
                        p for p in prompts 
                        if keyword in p.get('name', '').lower() 
                        or keyword in ' '.join(p.get('categories', [])).lower()
                    ]
                    
                    if filtered:
                        result = f"Found {len(filtered)} prompts matching '{keyword}':\n\n"
                        for p in filtered:
                            result += f"- {p.get('name', 'Unknown')} (Code: {p.get('code', 'N/A')})\n"
                        return result
                    else:
                        return f"No prompts found matching '{keyword}'."
                else:
                    return f"Error searching prompts: Status {response.status_code}"

        # ============================================
        # MCP TOOLS - GitHub, Jira, Drive
        # ============================================

        elif tool_name == "github_list_repos":
            user_id = user.get('sub')
            if not user_id:
                raise HTTPException(status_code=401, detail="User ID not found in token")
            print(f"[github_list_repos] Using user_id='{user_id}' (from user['sub']={user.get('sub')}, email={user.get('email')})")

            # Use native GitHub MCP server
            if not MCP_CLIENT_AVAILABLE:
                return "Error: GitHub MCP client not available. Please check MCP server configuration."

            try:
                result_data = await call_github_mcp_tool("list_repositories", {}, user_id)
                # GitHub MCP server returns different format, need to adapt
                if isinstance(result_data, dict) and 'content' in result_data:
                    # MCP tools return content as list of text blocks
                    repos_data = json.loads(result_data['content'][0]['text']) if result_data['content'] else {}
                else:
                    repos_data = result_data if isinstance(result_data, dict) else {}

                # Extract repositories list from nested structure {"total": N, "repositories": [...]}
                repos_list = repos_data.get('repositories', [])
                total = repos_data.get('total', len(repos_list))

                result = f"You have {total} GitHub repositories:\n\n"
                for repo in repos_list[:10]:
                    repo_name = repo.get('name') or repo.get('full_name', 'Unknown')
                    result += f"• **{repo_name}**"
                    if repo.get('description'):
                        result += f" - {repo['description']}"
                    result += f"\n  Language: {repo.get('language', 'N/A')}, "
                    result += f"Stars: {repo.get('stargazers_count', 0)}, "
                    result += f"Private: {'Yes' if repo.get('private') else 'No'}\n"

                if total > 10:
                    result += f"\n... and {total - 10} more repositories."

                return result
            except Exception as e:
                error_msg = f"GitHub MCP server error: {str(e)}"
                print(f"[github_list_repos] {error_msg}")
                return error_msg

        elif tool_name == "github_search_code":
            user_id = user.get('sub')
            if not user_id:
                raise HTTPException(status_code=401, detail="User ID not found in token")
            query = arguments.get('query')
            repo = arguments.get('repo')

            # Use native GitHub MCP server
            if not MCP_CLIENT_AVAILABLE:
                return "Error: GitHub MCP client not available. Please check MCP server configuration."

            try:
                mcp_args = {"query": query}
                if repo:
                    mcp_args["repository"] = repo

                result_data = await call_github_mcp_tool("search_code", mcp_args, user_id)
                # Parse MCP response
                if isinstance(result_data, dict) and 'content' in result_data:
                    search_data = json.loads(result_data['content'][0]['text']) if result_data['content'] else {}
                else:
                    search_data = result_data if isinstance(result_data, dict) else {}

                total = search_data.get('total_count', len(search_data.get('items', [])))
                results = search_data.get('items', [])

                result = f"Found {total} code results for '{query}'"
                if repo:
                    result += f" in {repo}"
                result += ":\n\n"

                for item in results[:5]:
                    repo_path = item.get('repository', {}).get('full_name', '') if isinstance(item.get('repository'), dict) else item.get('repository', '')
                    file_path = item.get('path', '')
                    result += f"• **{repo_path}/{file_path}**\n"
                    if item.get('text_matches'):
                        snippet = item['text_matches'][0].get('fragment', '')[:150] if item['text_matches'] else ''
                        if snippet:
                            result += f"  ```\n  {snippet}...\n  ```\n"

                if total > 5:
                    result += f"\n... and {total - 5} more results."

                return result
            except Exception as e:
                error_msg = f"GitHub MCP server error: {str(e)}"
                print(f"[github_search_code] {error_msg}")
                return error_msg

        elif tool_name == "github_read_file":
            user_id = user.get('sub')
            if not user_id:
                raise HTTPException(status_code=401, detail="User ID not found in token")
            repo = arguments.get('repo')
            path = arguments.get('path')
            branch = arguments.get('branch', 'main')

            # Use native GitHub MCP server
            if not MCP_CLIENT_AVAILABLE:
                return "Error: GitHub MCP client not available. Please check MCP server configuration."

            try:
                mcp_args = {
                    "owner": repo.split('/')[0] if '/' in repo else user_id,
                    "repo": repo.split('/')[1] if '/' in repo else repo,
                    "path": path,
                    "ref": branch
                }

                result_data = await call_github_mcp_tool("read_file", mcp_args, user_id)
                # Parse MCP response
                if isinstance(result_data, dict) and 'content' in result_data:
                    file_data = json.loads(result_data['content'][0]['text']) if result_data['content'] else {}
                else:
                    file_data = result_data if isinstance(result_data, dict) else {}

                content = file_data.get('content', '')
                size = file_data.get('size', len(content))

                result = f"File: **{repo}/{path}** (branch: {branch})\n"
                result += f"Size: {size} bytes\n\n"
                result += f"```\n{content[:1000]}\n```"

                if len(content) > 1000:
                    result += f"\n\n... (truncated, showing first 1000 characters)"

                return result
            except Exception as e:
                error_msg = f"GitHub MCP server error: {str(e)}"
                print(f"[github_read_file] {error_msg}")
                return error_msg

        elif tool_name == "jira_list_projects":
            user_id = user.get('sub')
            if not user_id:
                raise HTTPException(status_code=401, detail="User ID not found in token")
            print(f"[jira_list_projects] Using user_id='{user_id}' (from user['sub']={user.get('sub')}, email={user.get('email')})")

            # Use native Jira MCP server
            if not MCP_CLIENT_AVAILABLE:
                return "Error: Jira MCP client not available. Please check MCP server configuration."

            try:
                result_data = await call_jira_mcp_tool("jira_list_projects", {}, user_id)
                # Parse MCP response
                if isinstance(result_data, dict) and 'content' in result_data:
                    projects_data = json.loads(result_data['content'][0]['text']) if result_data['content'] else {}
                else:
                    projects_data = result_data if isinstance(result_data, dict) else {}

                projects = projects_data.get('projects', [])
                result = f"You have access to {len(projects)} Jira projects:\n\n"

                # Show all projects with project type information
                for proj in projects:
                    key = proj.get('key', 'N/A')
                    name = proj.get('name', 'Unknown')

                    # Determine project type label
                    project_type = ""
                    if proj.get('simplified', False):
                        project_type = " (Team-managed)"
                    elif proj.get('style') == 'classic':
                        project_type = " (Company-managed)"
                    elif proj.get('style'):
                        project_type = f" ({proj['style'].title()})"

                    result += f"{key}: {name}{project_type}\n"

                return result
            except Exception as e:
                error_msg = f"Jira MCP server error: {str(e)}"
                print(f"[jira_list_projects] {error_msg}")
                return error_msg

        elif tool_name == "jira_search_issues":
            user_id = user.get('sub')
            if not user_id:
                raise HTTPException(status_code=401, detail="User ID not found in token")
            jql = arguments.get('jql')
            max_results = arguments.get('max_results', 50)

            # Use native Jira MCP server
            if not MCP_CLIENT_AVAILABLE:
                return "Error: Jira MCP client not available. Please check MCP server configuration."

            try:
                mcp_args = {"jql": jql, "max_results": max_results}
                result_data = await call_jira_mcp_tool("jira_search_issues", mcp_args, user_id)
                # Parse MCP response
                if isinstance(result_data, dict) and 'content' in result_data:
                    issues_data = json.loads(result_data['content'][0]['text']) if result_data['content'] else {}
                else:
                    issues_data = result_data if isinstance(result_data, dict) else {}

                total = issues_data.get('total', 0)
                issues = issues_data.get('issues', [])

                result = f"Found {total} Jira issues matching '{jql}':\n\n"

                for issue in issues[:10]:
                    result += f"• **{issue.get('key', 'N/A')}**: {issue.get('summary', 'Unknown')}\n"
                    result += f"  Status: {issue.get('status', 'Unknown')}, "
                    result += f"Priority: {issue.get('priority', 'N/A')}\n"

                if total > 10:
                    result += f"\n... and {total - 10} more issues."

                return result
            except Exception as e:
                error_msg = f"Jira MCP server error: {str(e)}"
                print(f"[jira_search_issues] {error_msg}")
                return error_msg

        elif tool_name == "jira_get_issue":
            user_id = user.get('sub')
            if not user_id:
                raise HTTPException(status_code=401, detail="User ID not found in token")
            issue_key = arguments.get('issue_key')

            # Use native Jira MCP server
            if not MCP_CLIENT_AVAILABLE:
                return "Error: Jira MCP client not available. Please check MCP server configuration."

            try:
                mcp_args = {"issue_key": issue_key}
                result_data = await call_jira_mcp_tool("jira_get_issue", mcp_args, user_id)
                # Parse MCP response
                if isinstance(result_data, dict) and 'content' in result_data:
                    issue_data = json.loads(result_data['content'][0]['text']) if result_data['content'] else {}
                else:
                    issue_data = result_data if isinstance(result_data, dict) else {}

                result = f"**{issue_data.get('key', 'N/A')}**: {issue_data.get('summary', 'Unknown')}\n\n"
                result += f"Status: {issue_data.get('status', 'Unknown')}\n"
                result += f"Priority: {issue_data.get('priority', 'N/A')}\n"
                result += f"Assignee: {issue_data.get('assignee', 'Unassigned')}\n"
                result += f"Reporter: {issue_data.get('reporter', 'Unknown')}\n"

                if issue_data.get('description'):
                    desc = issue_data['description'][:300]
                    result += f"\nDescription:\n{desc}"
                    if len(issue_data['description']) > 300:
                        result += "..."

                return result
            except Exception as e:
                error_msg = f"Jira MCP server error: {str(e)}"
                print(f"[jira_get_issue] {error_msg}")
                return error_msg

        elif tool_name == "jira_api_call":
            user_id = user.get('sub')
            if not user_id:
                raise HTTPException(status_code=401, detail="User ID not found in token")

            endpoint = arguments.get('endpoint')
            method = arguments.get('method', 'GET')
            params = arguments.get('params', {})
            body = arguments.get('body', {})

            # Use native Jira MCP server
            if not MCP_CLIENT_AVAILABLE:
                return "Error: Jira MCP client not available. Please check MCP server configuration."

            try:
                mcp_args = {
                    "endpoint": endpoint,
                    "method": method,
                    "params": params,
                    "body": body
                }
                result_data = await call_jira_mcp_tool("jira_api_call", mcp_args, user_id)

                # Parse MCP response
                if isinstance(result_data, dict) and 'content' in result_data:
                    api_response = json.loads(result_data['content'][0]['text']) if result_data['content'] else {}
                else:
                    api_response = result_data if isinstance(result_data, dict) else {}

                # Format response for LLM
                status_code = api_response.get('status_code', 'Unknown')
                data = api_response.get('data', {})
                success = api_response.get('success', False)

                if success:
                    # Special formatting for common endpoints
                    if endpoint == 'search' or endpoint == 'search/jql' or endpoint.startswith('search'):
                        # JQL Search results - format nicely
                        total = data.get('total', 0)
                        issues = data.get('issues', [])

                        result = f"[OK] Found {total} Jira issues\n\n"

                        for issue in issues[:20]:  # Show up to 20 issues
                            key = issue.get('key', 'N/A')
                            fields = issue.get('fields', {})
                            summary = fields.get('summary', 'Unknown')
                            status = fields.get('status', {}).get('name', 'Unknown')
                            priority = fields.get('priority', {}).get('name', 'N/A')
                            assignee = fields.get('assignee', {}).get('displayName', 'Unassigned') if fields.get('assignee') else 'Unassigned'

                            result += f"• **{key}**: {summary}\n"
                            result += f"  Status: {status}, Priority: {priority}, Assignee: {assignee}\n"

                        if total > 20:
                            result += f"\n... and {total - 20} more issues."

                        return result

                    elif endpoint.startswith('issue/') and '/worklog' in endpoint:
                        # Work log results
                        worklogs = data.get('worklogs', [])
                        result = f"[OK] Found {len(worklogs)} work log entries\n\n"
                        for wl in worklogs:
                            author = wl.get('author', {}).get('displayName', 'Unknown')
                            time_spent = wl.get('timeSpent', 'N/A')
                            result += f"• {author}: {time_spent}\n"
                        return result

                    else:
                        # Generic response
                        result = f"[OK] Jira API Call Successful ({method} {endpoint})\n"
                        result += f"Status Code: {status_code}\n\n"

                        # Show summary for common data types
                        if isinstance(data, list):
                            result += f"Returned {len(data)} items:\n```json\n{json.dumps(data[:5], indent=2)}\n```"
                            if len(data) > 5:
                                result += f"\n... and {len(data) - 5} more items."
                        elif isinstance(data, dict) and 'total' in data:
                            result += f"Total: {data.get('total')}\n```json\n{json.dumps(data, indent=2)}\n```"
                        else:
                            result += f"Response:\n```json\n{json.dumps(data, indent=2)}\n```"

                        return result
                else:
                    result = f"[ERROR] Jira API Call Failed ({method} {endpoint})\n"
                    result += f"Status Code: {status_code}\n"
                    result += f"Error: {data}"
                    return result
            except Exception as e:
                error_msg = f"Jira API call error: {str(e)}"
                print(f"[jira_api_call] {error_msg}")
                return error_msg

        elif tool_name == "drive_list_files":
            user_id = user.get('sub')
            if not user_id:
                raise HTTPException(status_code=401, detail="User ID not found in token")
            query = arguments.get('query')
            
            print(f"[drive_list_files] Using user_id='{user_id}' (from user['sub']={user.get('sub')}, email={user.get('email')})")

            # Use native Drive MCP server
            if not MCP_CLIENT_AVAILABLE:
                return "Error: Drive MCP client not available. Please check MCP server configuration."

            try:
                mcp_args = {}
                if query:
                    mcp_args["query"] = query
                mcp_args["page_size"] = 10

                result_data = await call_drive_mcp_tool("drive_list_files", mcp_args, user_id)
                # Parse MCP response
                if isinstance(result_data, dict) and 'content' in result_data:
                    files_data = json.loads(result_data['content'][0]['text']) if result_data['content'] else {}
                else:
                    files_data = result_data if isinstance(result_data, dict) else {}

                files = files_data.get('files', [])
                result = f"Found {len(files)} files in Google Drive"
                if query:
                    result += f" matching '{query}'"
                result += ":\n\n"

                for file in files[:10]:
                    result += f"• **{file.get('name', 'Unknown')}** (file_id: `{file.get('id', 'N/A')}`)\n"
                    result += f"  Type: {file.get('mimeType', 'Unknown')}, "
                    result += f"Modified: {file.get('modifiedTime', 'N/A')}\n"

                if len(files) > 10:
                    result += f"\n... and {len(files) - 10} more files."

                return result
            except Exception as e:
                error_msg = f"Drive MCP server error: {str(e)}"
                print(f"[drive_list_files] {error_msg}")
                return error_msg

        elif tool_name == "drive_search_files":
            user_id = user.get('sub')
            if not user_id:
                raise HTTPException(status_code=401, detail="User ID not found in token")
            query = arguments.get('query')

            # Use native Drive MCP server
            if not MCP_CLIENT_AVAILABLE:
                return "Error: Drive MCP client not available. Please check MCP server configuration."

            try:
                mcp_args = {"query": query}
                result_data = await call_drive_mcp_tool("drive_search_files", mcp_args, user_id)
                # Parse MCP response
                if isinstance(result_data, dict) and 'content' in result_data:
                    files_data = json.loads(result_data['content'][0]['text']) if result_data['content'] else {}
                else:
                    files_data = result_data if isinstance(result_data, dict) else {}

                files = files_data.get('files', [])
                result = f"Found {len(files)} files matching '{query}':\n\n"

                for file in files[:10]:
                    result += f"• **{file.get('name', 'Unknown')}** (file_id: `{file.get('id', 'N/A')}`)\n"
                    result += f"  Type: {file.get('mimeType', 'Unknown')}\n"

                if len(files) > 10:
                    result += f"\n... and {len(files) - 10} more files."

                return result
            except Exception as e:
                error_msg = f"Drive MCP server error: {str(e)}"
                print(f"[drive_search_files] {error_msg}")
                return error_msg

        # Advanced Jira tools
        elif tool_name in ["jira_get_project_details", "jira_get_project_analytics", 
                          "jira_get_issue_comments", "jira_get_all_projects_summary",
                          "jira_list_filters", "jira_execute_filter"]:
            user_id = user.get('sub')
            if not user_id:
                raise HTTPException(status_code=401, detail="User ID not found in token")
            
            # Map tool names to endpoints
            endpoint_map = {
                "jira_get_project_details": f"/tools/jira/project/{arguments.get('project_key')}",
                "jira_get_project_analytics": f"/tools/jira/project/{arguments.get('project_key')}/analytics",
                "jira_get_issue_comments": f"/tools/jira/issue/{arguments.get('issue_key')}/comments",
                "jira_get_all_projects_summary": "/tools/jira/all-projects-summary",
                "jira_list_filters": "/tools/jira/filters",
                "jira_execute_filter": f"/tools/jira/filter/{arguments.get('filter_id')}/execute"
            }
            
            endpoint = endpoint_map.get(tool_name)
            if not endpoint:
                return f"Error: Unknown Jira tool: {tool_name}"
            
            params = {"user_id": user_id}
            if tool_name == "jira_execute_filter":
                params["max_results"] = arguments.get('max_results', 50)
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{MCP_URL}{endpoint}", params=params)
                if response.status_code == 200:
                    data = response.json()
                    if "error" in data:
                        return f"Jira tool error: {data['error']}"
                    return json.dumps(data, indent=2)
                else:
                    return f"Error calling Jira tool: Status {response.status_code}"

        # Database tools
        elif tool_name == "insurance_list_tables":
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{MCP_URL}/insurance/tables")
                if response.status_code == 200:
                    data = response.json()
                    if "error" in data:
                        return f"Insurance DB error: {data['error']}"
                    
                    tables = data.get('tables', [])
                    result = f"Insurance database has {len(tables)} tables:\n\n"
                    
                    for table in tables[:20]:
                        result += f"• {table}\n"
                    
                    if len(tables) > 20:
                        result += f"\n... and {len(tables) - 20} more tables."
                    
                    return result
                else:
                    return f"Error listing Insurance tables: Status {response.status_code}"

        elif tool_name == "insurance_get_table_schema":
            table_name = arguments.get('table_name')
            if not table_name:
                return "Error: table_name is required"

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{MCP_URL}/insurance/table/{table_name}")
                if response.status_code == 200:
                    data = response.json()
                    if "error" in data:
                        return f"Insurance DB error: {data['error']}"

                    table = data.get('table', table_name)
                    columns = data.get('columns', [])

                    result = f"Table '{table}' schema ({len(columns)} columns):\n\n"

                    for col in columns:
                        name = col.get('name', 'unknown')
                        data_type = col.get('type', 'unknown')
                        nullable = col.get('nullable', 'unknown')
                        key = col.get('key', '')
                        extra = col.get('extra', '')

                        result += f"• {name} ({data_type})"
                        if key == 'PRI':
                            result += " [PRIMARY KEY]"
                        if nullable == 'NO':
                            result += " [NOT NULL]"
                        if extra:
                            result += f" [{extra}]"
                        result += "\n"

                    return result
                else:
                    return f"Error getting Insurance table schema: Status {response.status_code}"

        elif tool_name == "insurance_query":
            sql = arguments.get('sql')
            if not sql:
                return "Error: SQL query is required"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{MCP_URL}/insurance/query",
                    json={"sql": sql}
                )
                if response.status_code == 200:
                    data = response.json()
                    if "error" in data:
                        return f"Insurance DB query error: {data['error']}"
                    
                    row_count = data.get('row_count', 0)
                    rows = data.get('data', [])
                    
                    result = f"Query returned {row_count} rows:\n\n"
                    
                    if rows:
                        # Show column headers
                        if row_count > 0:
                            columns = list(rows[0].keys())
                            result += f"Columns: {', '.join(columns)}\n\n"
                        
                        # Show first 10 rows
                        for i, row in enumerate(rows[:10], 1):
                            result += f"Row {i}:\n"
                            for col, val in row.items():
                                result += f"  {col}: {val}\n"
                            result += "\n"
                        
                        if row_count > 10:
                            result += f"... and {row_count - 10} more rows."
                    
                    return result
                else:
                    return f"Error executing Insurance query: Status {response.status_code}"

        elif tool_name == "claimhub_list_tables":
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{MCP_URL}/claimhub/tables")
                if response.status_code == 200:
                    data = response.json()
                    if "error" in data:
                        return f"ClaimHub DB error: {data['error']}"
                    
                    tables = data.get('tables', [])
                    result = f"ClaimHub database has {len(tables)} tables:\n\n"
                    
                    for table in tables[:20]:
                        result += f"• {table}\n"
                    
                    if len(tables) > 20:
                        result += f"\n... and {len(tables) - 20} more tables."
                    
                    return result
                else:
                    return f"Error listing ClaimHub tables: Status {response.status_code}"

        elif tool_name == "claimhub_get_table_schema":
            table_name = arguments.get('table_name')
            if not table_name:
                return "Error: table_name is required"

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{MCP_URL}/claimhub/table/{table_name}")
                if response.status_code == 200:
                    data = response.json()
                    if "error" in data:
                        return f"ClaimHub DB error: {data['error']}"

                    table = data.get('table', table_name)
                    columns = data.get('columns', [])

                    result = f"Table '{table}' schema ({len(columns)} columns):\n\n"

                    for col in columns:
                        name = col.get('name', 'unknown')
                        data_type = col.get('type', 'unknown')
                        nullable = col.get('nullable', 'unknown')

                        result += f"• {name} ({data_type})"
                        if nullable == 'NO':
                            result += " [NOT NULL]"
                        result += "\n"

                    return result
                else:
                    return f"Error getting ClaimHub table schema: Status {response.status_code}"

        elif tool_name == "claimhub_query":
            sql = arguments.get('sql')
            if not sql:
                return "Error: SQL query is required"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{MCP_URL}/claimhub/query",
                    json={"query": sql}
                )
                if response.status_code == 200:
                    data = response.json()
                    if "error" in data:
                        return f"ClaimHub DB query error: {data['error']}"
                    
                    row_count = data.get('row_count', 0)
                    rows = data.get('data', [])
                    
                    result = f"Query returned {row_count} rows:\n\n"
                    
                    if rows:
                        # Show column headers
                        if row_count > 0:
                            columns = list(rows[0].keys())
                            result += f"Columns: {', '.join(columns)}\n\n"
                        
                        # Show first 10 rows
                        for i, row in enumerate(rows[:10], 1):
                            result += f"Row {i}:\n"
                            for col, val in row.items():
                                result += f"  {col}: {val}\n"
                            result += "\n"
                        
                        if row_count > 10:
                            result += f"... and {row_count - 10} more rows."
                    
                    return result
                else:
                    return f"Error executing ClaimHub query: Status {response.status_code}"

        # N8N workflow tools
        elif tool_name == "n8n_list_workflows":
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{N8N_URL}/api/v1/workflows")
                if response.status_code == 200:
                    workflows = response.json()
                    result = f"[List] Found {len(workflows)} n8n workflows:\n\n"
                    
                    for wf in workflows:
                        status = "OK: Active" if wf.get('active') else "[Paused] Inactive"
                        workflow_id = wf.get('id')
                        result += f"• **{wf.get('name')}** (ID: `{workflow_id}`)\n"
                        result += f"  Status: {status}\n"
                        result += f"  Nodes: {len(wf.get('nodes', []))}\n"
                        if wf.get('active') and workflow_id:
                            result += f"  Webhook: {N8N_URL}/webhook/{workflow_id}\n"
                        result += "\n"
                    
                    return result
                else:
                    return f"ERROR: Error listing workflows: HTTP {response.status_code}: {response.text}"

        elif tool_name == "n8n_create_workflow":
            workflow_json = arguments.get('workflow_json')
            activate = arguments.get('activate', True)
            execute_after_create = arguments.get('execute_after_create', False)
            initial_payload = arguments.get('initial_payload', {})
            
            if not workflow_json:
                return "Error: workflow_json is required. Provide a valid n8n workflow JSON object."
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                workflow_data = {
                    **workflow_json,
                    "active": activate
                }
                
                response = await client.post(
                    f"{N8N_URL}/api/v1/workflows",
                    json=workflow_data
                )
                if response.status_code in [200, 201]:
                    created_workflow = response.json()
                    workflow_id = created_workflow.get('id')
                    workflow_name = created_workflow.get('name', 'Unnamed Workflow')
                    
                    result = f"OK: Successfully created n8n workflow: **{workflow_name}**\n\n"
                    result += f"Workflow ID: `{workflow_id}`\n"
                    result += f"Status: {'OK: Active' if activate else '[Paused] Inactive'}\n"
                    if activate and workflow_id:
                        result += f"Webhook URL: {N8N_URL}/webhook/{workflow_id}\n"
                    
                    # Execute workflow if requested
                    if execute_after_create and workflow_id:
                        exec_response = await client.post(
                            f"{N8N_URL}/webhook/{workflow_id}",
                            json=initial_payload
                        )
                        if exec_response.status_code in [200, 201]:
                            result += f"\n[Sync] Workflow executed immediately:\n"
                            result += "OK: Execution successful\n"
                            try:
                                exec_data = exec_response.json()
                                result += f"Response: {json.dumps(exec_data, indent=2)}\n"
                            except:
                                result += f"Response: {exec_response.text}\n"
                        else:
                            result += f"\nERROR: Execution failed: HTTP {exec_response.status_code}\n"
                    
                    result += f"\n[Info] You can now trigger this workflow using: `n8n_trigger_workflow(workflow_id='{workflow_id}')`"
                    return result
                else:
                    return f"ERROR: Error creating workflow: HTTP {response.status_code}: {response.text}"

        elif tool_name == "n8n_get_workflow":
            workflow_id = arguments.get('workflow_id')
            
            if not workflow_id:
                return "Error: workflow_id is required. Use n8n_list_workflows to see available workflow IDs."
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{N8N_URL}/api/v1/workflows/{workflow_id}")
                if response.status_code == 200:
                    workflow = response.json()
                    result = f"[List] Workflow Details: **{workflow.get('name', 'Unnamed')}**\n\n"
                    result += f"ID: `{workflow.get('id')}`\n"
                    result += f"Status: {'OK: Active' if workflow.get('active') else '[Paused] Inactive'}\n"
                    result += f"Nodes: {len(workflow.get('nodes', []))}\n"
                    result += f"Created: {workflow.get('createdAt', 'N/A')}\n"
                    result += f"Updated: {workflow.get('updatedAt', 'N/A')}\n"
                    if workflow.get('active') and workflow.get('id'):
                        result += f"Webhook URL: {N8N_URL}/webhook/{workflow.get('id')}\n"
                    
                    # Show node summary
                    nodes = workflow.get('nodes', [])
                    if nodes:
                        result += f"\n**Nodes ({len(nodes)}):**\n"
                        for node in nodes[:10]:
                            result += f"• {node.get('name', 'Unknown')} ({node.get('type', 'unknown')})\n"
                        if len(nodes) > 10:
                            result += f"... and {len(nodes) - 10} more nodes\n"
                    
                    return result
                else:
                    return f"ERROR: Error getting workflow: HTTP {response.status_code}: {response.text}"

        elif tool_name == "n8n_update_workflow":
            workflow_id = arguments.get('workflow_id')
            workflow_json = arguments.get('workflow_json')
            activate = arguments.get('activate')
            
            if not workflow_id or not workflow_json:
                return "Error: workflow_id and workflow_json are required."
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                update_data = {
                    **workflow_json,
                    "id": workflow_id
                }
                if activate is not None:
                    update_data["active"] = activate
                
                response = await client.put(
                    f"{N8N_URL}/api/v1/workflows/{workflow_id}",
                    json=update_data
                )
                if response.status_code == 200:
                    updated_workflow = response.json()
                    result = f"OK: Successfully updated n8n workflow: **{updated_workflow.get('name')}**\n\n"
                    result += f"Workflow ID: `{workflow_id}`\n"
                    result += f"Status: {'OK: Active' if updated_workflow.get('active') else '[Paused] Inactive'}\n"
                    if updated_workflow.get('active') and workflow_id:
                        result += f"Webhook URL: {N8N_URL}/webhook/{workflow_id}\n"
                    return result
                else:
                    return f"ERROR: Error updating workflow: HTTP {response.status_code}: {response.text}"

        elif tool_name == "n8n_delete_workflow":
            workflow_id = arguments.get('workflow_id')
            
            if not workflow_id:
                return "Error: workflow_id is required. Use n8n_list_workflows to see available workflow IDs."
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                # First get workflow name for confirmation
                get_response = await client.get(f"{N8N_URL}/api/v1/workflows/{workflow_id}")
                workflow_name = "Unknown"
                if get_response.status_code == 200:
                    workflow_name = get_response.json().get('name', 'Unknown')
                
                # Delete workflow
                response = await client.delete(f"{N8N_URL}/api/v1/workflows/{workflow_id}")
                if response.status_code in [200, 204]:
                    return f"OK: Successfully deleted n8n workflow: **{workflow_name}** (ID: `{workflow_id}`)"
                else:
                    return f"ERROR: Error deleting workflow: HTTP {response.status_code}: {response.text}"

        elif tool_name == "n8n_activate_workflow":
            workflow_id = arguments.get('workflow_id')
            active = arguments.get('active', True)
            
            if not workflow_id:
                return "Error: workflow_id is required. Use n8n_list_workflows to see available workflow IDs."
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Get current workflow
                get_response = await client.get(f"{N8N_URL}/api/v1/workflows/{workflow_id}")
                if get_response.status_code != 200:
                    return f"ERROR: Error getting workflow: HTTP {get_response.status_code}: {get_response.text}"
                
                workflow = get_response.json()
                workflow["active"] = active
                
                # Update workflow activation status
                response = await client.put(
                    f"{N8N_URL}/api/v1/workflows/{workflow_id}",
                    json=workflow
                )
                if response.status_code == 200:
                    status = "OK: Activated" if active else "[Paused] Deactivated"
                    result = f"{status} n8n workflow: **{workflow.get('name')}** (ID: `{workflow_id}`)\n\n"
                    if active:
                        result += f"Webhook URL: {N8N_URL}/webhook/{workflow_id}\n"
                    return result
                else:
                    return f"ERROR: Error updating workflow: HTTP {response.status_code}: {response.text}"

        elif tool_name == "n8n_trigger_workflow":
            workflow_id = arguments.get('workflow_id')
            payload = arguments.get('payload', {})

            if not workflow_id:
                return "Error: workflow_id is required. Use n8n_list_workflows to see available workflow IDs."

            # Get user email for OAuth token retrieval
            user_email = user.get('email') or user.get('sub', '')
            
            # Fetch OAuth tokens from MCP server for all providers
            oauth_tokens = {}
            if user_email:
                try:
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        providers = ['github', 'jira', 'google_drive']
                        for provider in providers:
                            try:
                                # Map provider names: frontend uses 'drive' but API uses 'google_drive'
                                api_provider = 'drive' if provider == 'google_drive' else provider
                                token_response = await client.get(
                                    f"{MCP_URL}/integrations/{user_email}/{api_provider}/token"
                                )
                                if token_response.status_code == 200:
                                    token_data = token_response.json()
                                    oauth_tokens[provider] = token_data.get('access_token', '')
                                    print(f"[n8n_trigger] Retrieved {provider} token for user {user_email}")
                                else:
                                    print(f"[n8n_trigger] No {provider} token found for user {user_email}")
                            except Exception as e:
                                print(f"[n8n_trigger] Error fetching {provider} token: {e}")
                except Exception as e:
                    print(f"[n8n_trigger] Error fetching OAuth tokens: {e}")

            # Inject OAuth tokens and user_id into payload
            enhanced_payload = {
                **payload,
                "user_id": user_email,
                "oauth_tokens": oauth_tokens
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{N8N_URL}/webhook/{workflow_id}",
                    json=enhanced_payload
                )
                if response.status_code in [200, 201]:
                    result = f"OK: Successfully triggered n8n workflow: {workflow_id}\n\n"
                    try:
                        response_data = response.json()
                        result += f"Response: {json.dumps(response_data, indent=2)}"
                    except:
                        result += f"Response: {response.text}"
                    return result
                else:
                    return f"ERROR: Error triggering n8n workflow: HTTP {response.status_code}: {response.text}"

        # Prompt validation tools
        elif tool_name == "search_prompts_by_intent":
            user_query = arguments.get('user_query', '')

            if not user_query:
                return "Error: user_query is required. Provide the user's request (e.g., 'offer letter', 'contract')."

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{MCP_URL}/mcp-server/prompts/search/intent",
                    params={"query": user_query}
                )
                if response.status_code == 200:
                    data = response.json()
                    if not data.get('success'):
                        return f"Error searching prompts: {data.get('error', 'Unknown error')}"

                    matches = data.get('matches', [])
                    if not matches:
                        return f"No matching templates found for '{user_query}'. You can ask 'what prompts are available?' to see all templates."

                    result = f"**Found {len(matches)} template(s) matching '{user_query}':**\n\n"
                    for match in matches:
                        result += f"**{match['name']}** (code: `{match['code']}`)\n"
                        result += f"  Categories: {', '.join(match.get('categories', []))}\n"
                        if match.get('required_variables'):
                            result += f"  Required variables: {', '.join(match['required_variables'])}\n"
                        result += "\n"

                    result += f"\n**IMPORTANT**: Before generating the document, use `validate_prompt_variables` with the prompt code to get ALL required variables that must be collected from the user."
                    return result
                else:
                    return f"Error searching prompts: HTTP {response.status_code}"

        elif tool_name == "validate_prompt_variables":
            prompt_code = arguments.get('prompt_code', '')

            if not prompt_code:
                return "Error: prompt_code is required. Use search_prompts_by_intent first to find the prompt code."

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{MCP_URL}/mcp-server/prompts/{prompt_code}/validate"
                )
                if response.status_code == 200:
                    data = response.json()
                    if not data.get('success'):
                        return f"Error validating prompt: {data.get('error', 'Prompt not found')}"

                    # Return the user-friendly message directly
                    result = f"**Template: {data['prompt_name']}**\n\n"
                    result += data['message'] + "\n\n"

                    # Add detailed variable information
                    if data.get('required_variables'):
                        result += "**Required fields:**\n"
                        for var_info in data.get('variables', []):
                            if var_info.get('required'):
                                result += f"  • {var_info['name']}: {var_info.get('description', var_info['name'])}\n"

                    if data.get('optional_variables'):
                        result += "\n**Optional fields:**\n"
                        for var_info in data.get('variables', []):
                            if not var_info.get('required'):
                                default = f" (default: {var_info['default']})" if var_info.get('default') else ""
                                result += f"  • {var_info['name']}: {var_info.get('description', var_info['name'])}{default}\n"

                    result += "\n**CRITICAL**: You MUST ask the user for ALL required variables BEFORE generating the document. DO NOT proceed until user provides all values."
                    return result
                else:
                    return f"Error validating prompt: HTTP {response.status_code}"

        # Generic GitHub MCP tool handlers
        elif tool_name in ["github_create_issue", "github_list_issues", "github_get_issue",
                          "github_list_prs", "github_get_pr", "github_create_pr",
                          "github_create_file", "github_update_file", "github_merge_pr",
                          "github_create_branch", "github_list_commits", "github_get_repo",
                          "github_list_collaborators", "github_scan_repo"]:
            user_id = user.get('sub')
            if not user_id:
                return "Error: User ID not found in token"

            # Use native GitHub MCP server
            if not MCP_CLIENT_AVAILABLE:
                return "Error: GitHub MCP client not available. Please check MCP server configuration."

            try:
                # Map tool names to GitHub MCP server tool names
                tool_name_mapping = {
                    "github_create_issue": "create_issue",
                    "github_list_issues": "list_issues",
                    "github_get_issue": "get_issue",
                    "github_list_prs": "list_pull_requests",
                    "github_get_pr": "get_pull_request",
                    "github_create_pr": "create_pull_request",
                    "github_create_file": "create_file",
                    "github_update_file": "update_file",
                    "github_merge_pr": "merge_pull_request",
                    "github_create_branch": "create_branch",
                    "github_list_commits": "list_commits",
                    "github_get_repo": "get_repository",
                    "github_list_collaborators": "list_collaborators"
                }

                mcp_tool_name = tool_name_mapping.get(tool_name, tool_name.replace("github_", ""))
                result_data = await call_github_mcp_tool(mcp_tool_name, arguments, user_id)

                # Parse MCP response
                if isinstance(result_data, dict) and 'content' in result_data:
                    if result_data['content']:
                        return result_data['content'][0].get('text', json.dumps(result_data))
                return json.dumps(result_data, indent=2)
            except Exception as e:
                error_msg = f"GitHub MCP server error: {str(e)}"
                print(f"[{tool_name}] {error_msg}")
                return error_msg

        elif tool_name in ["jira_create_issue", "jira_update_issue", "jira_add_comment",
                          "jira_transition_issue", "jira_list_boards", "jira_list_sprints",
                          "jira_add_attachment", "jira_log_work",
                          "jira_list_my_active_projects", "jira_list_projects_with_role"]:
            user_id = user.get('sub')
            if not user_id:
                return "Error: User ID not found in token"

            # Use native Jira MCP server
            if not MCP_CLIENT_AVAILABLE:
                return "Error: Jira MCP client not available. Please check MCP server configuration."

            try:
                result_data = await call_jira_mcp_tool(tool_name, arguments, user_id)

                # Parse MCP response
                if isinstance(result_data, dict) and 'content' in result_data:
                    if result_data['content']:
                        return result_data['content'][0].get('text', json.dumps(result_data))
                return json.dumps(result_data, indent=2)
            except Exception as e:
                error_msg = f"Jira MCP server error: {str(e)}"
                print(f"[{tool_name}] {error_msg}")
                return error_msg

        elif tool_name in ["drive_create_file", "drive_update_file", "drive_create_folder",
                          "drive_share_file", "drive_delete_file", "drive_export_file",
                          "drive_read_file", "drive_list_folder_contents", "drive_list_shared_files",
                          "drive_api_call"]:
            user_id = user.get('sub')
            if not user_id:
                return "Error: User ID not found in token"

            # Use native Drive MCP server
            if not MCP_CLIENT_AVAILABLE:
                return "Error: Drive MCP client not available. Please check MCP server configuration."

            try:
                result_data = await call_drive_mcp_tool(tool_name, arguments, user_id)

                # Parse MCP response
                if isinstance(result_data, dict) and 'content' in result_data:
                    if result_data['content']:
                        content_text = result_data['content'][0].get('text', '')
                        # Try to parse as JSON, if fails return as text
                        try:
                            parsed = json.loads(content_text)
                            return json.dumps(parsed, indent=2)
                        except:
                            return content_text
                return json.dumps(result_data, indent=2)
            except Exception as e:
                error_msg = f"Drive MCP server error: {str(e)}"
                print(f"[{tool_name}] {error_msg}")
                return error_msg

        else:
            return f"Unknown tool: {tool_name}"
    
    except Exception as e:
        return f"Error executing tool {tool_name}: {str(e)}"

