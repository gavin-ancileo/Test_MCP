#!/usr/bin/env python3
"""
Upload 40-prompts-rich.sql to database via ECS task
This script executes SQL file through ECS task using AWS Systems Manager
"""

import boto3
import json
import subprocess
import sys
import os

# AWS Configuration
CLUSTER = "aap-cluster"
SERVICE = "aap-mcp-server-new"
CONTAINER = "mcp-server"
REGION = "ap-southeast-2"
SQL_FILE = "backend/mcp-server/40-prompts-rich.sql"

def get_secret():
    """Get database credentials from Secrets Manager"""
    try:
        client = boto3.client('secretsmanager', region_name=REGION)
        response = client.get_secret_value(SecretId='AAP/uat/mcp-server')
        return json.loads(response['SecretString'])
    except Exception as e:
        print(f"❌ Error getting secret: {e}")
        sys.exit(1)

def get_task_arn():
    """Get running ECS task ARN"""
    try:
        ecs = boto3.client('ecs', region_name=REGION)
        response = ecs.list_tasks(
            cluster=CLUSTER,
            serviceName=SERVICE,
            desiredStatus='RUNNING'
        )
        if not response['taskArns']:
            print("❌ No running task found")
            sys.exit(1)
        return response['taskArns'][0]
    except Exception as e:
        print(f"❌ Error getting task ARN: {e}")
        sys.exit(1)

def read_sql_file():
    """Read SQL file content"""
    if not os.path.exists(SQL_FILE):
        print(f"❌ SQL file not found: {SQL_FILE}")
        sys.exit(1)
    
    with open(SQL_FILE, 'r', encoding='utf-8') as f:
        return f.read()

def execute_sql_via_ecs(task_arn, sql_content, db_config):
    """Execute SQL via ECS execute-command"""
    db_password = db_config['DB_PASSWORD']
    db_host = db_config['DB_HOST']
    db_port = db_config['DB_PORT']
    db_user = db_config['DB_USER']
    db_name = db_config['DB_NAME']
    
    # Write SQL to temporary file in container and execute
    # Using psql with stdin to avoid command line length limits
    command = f"""sh -c 'export PGPASSWORD="{db_password}" && psql -h {db_host} -p {db_port} -U {db_user} -d {db_name} << EOF
{sql_content}
EOF'"""
    
    print("🚀 Executing SQL via ECS task...")
    print(f"   Task: {task_arn}")
    print(f"   Database: {db_host}:{db_port}/{db_name}")
    print("")
    
    try:
        # Use AWS CLI to execute command
        result = subprocess.run([
            'aws', 'ecs', 'execute-command',
            '--cluster', CLUSTER,
            '--task', task_arn,
            '--container', CONTAINER,
            '--region', REGION,
            '--interactive',
            '--command', command
        ], input=command.encode(), check=True)
        
        print("✅ SQL executed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error executing SQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    print("🔍 Getting database credentials...")
    db_config = get_secret()
    
    print("🔍 Getting running ECS task...")
    task_arn = get_task_arn()
    print(f"✅ Found task: {task_arn}")
    print("")
    
    print("📄 Reading SQL file...")
    sql_content = read_sql_file()
    print(f"✅ SQL file loaded ({len(sql_content)} characters)")
    print("")
    
    # Execute SQL
    if execute_sql_via_ecs(task_arn, sql_content, db_config):
        print("")
        print("🔍 Verifying prompts count...")
        # Verify count
        verify_command = f'sh -c \'export PGPASSWORD="{db_config["DB_PASSWORD"]}" && psql -h {db_config["DB_HOST"]} -p {db_config["DB_PORT"]} -U {db_config["DB_USER"]} -d {db_config["DB_NAME"]} -c "SELECT COUNT(*) as prompt_count FROM prompts;"\''
        
        subprocess.run([
            'aws', 'ecs', 'execute-command',
            '--cluster', CLUSTER,
            '--task', task_arn,
            '--container', CONTAINER,
            '--region', REGION,
            '--interactive',
            '--command', verify_command
        ])
    else:
        print("❌ Failed to execute SQL")
        sys.exit(1)

if __name__ == "__main__":
    main()









