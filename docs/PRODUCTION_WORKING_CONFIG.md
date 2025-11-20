# Production Working Configuration

**Status**: WORKING - OAuth integrations (GitHub, Jira, Google Drive) fully functional
**Date**: 2025-01-27
**Last Verified**: User confirmed "integrate và chat đc r" (integrations and chat working)

## Services Overview

### 1. MCP Server Service

**Service Details:**
- Service Name: `aap-mcp-server-new`
- Task Definition: `arn:aws:ecs:ap-southeast-2:233693675018:task-definition/aap-mcp-server-new:8`
- **Revision**: 8
- Desired Count: 1
- Running Count: 1
- Launch Type: FARGATE
- Created At: 2025-10-27T09:12:44.909000+07:00

**Task Definition Configuration:**
- Family: `aap-mcp-server-new`
- Revision: 8
- CPU: 512
- Memory: 1024
- Docker Image: `233693675018.dkr.ecr.ap-southeast-2.amazonaws.com/aap/mcp-server:latest`

**Environment Variables:**
```json
{
  "AWS_REGION": "ap-southeast-2",
  "ENVIRONMENT": "uat",
  "DB_HOST": "aap-rds-new.cv2usk6ye3hm.ap-southeast-2.rds.amazonaws.com",
  "DB_PORT": "5432",
  "DB_NAME": "prompts",
  "DB_USER": "AncileoMaster",
  "INSURANCE_DB_HOST": "insurance-rds-core-uat-aurora-ai-reader.cpqslknntpar.ap-southeast-1.rds.amazonaws.com",
  "INSURANCE_DB_PORT": "3306",
  "INSURANCE_DB_NAME": "insurance-platform-dev",
  "INSURANCE_DB_USER": "ti_ai_usr",
  "INSURANCE_DB_PASSWORD": "o332:mPIr!09",
  "CLAIMHUB_DB_HOST": "uat-read-replica-claimhub.ceqjfmi6jhdd.ap-southeast-1.rds.amazonaws.com",
  "CLAIMHUB_DB_PORT": "5432",
  "CLAIMHUB_DB_NAME": "assessment",
  "CLAIMHUB_DB_USER": "mcp_readonly",
  "CLAIMHUB_DB_PASSWORD": "37BpB6133EXV"
}
```

**KEY CONFIGURATION:**
- **DB_NAME is set to "prompts"** - This is CRITICAL for OAuth integrations to work
- The OAuth tokens are stored in the `prompts` database, NOT `aap_db`

---

### 2. Agent API Service

**Service Details:**
- Service Name: `aap-agentcore-new`
- Task Definition: `arn:aws:ecs:ap-southeast-2:233693675018:task-definition/aap-agentcore-new:62`
- **Revision**: 62
- Desired Count: 1
- Running Count: 1
- Launch Type: FARGATE
- Created At: 2025-10-27T09:12:20.678000+07:00

**Task Definition Configuration:**
- Family: `aap-agentcore-new`
- Revision: 62
- CPU: 1024
- Memory: 2048
- Docker Image: `233693675018.dkr.ecr.ap-southeast-2.amazonaws.com/aap/agentcore:improved-tool-desc`

---

## Key Points for Reverting

If you need to revert back to this working configuration:

### MCP Server
```bash
# Update MCP Server to task definition revision 8
aws ecs update-service \
  --cluster aap-cluster \
  --service aap-mcp-server-new \
  --task-definition aap-mcp-server-new:8 \
  --region ap-southeast-2
```

### Agent API
```bash
# Update Agent API to task definition revision 62
aws ecs update-service \
  --cluster aap-cluster \
  --service aap-agentcore-new \
  --task-definition aap-agentcore-new:62 \
  --region ap-southeast-2
```

### Or use AWS Console
1. Navigate to ECS → Clusters → aap-cluster
2. Click on the service (aap-mcp-server-new or aap-agentcore-new)
3. Click "Update Service"
4. Select task definition revision:
   - MCP Server: revision 8
   - Agent API: revision 62
5. Click "Update"

---

## Testing OAuth Integrations

After reverting, test with these commands in the chat:
- `any files in my drive` - Tests Google Drive integration
- `any project in my jira` - Tests Jira integration
- `any repos in my github` - Tests GitHub integration

**Expected Results:**
User confirmed working with:
- 45 files found in Google Drive
- 25 Jira projects found
- GitHub integration working

---

## Critical Database Configuration

The MCP Server MUST have these environment variables set:
- `DB_NAME=prompts` (NOT `aap_db`)
- `DB_HOST=aap-rds-new.cv2usk6ye3hm.ap-southeast-2.rds.amazonaws.com`
- `DB_USER=AncileoMaster`

This configuration ensures that OAuth tokens are retrieved from the correct database where they are stored by the Agent API during the OAuth callback flow.

---

## Docker Images

**MCP Server:**
- Tag: `latest` (currently working)
- Full path: `233693675018.dkr.ecr.ap-southeast-2.amazonaws.com/aap/mcp-server:latest`

**Agent API:**
- Tag: `improved-tool-desc` (currently working)
- Full path: `233693675018.dkr.ecr.ap-southeast-2.amazonaws.com/aap/agentcore:improved-tool-desc`

To pull specific images:
```bash
# Login to ECR
aws ecr get-login-password --region ap-southeast-2 | docker login --username AWS --password-stdin 233693675018.dkr.ecr.ap-southeast-2.amazonaws.com

# Pull MCP Server
docker pull 233693675018.dkr.ecr.ap-southeast-2.amazonaws.com/aap/mcp-server:latest

# Pull Agent API
docker pull 233693675018.dkr.ecr.ap-southeast-2.amazonaws.com/aap/agentcore:improved-tool-desc
```

---

## Notes

- All integrations (GitHub, Jira, Google Drive) confirmed working on 2025-01-27
- User manually fixed configuration directly on production via AWS Console
- DO NOT use `aws ecs update-service --force-new-deployment` alone - it only restarts with the same image
- To deploy new code, you MUST push a new Docker image to ECR and update the task definition
