# Data Model: ChatKit UI

**Feature**: 015-chatkit-ui
**Date**: 2025-12-31
**Phase**: Phase 1 Design

## Overview

This document defines the data models and relationships for the ChatKit UI feature. The data model focuses on frontend state management and backend persistence for chat threads, with integration to existing Task and User models.

## Frontend Data Models (TypeScript)

### 1. ChatSession

Represents an active ChatKit session with authentication and connection state.

```typescript
interface ChatSession {
  /** ChatKit client secret for session authentication */
  clientSecret: string;

  /** Session creation timestamp */
  createdAt: Date;

  /** Session expiry timestamp */
  expiresAt: Date;

  /** Current session status */
  status: 'initializing' | 'ready' | 'error' | 'expired';

  /** User ID associated with this session */
  userId: string;

  /** Error message if status is 'error' */
  error?: string;
}
```

**Validation Rules**:
- `clientSecret` must be non-empty string
- `expiresAt` must be after `createdAt`
- `userId` must match authenticated user from Better Auth JWT

**State Transitions**:
```
initializing → ready (on successful connection)
initializing → error (on connection failure)
ready → expired (on session timeout)
expired → initializing (on session refresh)
```

---

### 2. ChatThread

Represents a conversation thread with message history and metadata.

```typescript
interface ChatThread {
  /** Unique thread identifier from ChatKit */
  id: string;

  /** Display name for the thread */
  name: string;

  /** Preview of the last message */
  lastMessagePreview: string;

  /** Timestamp of last message */
  lastUpdated: Date;

  /** Total number of messages in thread */
  messageCount: number;

  /** Whether this is the currently active thread */
  isActive: boolean;

  /** Thread creation timestamp */
  createdAt: Date;

  /** User ID who owns this thread */
  userId: string;
}
```

**Validation Rules**:
- `id` must be unique per user
- `name` max 100 characters, defaults to "Chat {timestamp}" if not set
- `lastMessagePreview` max 200 characters
- `messageCount` must be >= 0
- `userId` must match authenticated user

**Default Values**:
- `name`: "New Chat" or auto-generated from first message
- `messageCount`: 0 for new threads
- `isActive`: false (set to true when switched to)

---

### 3. ChatMessage

Represents a single message in a chat thread.

```typescript
interface ChatMessage {
  /** Unique message identifier */
  id: string;

  /** Thread this message belongs to */
  threadId: string;

  /** Message sender role */
  role: 'user' | 'assistant';

  /** Message content (supports markdown) */
  content: string;

  /** Message creation timestamp */
  createdAt: Date;

  /** Optional tool calls made during this message */
  toolCalls?: ToolCall[];

  /** Message status for loading states */
  status: 'sending' | 'sent' | 'error';

  /** Error message if status is 'error' */
  error?: string;
}
```

**Validation Rules**:
- `role` must be either 'user' or 'assistant'
- `content` must be non-empty string
- User messages have `toolCalls` = undefined
- Assistant messages may have `toolCalls` array

**Status Flow**:
```
User Message: sending → sent (on API success) or sending → error (on API failure)
Assistant Message: Created with status 'sent' (streamed from backend)
```

---

### 4. ToolCall

Represents an AI tool invocation during message processing.

```typescript
interface ToolCall {
  /** Tool identifier matching MCP tool names */
  id: string;

  /** Human-readable tool name */
  name: 'create_task' | 'search_tasks' | 'view_tasks' | 'update_task' | 'delete_task';

  /** Tool input parameters */
  parameters: Record<string, unknown>;

  /** Tool execution result */
  result?: {
    success: boolean;
    data?: unknown;
    error?: string;
  };

  /** Timestamp when tool was called */
  calledAt: Date;
}
```

**Validation Rules**:
- `name` must match one of the predefined tool names
- `parameters` must be valid JSON object
- `result` is populated after tool execution completes

---

### 5. ComposerTool

Represents a tool available in the composer menu.

```typescript
interface ComposerTool {
  /** Unique tool identifier */
  id: string;

  /** Icon name (from icon library) */
  icon: string;

  /** Full label shown in menu */
  label: string;

  /** Short label for compact views */
  shortLabel?: string;

  /** Custom placeholder text for composer */
  placeholderOverride?: string;

  /** Whether tool is enabled */
  enabled: boolean;
}
```

**Predefined Tools**:
```typescript
const COMPOSER_TOOLS: ComposerTool[] = [
  {
    id: 'create_task',
    icon: 'plus',
    label: 'Create Task',
    shortLabel: 'Create',
    placeholderOverride: 'What would you like to add?',
    enabled: true,
  },
  {
    id: 'search_tasks',
    icon: 'search',
    label: 'Search Tasks',
    shortLabel: 'Search',
    placeholderOverride: 'Search by title or tag...',
    enabled: true,
  },
  {
    id: 'view_tasks',
    icon: 'list',
    label: 'View All Tasks',
    shortLabel: 'View',
    enabled: true,
  },
];
```

---

### 6. ChatUIState

Global UI state for the chat interface.

```typescript
interface ChatUIState {
  /** Current active session */
  session: ChatSession | null;

  /** List of user's threads */
  threads: ChatThread[];

  /** Currently active thread ID */
  currentThreadId: string | null;

  /** Whether AI is currently responding */
  isResponding: boolean;

  /** Loading state for various operations */
  loading: {
    session: boolean;
    threads: boolean;
    messages: boolean;
  };

  /** Error states */
  errors: {
    session?: string;
    threads?: string;
    messages?: string;
  };

  /** Whether thread sidebar is open (mobile) */
  sidebarOpen: boolean;
}
```

---

## Backend Data Models (SQLModel/Pydantic)

### 1. ChatKitSession (Database Table)

Stores active ChatKit sessions for tracking and management.

```sql
CREATE TABLE chatkit_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    client_secret_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'expired', 'revoked')),
    last_used_at TIMESTAMP
);

CREATE INDEX idx_chatkit_sessions_user_id ON chatkit_sessions(user_id);
CREATE INDEX idx_chatkit_sessions_expires_at ON chatkit_sessions(expires_at);
CREATE INDEX idx_chatkit_sessions_status ON chatkit_sessions(status);
```

**SQLModel Definition**:
```python
class ChatKitSession(SQLModel, table=True):
    __tablename__ = "chatkit_sessions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False)
    client_secret_hash: str = Field(max_length=255, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(nullable=False)
    status: str = Field(default="active", max_length=20)
    last_used_at: datetime | None = Field(default=None)
```

**Business Rules**:
- Sessions expire after 24 hours by default
- Expired sessions should be cleaned up by background job
- User can have multiple active sessions (multi-device support)

---

### 2. ChatThread (Database Table)

Stores chat thread metadata for persistence.

```sql
CREATE TABLE chat_threads (
    id VARCHAR(100) PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL DEFAULT 'New Chat',
    last_message_preview VARCHAR(200),
    message_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_chat_threads_user_id ON chat_threads(user_id);
CREATE INDEX idx_chat_threads_updated_at ON chat_threads(updated_at DESC);
```

**SQLModel Definition**:
```python
class ChatThread(SQLModel, table=True):
    __tablename__ = "chat_threads"

    id: str = Field(primary_key=True, max_length=100)
    user_id: UUID = Field(foreign_key="users.id", nullable=False)
    name: str = Field(default="New Chat", max_length=100)
    last_message_preview: str | None = Field(default=None, max_length=200)
    message_count: int = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Business Rules**:
- Thread ID comes from ChatKit (external system)
- `name` auto-generated from first user message if not set
- `updated_at` refreshed on every new message
- Soft delete: mark as inactive instead of hard delete (future enhancement)

---

## Request/Response Schemas (Pydantic)

### 1. SessionRequest

```python
class SessionRequest(BaseModel):
    """Request to create a new ChatKit session"""
    # JWT token automatically extracted from Authorization header
    # No body parameters needed
    pass
```

### 2. SessionResponse

```python
class SessionResponse(BaseModel):
    """Response containing ChatKit client secret"""
    client_secret: str
    expires_at: datetime

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "client_secret": "cs_1234567890abcdef",
            "expires_at": "2025-12-31T23:59:59Z"
        }
    })
```

### 3. ThreadSyncRequest

```python
class ThreadSyncRequest(BaseModel):
    """Request to sync thread metadata to backend"""
    thread_id: str = Field(max_length=100)
    name: str = Field(max_length=100)
    last_message_preview: str | None = Field(default=None, max_length=200)
    message_count: int = Field(ge=0)
```

### 4. ThreadListResponse

```python
class ThreadItem(BaseModel):
    """Single thread in list response"""
    id: str
    name: str
    last_message_preview: str | None
    message_count: int
    created_at: datetime
    updated_at: datetime

class ThreadListResponse(BaseModel):
    """Response containing user's thread list"""
    threads: list[ThreadItem]
    total: int
```

---

## Data Relationships

```
User (existing)
  ├── ChatKitSession (1:many)
  │   └── Used for authentication and session management
  ├── ChatThread (1:many)
  │   └── Stores thread metadata for persistence
  └── Task (existing, 1:many)
      └── Tasks created/managed via ChatKit tools

ChatThread
  └── Messages (managed by ChatKit backend, not stored in our DB)
```

---

## Data Flow Diagrams

### Session Creation Flow

```
1. User opens chat interface
2. Frontend calls getClientSecret()
3. Frontend sends JWT to POST /api/chatkit/session
4. Backend validates JWT, extracts user_id
5. Backend generates client_secret via OpenAI API
6. Backend stores session in chatkit_sessions table
7. Backend returns client_secret to frontend
8. Frontend uses client_secret to establish ChatKit session
9. ChatKit session connects to OpenAI backend
```

### Thread Persistence Flow

```
1. User switches thread or sends message
2. ChatKit onThreadChange event fires
3. Frontend updates localStorage immediately
4. Frontend debounces backend sync (500ms)
5. Frontend sends POST /api/users/{user_id}/chatkit/threads/{thread_id}/sync
6. Backend updates chat_threads table
7. On app reload, frontend fetches threads from backend
8. Frontend populates localStorage with fetched threads
```

---

## Storage Estimates

### localStorage (Per User)
- Thread metadata: ~500 bytes per thread
- Last thread ID: ~20 bytes
- **Total for 100 threads**: ~50 KB

### PostgreSQL (Per User)
- ChatKitSession: ~200 bytes per session
- ChatThread: ~300 bytes per thread
- **Estimated for 1000 users with avg 50 threads each**: ~15 MB

---

## Data Retention Policies

| Data Type | Retention Period | Cleanup Method |
|-----------|------------------|----------------|
| ChatKitSession | 30 days after expiry | Automated cleanup job |
| ChatThread (active) | Indefinite | User-initiated deletion |
| ChatThread (inactive) | 90 days | Automated archival |
| localStorage cache | Browser lifetime | Browser storage management |

---

## Validation Summary

### Required Validations (Frontend)
- ✅ Chat session must have valid client_secret
- ✅ Thread IDs must be unique per user
- ✅ Message content must be non-empty
- ✅ Tool names must match predefined list

### Required Validations (Backend)
- ✅ JWT token must be valid and not expired
- ✅ User ID from JWT must match path parameter
- ✅ Thread ownership must be verified before sync
- ✅ Session expiry timestamp must be in future

---

## Next Steps

Phase 1 data models complete. Proceed to:

1. API Contract Definition (contracts/)
2. Quickstart Implementation Guide
3. Update agent context with new models

---

**Data Model Completed**: 2025-12-31
**Reviewed By**: AI Architect
**Approved for API Contract Design**: ✅
