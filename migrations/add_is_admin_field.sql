-- Migration to add is_admin field to users table
-- Run this SQL manually or through Flask-Migrate

-- Check if column exists before adding (PostgreSQL)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'users'
        AND column_name = 'is_admin'
    ) THEN
        ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE NOT NULL;
    END IF;
END $$;

-- For SQLite (if using SQLite in development)
-- SQLite doesn't support DO blocks, so use this instead:
-- ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0 NOT NULL;

-- Create index for faster admin queries
CREATE INDEX IF NOT EXISTS idx_users_is_admin ON users(is_admin);

-- Optionally, set the first user (usually admin) as admin
-- UPDATE users SET is_admin = TRUE WHERE id = 1;