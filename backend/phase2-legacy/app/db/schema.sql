-- AAP MCP POC - Complete Database Schema
-- Version: 2.0
-- Description: Production-ready schema with all tables, indexes, and constraints

BEGIN;

-- Clean up existing tables (be careful in production!)
DROP TABLE IF EXISTS execution_io CASCADE;
DROP TABLE IF EXISTS executions CASCADE;
DROP TABLE IF EXISTS prompt_assets CASCADE;
DROP TABLE IF EXISTS prompt_versions CASCADE;
DROP TABLE IF EXISTS prompts CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS audit_logs CASCADE;

-- Users table (for tracking who creates/modifies prompts)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    roles TEXT[] DEFAULT '{}', -- Array of roles: admin, hr, dev, qa, pm
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Main prompts table
CREATE TABLE prompts (
    id SERIAL PRIMARY KEY,
    code VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'hr_offer_letter'
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(50), -- hr, dev, qa, pm, ba
    tags TEXT[] DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    is_template BOOLEAN DEFAULT FALSE, -- Template vs active prompt
    created_by INTEGER REFERENCES users(id),
    updated_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Prompt versions (support versioning)
CREATE TABLE prompt_versions (
    id SERIAL PRIMARY KEY,
    prompt_id INTEGER NOT NULL REFERENCES prompts(id) ON DELETE CASCADE,
    version INTEGER NOT NULL DEFAULT 1,
    content TEXT, -- The actual prompt template with {{variables}}
    arguments_json JSONB NOT NULL DEFAULT '[]'::jsonb, -- MCP argument definitions
    rules_json JSONB DEFAULT '{}'::jsonb, -- Rendering rules
    variables_json JSONB DEFAULT '{}'::jsonb, -- Extracted variables metadata
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    change_notes TEXT,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(prompt_id, version)
);

-- Assets linked to prompt versions (templates, documents, etc.)
CREATE TABLE prompt_assets (
    id SERIAL PRIMARY KEY,
    prompt_version_id INTEGER NOT NULL REFERENCES prompt_versions(id) ON DELETE CASCADE,
    asset_key VARCHAR(120) NOT NULL, -- e.g., 'offer_letter_docx'
    asset_type VARCHAR(50), -- docx, pdf, json, yaml
    provider VARCHAR(40) NOT NULL, -- drive, s3, github
    uri TEXT NOT NULL, -- drive://file/{id} or s3://bucket/key
    mime_type VARCHAR(120),
    file_size BIGINT,
    checksum VARCHAR(255),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(prompt_version_id, asset_key)
);

-- Execution history
CREATE TABLE executions (
    id SERIAL PRIMARY KEY,
    prompt_version_id INTEGER REFERENCES prompt_versions(id),
    user_id INTEGER REFERENCES users(id),
    user_email VARCHAR(255), -- Fallback if user not in DB
    session_id VARCHAR(255),
    external_exec_id VARCHAR(255), -- For external system tracking
    status VARCHAR(40) NOT NULL DEFAULT 'running', -- running, succeeded, failed
    error_message TEXT,
    started_at TIMESTAMP DEFAULT NOW(),
    finished_at TIMESTAMP,
    duration_ms INTEGER, -- Execution time in milliseconds
    artifacts_json JSONB DEFAULT '{}'::jsonb, -- Output artifacts
    metadata JSONB DEFAULT '{}'::jsonb -- Additional execution metadata
);

-- Execution input/output log
CREATE TABLE execution_io (
    id SERIAL PRIMARY KEY,
    execution_id INTEGER NOT NULL REFERENCES executions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- input, output, trace, error
    sequence INTEGER DEFAULT 0, -- Order of operations
    data_json JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Audit log for compliance
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    user_email VARCHAR(255),
    action VARCHAR(100) NOT NULL, -- create_prompt, update_prompt, execute_prompt, etc.
    resource_type VARCHAR(50), -- prompt, execution, asset
    resource_id INTEGER,
    old_data JSONB,
    new_data JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_prompts_code ON prompts(code);
CREATE INDEX idx_prompts_category ON prompts(category);
CREATE INDEX idx_prompts_is_active ON prompts(is_active);
CREATE INDEX idx_prompt_versions_prompt_id ON prompt_versions(prompt_id);
CREATE INDEX idx_prompt_versions_is_default ON prompt_versions(is_default);
CREATE INDEX idx_executions_status ON executions(status);
CREATE INDEX idx_executions_user_email ON executions(user_email);
CREATE INDEX idx_executions_started_at ON executions(started_at DESC);
CREATE INDEX idx_execution_io_execution_id ON execution_io(execution_id);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);

-- Create views for common queries
CREATE OR REPLACE VIEW active_prompts AS
SELECT 
    p.id,
    p.code,
    p.name,
    p.description,
    p.category,
    p.tags,
    pv.version,
    pv.content,
    pv.arguments_json,
    pv.rules_json,
    pv.id as version_id
FROM prompts p
JOIN prompt_versions pv ON p.id = pv.prompt_id
WHERE p.is_active = TRUE 
  AND pv.is_default = TRUE;

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply update trigger to relevant tables
CREATE TRIGGER update_prompts_updated_at BEFORE UPDATE ON prompts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to ensure only one default version per prompt
CREATE OR REPLACE FUNCTION ensure_single_default_version()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.is_default = TRUE THEN
        UPDATE prompt_versions 
        SET is_default = FALSE 
        WHERE prompt_id = NEW.prompt_id 
          AND id != NEW.id;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER ensure_single_default_trigger
    BEFORE INSERT OR UPDATE ON prompt_versions
    FOR EACH ROW EXECUTE FUNCTION ensure_single_default_version();

-- Insert default data
INSERT INTO users (email, name, roles) VALUES
    ('admin@company.com', 'System Admin', ARRAY['admin']),
    ('hr@company.com', 'HR Manager', ARRAY['hr']),
    ('dev@company.com', 'Developer', ARRAY['dev']);

-- Insert sample prompts
INSERT INTO prompts (code, name, description, category, created_by) VALUES
    ('hr_offer_letter', 'HR Offer Letter Generator', 'Generate offer letters from templates', 'hr', 2),
    ('dev_code_review', 'Code Review Assistant', 'Automated code review with PR analysis', 'dev', 3),
    ('admin_onboarder', 'Admin Document Onboarder', 'Convert DOCX templates to prompts', 'admin', 1);

-- Insert prompt versions with proper arguments
INSERT INTO prompt_versions (prompt_id, version, content, arguments_json, rules_json, is_default) VALUES
    (1, 1, 'Generate offer letter for {{candidate_name}}, position {{position}}, salary {{salary}}',
     '[{"name":"candidate_name","type":"string","required":true,"description":"Full name of candidate"},
       {"name":"position","type":"string","required":true,"description":"Job position"},
       {"name":"salary","type":"string","required":true,"description":"Salary offer"},
       {"name":"start_date","type":"string","required":false,"description":"Start date"}]'::jsonb,
     '{"renderer":"docx_tokens","post_process":{"default_output_folder_id":"1ViGWBhDzjbNit-oy0YTMaB8PSke8PVrs"}}'::jsonb,
     true),
    (2, 1, 'Review PR #{{pr_number}} in repository {{repository}}',
     '[{"name":"pr_number","type":"string","required":true},
       {"name":"repository","type":"string","required":true}]'::jsonb,
     '{}'::jsonb,
     true);

COMMIT;

-- Verify installation
SELECT 
    'Tables created' as status,
    COUNT(*) as table_count 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name IN ('users', 'prompts', 'prompt_versions', 'prompt_assets', 'executions', 'execution_io', 'audit_logs');