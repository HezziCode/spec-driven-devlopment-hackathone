# Feature Specification: Task Update Operations

## Feature ID
009-task-update-ops

## Overview
Implement PUT and PATCH endpoints for updating tasks with full and partial update capabilities, user isolation, tag management, and proper validation.

## User Stories

### US-1: Full Task Update (PUT)
**As a** registered user
**I want to** update all fields of my task at once
**So that** I can replace the entire task with new information

**Acceptance Criteria:**
- PUT /api/users/{user_id}/tasks/{task_id} endpoint available
- All task fields can be updated: title, description, completed, priority, tags
- User must own the task (enforce user_id match)
- Tags are replaced entirely (old tags deleted, new tags added)
- Updated timestamp is refreshed
- Returns 200 OK with updated task
- Returns 403 Forbidden if user doesn't own task
- Returns 404 Not Found if task doesn't exist
- Returns 422 Unprocessable Entity for validation errors

### US-2: Partial Task Update (PATCH)
**As a** registered user
**I want to** update only specific fields of my task
**So that** I can make small changes without sending all data

**Acceptance Criteria:**
- PATCH /api/users/{user_id}/tasks/{task_id} endpoint available
- Only provided fields are updated (others remain unchanged)
- Supports updating any subset of: title, description, completed, priority, tags
- User must own the task (enforce user_id match)
- If tags provided, they replace existing tags entirely
- If tags not provided, existing tags remain unchanged
- Updated timestamp is refreshed only if changes are made
- Returns 200 OK with updated task
- Returns 403 Forbidden if user doesn't own task
- Returns 404 Not Found if task doesn't exist
- Returns 422 Unprocessable Entity for validation errors

### US-3: Task Completion Toggle
**As a** registered user
**I want to** quickly mark tasks as complete or incomplete
**So that** I can track my progress efficiently

**Acceptance Criteria:**
- PATCH /api/users/{user_id}/tasks/{task_id} with only `{"completed": true/false}`
- Only the completed field is updated
- Other fields remain unchanged
- Updated timestamp is refreshed
- Returns updated task with correct completion status

### US-4: Priority Updates
**As a** registered user
**I want to** change the priority of my tasks
**So that** I can reorganize my task list by importance

**Acceptance Criteria:**
- PUT or PATCH can update priority field
- Valid priority values: low, medium, high, critical
- Invalid priority values return 422 Unprocessable Entity
- Default priority is medium if not specified in PUT

### US-5: Tag Management in Updates
**As a** registered user
**I want to** update tags on my tasks
**So that** I can reorganize and categorize my tasks

**Acceptance Criteria:**
- Tags can be updated via PUT or PATCH
- Providing tags array replaces all existing tags
- Empty array removes all tags
- Not providing tags in PATCH preserves existing tags
- Tag validation applies: max 10 tags, max 50 chars each
- Duplicate tags within same task prevented by database constraint

## Technical Requirements

### API Endpoints

#### PUT /api/users/{user_id}/tasks/{task_id}
**Purpose:** Full task replacement (all fields required)

**Request Body:**
```json
{
  "title": "string (required, 1-200 chars)",
  "description": "string (optional, max 1000 chars)",
  "completed": "boolean (required)",
  "priority": "enum (required: low|medium|high|critical)",
  "tags": ["string"] (optional, max 10 items, max 50 chars each)
}
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "string",
  "description": "string",
  "completed": "boolean",
  "priority": "string",
  "tags": ["string"],
  "created_at": "ISO 8601",
  "updated_at": "ISO 8601"
}
```

**Error Responses:**
- 401 Unauthorized: Invalid or missing JWT token
- 403 Forbidden: user_id mismatch (user doesn't own task)
- 404 Not Found: Task doesn't exist
- 422 Unprocessable Entity: Validation errors

#### PATCH /api/users/{user_id}/tasks/{task_id}
**Purpose:** Partial task update (any subset of fields)

**Request Body (all fields optional):**
```json
{
  "title": "string (optional, 1-200 chars)",
  "description": "string (optional, max 1000 chars)",
  "completed": "boolean (optional)",
  "priority": "enum (optional: low|medium|high|critical)",
  "tags": ["string"] (optional, max 10 items, max 50 chars each)
}
```

**Response (200 OK):** Same as PUT response

**Error Responses:** Same as PUT

### Database Operations

#### Tag Management Strategy
1. **Full Replacement Approach:**
   - When tags are provided (PUT or PATCH), delete all existing TaskTag records
   - Insert new TaskTag records for each tag in the array
   - Use database transaction to ensure atomicity
   - Prevents orphaned tags and duplicate handling complexity

2. **Partial Update Handling:**
   - For PATCH without tags field: skip tag operations entirely
   - For PATCH with tags field: treat as full replacement
   - Use `exclude_unset=True` in Pydantic to detect provided fields

#### Updated Timestamp
- Always update `updated_at` to `datetime.utcnow()` when task is modified
- SQLModel field default: `Field(default_factory=datetime.utcnow)`

### User Isolation
- JWT middleware extracts `user_id` from token → `request.state.user_id`
- Route handler verifies `path_user_id == request.state.user_id`
- Service layer queries scoped to `user_id`: `WHERE task.user_id = user_id AND task.id = task_id`
- Return 403 if user_id mismatch
- Return 404 for non-existent tasks (don't leak existence to unauthorized users)

### Validation Rules

#### Field Validations
- **title**: Required for PUT, optional for PATCH, 1-200 characters, non-empty
- **description**: Optional, max 1000 characters
- **completed**: Boolean, required for PUT, optional for PATCH
- **priority**: Enum (low, medium, high, critical), required for PUT, optional for PATCH
- **tags**: Optional array, max 10 items, each max 50 characters, no empty strings

#### Error Response Format
```json
{
  "detail": {
    "errors": [
      "Title must be 200 characters or less",
      "Priority must be one of: low, medium, high, critical"
    ]
  }
}
```

## Non-Functional Requirements

### Performance
- Update operations complete within 200ms (p95)
- Tag replacement uses batch delete + batch insert
- Use database indexes for user_id and task_id lookups
- Single database transaction per update

### Security
- JWT authentication required for all update endpoints
- User isolation strictly enforced
- SQL injection prevented via SQLModel parameterized queries
- Input validation via Pydantic schemas
- No sensitive data in error messages

### Reliability
- Database transactions ensure atomicity (task + tags updated together)
- Rollback on any failure during update
- Idempotent operations (same request produces same result)

### Maintainability
- Shared service layer logic between PUT and PATCH
- Type hints on all functions
- Comprehensive docstrings
- Test coverage > 95%

## Implementation Details

### Schema Design

#### TaskUpdate Schema (Pydantic)
```python
class TaskUpdate(BaseModel):
    """Schema for updating tasks (used by both PUT and PATCH)."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    completed: Optional[bool] = None
    priority: Optional[PriorityEnum] = None
    tags: Optional[List[str]] = Field(None, max_length=10)
```

#### Differentiate PUT vs PATCH
- **PUT**: Validate all required fields at route level or use separate schema
- **PATCH**: Use `exclude_unset=True` when calling `task_data.dict(exclude_unset=True)`

### Service Layer

#### update_task Function
```python
def update_task(
    session: Session,
    task_id: UUID,
    task_data: TaskUpdate,
    user_id: UUID,
    is_full_update: bool = False
) -> Optional[Task]:
    """
    Update a task with full or partial data.

    Args:
        session: Database session
        task_id: Task UUID
        task_data: Update data (from PUT or PATCH)
        user_id: User UUID (for isolation)
        is_full_update: If True, all fields required (PUT)

    Returns:
        Updated task or None if not found/unauthorized
    """
    # 1. Fetch task and verify ownership
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        return None

    # 2. Update task fields (conditionally for PATCH)
    update_data = task_data.dict(exclude_unset=not is_full_update)
    for field, value in update_data.items():
        if field != "tags":  # Handle tags separately
            setattr(task, field, value)

    # 3. Update timestamp
    task.updated_at = datetime.utcnow()

    # 4. Handle tags if provided
    if "tags" in update_data:
        # Delete existing tags
        session.exec(delete(TaskTag).where(TaskTag.task_id == task_id))
        # Add new tags
        for tag_name in update_data["tags"]:
            if tag_name.strip():
                session.add(TaskTag(task_id=task_id, tag_name=tag_name.strip()))

    # 5. Commit transaction
    session.add(task)
    session.commit()
    session.refresh(task)

    # 6. Load tags for response
    task.tags = [tag.tag_name for tag in task.tags]

    return task
```

### Route Handlers

#### PUT Handler
```python
@router.put("/users/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_user_task(
    user_id: UUID,
    task_id: UUID,
    task_data: TaskUpdate,
    current_user_id: str = Depends(get_user_id_from_token),
    session: Session = Depends(get_session)
):
    """Update task (full replacement)."""
    if str(user_id) != current_user_id:
        raise HTTPException(403, detail="Not authorized")

    # Validate all fields present for PUT (add logic or use separate schema)
    task = update_task(session, task_id, task_data, user_id, is_full_update=True)
    if not task:
        raise HTTPException(404, detail="Task not found")

    return task
```

#### PATCH Handler
```python
@router.patch("/users/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def partial_update_user_task(
    user_id: UUID,
    task_id: UUID,
    task_data: TaskUpdate,
    current_user_id: str = Depends(get_user_id_from_token),
    session: Session = Depends(get_session)
):
    """Partially update task (only provided fields)."""
    if str(user_id) != current_user_id:
        raise HTTPException(403, detail="Not authorized")

    task = update_task(session, task_id, task_data, user_id, is_full_update=False)
    if not task:
        raise HTTPException(404, detail="Task not found")

    return task
```

## Testing Strategy

### Unit Tests (Service Layer)
1. **update_task function:**
   - Update all fields (full update)
   - Update only title (partial update)
   - Update only completed status
   - Update tags (replace existing)
   - Update with empty tags (remove all)
   - PATCH without tags (preserve existing)
   - Verify updated_at changes
   - Return None for non-existent task
   - Return None for wrong user_id

### Integration Tests (API Endpoints)
1. **PUT /tasks/{id}:**
   - Full update success (200 OK)
   - Update with new tags
   - Update removing all tags
   - User isolation (403)
   - Non-existent task (404)
   - Invalid data (422)
   - Missing required fields (422)

2. **PATCH /tasks/{id}:**
   - Partial update (only title) (200 OK)
   - Update only completed status
   - Update only priority
   - Update tags while preserving other fields
   - PATCH without tags preserves existing tags
   - User isolation (403)
   - Non-existent task (404)
   - Invalid data (422)

3. **Cross-endpoint tests:**
   - Create task → PATCH → verify only changed fields updated
   - Create task with tags → PATCH without tags → verify tags preserved
   - Create task with tags → PATCH with new tags → verify tags replaced

### Edge Cases
- Empty string for optional fields
- Maximum length strings (title 200, description 1000)
- Invalid priority value
- 11 tags (exceeds max)
- Tag with 51 characters (exceeds max)
- Duplicate tags in request
- Special characters in tags
- Concurrent updates (test transaction isolation)

## Dependencies
- Feature 008-task-crud-endpoints (create/get/delete endpoints)
- Feature 007-auth-endpoints (JWT authentication)
- Feature 006-jwt-auth-middleware (user_id extraction)
- Feature 005-database-foundation (models, migrations)

## Success Criteria
- All user stories acceptance criteria met
- PUT endpoint updates all fields correctly
- PATCH endpoint updates only provided fields
- User isolation enforced (403 on mismatch)
- Tags managed correctly (replace on update, preserve on PATCH without tags)
- All tests passing (unit + integration)
- Test coverage > 95%
- API responds within 200ms (p95)
- No data leakage between users

## Out of Scope
- Batch updates (multiple tasks at once)
- Partial tag updates (add/remove individual tags without replacing all)
- Task history/versioning
- Optimistic locking for concurrent updates
- Undo/redo functionality

## References
- REST API Endpoints Spec: /specs/api/rest-endpoints.md
- Database Schema: /specs/database/schema.md
- Task CRUD Endpoints: /specs/008-task-crud-endpoints/
- JWT Auth Middleware: /specs/006-jwt-auth-middleware/
