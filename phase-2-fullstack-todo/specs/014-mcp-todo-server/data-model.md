# Data Model: MCP Server for Todo Management

**Feature**: 014-mcp-todo-server
**Date**: 2025-12-30

## Existing Entities (Phase II - No Changes Required)

### Task Entity
The existing Task model from Phase II is fully compatible with MCP server requirements.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | Primary Key, Auto-generated | Unique task identifier |
| user_id | UUID | Foreign Key (users.id), Not Null, Indexed | Owner reference |
| title | String | Max 200 chars, Not Null | Task title |
| description | String | Max 1000 chars, Nullable | Task details |
| completed | Boolean | Default False, Not Null, Indexed | Completion status |
| priority | String | Enum (low/medium/high/critical), Default 'medium' | Priority level |
| created_at | DateTime | Not Null, Auto-generated | Creation timestamp |
| updated_at | DateTime | Not Null, Auto-updated | Last modification |

**Indexes**:
- `idx_tasks_user_id` on user_id
- `idx_tasks_completed` on completed
- `idx_tasks_priority` on priority
- `idx_user_completed` on (user_id, completed) - composite

### User Entity
Referenced by user_id in tools. No modifications needed.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | User identifier passed to tools |
| username | String | Display name |
| email | String | User email |

## New Schemas (MCP Tool Input/Output)

### Tool Input Schemas

#### CreateTaskInput
```python
class CreateTaskInput(BaseModel):
    """Input schema for create_task tool."""
    user_id: str = Field(..., description="User UUID who owns the task")
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: str = Field("", max_length=2000, description="Optional task description")
```

#### UpdateTaskInput
```python
class UpdateTaskInput(BaseModel):
    """Input schema for update_task tool."""
    user_id: str = Field(..., description="User UUID who owns the task")
    task_id: str = Field(..., description="Task UUID to update")
    title: str | None = Field(None, min_length=1, max_length=200, description="New title")
    description: str | None = Field(None, max_length=2000, description="New description")

    @model_validator(mode='after')
    def check_at_least_one_field(self):
        if self.title is None and self.description is None:
            raise ValueError("At least one of title or description must be provided")
        return self
```

#### ListTasksInput
```python
class TaskStatus(str, Enum):
    all = "all"
    pending = "pending"
    completed = "completed"

class ListTasksInput(BaseModel):
    """Input schema for list_tasks tool."""
    user_id: str = Field(..., description="User UUID")
    status: TaskStatus = Field(TaskStatus.all, description="Filter by status")
```

#### SearchTasksInput
```python
class SearchTasksInput(BaseModel):
    """Input schema for search_tasks tool."""
    user_id: str = Field(..., description="User UUID")
    query: str = Field(..., min_length=1, max_length=100, description="Search query")
```

#### TaskIdInput
```python
class TaskIdInput(BaseModel):
    """Input schema for single task operations (mark_complete, delete)."""
    user_id: str = Field(..., description="User UUID who owns the task")
    task_id: str = Field(..., description="Task UUID to operate on")
```

### Tool Output Schemas

#### TaskResponse
```python
class TaskResponse(BaseModel):
    """Standard response for single task operations."""
    task_id: str
    status: str  # created, updated, deleted, completed
    title: str
```

#### TaskListResponse
```python
class TaskListResponse(BaseModel):
    """Response for list/search operations."""
    tasks: list[TaskDetail]
    total: int

class TaskDetail(BaseModel):
    """Task details in list responses."""
    id: str
    title: str
    description: str | None
    completed: bool
    priority: str
    created_at: str
    updated_at: str
```

#### ErrorResponse
```python
class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    code: str  # NOT_FOUND, VALIDATION_ERROR, DATABASE_ERROR
    task_id: str | None = None
```

## State Transitions

### Task Completion State
```
pending (completed=False) --[mark_complete]--> completed (completed=True)
```

Note: mark_complete is idempotent - calling on already completed task succeeds.

### Task Lifecycle
```
[create_task] --> exists (pending)
                    |
    [update_task] <-+-> [mark_complete]
                    |
              [delete_task] --> removed
```

## Data Validation Rules

| Rule | Field | Validation |
|------|-------|------------|
| Title required | title | 1-200 characters, non-empty |
| Description optional | description | 0-2000 characters |
| User isolation | user_id | Must match resource owner |
| UUID format | user_id, task_id | Valid UUID string |
| Search query | query | 1-100 characters |
| Status filter | status | One of: all, pending, completed |

## Query Patterns

### List Tasks with Status Filter
```python
# Status = "all"
select(Task).where(Task.user_id == user_id)

# Status = "pending"
select(Task).where(Task.user_id == user_id, Task.completed == False)

# Status = "completed"
select(Task).where(Task.user_id == user_id, Task.completed == True)
```

### Search Tasks (Case-Insensitive)
```python
select(Task).where(
    Task.user_id == user_id,
    or_(
        Task.title.ilike(f"%{query}%"),
        Task.description.ilike(f"%{query}%")
    )
)
```

### Single Task with User Verification
```python
select(Task).where(
    Task.id == task_id,
    Task.user_id == user_id
)
```
