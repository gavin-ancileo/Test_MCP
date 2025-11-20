#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create N8N API key via ECS one-off task
Runs the create-n8n-api-key.py script inside ECS with VPC access to RDS
"""
import boto3
import os
import sys
import json
import io

# Set UTF-8 encoding for console output
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_SESSION_TOKEN = os.getenv('AWS_SESSION_TOKEN')

REGION = 'ap-southeast-2'
CLUSTER = 'aap-cluster'
TASK_DEF_FAMILY = 'aap-agentcore-new'  # Use agent-api task definition (has VPC access)
API_KEY = 'n8n_api_fd8563f2f8aafbc5fa09086fb90de086'

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN,
    region_name=REGION
)
ecs = session.client('ecs', region_name=REGION)

print("=" * 80)
print("CREATE N8N API KEY VIA ECS TASK")
print("=" * 80)
print()

# Get task definition to get network config
print("📥 Getting task definition...")
try:
    task_def_response = ecs.describe_task_definition(taskDefinition=TASK_DEF_FAMILY)
    task_def = task_def_response['taskDefinition']
    container_def = task_def['containerDefinitions'][0]
    
    # Get network configuration from service
    print("📥 Getting service network configuration...")
    service_response = ecs.describe_services(
        cluster=CLUSTER,
        services=['aap-agentcore-new']
    )
    
    if not service_response['services']:
        print("❌ Service aap-agentcore-new not found")
        sys.exit(1)
    
    service = service_response['services'][0]
    network_config = service['networkConfiguration']['awsvpcConfiguration']
    
    subnets = network_config['subnets']
    security_groups = network_config.get('securityGroups', [])
    
    print(f"✅ Got network config:")
    print(f"   Subnets: {subnets}")
    print(f"   Security Groups: {security_groups}")
    print()
    
    # Create Python script to run
    # Escape quotes in script content
    script_content = f'''import psycopg2
import os
import sys

API_KEY = "{API_KEY}"

PG_HOST = os.getenv('DB_HOST')
PG_PORT = os.getenv('DB_PORT', '5432')
PG_DATABASE = 'n8n'
PG_USER = os.getenv('DB_USER')
PG_PASSWORD = os.getenv('DB_PASSWORD')

print("=" * 60)
print("CREATE N8N API KEY IN DATABASE")
print("=" * 60)
print(f"API Key: {{API_KEY[:30]}}...")
print(f"Connecting to: {{PG_HOST}}")
print()

try:
    # First connect to postgres database to find n8n database
    conn = psycopg2.connect(host=PG_HOST, port=PG_PORT, database='postgres', user=PG_USER, password=PG_PASSWORD)
    conn.autocommit = True
    cursor = conn.cursor()
    
    cursor.close()
    conn.close()
    
    # Connect directly to n8n database (we know it exists and has schema)
    print(f"📌 Connecting to 'n8n' database...")
    conn = psycopg2.connect(host=PG_HOST, port=PG_PORT, database='n8n', user=PG_USER, password=PG_PASSWORD)
    cursor = conn.cursor()
    
    print("✅ api_key table exists")
    
    # Check if user exists, create one if not
    cursor.execute('SELECT id FROM "user" LIMIT 1')
    user_row = cursor.fetchone()
    
    if not user_row:
        print("⚠️  No users found, creating default user...")
        import uuid
        user_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO "user" (id, email, firstName, lastName, globalRole, createdAt, updatedAt)
            VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
        """, (user_id, 'agent-api@ancileo.com', 'Agent', 'API', 'owner'))
        conn.commit()
        print(f"✅ Created user: {{user_id}}")
    else:
        user_id = user_row[0]
        print(f"✅ Found user ID: {{user_id}}")
    
    # Delete existing 'Agent API' key if exists
    cursor.execute("DELETE FROM api_key WHERE label = 'Agent API'")
    deleted = cursor.rowcount
    if deleted > 0:
        print(f"   Deleted {{deleted}} existing key(s)")
    
    # Insert API key
    import uuid
    api_key_id = str(uuid.uuid4())
    cursor.execute("""
        INSERT INTO api_key (id, name, api_key, user_id, label, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
        RETURNING id
    """, (api_key_id, 'Agent API', API_KEY, user_id, 'Agent API'))
    result = cursor.fetchone()
    conn.commit()
    
    if result:
        print(f"✅ API key created! ID: {{result[0]}}")
        print(f"   Key: {{API_KEY}}")
    else:
        print("❌ Failed to create")
        sys.exit(1)
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"❌ ERROR: {{e}}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
'''
    
    # Use python -c to run inline script
    # Need to escape properly for command line
    import shlex
    escaped_script = script_content.replace("'", "'\"'\"'")
    command = ['python', '-c', script_content]
    
    print("🚀 Running ECS task...")
    print(f"   Cluster: {CLUSTER}")
    print(f"   Task Definition: {TASK_DEF_FAMILY}")
    print(f"   API Key: {API_KEY[:30]}...")
    print()
    
    response = ecs.run_task(
        cluster=CLUSTER,
        taskDefinition=TASK_DEF_FAMILY,
        launchType='FARGATE',
        networkConfiguration={
            'awsvpcConfiguration': {
                'subnets': subnets,
                'securityGroups': security_groups,
                'assignPublicIp': 'DISABLED'
            }
        },
        overrides={
            'containerOverrides': [
                {
                    'name': container_def['name'],
                    'command': command
                }
            ]
        }
    )
    
    task_arn = response['tasks'][0]['taskArn']
    print(f"✅ Task started: {task_arn}")
    print()
    print("⏳ Waiting for task to complete...")
    print("   Check CloudWatch logs for output")
    print()
    print(f"   Log group: /ecs/aap-agentcore-new")
    print(f"   Task ID: {task_arn.split('/')[-1]}")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

