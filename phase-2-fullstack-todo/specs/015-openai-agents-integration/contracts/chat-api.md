# API Contract: Chat Endpoint

**Feature**: 015-openai-agents-integration
**Version**: 1.0.0
**Date**: 2025-12-30

## Endpoint

```
POST /api/users/{user_id}/chat
```

## Authentication

- **Required**: JWT Bearer token in `Authorization` header
- **Validation**: `user_id` in path must match authenticated user from JWT

## Request

### Headers

| Header | Required | Description |
|--------|----------|-------------|
| Authorization | Yes | `Bearer <jwt_token>` |
| Content-Type | Yes | `application/json` |

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string (UUID) | Yes | User's unique identifier |

### Request Body

```json
{
  "conversation_id": "uuid-string",  // optional
  "message": "string"                // required, 1-4000 chars
}
```

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| conversation_id | string | No | Valid UUID | Existing conversation ID. Creates new conversation if not provided. |
| message | string | Yes | 1-4000 characters | User's natural language message |

### Example Request

```bash
curl -X POST "http://localhost:8000/api/users/123e4567-e89b-12d3-a456-426614174000/chat" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add a task to buy groceries"
  }'
```

## Response

### Success Response (200 OK)

```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "Done! I've added 'Buy groceries' to your tasks.",
  "tool_calls": [
    {
      "tool_name": "create_task",
      "arguments": {
        "title": "Buy groceries",
        "description": ""
      },
      "result": {
        "task_id": "660e8400-e29b-41d4-a716-446655440001",
        "status": "created",
        "title": "Buy groceries"
      }
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| conversation_id | string | UUID of the conversation |
| response | string | AI assistant's natural language response |
| tool_calls | array | List of MCP tools invoked during this request |

### Tool Call Object

| Field | Type | Description |
|-------|------|-------------|
| tool_name | string | Name of the tool called (e.g., "create_task", "list_tasks") |
| arguments | object | Arguments passed to the tool |
| result | object | Result returned by the tool |

## Error Responses

### 400 Bad Request

```json
{
  "error": "Message is required",
  "code": "VALIDATION_ERROR",
  "timestamp": "2025-12-30T12:00:00Z"
}
```

### 401 Unauthorized

```json
{
  "error": "Missing or invalid JWT token",
  "code": "UNAUTHORIZED",
  "timestamp": "2025-12-30T12:00:00Z"
}
```

### 403 Forbidden

```json
{
  "error": "User ID in path does not match authenticated user",
  "code": "FORBIDDEN",
  "timestamp": "2025-12-30T12:00:00Z"
}
```

### 404 Not Found

```json
{
  "error": "Conversation not found",
  "code": "NOT_FOUND",
  "timestamp": "2025-12-30T12:00:00Z"
}
```

### 422 Unprocessable Entity

```json
{
  "error": "Message must be between 1 and 4000 characters",
  "code": "VALIDATION_ERROR",
  "timestamp": "2025-12-30T12:00:00Z"
}
```

### 500 Internal Server Error

```json
{
  "error": "An unexpected error occurred",
  "code": "INTERNAL_ERROR",
  "timestamp": "2025-12-30T12:00:00Z"
}
```

### 503 Service Unavailable

```json
{
  "error": "AI service temporarily unavailable",
  "code": "AI_SERVICE_ERROR",
  "timestamp": "2025-12-30T12:00:00Z"
}
```

## Available Tools

The agent can invoke the following MCP tools:

| Tool | Description | When Used |
|------|-------------|-----------|
| `create_task` | Create a new task | User mentions adding/creating something |
| `list_tasks` | List user's tasks | User asks to see/show tasks |
| `mark_complete` | Mark task as completed | User says done/finished |
| `update_task` | Update task details | User wants to change/update |
| `delete_task` | Delete a task | User says remove/delete |
| `search_tasks` | Search tasks by keyword | User searches for specific task |

## Conversation Flow Examples

### Example 1: Create Task

**Request:**
```json
{
  "message": "I need to buy groceries this weekend"
}
```

**Response:**
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "Got it! I've added 'Buy groceries' to your tasks for this weekend.",
  "tool_calls": [
    {
      "tool_name": "create_task",
      "arguments": {"title": "Buy groceries", "description": ""},
      "result": {"task_id": "...", "status": "created", "title": "Buy groceries"}
    }
  ]
}
```

### Example 2: List Tasks

**Request:**
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "What do I have to do?"
}
```

**Response:**
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "You have 3 pending tasks:\n1. Buy groceries\n2. Call mom\n3. Finish report",
  "tool_calls": [
    {
      "tool_name": "list_tasks",
      "arguments": {"status": "pending"},
      "result": {"tasks": [...], "total": 3}
    }
  ]
}
```

### Example 3: Complete Task

**Request:**
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "I finished buying groceries"
}
```

**Response:**
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "Great job! I've marked 'Buy groceries' as complete. ✓",
  "tool_calls": [
    {
      "tool_name": "search_tasks",
      "arguments": {"query": "groceries"},
      "result": {"tasks": [...], "total": 1}
    },
    {
      "tool_name": "mark_complete",
      "arguments": {"task_id": "..."},
      "result": {"task_id": "...", "status": "completed", "title": "Buy groceries"}
    }
  ]
}
```

## Rate Limiting

| Limit | Value |
|-------|-------|
| Requests per minute | 60 |
| Messages per conversation | 100 |
| Max concurrent conversations | 10 |

## Performance Requirements

| Metric | Target |
|--------|--------|
| Response time (p95) | < 3 seconds |
| Response time (p50) | < 1.5 seconds |
| Error rate | < 1% |
