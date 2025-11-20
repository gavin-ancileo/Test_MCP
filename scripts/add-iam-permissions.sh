#!/bin/bash
# Add EC2 and networking permissions to BedrockAPIKey-irl5 user
# Run this on AWS CloudShell with admin permissions

set -e

IAM_USER="BedrockAPIKey-irl5"
POLICY_NAME="AAP-Networking-Debug-Policy"

echo "🔧 Adding networking debug permissions to $IAM_USER..."

# Create inline policy with required permissions
aws iam put-user-policy \
  --user-name "$IAM_USER" \
  --policy-name "$POLICY_NAME" \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Sid": "EC2NetworkingReadAccess",
        "Effect": "Allow",
        "Action": [
          "ec2:DescribeVpcs",
          "ec2:DescribeVpcPeeringConnections",
          "ec2:DescribeRouteTables",
          "ec2:DescribeSecurityGroups",
          "ec2:DescribeSecurityGroupRules",
          "ec2:DescribeSubnets",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DescribeNatGateways",
          "ec2:DescribeInternetGateways"
        ],
        "Resource": "*"
      },
      {
        "Sid": "ECSFullAccess",
        "Effect": "Allow",
        "Action": [
          "ecs:*"
        ],
        "Resource": "*"
      },
      {
        "Sid": "CloudWatchLogsAccess",
        "Effect": "Allow",
        "Action": [
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams",
          "logs:FilterLogEvents",
          "logs:GetLogEvents"
        ],
        "Resource": "*"
      },
      {
        "Sid": "SecretsManagerReadAccess",
        "Effect": "Allow",
        "Action": [
          "secretsmanager:ListSecrets",
          "secretsmanager:DescribeSecret",
          "secretsmanager:GetSecretValue"
        ],
        "Resource": "*"
      },
      {
        "Sid": "CloudFormationReadAccess",
        "Effect": "Allow",
        "Action": [
          "cloudformation:DescribeStacks",
          "cloudformation:DescribeStackResources",
          "cloudformation:ListStacks"
        ],
        "Resource": "*"
      },
      {
        "Sid": "ELBReadAccess",
        "Effect": "Allow",
        "Action": [
          "elasticloadbalancing:DescribeLoadBalancers",
          "elasticloadbalancing:DescribeTargetGroups",
          "elasticloadbalancing:DescribeTargetHealth",
          "elasticloadbalancing:DescribeListeners",
          "elasticloadbalancing:DescribeRules"
        ],
        "Resource": "*"
      }
    ]
  }'

echo "✅ Policy '$POLICY_NAME' has been attached to user '$IAM_USER'"
echo ""
echo "Permissions granted:"
echo "  - EC2 VPC, Peering, Routes, Security Groups (Read-only)"
echo "  - ECS (Full access for task management)"
echo "  - CloudWatch Logs (Read access)"
echo "  - Secrets Manager (Read access)"
echo "  - CloudFormation (Read access)"
echo "  - ELB/ALB (Read access)"
echo ""
echo "🔄 Note: Changes may take a few seconds to propagate"
echo "💡 You can now run debug-database-peering.sh script"
