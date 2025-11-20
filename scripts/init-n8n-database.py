#!/usr/bin/env python3
"""
Initialize N8N Database Schema
Creates essential tables for n8n to work: user, api_key, workflow_entity, etc.
"""
import psycopg2
import os
import sys

# Database credentials from environment (ECS injects from Secrets Manager)
PG_HOST = os.getenv('DB_HOST')
PG_PORT = os.getenv('DB_PORT', '5432')
PG_DATABASE = 'n8n'
PG_USER = os.getenv('DB_USER')
PG_PASSWORD = os.getenv('DB_PASSWORD')

print("=" * 80)
print("INITIALIZE N8N DATABASE SCHEMA")
print("=" * 80)
print()

if not all([PG_HOST, PG_USER, PG_PASSWORD]):
    print("❌ Missing database credentials")
    print("   Required: DB_HOST, DB_USER, DB_PASSWORD")
    sys.exit(1)

print(f"📋 Configuration:")
print(f"   Host: {PG_HOST}")
print(f"   Port: {PG_PORT}")
print(f"   Database: {PG_DATABASE}")
print(f"   User: {PG_USER}")
print()

# N8N Database Schema
# Based on n8n's actual schema structure
SCHEMA_SQL = """
-- N8N Database Schema
-- Creates essential tables for n8n workflow automation

BEGIN;

-- User table (required for API keys and workflows)
CREATE TABLE IF NOT EXISTS "user" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    firstName VARCHAR(255),
    lastName VARCHAR(255),
    password VARCHAR(255),
    globalRole VARCHAR(50) DEFAULT 'member',
    apiKey VARCHAR(255),
    createdAt TIMESTAMP DEFAULT NOW(),
    updatedAt TIMESTAMP DEFAULT NOW()
);

-- API Key table (for API authentication)
CREATE TABLE IF NOT EXISTS api_key (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    api_key VARCHAR(255) UNIQUE NOT NULL,
    user_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    label VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Workflow Entity table (stores workflows)
CREATE TABLE IF NOT EXISTS workflow_entity (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    active BOOLEAN DEFAULT FALSE,
    nodes JSONB,
    connections JSONB,
    settings JSONB,
    staticData JSONB,
    tags JSONB,
    pinData JSONB,
    versionId VARCHAR(255),
    createdAt TIMESTAMP DEFAULT NOW(),
    updatedAt TIMESTAMP DEFAULT NOW()
);

-- Credentials Entity table (stores credentials)
CREATE TABLE IF NOT EXISTS credentials_entity (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(255) NOT NULL,
    data TEXT,  -- Encrypted credentials
    nodesAccess JSONB,
    createdAt TIMESTAMP DEFAULT NOW(),
    updatedAt TIMESTAMP DEFAULT NOW()
);

-- Execution Entity table (stores workflow executions)
CREATE TABLE IF NOT EXISTS execution_entity (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflowId UUID REFERENCES workflow_entity(id) ON DELETE CASCADE,
    finished BOOLEAN DEFAULT FALSE,
    mode VARCHAR(50),
    retryOf UUID,
    retrySuccessId UUID,
    startedAt TIMESTAMP,
    stoppedAt TIMESTAMP,
    waitTill TIMESTAMP,
    data JSONB,
    workflowData JSONB,
    createdAt TIMESTAMP DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_api_key_api_key ON api_key(api_key);
CREATE INDEX IF NOT EXISTS idx_api_key_user_id ON api_key(user_id);
CREATE INDEX IF NOT EXISTS idx_workflow_entity_active ON workflow_entity(active);
CREATE INDEX IF NOT EXISTS idx_execution_entity_workflow_id ON execution_entity(workflowId);
CREATE INDEX IF NOT EXISTS idx_execution_entity_finished ON execution_entity(finished);

COMMIT;
"""

def main():
    print("🔌 Connecting to PostgreSQL...")
    try:
        # First connect to postgres to ensure n8n database exists
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            database='postgres',
            user=PG_USER,
            password=PG_PASSWORD
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if n8n database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (PG_DATABASE,))
        if not cursor.fetchone():
            print(f"📦 Creating database '{PG_DATABASE}'...")
            cursor.execute(f'CREATE DATABASE "{PG_DATABASE}"')
            print(f"✅ Database '{PG_DATABASE}' created")
        else:
            print(f"✅ Database '{PG_DATABASE}' already exists")
        
        cursor.close()
        conn.close()
        
        # Now connect to n8n database
        print(f"🔌 Connecting to '{PG_DATABASE}' database...")
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            database=PG_DATABASE,
            user=PG_USER,
            password=PG_PASSWORD
        )
        cursor = conn.cursor()
        
        # Check existing tables
        cursor.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' 
            ORDER BY tablename
        """)
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        if existing_tables:
            print(f"📋 Found {len(existing_tables)} existing tables:")
            for table in existing_tables:
                print(f"   - {table}")
            print()
        
        # Create schema
        print("🔧 Creating N8N schema...")
        cursor.execute(SCHEMA_SQL)
        conn.commit()
        print("✅ Schema created successfully!")
        print()
        
        # Verify tables were created
        cursor.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' 
            ORDER BY tablename
        """)
        all_tables = [row[0] for row in cursor.fetchall()]
        
        print(f"📋 Database now has {len(all_tables)} tables:")
        for table in all_tables:
            print(f"   ✅ {table}")
        
        # Check if user table has any users
        cursor.execute('SELECT COUNT(*) FROM "user"')
        user_count = cursor.fetchone()[0]
        print()
        print(f"👤 Users in database: {user_count}")
        
        if user_count == 0:
            print("⚠️  No users found. N8N needs at least one user to work.")
            print("   You may need to create a user through n8n UI or API.")
        
        cursor.close()
        conn.close()
        
        print()
        print("=" * 80)
        print("✅ N8N DATABASE SCHEMA INITIALIZED SUCCESSFULLY")
        print("=" * 80)
        print()
        print("Next steps:")
        print("1. Create a user in the 'user' table (or let n8n create it on first login)")
        print("2. Create API key in 'api_key' table")
        print("3. Restart n8n service if needed")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

