#!/usr/bin/env python3
"""
Apply migration 02-add-timestamps-to-prompts to production database
This script adds created_at and updated_at columns to the prompts table
"""

import os
import psycopg2
from psycopg2 import sql

# Database connection from environment variables
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'aap-rds-new.cv2usk6ye3hm.ap-southeast-2.rds.amazonaws.com'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'prompts'),
    'user': os.getenv('DB_USER', 'AncileoMaster'),
    'password': os.getenv('DB_PASSWORD', 'AncileoAAP2025SecureDB#')
}

MIGRATION_SQL = """
-- Migration: 02-add-timestamps-to-prompts
-- Description: Add created_at and updated_at columns to existing prompts table

DO $$
BEGIN
    -- Add created_at column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'prompts' AND column_name = 'created_at'
    ) THEN
        ALTER TABLE prompts ADD COLUMN created_at TIMESTAMP DEFAULT NOW();
        RAISE NOTICE 'Added created_at column to prompts table';
    ELSE
        RAISE NOTICE 'created_at column already exists, skipping';
    END IF;

    -- Add updated_at column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'prompts' AND column_name = 'updated_at'
    ) THEN
        ALTER TABLE prompts ADD COLUMN updated_at TIMESTAMP DEFAULT NOW();
        RAISE NOTICE 'Added updated_at column to prompts table';
    ELSE
        RAISE NOTICE 'updated_at column already exists, skipping';
    END IF;

    -- Backfill existing rows with current timestamp
    UPDATE prompts
    SET created_at = COALESCE(created_at, NOW()),
        updated_at = COALESCE(updated_at, NOW())
    WHERE created_at IS NULL OR updated_at IS NULL;

    RAISE NOTICE 'Backfilled timestamps for existing rows';

    -- Create updated_at trigger function if it doesn't exist
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $func$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
    $func$ LANGUAGE plpgsql;

    RAISE NOTICE 'Created/updated trigger function update_updated_at_column()';

    -- Drop existing trigger if it exists (to avoid duplicate trigger error)
    DROP TRIGGER IF EXISTS update_prompts_updated_at ON prompts;

    -- Create trigger to auto-update updated_at on UPDATE
    CREATE TRIGGER update_prompts_updated_at
        BEFORE UPDATE ON prompts
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();

    RAISE NOTICE 'Created trigger update_prompts_updated_at';

    -- Create schema_migrations table if it doesn't exist
    CREATE TABLE IF NOT EXISTS schema_migrations (
        version VARCHAR(255) PRIMARY KEY,
        description TEXT,
        applied_at TIMESTAMP DEFAULT NOW()
    );

    -- Record this migration
    INSERT INTO schema_migrations (version, description)
    VALUES ('02-add-timestamps-to-prompts', 'Add created_at and updated_at columns to existing prompts table')
    ON CONFLICT (version) DO NOTHING;

    RAISE NOTICE 'Migration 02-add-timestamps-to-prompts completed successfully';
END $$;
"""

def main():
    print("🔄 Connecting to database...")
    print(f"   Host: {DB_CONFIG['host']}")
    print(f"   Database: {DB_CONFIG['database']}")
    print(f"   User: {DB_CONFIG['user']}")
    print()

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cur = conn.cursor()

        print("✅ Connected to database")
        print()
        print("🚀 Applying migration 02-add-timestamps-to-prompts...")
        print()

        # Execute migration
        cur.execute(MIGRATION_SQL)

        # Get all notices from the migration
        for notice in conn.notices:
            print(f"   {notice.strip()}")

        print()
        print("✅ Migration applied successfully!")
        print()

        # Verify the migration
        print("🔍 Verifying schema...")
        cur.execute("""
            SELECT column_name, data_type, column_default, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'prompts'
            ORDER BY ordinal_position;
        """)

        columns = cur.fetchall()
        print(f"   Prompts table has {len(columns)} columns:")
        for col in columns:
            col_name, data_type, default, nullable = col
            default_str = f" DEFAULT {default[:30]}..." if default and len(default) > 30 else f" DEFAULT {default}" if default else ""
            print(f"   - {col_name} ({data_type}){default_str}")

        # Check if created_at and updated_at exist
        has_created_at = any(col[0] == 'created_at' for col in columns)
        has_updated_at = any(col[0] == 'updated_at' for col in columns)

        print()
        if has_created_at and has_updated_at:
            print("✅ VERIFIED: Both created_at and updated_at columns exist!")
        else:
            if not has_created_at:
                print("❌ ERROR: created_at column NOT found!")
            if not has_updated_at:
                print("❌ ERROR: updated_at column NOT found!")

        # Check schema_migrations table
        print()
        print("🔍 Checking migration history...")
        cur.execute("SELECT version, description, applied_at FROM schema_migrations ORDER BY applied_at DESC;")
        migrations = cur.fetchall()

        if migrations:
            print(f"   Applied migrations ({len(migrations)}):")
            for version, desc, applied_at in migrations:
                print(f"   - {version}: {desc} (applied: {applied_at})")
        else:
            print("   No migrations recorded yet")

        cur.close()
        conn.close()

        print()
        print("🎉 Migration completed successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == '__main__':
    main()
