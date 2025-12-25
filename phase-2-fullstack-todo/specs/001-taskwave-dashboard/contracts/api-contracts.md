# API Contracts: TaskWave Dashboard

## Authentication

All endpoints except authentication endpoints require a valid JWT token in the Authorization header:

```
Authorization: Bearer <jwt_token>
```

## GET /api/{user_id}/tasks

Retrieve all tasks for the authenticated user

### Query Parameters
- `limit` (optional): number - Maximum number of tasks to return (default: 20, max: 100)
- `offset` (optional): number - Number of tasks to skip (default: 0)
- `status` (optional): string - Filter by status ("completed", "pending")
- `priority` (optional): string - Filter by priority ("high", "medium", "low")
- `tag` (optional): string - Filter by tag name
- `search` (optional): string - Search term for title/description

### Response (200 OK)
```json
{
  "tasks": [
    {
      "id": "string",
      "title": "string",
      "description": "string",
      "completed": "boolean",
      "priority": "string",
      "tags": ["string"],
      "user_id": "string",
      "created_at": "ISO 8601",
      "updated_at": "ISO 8601"
    }
  ],
  "total": "number"
}
```

## POST /api/{user_id}/tasks

Create a new task for the authenticated user

### Request Body
```json
{
  "title": "string",
  "description": "string",
  "priority": "string",
  "tags": ["string"]
}
```

### Response (201 Created)
```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "completed": "boolean",
  "priority": "string",
  "tags": ["string"],
  "user_id": "string",
  "created_at": "ISO 8601",
  "updated_at": "ISO 8601"
}
```

## GET /api/{user_id}/tasks/{task_id}

Retrieve a specific task for the authenticated user

### Response (200 OK)
```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "completed": "boolean",
  "priority": "string",
  "tags": ["string"],
  "user_id": "string",
  "created_at": "ISO 8601",
  "updated_at": "ISO 8601"
}
```

## PUT /api/{user_id}/tasks/{task_id}

Update an existing task for the authenticated user

### Request Body
```json
{
  "title": "string",
  "description": "string",
  "completed": "boolean",
  "priority": "string",
  "tags": ["string"]
}
```

### Response (200 OK)
```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "completed": "boolean",
  "priority": "string",
  "tags": ["string"],
  "user_id": "string",
  "created_at": "ISO 8601",
  "updated_at": "ISO 8601"
}
```

## PATCH /api/{user_id}/tasks/{task_id}

Partially update an existing task for the authenticated user

### Request Body (any subset of task fields)
```json
{
  "completed": "boolean"
}
```

### Response (200 OK)
```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "completed": "boolean",
  "priority": "string",
  "tags": ["string"],
  "user_id": "string",
  "created_at": "ISO 8601",
  "updated_at": "ISO 8601"
}
```

## DELETE /api/{user_id}/tasks/{task_id}

Delete a specific task for the authenticated user

### Response (200 OK)
```json
{
  "message": "Task deleted successfully"
}
```

## GET /api/{user_id}/streak

Retrieve the user's completion streak information

### Response (200 OK)
```json
{
  "currentStreak": "number",
  "longestStreak": "number",
  "lastCompletedDate": "ISO 8601 date"
}
```