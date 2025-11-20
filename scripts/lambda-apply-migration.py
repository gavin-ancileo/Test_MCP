#!/usr/bin/env python3
"""
AWS Lambda function to apply database migration
This can be deployed as a Lambda in the VPC to access RDS
"""

import os
import json
import psycopg2

def lambda_handler(event, context):
    """
    Lambda handler to apply migration 02-add-timestamps-to-prompts
    """

    # Database connection from environment variables or AWS Secrets Manager
    db_config = {
        'host': os.getenv('DB_HOST', 'aap-rds-new.cv2usk6ye3hm.ap-southeast-2.rds.amazonaws.com'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'prompts'),
        'user': os.getenv('DB_USER', 'AncileoMaster'),
        'password': os.getenv('DB_PASSWORD', 'AncileoAAP2025SecureDB#')
    }

    migration_sql = """
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

    -- Backfill existing rows
    UPDATE prompts
    SET created_at = COALESCE(created_at, NOW()),
        updated_at = COALESCE(updated_at, NOW())
    WHERE created_at IS NULL OR updated_at IS NULL;

    -- Create trigger function
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $func$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
    $func$ LANGUAGE plpgsql;

    -- Drop and recreate trigger
    DROP TRIGGER IF EXISTS update_prompts_updated_at ON prompts;

    CREATE TRIGGER update_prompts_updated_at
        BEFORE UPDATE ON prompts
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();

    -- Create schema_migrations table
    CREATE TABLE IF NOT EXISTS schema_migrations (
        version VARCHAR(255) PRIMARY KEY,
        description TEXT,
        applied_at TIMESTAMP DEFAULT NOW()
    );

    -- Record migration
    INSERT INTO schema_migrations (version, description)
    VALUES ('02-add-timestamps-to-prompts', 'Add created_at and updated_at columns')
    ON CONFLICT (version) DO NOTHING;

    RAISE NOTICE 'Migration completed successfully';
END $$;
"""

    try:
        print(f"Connecting to database: {db_config['host']}/{db_config['database']}")

        conn = psycopg2.connect(**db_config)
        conn.autocommit = True
        cur = conn.cursor()

        print("Applying migration...")
        cur.execute(migration_sql)

        # Verify the migration
        cur.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'prompts' AND column_name IN ('created_at', 'updated_at')
            ORDER BY column_name;
        """)

        columns = cur.fetchall()
        has_both = len(columns) == 2

        cur.close()
        conn.close()

        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'message': 'Migration applied successfully',
                'columns_added': columns,
                'verified': has_both
            })
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }

if __name__ == '__main__':
    # For local testing
    result = lambda_handler({}, {})
    print(json.dumps(result, indent=2))
