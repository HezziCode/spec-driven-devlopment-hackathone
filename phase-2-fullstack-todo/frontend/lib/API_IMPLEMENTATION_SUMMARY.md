# API Client Implementation Summary

## File: `/frontend/lib/api.ts`

### Overview
Centralized, production-ready API client for TaskWave Dashboard frontend. Handles all communication with FastAPI backend with automatic JWT authentication, type safety, and comprehensive logging.

### Key Features Implemented

#### 1. Configuration
- **API_BASE_URL**: Reads from `NEXT_PUBLIC_API_URL` or falls back to `NEXT_PUBLIC_API_BASE_URL` or `/api`
- **Development mode detection**: Enables/disables logging based on `NODE_ENV`

#### 2. Logging Utilities (Development Only)
- **logRequest()**: Logs HTTP method, URL, headers, and request body
- **logResponse()**: Logs HTTP method, URL, status code, and response data
- **logError()**: Logs errors with message and stack trace
- All logging is automatically disabled in production

#### 3. Query String Helper
- **buildQueryString()**: Converts parameter objects to URL query strings
  - Properly encodes special characters
  - Filters out undefined, null, and empty values
  - Returns empty string if no parameters provided

#### 4. Core API Request Function
- **apiRequest<T>()**: Generic async function with full type safety
  - Automatically attaches JWT token via `getAuthToken()`
  - Sets Content-Type: application/json header
  - Handles error responses gracefully
  - Supports both JSON and empty responses
  - Throws descriptive errors with status codes and error data
  - Logs all requests/responses in development mode

#### 5. Authentication Endpoints (authApi)
```typescript
authApi.signup(data: SignupRequest): Promise<AuthResponse>
authApi.login(data: LoginRequest): Promise<AuthResponse>
authApi.logout(): Promise<{ message: string }>
```

- **POST /auth/signup**: Register new user
- **POST /auth/login**: Authenticate and get JWT token
- **POST /auth/logout**: Invalidate session

#### 6. Task Management Endpoints (taskApi)
```typescript
taskApi.getTasks(userId: string, params?: TaskQueryParams): Promise<TaskListResponse>
taskApi.getTask(userId: string, taskId: string): Promise<TaskResponse>
taskApi.createTask(userId: string, data: CreateTaskRequest): Promise<TaskResponse>
taskApi.updateTask(userId: string, taskId: string, data: UpdateTaskRequest): Promise<TaskResponse>
taskApi.patchTask(userId: string, taskId: string, data: PatchTaskRequest): Promise<TaskResponse>
taskApi.deleteTask(userId: string, taskId: string): Promise<{ message: string }>
```

- **GET /users/{user_id}/tasks**: List tasks with filtering/pagination
- **POST /users/{user_id}/tasks**: Create new task
- **GET /users/{user_id}/tasks/{task_id}**: Get single task
- **PUT /users/{user_id}/tasks/{task_id}**: Full replace (all fields required)
- **PATCH /users/{user_id}/tasks/{task_id}**: Partial update (any subset of fields)
- **DELETE /users/{user_id}/tasks/{task_id}**: Delete task

#### 7. User Profile Endpoints (userApi)
```typescript
userApi.getProfile(userId: string): Promise<UserResponse>
userApi.updateProfile(userId: string, data: UpdateUserRequest): Promise<UserResponse>
```

- **GET /users/{user_id}**: Get user profile
- **PUT /users/{user_id}**: Update profile (username, email)

### Type Imports

All types imported from `@/types/api`:

```typescript
TaskResponse              // Single task from API
TaskListResponse          // Paginated task list
CreateTaskRequest         // Create task payload
UpdateTaskRequest         // Full task update payload (PUT)
PatchTaskRequest          // Partial task update payload (PATCH)
AuthResponse              // Login/signup response
User                      // User data from auth
UserResponse              // User profile response
LoginRequest              // Login payload
SignupRequest             // Signup payload
UpdateUserRequest         // Profile update payload
TaskQueryParams           // Query filter options
```

### Authentication Flow

1. User logs in via `authApi.login()`
2. Backend returns JWT token in response
3. Frontend stores token (via Better Auth session storage)
4. `apiRequest()` retrieves token via `getAuthToken()`
5. Token attached to all subsequent requests as `Authorization: Bearer {token}`
6. Backend validates token and enforces user isolation via user_id in path

### Error Handling

Error objects thrown by `apiRequest()` include:

```typescript
{
  message: string;        // User-friendly error message
  status?: number;        // HTTP status code
  data?: any;            // Full error response from API
}
```

Errors can be caught and handled:
```typescript
try {
  await taskApi.getTasks(userId);
} catch (error: any) {
  console.error('Status:', error.status);
  console.error('Message:', error.message);
  console.error('Data:', error.data);
}
```

### Query Parameters Support

`getTasks()` supports advanced filtering via TaskQueryParams:

- `limit`: Results per page (default 20, max 100)
- `offset`: Pagination offset
- `completed`: Filter by completion status
- `priority`: Filter by priority level
- `tag`: Filter by tag name
- `search`: Search title/description
- `sort`: Sort by created|title|priority|updated

Example:
```typescript
const tasks = await taskApi.getTasks(userId, {
  limit: 50,
  priority: 'high',
  search: 'urgent',
  sort: 'created'
});
```

### Exports

**Named exports:**
- `authApi`: Authentication endpoints
- `taskApi`: Task management endpoints
- `userApi`: User profile endpoints
- `buildQueryString`: Query string helper
- `logRequest`: Request logger (development only)
- `logResponse`: Response logger (development only)
- `logError`: Error logger (development only)

**Default export:** Object containing all the above

### Dependencies

- `@/types/api`: Type definitions matching backend FastAPI schemas
- `./auth`: `getAuthToken()` function for JWT retrieval
- Native Fetch API (no external HTTP library needed)

### Browser Compatibility

- Uses standard Fetch API (available in all modern browsers)
- TypeScript generics for type safety
- No dependencies on axios, node-fetch, or other HTTP libraries

### Development vs Production

**Development mode** (`NODE_ENV === 'development'`):
- Logs all API requests with method, URL, headers, body
- Logs all responses with status code and data
- Logs all errors with stack traces
- Prefixed with `[API]` for easy filtering

**Production mode**:
- All logging disabled
- Minimal console output
- Optimized for performance

### Error Response Formats Handled

1. **JSON error response** (API returns error object):
   - Extracts error message from `error`, `message`, or `detail` field

2. **Non-JSON error response**:
   - Uses HTTP status text as fallback

3. **Network errors**:
   - Wrapped with descriptive message

### Best Practices Implemented

1. **Single Responsibility**: Each function has one clear purpose
2. **Type Safety**: No `any` types except for legitimate use cases
3. **Error Handling**: Graceful error parsing and meaningful messages
4. **Documentation**: Comprehensive JSDoc comments on all functions
5. **Separation of Concerns**: Logging, authentication, and requests handled separately
6. **No Secrets in Code**: JWT token retrieved at request time from secure storage
7. **Testability**: Pure functions with no external dependencies (except auth)
8. **Performance**: Lazy token retrieval, efficient query string building

### Future Enhancements

Potential additions without breaking changes:

1. Retry logic for failed requests
2. Request timeout configuration
3. Automatic token refresh before expiration
4. Request/response interceptors
5. Caching layer integration
6. Rate limiting detection
7. Batch request support
8. File upload endpoints

### Testing Considerations

All functions are testable:

```typescript
// Mock example
jest.mock('@/lib/auth', () => ({
  getAuthToken: jest.fn(() => 'mock-token')
}));

// Can test individual functions
// Can mock fetch responses
// Can verify correct endpoints are called
// Can validate query string building
```

## Related Files

- `/frontend/types/api.ts`: Type definitions
- `/frontend/lib/auth.ts`: Authentication utilities
- `/frontend/lib/errors.ts`: Error handling utilities
- `/specs/api/rest-endpoints.md`: API specification

## Implementation Status

✓ All required endpoints implemented
✓ JWT authentication integrated
✓ Type safety achieved
✓ Development logging utilities included
✓ Query string builder implemented
✓ Error handling robust
✓ Documentation complete
✓ No external HTTP dependencies
✓ Production-ready code quality
