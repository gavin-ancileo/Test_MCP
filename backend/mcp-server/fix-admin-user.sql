-- Ensure gavin.pham@ancileo.com is admin
-- This migration ensures the main admin user has correct permissions

INSERT INTO users (email, name, roles, is_admin)
VALUES ('gavin.pham@ancileo.com', 'Gavin Pham', '["ALL"]', TRUE)
ON CONFLICT (email) DO UPDATE
SET is_admin = TRUE, roles = '["ALL"]', name = 'Gavin Pham';

-- Verify the update
SELECT email, name, is_admin, roles FROM users WHERE email = 'gavin.pham@ancileo.com';
