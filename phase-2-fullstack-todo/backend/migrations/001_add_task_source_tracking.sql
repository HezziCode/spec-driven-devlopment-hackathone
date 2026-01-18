-- Migration: Add task source tracking fields
-- Feature: 016-fix-chat-task-persistence
-- Date: 2026-01-05
-- Description: Add source and created_by_thread_id columns to tasks table for tracking chat-created tasks

-- Add source column with default 'manual'
ALTER TABLE tasks
ADD COLUMN IF NOT EXISTS source VARCHAR(50) NOT NULL DEFAULT 'manual';

-- Add created_by_thread_id column (nullable, references chat_threads)
ALTER TABLE tasks
ADD COLUMN IF NOT EXISTS created_by_thread_id VARCHAR(100);

-- Add check constraint for source field
ALTER TABLE tasks
ADD CONSTRAINT tasks_source_check
CHECK (source IN ('manual', 'chat'));

-- Add foreign key constraint (ON DELETE SET NULL to preserve task when thread deleted)
ALTER TABLE tasks
ADD CONSTRAINT tasks_created_by_thread_id_fkey
FOREIGN KEY (created_by_thread_id)
REFERENCES chat_threads(id)
ON DELETE SET NULL;

-- Add index for efficient filtering by source
CREATE INDEX IF NOT EXISTS idx_task_source ON tasks(source);

-- Add index for thread-task relationship queries
CREATE INDEX IF NOT EXISTS idx_tasks_created_by_thread_id ON tasks(created_by_thread_id);

-- Verify migration
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'tasks'
  AND column_name IN ('source', 'created_by_thread_id');
