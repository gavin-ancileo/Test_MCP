"""
GitHub MCP Server Wrapper
Custom MCP server wrapper for GitHub
This implements a simple MCP server interface that wraps GitHub REST API calls
"""

import httpx
import json
import os
from typing import Dict, Any, Optional, AsyncGenerator
from contextlib import asynccontextmanager

try:
    from mcp import ClientSession
    try:
        from mcp.types import Tool, TextContent
    except ImportError:
        # Fallback if types not available
        from typing import TypedDict
        class TextContent(TypedDict):
            type: str
            text: str
        class Tool(TypedDict):
            name: str
            description: str
            inputSchema: dict
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False


class GitHubMCPWrapper:
    """
    Simple MCP server wrapper for GitHub API
    Implements MCP protocol to wrap GitHub REST API calls
    """

    def __init__(self, user_id: str, access_token: str):
        self.user_id = user_id
        self.access_token = access_token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

    async def list_tools(self) -> list[dict]:
        """List available GitHub MCP tools"""
        return [
            {
                "name": "list_repositories",
                "description": "List all GitHub repositories for the user (personal, collaborator, organization). Returns repositories immediately. Do not say you will list repos, just return the results.",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_repository",
                "description": "Get detailed information about a specific repository including description, language, stars, forks, etc. Returns repository details immediately.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "owner": {"type": "string", "description": "Repository owner (username or organization)"},
                        "repo": {"type": "string", "description": "Repository name"}
                    },
                    "required": ["owner", "repo"]
                }
            },
            {
                "name": "search_repositories",
                "description": "Search for repositories on GitHub by keyword, language, topic, etc. Returns matching repositories immediately.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query (e.g., 'language:python stars:>100')"},
                        "max_results": {"type": "integer", "description": "Maximum number of results", "default": 30}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "list_issues",
                "description": "List issues in a repository. Returns issues immediately.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "owner": {"type": "string", "description": "Repository owner"},
                        "repo": {"type": "string", "description": "Repository name"},
                        "state": {"type": "string", "enum": ["open", "closed", "all"], "description": "Issue state filter", "default": "open"}
                    },
                    "required": ["owner", "repo"]
                }
            },
            {
                "name": "get_issue",
                "description": "Get details of a specific issue including title, body, comments, labels, etc. Returns issue details immediately.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "owner": {"type": "string", "description": "Repository owner"},
                        "repo": {"type": "string", "description": "Repository name"},
                        "issue_number": {"type": "integer", "description": "Issue number"}
                    },
                    "required": ["owner", "repo", "issue_number"]
                }
            },
            {
                "name": "create_issue",
                "description": "Create a new issue in a repository. Returns created issue details immediately.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "owner": {"type": "string", "description": "Repository owner"},
                        "repo": {"type": "string", "description": "Repository name"},
                        "title": {"type": "string", "description": "Issue title"},
                        "body": {"type": "string", "description": "Issue body/description"}
                    },
                    "required": ["owner", "repo", "title"]
                }
            },
            {
                "name": "list_pull_requests",
                "description": "List pull requests in a repository. Returns PRs immediately.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "owner": {"type": "string", "description": "Repository owner"},
                        "repo": {"type": "string", "description": "Repository name"},
                        "state": {"type": "string", "enum": ["open", "closed", "all"], "description": "PR state filter", "default": "open"}
                    },
                    "required": ["owner", "repo"]
                }
            },
            {
                "name": "github_api_call",
                "description": "Universal GitHub REST API caller - call ANY GitHub API endpoint directly. Use this for advanced operations not covered by specific tools. See GitHub REST API docs: https://docs.github.com/en/rest. Examples: GET /repos/{owner}/{repo}/contents/{path} (get file content), GET /users/{username} (get user info), etc.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "endpoint": {
                            "type": "string",
                            "description": "API endpoint path (without base URL). Examples: '/user', '/repos/{owner}/{repo}', '/repos/{owner}/{repo}/issues'. Do NOT include 'https://api.github.com' prefix."
                        },
                        "method": {
                            "type": "string",
                            "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"],
                            "description": "HTTP method",
                            "default": "GET"
                        },
                        "params": {
                            "type": "object",
                            "description": "Query parameters (e.g., {\"per_page\": 100, \"state\": \"open\"})",
                            "default": {}
                        },
                        "body": {
                            "type": "object",
                            "description": "Request body for POST/PUT/PATCH requests",
                            "default": {}
                        }
                    },
                    "required": ["endpoint"]
                }
            },
        ]

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a GitHub tool"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            if tool_name == "list_repositories":
                # List all repos (personal, collaborator, organization)
                response = await client.get(
                    f"{self.base_url}/user/repos",
                    headers=self.headers,
                    params={
                        "per_page": 100,
                        "affiliation": "owner,collaborator,organization_member",
                        "sort": "updated",
                        "direction": "desc"
                    }
                )
                if response.status_code == 200:
                    repos = response.json()
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps({
                                    "total": len(repos),
                                    "repositories": [
                                        {
                                            "id": r.get("id"),
                                            "name": r.get("name"),
                                            "full_name": r.get("full_name"),
                                            "description": r.get("description", ""),
                                            "private": r.get("private", False),
                                            "language": r.get("language", ""),
                                            "stargazers_count": r.get("stargazers_count", 0),
                                            "forks_count": r.get("forks_count", 0),
                                            "html_url": r.get("html_url", ""),
                                            "updated_at": r.get("updated_at", "")
                                        }
                                        for r in repos
                                    ]
                                })
                            }
                        ]
                    }
                else:
                    raise Exception(f"GitHub API error: {response.status_code} - {response.text}")

            elif tool_name == "get_repository":
                owner = arguments.get("owner")
                repo = arguments.get("repo")

                response = await client.get(
                    f"{self.base_url}/repos/{owner}/{repo}",
                    headers=self.headers
                )
                if response.status_code == 200:
                    r = response.json()
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps({
                                    "id": r.get("id"),
                                    "name": r.get("name"),
                                    "full_name": r.get("full_name"),
                                    "description": r.get("description", ""),
                                    "private": r.get("private", False),
                                    "language": r.get("language", ""),
                                    "stargazers_count": r.get("stargazers_count", 0),
                                    "forks_count": r.get("forks_count", 0),
                                    "open_issues_count": r.get("open_issues_count", 0),
                                    "default_branch": r.get("default_branch", "main"),
                                    "html_url": r.get("html_url", ""),
                                    "created_at": r.get("created_at", ""),
                                    "updated_at": r.get("updated_at", "")
                                })
                            }
                        ]
                    }
                else:
                    raise Exception(f"GitHub API error: {response.status_code} - {response.text}")

            elif tool_name == "search_repositories":
                query = arguments.get("query")
                max_results = arguments.get("max_results", 30)

                response = await client.get(
                    f"{self.base_url}/search/repositories",
                    headers=self.headers,
                    params={"q": query, "per_page": max_results}
                )
                if response.status_code == 200:
                    data = response.json()
                    repos = data.get("items", [])
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps({
                                    "total_count": data.get("total_count", 0),
                                    "repositories": [
                                        {
                                            "name": r.get("name"),
                                            "full_name": r.get("full_name"),
                                            "description": r.get("description", ""),
                                            "language": r.get("language", ""),
                                            "stargazers_count": r.get("stargazers_count", 0),
                                            "html_url": r.get("html_url", "")
                                        }
                                        for r in repos
                                    ]
                                })
                            }
                        ]
                    }
                else:
                    raise Exception(f"GitHub API error: {response.status_code} - {response.text}")

            elif tool_name == "list_issues":
                owner = arguments.get("owner")
                repo = arguments.get("repo")
                state = arguments.get("state", "open")

                response = await client.get(
                    f"{self.base_url}/repos/{owner}/{repo}/issues",
                    headers=self.headers,
                    params={"state": state, "per_page": 100}
                )
                if response.status_code == 200:
                    issues = response.json()
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps({
                                    "total": len(issues),
                                    "issues": [
                                        {
                                            "number": i.get("number"),
                                            "title": i.get("title"),
                                            "state": i.get("state", ""),
                                            "user": i.get("user", {}).get("login", ""),
                                            "created_at": i.get("created_at", ""),
                                            "html_url": i.get("html_url", "")
                                        }
                                        for i in issues
                                    ]
                                })
                            }
                        ]
                    }
                else:
                    raise Exception(f"GitHub API error: {response.status_code} - {response.text}")

            elif tool_name == "get_issue":
                owner = arguments.get("owner")
                repo = arguments.get("repo")
                issue_number = arguments.get("issue_number")

                response = await client.get(
                    f"{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}",
                    headers=self.headers
                )
                if response.status_code == 200:
                    i = response.json()
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps({
                                    "number": i.get("number"),
                                    "title": i.get("title"),
                                    "body": i.get("body", ""),
                                    "state": i.get("state", ""),
                                    "user": i.get("user", {}).get("login", ""),
                                    "labels": [l.get("name", "") for l in i.get("labels", [])],
                                    "assignees": [a.get("login", "") for a in i.get("assignees", [])],
                                    "created_at": i.get("created_at", ""),
                                    "updated_at": i.get("updated_at", ""),
                                    "html_url": i.get("html_url", "")
                                })
                            }
                        ]
                    }
                else:
                    raise Exception(f"GitHub API error: {response.status_code} - {response.text}")

            elif tool_name == "create_issue":
                owner = arguments.get("owner")
                repo = arguments.get("repo")
                title = arguments.get("title")
                body = arguments.get("body", "")

                payload = {
                    "title": title,
                    "body": body
                }

                response = await client.post(
                    f"{self.base_url}/repos/{owner}/{repo}/issues",
                    headers=self.headers,
                    json=payload
                )
                if response.status_code == 201:
                    i = response.json()
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps({
                                    "number": i.get("number"),
                                    "title": i.get("title"),
                                    "html_url": i.get("html_url", ""),
                                    "success": True
                                })
                            }
                        ]
                    }
                else:
                    raise Exception(f"GitHub API error: {response.status_code} - {response.text}")

            elif tool_name == "list_pull_requests":
                owner = arguments.get("owner")
                repo = arguments.get("repo")
                state = arguments.get("state", "open")

                response = await client.get(
                    f"{self.base_url}/repos/{owner}/{repo}/pulls",
                    headers=self.headers,
                    params={"state": state, "per_page": 100}
                )
                if response.status_code == 200:
                    prs = response.json()
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps({
                                    "total": len(prs),
                                    "pull_requests": [
                                        {
                                            "number": pr.get("number"),
                                            "title": pr.get("title"),
                                            "state": pr.get("state", ""),
                                            "user": pr.get("user", {}).get("login", ""),
                                            "created_at": pr.get("created_at", ""),
                                            "html_url": pr.get("html_url", "")
                                        }
                                        for pr in prs
                                    ]
                                })
                            }
                        ]
                    }
                else:
                    raise Exception(f"GitHub API error: {response.status_code} - {response.text}")

            elif tool_name == "github_api_call":
                # Generic API caller - allows calling any GitHub REST API endpoint
                endpoint = arguments.get("endpoint", "").lstrip("/")  # Remove leading slash
                method = arguments.get("method", "GET").upper()
                params = arguments.get("params", {})
                body = arguments.get("body", {})

                # Construct full URL
                url = f"{self.base_url}/{endpoint}"

                # Make the API call based on method
                if method == "GET":
                    response = await client.get(url, headers=self.headers, params=params)
                elif method == "POST":
                    response = await client.post(url, headers=self.headers, params=params, json=body if body else None)
                elif method == "PUT":
                    response = await client.put(url, headers=self.headers, params=params, json=body if body else None)
                elif method == "DELETE":
                    response = await client.delete(url, headers=self.headers, params=params)
                elif method == "PATCH":
                    response = await client.patch(url, headers=self.headers, params=params, json=body if body else None)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                # Return response
                if response.status_code in [200, 201, 204]:
                    try:
                        data = response.json() if response.text else {}
                        return {
                            "content": [
                                {
                                    "type": "text",
                                    "text": json.dumps({
                                        "status_code": response.status_code,
                                        "data": data,
                                        "success": True
                                    })
                                }
                            ]
                        }
                    except json.JSONDecodeError:
                        # Return raw text if not JSON
                        return {
                            "content": [
                                {
                                    "type": "text",
                                    "text": json.dumps({
                                        "status_code": response.status_code,
                                        "data": response.text,
                                        "success": True
                                    })
                                }
                            ]
                        }
                else:
                    # Error response
                    error_detail = response.text
                    try:
                        error_json = response.json()
                        error_detail = json.dumps(error_json)
                    except:
                        pass
                    raise Exception(f"GitHub API error ({method} {endpoint}): {response.status_code} - {error_detail}")

            else:
                raise ValueError(f"Unknown GitHub tool: {tool_name}")


@asynccontextmanager
async def get_github_mcp_wrapper_session(user_id: str, access_token: str) -> AsyncGenerator[ClientSession, None]:
    """
    Get a GitHub MCP wrapper session

    This creates a mock ClientSession that wraps the GitHubMCPWrapper
    """
    if not MCP_AVAILABLE:
        raise RuntimeError("MCP library not available")

    wrapper = GitHubMCPWrapper(user_id, access_token)

    # Create a simple session-like object
    class GitHubMCPSession:
        def __init__(self, wrapper):
            self.wrapper = wrapper

        async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
            return await self.wrapper.call_tool(name, arguments)

        async def list_tools(self):
            return await self.wrapper.list_tools()

    session = GitHubMCPSession(wrapper)
    try:
        yield session
    finally:
        pass  # Cleanup if needed
