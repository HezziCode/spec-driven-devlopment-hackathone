# Implementation Plan: Advanced Task Filtering and Search

**Feature**: Advanced Task Filtering and Search
**Branch**: `012-task-filtering-search`
**Created**: 2025-12-25
**Status**: Planning

---

## Executive Summary

This plan enhances the existing GET /users/{user_id}/tasks endpoint with comprehensive filtering, search, sorting, and pagination capabilities. The implementation focuses on query optimization using database indexes and efficient SQLModel query construction.

**Key Design Decisions**:
1. Query builder pattern for constructing filtered queries dynamically
2. Database indexes on priority and completed fields for filter performance
3. LEFT JOIN with TaskTag for tag filtering (handles tasks without tags)
4. Case-insensitive search using ILIKE or lower() function
5. Priority sorting using CASE expression (critical>high>medium>low)
6. Separate count query for total (avoid loading all data)
7. Pagination with limit capping (max 100)

---

## Technical Context

### Existing Infrastructure

**Current Endpoint** (`backend/routes/tasks.py`):
```python
@router.get("/tasks", response_model=TaskListResponse)
async def get_user_tasks_list(
    user_id: UUID,
    current_user_id: str = Depends(get_user_id_from_token),
    session: Session = Depends(get_session),
    completed: Optional[bool] = Query(None),
    priority: Optional[PriorityEnum] = Query(None),
    tag: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    # Currently has basic filtering, needs enhancement
```

**Current Schema** (`backend/schemas/task.py`):
```python
class TaskListResponse(BaseModel):
    tasks: List[TaskResponse]
    total: int
    # Need to add: page, limit
```

**Current Service** (`backend/services/task_service.py`):
```python
def get_user_tasks(...):
    # Has basic filtering logic
    # Needs query builder enhancement
```

---

## Architecture Design

### Query Builder Pattern

**Function**: `build_task_query(session, user_id, filters) -> Tuple[List[Task], int]`

**Location**: `backend/services/task_service.py`

**Logic Flow**:
```python
1. Start with base query: select(Task).where(Task.user_id == user_id)
2. Add search filter (if provided): .where(or_(Task.title.ilike(f"%{search}%"), Task.description.ilike(f"%{search}%")))
3. Add priority filter (if provided): .where(Task.priority == priority)
4. Add status filter (if provided): .where(Task.completed == status_bool)
5. Add tag filter (if provided): .join(TaskTag).where(TaskTag.tag_name == tag).distinct()
6. Add sort order (based on sort parameter)
7. Execute count query (same filters, no pagination): total = session.exec(select(func.count()).select_from(filtered_query.subquery())).one()
8. Apply pagination: .offset(offset).limit(min(limit, 100))
9. Execute and return: (tasks, total)
```

---

## Implementation Strategy

### Phase 0: Research & Decisions

**Decision 1: Search Implementation**

**Chosen**: SQLAlchemy `ilike()` for case-insensitive partial matching

**Rationale**:
- Works with PostgreSQL and SQLite
- No external dependencies (full-text search engines)
- Sufficient for partial matching in title/description
- SQL injection safe when parameterized

**Query Pattern**:
```python
.where(
    or_(
        Task.title.ilike(f"%{search}%"),
        Task.description.ilike(f"%{search}%")
    )
)
```

**Alternatives**: `func.lower()` with `like()`, full-text search (Elastic)

---

**Decision 2: Tag Filtering with Join**

**Chosen**: LEFT JOIN DISTINCT for inclusive tag matching

**Rationale**:
- Returns tasks that have the specified tag
- LEFT JOIN handles tasks without any tags
- DISTINCT prevents duplicate task rows (task with multiple tags)
- Efficient with proper indexes on TaskTag.tag_name

**Query Pattern**:
```python
if tag_filter:
    query = query.join(TaskTag, Task.id == TaskTag.task_id)
    query = query.where(TaskTag.tag_name == tag_filter)
    query = query.distinct()
```

**Alternatives**: Subquery EXISTS, separate tag query

---

**Decision 3: Priority Sorting**

**Chosen**: CASE expression for custom priority order

**Rationale**:
- Priority is enum (not numeric)
- Need custom order: critical > high > medium > low
- CASE maps enum to sortable numeric values

**Query Pattern**:
```python
if sort == "priority":
    query = query.order_by(
        case(
            (Task.priority == "critical", 1),
            (Task.priority == "high", 2),
            (Task.priority == "medium", 3),
            (Task.priority == "low", 4)
        )
    )
```

**Alternatives**: Sort in Python (inefficient), database priority_order column

---

**Decision 4: Pagination Metadata**

**Chosen**: Extend TaskListResponse with page and limit fields

**Rationale**:
- Clients need pagination state for UI
- Calculate page from offset/limit: `page = (offset // limit) + 1`
- Total enables "Page X of Y" display

**Schema Update**:
```python
class TaskListResponse(BaseModel):
    tasks: List[TaskResponse]
    total: int
    page: int       # NEW
    limit: int      # NEW
```

---

## Phase 1: Data Model & Contracts

### Existing Models (No Changes)

**Task Model** (`backend/models.py`):
- Already has all required fields
- Indexes exist on user_id, priority, completed

**TaskTag Model** (`backend/models.py`):
- Junction table for task-tag many-to-many
- Has index on tag_name for efficient filtering

**Required Indexes** (verify exist):
- `Task.user_id` (for user isolation)
- `Task.priority` (for priority filtering)
- `Task.completed` (for status filtering)
- `TaskTag.tag_name` (for tag filtering)
- `Task.created_at`, `Task.updated_at` (for sorting)

---

### API Contract Enhancement

**Endpoint**: GET /users/{user_id}/tasks

**NEW Query Parameters**:
- `search` (str, optional): Text to search in title/description
- `priority` (enum, optional): low | medium | high | critical
- `tag` (str, optional): Tag name to filter by
- `status` (str, optional): pending | completed | all (default: all)
- `sort` (str, optional): created | title | priority | updated (default: created)
- `limit` (int, optional): Items per page (default: 20, max: 100)
- `offset` (int, optional): Pagination offset (default: 0)

**Enhanced Response**:
```json
{
  "tasks": [
    {
      "id": "uuid",
      "title": "Task title",
      "description": "Description",
      "priority": "high",
      "completed": false,
      "tags": ["work", "urgent"],
      "user_id": "uuid",
      "created_at": "2025-12-25T10:00:00Z",
      "updated_at": "2025-12-25T15:30:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "limit": 20
}
```

---

## Phase 2: Implementation Components

### 1. Update TaskListResponse Schema

**File**: `backend/schemas/task.py`

**Changes**:
```python
class TaskListResponse(BaseModel):
    tasks: List[TaskResponse]
    total: int
    page: int = Field(..., description="Current page number (1-indexed)")
    limit: int = Field(..., description="Items per page")
```

---

### 2. Enhance get_user_tasks Service Function

**File**: `backend/services/task_service.py`

**Current Signature**:
```python
def get_user_tasks(
    session: Session,
    user_id: UUID,
    completed: Optional[bool],
    priority: Optional[str],
    tag: Optional[str],
    search: Optional[str],
    limit: int,
    offset: int
) -> Tuple[List[Task], int]:
```

**Enhancement Strategy**:
1. Build base query with user isolation
2. Apply filters conditionally (only if parameter provided)
3. Execute count query (for total)
4. Apply sorting
5. Apply pagination
6. Return (tasks, total)

**Pseudocode**:
```python
# Base query
query = select(Task).where(Task.user_id == user_id)

# Search filter
if search:
    search_pattern = f"%{search}%"
    query = query.where(
        or_(
            Task.title.ilike(search_pattern),
            Task.description.ilike(search_pattern)
        )
    )

# Priority filter
if priority:
    query = query.where(Task.priority == priority)

# Status filter
if completed is not None:  # Handle completed param (existing)
    query = query.where(Task.completed == completed)

# Tag filter (requires join)
if tag:
    query = query.join(TaskTag).where(TaskTag.tag_name == tag).distinct()

# Get total count (before pagination)
count_query = select(func.count()).select_from(query.subquery())
total = session.exec(count_query).one()

# Sorting
if sort == "created":
    query = query.order_by(Task.created_at.desc())
elif sort == "title":
    query = query.order_by(Task.title)
elif sort == "priority":
    query = query.order_by(
        case(
            (Task.priority == "critical", 1),
            (Task.priority == "high", 2),
            (Task.priority == "medium", 3),
            (Task.priority == "low", 4)
        )
    )
elif sort == "updated":
    query = query.order_by(Task.updated_at.desc())
else:  # Default
    query = query.order_by(Task.created_at.desc())

# Pagination (cap limit at 100)
capped_limit = min(limit, 100)
query = query.offset(offset).limit(capped_limit)

# Execute
tasks = session.exec(query).all()

return tasks, total
```

---

### 3. Update Route Handler

**File**: `backend/routes/tasks.py`

**Enhancement**:
```python
@router.get("/tasks", response_model=TaskListResponse)
async def get_user_tasks_list(
    user_id: UUID,
    current_user_id: str = Depends(get_user_id_from_token),
    session: Session = Depends(get_session),
    search: Optional[str] = Query(None, description="Search in title/description"),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    priority: Optional[PriorityEnum] = Query(None, description="Filter by priority"),
    tag: Optional[str] = Query(None, description="Filter by tag name"),
    sort: Optional[str] = Query("created", description="Sort by: created|title|priority|updated"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    offset: int = Query(0, ge=0, description="Pagination offset")
):
    # Verify user authorization
    if str(user_id) != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Get filtered tasks
    tasks, total = get_user_tasks(
        session, user_id, completed, priority, tag, search, sort, limit, offset
    )

    # Serialize tags
    tasks_data = []
    for task in tasks:
        task_dict = task.model_dump()
        task_dict['tags'] = [t.tag_name for t in task.tags] if task.tags else []
        tasks_data.append(TaskResponse(**task_dict))

    # Calculate page number
    page = (offset // limit) + 1 if limit > 0 else 1

    return TaskListResponse(
        tasks=tasks_data,
        total=total,
        page=page,
        limit=limit
    )
```

---

## Testing Strategy

### Test Categories

**1. Search Tests** (5 tests):
- Search matches title (case-insensitive)
- Search matches description (case-insensitive)
- Search with no matches returns empty
- Search with special characters handled safely
- Empty/whitespace search returns all tasks

**2. Priority Filter Tests** (4 tests):
- Filter by each priority level (low, medium, high, critical)
- Invalid priority value returns validation error
- Combined with other filters

**3. Tag Filter Tests** (4 tests):
- Filter by existing tag returns matching tasks
- Filter by non-existent tag returns empty
- Task with multiple tags appears when filtering by any of them
- Tag filter with tasks having no tags

**4. Status Filter Tests** (3 tests):
- Filter by pending (completed=false)
- Filter by completed (completed=true)
- Filter by all (no filter)

**5. Sort Tests** (5 tests):
- Sort by created (descending, default)
- Sort by title (alphabetical)
- Sort by priority (critical→high→medium→low)
- Sort by updated (descending)
- Invalid sort parameter uses default

**6. Combined Filter Tests** (5 tests):
- Search + priority + tag + status (all filters at once)
- Search + sort
- Tag + priority + sort
- Multiple filters returning zero results
- Multiple filters with pagination

**7. Pagination Tests** (6 tests):
- Default limit=20, offset=0
- Custom limit and offset
- Limit > 100 capped at 100
- Offset beyond total returns empty
- Page number calculation correct
- Total count reflects filtered results (not all tasks)

**Total**: ~32 tests

---

## Performance Optimization

### Required Indexes (Verify Existence)

```sql
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
CREATE INDEX idx_tasks_updated_at ON tasks(updated_at DESC);
CREATE INDEX idx_tasktag_tag_name ON task_tags(tag_name);
CREATE INDEX idx_tasktag_task_id ON task_tags(task_id);
```

### Query Performance

**Search Query** (worst case):
- Full table scan on title/description (no index on text fields)
- Acceptable for <10k tasks per user
- Consider adding GIN index for PostgreSQL full-text search if needed

**Filter Queries** (best case):
- Priority filter: Index scan on priority field
- Status filter: Index scan on completed field
- Tag filter: Index scan on tag_name, join via task_id index

**Combined Query Performance**:
- Multiple indexed filters use index intersection
- Expected: <100ms for 10k tasks with all filters

---

## Constitution Compliance

✅ **Performance-First Architecture** (Principle V):
- O(1) index lookups for priority/status filters
- O(n) for search (unavoidable without full-text index)
- O(log n) for sorting with indexes
- Pagination prevents loading large datasets

✅ **Type Safety** (Principle III):
- All query parameters typed (Optional[str], Optional[PriorityEnum], int)
- Pydantic Query validation
- Response schema fully typed

✅ **Modular Architecture** (Principle VI):
- Query building in service layer
- HTTP parameter handling in route layer
- Clear separation of concerns

---

## Risk Assessment

**R1: Performance Degradation with Large Datasets**
- Impact: Slow queries with 10k+ tasks
- Mitigation: Database indexes, query optimization, pagination
- Verification: Load testing with 10k tasks

**R2: SQL Injection via Search Parameter**
- Impact: Critical security breach
- Mitigation: Parameterized queries (SQLModel handles this)
- Verification: Test with special characters (%, _, \, ')

**R3: Tag Join Performance**
- Impact: Slow queries when filtering by tags
- Mitigation: Indexes on TaskTag table, DISTINCT to avoid duplicates
- Verification: Benchmark tag filter with large tag datasets

---

## Success Metrics

- ✅ All 17 functional requirements implemented
- ✅ Search performance <2s (95th percentile)
- ✅ Filter performance <1.5s (95th percentile)
- ✅ All 32+ tests passing
- ✅ Handles 10k+ tasks per user
- ✅ Code coverage ≥95%

---

## Next Steps

1. Run `/sp.tasks` to generate detailed task breakdown
2. Implement query builder function
3. Update route handler with new parameters
4. Update TaskListResponse schema
5. Create comprehensive test suite
6. Verify performance with large datasets
