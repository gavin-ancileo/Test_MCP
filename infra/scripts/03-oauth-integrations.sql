-- OAuth Integrations Table
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

CREATE UNIQUE INDEX IF NOT EXISTS idx_user_provider ON oauth_integrations(user_id, provider);
CREATE INDEX IF NOT EXISTS idx_user_id ON oauth_integrations(user_id);

-- Add updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_oauth_integrations_updated_at BEFORE UPDATE
    ON oauth_integrations FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
