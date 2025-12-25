# Implementation Plan: Task Update Operations

## Feature ID
009-task-update-ops

## Overview
This plan outlines the technical approach for implementing PUT and PATCH endpoints for task updates with full and partial update capabilities, user isolation, tag management, and comprehensive validation.

## Architecture Decisions

### Decision 1: Shared Service Function for PUT and PATCH
**Context:** Both PUT and PATCH update tasks, differing only in required vs optional fields.

**Options Considered:**
1. **Separate functions** for PUT and PATCH updates
2. **Shared function** with `is_full_update` flag
3. **PATCH-only function** with PUT validating at route level

**Decision:** Use shared function with flexibility for both operations (Option 2)

**Rationale:**
- Reduces code duplication (DRY principle)
- Single source of truth for update logic
- Tag management logic is identical for both
- Easy to maintain and test
- Performance equivalent to separate functions

**Trade-offs:**
- Slightly more complex function signature
- Need to handle `exclude_unset` logic
- Offset by better maintainability

### Decision 2: Tag Replacement Strategy
**Context:** Tags are related entities in TaskTag table; need strategy for updates.

**Options Considered:**
1. **Delta approach:** Calculate diff (add new, remove old)
2. **Full replacement:** Delete all existing, insert new
3. **Upsert approach:** Update existing, add new, remove orphans

**Decision:** Full replacement strategy (Option 2)

**Rationale:**
- Simplest implementation (fewer moving parts)
- Clearest semantics for API clients
- No risk of orphaned tags
- Database transaction ensures atomicity
- Performance acceptable for small tag lists (max 10)

**Trade-offs:**
- More database operations (delete + insert vs update)
- Mitigated by small tag counts and single transaction

### Decision 3: PATCH Without Tags Behavior
**Context:** When tags field not provided in PATCH, decide whether to preserve or clear tags.

**Options Considered:**
1. **Preserve existing tags** (no-op for tags)
2. **Clear all tags** (treat as empty array)
3. **Make it explicit** (require tags field always)

**Decision:** Preserve existing tags (Option 1)

**Rationale:**
- Aligns with PATCH semantics (update only provided fields)
- More intuitive for API clients
- Allows updating other fields without affecting tags
- Uses Pydantic's `exclude_unset=True` to detect field presence

**Trade-offs:**
- Slight complexity in distinguishing "not provided" vs "empty array"
- Mitigated by Pydantic's built-in capabilities

### Decision 4: User Isolation Enforcement
**Context:** Prevent users from updating other users' tasks.

**Options Considered:**
1. **JWT-only verification** (trust middleware)
2. **Dual verification** (JWT + database query)
3. **Database-only** (user_id in WHERE clause)

**Decision:** Dual verification - JWT middleware + database query (Option 2)

**Rationale:**
- Defense in depth (multiple security layers)
- Prevents timing attacks (404 for both non-existent and unauthorized)
- Database query is required anyway to fetch task
- Clear separation: middleware authenticates, service authorizes

**Trade-offs:**
- Minimal overhead (single query already needed)
- Increased security justifies any minor complexity

### Decision 5: Error Response Strategy
**Context:** Determine what information to return for errors.

**Options Considered:**
1. **404 for both non-existent and unauthorized** (hide existence)
2. **403 for unauthorized, 404 for non-existent** (expose existence)
3. **Generic 400 for all client errors** (minimal info)

**Decision:** 404 for both (Option 1)

**Rationale:**
- Security best practice (prevents user enumeration)
- No information leakage to unauthorized users
- Consistent with authentication security principles

**Trade-offs:**
- Less helpful for debugging (but acceptable for production)
- Can use detailed logging internally

## Technical Implementation Plan

### Phase 1: Schema Enhancements
**Goal:** Ensure schemas support both PUT and PATCH operations

**Tasks:**
1. Review existing TaskUpdate schema
2. Verify all fields are Optional for PATCH compatibility
3. Add validation for full updates (PUT) at route level
4. Create comprehensive validation tests

**Files:**
- `backend/schemas/task.py` (review/update)

**Acceptance:**
- TaskUpdate schema has all fields Optional
- Validation rules enforce constraints (length, enums)
- Pydantic validation tests pass

### Phase 2: Service Layer Implementation
**Goal:** Implement shared update logic with full and partial support

**Tasks:**
1. Enhance `update_task` function to handle both PUT and PATCH
2. Implement tag replacement logic with transaction
3. Add updated_at timestamp update
4. Handle exclude_unset for partial updates
5. Verify user ownership in service layer
6. Add comprehensive docstrings and type hints

**Files:**
- `backend/services/task_service.py` (update existing function)

**Key Logic:**
```python
def update_task(
    session: Session,
    task_id: UUID,
    task_data: TaskUpdate,
    user_id: UUID
) -> Optional[Task]:
    """
    Update task with full or partial data.
    Handles tags replacement and user isolation.
    """
    # 1. Fetch and verify ownership
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        return None

    # 2. Get only provided fields (for PATCH)
    update_data = task_data.dict(exclude_unset=True)

    # 3. Update task fields
    for field, value in update_data.items():
        if field != "tags":
            setattr(task, field, value)

    # 4. Update timestamp
    task.updated_at = datetime.utcnow()

    # 5. Handle tags if provided
    if "tags" in update_data:
        # Delete existing tags
        existing_tags = session.exec(
            select(TaskTag).where(TaskTag.task_id == task_id)
        ).all()
        for tag in existing_tags:
            session.delete(tag)

        # Add new tags
        for tag_name in update_data["tags"]:
            if tag_name.strip():
                session.add(TaskTag(
                    task_id=task_id,
                    tag_name=tag_name.strip()
                ))

    # 6. Commit and return
    session.add(task)
    session.commit()
    session.refresh(task)

    # 7. Load tags for response
    task.tags = [tag.tag_name for tag in task.tags]

    return task
```

**Acceptance:**
- Function handles both full and partial updates
- Tags replaced correctly when provided
- Tags preserved when not provided (PATCH)
- User ownership verified
- Transaction ensures atomicity
- Unit tests pass (100% coverage)

### Phase 3: Route Handlers Update
**Goal:** Update PUT and PATCH endpoints to use enhanced service

**Tasks:**
1. Review existing PUT handler in routes/tasks.py
2. Review existing PATCH handler in routes/tasks.py
3. Ensure both use shared service function correctly
4. Add proper error handling (403, 404, 422)
5. Verify JWT middleware integration
6. Add comprehensive docstrings

**Files:**
- `backend/routes/tasks.py` (review/update existing handlers)

**Key Logic (PUT):**
```python
@router.put("/users/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_user_task(
    user_id: UUID,
    task_id: UUID,
    task_data: TaskUpdate,
    current_user_id: str = Depends(get_user_id_from_token),
    session: Session = Depends(get_session)
):
    """Full task update (PUT) - all fields required."""
    # User isolation check
    if str(user_id) != current_user_id:
        raise HTTPException(403, detail="Not authorized")

    # Call service
    task = update_task(session, task_id, task_data, user_id)
    if not task:
        raise HTTPException(404, detail="Task not found")

    return task
```

**Key Logic (PATCH):**
```python
@router.patch("/users/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def partial_update_user_task(
    user_id: UUID,
    task_id: UUID,
    task_data: TaskUpdate,
    current_user_id: str = Depends(get_user_id_from_token),
    session: Session = Depends(get_session)
):
    """Partial task update (PATCH) - any fields optional."""
    # User isolation check
    if str(user_id) != current_user_id:
        raise HTTPException(403, detail="Not authorized")

    # Call service (exclude_unset handled in service)
    task = update_task(session, task_id, task_data, user_id)
    if not task:
        raise HTTPException(404, detail="Task not found")

    return task
```

**Acceptance:**
- PUT endpoint validates and updates all fields
- PATCH endpoint updates only provided fields
- User isolation enforced (403)
- Proper error responses (403, 404, 422)
- Integration with JWT middleware
- Route tests pass

### Phase 4: Comprehensive Testing
**Goal:** Ensure all functionality is thoroughly tested

**Tasks:**
1. Write unit tests for service layer
2. Write integration tests for PUT endpoint
3. Write integration tests for PATCH endpoint
4. Write cross-endpoint tests
5. Write edge case tests
6. Verify test coverage > 95%

**Files:**
- `backend/tests/test_tasks.py` (add new tests)
- `backend/tests/test_task_service.py` (create if needed)

**Test Categories:**

#### Unit Tests (Service Layer)
```python
def test_update_task_full():
    """Test full task update with all fields."""

def test_update_task_partial_title():
    """Test updating only title field."""

def test_update_task_partial_completed():
    """Test toggling completion status."""

def test_update_task_with_tags():
    """Test replacing task tags."""

def test_update_task_remove_tags():
    """Test removing all tags."""

def test_update_task_preserve_tags():
    """Test PATCH without tags preserves existing."""

def test_update_task_timestamp():
    """Test updated_at timestamp changes."""

def test_update_task_not_found():
    """Test returns None for non-existent task."""

def test_update_task_wrong_user():
    """Test returns None for wrong user_id."""
```

#### Integration Tests (API)
```python
def test_put_task_success():
    """Test PUT updates all fields successfully."""

def test_put_task_with_new_tags():
    """Test PUT replaces tags."""

def test_put_task_unauthorized():
    """Test PUT returns 403 for wrong user."""

def test_put_task_not_found():
    """Test PUT returns 404 for non-existent task."""

def test_patch_task_partial():
    """Test PATCH updates only title."""

def test_patch_task_completed():
    """Test PATCH toggles completion."""

def test_patch_task_preserves_tags():
    """Test PATCH without tags preserves existing."""

def test_patch_task_replaces_tags():
    """Test PATCH with tags replaces existing."""

def test_patch_task_unauthorized():
    """Test PATCH returns 403 for wrong user."""

def test_patch_task_validation_error():
    """Test PATCH returns 422 for invalid data."""
```

#### Edge Cases
```python
def test_update_max_length_fields():
    """Test fields at maximum length."""

def test_update_invalid_priority():
    """Test invalid priority value."""

def test_update_too_many_tags():
    """Test exceeding 10 tags limit."""

def test_update_tag_too_long():
    """Test tag exceeding 50 characters."""

def test_update_empty_title():
    """Test empty title returns validation error."""

def test_update_special_chars_in_tags():
    """Test special characters in tags."""
```

**Acceptance:**
- All test categories implemented
- Tests pass consistently
- Coverage > 95%
- Edge cases handled correctly

### Phase 5: Documentation and Review
**Goal:** Complete documentation and verify implementation

**Tasks:**
1. Update API documentation (OpenAPI/Swagger)
2. Add inline code comments for complex logic
3. Update CLAUDE.md if needed
4. Verify all acceptance criteria met
5. Performance testing (ensure < 200ms p95)
6. Security review (user isolation, injection prevention)

**Files:**
- `backend/routes/tasks.py` (inline docs)
- `backend/services/task_service.py` (inline docs)
- README updates if needed

**Acceptance:**
- OpenAPI docs reflect PUT/PATCH endpoints
- Code comments explain complex logic
- All acceptance criteria verified
- Performance benchmarks met
- Security review passed

## Data Flow

### PUT Request Flow
```
Client Request (JWT + Task Data)
    ↓
FastAPI Route Handler (PUT /users/{user_id}/tasks/{task_id})
    ↓
JWT Middleware → Extract user_id
    ↓
Route Handler → Verify user_id match (403 if mismatch)
    ↓
Task Service → update_task()
    ↓
    ├─→ Fetch task from DB
    ├─→ Verify ownership (404 if not found/wrong user)
    ├─→ Update all task fields
    ├─→ Update timestamp
    ├─→ Delete existing tags
    ├─→ Insert new tags
    └─→ Commit transaction
    ↓
Load tags into task object
    ↓
Return task to client (200 OK)
```

### PATCH Request Flow
```
Client Request (JWT + Partial Task Data)
    ↓
FastAPI Route Handler (PATCH /users/{user_id}/tasks/{task_id})
    ↓
JWT Middleware → Extract user_id
    ↓
Route Handler → Verify user_id match (403 if mismatch)
    ↓
Task Service → update_task()
    ↓
    ├─→ Fetch task from DB
    ├─→ Verify ownership (404 if not found/wrong user)
    ├─→ Extract only provided fields (exclude_unset=True)
    ├─→ Update only provided task fields
    ├─→ Update timestamp
    ├─→ If tags provided:
    │   ├─→ Delete existing tags
    │   └─→ Insert new tags
    ├─→ If tags not provided: preserve existing
    └─→ Commit transaction
    ↓
Load tags into task object
    ↓
Return task to client (200 OK)
```

## Database Schema Considerations

### Existing Schema (No Changes Required)
```sql
-- tasks table
CREATE TABLE tasks (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    title VARCHAR(200) NOT NULL,
    description VARCHAR(1000),
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- task_tags table
CREATE TABLE task_tags (
    id UUID PRIMARY KEY,
    task_id UUID NOT NULL REFERENCES tasks(id),
    tag_name VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(task_id, tag_name)
);

-- Indexes (already exist)
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_user_completed ON tasks(user_id, completed);
CREATE INDEX idx_task_tags_task_id ON task_tags(task_id);
```

### Transaction Considerations
- Use SQLModel session for automatic transaction management
- All updates within single transaction (task + tags)
- Rollback on any error ensures consistency
- UNIQUE constraint on (task_id, tag_name) prevents duplicates

## Security Considerations

### User Isolation
- JWT middleware extracts user_id from token
- Route handler verifies path user_id matches token user_id (403 if not)
- Service layer queries include user_id filter (defense in depth)
- Return 404 for both non-existent and unauthorized (no info leakage)

### Input Validation
- Pydantic schemas validate all inputs
- Length constraints enforced (title, description, tags)
- Enum validation for priority
- SQLModel prevents SQL injection via parameterized queries

### Authentication
- All endpoints require valid JWT token
- Middleware rejects invalid/expired tokens (401)
- HTTPS required in production (environment config)

## Performance Considerations

### Query Optimization
- Use session.get(Task, task_id) for O(1) lookup (primary key)
- Single query to fetch task
- Batch delete for tags (one query)
- Batch insert for tags (one query per tag, acceptable for max 10)
- Total queries: ~1 fetch + 1 delete + N inserts (N ≤ 10)

### Caching
- Not required for update operations (always need fresh data)
- Consider caching for GET operations only

### Database Indexes
- Existing indexes sufficient: user_id, (user_id, completed), task_id
- Primary key index on tasks.id ensures fast lookups

### Performance Target
- p95 latency < 200ms for update operations
- Measured with 10 concurrent users
- Database connection pooling configured

## Error Handling

### Error Response Format
All errors follow FastAPI's HTTPException format:
```json
{
  "detail": "Error message"
}
```

### Error Codes
- **400 Bad Request:** Malformed request (rare, Pydantic catches most)
- **401 Unauthorized:** Missing or invalid JWT token (middleware)
- **403 Forbidden:** User ID mismatch (not authorized to update this task)
- **404 Not Found:** Task doesn't exist or user doesn't own it
- **422 Unprocessable Entity:** Validation errors (Pydantic)
- **500 Internal Server Error:** Unexpected errors (logged for debugging)

### Logging Strategy
- Log all 500 errors with full context
- Log 403 errors for security monitoring
- Do not log sensitive data (passwords, tokens)
- Use structured logging for easy parsing

## Dependencies and Prerequisites

### Required Features (Already Implemented)
- ✅ 005-database-foundation: Database models and migrations
- ✅ 006-jwt-auth-middleware: JWT authentication and user_id extraction
- ✅ 007-auth-endpoints: User signup/login
- ✅ 008-task-crud-endpoints: Task create, get, delete (update handlers exist)

### Environment Variables
- DATABASE_URL: Neon PostgreSQL connection string
- BETTER_AUTH_SECRET: JWT secret for token verification
- ENVIRONMENT: dev/staging/prod
- LOG_LEVEL: DEBUG/INFO/WARNING/ERROR

### Python Dependencies (Already Installed)
- fastapi
- sqlmodel
- pydantic
- python-jose (for JWT)
- pytest (for testing)

## Rollout Plan

### Phase 1: Implementation (Current)
- Implement schema enhancements
- Implement service layer updates
- Update route handlers
- Write comprehensive tests

### Phase 2: Testing
- Run unit tests
- Run integration tests
- Test edge cases
- Verify test coverage > 95%

### Phase 3: Review
- Code review
- Security review
- Performance testing
- Documentation review

### Phase 4: Deployment
- Deploy to staging environment
- Run smoke tests
- Monitor for errors
- Deploy to production

## Success Metrics

### Functionality
- ✅ PUT endpoint updates all fields correctly
- ✅ PATCH endpoint updates only provided fields
- ✅ Tags replaced when provided in update
- ✅ Tags preserved when not provided in PATCH
- ✅ User isolation enforced (403 on mismatch)
- ✅ Proper error responses (403, 404, 422)

### Quality
- ✅ Test coverage > 95%
- ✅ All tests passing
- ✅ No linting errors
- ✅ Type hints on all functions
- ✅ Comprehensive docstrings

### Performance
- ✅ p95 latency < 200ms
- ✅ No N+1 query problems
- ✅ Database indexes utilized

### Security
- ✅ User isolation verified
- ✅ No SQL injection vulnerabilities
- ✅ No information leakage
- ✅ JWT authentication enforced

## Risks and Mitigations

### Risk 1: Concurrent Updates
**Risk:** Two clients update same task simultaneously, causing conflicts.
**Impact:** Medium - Last write wins, potential data loss
**Mitigation:**
- Use database transactions (already planned)
- Consider optimistic locking if needed (out of scope for now)
- Document expected behavior

### Risk 2: Tag Duplication on Insert
**Risk:** Race condition could create duplicate tags despite UNIQUE constraint.
**Impact:** Low - Database constraint prevents it, but raises exception
**Mitigation:**
- UNIQUE constraint already in place
- Transaction rollback on constraint violation
- Handle exception gracefully

### Risk 3: Large Tag Lists Performance
**Risk:** Replacing 10 tags requires 11 queries (1 delete + 10 inserts).
**Impact:** Low - Max 10 tags, acceptable performance
**Mitigation:**
- Performance testing verifies < 200ms
- Consider batch insert if needed (optimization)

### Risk 4: Validation Bypass
**Risk:** Client sends invalid data bypassing Pydantic validation.
**Impact:** Low - Pydantic validates automatically, defense in depth
**Mitigation:**
- Pydantic validation at schema level
- Additional validation in service layer if needed
- Database constraints as last line of defense

## Future Enhancements (Out of Scope)

### Batch Updates
Allow updating multiple tasks in one request:
```
PATCH /users/{user_id}/tasks?ids=id1,id2,id3
```

### Partial Tag Updates
Add/remove individual tags without replacing all:
```
POST /users/{user_id}/tasks/{task_id}/tags
DELETE /users/{user_id}/tasks/{task_id}/tags/{tag_name}
```

### Task History
Track all changes to tasks with versioning:
```sql
CREATE TABLE task_history (
    id UUID PRIMARY KEY,
    task_id UUID REFERENCES tasks(id),
    field_name VARCHAR(50),
    old_value TEXT,
    new_value TEXT,
    changed_by UUID REFERENCES users(id),
    changed_at TIMESTAMP
);
```

### Optimistic Locking
Prevent concurrent update conflicts:
```python
class Task(SQLModel, table=True):
    version: int = Field(default=1)
    # Increment version on each update
```

### Undo/Redo
Allow users to revert changes:
```
POST /users/{user_id}/tasks/{task_id}/undo
POST /users/{user_id}/tasks/{task_id}/redo
```

## Conclusion
This plan provides a comprehensive approach to implementing task update operations with PUT and PATCH endpoints. The architecture decisions prioritize simplicity, security, and maintainability while meeting all functional and non-functional requirements. The implementation is straightforward, leveraging existing infrastructure and following established patterns from previous features.
