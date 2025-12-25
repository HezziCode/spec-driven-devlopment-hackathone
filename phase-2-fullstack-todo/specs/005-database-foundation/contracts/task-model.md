# Contract: Task Model

**Module**: `backend.models`
**Class**: `Task`
**Type**: SQLModel (table=True)
**Purpose**: Represents a todo task belonging to a user

## Public Interface

### Import

```python
from backend.models import Task
```

### Class Definition

```python
class Task(SQLModel, table=True):
    """
    Task model representing a todo item with user ownership.

    Attributes:
        id: Unique UUID identifier (auto-generated)
        user_id: Foreign key to User model (owner)
        title: Task title (1-200 characters)
        description: Optional detailed description
        completed: Completion status (default False)
        priority: Priority level enum (low, medium, high, critical)
        created_at: Task creation timestamp (UTC)
        updated_at: Last modification timestamp (UTC)
        user: Many-to-one relationship to User model
        tags: One-to-many relationship to TaskTag model
    """
```

### Fields

| Field | Type | Nullable | Default | Constraints |
|-------|------|----------|---------|-------------|
| id | UUID | No | uuid4() | PRIMARY KEY |
| user_id | UUID | No | - | FOREIGN KEY(users.id), INDEX |
| title | str | No | - | MAX_LENGTH=200 |
| description | str \| None | Yes | None | - |
| completed | bool | No | False | INDEX |
| priority | str | No | 'medium' | ENUM('low','medium','high','critical'), INDEX |
| created_at | datetime | No | UTC now | - |
| updated_at | datetime | No | UTC now | - |

### Relationships

| Relationship | Type | Target Model | Access Pattern |
|--------------|------|--------------|----------------|
| user | User | User | `task.user` returns the owner User |
| tags | List[TaskTag] | TaskTag | `task.tags` returns all tags for this task |

### Usage Examples

**Create Task Instance**:
```python
from backend.models import Task
from uuid import uuid4
from datetime import datetime

task = Task(
    user_id=uuid4(),  # Must be valid user ID
    title="Complete project documentation",
    description="Write comprehensive docs for the API",
    priority="high",
    completed=False,
    created_at=datetime.utcnow(),
    updated_at=datetime.utcnow()
)
```

**Access Task Owner**:
```python
# Assuming task is loaded from database
owner = task.user
print(f"Task created by: {owner.username}")
```

**Access Task Tags**:
```python
# Get all tag names for a task
tag_names = [tag.tag_name for tag in task.tags]
print(f"Tags: {', '.join(tag_names)}")
```

**Query Tasks by User**:
```python
from sqlmodel import Session, select

# Get all tasks for a user
tasks = session.exec(
    select(Task).where(Task.user_id == user.id)
).all()
```

**Query Pending Tasks**:
```python
# Get incomplete tasks for a user
pending_tasks = session.exec(
    select(Task).where(
        Task.user_id == user.id,
        Task.completed == False
    )
).all()
```

**Query High Priority Tasks**:
```python
# Get high/critical priority tasks
high_priority = session.exec(
    select(Task).where(
        Task.user_id == user.id,
        Task.priority.in_(['high', 'critical'])
    )
).all()
```

## Constraints

### Database Level

- **PRIMARY KEY** on `id`
- **FOREIGN KEY** from `user_id` to `users.id` (referential integrity)
- **NOT NULL** on all fields except `description`
- **CHECK constraint** on `priority`: must be one of ('low', 'medium', 'high', 'critical')
- **INDEX** on `user_id` for efficient user-based queries
- **INDEX** on `completed` for status filtering
- **INDEX** on `priority` for priority filtering
- **COMPOSITE INDEX** on `(user_id, completed)` for combined filtering

### Application Level (recommended)

- Title validation: 1-200 characters, not empty
- Description validation: Maximum 1000 characters when provided
- Priority validation: Must be from defined enum
- User ID validation: Must reference existing user

## Type Hints

All fields have complete type hints:

```python
id: UUID
user_id: UUID
title: str
description: str | None  # or Optional[str]
completed: bool
priority: str
created_at: datetime
updated_at: datetime
user: User  # Relationship
tags: List["TaskTag"]  # Relationship (forward reference)
```

**Mypy Compliance**: Passes strict mode with zero errors

## Priority Enumeration

Valid values for `priority` field:

| Value | Display Name | Sort Order | Description |
|-------|--------------|------------|-------------|
| `critical` | Critical | 1 | Urgent, highest priority |
| `high` | High | 2 | Important, high priority |
| `medium` | Medium | 3 | Normal priority (default) |
| `low` | Low | 4 | Lower priority, can wait |

**Sort Logic**: When sorting by priority, order is critical → high → medium → low

## Table Name

**Database Table**: `tasks`

## Indexes

- **idx_tasks_pkey** (PRIMARY KEY) on `id`
- **idx_tasks_user_id** (BTREE) on `user_id` - for user filtering
- **idx_tasks_completed** (BTREE) on `completed` - for status filtering
- **idx_tasks_priority** (BTREE) on `priority` - for priority filtering
- **idx_user_completed** (COMPOSITE) on `(user_id, completed)` - for combined user + status queries

## Migration

Table created by: `migrations/create_tables.py`

SQL equivalent:
```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    priority VARCHAR(20) NOT NULL DEFAULT 'medium'
        CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_user_completed ON tasks(user_id, completed);
```

## Testing

Verify Task model contract:

```python
# Test 1: Model importable
from backend.models import Task

# Test 2: Foreign key enforced
task = Task(user_id=invalid_uuid, title="Test")
session.add(task)
session.commit()  # Should raise ForeignKeyViolation

# Test 3: Priority validation
task = Task(user_id=user.id, title="Test", priority="invalid")
# Should be rejected at database level

# Test 4: Relationship access
task = session.get(Task, task_id)
owner = task.user  # Should load User
tags = task.tags  # Should load List[TaskTag]
```
