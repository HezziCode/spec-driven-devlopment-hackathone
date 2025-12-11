# REST API Endpoints Specification

## Overview
This document defines the REST API endpoints for the Phase 2 full-stack todo web application. All endpoints require JWT authentication and enforce user isolation to ensure users can only access their own data.

## Authentication
All API endpoints (except authentication endpoints) require a valid JWT token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

The JWT token contains user identity information that is used to enforce user isolation.

## Base URL
```
https://api.example.com/api/v1
```

## Error Response Format
All error responses follow this format:
```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "timestamp": "ISO 8601 timestamp"
}
```

## Endpoints

### Authentication Endpoints

#### POST /auth/signup
Create a new user account
- **Request**: `{"username": "string", "email": "string", "password": "string"}`
- **Response**: `{"user": {"id": "string", "username": "string", "email": "string"}, "token": "string"}`
- **Success**: 201 Created
- **Errors**: 400 Bad Request, 409 Conflict

#### POST /auth/login
Authenticate user and return JWT token
- **Request**: `{"email": "string", "password": "string"}`
- **Response**: `{"user": {"id": "string", "username": "string", "email": "string"}, "token": "string"}`
- **Success**: 200 OK
- **Errors**: 400 Bad Request, 401 Unauthorized

#### POST /auth/logout
Invalidate user session
- **Request**: (Empty body)
- **Response**: `{"message": "Successfully logged out"}`
- **Success**: 200 OK
- **Errors**: 401 Unauthorized

### Task Endpoints

#### GET /users/{user_id}/tasks
Retrieve all tasks for the authenticated user
- **Path Parameters**: `user_id` (must match authenticated user)
- **Query Parameters**:
  - `limit` (default: 20, max: 100)
  - `offset` (default: 0)
  - `status` (optional: "completed", "pending")
  - `priority` (optional: "low", "medium", "high", "critical")
  - `tag` (optional: tag name to filter by)
  - `search` (optional: search term for title/description)
- **Response**: `{"tasks": [{"id": "string", "title": "string", "description": "string", "completed": "boolean", "priority": "string", "tags": ["string"], "created_at": "ISO 8601", "updated_at": "ISO 8601"}], "total": "number"}`
- **Success**: 200 OK
- **Errors**: 401 Unauthorized, 403 Forbidden, 404 Not Found

#### POST /users/{user_id}/tasks
Create a new task for the authenticated user
- **Path Parameters**: `user_id` (must match authenticated user)
- **Request**: `{"title": "string", "description": "string", "priority": "string", "tags": ["string"]}`
- **Response**: `{"id": "string", "title": "string", "description": "string", "completed": "boolean", "priority": "string", "tags": ["string"], "user_id": "string", "created_at": "ISO 8601", "updated_at": "ISO 8601"}`
- **Success**: 201 Created
- **Errors**: 400 Bad Request, 401 Unauthorized, 403 Forbidden, 422 Unprocessable Entity

#### GET /users/{user_id}/tasks/{task_id}
Retrieve a specific task for the authenticated user
- **Path Parameters**: `user_id` (must match authenticated user), `task_id`
- **Response**: `{"id": "string", "title": "string", "description": "string", "completed": "boolean", "priority": "string", "tags": ["string"], "user_id": "string", "created_at": "ISO 8601", "updated_at": "ISO 8601"}`
- **Success**: 200 OK
- **Errors**: 401 Unauthorized, 403 Forbidden, 404 Not Found

#### PUT /users/{user_id}/tasks/{task_id}
Update an existing task for the authenticated user
- **Path Parameters**: `user_id` (must match authenticated user), `task_id`
- **Request**: `{"title": "string", "description": "string", "completed": "boolean", "priority": "string", "tags": ["string"]}`
- **Response**: `{"id": "string", "title": "string", "description": "string", "completed": "boolean", "priority": "string", "tags": ["string"], "user_id": "string", "created_at": "ISO 8601", "updated_at": "ISO 8601"}`
- **Success**: 200 OK
- **Errors**: 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 422 Unprocessable Entity

#### PATCH /users/{user_id}/tasks/{task_id}
Partially update an existing task for the authenticated user
- **Path Parameters**: `user_id` (must match authenticated user), `task_id`
- **Request**: Any subset of task fields
- **Response**: `{"id": "string", "title": "string", "description": "string", "completed": "boolean", "priority": "string", "tags": ["string"], "user_id": "string", "created_at": "ISO 8601", "updated_at": "ISO 8601"}`
- **Success**: 200 OK
- **Errors**: 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 422 Unprocessable Entity

#### DELETE /users/{user_id}/tasks/{task_id}
Delete a specific task for the authenticated user
- **Path Parameters**: `user_id` (must match authenticated user), `task_id`
- **Response**: `{"message": "Task deleted successfully"}`
- **Success**: 200 OK
- **Errors**: 401 Unauthorized, 403 Forbidden, 404 Not Found

### User Endpoints

#### GET /users/{user_id}
Retrieve user profile information
- **Path Parameters**: `user_id` (must match authenticated user)
- **Response**: `{"id": "string", "username": "string", "email": "string", "created_at": "ISO 8601", "updated_at": "ISO 8601"}`
- **Success**: 200 OK
- **Errors**: 401 Unauthorized, 403 Forbidden, 404 Not Found

#### PUT /users/{user_id}
Update user profile information
- **Path Parameters**: `user_id` (must match authenticated user)
- **Request**: `{"username": "string", "email": "string"}`
- **Response**: `{"id": "string", "username": "string", "email": "string", "updated_at": "ISO 8601"}`
- **Success**: 200 OK
- **Errors**: 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 422 Unprocessable Entity

## Security Considerations
- All endpoints (except auth) require valid JWT token
- User ID in path must match authenticated user's ID
- No cross-user access is permitted
- Rate limiting should be implemented to prevent abuse
- Input validation must be performed on all requests
- Sensitive data should be properly sanitized before response

## Performance Requirements
- API responses should return within 200ms for 95th percentile
- Support for pagination with configurable page sizes
- Efficient database queries with proper indexing
- Caching mechanisms for frequently accessed data (if needed)