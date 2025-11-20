"""
Jira MCP Server Wrapper
Custom MCP server wrapper for Jira since no official MCP server exists
This implements a simple MCP server interface that wraps Jira REST API calls
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


class JiraMCPWrapper:
    """
    Simple MCP server wrapper for Jira API
    Implements MCP protocol to wrap Jira REST API calls
    """
    
    def __init__(self, user_id: str, access_token: str, instance_url: Optional[str] = None, cloud_id: Optional[str] = None):
        self.user_id = user_id
        self.access_token = access_token
        self.cloud_id = cloud_id
        self.instance_url = instance_url

        # Use Jira Cloud API with cloudId for OAuth tokens
        if cloud_id:
            self.base_url = f"https://api.atlassian.com/ex/jira/{cloud_id}/rest/api/3"
        else:
            # Fallback to direct instance URL (legacy)
            self.base_url = f"{instance_url}/rest/api/3" if instance_url else "https://your-domain.atlassian.net/rest/api/3"

        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    async def list_tools(self) -> list[dict]:
        """List available Jira MCP tools"""
        return [
            {
                "name": "jira_list_projects",
                "description": "List all Jira projects accessible to the user",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "jira_search_issues",
                "description": "Search and count Jira issues using JQL (Jira Query Language). Use this to count bugs, find issues by status, assignee, or any other criteria across all projects. Examples: 'type=Bug AND status=Open' to count open bugs, 'project in (LEA, DEV) AND assignee=currentUser()' for your tickets.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "jql": {"type": "string", "description": "JQL query string (e.g., 'type=Bug', 'project=LEA AND status=Open')"},
                        "max_results": {"type": "integer", "description": "Maximum number of results to return (default 50, max 100)", "default": 50}
                    },
                    "required": ["jql"]
                }
            },
            {
                "name": "jira_get_issue",
                "description": "Get full details and summary of any specific Jira ticket by its key. Works for all project types (team-managed and company-managed). Use this when user asks about a specific ticket like 'LEA-660', 'ticket 123', or 'what is PROJECT-456 about'.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "issue_key": {"type": "string", "description": "Jira issue key in format PROJECT-NUMBER (e.g., LEA-660, DEV-123)"}
                    },
                    "required": ["issue_key"]
                }
            },
            {
                "name": "jira_create_issue",
                "description": "Create a new Jira issue",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_key": {"type": "string", "description": "Project key"},
                        "summary": {"type": "string", "description": "Issue summary"},
                        "description": {"type": "string", "description": "Issue description"},
                        "issue_type": {"type": "string", "description": "Issue type (e.g., Bug, Task)", "default": "Task"}
                    },
                    "required": ["project_key", "summary"]
                }
            },
            {
                "name": "jira_update_issue",
                "description": "Update a Jira issue",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "issue_key": {"type": "string", "description": "Jira issue key"},
                        "fields": {"type": "object", "description": "Fields to update"}
                    },
                    "required": ["issue_key", "fields"]
                }
            },
            {
                "name": "jira_add_comment",
                "description": "Add a comment to a Jira issue",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "issue_key": {"type": "string", "description": "Jira issue key"},
                        "body": {"type": "string", "description": "Comment body"}
                    },
                    "required": ["issue_key", "body"]
                }
            },
            {
                "name": "jira_get_project",
                "description": "Get details of a Jira project (supports all project types: team-managed, company-managed, business, service management, product discovery, etc.)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_key": {"type": "string", "description": "Jira project key (e.g., LEA, AQB, TSP, TPS)"}
                    },
                    "required": ["project_key"]
                }
            },
            {
                "name": "jira_get_boards",
                "description": "Get all boards in a project. Use this to find board IDs before adding issues to sprints. Works with both Scrum and Kanban boards.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_key": {
                            "type": "string",
                            "description": "The project key (e.g., 'LEA', 'PROJ')"
                        }
                    },
                    "required": ["project_key"]
                }
            },
            {
                "name": "jira_get_sprints",
                "description": "Get sprints in a board. Returns active, future, and/or closed sprints. Use this to find sprint IDs before adding issues.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "board_id": {
                            "type": "integer",
                            "description": "The board ID (get from jira_get_boards)"
                        },
                        "state": {
                            "type": "string",
                            "enum": ["active", "future", "closed"],
                            "description": "Filter by sprint state (optional). If not specified, returns all sprints."
                        }
                    },
                    "required": ["board_id"]
                }
            },
            {
                "name": "jira_add_to_sprint",
                "description": "Add an issue to a sprint. The issue will appear in the sprint board. Only works for Scrum boards.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "sprint_id": {
                            "type": "integer",
                            "description": "The sprint ID (get from jira_get_sprints)"
                        },
                        "issue_key": {
                            "type": "string",
                            "description": "The issue key (e.g., 'LEA-123')"
                        }
                    },
                    "required": ["sprint_id", "issue_key"]
                }
            },
            {
                "name": "jira_move_to_backlog",
                "description": "Move an issue to the board backlog (removes from any sprint). Only works for Scrum boards.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "issue_keys": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Array of issue keys to move to backlog (e.g., ['LEA-123', 'LEA-124'])"
                        }
                    },
                    "required": ["issue_keys"]
                }
            },
            {
                "name": "jira_assign_issue",
                "description": "Assign an issue to a user. Use empty string for account_id to unassign.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "issue_key": {
                            "type": "string",
                            "description": "The issue key (e.g., 'LEA-123')"
                        },
                        "account_id": {
                            "type": "string",
                            "description": "The Jira account ID of the user to assign. Use empty string '' to unassign. Get account ID from issue assignee or user search."
                        }
                    },
                    "required": ["issue_key", "account_id"]
                }
            },
            {
                "name": "jira_transition_issue",
                "description": "Transition an issue to a different status (e.g., 'In Progress', 'Done'). Use jira_get_transitions first to find valid transition IDs.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "issue_key": {
                            "type": "string",
                            "description": "The issue key (e.g., 'LEA-123')"
                        },
                        "transition_id": {
                            "type": "string",
                            "description": "The transition ID (use jira_get_transitions to find valid IDs for this issue)"
                        }
                    },
                    "required": ["issue_key", "transition_id"]
                }
            },
            {
                "name": "jira_get_transitions",
                "description": "Get available transitions for an issue. Use this to find transition IDs before calling jira_transition_issue. Different issues may have different available transitions based on their current status.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "issue_key": {
                            "type": "string",
                            "description": "The issue key (e.g., 'LEA-123')"
                        }
                    },
                    "required": ["issue_key"]
                }
            },
            {
                "name": "jira_api_call",
                "description": "Generic Jira REST API v3 caller - call ANY Jira API endpoint directly. Use this for advanced operations not covered by specific tools. See Jira Cloud REST API docs: https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/. Examples: GET /issue/{issueKey}/worklog (get work logs), POST /issue/{issueKey}/transitions (transition issue), GET /field (list custom fields), etc.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "endpoint": {
                            "type": "string",
                            "description": "API endpoint path (without base URL). Examples: '/search', '/issue/LEA-123', '/project/LEA/statuses', '/field'. Do NOT include '/rest/api/3' prefix."
                        },
                        "method": {
                            "type": "string",
                            "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"],
                            "description": "HTTP method",
                            "default": "GET"
                        },
                        "params": {
                            "type": "object",
                            "description": "Query parameters (e.g., {\"jql\": \"project=LEA\", \"maxResults\": 50})",
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
        """Call a Jira tool"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            if tool_name == "jira_list_projects":
                # Use /project/search to get ALL projects with pagination support
                # This endpoint returns all project types:
                # - team-managed software/business/service management
                # - company-managed software
                # - product discovery
                # - etc.
                all_projects = []
                start_at = 0
                max_results = 50

                while True:
                    response = await client.get(
                        f"{self.base_url}/project/search",
                        headers=self.headers,
                        params={
                            "expand": "description,lead,url,projectKeys,insight",
                            "startAt": start_at,
                            "maxResults": max_results
                        }
                    )
                    if response.status_code == 200:
                        data = response.json()
                        projects = data.get("values", [])
                        all_projects.extend(projects)

                        # Check if there are more results
                        total = data.get("total", 0)
                        if start_at + len(projects) >= total:
                            break
                        start_at += max_results
                    else:
                        raise Exception(f"Jira API error: {response.status_code} - {response.text}")

                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({
                                "total": len(all_projects),
                                "projects": [
                                    {
                                        "key": p.get("key"),
                                        "name": p.get("name"),
                                        "description": p.get("description", ""),
                                        "projectTypeKey": p.get("projectTypeKey", ""),  # software, business, service_desk, etc.
                                        "style": p.get("style", "unknown"),  # "team-managed", "company-managed", "next-gen", etc.
                                        "simplified": p.get("simplified", False),  # True for team-managed projects
                                        "projectCategory": p.get("projectCategory", {}).get("name", "") if p.get("projectCategory") else "",
                                        "projectTemplateKey": p.get("projectTemplateKey", ""),  # scrum, kanban, etc.
                                        "avatarUrls": p.get("avatarUrls", {})
                                    }
                                    for p in all_projects
                                ]
                            })
                        }
                    ]
                }
            
            elif tool_name == "jira_search_issues":
                jql = arguments.get("jql")
                max_results = arguments.get("max_results", 50)
                response = await client.get(
                    f"{self.base_url}/search",
                    headers=self.headers,
                    params={"jql": jql, "maxResults": max_results}
                )
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps({
                                    "total": data.get("total", 0),
                                    "issues": [
                                        {
                                            "key": issue.get("key"),
                                            "summary": issue["fields"].get("summary", ""),
                                            "status": issue["fields"]["status"].get("name", ""),
                                            "priority": issue["fields"].get("priority", {}).get("name", "N/A"),
                                            "assignee": issue["fields"].get("assignee", {}).get("displayName", "Unassigned") if issue["fields"].get("assignee") else "Unassigned"
                                        }
                                        for issue in data.get("issues", [])
                                    ]
                                })
                            }
                        ]
                    }
                else:
                    raise Exception(f"Jira API error: {response.status_code} - {response.text}")
            
            elif tool_name == "jira_get_issue":
                issue_key = arguments.get("issue_key")
                # Expand fields to support both team-managed and company-managed projects
                # Also try to get project info to determine project type
                response = await client.get(
                    f"{self.base_url}/issue/{issue_key}",
                    headers=self.headers,
                    params={"expand": "renderedFields,names,schema,transitions,operations,editmeta,changelog"}
                )
                if response.status_code == 200:
                    issue = response.json()
                    # Extract project key from issue key (e.g., "LEA-123" -> "LEA")
                    project_key = issue_key.split("-")[0] if "-" in issue_key else None

                    # Try to get project details to check if it's team-managed or company-managed
                    project_info = {}
                    if project_key:
                        try:
                            project_response = await client.get(
                                f"{self.base_url}/project/{project_key}",
                                headers=self.headers
                            )
                            if project_response.status_code == 200:
                                project_info = project_response.json()
                        except Exception as e:
                            print(f"[Jira MCP] Could not fetch project info for {project_key}: {e}")

                    # Extract description - handle both plain text and ADF (Atlassian Document Format)
                    description_field = issue["fields"].get("description")
                    if description_field:
                        if isinstance(description_field, dict):
                            # ADF format - extract plain text from content
                            def extract_text_from_adf(adf_node):
                                """Recursively extract text from ADF structure"""
                                if isinstance(adf_node, dict):
                                    if adf_node.get("type") == "text":
                                        return adf_node.get("text", "")
                                    if "content" in adf_node:
                                        return " ".join(extract_text_from_adf(child) for child in adf_node["content"])
                                elif isinstance(adf_node, list):
                                    return " ".join(extract_text_from_adf(item) for item in adf_node)
                                return ""
                            description = extract_text_from_adf(description_field).strip()
                        else:
                            description = str(description_field)
                    else:
                        description = ""

                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps({
                                    "key": issue.get("key"),
                                    "summary": issue["fields"].get("summary", ""),
                                    "description": description,
                                    "status": issue["fields"]["status"].get("name", ""),
                                    "priority": issue["fields"].get("priority", {}).get("name", "N/A") if issue["fields"].get("priority") else "N/A",
                                    "assignee": issue["fields"].get("assignee", {}).get("displayName", "Unassigned") if issue["fields"].get("assignee") else "Unassigned",
                                    "reporter": issue["fields"].get("reporter", {}).get("displayName", "Unknown") if issue["fields"].get("reporter") else "Unknown",
                                    "project_key": project_key,
                                    "project_type": project_info.get("style", "unknown") if project_info else "unknown",
                                    "project_name": project_info.get("name", "") if project_info else ""
                                })
                            }
                        ]
                    }
                elif response.status_code == 404:
                    # Try to provide more helpful error message
                    error_msg = f"Issue {issue_key} not found. This might be a company-managed project that requires different permissions or API access."
                    if project_key:
                        error_msg += f" Project key: {project_key}"
                    raise Exception(f"Jira API error 404: {error_msg}")
                else:
                    raise Exception(f"Jira API error: {response.status_code} - {response.text}")
            
            elif tool_name == "jira_create_issue":
                project_key = arguments.get("project_key")
                summary = arguments.get("summary")
                description = arguments.get("description", "")
                issue_type = arguments.get("issue_type", "Task")
                
                payload = {
                    "fields": {
                        "project": {"key": project_key},
                        "summary": summary,
                        "description": {"type": "doc", "version": 1, "content": [{"type": "paragraph", "content": [{"type": "text", "text": description}]}]},
                        "issuetype": {"name": issue_type}
                    }
                }
                
                response = await client.post(
                    f"{self.base_url}/issue",
                    headers=self.headers,
                    json=payload
                )
                if response.status_code == 201:
                    created = response.json()
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps({
                                    "key": created.get("key"),
                                    "id": created.get("id"),
                                    "self": created.get("self")
                                })
                            }
                        ]
                    }
                else:
                    raise Exception(f"Jira API error: {response.status_code} - {response.text}")
            
            elif tool_name == "jira_update_issue":
                issue_key = arguments.get("issue_key")
                fields = arguments.get("fields", {})
                
                payload = {"fields": fields}
                response = await client.put(
                    f"{self.base_url}/issue/{issue_key}",
                    headers=self.headers,
                    json=payload
                )
                if response.status_code == 204:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps({"success": True, "message": f"Issue {issue_key} updated"})
                            }
                        ]
                    }
                else:
                    raise Exception(f"Jira API error: {response.status_code} - {response.text}")
            
            elif tool_name == "jira_add_comment":
                issue_key = arguments.get("issue_key")
                body = arguments.get("body")
                
                payload = {
                    "body": {
                        "type": "doc",
                        "version": 1,
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [{"type": "text", "text": body}]
                            }
                        ]
                    }
                }
                
                response = await client.post(
                    f"{self.base_url}/issue/{issue_key}/comment",
                    headers=self.headers,
                    json=payload
                )
                if response.status_code == 201:
                    comment = response.json()
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps({
                                    "id": comment.get("id"),
                                    "body": comment.get("body", ""),
                                    "created": comment.get("created")
                                })
                            }
                        ]
                    }
                else:
                    raise Exception(f"Jira API error: {response.status_code} - {response.text}")
            
            elif tool_name == "jira_get_project":
                project_key = arguments.get("project_key")
                # Get project details with expand to support all project types:
                # - team-managed software/business/service management
                # - company-managed software
                # - product discovery
                # - next-gen projects
                response = await client.get(
                    f"{self.base_url}/project/{project_key}",
                    headers=self.headers,
                    params={"expand": "description,lead,url,projectKeys,insight,issueTypes"}
                )
                if response.status_code == 200:
                    project = response.json()
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps({
                                    "key": project.get("key"),
                                    "name": project.get("name"),
                                    "description": project.get("description", ""),
                                    "projectTypeKey": project.get("projectTypeKey", ""),  # software, business, service_desk, etc.
                                    "style": project.get("style", "unknown"),  # "team-managed", "company-managed", "next-gen", etc.
                                    "simplified": project.get("simplified", False),  # True for team-managed projects
                                    "projectCategory": project.get("projectCategory", {}).get("name", "") if project.get("projectCategory") else "",
                                    "projectTemplateKey": project.get("projectTemplateKey", ""),  # scrum, kanban, etc.
                                    "lead": project.get("lead", {}).get("displayName", "") if project.get("lead") else "",
                                    "url": project.get("url", ""),
                                    "avatarUrls": project.get("avatarUrls", {}),
                                    "issueTypes": [it.get("name", "") for it in project.get("issueTypes", [])] if project.get("issueTypes") else []
                                })
                            }
                        ]
                    }
                elif response.status_code == 404:
                    raise Exception(f"Project {project_key} not found. Please check the project key and your permissions.")
                else:
                    raise Exception(f"Jira API error: {response.status_code} - {response.text}")

            elif tool_name == "jira_get_boards":
                project_key = arguments.get("project_key")
                # Use Jira Agile API to get boards for a project
                # Note: This uses /rest/agile/1.0, not /rest/api/3
                agile_base = self.base_url.replace("/rest/api/3", "/rest/agile/1.0")
                response = await client.get(
                    f"{agile_base}/board",
                    headers=self.headers,
                    params={"projectKeyOrId": project_key}
                )
                if response.status_code == 200:
                    data = response.json()
                    boards = data.get("values", [])
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps({
                                    "total": len(boards),
                                    "boards": [
                                        {
                                            "id": board.get("id"),
                                            "name": board.get("name"),
                                            "type": board.get("type"),  # scrum, kanban, simple
                                            "self": board.get("self")
                                        }
                                        for board in boards
                                    ]
                                })
                            }
                        ]
                    }
                else:
                    raise Exception(f"Jira API error: {response.status_code} - {response.text}")

            elif tool_name == "jira_get_sprints":
                board_id = arguments.get("board_id")
                state = arguments.get("state")  # Optional: active, future, closed
                agile_base = self.base_url.replace("/rest/api/3", "/rest/agile/1.0")
                params = {}
                if state:
                    params["state"] = state

                response = await client.get(
                    f"{agile_base}/board/{board_id}/sprint",
                    headers=self.headers,
                    params=params
                )
                if response.status_code == 200:
                    data = response.json()
                    sprints = data.get("values", [])
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps({
                                    "total": len(sprints),
                                    "sprints": [
                                        {
                                            "id": sprint.get("id"),
                                            "name": sprint.get("name"),
                                            "state": sprint.get("state"),  # active, future, closed
                                            "startDate": sprint.get("startDate"),
                                            "endDate": sprint.get("endDate"),
                                            "goal": sprint.get("goal", "")
                                        }
                                        for sprint in sprints
                                    ]
                                })
                            }
                        ]
                    }
                else:
                    raise Exception(f"Jira API error: {response.status_code} - {response.text}")

            elif tool_name == "jira_add_to_sprint":
                sprint_id = arguments.get("sprint_id")
                issue_key = arguments.get("issue_key")
                agile_base = self.base_url.replace("/rest/api/3", "/rest/agile/1.0")

                # Get issue ID from key
                issue_response = await client.get(
                    f"{self.base_url}/issue/{issue_key}",
                    headers=self.headers,
                    params={"fields": "id"}
                )
                if issue_response.status_code != 200:
                    raise Exception(f"Failed to get issue: {issue_response.status_code} - {issue_response.text}")

                issue_id = issue_response.json().get("id")

                # Add issue to sprint
                response = await client.post(
                    f"{agile_base}/sprint/{sprint_id}/issue",
                    headers=self.headers,
                    json={"issues": [issue_id]}
                )
                if response.status_code == 204:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps({
                                    "success": True,
                                    "message": f"Issue {issue_key} added to sprint {sprint_id}"
                                })
                            }
                        ]
                    }
                else:
                    raise Exception(f"Jira API error: {response.status_code} - {response.text}")

            elif tool_name == "jira_move_to_backlog":
                issue_keys = arguments.get("issue_keys", [])
                agile_base = self.base_url.replace("/rest/api/3", "/rest/agile/1.0")

                # Get issue IDs from keys
                issue_ids = []
                for issue_key in issue_keys:
                    issue_response = await client.get(
                        f"{self.base_url}/issue/{issue_key}",
                        headers=self.headers,
                        params={"fields": "id"}
                    )
                    if issue_response.status_code == 200:
                        issue_ids.append(issue_response.json().get("id"))

                if not issue_ids:
                    raise Exception("No valid issue IDs found")

                # Move issues to backlog
                response = await client.post(
                    f"{agile_base}/backlog/issue",
                    headers=self.headers,
                    json={"issues": issue_ids}
                )
                if response.status_code == 204:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps({
                                    "success": True,
                                    "message": f"Moved {len(issue_ids)} issue(s) to backlog",
                                    "issues": issue_keys
                                })
                            }
                        ]
                    }
                else:
                    raise Exception(f"Jira API error: {response.status_code} - {response.text}")

            elif tool_name == "jira_assign_issue":
                issue_key = arguments.get("issue_key")
                account_id = arguments.get("account_id")

                # Assign issue (use empty string to unassign)
                payload = {"accountId": account_id if account_id else None}
                response = await client.put(
                    f"{self.base_url}/issue/{issue_key}/assignee",
                    headers=self.headers,
                    json=payload
                )
                if response.status_code == 204:
                    message = f"Issue {issue_key} assigned" if account_id else f"Issue {issue_key} unassigned"
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps({
                                    "success": True,
                                    "message": message
                                })
                            }
                        ]
                    }
                else:
                    raise Exception(f"Jira API error: {response.status_code} - {response.text}")

            elif tool_name == "jira_transition_issue":
                issue_key = arguments.get("issue_key")
                transition_id = arguments.get("transition_id")

                # Transition issue
                payload = {"transition": {"id": transition_id}}
                response = await client.post(
                    f"{self.base_url}/issue/{issue_key}/transitions",
                    headers=self.headers,
                    json=payload
                )
                if response.status_code == 204:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps({
                                    "success": True,
                                    "message": f"Issue {issue_key} transitioned"
                                })
                            }
                        ]
                    }
                else:
                    raise Exception(f"Jira API error: {response.status_code} - {response.text}")

            elif tool_name == "jira_get_transitions":
                issue_key = arguments.get("issue_key")

                # Get available transitions
                response = await client.get(
                    f"{self.base_url}/issue/{issue_key}/transitions",
                    headers=self.headers
                )
                if response.status_code == 200:
                    data = response.json()
                    transitions = data.get("transitions", [])
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps({
                                    "total": len(transitions),
                                    "transitions": [
                                        {
                                            "id": t.get("id"),
                                            "name": t.get("name"),
                                            "to": t.get("to", {}).get("name", ""),
                                            "hasScreen": t.get("hasScreen", False)
                                        }
                                        for t in transitions
                                    ]
                                })
                            }
                        ]
                    }
                else:
                    raise Exception(f"Jira API error: {response.status_code} - {response.text}")

            elif tool_name == "jira_api_call":
                # Generic API caller - allows calling any Jira REST API v3 endpoint
                endpoint = arguments.get("endpoint", "").lstrip("/")  # Remove leading slash if present
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
                    # Try to parse JSON response
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
                    raise Exception(f"Jira API error ({method} {endpoint}): {response.status_code} - {error_detail}")

            else:
                raise ValueError(f"Unknown Jira tool: {tool_name}")


@asynccontextmanager
async def get_jira_mcp_wrapper_session(user_id: str, access_token: str, instance_url: Optional[str] = None, cloud_id: Optional[str] = None) -> AsyncGenerator[ClientSession, None]:
    """
    Get a Jira MCP wrapper session

    This creates a mock ClientSession that wraps the JiraMCPWrapper
    """
    if not MCP_AVAILABLE:
        raise RuntimeError("MCP library not available")

    wrapper = JiraMCPWrapper(user_id, access_token, instance_url, cloud_id)
    
    # Create a simple session-like object
    class JiraMCPSession:
        def __init__(self, wrapper):
            self.wrapper = wrapper
        
        async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
            return await self.wrapper.call_tool(name, arguments)
        
        async def list_tools(self):
            return await self.wrapper.list_tools()
    
    session = JiraMCPSession(wrapper)
    try:
        yield session
    finally:
        pass  # Cleanup if needed

