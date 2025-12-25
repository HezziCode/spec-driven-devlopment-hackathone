# Feature Specification: Task Creation and Retrieval Endpoints

**Feature ID**: 008-task-crud-endpoints
**Feature Name**: Task Creation and Retrieval Endpoints
**Version**: 1.0.0
**Status**: Implementation
**Created**: 2025-12-24
**Last Updated**: 2025-12-24

## Overview

This feature implements two critical task management endpoints - POST and GET - for the Phase 2 Full-Stack Todo Web App. These endpoints enable users to create new tasks and retrieve their task lists with advanced filtering, search, and pagination capabilities. Both endpoints enforce strict user isolation through JWT authentication to ensure data security and privacy.

## User Stories

### US-1: Create New Task
**As a** registered user
**I want to** create a new task with title, description, priority, and tags
**So that** I can organize and track my work items

**Acceptance Criteria**:
- User can create a task with a required title (1-200 characters)
- User can add an optional description (max 1000 characters)
- User can set priority level (low, medium, high, critical) with medium as default
- User can add multiple tags (max 10 tags, 50 characters each)
- Task is automatically associated with the authenticated user
- Task is created with completed=false by default
- System returns 201 Created with full task object including auto-generated ID and timestamps
- System validates user_id in path matches JWT token user_id (returns 403 if mismatch)
- System returns 422 for validation errors (title too long, too many tags, etc.)
- System returns 401 if JWT token is missing or invalid

### US-2: Retrieve Task List
**As a** registered user
**I want to** retrieve my tasks with filtering, search, and pagination options
**So that** I can efficiently find and view specific tasks

**Acceptance Criteria**:
- User can retrieve all their tasks (default limit: 20, max: 100)
- User can paginate through tasks using limit and offset parameters
- User can filter by completion status (completed/pending)
- User can filter by priority level (low, medium, high, critical)
- User can filter by tag name
- User can search across title and description fields (case-insensitive)
- System returns 200 OK with {tasks: array, total: number} response
- System validates user_id in path matches JWT token user_id (returns 403 if mismatch)
- System returns 401 if JWT token is missing or invalid
- Tasks are sorted by created_at timestamp (newest first)

### US-3: User Isolation Enforcement
**As a** platform administrator
**I want to** ensure users can only create and view their own tasks
**So that** data privacy and security are maintained

**Acceptance Criteria**:
- All requests must include valid JWT token in Authorization header
- user_id in URL path must match user_id from JWT token
- System returns 403 Forbidden if user_id mismatch detected
- System returns 401 Unauthorized if JWT token is missing or invalid
- No cross-user data access is possible under any circumstances

## Functional Requirements

### FR-1: POST /api/users/{user_id}/tasks

**Purpose**: Create a new task for the authenticated user

**Request**:
- **Method**: POST
- **Path**: `/api/users/{user_id}/tasks`
- **Headers**: `Authorization: Bearer <jwt_token>`
- **Path Parameters**:
  - `user_id` (UUID, required): Must match authenticated user's ID
- **Request Body**:
```json
{
  "title": "string (1-200 chars, required)",
  "description": "string (max 1000 chars, optional)",
  "priority": "low|medium|high|critical (optional, default: medium)",
  "tags": ["string", "string", ...] (optional, max 10 tags, 50 chars each)
}
```

**Response**:
- **Success (201 Created)**:
```json
{
  "id": "uuid",
  "title": "string",
  "description": "string or null",
  "completed": false,
  "priority": "string",
  "tags": ["string", ...],
  "user_id": "uuid",
  "created_at": "ISO 8601 timestamp",
  "updated_at": "ISO 8601 timestamp"
}
```

**Error Responses**:
- **400 Bad Request**: Malformed JSON
- **401 Unauthorized**: Missing or invalid JWT token
- **403 Forbidden**: user_id in path doesn't match authenticated user
- **422 Unprocessable Entity**: Validation errors (title too long, too many tags, etc.)
- **500 Internal Server Error**: Unexpected server error

**Business Rules**:
1. Title is required and must be 1-200 characters
2. Description is optional, max 1000 characters
3. Priority defaults to "medium" if not provided
4. Tags are optional, max 10 tags per task
5. Each tag must be 1-50 characters
6. Empty tags are stripped and ignored
7. Completed flag is always false for new tasks
8. created_at and updated_at are auto-generated
9. Task is automatically associated with user_id from JWT
10. Path user_id must match JWT user_id (403 if mismatch)

### FR-2: GET /api/users/{user_id}/tasks

**Purpose**: Retrieve task list for the authenticated user with filtering and pagination

**Request**:
- **Method**: GET
- **Path**: `/api/users/{user_id}/tasks`
- **Headers**: `Authorization: Bearer <jwt_token>`
- **Path Parameters**:
  - `user_id` (UUID, required): Must match authenticated user's ID
- **Query Parameters**:
  - `limit` (integer, optional): Number of tasks to return (default: 20, max: 100)
  - `offset` (integer, optional): Number of tasks to skip (default: 0)
  - `status` (string, optional): Filter by status ("completed" or "pending")
  - `priority` (string, optional): Filter by priority ("low", "medium", "high", "critical")
  - `tag` (string, optional): Filter by tag name (exact match)
  - `search` (string, optional): Search term for title and description (case-insensitive)

**Response**:
- **Success (200 OK)**:
```json
{
  "tasks": [
    {
      "id": "uuid",
      "title": "string",
      "description": "string or null",
      "completed": boolean,
      "priority": "string",
      "tags": ["string", ...],
      "user_id": "uuid",
      "created_at": "ISO 8601 timestamp",
      "updated_at": "ISO 8601 timestamp"
    }
  ],
  "total": number
}
```

**Error Responses**:
- **400 Bad Request**: Invalid query parameters
- **401 Unauthorized**: Missing or invalid JWT token
- **403 Forbidden**: user_id in path doesn't match authenticated user
- **500 Internal Server Error**: Unexpected server error

**Business Rules**:
1. Default limit is 20 tasks per page
2. Maximum limit is 100 tasks per page
3. Offset defaults to 0
4. Status filter maps "pending" to completed=false, "completed" to completed=true
5. Priority filter must be exact match (case-sensitive)
6. Tag filter matches exact tag name (case-sensitive)
7. Search is case-insensitive and matches partial strings in title or description
8. Multiple filters are combined with AND logic
9. Results are ordered by created_at timestamp (newest first)
10. Total count reflects filtered results, not all user tasks
11. Path user_id must match JWT user_id (403 if mismatch)

## Data Models

### Task Model (SQLModel)
```python
class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    title: str = Field(max_length=200, nullable=False)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False, nullable=False, index=True)
    priority: str = Field(default="medium", max_length=20, nullable=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    user: User = Relationship(back_populates="tasks")
    tags: List["TaskTag"] = Relationship(back_populates="task")
```

### TaskTag Model (SQLModel)
```python
class TaskTag(SQLModel, table=True):
    __tablename__ = "task_tags"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    task_id: UUID = Field(foreign_key="tasks.id", nullable=False, index=True)
    tag_name: str = Field(max_length=50, nullable=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    task: Task = Relationship(back_populates="tags")

    __table_args__ = (
        UniqueConstraint("task_id", "tag_name", name="uq_task_tag"),
    )
```

## API Contracts

### Pydantic Schemas

```python
# schemas/task.py

class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    priority: Optional[PriorityEnum] = Field(default=PriorityEnum.medium)

class TaskCreate(TaskBase):
    tags: Optional[List[str]] = Field(default=[], max_items=10)

class TaskUpdate(TaskBase):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    completed: Optional[bool] = None
    tags: Optional[List[str]] = Field(default=[], max_items=10)

class TaskResponse(TaskBase):
    id: UUID
    completed: bool
    tags: List[str]
    user_id: UUID
    created_at: datetime
    updated_at: datetime

class TaskListResponse(BaseModel):
    tasks: List[TaskResponse]
    total: int
```

## Non-Functional Requirements

### NFR-1: Performance
- POST endpoint must respond within 200ms for 95th percentile
- GET endpoint must respond within 200ms for 95th percentile (up to 100 tasks)
- Database queries must use proper indexes (user_id, completed, priority)
- Tag filtering must use efficient JOIN operations

### NFR-2: Security
- All endpoints require valid JWT token in Authorization header
- user_id in path must match user_id from JWT token
- No SQL injection vulnerabilities (use parameterized queries)
- Input validation on all fields (length, format, type)
- Return proper HTTP status codes (401, 403, 422)
- Sanitize error messages (no sensitive data exposure)

### NFR-3: Reliability
- Handle database connection failures gracefully
- Implement proper transaction management
- Validate all inputs before database operations
- Return consistent error response format
- Log errors for debugging (without sensitive data)

### NFR-4: Maintainability
- Separate concerns: routes, services, schemas, models
- Follow FastAPI best practices
- Use dependency injection for database sessions
- Comprehensive docstrings for all functions
- Type hints on all function signatures

### NFR-5: Scalability
- Support pagination for large task lists
- Efficient database queries with proper indexing
- Minimal database round trips per request
- Support for concurrent user requests

## Edge Cases and Error Handling

### Edge Case 1: Empty Title
- **Scenario**: User submits task with empty or whitespace-only title
- **Expected**: 422 Unprocessable Entity with error message
- **Implementation**: Pydantic validation with min_length=1

### Edge Case 2: Title Exceeds Max Length
- **Scenario**: User submits task with title > 200 characters
- **Expected**: 422 Unprocessable Entity with error message
- **Implementation**: Pydantic validation with max_length=200

### Edge Case 3: Too Many Tags
- **Scenario**: User submits task with > 10 tags
- **Expected**: 422 Unprocessable Entity with error message
- **Implementation**: Service layer validation + Pydantic max_items=10

### Edge Case 4: Empty Tags
- **Scenario**: User submits task with empty strings in tags array
- **Expected**: Empty tags are stripped and ignored
- **Implementation**: Service layer filters out empty tags

### Edge Case 5: User ID Mismatch
- **Scenario**: user_id in path doesn't match JWT token user_id
- **Expected**: 403 Forbidden with error message
- **Implementation**: Route handler validates user_id before service call

### Edge Case 6: Invalid JWT Token
- **Scenario**: Missing, malformed, or expired JWT token
- **Expected**: 401 Unauthorized with error message
- **Implementation**: JWT middleware intercepts request before route handler

### Edge Case 7: Invalid Filter Parameters
- **Scenario**: User provides invalid status, priority, or limit values
- **Expected**: 400 Bad Request with validation error
- **Implementation**: Pydantic query parameter validation

### Edge Case 8: Large Offset with No Results
- **Scenario**: User requests offset=1000 but only has 50 tasks
- **Expected**: 200 OK with empty tasks array and correct total count
- **Implementation**: Database query returns empty result set

### Edge Case 9: Duplicate Tags on Same Task
- **Scenario**: User submits ["work", "work", "urgent"] as tags
- **Expected**: Duplicate tags are deduplicated in service layer
- **Implementation**: Database unique constraint + service layer deduplication

### Edge Case 10: Special Characters in Search
- **Scenario**: User searches with SQL special characters (%_\)
- **Expected**: Characters are escaped, safe search performed
- **Implementation**: SQLModel/SQLAlchemy parameterized queries handle escaping

## Testing Requirements

### Unit Tests
1. Test create_task with valid data
2. Test create_task with empty title (validation error)
3. Test create_task with title > 200 characters (validation error)
4. Test create_task with > 10 tags (validation error)
5. Test create_task with empty tags (tags stripped)
6. Test get_user_tasks without filters
7. Test get_user_tasks with status filter (completed/pending)
8. Test get_user_tasks with priority filter
9. Test get_user_tasks with tag filter
10. Test get_user_tasks with search term
11. Test get_user_tasks with multiple filters combined
12. Test get_user_tasks with pagination (limit/offset)
13. Test get_user_tasks with large offset (empty results)

### Integration Tests
1. Test POST /api/users/{user_id}/tasks with valid JWT
2. Test POST /api/users/{user_id}/tasks without JWT (401)
3. Test POST /api/users/{user_id}/tasks with user_id mismatch (403)
4. Test POST /api/users/{user_id}/tasks with invalid data (422)
5. Test GET /api/users/{user_id}/tasks with valid JWT
6. Test GET /api/users/{user_id}/tasks without JWT (401)
7. Test GET /api/users/{user_id}/tasks with user_id mismatch (403)
8. Test GET /api/users/{user_id}/tasks with all filter combinations
9. Test GET /api/users/{user_id}/tasks with pagination
10. Test create task → retrieve task list (end-to-end flow)

### Test Coverage Target
- Minimum 95% code coverage for routes, services, schemas
- All edge cases covered with explicit tests
- All error paths tested with proper assertions

## Success Criteria

### Functional Success Criteria
- ✅ POST endpoint creates tasks successfully with all fields
- ✅ GET endpoint retrieves task lists with correct filtering
- ✅ Pagination works correctly (limit, offset, total count)
- ✅ All filters work independently and in combination
- ✅ Search works across title and description (case-insensitive)
- ✅ User isolation enforced (403 on mismatch)
- ✅ Tags are properly created and associated with tasks
- ✅ Validation errors return 422 with clear messages

### Technical Success Criteria
- ✅ All tests passing (unit + integration)
- ✅ Test coverage ≥ 95%
- ✅ Response times < 200ms (95th percentile)
- ✅ Type hints on all functions
- ✅ Proper error handling and logging
- ✅ Code follows FastAPI best practices
- ✅ Database queries optimized with indexes

### Security Success Criteria
- ✅ JWT authentication enforced on both endpoints
- ✅ User isolation validated (no cross-user access possible)
- ✅ Input validation prevents injection attacks
- ✅ Error messages don't leak sensitive data
- ✅ Proper HTTP status codes for all scenarios

## Dependencies

### Internal Dependencies
- Database foundation complete (Task, TaskTag, User models)
- JWT middleware complete (request.state.user_id available)
- Auth endpoints complete (users can signup/login/get tokens)
- Database connection and session management ready

### External Dependencies
- FastAPI framework
- SQLModel ORM
- Pydantic for validation
- Neon PostgreSQL database
- python-jose for JWT decoding (middleware)

## Out of Scope

- Task updates (PUT/PATCH endpoints) - covered in separate feature
- Task deletion (DELETE endpoint) - covered in separate feature
- Task ordering by fields other than created_at
- Task archiving or soft deletes
- Task sharing between users
- Task reminders or notifications
- Task attachments or file uploads
- Bulk task operations
- Task templates
- Advanced search with boolean operators

## Appendix

### Related Specifications
- Database Schema: `/specs/database/schema.md`
- REST API Endpoints: `/specs/api/rest-endpoints.md`
- JWT Authentication: `/specs/006-jwt-auth-middleware/spec.md`
- Auth Endpoints: `/specs/007-auth-endpoints/spec.md`

### References
- FastAPI Documentation: https://fastapi.tiangolo.com/
- SQLModel Documentation: https://sqlmodel.tiangolo.com/
- Pydantic Validation: https://docs.pydantic.dev/latest/
- JWT Best Practices: https://jwt.io/introduction

### Glossary
- **JWT**: JSON Web Token for authentication
- **User Isolation**: Ensuring users can only access their own data
- **Path Parameter**: Variable in URL path (e.g., {user_id})
- **Query Parameter**: Optional filter in URL query string (e.g., ?limit=20)
- **Pagination**: Breaking large result sets into pages
- **SQLModel**: Python library combining SQLAlchemy and Pydantic
- **Pydantic**: Data validation library for Python
- **FastAPI**: Modern Python web framework for APIs
