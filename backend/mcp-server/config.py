"""
Configuration management for MCP Server
Loads configuration from AWS Secrets Manager or environment variables
"""

import os
import json
from typing import Dict

def load_config() -> Dict:
    """
    Load configuration from environment variables (ECS secrets injection).

    In ECS, Secrets Manager values are injected as individual environment variables.
    Each key from the secret becomes an env var (e.g., DB_HOST, INSURANCE_DB_HOST, etc.)

    Priority:
    1. Environment variables (from ECS secrets or local docker-compose)
    2. Default values (fallback)

    Returns:
        Dict: Configuration dictionary with database and service settings
    """
    # Load all config from environment variables
    # ECS injects secrets as individual env vars
    print("Loading configuration from environment variables")
    config = {
        # Main AAP database
        'DB_HOST': os.getenv('DB_HOST', 'postgres'),
        'DB_PORT': os.getenv('DB_PORT', '5432'),
        'DB_NAME': os.getenv('DB_NAME', 'aap_db'),
        'DB_USER': os.getenv('DB_USER', 'postgres'),
        'DB_PASSWORD': os.getenv('DB_PASSWORD', 'postgres123'),

        # Insurance database (cross-region)
        'INSURANCE_DB_HOST': os.getenv('INSURANCE_DB_HOST'),
        'INSURANCE_DB_PORT': os.getenv('INSURANCE_DB_PORT', '3306'),
        'INSURANCE_DB_NAME': os.getenv('INSURANCE_DB_NAME', 'insurance'),
        'INSURANCE_DB_USER': os.getenv('INSURANCE_DB_USER'),
        'INSURANCE_DB_PASSWORD': os.getenv('INSURANCE_DB_PASSWORD'),

        # ClaimHub database (cross-region)
        'CLAIMHUB_DB_HOST': os.getenv('CLAIMHUB_DB_HOST'),
        'CLAIMHUB_DB_PORT': os.getenv('CLAIMHUB_DB_PORT', '5432'),
        'CLAIMHUB_DB_NAME': os.getenv('CLAIMHUB_DB_NAME', 'assessment'),
        'CLAIMHUB_DB_USER': os.getenv('CLAIMHUB_DB_USER'),
        'CLAIMHUB_DB_PASSWORD': os.getenv('CLAIMHUB_DB_PASSWORD'),

        # OAuth credentials
        'GITHUB_CLIENT_ID': os.getenv('GITHUB_CLIENT_ID'),
        'GITHUB_CLIENT_SECRET': os.getenv('GITHUB_CLIENT_SECRET'),
        'JIRA_CLIENT_ID': os.getenv('JIRA_CLIENT_ID'),
        'JIRA_CLIENT_SECRET': os.getenv('JIRA_CLIENT_SECRET'),
        'GOOGLE_CLIENT_ID': os.getenv('GOOGLE_CLIENT_ID'),
        'GOOGLE_CLIENT_SECRET': os.getenv('GOOGLE_CLIENT_SECRET'),

        # Services
        'N8N_URL': os.getenv('N8N_URL', 'http://localhost:5678'),
        'AWS_REGION': os.getenv('AWS_REGION', 'ap-southeast-2')
    }

    return config

# Load configuration on module import
CONFIG = load_config()
print(f"✅ Config loaded - Main DB: {CONFIG.get('DB_HOST')}, Insurance DB: {CONFIG.get('INSURANCE_DB_HOST')}, ClaimHub DB: {CONFIG.get('CLAIMHUB_DB_HOST')}")

