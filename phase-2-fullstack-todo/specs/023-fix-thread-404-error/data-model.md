# Data Model: Chat Thread Synchronization

## Overview

This data model addresses the synchronization between frontend and backend for chat thread creation and access to prevent "Thread not found" errors.

## Entities

### ChatThread
Represents a conversation thread with proper validation for synchronization

**Attributes**:
- id: string (primary key, unique identifier)
- user_id: UUID (foreign key to users table, ensures user isolation)
- name: string (display name for the thread)
- last_message_preview: string | null (preview of last message)
- message_count: integer (number of messages in thread)
- created_at: datetime (timestamp when thread was created)
- updated_at: datetime (timestamp when thread was last updated)

**Validation Rules**:
- user_id must reference existing user
- id must be unique across all threads
- user_id must match authenticated user for access (user isolation)

**State Transitions**:
- Created: When first message is sent to new thread
- Active: When thread has messages and is accessible
- Archived: When thread is deleted (soft delete in future enhancements)

### ChatMessage
Represents individual messages within a thread with foreign key relationship

**Attributes**:
- id: UUID (primary key)
- thread_id: string (foreign key to ChatThread.id)
- user_id: UUID (foreign key to users table, for user isolation)
- role: string ('user' or 'assistant')
- content: string (message content)
- created_at: datetime (timestamp when message was created)

**Validation Rules**:
- thread_id must reference existing ChatThread
- user_id must match authenticated user for access
- thread_id must exist before message creation is committed

## Relationships

- ChatThread (1) ←→ (Many) ChatMessage
- ChatThread (Many) ←→ (1) User (via user_id)

## Synchronization Constraints

### Thread Creation Order
1. ChatThread must be fully committed to database
2. Only then can ChatMessage be created with reference to that thread_id
3. Foreign key constraint ensures integrity

### Access Validation
1. Thread must exist in database before access
2. User must own the thread (user_id match)
3. Proper session management between operations