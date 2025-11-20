-- Create users table for role-based access control
-- Users are created automatically on first SSO login

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    roles TEXT NOT NULL DEFAULT '["ALL"]',  -- JSON array of roles
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index for fast email lookup
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Insert default admin user (Gavin from SSO)
INSERT INTO users (email, name, roles, is_admin)
VALUES ('gavin.pham@ancileo.com', 'Gavin Pham', '["ADMIN"]', TRUE)
ON CONFLICT (email) DO NOTHING;

-- Insert test users for development
INSERT INTO users (email, name, roles, is_admin) VALUES
  ('test.ba@ancileo.com', 'Test BA User', '["BA", "PM"]', FALSE),
  ('test.qa@ancileo.com', 'Test QA User', '["QA"]', FALSE),
  ('test.dev@ancileo.com', 'Test Dev User', '["DEV", "TECH_LEAD"]', FALSE),
  ('test.hr@ancileo.com', 'Test HR User', '["HR"]', FALSE)
ON CONFLICT (email) DO NOTHING;

-- View current users
SELECT email, name, roles, is_admin FROM users ORDER BY created_at;
