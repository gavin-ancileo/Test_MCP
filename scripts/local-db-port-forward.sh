#!/bin/bash
# Local Database Port Forwarding via AWS Systems Manager Session Manager
# Forwards localhost:5432 to RDS database through ECS task

set -e

CLUSTER="aap-cluster"
SERVICE="aap-mcp-server-new"
CONTAINER="mcp-server"
REGION="ap-southeast-2"
RDS_HOST="aap-rds-new.cv2usk6ye3hm.ap-southeast-2.rds.amazonaws.com"
RDS_PORT="5432"
LOCAL_PORT="5432"

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
echo "🔗 Starting port forwarding..."
echo "   Local: localhost:$LOCAL_PORT"
echo "   Remote: $RDS_HOST:$RDS_PORT"
echo ""
echo "⚠️  Keep this terminal open while using the connection"
echo "   Press Ctrl+C to stop"
echo ""

# Install socat in container if needed, then start port forwarding
aws ecs execute-command \
  --cluster $CLUSTER \
  --task $TASK_ARN \
  --container $CONTAINER \
  --region $REGION \
  --interactive \
  --command "sh -c 'apt-get update && apt-get install -y socat || true; socat TCP-LISTEN:$LOCAL_PORT,fork,reuseaddr TCP:$RDS_HOST:$RDS_PORT'"









