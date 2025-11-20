-- Migration: 02-add-timestamps-to-prompts
-- Description: Add created_at and updated_at columns to existing prompts table
-- Date: 2025-11-20
-- Reason: Production database has prompts table without timestamps, causing ORDER BY failures

-- This migration is idempotent and safe to run multiple times

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
