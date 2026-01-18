# Data Model: Fix Chat Thread and API Key Errors

**Feature**: Fix Chat Thread and API Key Errors
**Date**: 2026-01-13
**Author**: Claude Code

## Overview

This data model describes the entities and relationships involved in fixing the chat thread 404 errors and OpenAI API key 401 errors. The focus is on ensuring proper thread synchronization and API authentication while maintaining data integrity.

## Entity Definitions

### ChatThread
- **Description**: Represents a conversation thread between user and AI assistant
- **Fields**:
  - `id: UUID` (primary key) - Unique identifier for the thread
  - `user_id: UUID` (foreign key) - Owner of the thread
  - `name: string` - Display name for the thread
  - `last_message_preview: string` - Preview text of the last message
  - `message_count: integer` - Number of messages in the thread
  - `created_at: datetime` - Timestamp when thread was created
  - `updated_at: datetime` - Timestamp when thread was last updated
- **Relationships**:
  - One-to-many with ChatMessage (one thread contains many messages)
  - Many-to-one with User (many threads belong to one user)
- **Validation**:
  - `user_id` must be valid and exist in users table
  - `name` must not exceed 255 characters
  - `message_count` must be non-negative

### ChatMessage
- **Description**: Represents an individual message within a chat thread
- **Fields**:
  - `id: UUID` (primary key) - Unique identifier for the message
  - `thread_id: UUID` (foreign key) - Thread this message belongs to
  - `user_id: UUID` (foreign key) - User who sent the message
  - `role: string` - Role of the sender (user/assistant/system)
  - `content: string` - Content of the message
  - `created_at: datetime` - Timestamp when message was created
- **Relationships**:
  - Many-to-one with ChatThread (many messages belong to one thread)
  - Many-to-one with User (many messages associated with one user)
- **Validation**:
  - `thread_id` must be valid and exist in chat_threads table
  - `user_id` must be valid and exist in users table
  - `role` must be one of ["user", "assistant", "system"]
  - `content` must not be empty

### User
- **Description**: Represents an authenticated user in the system
- **Fields**:
  - `id: UUID` (primary key) - Unique identifier for the user
  - `username: string` - User's display name
  - `email: string` - User's email address
  - `created_at: datetime` - Timestamp when user was created
  - `updated_at: datetime` - Timestamp when user was last updated
- **Relationships**:
  - One-to-many with ChatThread (one user has many threads)
  - One-to-many with ChatMessage (one user sends many messages)
- **Validation**:
  - `email` must be a valid email format
  - `username` must be unique across all users

## State Transitions

### ChatThread States
- **Pending Creation**: Thread entity exists in memory but not yet committed to database
- **Created**: Thread is committed to database and available for access
- **Active**: Thread has received messages and is actively being used
- **Inactive**: Thread exists but no activity for extended period

### Thread Access Lifecycle
1. **Thread Creation Request**: User initiates new chat session
2. **Database Commit**: Thread is saved to database with initial properties
3. **Visibility Confirmation**: Thread becomes accessible to other processes
4. **Access Attempt**: Frontend tries to access the newly created thread
5. **Successful Access**: Thread is accessible and can be used for messaging

## Relationship Constraints

### Foreign Key Constraints
- `chat_messages.thread_id` references `chat_threads.id` (CASCADE DELETE)
- `chat_messages.user_id` references `users.id` (RESTRICT DELETE)
- `chat_threads.user_id` references `users.id` (RESTRICT DELETE)

### Unique Constraints
- `users.email` must be unique
- `users.username` must be unique

### Indexes for Performance
- Index on `chat_threads.user_id` for user-specific thread queries
- Index on `chat_messages.thread_id` for thread-specific message queries
- Index on `chat_messages.created_at` for chronological message ordering

## Validation Rules

### Thread Creation Validation
- Must have valid user_id belonging to authenticated user
- Thread name must be provided (default to first few words of first message if not provided)
- Thread must not exceed maximum allowed threads per user (e.g., 100)

### Thread Access Validation
- User can only access their own threads
- Thread must exist in database before access attempt
- Thread must be in valid state (not in process of deletion)

### Message Validation
- Message must belong to an existing thread
- Message role must be valid (user/assistant/system)
- Message content must not exceed maximum character limit (e.g., 10,000 characters)

## Error Handling States

### Thread Not Found (404) Prevention
- Before returning thread, verify it exists in database
- Implement retry mechanism with exponential backoff
- Add small delay after creation to ensure database visibility
- Use proper session synchronization (`commit`, `expire_all`)

### API Authentication (401) Prevention
- Validate API key configuration at application startup
- Ensure API key is available for all OpenAI requests
- Implement fallback authentication methods if primary method fails
- Securely store and access API key without exposing in client code

## Data Integrity Measures

### Transaction Management
- Use database transactions for thread creation operations
- Ensure atomicity of thread creation with initial message if applicable
- Implement proper rollback mechanisms for failed operations

### Concurrency Control
- Prevent race conditions during thread creation and access
- Use proper locking mechanisms when necessary
- Implement optimistic locking for concurrent updates

## Monitoring Points

### Key Metrics
- Thread creation success rate
- Thread access success rate
- Average time from creation to first access
- Frequency of 404/401 errors

### Audit Trail
- Log thread creation and access attempts
- Track API authentication requests
- Monitor error patterns for troubleshooting

## API Contract Implications

### GET /api/users/{user_id}/chat/threads/{thread_id}
- Response: 200 OK with thread and messages, 404 Not Found if thread doesn't exist
- Validation: Ensure thread belongs to specified user_id

### POST /api/users/{user_id}/chat/messages
- Request: Message content and optional thread_id (creates new thread if not provided)
- Response: 201 Created with new message and thread info, 401 Unauthorized if API key invalid
- Validation: Ensure user owns specified thread or creates new thread for user