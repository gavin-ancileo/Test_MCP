# MCP Migration Progress

## Completed (Phase 1 - Foundation)

### 1. Added MCP Python Client Library
- ✅ Added `mcp>=1.0.0` to `backend/agent-api/requirements.txt`
- This enables communication with native MCP servers

### 2. Created MCP Client Helper Module
- ✅ Created `backend/agent-api/tools/mcp_client.py`
- Functions:
  - `get_user_oauth_token()`: Retrieves OAuth tokens from Company MCP Server
  - `get_github_mcp_session()`: Creates GitHub MCP server session
  - `call_github_mcp_tool()`: Calls GitHub MCP tools
  - `get_drive_mcp_session()`: Placeholder for Drive MCP (to be implemented)
  - `call_drive_mcp_tool()`: Placeholder for Drive MCP (to be implemented)

### 3. Updated Executor to Use Native GitHub MCP Server
- ✅ Updated `backend/agent-api/tools/executor.py`:
  - Added MCP client imports
  - Updated `github_list_repos` to use native GitHub MCP server
  - Implemented fallback to HTTP (Company MCP Server) if native MCP fails
  - This ensures backward compatibility during migration

## Architecture

### Current Flow (GitHub List Repos)
```
User Request
    ↓
Agent API executor.py
    ↓
Try Native GitHub MCP Server (via mcp_client.py)
    ├─ Success → Return formatted result
    └─ Failure → Fallback to Company MCP Server HTTP
                    ↓
                Return formatted result
```

### Token Management
- OAuth tokens stored in Company MCP Server (PostgreSQL)
- Native MCP servers receive tokens via:
  - Environment variables (for GitHub PAT)
  - Per-user OAuth tokens (retrieved from Company MCP Server)

## Next Steps

### Phase 2: Complete GitHub Tools Migration
- [ ] Update `github_search_code` to use native MCP server
- [ ] Update `github_read_file` to use native MCP server
- [ ] Update other GitHub tools (create_issue, list_prs, etc.)
- [ ] Test all GitHub operations end-to-end

### Phase 3: Google Drive MCP Server
- [ ] Choose Drive MCP server implementation (mcp-gdrive recommended)
- [ ] Implement `get_drive_mcp_session()` in mcp_client.py
- [ ] Update Drive tools in executor.py
- [ ] Test Drive operations

### Phase 4: Jira
- [ ] Decision: Keep custom implementation or build MCP server
- [ ] If building MCP server: Create Jira MCP server
- [ ] If keeping custom: Document decision

### Phase 5: Cleanup
- [ ] Remove custom GitHub/Drive tools from Company MCP Server
- [ ] Remove HTTP endpoints `/tools/github/*`, `/tools/drive/*`
- [ ] Update documentation

## Configuration Needed

### Environment Variables
- `GITHUB_PERSONAL_ACCESS_TOKEN`: Fallback GitHub token (if no user token)
- `GITHUB_MCP_USE_DOCKER`: Set to 'true' to use Docker (default), 'false' for binary
- `MCP_URL`: Company MCP Server URL (for OAuth token retrieval)

### Docker Requirements
- Docker must be available to run GitHub MCP server container
- Or: GitHub MCP server binary must be in PATH

## Testing Checklist

- [ ] Test `github_list_repos` with native MCP server
- [ ] Test fallback to HTTP if native MCP fails
- [ ] Test with user OAuth token
- [ ] Test with environment variable token
- [ ] Verify Company MCP Server still works for prompts, DB, OAuth
- [ ] Test error handling

## Notes

- Implementation uses graceful fallback pattern
- Company MCP Server endpoints remain unchanged
- OAuth token management stays in Company MCP Server
- Native MCP servers are called on-demand (not always running)

