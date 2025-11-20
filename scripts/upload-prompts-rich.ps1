# Upload 40-prompts-rich.sql to database via ECS task
# PowerShell version for Windows

$CLUSTER = "aap-cluster"
$SERVICE = "aap-mcp-server-new"
$CONTAINER = "mcp-server"
$REGION = "ap-southeast-2"
$SQL_FILE = "40-prompts-rich.sql"

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

# Get database credentials from Secrets Manager
Write-Host "🔐 Getting database credentials..." -ForegroundColor Cyan
$SECRET_JSON = aws secretsmanager get-secret-value `
  --secret-id AAP/uat/mcp-server `
  --region $REGION `
  --query SecretString `
  --output text | ConvertFrom-Json

$DB_HOST = $SECRET_JSON.DB_HOST
$DB_PORT = $SECRET_JSON.DB_PORT
$DB_NAME = $SECRET_JSON.DB_NAME
$DB_USER = $SECRET_JSON.DB_USER
$DB_PASSWORD = $SECRET_JSON.DB_PASSWORD

Write-Host "📝 Uploading SQL file to database..." -ForegroundColor Cyan
Write-Host "   Database: $DB_HOST`:$DB_PORT/$DB_NAME"
Write-Host "   User: $DB_USER"
Write-Host ""

# Check if SQL file exists locally
$SQL_PATH = "backend\mcp-server\$SQL_FILE"
if (Test-Path $SQL_PATH) {
  Write-Host "📄 SQL file found locally, reading content..." -ForegroundColor Green
  $SQL_CONTENT = Get-Content $SQL_PATH -Raw
  
  # Escape SQL content for command line
  $SQL_CONTENT_ESCAPED = $SQL_CONTENT -replace '"', '\"' -replace '`', '\`' -replace '\$', '\$'
  
  Write-Host "🚀 Executing SQL via ECS task..." -ForegroundColor Yellow
  Write-Host ""
  
  # Execute SQL via psql in container
  $COMMAND = "sh -c 'export PGPASSWORD=`"$DB_PASSWORD`" && echo `"$($SQL_CONTENT_ESCAPED)`" | psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME'"
  
  aws ecs execute-command `
    --cluster $CLUSTER `
    --task $TASK_ARN `
    --container $CONTAINER `
    --region $REGION `
    --interactive `
    --command $COMMAND
} else {
  Write-Host "⚠️  SQL file not found at: $SQL_PATH" -ForegroundColor Yellow
  Write-Host "Checking if file exists in container..." -ForegroundColor Yellow
  
  # Try to execute SQL file if it exists in container
  aws ecs execute-command `
    --cluster $CLUSTER `
    --task $TASK_ARN `
    --container $CONTAINER `
    --region $REGION `
    --interactive `
    --command "sh -c 'if [ -f `/app/$SQL_FILE` ]; then export PGPASSWORD=`"$DB_PASSWORD`" && psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f /app/$SQL_FILE; else echo `"SQL file not found in container`"; fi'"
}

Write-Host ""
Write-Host "✅ SQL upload completed!" -ForegroundColor Green
Write-Host "🔍 Verifying prompts count..." -ForegroundColor Cyan
aws ecs execute-command `
  --cluster $CLUSTER `
  --task $TASK_ARN `
  --container $CONTAINER `
  --region $REGION `
  --interactive `
  --command "sh -c 'export PGPASSWORD=`"$DB_PASSWORD`" && psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c `"SELECT COUNT(*) as prompt_count FROM prompts;`"'"









