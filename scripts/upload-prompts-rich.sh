#!/bin/bash
# Upload 40-prompts-rich.sql to database via ECS task
# This script uses ECS execute-command to connect to container and run psql

set -e

CLUSTER="aap-cluster"
SERVICE="aap-mcp-server-new"
CONTAINER="mcp-server"
REGION="ap-southeast-2"
SQL_FILE="40-prompts-rich.sql"

echo "🔍 Getting running task ARN..."
TASK_ARN=$(aws ecs list-tasks \
  --cluster $CLUSTER \
  --service-name $SERVICE \
  --region $REGION \
  --desired-status RUNNING \
  --query 'taskArns[0]' \
  --output text)

if [ -z "$TASK_ARN" ] || [ "$TASK_ARN" == "None" ]; then
  echo "❌ No running task found for service $SERVICE"
  exit 1
fi

echo "✅ Found task: $TASK_ARN"
echo ""

# Get database credentials from Secrets Manager
echo "🔐 Getting database credentials..."
SECRET=$(aws secretsmanager get-secret-value \
  --secret-id AAP/uat/mcp-server \
  --region $REGION \
  --query SecretString \
  --output text)

DB_HOST=$(echo $SECRET | jq -r '.DB_HOST')
DB_PORT=$(echo $SECRET | jq -r '.DB_PORT')
DB_NAME=$(echo $SECRET | jq -r '.DB_NAME')
DB_USER=$(echo $SECRET | jq -r '.DB_USER')
DB_PASSWORD=$(echo $SECRET | jq -r '.DB_PASSWORD')

echo "📝 Uploading SQL file to database..."
echo "   Database: $DB_HOST:$DB_PORT/$DB_NAME"
echo "   User: $DB_USER"
echo ""

# Check if SQL file exists in container
# If not, we'll need to copy it or read from local file
if [ -f "backend/mcp-server/$SQL_FILE" ]; then
  echo "📄 SQL file found locally, will copy to container..."
  # Copy SQL file content to container and execute
  SQL_CONTENT=$(cat "backend/mcp-server/$SQL_FILE")
  
  # Execute SQL via psql in container
  aws ecs execute-command \
    --cluster $CLUSTER \
    --task $TASK_ARN \
    --container $CONTAINER \
    --region $REGION \
    --interactive \
    --command "sh -c 'export PGPASSWORD=\"$DB_PASSWORD\" && psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c \"$SQL_CONTENT\"'"
else
  echo "⚠️  SQL file not found locally, checking if it exists in container..."
  # Try to execute SQL file if it exists in container
  aws ecs execute-command \
    --cluster $CLUSTER \
    --task $TASK_ARN \
    --container $CONTAINER \
    --region $REGION \
    --interactive \
    --command "sh -c 'if [ -f \"/app/$SQL_FILE\" ]; then export PGPASSWORD=\"$DB_PASSWORD\" && psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f /app/$SQL_FILE; else echo \"SQL file not found in container\"; fi'"
fi

echo ""
echo "✅ SQL upload completed!"
echo "🔍 Verifying prompts count..."
aws ecs execute-command \
  --cluster $CLUSTER \
  --task $TASK_ARN \
  --container $CONTAINER \
  --region $REGION \
  --interactive \
  --command "sh -c 'export PGPASSWORD=\"$DB_PASSWORD\" && psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c \"SELECT COUNT(*) as prompt_count FROM prompts;\"'"









