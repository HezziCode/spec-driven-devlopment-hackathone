# Data Model: ChatKit AI Chat Server

## Entities

### Thread

Conversation container that maintains context for a series of messages.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary Key | Unique thread identifier |
| `user_id` | UUID | Foreign Key, Indexed | Owner of the thread |
| `title` | String | Max 200 chars, Optional | Human-readable thread title |
| `created_at` | DateTime | Default: now | Thread creation timestamp |
| `updated_at` | DateTime | Default: now, Auto-update | Last activity timestamp |

**Relationships**:
- Many-to-one: User (each thread belongs to one user)
- One-to-many: ChatMessage (each thread has many messages)

### ChatMessage

Individual message within a thread conversation.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Primary Key | Unique message identifier |
| `thread_id` | UUID | Foreign Key, Indexed | Parent thread |
| `role` | String | Enum: "user", "assistant" | Message author type |
| `content` | Text | Required | Message content |
| `created_at` | DateTime | Default: now | Message timestamp |

**Relationships**:
- Many-to-one: Thread (each message belongs to one thread)

### ThreadMessageIndex (Optional)

For optimized retrieval of recent messages per thread.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `thread_id` | UUID | Foreign Key, Primary Key | Parent thread |
| `message_order` | Integer | Primary Key, Auto-increment | Position in conversation |
| `message_id` | UUID | Foreign Key | Reference to ChatMessage |

**Note**: Can be derived from `created_at` ordering - only needed for very high-volume scenarios.

## Validation Rules

1. **Thread Creation**:
   - `user_id` must reference existing User
   - `title` must be between 1-200 characters if provided

2. **Message Creation**:
   - `thread_id` must reference existing Thread
   - `role` must be either "user" or "assistant"
   - `content` must be non-empty

3. **User Isolation**:
   - Users can only access threads they own
   - Queries must filter by `user_id` (enforced at API level)

## State Transitions

```
Thread States:
  ACTIVE ←→ ARCHIVED (user can archive threads)
  (No soft delete - permanent storage per constitution)

Message States:
  PERSISTED (default - immutable after creation)
```

## Indexes

| Table | Column(s) | Index Type | Purpose |
|-------|-----------|------------|---------|
| Thread | user_id | B-tree | User's threads listing |
| Thread | updated_at | B-tree | Sort by recent activity |
| ChatMessage | thread_id | B-tree | Thread messages retrieval |
| ChatMessage | thread_id, created_at | B-tree | Recent messages query |
| ChatMessage | created_at | B-tree | Global message search |

## Example Data

```json
{
  "thread": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "550e8400-e29b-41d4-a716-446655440001",
    "title": "Task Management Help",
    "created_at": "2025-12-30T10:00:00Z",
    "updated_at": "2025-12-30T10:05:00Z"
  },
  "messages": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440000",
      "thread_id": "550e8400-e29b-41d4-a716-446655440000",
      "role": "user",
      "content": "How do I create a task?",
      "created_at": "2025-12-30T10:00:01Z"
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "thread_id": "550e8400-e29b-41d4-a716-446655440000",
      "role": "assistant",
      "content": "You can create a task by clicking the 'Add Task' button...",
      "created_at": "2025-12-30T10:00:05Z"
    }
  ]
}
```
