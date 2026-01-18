-- Migration: Fix cascade delete for chat_messages
-- Feature: 016-fix-chat-task-persistence
-- Date: 2026-01-05
-- Description: Ensure chat_messages are automatically deleted when thread is deleted

-- Check existing foreign key constraints
SELECT
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    rc.delete_rule
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
JOIN information_schema.referential_constraints AS rc
  ON tc.constraint_name = rc.constraint_name
WHERE tc.table_name = 'chat_messages'
  AND kcu.column_name = 'thread_id';

-- Drop existing foreign key constraint if it exists
ALTER TABLE chat_messages
DROP CONSTRAINT IF EXISTS chat_messages_thread_id_fkey;

-- Recreate with CASCADE DELETE
ALTER TABLE chat_messages
ADD CONSTRAINT chat_messages_thread_id_fkey
FOREIGN KEY (thread_id)
REFERENCES chat_threads(id)
ON DELETE CASCADE;

-- Also ensure user_id has CASCADE DELETE
ALTER TABLE chat_messages
DROP CONSTRAINT IF EXISTS chat_messages_user_id_fkey;

ALTER TABLE chat_messages
ADD CONSTRAINT chat_messages_user_id_fkey
FOREIGN KEY (user_id)
REFERENCES users(id)
ON DELETE CASCADE;

-- Verify cascade delete is configured
SELECT
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    rc.delete_rule
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
JOIN information_schema.referential_constraints AS rc
  ON tc.constraint_name = rc.constraint_name
WHERE tc.table_name = 'chat_messages'
  AND rc.delete_rule = 'CASCADE';
