# Native MCP Servers Setup Guide

## Overview

This project now uses **native MCP servers** for external integrations (GitHub, Jira, Google Drive) while keeping the **Company MCP Server** for business logic (prompts, database queries, OAuth management).

## Architecture

```
┌─────────────────┐
│   Agent API     │
│  (Python/FastAPI)│
└────────┬────────┘
         │
         ├─── HTTP ───> Company MCP Server (Prompts, DB, OAuth)
         │
         ├─── MCP ───> GitHub MCP Server (Official - Docker)
         │
         ├─── MCP ───> Jira MCP Server (Custom Python Wrapper)
         │
         └─── MCP ───> Google Drive MCP Server (Custom Python Wrapper)
```

## Components

### 1. Company MCP Server (`backend/mcp-server/`)
- **Purpose**: Business logic (prompts, database queries, OAuth management)
- **Status**: ✅ Keep as-is
- **Endpoints**: 
  - `/prompts/*` - Prompt management
  - `/insurance/*` - Insurance database queries
  - `/claimhub/*` - ClaimHub database queries
  - `/integrations/*` - OAuth token storage/retrieval

### 2. GitHub MCP Server (Official)
- **Source**: https://github.com/github/github-mcp-server
- **Type**: Official MCP server from GitHub
- **Language**: Go
- **Transport**: STDIO (via Docker)
- **Status**: ✅ Implemented

### 3. Jira MCP Server (Custom Wrapper)
- **Source**: Custom Python wrapper (`backend/agent-api/tools/jira_mcp_wrapper.py`)
- **Type**: Custom MCP server wrapper (no official MCP server exists)
- **Language**: Python
- **Transport**: In-process (no separate process needed)
- **Status**: ✅ Implemented

### 4. Google Drive MCP Server (Custom Wrapper)
- **Source**: Custom Python wrapper (`backend/agent-api/tools/drive_mcp_wrapper.py`)
- **Type**: Custom MCP server wrapper
- **Language**: Python
- **Transport**: In-process (no separate process needed)
- **Status**: ✅ Implemented

## Installation

### 1. Install MCP Python Client Library

```bash
cd backend/agent-api
pip install mcp>=1.0.0
```

Or add to `requirements.txt`:
```
mcp>=1.0.0
```

### 2. GitHub MCP Server Setup

#### Option A: Docker (Recommended)
GitHub MCP server runs via Docker. Ensure Docker is available:

```bash
# Test GitHub MCP server
docker run -i --rm \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=your_token_here \
  ghcr.io/github/github-mcp-server:latest
```

#### Option B: Binary
Download GitHub MCP server binary and ensure it's in PATH.

#### Configuration
- **Environment Variable**: `GITHUB_PERSONAL_ACCESS_TOKEN` (fallback if no user token)
- **User Tokens**: Retrieved from Company MCP Server via OAuth

### 3. Jira MCP Server Setup

No separate installation needed - uses custom Python wrapper.

#### Configuration
- **Jira Instance URL**: Set `JIRA_INSTANCE_URL` environment variable
  - Example: `https://your-domain.atlassian.net`
- **OAuth Tokens**: Retrieved from Company MCP Server
- **Instance URL**: Can be extracted from integration metadata or use env var

### 4. Google Drive MCP Server Setup

No separate installation needed - uses custom Python wrapper.

#### Configuration
- **OAuth Credentials**: `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` (required)
- **OAuth Tokens**: Retrieved from Company MCP Server

## Environment Variables

### Agent API

```bash
# Company MCP Server
MCP_URL=http://mcp-server:8001  # Local Docker
# MCP_URL=http://mcp-server.aap.local:8001  # ECS Production

# GitHub MCP Server
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_pat  # Fallback token
GITHUB_MCP_USE_DOCKER=true  # Use Docker (default) or false for binary

# Jira
JIRA_INSTANCE_URL=https://your-domain.atlassian.net

# Google Drive
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

## How It Works

### Token Flow

1. **User makes request** → Agent API receives request with user context
2. **Agent API needs OAuth token** → Calls Company MCP Server: `GET /integrations/{user_id}/{provider}/token`
3. **Company MCP Server** → Returns OAuth token from PostgreSQL
4. **Agent API** → Passes token to native MCP server
5. **Native MCP Server** → Uses token to call external API (GitHub/Jira/Drive)
6. **Response** → Returns to Agent API → Returns to user

### GitHub MCP Server Flow

```
User Request
    ↓
Agent API executor.py
    ↓
mcp_client.py → get_github_mcp_session()
    ├─ Get OAuth token from Company MCP Server
    ├─ Spawn Docker: docker run -e GITHUB_TOKEN=... github-mcp-server
    └─ Communicate via STDIO (MCP protocol)
        ↓
    Call tool: list_repositories, search_code, etc.
        ↓
    Return formatted result
```

### Jira MCP Server Flow

```
User Request
    ↓
Agent API executor.py
    ↓
mcp_client.py → get_jira_mcp_session()
    ├─ Get OAuth token from Company MCP Server
    ├─ Get Jira instance URL (env var or metadata)
    └─ Create JiraMCPWrapper (in-process)
        ↓
    Call Jira REST API directly
        ↓
    Return formatted result (MCP format)
```

### Drive MCP Server Flow

```
User Request
    ↓
Agent API executor.py
    ↓
mcp_client.py → get_drive_mcp_session()
    ├─ Get OAuth token from Company MCP Server
    └─ Create DriveMCPWrapper (in-process)
        ↓
    Call Google Drive API directly
        ↓
    Return formatted result (MCP format)
```

## Files Created/Modified

### New Files
1. `backend/agent-api/tools/mcp_client.py` - MCP client helper
2. `backend/agent-api/tools/jira_mcp_wrapper.py` - Jira MCP wrapper
3. `backend/agent-api/tools/drive_mcp_wrapper.py` - Drive MCP wrapper
4. `docs/MCP_SERVERS_INFO.md` - Information about all MCP servers
5. `docs/NATIVE_MCP_SERVERS_SETUP.md` - This file

### Modified Files
1. `backend/agent-api/requirements.txt` - Added `mcp>=1.0.0`
2. `backend/agent-api/tools/executor.py` - Updated all GitHub/Jira/Drive tools to use native MCP servers

## Testing

### Test GitHub MCP Server

```python
# In Python shell or test script
from backend.agent-api.tools.mcp_client import call_github_mcp_tool

result = await call_github_mcp_tool("list_repositories", {}, "user@example.com")
print(result)
```

### Test Jira MCP Server

```python
from backend.agent-api.tools.mcp_client import call_jira_mcp_tool

result = await call_jira_mcp_tool("jira_list_projects", {}, "user@example.com")
print(result)
```

### Test Drive MCP Server

```python
from backend.agent-api.tools.mcp_client import call_drive_mcp_tool

result = await call_drive_mcp_tool("drive_list_files", {}, "user@example.com")
print(result)
```

## Fallback Behavior

All tools implement **graceful fallback**:
1. **Try native MCP server first**
2. **If fails** → Fallback to Company MCP Server HTTP endpoints
3. **Ensures backward compatibility** during migration

## Troubleshooting

### GitHub MCP Server Issues

**Problem**: Docker not available
- **Solution**: Set `GITHUB_MCP_USE_DOCKER=false` and ensure binary is in PATH

**Problem**: Token not found
- **Solution**: Check OAuth integration in Company MCP Server, or set `GITHUB_PERSONAL_ACCESS_TOKEN`

### Jira MCP Server Issues

**Problem**: Instance URL not found
- **Solution**: Set `JIRA_INSTANCE_URL` environment variable

**Problem**: Token expired
- **Solution**: Reconnect Jira integration in Settings > Integrations

### Drive MCP Server Issues

**Problem**: OAuth credentials not configured
- **Solution**: Set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`

**Problem**: Token not found
- **Solution**: Connect Google Drive in Settings > Integrations

## Next Steps

### Phase 1: Testing (Current)
- [x] Implement all 3 native MCP servers
- [ ] Test GitHub operations end-to-end
- [ ] Test Jira operations end-to-end
- [ ] Test Drive operations end-to-end
- [ ] Verify fallback works correctly

### Phase 2: Cleanup (Future)
- [ ] Remove custom integration tools from Company MCP Server
- [ ] Remove HTTP endpoints `/tools/github/*`, `/tools/jira/*`, `/tools/drive/*`
- [ ] Update documentation

### Phase 3: Optimization (Future)
- [ ] Consider caching for frequently accessed data
- [ ] Optimize token retrieval (batch requests)
- [ ] Add connection pooling for MCP servers

## Notes

- **Company MCP Server** remains unchanged for prompts, DB, OAuth
- **Native MCP servers** are called on-demand (not always running)
- **OAuth tokens** are still managed by Company MCP Server
- **Fallback pattern** ensures no breaking changes

