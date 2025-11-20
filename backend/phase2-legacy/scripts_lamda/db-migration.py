# Sửa lại code aap-api - BỎ SECRETS MANAGER
import json
import pg8000
import os
from datetime import datetime

def lambda_handler(event, context):
    # Direct credentials - không dùng Secrets Manager
    DB_HOST = os.environ.get('DB_HOST')
    DB_USER = os.environ.get('DB_USER', 'dbadmin')
    DB_PASS = os.environ.get('DB_PASS')
    DB_NAME = os.environ.get('DB_NAME', 'aapdb')
    DB_PORT = int(os.environ.get('DB_PORT', 5432))
    
    # CORS headers
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
        'Access-Control-Allow-Headers': '*'
    }
    
    # Parse request
    method = event.get('requestContext', {}).get('http', {}).get('method', 'GET')
    path = event.get('rawPath', '/')
    
    if method == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': ''}
    
    try:
        # Direct connection - không cần boto3
        conn = pg8000.connect(
            host=DB_HOST, port=DB_PORT,
            database=DB_NAME, user=DB_USER, password=DB_PASS,
            timeout=10
        )
        cur = conn.cursor()
        
        # Routes (giữ nguyên logic cũ)
        if path == '/health':
            result = {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}
        
        elif path == '/api/prompts' and method == 'GET':
            cur.execute("""
                SELECT id, code, name, description, category
                FROM prompts WHERE is_active = TRUE
                ORDER BY created_at DESC
            """)
            columns = [d[0] for d in cur.description]
            prompts = [dict(zip(columns, row)) for row in cur.fetchall()]
            result = {'prompts': prompts}
        
        else:
            result = {'path': path, 'method': method}
        
        cur.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(result)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }