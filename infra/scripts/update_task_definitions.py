#!/usr/bin/env python3
"""
Script to update ECS task definitions with Secrets Manager integration
Removes hardcoded environment variables and injects secrets properly
"""
import json
import sys

def create_secret_ref(secret_name, key_name):
    """Create a Secrets Manager ARN reference for ECS"""
    return {
        "name": key_name,
        "valueFrom": f"arn:aws:secretsmanager:ap-southeast-2:233693675018:secret:{secret_name}:{key_name}::"
    }

def update_mcp_server_task_def(input_file, output_file):
    """Update MCP Server task definition to use Secrets Manager for all sensitive data"""

    with open(input_file, 'r') as f:
        task_def = json.load(f)

    # Extract the task definition (remove metadata)
    td = task_def['taskDefinition']
    container = td['containerDefinitions'][0]

    # Keys to move from environment to secrets
    sensitive_keys = [
        'DB_HOST', 'DB_PORT', 'DB_USER', 'DB_PASSWORD', 'DB_NAME',
        'GITHUB_CLIENT_ID', 'GITHUB_CLIENT_SECRET',
        'JIRA_CLIENT_ID', 'JIRA_CLIENT_SECRET',
        'GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET',
        'CLAIMHUB_DB_HOST', 'CLAIMHUB_DB_PORT', 'CLAIMHUB_DB_USER', 'CLAIMHUB_DB_PASSWORD', 'CLAIMHUB_DB_NAME',
        'INSURANCE_DB_HOST', 'INSURANCE_DB_PORT', 'INSURANCE_DB_USER', 'INSURANCE_DB_PASSWORD', 'INSURANCE_DB_NAME',
        'N8N_URL'
    ]

    # Keep only non-sensitive environment variables
    new_environment = [
        {"name": "AWS_REGION", "value": "ap-southeast-2"},
        {"name": "ENVIRONMENT", "value": "prod"}
    ]

    # Create secrets array with all sensitive keys
    secrets = [create_secret_ref("AAP/prod/mcp-server-z56uEi", key) for key in sensitive_keys]

    # Update container definition
    container['environment'] = new_environment
    container['secrets'] = secrets

    # Clean up task definition for registration
    clean_td = {
        "family": td['family'],
        "taskRoleArn": td.get('taskRoleArn'),
        "executionRoleArn": td['executionRoleArn'],
        "networkMode": td['networkMode'],
        "containerDefinitions": [container],
        "requiresCompatibilities": td['requiresCompatibilities'],
        "cpu": td['cpu'],
        "memory": td['memory']
    }

    # Remove None values
    clean_td = {k: v for k, v in clean_td.items() if v is not None}

    with open(output_file, 'w') as f:
        json.dump(clean_td, f, indent=2)

    print(f"[OK] MCP Server task definition updated:")
    print(f"   - {len(secrets)} secrets injected from Secrets Manager")
    print(f"   - {len(new_environment)} non-sensitive environment variables retained")
    print(f"   - Output: {output_file}")

def update_agentcore_task_def(input_file, output_file):
    """Update AgentCore task definition to use PROD secrets"""

    with open(input_file, 'r') as f:
        task_def = json.load(f)

    td = task_def['taskDefinition']
    container = td['containerDefinitions'][0]

    # ALL secrets that should come from Secrets Manager
    all_secret_keys = [
        'GITHUB_CLIENT_ID', 'GITHUB_CLIENT_SECRET',
        'JIRA_CLIENT_ID', 'JIRA_CLIENT_SECRET',
        'GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET',
        'OPENAI_API_KEY',
        'DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD',
        'COGNITO_REGION', 'COGNITO_USER_POOL_ID',
        'DYNAMODB_TABLE', 'MCP_URL', 'COGNITO_DOMAIN',
        'GITHUB_REDIRECT_URI', 'JIRA_REDIRECT_URI', 'GOOGLE_REDIRECT_URI',
        'N8N_API_KEY'
    ]

    # Replace ALL secrets with PROD references
    container['secrets'] = [create_secret_ref("AAP/prod/agentcore-AH5fwm", key) for key in all_secret_keys]

    # Clean up for registration
    clean_td = {
        "family": td['family'],
        "taskRoleArn": td.get('taskRoleArn'),
        "executionRoleArn": td['executionRoleArn'],
        "networkMode": td['networkMode'],
        "containerDefinitions": [container],
        "requiresCompatibilities": td['requiresCompatibilities'],
        "cpu": td['cpu'],
        "memory": td['memory']
    }

    clean_td = {k: v for k, v in clean_td.items() if v is not None}

    with open(output_file, 'w') as f:
        json.dump(clean_td, f, indent=2)

    print(f"[OK] AgentCore task definition updated:")
    print(f"   - {len(all_secret_keys)} secrets injected from Secrets Manager (PROD)")
    print(f"   - Output: {output_file}")

if __name__ == "__main__":
    print("=== Updating ECS Task Definitions ===\n")

    # Update MCP Server
    update_mcp_server_task_def(
        "infra/ecs-task-definitions/mcp-server-task-def-backup.json",
        "infra/ecs-task-definitions/mcp-server-task-def-new.json"
    )

    print()

    # Update AgentCore
    update_agentcore_task_def(
        "infra/ecs-task-definitions/agentcore-task-def-backup.json",
        "infra/ecs-task-definitions/agentcore-task-def-new.json"
    )

    print("\n=== Next Steps ===")
    print("1. Review generated task definitions in infra/ecs-task-definitions/")
    print("2. Register with: aws ecs register-task-definition --cli-input-json file://...")
    print("3. Update services: aws ecs update-service --task-definition ...")
