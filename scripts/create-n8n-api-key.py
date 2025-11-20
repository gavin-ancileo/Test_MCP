#!/usr/bin/env python3
"""
Create N8N API key directly in PostgreSQL database
"""

import psycopg2
import secrets
import os

# PostgreSQL connection from environment
PG_HOST = os.getenv('DB_HOST', 'aap-rds-new.cv2usk6ye3hm.ap-southeast-2.rds.amazonaws.com')
PG_PORT = os.getenv('DB_PORT', '5432')
PG_DATABASE = 'n8n'  # N8N database name
PG_USER = os.getenv('DB_USER', 'AncileoMaster')
PG_PASSWORD = os.getenv('DB_PASSWORD', 'AncileoAAP2025SecureDB#')

def create_api_key(api_key_value=None):
    """Create N8N API key in database"""
    
    # Use provided API key or generate new one
    if api_key_value:
        api_key = api_key_value
        print(f"Using provided API key: {api_key[:30]}...")
    else:
        # Generate secure random API key (40 chars)
        api_key = 'n8n_api_' + secrets.token_hex(16)
        print(f"Generated new API key: {api_key}")

    print(f"Generated API key: {api_key}")
    print(f"\nConnecting to PostgreSQL at {PG_HOST}...")

    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        database=PG_DATABASE,
        user=PG_USER,
        password=PG_PASSWORD
    )
    cursor = conn.cursor()

    # Check if api_key table exists
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name = 'api_key'
        )
    """)

    table_exists = cursor.fetchone()[0]

    if not table_exists:
        print("\nERROR: api_key table does not exist in N8N database")
        print("N8N may not be fully initialized yet")
        cursor.close()
        conn.close()
        return None

    # Get first user ID
    cursor.execute("SELECT id FROM \"user\" LIMIT 1")
    user_row = cursor.fetchone()

    if not user_row:
        print("\nERROR: No users found in N8N database")
        cursor.close()
        conn.close()
        return None

    user_id = user_row[0]
    print(f"OK: Found user ID: {user_id}")

    # Delete existing 'Agent API' key if exists (to avoid conflicts)
    cursor.execute("""
        DELETE FROM api_key WHERE label = 'Agent API'
    """)
    deleted = cursor.rowcount
    if deleted > 0:
        print(f"   Deleted {deleted} existing 'Agent API' key(s)")
    
    # Insert API key
    cursor.execute("""
        INSERT INTO api_key (label, api_key, user_id, created_at)
        VALUES (%s, %s, %s, NOW())
        RETURNING id
    """, ('Agent API', api_key, user_id))

    result = cursor.fetchone()
    conn.commit()

    if result:
        print(f"\nOK: API key created successfully!")
        print(f"   - ID: {result[0]}")
        print(f"   - Key: {api_key}")
    else:
        print(f"\nINFO: API key already exists or was not created")

    cursor.close()
    conn.close()

    return api_key


if __name__ == '__main__':
    import sys
    
    print("=" * 60)
    print("CREATE N8N API KEY")
    print("=" * 60)
    
    # Get API key from command line or use default
    api_key_value = None
    if len(sys.argv) > 1:
        api_key_value = sys.argv[1]
        print(f"\nUsing API key from command line: {api_key_value[:30]}...")
    else:
        print("\nNo API key provided, will generate new one")
        print("Usage: python create-n8n-api-key.py <api_key_value>")

    api_key = create_api_key(api_key_value)

    if api_key:
        print(f"\n>>> API Key: {api_key}")
        print("\nNext steps:")
        print("1. Ensure this key is in AWS Secrets Manager AAP/prod/agentcore as N8N_API_KEY")
        print("2. Restart Agent API service if needed")
