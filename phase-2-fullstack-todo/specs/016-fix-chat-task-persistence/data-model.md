# Data Model: Fix Chat Task Persistence

**Feature**: 016-fix-chat-task-persistence
**Date**: 2026-01-05
**Status**: Complete

## Overview

This document defines the data models required for fixing chat task persistence issues. Models are defined using SQLModel (Pydantic + SQLAlchemy) for type safety and ORM functionality.

---

## Core Entities

### ChatThread

**Purpose**: Represents a conversation session between a user and the AI chatbot.

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime

class ChatThread(SQLModel, table=True):
    __tablename__ = "chat_threads"

    # Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique identifier for the thread"
    )

    # Foreign Keys
    user_id: UUID = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        description="Owner of the thread"
    )

    # Attributes
    name: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Optional thread name/title"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Thread creation timestamp"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last update timestamp"
    )

    # Relationships
    user: "User" = Relationship(back_populates="chat_threads")

    messages: List["ChatMessage"] = Relationship(
        back_populates="thread",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "passive_deletes": True,
            "order_by": "ChatMessage.created_at"
        }
    )

    tasks: List["Task"] = Relationship(
        back_populates="created_by_thread",
        sa_relationship_kwargs={"passive_deletes": True}
    )
```

**Validation Rules**:
- `user_id`: Must reference existing user
- `name`: Optional, max 200 characters
- `created_at`: Auto-generated, immutable
- `updated_at`: Auto-updated on modifications

**Indexes**:
- Primary: `id`
- Foreign: `user_id` (for user isolation queries)

**Cascade Behavior**:
- When thread deleted → all messages deleted (CASCADE)
- When thread deleted → tasks keep reference but set to NULL (SET NULL)

---

### ChatMessage

**Purpose**: Represents a single message in a conversation (user or assistant).

**SQLModel Definition**:
```python
from sqlalchemy import Column, Text

class ChatMessage(SQLModel, table=True):
    __tablename__ = "chat_messages"

    # Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique identifier for the message"
    )

    # Foreign Keys
    thread_id: UUID = Field(
        foreign_key="chat_threads.id",
        nullable=False,
        index=True,
        ondelete="CASCADE",
        description="Thread this message belongs to"
    )

    user_id: UUID = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        description="User who owns this conversation"
    )

    # Attributes
    role: str = Field(
        max_length=20,
        nullable=False,
        description="Message sender: 'user' or 'assistant'"
    )

    content: str = Field(
        sa_column=Column(Text),
        nullable=False,
        description="Message text content"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
        description="Message creation timestamp"
    )

    # Relationships
    thread: ChatThread = Relationship(back_populates="messages")
    user: "User" = Relationship(back_populates="chat_messages")

    # Validation
    @validator("role")
    def validate_role(cls, v):
        if v not in ["user", "assistant"]:
            raise ValueError("Role must be 'user' or 'assistant'")
        return v

    @validator("content")
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError("Content cannot be empty")
        return v.strip()
```

**Validation Rules**:
- `thread_id`: Must reference existing thread
- `user_id`: Must reference existing user
- `role`: Must be "user" or "assistant"
- `content`: Required, cannot be empty or whitespace-only
- `created_at`: Auto-generated, immutable

**Indexes**:
- Primary: `id`
- Foreign: `thread_id` (for thread message queries)
- Foreign: `user_id` (for user isolation)
- Timestamp: `created_at` (for ordering)

**Cascade Behavior**:
- When thread deleted → message deleted (CASCADE)
- When user deleted → message deleted (CASCADE)

---

### Task (Updated)

**Purpose**: Represents a todo item, now with source tracking for chat-created tasks.

**SQLModel Definition** (additions only):
```python
class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    # ... existing fields (id, user_id, title, description, etc.) ...

    # NEW FIELDS for chat integration
    source: str = Field(
        default="manual",
        max_length=50,
        nullable=False,
        description="Creation source: 'manual' or 'chat'"
    )

    created_by_thread_id: Optional[UUID] = Field(
        default=None,
        foreign_key="chat_threads.id",
        nullable=True,
        ondelete="SET NULL",
        description="Thread that created this task (if from chat)"
    )

    # Relationships (new)
    created_by_thread: Optional[ChatThread] = Relationship(
        back_populates="tasks"
    )

    # Validation
    @validator("source")
    def validate_source(cls, v):
        if v not in ["manual", "chat"]:
            raise ValueError("Source must be 'manual' or 'chat'")
        return v
```

**Validation Rules**:
- `source`: Must be "manual" or "chat"
- `created_by_thread_id`: Optional, must reference existing thread if provided
- If `source` is "chat", `created_by_thread_id` should be set

**Indexes**:
- New: `source` (for filtering by creation method)

**Cascade Behavior**:
- When thread deleted → `created_by_thread_id` set to NULL (SET NULL)

---

### User (Updated)

**Purpose**: User entity with new relationships for chat functionality.

**SQLModel Definition** (additions only):
```python
class User(SQLModel, table=True):
    __tablename__ = "users"

    # ... existing fields (id, username, email, etc.) ...

    # NEW RELATIONSHIPS for chat
    chat_threads: List[ChatThread] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "passive_deletes": True
        }
    )

    chat_messages: List[ChatMessage] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "passive_deletes": True
        }
    )
```

**Cascade Behavior**:
- When user deleted → all threads deleted (CASCADE)
- When user deleted → all messages deleted (CASCADE)

---

## Database Schema

### Tables

#### chat_threads
```sql
CREATE TABLE chat_threads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(200),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_chat_threads_user_id ON chat_threads(user_id);
```

#### chat_messages
```sql
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id UUID NOT NULL REFERENCES chat_threads(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_chat_messages_thread_id ON chat_messages(thread_id);
CREATE INDEX idx_chat_messages_user_id ON chat_messages(user_id);
CREATE INDEX idx_chat_messages_created_at ON chat_messages(created_at);
```

#### tasks (updates)
```sql
ALTER TABLE tasks
ADD COLUMN source VARCHAR(50) NOT NULL DEFAULT 'manual'
    CHECK (source IN ('manual', 'chat')),
ADD COLUMN created_by_thread_id UUID
    REFERENCES chat_threads(id) ON DELETE SET NULL;

CREATE INDEX idx_tasks_source ON tasks(source);
CREATE INDEX idx_tasks_created_by_thread_id ON tasks(created_by_thread_id);
```

---

## Relationships Diagram

```
User (1) ──────< (N) ChatThread
                      │
                      │ (1)
                      │
                      ├──< (N) ChatMessage
                      │
                      └──< (N) Task (optional)

Legend:
─── : One-to-Many relationship
< : Many side
CASCADE: Child deleted when parent deleted
SET NULL: Foreign key set to NULL when parent deleted
```

---

## Data Constraints

### Business Rules

1. **Thread Limit**: Each user can have maximum 20 active threads
   - Enforced at application level (not database constraint)
   - Checked before creating new thread

2. **Message Ordering**: Messages within a thread ordered by `created_at`
   - Enforced by query ORDER BY clause
   - Index on `created_at` for performance

3. **User Isolation**: All queries must filter by authenticated user's ID
   - Enforced by middleware and service layer
   - Prevents cross-user data access

4. **Content Validation**: Message content cannot be empty
   - Enforced by Pydantic validator
   - Trimmed of leading/trailing whitespace

5. **Role Validation**: Message role must be "user" or "assistant"
   - Enforced by Pydantic validator
   - Database CHECK constraint as backup

### Referential Integrity

1. **Thread → User**: Thread must belong to existing user
   - Foreign key constraint
   - CASCADE delete when user deleted

2. **Message → Thread**: Message must belong to existing thread
   - Foreign key constraint
   - CASCADE delete when thread deleted

3. **Message → User**: Message must belong to existing user
   - Foreign key constraint
   - CASCADE delete when user deleted

4. **Task → Thread**: Task can optionally reference thread
   - Foreign key constraint
   - SET NULL when thread deleted (preserve task)

---

## Migration Strategy

### Step 1: Verify Existing Schema
```sql
-- Check if tables exist
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('chat_threads', 'chat_messages');

-- Check existing foreign keys
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
WHERE tc.table_name IN ('chat_threads', 'chat_messages');
```

### Step 2: Fix Foreign Key Cascades (if needed)
```sql
-- Fix chat_messages → chat_threads cascade
ALTER TABLE chat_messages
DROP CONSTRAINT IF EXISTS chat_messages_thread_id_fkey;

ALTER TABLE chat_messages
ADD CONSTRAINT chat_messages_thread_id_fkey
FOREIGN KEY (thread_id)
REFERENCES chat_threads(id)
ON DELETE CASCADE;

-- Fix chat_messages → users cascade
ALTER TABLE chat_messages
DROP CONSTRAINT IF EXISTS chat_messages_user_id_fkey;

ALTER TABLE chat_messages
ADD CONSTRAINT chat_messages_user_id_fkey
FOREIGN KEY (user_id)
REFERENCES users(id)
ON DELETE CASCADE;
```

### Step 3: Add Task Source Tracking
```sql
-- Add new columns to tasks table
ALTER TABLE tasks
ADD COLUMN IF NOT EXISTS source VARCHAR(50) NOT NULL DEFAULT 'manual',
ADD COLUMN IF NOT EXISTS created_by_thread_id UUID;

-- Add check constraint
ALTER TABLE tasks
ADD CONSTRAINT tasks_source_check
CHECK (source IN ('manual', 'chat'));

-- Add foreign key
ALTER TABLE tasks
ADD CONSTRAINT tasks_created_by_thread_id_fkey
FOREIGN KEY (created_by_thread_id)
REFERENCES chat_threads(id)
ON DELETE SET NULL;

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_tasks_source
ON tasks(source);

CREATE INDEX IF NOT EXISTS idx_tasks_created_by_thread_id
ON tasks(created_by_thread_id);
```

### Step 4: Verify Indexes
```sql
-- Check all indexes on chat tables
SELECT
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename IN ('chat_threads', 'chat_messages', 'tasks')
ORDER BY tablename, indexname;
```

---

## Performance Considerations

### Query Optimization

1. **Thread List Query** (most frequent):
```sql
SELECT id, name, created_at, updated_at,
       (SELECT COUNT(*) FROM chat_messages WHERE thread_id = chat_threads.id) as message_count,
       (SELECT content FROM chat_messages WHERE thread_id = chat_threads.id ORDER BY created_at DESC LIMIT 1) as last_message
FROM chat_threads
WHERE user_id = $1
ORDER BY updated_at DESC
LIMIT 50 OFFSET 0;
```
- Uses index on `user_id`
- Subqueries use index on `thread_id`

2. **Message History Query**:
```sql
SELECT id, role, content, created_at
FROM chat_messages
WHERE thread_id = $1 AND user_id = $2
ORDER BY created_at ASC;
```
- Uses composite index on `(thread_id, created_at)`
- User_id check for security

3. **Thread Count Query** (for limit enforcement):
```sql
SELECT COUNT(*)
FROM chat_threads
WHERE user_id = $1;
```
- Uses index on `user_id`
- Fast count for limit check

### Index Strategy

**Existing Indexes**:
- `chat_threads.user_id` - For user isolation
- `chat_messages.thread_id` - For message retrieval
- `chat_messages.user_id` - For user isolation
- `chat_messages.created_at` - For message ordering
- `tasks.source` - For filtering by creation method

**Composite Indexes** (if needed for performance):
```sql
-- For message queries with user isolation
CREATE INDEX idx_chat_messages_thread_user
ON chat_messages(thread_id, user_id);

-- For ordered message retrieval
CREATE INDEX idx_chat_messages_thread_created
ON chat_messages(thread_id, created_at);
```

---

## Data Model Status

**Status**: Complete and ready for implementation
**Next Phase**: Generate API contracts
