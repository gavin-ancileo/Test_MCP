-- ============================================
-- DATABASE INITIALIZATION (Run once on first setup)
-- ============================================
-- This creates the database if it doesn't exist
-- Docker postgres will run this automatically on first start

-- Create migrations tracking table
CREATE TABLE IF NOT EXISTS schema_migrations (
    id SERIAL PRIMARY KEY,
    version VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    applied_at TIMESTAMP DEFAULT NOW()
);

-- Insert initial migration record
INSERT INTO schema_migrations (version, description)
VALUES ('00-init', 'Initial database setup')
ON CONFLICT (version) DO NOTHING;
