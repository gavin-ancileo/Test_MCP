# Local Database Port Forwarding via AWS Systems Manager Session Manager
# Forwards localhost:5432 to RDS database through ECS task
# Usage: .\local-db-port-forward.ps1

$CLUSTER = "aap-cluster"
$SERVICE = "aap-mcp-server-new"
$CONTAINER = "mcp-server"
$REGION = "ap-southeast-2"
$RDS_HOST = "aap-rds-new.cv2usk6ye3hm.ap-southeast-2.rds.amazonaws.com"
$RDS_PORT = "5432"
$LOCAL_PORT = "5432"

Write-Host "🔍 Getting running task ARN..." -ForegroundColor Cyan
$TASK_ARN = aws ecs list-tasks `
  --cluster $CLUSTER `
  --service-name $SERVICE `
  --region $REGION `
  --desired-status RUNNING `
  --query 'taskArns[0]' `
  --output text

if ([string]::IsNullOrWhiteSpace($TASK_ARN) -or $TASK_ARN -eq "None") {
  Write-Host "❌ No running task found for service $SERVICE" -ForegroundColor Red
  exit 1
}

Write-Host "✅ Found task: $TASK_ARN" -ForegroundColor Green
Write-Host ""
Write-Host "🔗 Starting port forwarding..." -ForegroundColor Cyan
Write-Host "   Local: localhost:$LOCAL_PORT"
Write-Host "   Remote: $RDS_HOST:$RDS_PORT"
Write-Host ""
Write-Host "⚠️  Keep this terminal open while using the connection" -ForegroundColor Yellow
Write-Host "   Press Ctrl+C to stop"
Write-Host ""

# Start port forwarding
aws ecs execute-command `
  --cluster $CLUSTER `
  --task $TASK_ARN `
  --container $CONTAINER `
  --region $REGION `
  --interactive `
  --command "sh -c 'apt-get update && apt-get install -y socat || true; socat TCP-LISTEN:$LOCAL_PORT,fork,reuseaddr TCP:$RDS_HOST:$RDS_PORT'"









