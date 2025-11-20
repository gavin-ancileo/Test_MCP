#!/usr/bin/env python3
"""
Lambda function to seed 3 test prompts directly to database
"""
import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor

def lambda_handler(event, context):
    """Lambda handler to seed 3 test prompts"""
    
    # Get DB config from Secrets Manager or environment
    try:
        import boto3
        secrets_client = boto3.client('secretsmanager', region_name='ap-southeast-2')
        environment = os.getenv('ENVIRONMENT', 'uat')
        secret = secrets_client.get_secret_value(SecretId=f'AAP/{environment}/mcp-server')
        config = json.loads(secret['SecretString'])
        
        DB_HOST = config.get('DB_HOST')
        DB_PORT = config.get('DB_PORT', '5432')
        DB_NAME = config.get('DB_NAME', 'aap_db')
        DB_USER = config.get('DB_USER')
        DB_PASSWORD = config.get('DB_PASSWORD')
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': f'Failed to get DB credentials: {str(e)}'
            })
        }
    
    # 3 test prompts
    test_prompts = [
        ('test_1', 'Test Prompt 1', '["test"]', 'Test content 1 with {{variable1}}'),
        ('test_2', 'Test Prompt 2', '["test"]', 'Test content 2 with {{variable2}}'),
        ('test_3', 'Test Prompt 3', '["test"]', 'Test content 3 with {{variable3}}')
    ]
    
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=int(DB_PORT),
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            cursor_factory=RealDictCursor,
            connect_timeout=10
        )
        cur = conn.cursor()
        
        # Clear existing test prompts
        cur.execute("DELETE FROM prompts WHERE code LIKE 'test_%'")
        conn.commit()
        
        # Insert 3 test prompts
        for code, name, categories, content in test_prompts:
            cur.execute("""
                INSERT INTO prompts (code, name, categories, content)
                VALUES (%s, %s, %s, %s)
            """, (code, name, categories, content))
        
        conn.commit()
        
        # Verify
        cur.execute("SELECT COUNT(*) as count FROM prompts WHERE code LIKE 'test_%'")
        test_count = cur.fetchone()['count']
        
        cur.execute("SELECT COUNT(*) as count FROM prompts")
        total_count = cur.fetchone()[0]
        
        cur.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'message': f'Seeded {test_count} test prompts successfully',
                'test_count': int(test_count),
                'total_count': int(total_count)
            })
        }
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': str(e),
                'trace': error_trace
            })
        }

