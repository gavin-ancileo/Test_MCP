#!/bin/bash
# Debug database peering connectivity issues
# Run this on AWS CloudShell with proper IAM permissions

set -e

REGION="ap-southeast-2"
AAP_VPC_ID="vpc-0d0773dfba7b2b85d"  # From previous output
AAP_VPC_CIDR="172.16.0.0/16"

echo "========================================"
echo "DATABASE PEERING CONNECTIVITY DEBUG"
echo "========================================"
echo ""

# 1. Check VPC Peering Connections
echo "1️⃣ Checking VPC Peering Connections..."
echo "----------------------------------------"
aws ec2 describe-vpc-peering-connections \
  --region $REGION \
  --filters "Name=requester-vpc-info.vpc-id,Values=$AAP_VPC_ID" \
  --query 'VpcPeeringConnections[*].[VpcPeeringConnectionId,Status.Code,RequesterVpcInfo.CidrBlock,AccepterVpcInfo.CidrBlock,Tags[?Key==`Name`].Value|[0]]' \
  --output table || echo "⚠️ No VPC peering connections found OR permission denied"

echo ""

# 2. Check Route Tables
echo "2️⃣ Checking Route Tables for AAP VPC..."
echo "----------------------------------------"
aws ec2 describe-route-tables \
  --region $REGION \
  --filters "Name=vpc-id,Values=$AAP_VPC_ID" \
  --query 'RouteTables[*].{RouteTableId:RouteTableId,Routes:Routes[*].[DestinationCidrBlock,VpcPeeringConnectionId,State]}' \
  --output json | python3 -c "
import json, sys
data = json.load(sys.stdin)
for rt in data:
    print(f\"Route Table: {rt['RouteTableId']}\")
    for route in rt['Routes']:
        if route[1]:  # Has peering connection
            print(f\"  → {route[0]} via {route[1]} ({route[2]})\")
" || echo "⚠️ Could not read route tables"

echo ""

# 3. Check Security Groups for Agent API
echo "3️⃣ Checking Security Groups for Agent API..."
echo "----------------------------------------"
aws ec2 describe-security-groups \
  --region $REGION \
  --filters "Name=tag:Name,Values=*agentcore*" \
  --query 'SecurityGroups[*].{GroupId:GroupId,GroupName:GroupName,InboundRules:IpPermissions[*].[IpProtocol,FromPort,ToPort,IpRanges[*].CidrIp]}' \
  --output json | python3 -c "
import json, sys
data = json.load(sys.stdin)
for sg in data:
    print(f\"Security Group: {sg['GroupId']} ({sg['GroupName']})\")
    print(f\"  Inbound Rules:\")
    for rule in sg.get('InboundRules', []):
        protocol = rule[0] if rule[0] != '-1' else 'ALL'
        ports = f\"{rule[1]}-{rule[2]}\" if rule[1] else 'ALL'
        cidrs = rule[3] if rule[3] else ['N/A']
        for cidr in cidrs:
            print(f\"    - {protocol} port {ports} from {cidr}\")
" || echo "⚠️ Could not read security groups"

echo ""

# 4. Check if Secrets Manager has DB credentials
echo "4️⃣ Checking Secrets Manager for Database Credentials..."
echo "----------------------------------------"
echo "Checking for AAP/uat/insurance-db secret..."
aws secretsmanager get-secret-value \
  --region $REGION \
  --secret-id "AAP/uat/insurance-db" \
  --query '[SecretString]' \
  --output text 2>/dev/null && echo "✅ Insurance DB secret exists" || echo "❌ Insurance DB secret NOT FOUND"

echo ""
echo "Checking for AAP/uat/claimhub-db secret..."
aws secretsmanager get-secret-value \
  --region $REGION \
  --secret-id "AAP/uat/claimhub-db" \
  --query '[SecretString]' \
  --output text 2>/dev/null && echo "✅ ClaimHub DB secret exists" || echo "❌ ClaimHub DB secret NOT FOUND"

echo ""

# 5. Check CloudFormation Stack
echo "5️⃣ Checking VPC Peering CloudFormation Stack..."
echo "----------------------------------------"
aws cloudformation describe-stacks \
  --region $REGION \
  --query "Stacks[?contains(StackName, 'peering') || contains(StackName, 'vpc-13')].{StackName:StackName,Status:StackStatus,Created:CreationTime}" \
  --output table || echo "⚠️ No VPC peering stack found"

echo ""

# 6. Get Agent API Task Info
echo "6️⃣ Getting Agent API Task Details..."
echo "----------------------------------------"
TASK_ARN=$(aws ecs list-tasks \
  --region $REGION \
  --cluster aap-cluster \
  --service-name aap-agentcore-new \
  --query 'taskArns[0]' \
  --output text)

if [ "$TASK_ARN" != "None" ] && [ ! -z "$TASK_ARN" ]; then
    echo "Agent API Task: $TASK_ARN"

    # Get task network details
    aws ecs describe-tasks \
      --region $REGION \
      --cluster aap-cluster \
      --tasks $TASK_ARN \
      --query 'tasks[0].{SubnetId:attachments[0].details[?name==`subnetId`].value|[0],PrivateIP:attachments[0].details[?name==`privateIPv4Address`].value|[0]}' \
      --output table
else
    echo "⚠️ No running Agent API task found"
fi

echo ""
echo "========================================"
echo "DIAGNOSIS"
echo "========================================"
echo ""
echo "Common issues:"
echo "1. VPC Peering not created → Deploy cf-13-vpc-peering.yml"
echo "2. VPC Peering not accepted → Accept in peer account"
echo "3. Routes not configured → Add routes in peer VPC"
echo "4. Security groups blocking → Allow inbound from AAP VPC CIDR"
echo "5. Secrets not configured → Create AAP/uat/insurance-db secret"
echo ""
echo "Next steps:"
echo "- If peering exists but status != 'active': Accept peering in peer account"
echo "- If routes missing: Add routes in both VPCs"
echo "- If security groups missing rules: Add inbound rules for MySQL/PostgreSQL"
echo "- If secrets missing: Create secrets with DB credentials"
echo ""
