#!/usr/bin/env python3
"""
Initialize AAP Database Schema
Run this script to create the required database tables for user management and prompts
"""

import psycopg2
import json

# Database credentials (from AWS Secrets Manager: AAP/uat/mcp-server)
DB_CONFIG = {
    'host': 'aap-rds-new.cv2usk6ye3hm.ap-southeast-2.rds.amazonaws.com',
    'port': 5432,
    'database': 'prompts',
    'user': 'AncileoMaster',
    'password': 'AncileoAAP2025SecureDB#'
}

SCHEMA_SQL = """
-- AAP Database Schema (matches app.py requirements)
BEGIN;

-- Users table (matches app.py user_login requirements)
CREATE TABLE IF NOT EXISTS users (
    email VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    roles TEXT NOT NULL DEFAULT '["ALL"]',  -- JSON array as text
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Prompts table
CREATE TABLE IF NOT EXISTS prompts (
    id SERIAL PRIMARY KEY,
    code VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- OAuth integrations table
CREATE TABLE IF NOT EXISTS integrations (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    provider VARCHAR(50) NOT NULL,  -- github, jira, drive
    provider_user_email VARCHAR(255),
    provider_user_id VARCHAR(255),
    access_token TEXT,
    refresh_token TEXT,
    scope TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(user_email, provider)
);

-- OAuth state tracking table
CREATE TABLE IF NOT EXISTS oauth_states (
    state VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255),
    user_email VARCHAR(255) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL
);

-- Insert default admin user (gavin.pham@ancileo.com)
INSERT INTO users (email, name, roles, is_admin)
VALUES ('gavin.pham@ancileo.com', 'Gavin Pham', '["ALL"]', TRUE)
ON CONFLICT (email) DO UPDATE
SET is_admin = TRUE, roles = '["ALL"]';

-- Insert other default users
INSERT INTO users (email, name, roles, is_admin)
VALUES
    ('admin@company.com', 'System Admin', '["admin"]', TRUE),
    ('hr@company.com', 'HR Manager', '["hr"]', FALSE),
    ('dev@company.com', 'Developer', '["dev"]', FALSE)
ON CONFLICT (email) DO NOTHING;

COMMIT;
"""

def main():
    print("🔧 Connecting to database...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print(f"✅ Connected to {DB_CONFIG['database']} at {DB_CONFIG['host']}")

        cur = conn.cursor()

        print("\n🔧 Creating database schema...")
        cur.execute(SCHEMA_SQL)
        conn.commit()

        print("\n✅ Schema created successfully!")

        # Verify tables
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cur.fetchall()]
        print(f"\n📊 Created {len(tables)} tables:")
        for table in tables:
            print(f"   - {table}")

        # Verify users
        cur.execute('SELECT email, name, is_admin FROM users ORDER BY is_admin DESC, email')
        users = cur.fetchall()
        print(f"\n👥 Created {len(users)} users:")
        for email, name, is_admin in users:
            role = "admin" if is_admin else "user"
            print(f"   - {email}: {name} ({role})")

        cur.close()
        conn.close()

        print("\n🎉 Database initialized successfully!")
        print("\n✅ You can now login with: gavin.pham@ancileo.com")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
