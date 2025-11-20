# Google Drive MCP Server

Native TypeScript MCP server for Google Drive integration with multi-user OAuth support.

## Architecture

This is a **native MCP protocol server** that replaces the previous Python wrapper. It provides:

- ✅ True MCP protocol compliance using `@modelcontextprotocol/sdk`
- ✅ Official Google APIs Node.js client (`googleapis`)
- ✅ Multi-user OAuth support (token passed per-request via environment)
- ✅ STDIO transport for communication with Agent API
- ✅ Per-request process spawning (isolated per user)

## Features

### 7 Tools Implemented

1. **drive_list_files** - List files with optional filtering and folder support
2. **drive_search_files** - Search by name or content
3. **drive_read_file** - Read file content (handles Google Workspace files automatically)
4. **drive_create_file** - Create new files
5. **drive_update_file** - Update existing files
6. **drive_export_file** - Export Google Workspace files to PDF/DOCX/CSV/etc
7. **drive_api_call** - Universal Drive API v3 caller for advanced operations

### Google Workspace File Support

Automatically handles export for:
- 📄 **Google Docs** → text/plain
- 📊 **Google Sheets** → text/csv
- 📽️ **Google Slides** → application/pdf
- 🎨 **Google Drawings** → application/pdf
- 📝 **Google Forms** → application/zip

## Development

### Prerequisites

- Node.js 20+
- npm or yarn

### Local Setup

```bash
# Install dependencies
npm install

# Build TypeScript
npm run build

# Test with a sample token
GOOGLE_DRIVE_ACCESS_TOKEN="ya29.a0AfB_..." node dist/index.js
```

### Testing

Test the server using the MCP Inspector:

```bash
# Install MCP Inspector
npm install -g @modelcontextprotocol/inspector

# Run server with test token
GOOGLE_DRIVE_ACCESS_TOKEN="your_token" npx @modelcontextprotocol/inspector node dist/index.js
```

## Deployment

### Docker Build

The server is built as part of the agent-api Docker image using multi-stage build:

```dockerfile
# Stage 1: Build TypeScript MCP server
FROM node:20-slim AS drive-mcp-builder
WORKDIR /drive-mcp-server
COPY ../drive-mcp-server/package*.json ./
RUN npm ci
COPY ../drive-mcp-server/tsconfig.json ./
COPY ../drive-mcp-server/src ./src
RUN npm run build

# Stage 2: Copy to Python container
FROM python:3.11-slim
COPY --from=drive-mcp-builder /drive-mcp-server/dist /app/drive-mcp-server/dist
COPY --from=drive-mcp-builder /drive-mcp-server/node_modules /app/drive-mcp-server/node_modules
```

### Environment Variables

- `GOOGLE_DRIVE_ACCESS_TOKEN` (required): User's OAuth access token
  - Passed per-request by Agent API
  - Token is unique per user
  - Automatically retrieved from Company MCP Server

### Production Usage

The Agent API spawns this server per-request:

```python
# In backend/agent-api/tools/mcp_client.py
server_params = StdioServerParameters(
    command="node",
    args=["/app/drive-mcp-server/dist/index.js"],
    env={"GOOGLE_DRIVE_ACCESS_TOKEN": user_token}
)
```

## Architecture Diagram

```
┌─────────────────────────────────────────┐
│ Agent API (Python/FastAPI)              │
│                                          │
│  1. Receive tool call with user_id      │
│  2. Get user's OAuth token              │
│  3. Spawn MCP server with token         │
│  4. Call tool via STDIO                  │
│  5. Return result                        │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ Drive MCP Server (TypeScript/Node.js)   │
│                                          │
│  - Reads token from environment         │
│  - Implements MCP protocol              │
│  - Calls Google Drive API v3            │
│  - Returns JSON-RPC responses           │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ Google Drive API v3                      │
└─────────────────────────────────────────┘
```

## Benefits Over Previous Wrapper

| Aspect | Python Wrapper | Native MCP Server |
|--------|----------------|-------------------|
| **Protocol** | Mimics MCP | True MCP protocol |
| **Token Refresh** | ❌ None | ✅ Via Agent API |
| **MIME Types** | ❌ Incomplete | ✅ All Workspace types |
| **Export Validation** | ❌ No validation | ✅ Validates before export |
| **Binary Files** | ❌ Corruption issues | ✅ Proper handling |
| **Error Format** | Custom | JSON-RPC standard |
| **SDK** | Manual REST | Official `googleapis` |
| **Testing** | Coupled | Independent |

## Error Handling

The server provides enhanced error handling:

```json
{
  "error": "File not found",
  "code": 404,
  "tool": "drive_read_file",
  "details": []
}
```

All errors follow JSON-RPC error format for consistency with MCP protocol.

## Security

- ✅ Token only in process environment (not files)
- ✅ Process dies after request (no persistence)
- ✅ No shared state between users
- ✅ Token never logged to stdout

## Monitoring

Server logs to stderr (doesn't interfere with STDIO protocol):

```
[Drive MCP] Server started successfully
[Drive MCP] Error executing drive_read_file: File not found
```

Agent API logs:

```
[MCP Client] Drive MCP server initialized for user user@example.com
[MCP Client] Error connecting to Drive MCP server: ...
[MCP Client] Falling back to Drive wrapper
```

## Troubleshooting

### Server not found

If you see:
```
[MCP Client] Drive MCP server not found at /app/drive-mcp-server/dist/index.js, falling back to wrapper
```

**Solution**: Ensure Docker build completed successfully and server was copied to final image.

### Token expired

If you see 401 errors:
```
{
  "error": "Request had invalid authentication credentials",
  "code": 401
}
```

**Solution**: User needs to reconnect Google Drive in Settings > Integrations. The Agent API automatically handles token refresh from Company MCP Server.

### Node.js not found

If you see:
```
Error: spawn node ENOENT
```

**Solution**: Ensure Node.js is installed in the Docker image (should be in Dockerfile stage 2).

## Future Enhancements

- [ ] Add rate limit handling with exponential backoff
- [ ] Implement token refresh within MCP server (currently handled by Agent API)
- [ ] Add support for Google Drive streaming (large files)
- [ ] Implement batch operations for multiple files
- [ ] Add Google Sheets API integration (advanced spreadsheet operations)
- [ ] Add Google Docs API integration (advanced document editing)

## License

MIT - Part of Ancileo AI Assistant Platform
