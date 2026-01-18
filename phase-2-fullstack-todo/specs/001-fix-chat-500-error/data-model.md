# Data Model: Chat Thread and Message Entities

**Feature**: Fix Chat Message Loading Error (001-fix-chat-500-error)
**Date**: 2026-01-04
**Purpose**: Document existing data models involved in chat functionality

## Overview

The chat feature uses two primary entities: Thread and Message. These models are already defined in the codebase and do not require changes for this fix. This document serves as reference for understanding the data structure.

## Entities

### Thread

Represents a chat conversation thread between a user and the AI assistant.

**Attributes**:
- `id` (UUID, Primary Key): Unique identifier for the thread
- `user_id` (UUID, Foreign Key → users.id): Owner of the thread
- `created_at` (Timestamp): When the thread was created
- `updated_at` (Timestamp): Last modification time

**Relationships**:
- Belongs to one User (via `user_id`)
- Has many Messages (one-to-many)

**Validation Rules**:
- `user_id` must reference an existing user
- Thread can only be accessed by the owning user (user isolation)

**State Transitions**:
- Created: New thread initialized
- Active: Thread has messages
- (No explicit state field - inferred from message count)

### Message

Represents individual messages within a chat thread.

**Attributes**:
- `id` (UUID, Primary Key): Unique identifier for the message
- `user_id` (UUID, Foreign Key → users.id): Owner of the message
- `thread_id` (UUID, Foreign Key → threads.id): Parent thread
- `role` (String): Message sender role ('user' or 'assistant')
- `content` (Text): Message content
- `created_at` (Timestamp): When the message was sent

**Relationships**:
- Belongs to one User (via `user_id`)
- Belongs to one Thread (via `thread_id`)

**Validation Rules**:
- `role` must be either 'user' or 'assistant'
- `content` must not be empty
- `user_id` must match thread's `user_id` (user isolation)
- `thread_id` must reference an existing thread

**State Transitions**:
- Created: Message added to thread
- (Messages are immutable - no updates or deletions)

## Database Schema

### threads Table
```sql
CREATE TABLE threads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_threads_user_id ON threads(user_id);
```

### messages Table
```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    thread_id UUID NOT NULL REFERENCES threads(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_messages_thread_id ON messages(thread_id);
CREATE INDEX idx_messages_user_id ON messages(user_id);
```

## SQLModel Models (Existing)

### Thread Model
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4

class Thread(SQLModel, table=True):
    __tablename__ = "threads"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### Message Model
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Literal

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False)
    thread_id: UUID = Field(foreign_key="threads.id", nullable=False)
    role: Literal["user", "assistant"] = Field(nullable=False)
    content: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

## Session Management Context

### Current Issue

The thread manager attempts to query these models using a generator object instead of a Session:

```python
# WRONG: session is a generator
thread = session.get(Thread, thread_id)  # AttributeError!
```

### Required Fix

The session must be a resolved SQLAlchemy Session object:

```python
# CORRECT: session is AsyncSession
thread = await session.get(Thread, thread_id)  # Works!
```

## Query Patterns

### Get Thread by ID
```python
async def get_thread(session: AsyncSession, thread_id: UUID) -> Thread | None:
    result = await session.execute(
        select(Thread).where(Thread.id == thread_id)
    )
    return result.scalar_one_or_none()
```

### Get Thread with Messages
```python
async def get_thread_with_messages(
    session: AsyncSession,
    thread_id: UUID
) -> tuple[Thread, list[Message]]:
    # Get thread
    thread = await session.get(Thread, thread_id)

    # Get messages
    result = await session.execute(
        select(Message)
        .where(Message.thread_id == thread_id)
        .order_by(Message.created_at)
    )
    messages = result.scalars().all()

    return thread, messages
```

### Create Message
```python
async def create_message(
    session: AsyncSession,
    thread_id: UUID,
    user_id: UUID,
    role: str,
    content: str
) -> Message:
    message = Message(
        thread_id=thread_id,
        user_id=user_id,
        role=role,
        content=content
    )
    session.add(message)
    await session.commit()
    await session.refresh(message)
    return message
```

## User Isolation

All queries must filter by `user_id` to enforce user isolation:

```python
# Verify thread belongs to user
async def get_user_thread(
    session: AsyncSession,
    user_id: UUID,
    thread_id: UUID
) -> Thread | None:
    result = await session.execute(
        select(Thread)
        .where(Thread.id == thread_id)
        .where(Thread.user_id == user_id)  # User isolation
    )
    return result.scalar_one_or_none()
```

## Changes Required for Fix

**None** - The data models are correct and do not need modification. The issue is purely in how sessions are passed to the thread manager, not in the model definitions.

## Notes

- Models follow SQLModel conventions
- Timestamps use UTC
- UUIDs are auto-generated
- Foreign key constraints ensure referential integrity
- Indexes optimize common queries (by user_id, thread_id)
- User isolation is enforced at query level, not model level
