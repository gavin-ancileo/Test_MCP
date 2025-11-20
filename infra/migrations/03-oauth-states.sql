-- Migration: 03-oauth-states
-- Description: Create OAuth states table for persistent flow management
-- Date: 2025-01-26

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM schema_migrations WHERE version = '03-oauth-states') THEN

        -- Create oauth_states table
        CREATE TABLE IF NOT EXISTS oauth_states (
            state VARCHAR(255) PRIMARY KEY,
            user_id VARCHAR(255) NOT NULL,
            user_email VARCHAR(255),
            provider VARCHAR(50) NOT NULL,
            created_at TIMESTAMP DEFAULT NOW(),
            expires_at TIMESTAMP DEFAULT NOW() + INTERVAL '10 minutes'
        );

        -- Create indexes
        CREATE INDEX IF NOT EXISTS idx_oauth_states_expires_at ON oauth_states(expires_at);
        CREATE INDEX IF NOT EXISTS idx_oauth_states_user_id ON oauth_states(user_id);

        -- Create cleanup function
        CREATE OR REPLACE FUNCTION cleanup_expired_oauth_states()
        RETURNS INTEGER AS $func$
        DECLARE
            deleted_count INTEGER;
        BEGIN
            DELETE FROM oauth_states WHERE expires_at < NOW();
            GET DIAGNOSTICS deleted_count = ROW_COUNT;
            RETURN deleted_count;
        END;
        $func$ LANGUAGE plpgsql;

        -- Record migration
        INSERT INTO schema_migrations (version, description)
        VALUES ('03-oauth-states', 'Create OAuth states table for persistent flow management');

        RAISE NOTICE 'Migration 03-oauth-states applied successfully';
    ELSE
        RAISE NOTICE 'Migration 03-oauth-states already applied, skipping';
    END IF;
END $$;
