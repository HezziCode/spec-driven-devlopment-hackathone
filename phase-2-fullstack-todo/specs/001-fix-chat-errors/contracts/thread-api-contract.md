# API Contract: Chat Thread Operations

**Feature**: Fix Chat Thread and API Key Errors
**Date**: 2026-01-13
**Version**: 1.0

## Overview

This contract defines the API endpoints for chat thread operations, specifically addressing the 404 error issues and ensuring proper thread synchronization between creation and access.

## Base URL

```
https://api.example.com/api/v1
```

All endpoints require authentication via JWT token in the Authorization header:

```
Authorization: Bearer <jwt_token>
```

## Common Error Responses

All endpoints follow the standard error response format:

```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "timestamp": "ISO 8601 timestamp"
}
```

## Endpoints

### GET /users/{user_id}/chat/threads

Retrieve all chat threads for the authenticated user.

**Authentication**: JWT required (verified against user_id in path)

**Path Parameters**:
- `user_id` (string, required): UUID of the user (must match authenticated user)

**Query Parameters**:
- `limit` (integer, optional): Number of threads to return (default: 50, max: 100)
- `offset` (integer, optional): Number of threads to skip for pagination (default: 0)

**Success Response**:
- `200 OK`
```json
{
  "threads": [
    {
      "id": "string",
      "name": "string",
      "last_message_preview": "string",
      "message_count": "integer",
      "created_at": "ISO 8601 datetime",
      "updated_at": "ISO 8601 datetime"
    }
  ],
  "total": "integer"
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or missing JWT token
- `403 Forbidden`: User_id in path doesn't match authenticated user
- `404 Not Found`: User doesn't exist

### GET /users/{user_id}/chat/threads/{thread_id}

Retrieve a specific chat thread with all its messages.

**Authentication**: JWT required (verified against user_id in path)

**Path Parameters**:
- `user_id` (string, required): UUID of the user (must match authenticated user)
- `thread_id` (string, required): UUID of the thread to retrieve

**Success Response**:
- `200 OK`
```json
{
  "id": "string",
  "name": "string",
  "user_id": "string",
  "created_at": "ISO 8601 datetime",
  "updated_at": "ISO 8601 datetime",
  "message_count": "integer",
  "last_message_preview": "string",
  "messages": [
    {
      "id": "string",
      "role": "string",
      "content": "string",
      "created_at": "ISO 8601 datetime"
    }
  ]
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or missing JWT token
- `403 Forbidden`: User_id in path doesn't match authenticated user or thread doesn't belong to user
- `404 Not Found`: Thread doesn't exist or user doesn't exist

### POST /users/{user_id}/chat/messages

Send a message to a chat thread (creates new thread if thread_id not provided).

**Authentication**: JWT required (verified against user_id in path)

**Path Parameters**:
- `user_id` (string, required): UUID of the user (must match authenticated user)

**Request Body**:
```json
{
  "message": "string",
  "thread_id": "string" (optional)
}
```

**Success Response**:
- `201 Created`
```json
{
  "thread_id": "string",
  "message": {
    "id": "string",
    "role": "string",
    "content": "string",
    "created_at": "ISO 8601 datetime"
  },
  "response_stream": "boolean"
}
```

The response includes a Server-Sent Events (SSE) stream for the AI assistant's response.

**SSE Event Types**:
- `thread_created`: Emitted when a new thread is created
  ```json
  {
    "event": "thread_created",
    "data": "{\"threadId\":\"string\"}"
  }
  ```
- `text_delta`: Emitted for each token of the AI response
  ```json
  {
    "event": "text_delta",
    "data": "{\"content\":\"string\"}"
  }
  ```
- `error`: Emitted when an error occurs
  ```json
  {
    "event": "error",
    "data": "Error message"
  }
  ```
- `done`: Emitted when response is complete
  ```json
  {
    "event": "done",
    "data": "{\"thread_id\":\"string\", \"message_id\":\"string\"}"
  }
  ```

**Error Responses**:
- `400 Bad Request`: Invalid request body
- `401 Unauthorized`: Invalid or missing JWT token
- `403 Forbidden`: User_id in path doesn't match authenticated user or thread doesn't belong to user
- `404 Not Found`: Thread doesn't exist (if thread_id provided)
- `422 Unprocessable Entity`: Message content validation failed

### DELETE /users/{user_id}/chat/threads/{thread_id}

Delete a specific chat thread.

**Authentication**: JWT required (verified against user_id in path)

**Path Parameters**:
- `user_id` (string, required): UUID of the user (must match authenticated user)
- `thread_id` (string, required): UUID of the thread to delete

**Success Response**:
- `200 OK`
```json
{
  "message": "Thread deleted successfully",
  "thread_id": "string"
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or missing JWT token
- `403 Forbidden`: User_id in path doesn't match authenticated user or thread doesn't belong to user
- `404 Not Found`: Thread doesn't exist

## Error Handling Specifications

### 404 Not Found Error Prevention
To prevent 404 errors when accessing newly created threads:

1. **Thread Creation Commit**: After creating a thread in the database, ensure the transaction is committed with `session.commit()`
2. **Session Synchronization**: Use `session.expire_all()` to ensure the new thread is visible to subsequent queries
3. **Small Delay**: Add a small delay (100ms) after thread creation to allow for database propagation before signaling completion
4. **Retry Logic**: Implement client-side retry mechanism with exponential backoff for temporary unavailability

### SSE Connection Stability
To ensure stable Server-Sent Events connections:

1. **Proper Headers**: Set appropriate headers for SSE (`Content-Type: text/event-stream`, `Cache-Control: no-cache`)
2. **Error Handling**: Emit proper error events when API authentication or other errors occur
3. **Connection Management**: Implement proper connection lifecycle management with connect/disconnect events
4. **Event Formatting**: Ensure all SSE events follow proper format with `event:` and `data:` fields

## Security Considerations

1. **User Isolation**: All endpoints verify that the authenticated user matches the user_id in the path
2. **Thread Ownership**: Users can only access threads that belong to them
3. **API Key Security**: OpenAI API keys are stored securely and not exposed in client-side code
4. **Rate Limiting**: Implement rate limiting to prevent abuse of chat endpoints
5. **Input Validation**: All inputs are validated to prevent injection attacks

## Performance Requirements

1. **Response Times**:
   - GET requests: < 500ms for 95th percentile
   - POST requests: < 1000ms for 95th percentile (including AI response time)
2. **Concurrent Connections**: Support at least 100 concurrent SSE connections per user
3. **Database Queries**: Optimize queries with proper indexing for thread/message retrieval
4. **Caching**: Consider caching for frequently accessed thread metadata

## Validation Rules

1. **Path Parameter Validation**: Verify UUID format for user_id and thread_id
2. **Authorization Validation**: Ensure JWT token is valid and matches user_id
3. **Ownership Validation**: Verify thread belongs to the specified user
4. **Input Validation**: Validate message content length and format
5. **Rate Limit Validation**: Implement appropriate rate limiting per user