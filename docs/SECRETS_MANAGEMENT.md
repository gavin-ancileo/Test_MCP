# Secrets Management - AAP Project

## Overview

The AAP (Ancileo Assistant Platform) project uses **AWS Secrets Manager** for all production secrets. This document describes the architecture, migration, and best practices.

## Architecture

### Secret Organization

```
AAP/
├── uat/                           # UAT environment
│   ├── agentcore                  # Agent API secrets (23 keys)
│   ├── mcp-server                 # MCP Server secrets (23 keys)
│   ├── frontend-config            # Frontend runtime config (10 keys)
│   └── n8n                        # N8N workflow automation (8 keys)
└── prod/                          # Production environment
    └── (same structure as uat)
```

### Services and Secrets

| Service | AWS Secret | Keys Count | Injection Method |
|---------|-----------|------------|------------------|
| **AgentCore** | `AAP/uat/agentcore` | 23 | ECS Task Definition (secrets section) |
| **MCP Server** | `AAP/uat/mcp-server` | 23 | ECS Task Definition (secrets section) |
| **Frontend** | `AAP/uat/frontend-config` | 10 | Runtime API (`/api/config`) |
| **N8N** | `AAP/uat/n8n` | 8 | ECS Task Definition |

---

## Secret Contents

### AAP/uat/agentcore (Agent API)

```json
{
  "DB_HOST": "RDS endpoint",
  "DB_PORT": "5432",
  "DB_NAME": "prompts",
  "DB_USER": "database username",
  "DB_PASSWORD": "database password",
  "OPENAI_API_KEY": "OpenAI API key",
  "OPENAI_MODEL": "gpt-4o",
  "USE_OPENAI": "true",
  "COGNITO_REGION": "ap-southeast-2",
  "COGNITO_USER_POOL_ID": "Cognito pool ID",
  "COGNITO_DOMAIN": "Cognito domain URL",
  "DYNAMODB_TABLE": "conversations table name",
  "MCP_URL": "MCP Server internal URL",
  "GITHUB_CLIENT_ID": "GitHub OAuth client ID",
  "GITHUB_CLIENT_SECRET": "GitHub OAuth secret",
  "GITHUB_REDIRECT_URI": "OAuth callback URL",
  "JIRA_CLIENT_ID": "Jira OAuth client ID",
  "JIRA_CLIENT_SECRET": "Jira OAuth secret",
  "JIRA_REDIRECT_URI": "OAuth callback URL",
  "GOOGLE_CLIENT_ID": "Google Drive OAuth client ID",
  "GOOGLE_CLIENT_SECRET": "Google Drive OAuth secret",
  "GOOGLE_REDIRECT_URI": "OAuth callback URL",
  "FORCE_ADMIN_MODE": "false"
}
```

### AAP/uat/mcp-server (MCP Server)

```json
{
  "DB_HOST": "Main RDS endpoint",
  "DB_PORT": "5432",
  "DB_NAME": "prompts",
  "DB_USER": "database username",
  "DB_PASSWORD": "database password",
  "AWS_REGION": "ap-southeast-2",
  "N8N_URL": "N8N internal URL",
  "GITHUB_CLIENT_ID": "For token refresh",
  "GITHUB_CLIENT_SECRET": "For token refresh",
  "JIRA_CLIENT_ID": "For token refresh",
  "JIRA_CLIENT_SECRET": "For token refresh",
  "GOOGLE_CLIENT_ID": "For token refresh",
  "GOOGLE_CLIENT_SECRET": "For token refresh",
  "CLAIMHUB_DB_HOST": "ClaimHub read replica",
  "CLAIMHUB_DB_PORT": "5432",
  "CLAIMHUB_DB_NAME": "assessment",
  "CLAIMHUB_DB_USER": "readonly username",
  "CLAIMHUB_DB_PASSWORD": "readonly password",
  "INSURANCE_DB_HOST": "Insurance DB endpoint",
  "INSURANCE_DB_PORT": "3306",
  "INSURANCE_DB_NAME": "insurance database",
  "INSURANCE_DB_USER": "readonly username",
  "INSURANCE_DB_PASSWORD": "readonly password"
}
```

### AAP/uat/frontend-config (Frontend Runtime Config)

```json
{
  "COGNITO_DOMAIN": "Cognito domain URL",
  "COGNITO_CLIENT_ID": "Cognito client ID",
  "COGNITO_USER_POOL_ID": "Cognito pool ID",
  "COGNITO_REGION": "ap-southeast-2",
  "COGNITO_REDIRECT_URI": "OAuth callback URL",
  "COGNITO_SCOPES": "openid email profile",
  "API_BASE_URL": "ALB URL for API",
  "AGENTCORE_URL": "ALB URL for AgentCore",
  "MCP_URL": "ALB URL for MCP",
  "ENVIRONMENT": "production"
}
```

---

## Code Integration

### Backend - Agent API

**File:** `backend/agent-api/app.py`

```python
def load_config():
    """Load from Secrets Manager or ENV (local dev)"""
    try:
        environment = os.getenv('ENVIRONMENT', 'uat')
        client = boto3.client('secretsmanager', region_name='ap-southeast-2')
        response = client.get_secret_value(SecretId=f'AAP/{environment}/agentcore')
        return json.loads(response['SecretString'])
    except Exception as e:
        print(f"WARNING: Could not load from Secrets Manager: {e}")
        # Fallback to env vars for local development
        return { ... }

CONFIG = load_config()
```

**New Endpoint:** `/api/config`

Frontend-facing endpoint that returns public configuration (Cognito, API URLs) loaded from Secrets Manager.

### Backend - MCP Server

**File:** `backend/mcp-server/app.py`

```python
def load_config():
    """Load config - prioritize env vars for local, SM for production"""
    if os.getenv('DB_HOST'):  # Local dev
        return { ... }

    # Production - AWS Secrets Manager
    try:
        environment = os.getenv('ENVIRONMENT', 'uat')
        client = boto3.client('secretsmanager')
        response = client.get_secret_value(SecretId=f'AAP/{environment}/mcp-server')
        return json.loads(response['SecretString'])
    except Exception as e:
        print(f"ERROR: {e}")
        raise
```

**Important:** No hardcoded fallback credentials in production code.

### Frontend - Runtime Config

**File:** `frontend/src/config/runtime-config.ts`

```typescript
export async function loadRuntimeConfig(): Promise<RuntimeConfig> {
  if (cachedConfig) return cachedConfig;

  const response = await fetch('/api/config');
  cachedConfig = await response.json();
  return cachedConfig;
}
```

**Usage:**

```typescript
import { loadRuntimeConfig } from '../config/runtime-config';

const config = await loadRuntimeConfig();
// Use config.cognitoDomain, config.apiBaseUrl, etc.
```

---

## ECS Task Definitions

### Secrets Injection

ECS automatically injects secrets from Secrets Manager as environment variables at runtime.

**Example (AgentCore):**

```json
{
  "containerDefinitions": [{
    "secrets": [
      {
        "name": "OPENAI_API_KEY",
        "valueFrom": "arn:aws:secretsmanager:ap-southeast-2:233693675018:secret:AAP/uat/agentcore-dnSo1q:OPENAI_API_KEY::"
      },
      {
        "name": "DB_PASSWORD",
        "valueFrom": "arn:aws:secretsmanager:ap-southeast-2:233693675018:secret:AAP/uat/agentcore-dnSo1q:DB_PASSWORD::"
      }
      // ... 18 more secrets
    ],
    "environment": [
      {"name": "ENVIRONMENT", "value": "prod"},
      {"name": "PYTHONDONTWRITEBYTECODE", "value": "1"}
    ]
  }]
}
```

**Key Points:**
- **Secrets** are injected at runtime (not visible in task definition)
- **Environment** variables are for non-sensitive config
- IAM Task Execution Role needs `secretsmanager:GetSecretValue` permission

---

## Local Development

### Setup

1. **Copy example file:**
   ```bash
   cp .env.example .env.local
   ```

2. **Fill in local values:**
   ```bash
   # .env.local
   DB_HOST=localhost
   DB_PORT=5432
   DB_USER=postgres
   DB_PASSWORD=postgres123
   OPENAI_API_KEY=sk-xxx-your-dev-key
   # ... other dev values
   ```

3. **Start services:**
   ```bash
   docker-compose up
   ```

### Local vs Production

| Aspect | Local Development | Production (AWS) |
|--------|------------------|------------------|
| Secrets Source | `.env.local` (git-ignored) | AWS Secrets Manager |
| Database | Docker PostgreSQL | AWS RDS |
| OAuth Redirect | `http://localhost:3000/callback` | `https://internal.assistant.leacare.ai/callback` |
| Frontend Config | Build-time env vars | Runtime API (`/api/config`) |

---

## Adding New Secrets

### Step 1: Add to Secrets Manager

```bash
# Get current secret
aws secretsmanager get-secret-value --secret-id AAP/uat/agentcore --query SecretString --output text > current.json

# Edit the JSON file
nano current.json
# Add your new key: "NEW_KEY": "new_value"

# Update the secret
aws secretsmanager update-secret --secret-id AAP/uat/agentcore --secret-string file://current.json

# Repeat for prod
aws secretsmanager update-secret --secret-id AAP/prod/agentcore --secret-string file://current.json
```

### Step 2: Update ECS Task Definition

```python
# In infra/scripts/update_task_definitions.py
# Add to the secrets list:

secrets = [
    # ... existing secrets ...
    create_secret_ref("AAP/uat/agentcore-dnSo1q", "NEW_KEY")
]
```

### Step 3: Register and Deploy

```bash
# Generate new task definition
python infra/scripts/update_task_definitions.py

# Register
aws ecs register-task-definition --cli-input-json file://infra/ecs-task-definitions/agentcore-task-def-new.json

# Deploy
aws ecs update-service --cluster aap-cluster --service aap-agentcore-new --task-definition aap-agentcore-new:71 --force-new-deployment
```

### Step 4: Update Code

```python
# backend/agent-api/app.py
# The new key is automatically available in CONFIG dict
new_value = CONFIG.get('NEW_KEY')
```

---

## Rotating Secrets

### Manual Rotation (Current)

1. Generate new credential
2. Update in AWS Secrets Manager
3. Deploy new ECS task (force new deployment)
4. Old tasks drain, new tasks pick up new secret

### Steps:

```bash
# 1. Update secret
aws secretsmanager update-secret --secret-id AAP/prod/agentcore --secret-string '{"DB_PASSWORD":"new-password",...}'

# 2. Update actual resource (e.g., RDS password)
aws rds modify-db-instance --db-instance-identifier aap-rds-new --master-user-password "new-password" --apply-immediately

# 3. Force ECS deployment
aws ecs update-service --cluster aap-cluster --service aap-agentcore-new --force-new-deployment
```

### Automatic Rotation (Future Enhancement)

AWS Secrets Manager supports automatic rotation via Lambda:
- RDS: Built-in rotation
- API Keys: Custom Lambda function
- OAuth Secrets: Refresh token flow

**Not implemented yet** - requires Lambda setup.

---

## Troubleshooting

### Issue: Service fails to start after deployment

**Check logs:**
```bash
aws logs tail /ecs/aap-agentcore-new --since 5m --follow
```

**Common causes:**
1. Missing secret key in Secrets Manager
2. IAM role lacks `secretsmanager:GetSecretValue` permission
3. Incorrect secret ARN in task definition

**Solution:**
```bash
# Verify secret exists
aws secretsmanager describe-secret --secret-id AAP/uat/agentcore

# Check IAM policy
aws iam get-role-policy --role-name ecsTaskExecutionRole --policy-name SecretsManagerPolicy
```

### Issue: Frontend shows "Failed to load config"

**Check:**
1. Backend `/api/config` endpoint is accessible
2. Frontend can reach backend (CORS, network)
3. AgentCore secret has required keys (COGNITO_DOMAIN, etc.)

**Test:**
```bash
curl https://internal.assistant.leacare.ai/api/config
```

### Issue: "Invalid state or missing code verifier" on login

**Cause:** Cognito redirect URI mismatch

**Solution:**
1. Check `COGNITO_REDIRECT_URI` in Secrets Manager
2. Verify it matches Cognito app client settings
3. Ensure ALB/CloudFront URL is correct

---

## Security Best Practices

### DO ✅

- Store all sensitive data in AWS Secrets Manager
- Use IAM roles (not access keys) for ECS tasks
- Rotate secrets regularly (quarterly minimum)
- Use separate secrets for UAT and prod
- Monitor Secrets Manager access via CloudTrail
- Use `.env.local` (git-ignored) for local development

### DON'T ❌

- Commit `.env`, `.env.production`, or any secret file to git
- Hardcode credentials in code
- Use same credentials across environments
- Log secret values (even in debug mode)
- Share secrets via Slack, email, or unencrypted channels
- Give developers direct access to prod Secrets Manager

---

## Migration Checklist

- [x] Create AWS Secrets Manager secrets for all environments
- [x] Update AgentCore task definition (20 secrets)
- [x] Update MCP Server task definition (22 secrets)
- [x] Remove hardcoded credentials from code
- [x] Implement frontend runtime config API
- [x] Deploy to ECS
- [x] Test authentication flow
- [x] Test OAuth integrations
- [x] Test external DB connections
- [x] Update .gitignore
- [x] Document secrets management
- [ ] Set up CloudWatch alerts for secret access
- [ ] Plan secret rotation schedule
- [ ] Train team on new process

---

## Support

For issues or questions:
1. Check CloudWatch logs first
2. Review this document
3. Contact DevOps team
4. AWS Support (for Secrets Manager issues)

**Last Updated:** 2025-11-07
**Maintained By:** DevOps Team
