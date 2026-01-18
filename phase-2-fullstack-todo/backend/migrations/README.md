# Database Migrations

This directory contains SQL migration scripts for the Phase 2/3 Todo application.

## Migration Files

### 001_add_task_source_tracking.sql
- **Feature**: 016-fix-chat-task-persistence
- **Purpose**: Add source tracking to tasks table
- **Changes**:
  - Add `source` column (VARCHAR(50), default 'manual')
  - Add `created_by_thread_id` column (VARCHAR(100), nullable)
  - Add check constraint for source ('manual' or 'chat')
  - Add foreign key to chat_threads with ON DELETE SET NULL
  - Add indexes for performance

### 002_fix_cascade_delete.sql
- **Feature**: 016-fix-chat-task-persistence
- **Purpose**: Fix cascade delete for chat_messages
- **Changes**:
  - Drop and recreate chat_messages.thread_id foreign key with CASCADE DELETE
  - Drop and recreate chat_messages.user_id foreign key with CASCADE DELETE
  - Verify cascade delete configuration

## Running Migrations

### Using psql (PostgreSQL CLI)
```bash
# Set DATABASE_URL environment variable
export DATABASE_URL="postgresql://user:password@host:port/database"

# Run migration
psql $DATABASE_URL -f migrations/001_add_task_source_tracking.sql
psql $DATABASE_URL -f migrations/002_fix_cascade_delete.sql
```

### Using Python script
```python
import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    with open("migrations/001_add_task_source_tracking.sql") as f:
        conn.execute(text(f.read()))
    with open("migrations/002_fix_cascade_delete.sql") as f:
        conn.execute(text(f.read()))
    conn.commit()
```

## Rollback

To rollback migrations, manually drop the added columns and constraints:

```sql
-- Rollback 001_add_task_source_tracking.sql
ALTER TABLE tasks DROP CONSTRAINT IF EXISTS tasks_source_check;
ALTER TABLE tasks DROP CONSTRAINT IF EXISTS tasks_created_by_thread_id_fkey;
DROP INDEX IF EXISTS idx_task_source;
DROP INDEX IF EXISTS idx_tasks_created_by_thread_id;
ALTER TABLE tasks DROP COLUMN IF EXISTS source;
ALTER TABLE tasks DROP COLUMN IF EXISTS created_by_thread_id;

-- Rollback 002_fix_cascade_delete.sql
-- (Recreate original foreign keys without CASCADE)
ALTER TABLE chat_messages DROP CONSTRAINT IF EXISTS chat_messages_thread_id_fkey;
ALTER TABLE chat_messages ADD CONSTRAINT chat_messages_thread_id_fkey
FOREIGN KEY (thread_id) REFERENCES chat_threads(id);

ALTER TABLE chat_messages DROP CONSTRAINT IF EXISTS chat_messages_user_id_fkey;
ALTER TABLE chat_messages ADD CONSTRAINT chat_messages_user_id_fkey
FOREIGN KEY (user_id) REFERENCES users(id);
```

## Verification

After running migrations, verify the changes:

```sql
-- Check tasks table columns
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'tasks'
  AND column_name IN ('source', 'created_by_thread_id');

-- Check foreign key constraints
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
WHERE tc.table_name IN ('tasks', 'chat_messages')
  AND tc.constraint_type = 'FOREIGN KEY';
```

## Notes

- All migrations are idempotent (can be run multiple times safely)
- Use `IF NOT EXISTS` and `IF EXISTS` clauses to prevent errors
- Always backup database before running migrations in production
- Test migrations on staging environment first
