#!/bin/bash
set -e

# ============================================
# Create DynamoDB Tables for Chat Storage
# ============================================

ENVIRONMENT=${1:-uat}
REGION=${AWS_DEFAULT_REGION:-ap-southeast-2}
STACK_NAME="aap-chat-storage-${ENVIRONMENT}"

echo "============================================"
echo "Creating Chat Storage Tables"
echo "Environment: $ENVIRONMENT"
echo "Region: $REGION"
echo "Stack: $STACK_NAME"
echo "============================================"

# Deploy CloudFormation stack
aws cloudformation deploy \
  --template-file ../cloudformation/chat-storage-tables.yaml \
  --stack-name "$STACK_NAME" \
  --parameter-overrides Environment="$ENVIRONMENT" \
  --region "$REGION" \
  --no-fail-on-empty-changeset \
  --tags \
    Environment="$ENVIRONMENT" \
    Application=AAP \
    ManagedBy=CloudFormation

echo ""
echo "✅ Chat Storage Tables created successfully!"
echo ""

# Get table names
echo "📊 Table Names:"
aws cloudformation describe-stacks \
  --stack-name "$STACK_NAME" \
  --region "$REGION" \
  --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
  --output table

echo ""
echo "🔍 Verifying tables..."

# Verify each table
for table in \
  "aap-chat-sessions-${ENVIRONMENT}" \
  "aap-chat-messages-${ENVIRONMENT}" \
  "aap-chat-memory-${ENVIRONMENT}" \
  "aap-conversations-${ENVIRONMENT}"
do
  echo -n "  Checking $table... "
  STATUS=$(aws dynamodb describe-table \
    --table-name "$table" \
    --region "$REGION" \
    --query 'Table.TableStatus' \
    --output text 2>/dev/null || echo "NOT_FOUND")

  if [ "$STATUS" = "ACTIVE" ]; then
    echo "✅ ACTIVE"
  else
    echo "⚠️ $STATUS"
  fi
done

echo ""
echo "============================================"
echo "Setup Complete!"
echo "============================================"
echo ""
echo "Next steps:"
echo "1. Update .env with table names:"
echo "   DYNAMODB_SESSIONS_TABLE=aap-chat-sessions-${ENVIRONMENT}"
echo "   DYNAMODB_MESSAGES_TABLE=aap-chat-messages-${ENVIRONMENT}"
echo "   DYNAMODB_MEMORY_TABLE=aap-chat-memory-${ENVIRONMENT}"
echo ""
echo "2. Deploy updated backend with Bedrock Memory support"
echo ""
