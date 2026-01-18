# API Contract: Chat Thread Operations

**Feature**: 016-fix-chat-task-persistence
**Version**: 1.0.0
**Base URL**: `/api/users/{user_id}/chat`

## Authentication

All endpoints require JWT authentication via Bearer token in Authorization header.

**Header**:
```
Authorization: Bearer <jwt_token>
```

**User Isolation**: The `user_id` in the path must match the authenticated user's ID from the JWT token. Requests with mismatched IDs will receive 403 Forbidden.

---

## Endpoints

### GET /api/users/{user_id}/chat/threads

**Purpose**: Retrieve all chat threads for the authenticated user with pagination.

**Path Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| user_id | UUID | Yes | User ID (must match authenticated user) |

**Query Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| limit | integer | No | 50 | Maximum threads to return (1-100) |
| offset | integer | No | 0 | Number of threads to skip |

**Request Example**:
```http
GET /api/users/29fd73b8-308f-42d8-af87-b7ab3ec544a8/chat/threads?limit=20&offset=0
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response 200 OK**:
```json
{
  "threads": [
    {
      "id": "a9f3416a-4202-41f9-b662-8ebabe927736",
      "name": "Task Planning Discussion",
      "message_count": 15,
      "last_message_preview": "Can you help me create a task for...",
      "created_at": "2026-01-05T10:00:00Z",
      "updated_at": "2026-01-05T14:30:00Z"
    },
    {
      "id": "b8e2305b-5313-52e0-c773-9fbcdf038847",
      "name": "Grocery Shopping",
      "message_count": 8,
      "last_message_preview": "I'll add that task for you.",
      "created_at": "2026-01-04T15:20:00Z",
      "updated_at": "2026-01-04T15:45:00Z"
    }
  ],
  "total": 12,
  "limit": 20,
  "offset": 0
}
```

**Response Schema**:
```typescript
interface ThreadListResponse {
  threads: Thread[];
  total: number;
  limit: number;
  offset: number;
}

interface Thread {
  id: string;           // UUID
  name: string | null;  // Optional thread name
  message_count: number;
  last_message_preview: string | null;
  created_at: string;   // ISO 8601 timestamp
  updated_at: string;   // ISO 8601 timestamp
}
```

**Error Responses**:

**401 Unauthorized** - Missing or invalid JWT token:
```json
{
  "error": "Authorization header is required",
  "code": "MISSING_TOKEN",
  "timestamp": "2026-01-05T10:00:00Z"
}
```

**403 Forbidden** - User ID mismatch:
```json
{
  "error": "User ID in path does not match authenticated user",
  "code": "FORBIDDEN",
  "timestamp": "2026-01-05T10:00:00Z"
}
```

**422 Unprocessable Entity** - Invalid query parameters:
```json
{
  "error": "Limit must be between 1 and 100",
  "code": "VALIDATION_ERROR",
  "timestamp": "2026-01-05T10:00:00Z"
}
```

---

### GET /api/users/{user_id}/chat/threads/{thread_id}

**Purpose**: Retrieve a specific thread with all its messages.

**Path Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| user_id | UUID | Yes | User ID (must match authenticated user) |
| thread_id | UUID | Yes | Thread ID to retrieve |

**Request Example**:
```http
GET /api/users/29fd73b8-308f-42d8-af87-b7ab3ec544a8/chat/threads/a9f3416a-4202-41f9-b662-8ebabe927736
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response 200 OK**:
```json
{
  "thread": {
    "id": "a9f3416a-4202-41f9-b662-8ebabe927736",
    "name": "Task Planning Discussion",
    "created_at": "2026-01-05T10:00:00Z",
    "updated_at": "2026-01-05T14:30:00Z"
  },
  "messages": [
    {
      "id": "c1d2e3f4-5678-90ab-cdef-1234567890ab",
      "role": "user",
      "content": "I need to buy groceries tomorrow",
      "created_at": "2026-01-05T10:00:00Z"
    },
    {
      "id": "d2e3f4g5-6789-01bc-def0-234567890abc",
      "role": "assistant",
      "content": "I'll add that task for you. What items do you need?",
      "created_at": "2026-01-05T10:00:05Z"
    },
    {
      "id": "e3f4g5h6-7890-12cd-ef01-34567890abcd",
      "role": "user",
      "content": "Milk, eggs, and bread",
      "created_at": "2026-01-05T10:00:15Z"
    }
  ]
}
```

**Response Schema**:
```typescript
interface ThreadDetailResponse {
  thread: ThreadDetail;
  messages: Message[];
}

interface ThreadDetail {
  id: string;
  name: string | null;
  created_at: string;
  updated_at: string;
}

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}
```

**Error Responses**:

**401 Unauthorized** - Missing or invalid JWT token
**403 Forbidden** - Thread doesn't belong to user
**404 Not Found** - Thread doesn't exist:
```json
{
  "error": "Thread with ID 'a9f3416a-4202-41f9-b662-8ebabe927736' not found",
  "code": "NOT_FOUND",
  "timestamp": "2026-01-05T10:00:00Z"
}
```

---

### POST /api/users/{user_id}/chat/messages

**Purpose**: Send a message to the chatbot and receive a streaming response.

**Path Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| user_id | UUID | Yes | User ID (must match authenticated user) |

**Request Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
Accept: text/event-stream
```

**Request Body**:
```json
{
  "message": "I need to buy groceries tomorrow",
  "thread_id": "a9f3416a-4202-41f9-b662-8ebabe927736"
}
```

**Request Schema**:
```typescript
interface SendMessageRequest {
  message: string;           // Required, non-empty
  thread_id?: string | null; // Optional, creates new thread if not provided
}
```

**Response 200 OK** (Server-Sent Events):
```
data: {"content": "I'll"}

data: {"content": " add"}

data: {"content": " that"}

data: {"content": " task"}

data: {"content": " for"}

data: {"content": " you."}

event: done
data: {"thread_id": "a9f3416a-4202-41f9-b662-8ebabe927736", "message_id": "d2e3f4g5-6789-01bc-def0-234567890abc"}

```

**SSE Event Types**:
| Event | Data Format | Description |
|-------|-------------|-------------|
| (default) | `{"content": "text"}` | Message content chunk |
| done | `{"thread_id": "uuid", "message_id": "uuid"}` | Stream complete with metadata |
| error | `{"error": "message"}` | Error during processing |

**Response Schema**:
```typescript
// SSE data chunks
interface ContentChunk {
  content: string;
}

interface DoneEvent {
  thread_id: string;
  message_id: string;
}

interface ErrorEvent {
  error: string;
}
```

**Error Responses**:

**400 Bad Request** - Thread limit reached:
```json
{
  "error": "Maximum thread limit (20) reached. Please delete old threads before creating new ones.",
  "code": "THREAD_LIMIT_REACHED",
  "timestamp": "2026-01-05T10:00:00Z"
}
```

**401 Unauthorized** - Missing or invalid JWT token

**403 Forbidden** - Thread doesn't belong to user:
```json
{
  "error": "Thread 'a9f3416a-4202-41f9-b662-8ebabe927736' does not belong to user",
  "code": "FORBIDDEN",
  "timestamp": "2026-01-05T10:00:00Z"
}
```

**422 Unprocessable Entity** - Invalid message:
```json
{
  "error": "Message content cannot be empty",
  "code": "VALIDATION_ERROR",
  "timestamp": "2026-01-05T10:00:00Z"
}
```

---

### DELETE /api/users/{user_id}/chat/threads/{thread_id}

**Purpose**: Delete a thread and all its associated messages.

**Path Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| user_id | UUID | Yes | User ID (must match authenticated user) |
| thread_id | UUID | Yes | Thread ID to delete |

**Request Example**:
```http
DELETE /api/users/29fd73b8-308f-42d8-af87-b7ab3ec544a8/chat/threads/a9f3416a-4202-41f9-b662-8ebabe927736
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response 200 OK**:
```json
{
  "message": "Thread deleted successfully",
  "thread_id": "a9f3416a-4202-41f9-b662-8ebabe927736",
  "deleted_messages": 15
}
```

**Response Schema**:
```typescript
interface DeleteThreadResponse {
  message: string;
  thread_id: string;
  deleted_messages: number;
}
```

**Error Responses**:

**401 Unauthorized** - Missing or invalid JWT token

**403 Forbidden** - Thread doesn't belong to user:
```json
{
  "error": "Thread 'a9f3416a-4202-41f9-b662-8ebabe927736' does not belong to user",
  "code": "FORBIDDEN",
  "timestamp": "2026-01-05T10:00:00Z"
}
```

**404 Not Found** - Thread doesn't exist:
```json
{
  "error": "Thread with ID 'a9f3416a-4202-41f9-b662-8ebabe927736' not found",
  "code": "NOT_FOUND",
  "timestamp": "2026-01-05T10:00:00Z"
}
```

---

## Common Error Response Format

All error responses follow this standard format:

```typescript
interface ErrorResponse {
  error: string;      // Human-readable error message
  code: string;       // Machine-readable error code
  timestamp: string;  // ISO 8601 timestamp
}
```

**Error Codes**:
| Code | HTTP Status | Description |
|------|-------------|-------------|
| MISSING_TOKEN | 401 | Authorization header not provided |
| INVALID_TOKEN | 401 | JWT token is invalid or expired |
| FORBIDDEN | 403 | User not authorized to access resource |
| NOT_FOUND | 404 | Requested resource doesn't exist |
| VALIDATION_ERROR | 422 | Request validation failed |
| THREAD_LIMIT_REACHED | 400 | User has reached maximum thread limit |
| DATABASE_ERROR | 500 | Internal database error (should be rare) |

---

## Rate Limiting

**Limits**:
- Thread list: 100 requests per minute per user
- Message send: 30 requests per minute per user
- Thread delete: 20 requests per minute per user

**Rate Limit Headers**:
```
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 25
X-RateLimit-Reset: 1704456000
```

**Rate Limit Exceeded Response (429)**:
```json
{
  "error": "Rate limit exceeded. Please try again in 45 seconds.",
  "code": "RATE_LIMIT_EXCEEDED",
  "timestamp": "2026-01-05T10:00:00Z",
  "retry_after": 45
}
```

---

## Security Considerations

1. **User Isolation**: All endpoints enforce user isolation by validating that the `user_id` in the path matches the authenticated user's ID from the JWT token.

2. **Input Validation**: All request bodies and query parameters are validated before processing.

3. **SQL Injection Prevention**: All database queries use parameterized statements via SQLModel ORM.

4. **XSS Prevention**: Message content is sanitized before storage and display.

5. **CORS**: Backend configured to allow requests only from trusted frontend origins.

---

**Contract Status**: Complete and ready for implementation
**Next**: Update agent context
