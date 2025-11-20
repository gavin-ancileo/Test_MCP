-- Check actual schema of prompts table in production database
-- Run this in AWS RDS Query Editor or psql

-- 1. Check if prompts table exists
SELECT EXISTS (
    SELECT FROM information_schema.tables
    WHERE table_name = 'prompts'
) as prompts_table_exists;

-- 2. List all columns in prompts table
SELECT
    column_name,
    data_type,
    character_maximum_length,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'prompts'
ORDER BY ordinal_position;

-- 3. Show sample data (first 5 rows)
SELECT * FROM prompts LIMIT 5;

-- 4. Check indexes
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'prompts';
