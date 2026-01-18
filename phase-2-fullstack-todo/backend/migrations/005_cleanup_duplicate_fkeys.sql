-- Remove duplicate foreign key constraint on chat_messages.thread_id
-- Keep only the properly named constraint 'chat_messages_thread_id_fkey'

-- Check current constraints
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

-- Drop the duplicate constraint 'fk_chat_messages_thread_id' if it exists
ALTER TABLE chat_messages
DROP CONSTRAINT IF EXISTS fk_chat_messages_thread_id;

-- Verify the cleanup
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