# API Contract: Thread Management for 404 Error Resolution

## Overview

This contract defines the API endpoints and behaviors needed to resolve the "Thread not found" and 404 errors in the chat functionality.

## Endpoints

### GET /api/users/{user_id}/chat/threads/{thread_id}

**Purpose**: Retrieve a specific thread with all its messages

**Request**:
- Method: GET
- Path: `/api/users/{user_id}/chat/threads/{thread_id}`
- Headers:
  - Authorization: Bearer {token}
- Parameters:
  - user_id: UUID of the authenticated user
  - thread_id: String ID of the thread to retrieve

**Success Response (200)**:
```json
{
  "id": "string",
  "name": "string",
  "user_id": "string",
  "created_at": "ISO 8601 timestamp",
  "updated_at": "ISO 8601 timestamp",
  "message_count": "number",
  "last_message_preview": "string | null",
  "messages": [
    {
      "id": "string",
      "role": "string",
      "content": "string",
      "created_at": "ISO 8601 timestamp"
    }
  ]
}
```

**Error Responses**:
- 401: Unauthorized (invalid or missing token)
- 403: Forbidden (user doesn't own the thread)
- 404: Thread not found (thread doesn't exist or isn't accessible)

**Behavior Changes for 404 Resolution**:
- Enhanced validation to ensure thread exists before attempting retrieval
- Improved error messaging for debugging timing issues
- Proper transaction handling to ensure thread is committed before access

### POST /api/users/{user_id}/chat/messages

**Purpose**: Send a message and create/stream response, handling new thread creation

**Request**:
- Method: POST
- Path: `/api/users/{user_id}/chat/messages`
- Headers:
  - Authorization: Bearer {token}
  - Content-Type: application/json
- Body:
```json
{
  "thread_id": "string | null",
  "message": "string"
}
```

**Response**: Server-Sent Events (text/event-stream) with thread_id in completion event

**Behavior Changes for 404 Resolution**:
- Ensure thread is fully committed to database before sending thread_id in completion event
- Proper session management between thread creation and message saving
- Validation that thread exists before sending ID to frontend

## Error Handling Contract

### 404 Error Scenarios
1. **Thread not found**: Thread ID doesn't exist in database
2. **User not authorized**: User doesn't own the thread
3. **Timing issue**: Thread created but not yet committed to database

### Error Response Format
```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "timestamp": "ISO 8601 timestamp"
}
```

## Synchronization Requirements

### Thread Creation Sequence
1. Backend creates thread in database with session.commit()
2. Backend validates thread exists in database
3. Backend sends thread_id in SSE completion event only after validation
4. Frontend receives thread_id and waits before attempting to load thread
5. Frontend implements retry mechanism for temporary unavailability

### Frontend Retry Contract
- Initial delay of 100ms before first load attempt
- Up to 3 retry attempts with exponential backoff (100ms, 200ms, 400ms)
- Proper error handling without clearing UI state