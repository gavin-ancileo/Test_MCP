-- ============================================
-- RUN ALL MIGRATIONS
-- ============================================
-- This file runs all migrations in order
-- Safe to run multiple times - migrations are idempotent
-- ============================================

\echo 'Starting database migrations...'
\echo ''

-- Run migrations in order
\i /migrations/01-prompts-table.sql
\i /migrations/02-oauth-integrations.sql
\i /migrations/03-oauth-states.sql

\echo ''
\echo 'Migration summary:'
SELECT version, description, applied_at
FROM schema_migrations
ORDER BY applied_at;

\echo ''
\echo 'All migrations completed!'
