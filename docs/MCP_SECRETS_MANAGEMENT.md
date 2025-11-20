# MCP Integration - Secrets Manager Configuration

## Overview

Tất cả các secret keys cho MCP integration (GitHub, Jira, Google Drive) đều được lưu trong **AWS Secrets Manager** thay vì environment variables trực tiếp.

## Secrets Manager Secret: `AAP/{environment}/agentcore`

### Required Keys for MCP Integration

#### OAuth Client Credentials
```json
{
  "GITHUB_CLIENT_ID": "GitHub OAuth client ID",
  "GITHUB_CLIENT_SECRET": "GitHub OAuth client secret",
  "JIRA_CLIENT_ID": "Jira OAuth client ID",
  "JIRA_CLIENT_SECRET": "Jira OAuth secret",
  "GOOGLE_CLIENT_ID": "Google Drive OAuth client ID",
  "GOOGLE_CLIENT_SECRET": "Google Drive OAuth secret"
}
```

#### OAuth Redirect URIs
```json
{
  "GITHUB_REDIRECT_URI": "https://internal.assistant.leacare.ai/integrations/callback/github",
  "JIRA_REDIRECT_URI": "https://internal.assistant.leacare.ai/integrations/callback/jira",
  "GOOGLE_REDIRECT_URI": "https://internal.assistant.leacare.ai/integrations/callback/google"
}
```

#### MCP Server Configuration
```json
{
  "MCP_URL": "http://mcp-server.aap.local:8001"
}
```

#### Optional Keys (for fallback/defaults)
```json
{
  "GITHUB_PERSONAL_ACCESS_TOKEN": "Optional: GitHub PAT for fallback (if user hasn't connected)",
  "JIRA_INSTANCE_URL": "Optional: Default Jira instance URL (e.g., https://your-domain.atlassian.net)",
  "GITHUB_MCP_USE_DOCKER": "true",
  "DRIVE_MCP_USE_DOCKER": "false"
}
```

## Code Implementation

### Priority Order for Configuration Values

1. **User OAuth Token** (from Company MCP Server database) - Highest priority
2. **Secrets Manager** (`CONFIG` from `config.py`) - Second priority
3. **Environment Variables** (`os.getenv()`) - Fallback for local development

### Files Using Secrets Manager

#### `backend/agent-api/tools/mcp_client.py`
- Imports `CONFIG` from `config.py` (which loads from Secrets Manager)
- Uses `CONFIG.get('KEY') or os.getenv('KEY')` pattern for all secrets
- Supports fallback to environment variables for local development

**Example:**
```python
# Import configuration from Secrets Manager
from config import CONFIG

# Get GitHub token with fallback
github_token = CONFIG.get('GITHUB_PERSONAL_ACCESS_TOKEN') or os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')

# Get Google OAuth credentials
google_client_id = CONFIG.get('GOOGLE_CLIENT_ID') or os.getenv('GOOGLE_CLIENT_ID')
google_client_secret = CONFIG.get('GOOGLE_CLIENT_SECRET') or os.getenv('GOOGLE_CLIENT_SECRET')
```

## Adding New Keys to Secrets Manager

### Steps

1. **Update Secret in AWS Secrets Manager:**
   ```bash
   aws secretsmanager update-secret \
     --secret-id AAP/uat/agentcore \
     --secret-string file://infra/secrets/agentcore-updated.json
   ```

2. **Update Local Secret File:**
   - Edit `infra/secrets/agentcore-updated.json`
   - Add new key-value pairs

3. **Update Documentation:**
   - Update this file (`docs/MCP_SECRETS_MANAGEMENT.md`)
   - Update `docs/SECRETS_MANAGEMENT.md` if needed

4. **Code Auto-Loads:**
   - No code changes needed if using `CONFIG.get('KEY')` pattern
   - `config.py` automatically loads all keys from Secrets Manager

## Current Secret Keys (from `infra/secrets/agentcore-updated.json`)

```json
{
  "GITHUB_CLIENT_ID": "${GITHUB_CLIENT_ID}",
  "GITHUB_CLIENT_SECRET": "${GITHUB_CLIENT_SECRET}",
  "JIRA_CLIENT_ID": "${JIRA_CLIENT_ID}",
  "JIRA_CLIENT_SECRET": "${JIRA_CLIENT_SECRET}",
  "GOOGLE_CLIENT_ID": "${GOOGLE_CLIENT_ID}",
  "GOOGLE_CLIENT_SECRET": "${GOOGLE_CLIENT_SECRET}",
  "MCP_URL": "http://mcp-server.aap.local:8001",
  "GITHUB_REDIRECT_URI": "https://internal.assistant.leacare.ai/integrations/callback/github",
  "JIRA_REDIRECT_URI": "https://internal.assistant.leacare.ai/integrations/callback/jira",
  "GOOGLE_REDIRECT_URI": "https://internal.assistant.leacare.ai/integrations/callback/google"
}
```

## Benefits

1. **Centralized Management**: All secrets in one place (AWS Secrets Manager)
2. **Security**: No secrets in code or environment variables in production
3. **Easy Updates**: Update secrets without code changes
4. **Environment-Specific**: Different secrets for UAT vs Production
5. **Fallback Support**: Still works with env vars for local development

## Testing

### Local Development
- Can use environment variables (`.env` file or `docker-compose.yml`)
- Code will fallback to `os.getenv()` if Secrets Manager unavailable

### Production/UAT
- All secrets loaded from Secrets Manager via `config.py`
- ECS Task Definition injects secrets as environment variables
- Code uses `CONFIG` dictionary (loaded from Secrets Manager)

