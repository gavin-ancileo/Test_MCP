#!/usr/bin/env python3
"""
Deploy Cognito User Pool CloudFormation stack with OAuth credentials from Secrets Manager

This script:
1. Fetches OAuth credentials from AWS Secrets Manager
2. Deploys CloudFormation stack with those credentials as parameters

Usage:
    python scripts/deploy-cognito-with-secrets.py --environment prod
"""

import boto3
import json
import sys
import argparse
import subprocess

def get_secret(secret_name: str, region: str = 'ap-southeast-2') -> dict:
    """Get secret from AWS Secrets Manager"""
    client = boto3.client('secretsmanager', region_name=region)
    try:
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response['SecretString'])
    except Exception as e:
        print(f"❌ Error getting secret {secret_name}: {e}")
        sys.exit(1)

def get_oauth_credentials(environment: str) -> dict:
    """Get OAuth credentials from Secrets Manager"""
    secret_name = f'AAP/{environment}/mcp-server'
    print(f"📥 Fetching OAuth credentials from {secret_name}...")
    
    secret = get_secret(secret_name)
    
    credentials = {
        'GOOGLE_CLIENT_ID': secret.get('GOOGLE_CLIENT_ID', ''),
        'GOOGLE_CLIENT_SECRET': secret.get('GOOGLE_CLIENT_SECRET', ''),
        'GITHUB_CLIENT_ID': secret.get('GITHUB_CLIENT_ID', ''),
        'GITHUB_CLIENT_SECRET': secret.get('GITHUB_CLIENT_SECRET', ''),
    }
    
    # Validate
    missing = [k for k, v in credentials.items() if not v]
    if missing:
        print(f"❌ Missing credentials in secret: {', '.join(missing)}")
        sys.exit(1)
    
    print("✅ OAuth credentials retrieved from Secrets Manager")
    return credentials

def deploy_stack(environment: str, credentials: dict, stack_name: str = None):
    """Deploy CloudFormation stack with OAuth credentials"""
    if not stack_name:
        stack_name = f'aap-{environment}-cognito-userpool'
    
    template_file = 'infra/cloudformation/cf-11-cognito-userpool.yaml'
    
    # Build CloudFormation deploy command
    cmd = [
        'aws', 'cloudformation', 'deploy',
        '--template-file', template_file,
        '--stack-name', stack_name,
        '--parameter-overrides',
        f'Environment={environment}',
        f'GoogleClientId={credentials["GOOGLE_CLIENT_ID"]}',
        f'GoogleClientSecret={credentials["GOOGLE_CLIENT_SECRET"]}',
        f'GitHubClientId={credentials["GITHUB_CLIENT_ID"]}',
        f'GitHubClientSecret={credentials["GITHUB_CLIENT_SECRET"]}',
        '--capabilities', 'CAPABILITY_IAM',
        '--region', 'ap-southeast-2'
    ]
    
    print(f"\n🚀 Deploying CloudFormation stack: {stack_name}")
    print(f"   Environment: {environment}")
    print(f"   Template: {template_file}")
    print()
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        print("\n✅ Stack deployed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed:")
        print(e.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description='Deploy Cognito User Pool with OAuth credentials from Secrets Manager'
    )
    parser.add_argument(
        '--environment',
        type=str,
        required=True,
        choices=['dev', 'uat', 'prod'],
        help='Environment (dev/uat/prod)'
    )
    parser.add_argument(
        '--stack-name',
        type=str,
        help='CloudFormation stack name (default: aap-{environment}-cognito-userpool)'
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("Cognito User Pool Deployment with Secrets Manager Integration")
    print("=" * 70)
    print()
    
    # Get OAuth credentials from Secrets Manager
    credentials = get_oauth_credentials(args.environment)
    
    # Deploy stack
    deploy_stack(args.environment, credentials, args.stack_name)
    
    print("\n" + "=" * 70)
    print("✅ Deployment complete!")
    print("=" * 70)

if __name__ == '__main__':
    main()

