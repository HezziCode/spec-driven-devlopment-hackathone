# Feature Specification: Task Deletion and Single Task Retrieval (Security-Focused)

**Feature ID**: 010-task-delete-get
**Status**: In Progress
**Priority**: High
**Created**: 2025-12-24
**Branch**: 010-task-delete-get

## Overview

Implement secure single task retrieval (GET) and deletion (DELETE) endpoints with robust user isolation and information disclosure prevention. This feature focuses on security-first design to prevent enumeration attacks and ensure cascade deletion of associated resources.

## Problem Statement

Users need the ability to:
1. Retrieve a specific task by ID to view its complete details including tags
2. Delete tasks they no longer need, with automatic cleanup of associated tags

However, these operations expose security risks:
- **Information Disclosure**: Returning 403 (Forbidden) vs 404 (Not Found) can reveal whether a task exists
- **Enumeration Attacks**: Attackers can probe task IDs to discover which tasks exist
- **Cross-User Access**: Users must not be able to access or delete other users' tasks
- **Data Integrity**: Deleting tasks must cascade to associated tags to prevent orphaned data

## Success Criteria

### Security Requirements (Critical)
- [ ] GET endpoint returns 404 for both non-existent tasks AND unauthorized access (no 403)
- [ ] DELETE endpoint returns 404 for both non-existent tasks AND unauthorized access (no 403)
- [ ] User ID from JWT token is verified before any database operations
- [ ] No information leakage about task existence in error messages
- [ ] All security tests pass (cross-user access attempts, enumeration prevention)

### Functional Requirements
- [ ] GET /api/users/{user_id}/tasks/{task_id} retrieves single task with tags
- [ ] DELETE /api/users/{user_id}/tasks/{task_id} deletes task and cascades to tags
- [ ] Both endpoints enforce user isolation (path user_id must match JWT user_id)
- [ ] Database queries are efficient with proper indexing
- [ ] Response times meet performance requirements (p95 < 200ms)

### Data Integrity Requirements
- [ ] Cascade delete removes all TaskTag records associated with deleted task
- [ ] No orphaned tags remain after task deletion
- [ ] Database transactions ensure atomic operations
- [ ] Updated_at timestamp not modified on GET operations

## User Stories

### US-010-01: Secure Single Task Retrieval
**As a** authenticated user
**I want to** retrieve a specific task by its ID
**So that** I can view its complete details including title, description, priority, completion status, and tags

**Acceptance Criteria:**
1. When I request GET /api/users/{my_user_id}/tasks/{valid_task_id} with valid JWT token
   - Then I receive 200 OK with task details including tags array
   - And the response includes: id, title, description, completed, priority, tags[], user_id, created_at, updated_at

2. When I request GET /api/users/{my_user_id}/tasks/{non_existent_task_id}
   - Then I receive 404 Not Found with message "Task not found"
   - And NO information is revealed about whether the task exists

3. When I request GET /api/users/{my_user_id}/tasks/{other_users_task_id}
   - Then I receive 404 Not Found with message "Task not found" (NOT 403)
   - And NO information is revealed about task ownership or existence

4. When I request GET /api/users/{different_user_id}/tasks/{any_task_id}
   - Then I receive 403 Forbidden with message "Not authorized to view tasks for this user"
   - And the request is rejected BEFORE any database queries

5. When I request without JWT token or with invalid token
   - Then I receive 401 Unauthorized
   - And the request is rejected by middleware before reaching the endpoint

**Security Test Cases:**
```python
# Test Case 1: Authorized access to own task
GET /api/users/user-123/tasks/task-456
Authorization: Bearer <valid-token-for-user-123>
Expected: 200 OK with task details

# Test Case 2: Non-existent task (404, not 403)
GET /api/users/user-123/tasks/non-existent-uuid
Authorization: Bearer <valid-token-for-user-123>
Expected: 404 Not Found (same as unauthorized access)

# Test Case 3: Cross-user access attempt (404, not 403)
GET /api/users/user-123/tasks/task-belonging-to-user-999
Authorization: Bearer <valid-token-for-user-123>
Expected: 404 Not Found (no information disclosure)

# Test Case 4: Path user_id mismatch (403 before DB query)
GET /api/users/user-999/tasks/any-task-id
Authorization: Bearer <valid-token-for-user-123>
Expected: 403 Forbidden (rejected immediately)

# Test Case 5: Missing authentication
GET /api/users/user-123/tasks/task-456
Expected: 401 Unauthorized (middleware rejection)
```

### US-010-02: Secure Task Deletion with Cascade
**As a** authenticated user
**I want to** delete a task I no longer need
**So that** it is permanently removed from the system along with its associated tags

**Acceptance Criteria:**
1. When I request DELETE /api/users/{my_user_id}/tasks/{valid_task_id} with valid JWT token
   - Then I receive 200 OK with message "Task deleted successfully"
   - And the task is permanently deleted from the database
   - And all associated TaskTag records are deleted (cascade)
   - And no orphaned tags remain

2. When I request DELETE /api/users/{my_user_id}/tasks/{non_existent_task_id}
   - Then I receive 404 Not Found with message "Task not found"
   - And NO information is revealed about whether the task exists

3. When I request DELETE /api/users/{my_user_id}/tasks/{other_users_task_id}
   - Then I receive 404 Not Found with message "Task not found" (NOT 403)
   - And NO information is revealed about task ownership or existence
   - And the other user's task is NOT deleted

4. When I request DELETE /api/users/{different_user_id}/tasks/{any_task_id}
   - Then I receive 403 Forbidden with message "Not authorized to delete tasks for this user"
   - And the request is rejected BEFORE any database queries

5. When I request without JWT token or with invalid token
   - Then I receive 401 Unauthorized
   - And the request is rejected by middleware before reaching the endpoint

6. When I delete a task with multiple tags
   - Then all TaskTag associations are deleted
   - And database queries confirm no orphaned tags exist

**Security Test Cases:**
```python
# Test Case 1: Authorized deletion of own task
DELETE /api/users/user-123/tasks/task-456
Authorization: Bearer <valid-token-for-user-123>
Expected: 200 OK, task and tags deleted

# Test Case 2: Non-existent task (404, not 403)
DELETE /api/users/user-123/tasks/non-existent-uuid
Authorization: Bearer <valid-token-for-user-123>
Expected: 404 Not Found (same as unauthorized access)

# Test Case 3: Cross-user deletion attempt (404, not 403)
DELETE /api/users/user-123/tasks/task-belonging-to-user-999
Authorization: Bearer <valid-token-for-user-123>
Expected: 404 Not Found, other user's task NOT deleted

# Test Case 4: Path user_id mismatch (403 before DB query)
DELETE /api/users/user-999/tasks/any-task-id
Authorization: Bearer <valid-token-for-user-123>
Expected: 403 Forbidden (rejected immediately)

# Test Case 5: Missing authentication
DELETE /api/users/user-123/tasks/task-456
Expected: 401 Unauthorized (middleware rejection)

# Test Case 6: Cascade delete verification
DELETE /api/users/user-123/tasks/task-with-tags-456
Authorization: Bearer <valid-token-for-user-123>
Expected: 200 OK, verify TaskTag records deleted via DB query
```

## API Specification

### GET /api/users/{user_id}/tasks/{task_id}

**Purpose**: Retrieve a single task by ID with tags for the authenticated user

**Path Parameters:**
- `user_id` (UUID, required): User ID (must match JWT user_id)
- `task_id` (UUID, required): Task ID to retrieve

**Headers:**
- `Authorization: Bearer <jwt_token>` (required)

**Request Body:** None

**Success Response (200 OK):**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "string (max 200 chars)",
  "description": "string (max 1000 chars) | null",
  "completed": false,
  "priority": "low | medium | high | critical",
  "tags": ["tag1", "tag2"],
  "created_at": "2025-12-24T10:30:00Z",
  "updated_at": "2025-12-24T10:30:00Z"
}
```

**Error Responses:**
- **401 Unauthorized**: Missing or invalid JWT token (middleware)
  ```json
  {
    "error": "Authorization header is required",
    "code": "MISSING_TOKEN",
    "timestamp": "2025-12-24T10:30:00Z"
  }
  ```

- **403 Forbidden**: Path user_id doesn't match JWT user_id
  ```json
  {
    "detail": "Not authorized to view tasks for this user"
  }
  ```

- **404 Not Found**: Task not found OR unauthorized access
  ```json
  {
    "detail": "Task not found"
  }
  ```
  **CRITICAL**: This response MUST be returned for BOTH:
  - Non-existent task IDs
  - Tasks that belong to other users

  This prevents information disclosure about task existence.

**Performance:**
- p95 latency: < 200ms
- Single database query with tags loaded
- Indexed query on task.id and task.user_id

### DELETE /api/users/{user_id}/tasks/{task_id}

**Purpose**: Delete a task and its associated tags for the authenticated user

**Path Parameters:**
- `user_id` (UUID, required): User ID (must match JWT user_id)
- `task_id` (UUID, required): Task ID to delete

**Headers:**
- `Authorization: Bearer <jwt_token>` (required)

**Request Body:** None

**Success Response (200 OK):**
```json
{
  "message": "Task deleted successfully"
}
```

**Error Responses:**
- **401 Unauthorized**: Missing or invalid JWT token (middleware)
  ```json
  {
    "error": "Authorization header is required",
    "code": "MISSING_TOKEN",
    "timestamp": "2025-12-24T10:30:00Z"
  }
  ```

- **403 Forbidden**: Path user_id doesn't match JWT user_id
  ```json
  {
    "detail": "Not authorized to delete tasks for this user"
  }
  ```

- **404 Not Found**: Task not found OR unauthorized access
  ```json
  {
    "detail": "Task not found"
  }
  ```
  **CRITICAL**: This response MUST be returned for BOTH:
  - Non-existent task IDs
  - Tasks that belong to other users

  This prevents information disclosure about task existence.

**Side Effects:**
- Task record deleted from `tasks` table
- All associated TaskTag records deleted from `task_tags` table (cascade)
- Database transaction ensures atomic operation

**Performance:**
- p95 latency: < 200ms
- Two database operations: tag deletion + task deletion
- Wrapped in transaction for atomicity

## Database Schema (Existing)

### Task Table
```sql
CREATE TABLE tasks (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id),
  title VARCHAR(200) NOT NULL,
  description VARCHAR(1000),
  completed BOOLEAN DEFAULT FALSE,
  priority VARCHAR(20) DEFAULT 'medium',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_user_completed (user_id, completed),
  INDEX idx_user_id (user_id)
);
```

### TaskTag Table
```sql
CREATE TABLE task_tags (
  id UUID PRIMARY KEY,
  task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
  tag_name VARCHAR(50) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE CONSTRAINT uq_task_tag (task_id, tag_name),
  INDEX idx_task_id (task_id),
  INDEX idx_tag_name (tag_name)
);
```

**Note**: The `ON DELETE CASCADE` constraint ensures automatic deletion of tags when a task is deleted. However, we still implement explicit cascade delete in the service layer for clarity and control.

## Security Considerations

### Information Disclosure Prevention
**Critical Security Requirement**: Never reveal whether a task exists when the user is not authorized to access it.

**Implementation Strategy:**
1. **Path User ID Verification** (First Line of Defense):
   - Check if `path_user_id == jwt_user_id` BEFORE any database queries
   - If mismatch: Return 403 Forbidden immediately
   - This prevents unauthorized users from probing the database

2. **Database Query with User Isolation**:
   - Query: `SELECT * FROM tasks WHERE id = ? AND user_id = ?`
   - Returns None for BOTH non-existent tasks AND unauthorized access

3. **Consistent Error Response**:
   - If query returns None: Return 404 "Task not found"
   - NEVER return 403 at this stage
   - Attacker cannot determine if task exists

**Why This Matters:**
```python
# BAD: Information Disclosure
task = get_task_by_id(task_id)
if not task:
    return 404  # Task doesn't exist
if task.user_id != user_id:
    return 403  # Task exists but unauthorized - LEAK!

# GOOD: No Information Disclosure
task = get_task_by_id(task_id, user_id)  # Query with user_id
if not task:
    return 404  # Could be non-existent OR unauthorized - SAFE!
```

### Cascade Delete Security
- Explicit cascade delete in service layer (defense in depth)
- Database-level cascade delete as backup (ON DELETE CASCADE)
- Transaction ensures atomic operation (no partial deletes)
- Verify no orphaned tags remain after deletion

### Authentication & Authorization
- **Authentication** (401): Verified by JWT middleware
- **Authorization** (403): Path user_id must match JWT user_id
- **Resource Access** (404): Task must exist AND belong to user

### Performance & Security Balance
- Single database query with user_id filter (efficient + secure)
- Indexed queries prevent enumeration timing attacks
- No additional database round-trips for authorization

## Testing Requirements

### Security Tests (Priority 1)
1. **Cross-User Access Prevention**:
   - Create task for user A
   - Attempt to GET/DELETE with user B's token
   - Verify 404 (not 403) is returned
   - Verify user B cannot access or delete user A's task

2. **Information Disclosure Prevention**:
   - Attempt to access non-existent task ID
   - Attempt to access other user's task ID
   - Verify IDENTICAL 404 response for both cases
   - Verify no timing differences between responses

3. **Path User ID Mismatch**:
   - User A attempts GET /api/users/user-B/tasks/task-X
   - Verify 403 Forbidden before database query
   - Verify no database queries are executed

4. **Authentication Requirement**:
   - Attempt GET/DELETE without JWT token
   - Attempt with expired token
   - Attempt with invalid token signature
   - Verify 401 Unauthorized from middleware

### Functional Tests
1. **Successful Retrieval**:
   - Create task with tags
   - GET request returns task with tags array
   - Verify all fields are present and correct

2. **Successful Deletion**:
   - Create task with multiple tags
   - DELETE request returns success message
   - Verify task deleted from database
   - Verify all tags deleted from database

3. **Cascade Delete Verification**:
   - Create task with 5 tags
   - Delete task
   - Query database for orphaned TaskTag records
   - Verify count is 0

### Performance Tests
1. GET endpoint response time < 200ms (p95)
2. DELETE endpoint response time < 200ms (p95)
3. Single database query for GET (with tags loaded)
4. Two database queries for DELETE (tags + task)

### Edge Cases
1. Task with no tags (tags array is empty)
2. Task with maximum tags (10 tags)
3. Concurrent deletion attempts
4. Deletion of already deleted task (404)

## Implementation Notes

### Current Implementation Status
The endpoints are already implemented in:
- `/backend/routes/tasks.py` (lines 86-115 for GET, lines 184-213 for DELETE)
- `/backend/services/task_service.py` (lines 101-116 for GET, lines 178-199 for DELETE)

### Identified Security Issues
**CRITICAL**: Current implementation has information disclosure vulnerability:
- Lines 99, 163, 197 in `tasks.py` return 403 for user_id mismatch
- This check happens AFTER verifying task existence
- Allows enumeration: 403 means task exists, 404 means it doesn't

**Fix Required**:
1. Keep path user_id verification (403 response) at the route level
2. Ensure service layer query includes user_id filter
3. Return 404 for all cases where task is not found OR not authorized
4. The current service layer already implements this correctly (query with user_id)

### Required Changes
1. **Route Layer** (`tasks.py`):
   - GET endpoint (line 99): Change 403 to check earlier, before service call
   - DELETE endpoint (line 197): Change 403 to check earlier, before service call
   - Both endpoints already have path user_id check at lines 97 and 195

2. **Service Layer** (`task_service.py`):
   - GET (line 101): Already queries with user_id - GOOD
   - DELETE (line 178): Already queries with user_id - GOOD
   - Cascade delete already implemented (lines 188-193) - GOOD

3. **Tests**:
   - Add security test suite for cross-user access
   - Add information disclosure prevention tests
   - Add cascade delete verification tests

### Implementation Approach
The current implementation is mostly correct. The security issue is subtle:
- The path user_id check (403) happens at the right place (before service call)
- The service layer correctly queries with user_id (returns None for unauthorized)
- The issue is in the error messages and test coverage

**Solution**: Focus on comprehensive security testing to verify the behavior is correct.

## Out of Scope
- Soft delete (tasks are hard deleted)
- Undo/restore functionality
- Batch deletion of multiple tasks
- Task archiving
- Audit logging of deletions
- Email notifications on deletion

## Dependencies
- JWT middleware (implemented in 006-jwt-auth-middleware)
- Database models (implemented in 005-database-foundation)
- Task creation endpoint (implemented in 008-task-crud-endpoints)
- User authentication (implemented in 007-auth-endpoints)

## Rollout Plan
1. Review existing implementation for security issues
2. Create comprehensive security test suite
3. Fix any identified security vulnerabilities
4. Run full test suite to verify behavior
5. Document security considerations in API docs
6. Deploy to staging for security review
7. Deploy to production after security approval

## Metrics & Monitoring
- Endpoint response times (p50, p95, p99)
- Error rates by status code (401, 403, 404, 500)
- Failed authorization attempts (potential attacks)
- Database query performance for GET/DELETE
- Cascade delete success rate

## References
- REST API Endpoints Spec: `/specs/api/rest-endpoints.md`
- Database Schema: `/specs/database/schema.md`
- JWT Middleware Spec: `/specs/006-jwt-auth-middleware/spec.md`
- OWASP Top 10: Information Exposure Through Error Messages
- Security Skill Pattern: `/.claude/skills/secure-resource-access/`
