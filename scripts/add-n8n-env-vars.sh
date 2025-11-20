#!/bin/bash
#
# Add N8N_URL and MCP_URL environment variables to Agent API task definition
#

set -e

AWS_REGION="ap-southeast-2"
TASK_DEF_NAME="aap-agentcore-new"

echo "🔍 Fetching current task definition for $TASK_DEF_NAME..."

# Get current task definition
aws ecs describe-task-definition \
  --task-definition "$TASK_DEF_NAME" \
  --region "$AWS_REGION" \
  --query 'taskDefinition' > /tmp/task-def.json

# Remove unnecessary fields
cat /tmp/task-def.json | jq 'del(.taskDefinitionArn, .revision, .status, .requiresAttributes, .compatibilities, .registeredAt, .registeredBy)' > /tmp/task-def-clean.json

# Add N8N_URL and MCP_URL to environment variables
echo "➕ Adding N8N_URL and MCP_URL environment variables..."

cat /tmp/task-def-clean.json | jq '
  .containerDefinitions[0].environment += [
    {"name": "N8N_URL", "value": "http://aap-n8n.aap.local:5678"},
    {"name": "MCP_URL", "value": "http://mcp-server.aap.local:8001"}
  ]
' > /tmp/task-def-new.json

# Register new task definition
echo "📤 Registering new task definition..."
NEW_TASK_DEF=$(aws ecs register-task-definition \
  --cli-input-json file:///tmp/task-def-new.json \
  --region "$AWS_REGION" \
  --query 'taskDefinition.taskDefinitionArn' \
  --output text)

echo "✅ New task definition registered: $NEW_TASK_DEF"

# Update service to use new task definition
echo "🚀 Updating service to use new task definition..."
aws ecs update-service \
  --cluster aap-cluster \
  --service "$TASK_DEF_NAME" \
  --task-definition "$NEW_TASK_DEF" \
  --force-new-deployment \
  --region "$AWS_REGION" \
  --no-cli-pager

echo "✅ Service updated! Waiting for deployment to stabilize..."

# Wait for service to stabilize
aws ecs wait services-stable \
  --cluster aap-cluster \
  --services "$TASK_DEF_NAME" \
  --region "$AWS_REGION" \
  || echo "⚠️ Wait timed out, check ECS console"

echo "🎉 Done! N8N_URL and MCP_URL have been added to the Agent API task definition."
