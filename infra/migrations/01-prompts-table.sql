-- Migration: 01-prompts-table
-- Description: Create prompts table for template storage
-- Date: 2025-01-26

-- Check if migration already applied
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM schema_migrations WHERE version = '01-prompts-table') THEN

        -- Create prompts table
        CREATE TABLE IF NOT EXISTS prompts (
            id SERIAL PRIMARY KEY,
            code VARCHAR(255) UNIQUE NOT NULL,
            name TEXT NOT NULL,
            content TEXT NOT NULL,
            variables JSONB DEFAULT '{}',
            categories TEXT[] DEFAULT '{}',
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );

        -- Create indexes
        CREATE INDEX IF NOT EXISTS idx_prompts_code ON prompts(code);
        -- GIN index for array requires explicit operator class
        CREATE INDEX IF NOT EXISTS idx_prompts_categories ON prompts USING GIN(categories array_ops);

        -- Create updated_at trigger
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $func$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $func$ LANGUAGE plpgsql;

        CREATE TRIGGER update_prompts_updated_at
            BEFORE UPDATE ON prompts
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();

        -- Record migration
        INSERT INTO schema_migrations (version, description)
        VALUES ('01-prompts-table', 'Create prompts table for template storage');

        RAISE NOTICE 'Migration 01-prompts-table applied successfully';
    ELSE
        RAISE NOTICE 'Migration 01-prompts-table already applied, skipping';
    END IF;
END $$;
