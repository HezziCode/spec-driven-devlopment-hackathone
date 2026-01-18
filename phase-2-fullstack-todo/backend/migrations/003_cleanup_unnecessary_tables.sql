-- Migration: Cleanup unnecessary chat tables
-- Feature: Database simplification
-- Date: 2026-01-06
-- Description: Remove all unnecessary chat-related tables, keep only chat_messages and chat_threads

-- Drop unnecessary tables in correct order (respecting foreign keys)
DROP TABLE IF EXISTS client_effects CASCADE;
DROP TABLE IF EXISTS chat_tools CASCADE;
DROP TABLE IF EXISTS chatkit_sessions CASCADE;
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;
DROP TABLE IF EXISTS threads CASCADE;

-- Verify only required tables remain
SELECT tablename
FROM pg_tables
WHERE schemaname='public'
  AND (tablename LIKE '%chat%' OR tablename LIKE '%thread%' OR tablename LIKE '%message%')
ORDER BY tablename;
