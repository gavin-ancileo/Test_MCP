-- Seed 3 test prompts
DELETE FROM prompts WHERE code LIKE 'test_%';

INSERT INTO prompts (code, name, categories, content) VALUES
('test_1', 'Test Prompt 1', '["test"]', 'Test content 1 with {{variable1}}'),
('test_2', 'Test Prompt 2', '["test"]', 'Test content 2 with {{variable2}}'),
('test_3', 'Test Prompt 3', '["test"]', 'Test content 3 with {{variable3}}');

-- Verify
SELECT COUNT(*) as test_count FROM prompts WHERE code LIKE 'test_%';
SELECT COUNT(*) as total_count FROM prompts;

