"""
Configuration management for Agent API
Loads configuration from AWS Secrets Manager or environment variables
"""

import os
import json
import boto3
from typing import Dict

def load_config() -> Dict:
    """
    Load configuration from Secrets Manager or environment variables.
    
    Priority:
    1. AWS Secrets Manager (production/uat)
    2. Environment variables (local development)
    
    Returns:
        Dict: Configuration dictionary with all settings
    """
    try:
        # Get environment from ENV var (default to uat for safety)
        environment = os.getenv('ENVIRONMENT', 'uat')
        secret_name = f'AAP/{environment}/agentcore'
        print(f"[Config] Loading configuration from Secrets Manager: {secret_name}")
        client = boto3.client('secretsmanager', region_name='ap-southeast-2')
        response = client.get_secret_value(SecretId=secret_name)
        config = json.loads(response['SecretString'])
        
        # Log important configuration values (without sensitive data)
        cognito_pool_id = config.get('COGNITO_USER_POOL_ID', 'Not configured')
        cognito_region = config.get('COGNITO_REGION', 'Not configured')
        print(f"[Config] Successfully loaded from Secrets Manager")
        print(f"[Config] COGNITO_USER_POOL_ID: {cognito_pool_id}")
        print(f"[Config] COGNITO_REGION: {cognito_region}")
        print(f"[Config] DYNAMODB_TABLE: {config.get('DYNAMODB_TABLE', 'Not configured')}")
        
        return config
    except Exception as e:
        print(f"WARNING: Could not load from Secrets Manager: {e}")
        print(f"[Config] Falling back to environment variables")
        fallback_config = {
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', ''),
            'OPENAI_MODEL': os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
            'USE_OPENAI': os.getenv('USE_OPENAI', 'true').lower() == 'true',
            'COGNITO_USER_POOL_ID': os.getenv('COGNITO_USER_POOL_ID', ''),
            'COGNITO_REGION': os.getenv('COGNITO_REGION', 'ap-southeast-2'),
            'DYNAMODB_TABLE': os.getenv('DYNAMODB_TABLE', 'aap-conversations-prod')
        }
        print(f"[Config] COGNITO_USER_POOL_ID (from ENV): {fallback_config.get('COGNITO_USER_POOL_ID', 'Not configured')}")
        return fallback_config

# Load configuration on module import
CONFIG = load_config()

# Inject CONFIG secrets into os.environ for oauth_integrations module
for key, value in CONFIG.items():
    if isinstance(value, str):
        os.environ[key] = value
    elif isinstance(value, bool):
        os.environ[key] = str(value).lower()
    elif value is not None:
        os.environ[key] = str(value)

print(f"OK: Loaded {len(CONFIG)} config values from Secrets Manager")

# AWS Clients
try:
    cognito = boto3.client('cognito-idp', region_name=CONFIG.get('COGNITO_REGION'))
except:
    cognito = None

# DynamoDB
try:
    dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-2')
    conversations_table = dynamodb.Table(CONFIG.get('DYNAMODB_TABLE', 'aap-conversations-prod'))
    print(f"OK: DynamoDB table connected: {CONFIG.get('DYNAMODB_TABLE')}")
except Exception as e:
    print(f"WARNING: DynamoDB connection failed: {e}")
    conversations_table = None

# OpenAI
import openai
if CONFIG.get('OPENAI_API_KEY'):
    openai.api_key = CONFIG['OPENAI_API_KEY']
    print("OK: OpenAI client initialized")
else:
    print("WARNING: No OpenAI API key found")

# MCP Server URL - Use service discovery for internal communication
# Priority: Secrets Manager > Environment Variable > Default
# Local Docker: http://mcp-server:8001
# ECS Production: http://mcp-server.aap.local:8001 (service discovery)
MCP_URL = CONFIG.get('MCP_URL') or os.getenv('MCP_URL', 'http://mcp-server.aap.local:8001')
print(f"[MCP] ========================================")
print(f"[MCP] Server URL: {MCP_URL}")
print(f"[MCP] Environment: {os.getenv('ENVIRONMENT', 'local')}")
print(f"[MCP] ========================================")

# N8N Server URL - Direct connection (separate from Company MCPs)
# Priority: Secrets Manager > Environment Variable > Default
N8N_URL = CONFIG.get('N8N_URL') or os.getenv('N8N_URL', 'http://aap-n8n.aap.local:5678')
print(f"[N8N] Server URL: {N8N_URL}")

