-- Migration: 001_add_user_role.sql
-- Adds `role` column to `user` table with default 'operator'
BEGIN;
ALTER TABLE "user" ADD COLUMN IF NOT EXISTS role varchar(32) DEFAULT 'operator';
COMMIT;

-- To revert:
-- BEGIN;
-- ALTER TABLE "user" DROP COLUMN IF EXISTS role;
-- COMMIT;
