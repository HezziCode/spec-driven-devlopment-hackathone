-- Migration: Fix CASCADE DELETE for chat_messages.thread_id
-- Feature: Fix thread deletion HTTP 500 errors
-- Date: 2026-01-06
-- Description: Drop and recreate foreign key with proper CASCADE DELETE

-- Drop existing foreign key constraint
ALTER TABLE chat_messages 
DROP CONSTRAINT IF EXISTS fk_chat_messages_thread_id;

-- Recreate with CASCADE DELETE
ALTER TABLE chat_messages
ADD CONSTRAINT fk_chat_messages_thread_id
FOREIGN KEY (thread_id) 
REFERENCES chat_threads(id) 
ON DELETE CASCADE;

-- Verify the constraint
SELECT 
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name,
    rc.delete_rule
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
JOIN information_schema.referential_constraints AS rc
    ON rc.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_name = 'chat_messages'
    AND kcu.column_name = 'thread_id';
