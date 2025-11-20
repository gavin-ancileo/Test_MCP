#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run N8N database schema initialization via ECS task
"""
import boto3
import os
import sys
import io

# Set UTF-8 encoding for console output
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_SESSION_TOKEN = os.getenv('AWS_SESSION_TOKEN')

REGION = 'ap-southeast-2'
CLUSTER = 'aap-cluster'
TASK_DEF_FAMILY = 'aap-agentcore-new'

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SESSION_TOKEN,
    region_name=REGION
)
ecs = session.client('ecs', region_name=REGION)

print("=" * 80)
print("RUN N8N DATABASE SCHEMA INITIALIZATION VIA ECS")
print("=" * 80)
print()

# Get task definition and network config
print("📥 Getting task definition and network configuration...")
try:
    task_def_response = ecs.describe_task_definition(taskDefinition=TASK_DEF_FAMILY)
    task_def = task_def_response['taskDefinition']
    container_def = task_def['containerDefinitions'][0]
    
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
    
    # Read the init script
    script_path = os.path.join(os.path.dirname(__file__), 'init-n8n-database.py')
    if not os.path.exists(script_path):
        print(f"❌ Script not found: {script_path}")
        sys.exit(1)
    
    with open(script_path, 'r', encoding='utf-8') as f:
        script_content = f.read()
    
    # Create command to run the script
    # The script will be available in the container, or we can inline it
    command = ['python', '-c', script_content]
    
    print("🚀 Running ECS task to initialize n8n database schema...")
    print(f"   Cluster: {CLUSTER}")
    print(f"   Task Definition: {TASK_DEF_FAMILY}")
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
    task_id = task_arn.split('/')[-1]
    
    print(f"✅ Task started: {task_arn}")
    print()
    print("⏳ Waiting for task to complete...")
    print("   Check CloudWatch logs for output")
    print()
    print(f"   Log group: /ecs/aap-agentcore-new")
    print(f"   Task ID: {task_id}")
    print()
    print("   You can check logs with:")
    print(f"   python check_ecs_task_logs.py  # (update TASK_ID to {task_id})")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

