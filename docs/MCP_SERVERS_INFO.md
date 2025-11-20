# Thông Tin Đầy Đủ Về Native MCP Servers

## 1. GitHub MCP Server (Official)

### Thông Tin Cơ Bản
- **Repository**: https://github.com/github/github-mcp-server
- **Official**: ✅ Yes - Official GitHub MCP Server
- **Language**: Go
- **License**: MIT
- **Stars**: 24.6k+ stars
- **Documentation**: https://docs.github.com/en/copilot/how-tos/provide-context/use-mcp/use-the-github-mcp-server

### Tính Năng
- **Git Operations**: clone, commit, branch, diff, log, status, push, pull, merge, rebase, worktree, tag
- **Repository Management**: List repos, search code, read files, create/update files
- **Issues & PRs**: Create, list, get, update issues and pull requests
- **Security**: Security advisories, vulnerability scanning
- **Copilot**: Integration with GitHub Copilot
- **Search**: Code search, user search, repository search

### Transport Methods
- ✅ **STDIO**: Spawn process, communicate via stdin/stdout
- ✅ **HTTP**: Support HTTP transport (if configured)
- ✅ **Docker**: Can run as Docker container

### Installation

#### Option 1: Docker (Recommended)
```bash
docker run -i --rm \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=your_token_here \
  ghcr.io/github/github-mcp-server
```

#### Option 2: Binary
- Download binary from releases
- Run: `./github-mcp-server`

#### Option 3: Build from Source
```bash
git clone https://github.com/github/github-mcp-server
cd github-mcp-server
go build
```

### Configuration

#### Environment Variables
- `GITHUB_PERSONAL_ACCESS_TOKEN`: GitHub PAT with required scopes
- `GITHUB_DYNAMIC_TOOLSETS=1`: Enable dynamic toolset discovery
- `GITHUB_READ_ONLY=1`: Run in read-only mode
- `GITHUB_LOCKDOWN_MODE=1`: Enable lockdown mode

#### Required Scopes (GitHub PAT)
- `repo`: Full repository access
- `read:packages`: Read packages
- `read:org`: Read organization info
- `read:user`: Read user info

### Token Management
- **Single Token**: Uses one GitHub PAT for all operations
- **Per-User**: Not natively supported (uses single PAT)
- **OAuth**: Can use OAuth token instead of PAT

### Tools Available
- `list_repositories` - List GitHub repositories
- `search_code` - Search code across repos
- `read_file` - Read file contents
- `create_issue` - Create GitHub issue
- `list_issues` - List issues
- `create_pull_request` - Create PR
- `list_pull_requests` - List PRs
- `create_file` - Create file in repo
- `update_file` - Update file in repo
- `merge_pull_request` - Merge PR
- `create_branch` - Create branch
- `list_commits` - List commits
- `get_repository` - Get repo details
- `list_collaborators` - List collaborators
- And many more...

### Deployment Options
- **Local**: Run as binary or Docker container
- **Docker Compose**: Add as service
- **ECS/Fargate**: Deploy as container service
- **Kubernetes**: Deploy as pod

### Python Client
- MCP Python SDK: `mcp` package
- Example:
```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async with stdio_client(StdioServerParameters(
    command="docker",
    args=["run", "-i", "--rm", "-e", "GITHUB_PERSONAL_ACCESS_TOKEN=token", 
          "ghcr.io/github/github-mcp-server"]
)) as (read, write):
    async with ClientSession(read, write) as session:
        # Use session to call tools
        result = await session.call_tool("list_repositories", {})
```

---

## 2. Google Drive MCP Server

### Option A: mcp-gdrive (Community - Recommended)

#### Thông Tin Cơ Bản
- **Repository**: https://github.com/isaacphi/mcp-gdrive
- **Official**: ❌ No - Community project
- **Language**: Rust
- **Maintainer**: isaacphi
- **Status**: Active

#### Tính Năng
- List files in Google Drive
- Search files
- Read file contents
- Read/Write Google Sheets
- OAuth 2.0 authentication

#### Installation
```bash
# Install from source (Rust)
git clone https://github.com/isaacphi/mcp-gdrive
cd mcp-gdrive
cargo build --release

# Or use pre-built binary
```

#### Configuration
- **OAuth Setup**: Requires Google Cloud OAuth Client ID and Secret
- **Credentials**: Stored in local file after OAuth flow
- **Scopes**: `https://www.googleapis.com/auth/drive`

#### Transport
- ✅ STDIO
- ❌ HTTP (not supported)

### Option B: CData MCP Server for Google Drive

#### Thông Tin Cơ Bản
- **Website**: https://cdn.cdata.com/help/RGK/mcp
- **Official**: ❌ No - Third-party commercial
- **Language**: Unknown
- **Type**: Commercial/Enterprise solution

#### Tính Năng
- Search, read, write data on Google Drive
- No SQL required
- Enterprise features

#### Configuration
- Requires CData license
- OAuth setup required

### Option C: Google Workspace MCP Server

#### Thông Tin Cơ Bản
- **Website**: https://workspacemcp.com
- **Official**: ❌ No - Third-party
- **Language**: Unknown
- **Type**: Commercial solution

#### Tính Năng
- Full Google Workspace integration
- Gmail, Drive, Docs, Sheets, Calendar
- Multi-user OAuth 2.1 support
- One-time setup for Claude Desktop

#### Configuration
- OAuth 2.1 multi-user support
- One-time authentication setup

### Recommendation
- **For Development**: Use `mcp-gdrive` (open source, active)
- **For Enterprise**: Consider CData or Google Workspace MCP Server

---

## 3. Jira MCP Server

### Current Status
- **Official**: ❌ No official MCP server from Atlassian
- **Community**: ❌ No well-known community implementations found
- **Status**: Need to build custom or find alternative

### Options

#### Option 1: Build Custom MCP Server
- Use MCP SDK (Python, Go, TypeScript available)
- Implement Jira API integration
- Use existing OAuth flow from Company MCP Server

#### Option 2: Use Jira REST API Directly
- Keep current custom implementation
- Continue using `backend/mcp-server/tools/integration_tools.py` for Jira
- No migration needed

#### Option 3: Find Community Implementation
- Check MCP servers registry: https://github.com/modelcontextprotocol/servers
- Search for Jira-related implementations
- May need to adapt for your use case

### Jira API Requirements
- **Authentication**: OAuth 2.0 or API Token
- **Base URL**: `https://your-domain.atlassian.net`
- **API Version**: REST API v3
- **Scopes**: `read:jira-work`, `write:jira-work`, `manage:jira-project`

### Recommendation
- **Short-term**: Keep custom Jira implementation
- **Long-term**: Build custom MCP server if needed, or wait for official/community solution

---

## MCP Protocol & Python Client

### MCP Protocol
- **Standard**: Model Context Protocol (MCP)
- **Transport**: STDIO (stdin/stdout) or HTTP
- **Format**: JSON-RPC 2.0
- **Specification**: https://modelcontextprotocol.io

### Python MCP Client

#### Installation
```bash
pip install mcp
```

#### Basic Usage (STDIO)
```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async with stdio_client(StdioServerParameters(
    command="docker",
    args=["run", "-i", "--rm", "ghcr.io/github/github-mcp-server"]
)) as (read, write):
    async with ClientSession(read, write) as session:
        # Initialize
        await session.initialize()
        
        # List tools
        tools = await session.list_tools()
        
        # Call tool
        result = await session.call_tool("list_repositories", {})
```

#### HTTP Transport (if supported)
```python
from mcp.client.http import HttpClient

client = HttpClient("http://mcp-server:8001")
async with client:
    result = await client.call_tool("tool_name", {})
```

### MCP SDK Languages
- ✅ Python: `mcp` package
- ✅ TypeScript/JavaScript: `@modelcontextprotocol/sdk`
- ✅ Go: `github.com/modelcontextprotocol/go-sdk`
- ✅ Rust: `mcp-sdk` crate
- ✅ C#: Available
- ✅ Java: Available

---

## Deployment Architecture

### Recommended Setup

```
┌─────────────────┐
│   Agent API     │
│  (Python/FastAPI)│
└────────┬────────┘
         │
         ├─── HTTP ───> Company MCP Server (Prompts, DB, OAuth)
         │
         ├─── MCP ───> GitHub MCP Server (Docker/Process)
         │
         ├─── MCP ───> Google Drive MCP Server (Process)
         │
         └─── Keep ───> Custom Jira Tools (or build MCP server)
```

### Docker Compose Example

```yaml
services:
  # Company MCP Server (keep existing)
  mcp-server:
    build: ./backend/mcp-server
    ports:
      - "8001:8001"
    # ... existing config

  # GitHub MCP Server
  github-mcp-server:
    image: ghcr.io/github/github-mcp-server:latest
    environment:
      - GITHUB_PERSONAL_ACCESS_TOKEN=${GITHUB_PAT}
    # Runs via STDIO, needs to be spawned by agent-api

  # Google Drive MCP Server
  drive-mcp-server:
    # Build from mcp-gdrive source or use pre-built
    # Runs via STDIO, needs to be spawned by agent-api
```

### ECS/Fargate Deployment
- **Company MCP Server**: Keep as existing ECS service
- **Native MCP Servers**: 
  - Option 1: Spawn as processes within agent-api container
  - Option 2: Deploy as separate ECS tasks (more complex)
  - Option 3: Use HTTP transport if available (simpler)

---

## Migration Strategy

### Phase 1: GitHub MCP Server
1. Install GitHub MCP server locally
2. Test with sample requests
3. Integrate MCP client into agent-api
4. Replace GitHub tools in `executor.py`
5. Test end-to-end

### Phase 2: Google Drive MCP Server
1. Choose implementation (recommend mcp-gdrive)
2. Setup OAuth flow
3. Integrate MCP client
4. Replace Drive tools
5. Test end-to-end

### Phase 3: Jira
1. **Option A**: Keep custom implementation
2. **Option B**: Build custom MCP server
3. **Option C**: Wait for official/community solution

### Phase 4: Cleanup
1. Remove `integration_tools.py` (GitHub, Drive parts)
2. Remove HTTP endpoints `/tools/github/*`, `/tools/drive/*`
3. Keep Company MCP Server endpoints
4. Update documentation

---

## Key Considerations

### Token Management
- **GitHub**: Single PAT or OAuth token (not per-user)
- **Drive**: OAuth per-user (stored in Company MCP Server)
- **Jira**: OAuth per-user (stored in Company MCP Server)

### Multi-User Support
- **GitHub MCP Server**: Limited - uses single token
- **Drive MCP Server**: Supports per-user OAuth
- **Jira**: Need custom solution for multi-user

### Error Handling
- MCP protocol has different error format than HTTP
- Need to adapt error handling in `executor.py`
- MCP errors are JSON-RPC errors

### Performance
- STDIO transport: No network overhead, but process management needed
- HTTP transport: Network overhead, but simpler deployment
- Consider caching for frequently accessed data

---

## Resources

### Official Documentation
- MCP Specification: https://modelcontextprotocol.io
- GitHub MCP Server: https://github.com/github/github-mcp-server
- MCP Servers Registry: https://github.com/modelcontextprotocol/servers

### Python MCP Client
- Package: `pip install mcp`
- Documentation: Check MCP SDK docs
- Examples: https://github.com/modelcontextprotocol/servers

### Community Resources
- MCP Discord/Slack: Check MCP community
- GitHub Discussions: Check individual server repos
- Stack Overflow: Tag `model-context-protocol`

