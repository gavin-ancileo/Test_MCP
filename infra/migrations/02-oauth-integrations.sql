-- Migration: 02-oauth-integrations
-- Description: Create OAuth integrations table
-- Date: 2025-01-26

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM schema_migrations WHERE version = '02-oauth-integrations') THEN

        -- Create oauth_integrations table
        CREATE TABLE IF NOT EXISTS oauth_integrations (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(255) NOT NULL,
            user_email VARCHAR(255),
            provider VARCHAR(50) NOT NULL,
            access_token TEXT NOT NULL,
            refresh_token TEXT,
            token_expires_at TIMESTAMP,
            scope TEXT,
            provider_user_id VARCHAR(255),
            provider_user_email VARCHAR(255),
            metadata JSONB,
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );

        -- Create indexes
        CREATE UNIQUE INDEX IF NOT EXISTS idx_user_provider ON oauth_integrations(user_id, provider);
        CREATE INDEX IF NOT EXISTS idx_user_id ON oauth_integrations(user_id);

        -- Create updated_at trigger (only if function exists)
        IF EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'update_updated_at_column') THEN
            CREATE TRIGGER update_oauth_integrations_updated_at
                BEFORE UPDATE ON oauth_integrations
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
        END IF;

        -- Record migration
        INSERT INTO schema_migrations (version, description)
        VALUES ('02-oauth-integrations', 'Create OAuth integrations table');

        RAISE NOTICE 'Migration 02-oauth-integrations applied successfully';
    ELSE
        RAISE NOTICE 'Migration 02-oauth-integrations already applied, skipping';
    END IF;
END $$;
