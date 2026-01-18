# Data Model: ChatKit Frontend-Backend Integration

## Entities

### ChatSession
**Description**: Represents an authenticated connection between the frontend and AI backend with proper JWT token validation
**Attributes**:
- id: UUID (primary key)
- user_id: UUID (foreign key to users table)
- client_secret: string (ChatKit client secret)
- created_at: timestamp
- expires_at: timestamp
- status: enum (active, expired, revoked)

**Relationships**:
- Belongs to User (many-to-one)
- One-to-many with ChatThread

### ChatThread
**Description**: Represents a conversation thread with message history
**Attributes**:
- id: UUID (primary key)
- session_id: UUID (foreign key to chat_sessions table)
- title: string (auto-generated from first message)
- created_at: timestamp
- updated_at: timestamp

**Relationships**:
- Belongs to ChatSession (many-to-one)
- One-to-many with ChatMessage

### ChatMessage
**Description**: Represents a single message in a chat thread
**Attributes**:
- id: UUID (primary key)
- thread_id: UUID (foreign key to chat_threads table)
- role: enum (user, assistant)
- content: text
- created_at: timestamp
- metadata: JSON (additional message data)

**Relationships**:
- Belongs to ChatThread (many-to-one)

### ClientEffectEvent
**Description**: Represents an event sent from the backend to the frontend to trigger UI updates
**Attributes**:
- id: UUID (primary key)
- thread_id: UUID (foreign key to chat_threads table)
- event_type: enum (task_created, task_updated, task_deleted, task_completed)
- event_data: JSON (data for the event)
- created_at: timestamp

**Relationships**:
- Belongs to ChatThread (many-to-one)

### ChatTool
**Description**: Represents a contextual tool available in the chat composer
**Attributes**:
- id: string (primary key, e.g., "create_task", "search_tasks")
- name: string (display name)
- icon: string (icon identifier)
- label: string (button text)
- description: string (tool description)
- enabled: boolean (whether tool is active)

## Validation Rules

### ChatSession
- user_id must reference an existing user
- client_secret must be non-empty
- expires_at must be in the future
- status must be one of the defined enum values

### ChatThread
- session_id must reference an active session
- title must be 1-200 characters
- created_at and updated_at must be valid timestamps

### ChatMessage
- thread_id must reference an existing thread
- role must be either 'user' or 'assistant'
- content must be non-empty
- created_at must be a valid timestamp

### ClientEffectEvent
- thread_id must reference an existing thread
- event_type must be one of the defined enum values
- event_data must be valid JSON

### ChatTool
- id must be unique
- name and label must be non-empty
- enabled must be a boolean value

## State Transitions

### ChatSession
- Created → Active (when session is established)
- Active → Expired (when token expires)
- Active → Revoked (when manually revoked)

### ChatMessage
- Created (when message is added to thread)
- Processed (when AI has responded to user message)