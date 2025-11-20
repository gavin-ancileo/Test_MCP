#!/bin/bash
# Quick fix for N8N connectivity - Run directly on AWS CloudShell
# Just copy and paste this entire script

set -e

echo "🔧 Adding N8N_URL and MCP_URL to Agent API task definition..."

# Fetch current task definition
aws ecs describe-task-definition \
  --task-definition aap-agentcore-new \
  --region ap-southeast-2 \
  --query 'taskDefinition' > /tmp/task-def.json

# Clean up unnecessary fields
cat /tmp/task-def.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
for key in ['taskDefinitionArn', 'revision', 'status', 'requiresAttributes', 'compatibilities', 'registeredAt', 'registeredBy']:
    data.pop(key, None)
print(json.dumps(data, indent=2))
" > /tmp/task-def-clean.json

# Add environment variables
cat /tmp/task-def-clean.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
env_vars = data['containerDefinitions'][0].get('environment', [])

# Remove if already exists
env_vars = [e for e in env_vars if e['name'] not in ['N8N_URL', 'MCP_URL']]

# Add new variables
env_vars.extend([
    {'name': 'N8N_URL', 'value': 'http://aap-n8n.aap.local:5678'},
    {'name': 'MCP_URL', 'value': 'http://mcp-server.aap.local:8001'}
])

data['containerDefinitions'][0]['environment'] = env_vars
print(json.dumps(data, indent=2))
" > /tmp/task-def-new.json

# Register new task definition
echo "📤 Registering new task definition..."
NEW_TASK_DEF=$(aws ecs register-task-definition \
  --cli-input-json file:///tmp/task-def-new.json \
  --region ap-southeast-2 \
  --query 'taskDefinition.taskDefinitionArn' \
  --output text)

echo "✅ New task definition: $NEW_TASK_DEF"

# Update service
echo "🚀 Updating Agent API service..."
aws ecs update-service \
  --cluster aap-cluster \
  --service aap-agentcore-new \
  --task-definition "$NEW_TASK_DEF" \
  --force-new-deployment \
  --region ap-southeast-2 \
  --no-cli-pager

echo ""
echo "✅ DONE! Service is updating..."
echo "⏳ Wait 2-3 minutes for new task to start, then test admin panel"
echo ""
echo "Verify with: aws ecs describe-services --cluster aap-cluster --services aap-agentcore-new --region ap-southeast-2 --query 'services[0].deployments'"
