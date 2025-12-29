# TaskWave API Client Guide

## Overview

The centralized API client in `lib/api.ts` provides a complete, type-safe interface for communicating with the FastAPI backend. It includes:

- **JWT Authentication**: Automatic token attachment to all authenticated requests
- **Query String Building**: Helper function for clean URL parameter encoding
- **Development Logging**: Structured logging utilities for debugging
- **Type Safety**: Full TypeScript support with types from `@/types/api`
- **Error Handling**: Consistent error parsing and response handling

## Configuration

The API client reads the base URL from environment variables:

```bash
NEXT_PUBLIC_API_URL      # Primary environment variable (recommended)
NEXT_PUBLIC_API_BASE_URL # Fallback for backward compatibility
```

Default: `/api` (relative URL for same-origin requests)

## Usage Examples

### Authentication

```typescript
import { authApi } from '@/lib/api';

// Sign up new user
const { user, token } = await authApi.signup({
  username: 'john_doe',
  email: 'john@example.com',
  password: 'securePassword123'
});

// Login
const response = await authApi.login({
  email: 'john@example.com',
  password: 'securePassword123'
});

// Logout
await authApi.logout();
```

### Task Management

```typescript
import { taskApi } from '@/lib/api';
import { getCurrentUserId } from '@/lib/auth';

const userId = getCurrentUserId();

// Get all tasks with filtering
const tasks = await taskApi.getTasks(userId, {
  limit: 20,
  offset: 0,
  status: 'pending',
  priority: 'high',
  search: 'urgent',
  sort: 'created'
});

// Get single task
const task = await taskApi.getTask(userId, 'task-id-123');

// Create task
const newTask = await taskApi.createTask(userId, {
  title: 'New Task',
  description: 'Task description',
  priority: 'high',
  tags: ['important', 'work']
});

// Full update (PUT) - requires all fields
const updated = await taskApi.updateTask(userId, 'task-id-123', {
  title: 'Updated Task',
  description: 'Updated description',
  completed: false,
  priority: 'medium',
  tags: ['work']
});

// Partial update (PATCH) - only provided fields are updated
const patched = await taskApi.patchTask(userId, 'task-id-123', {
  completed: true
  // Only 'completed' is updated, other fields remain unchanged
});

// Delete task
await taskApi.deleteTask(userId, 'task-id-123');
```

### User Profile

```typescript
import { userApi } from '@/lib/api';
import { getCurrentUserId } from '@/lib/auth';

const userId = getCurrentUserId();

// Get profile
const profile = await userApi.getProfile(userId);

// Update profile
const updated = await userApi.updateProfile(userId, {
  username: 'new_username',
  email: 'newemail@example.com'
});
```

## Query Parameters

The `getTasks` endpoint supports the following query parameters:

```typescript
interface TaskQueryParams {
  limit?: number;      // Results per page (default: 20, max: 100)
  offset?: number;     // Pagination offset (default: 0)
  completed?: boolean; // Filter by completion status
  priority?: 'low' | 'medium' | 'high' | 'critical';
  tag?: string;        // Filter by tag name
  search?: string;     // Search in title/description
  sort?: 'created' | 'title' | 'priority' | 'updated';
}
```

Example:
```typescript
const tasks = await taskApi.getTasks(userId, {
  limit: 50,
  offset: 100,
  priority: 'high',
  search: 'bug fix',
  sort: 'created'
});
```

## Error Handling

The API client throws errors with additional properties for detailed error information:

```typescript
try {
  await taskApi.createTask(userId, {
    title: '',
    description: '',
    priority: 'invalid',
    tags: []
  });
} catch (error: any) {
  console.error('Status:', error.status);      // HTTP status code
  console.error('Message:', error.message);    // Error message
  console.error('Data:', error.data);          // Full error response from API
}
```

## Development Logging

In development mode (`NODE_ENV === 'development'`), the API client automatically logs:

- **Request logs**: Method, URL, headers, and request body
- **Response logs**: Method, URL, status code, and response data
- **Error logs**: Full error details including stack trace

Example output:
```
[API] POST /auth/login { headers: {...}, body: {...} }
[API] POST /auth/login 200 { user: {...}, token: '...' }
```

These logs are automatically disabled in production.

## Helper Functions

### buildQueryString

Converts a parameters object to a properly encoded query string:

```typescript
import { buildQueryString } from '@/lib/api';

const qs = buildQueryString({
  limit: 20,
  search: 'my task',
  priority: 'high'
});
// Result: "?limit=20&search=my+task&priority=high"
```

Filters out undefined, null, and empty string values.

### logRequest, logResponse, logError

Development logging utilities (only active in development mode):

```typescript
import { logRequest, logResponse, logError } from '@/lib/api';

logRequest('GET', '/api/users/123/tasks', config);
logResponse('GET', '/api/users/123/tasks', 200, data);
logError('GET', '/api/users/123/tasks', error);
```

## Type Safety

All API functions are fully typed with TypeScript. Types are imported from `@/types/api`:

```typescript
import type {
  TaskResponse,
  TaskListResponse,
  CreateTaskRequest,
  UpdateTaskRequest,
  AuthResponse,
  User,
  UserResponse,
  LoginRequest,
  SignupRequest,
  UpdateUserRequest,
  TaskQueryParams,
} from '@/types/api';
```

## JWT Token Management

The API client automatically attaches the JWT token to all authenticated requests using the `getAuthToken()` function from `lib/auth.ts`.

Token is attached as:
```
Authorization: Bearer {token}
```

The token is retrieved from browser storage (localStorage or cookies) and validated before attachment.

## Best Practices

1. **Always use getCurrentUserId()** to get the authenticated user's ID before making API calls
2. **Handle errors gracefully** - all endpoints can throw errors on network failures or API errors
3. **Use PATCH for partial updates** - only update fields that changed for better performance
4. **Respect pagination** - use limit/offset for large datasets
5. **Cache results** - consider using React Query or SWR for automatic caching and revalidation

## API Response Format

All successful responses return the data directly:

```typescript
// Task response
{
  id: "uuid-123",
  title: "Task Title",
  description: "Description",
  completed: false,
  priority: "high",
  tags: ["tag1", "tag2"],
  user_id: "uuid-456",
  created_at: "2024-01-01T00:00:00Z",
  updated_at: "2024-01-01T00:00:00Z"
}

// Task list response
{
  tasks: [...],
  total: 42,
  page: 1,
  limit: 20
}

// Authentication response
{
  user: { id, username, email },
  token: "jwt-token-string"
}
```

## Environment Setup

Required environment variables in `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

For production, update to your production API URL.
