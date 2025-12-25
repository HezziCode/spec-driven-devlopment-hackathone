# Contract: TaskTag Model

**Module**: `backend.models`
**Class**: `TaskTag`
**Type**: SQLModel (table=True)
**Purpose**: Junction table for many-to-many relationship between tasks and tags

## Public Interface

### Import

```python
from backend.models import TaskTag
```

### Class Definition

```python
class TaskTag(SQLModel, table=True):
    """
    Junction table model for task-tag associations.

    Represents many-to-many relationship between tasks and tag names.
    Prevents duplicate tags on the same task via unique constraint.

    Attributes:
        id: Unique UUID identifier (auto-generated)
        task_id: Foreign key to Task model
        tag_name: Name of the tag (1-50 characters)
        created_at: Tag association timestamp (UTC)
        task: Many-to-one relationship to Task model
    """
```

### Fields

| Field | Type | Nullable | Default | Constraints |
|-------|------|----------|---------|-------------|
| id | UUID | No | uuid4() | PRIMARY KEY |
| task_id | UUID | No | - | FOREIGN KEY(tasks.id), INDEX |
| tag_name | str | No | - | MAX_LENGTH=50, INDEX |
| created_at | datetime | No | UTC now | - |

**Unique Constraint**: `UNIQUE(task_id, tag_name)` - Prevents duplicate tags on same task

### Relationships

| Relationship | Type | Target Model | Access Pattern |
|--------------|------|--------------|----------------|
| task | Task | Task | `tasktag.task` returns the associated Task |

### Usage Examples

**Create Tag Association**:
```python
from backend.models import TaskTag
from uuid import uuid4
from datetime import datetime

tag = TaskTag(
    task_id=task.id,
    tag_name="urgent",
    created_at=datetime.utcnow()
)
```

**Add Tag to Task**:
```python
from sqlmodel import Session

# Create tag association
tag = TaskTag(task_id=task.id, tag_name="work")
session.add(tag)
session.commit()
```

**Get All Tags for Task**:
```python
# Via relationship
tags = task.tags  # Returns List[TaskTag]
tag_names = [tag.tag_name for tag in tags]

# Via query
tags = session.exec(
    select(TaskTag).where(TaskTag.task_id == task.id)
).all()
```

**Get All Tasks with Specific Tag**:
```python
# Join query
tasks_with_tag = session.exec(
    select(Task)
    .join(TaskTag)
    .where(TaskTag.tag_name == "urgent")
).all()
```

**Remove Tag from Task**:
```python
# Find and delete the association
tag = session.exec(
    select(TaskTag).where(
        TaskTag.task_id == task.id,
        TaskTag.tag_name == "work"
    )
).first()

if tag:
    session.delete(tag)
    session.commit()
```

## Constraints

### Database Level

- **PRIMARY KEY** on `id`
- **FOREIGN KEY** from `task_id` to `tasks.id` with **CASCADE DELETE**
  - When a task is deleted, all its TaskTag records are automatically removed
- **NOT NULL** on all fields
- **UNIQUE constraint** on `(task_id, tag_name)` combination
  - Prevents adding the same tag twice to a task
  - Enforced at database level (handles concurrent inserts correctly)
- **INDEX** on `task_id` for efficient task-based queries
- **INDEX** on `tag_name` for efficient tag-based queries

### Application Level (recommended)

- Tag name validation: 1-50 characters, not empty
- Tag name normalization: Lowercase or consistent casing
- Prevent empty tag names or whitespace-only tags

## Type Hints

All fields have complete type hints:

```python
id: UUID
task_id: UUID
tag_name: str
created_at: datetime
task: Task  # Relationship
```

**Mypy Compliance**: Passes strict mode with zero errors

## Unique Constraint Behavior

### Preventing Duplicate Tags

The unique constraint on `(task_id, tag_name)` ensures:

```python
# First tag succeeds
tag1 = TaskTag(task_id=task.id, tag_name="urgent")
session.add(tag1)
session.commit()  # ✓ Success

# Duplicate tag fails
tag2 = TaskTag(task_id=task.id, tag_name="urgent")
session.add(tag2)
session.commit()  # ✗ Raises IntegrityError: UNIQUE constraint failed
```

**Error Handling**: Catch `sqlalchemy.exc.IntegrityError` and return appropriate error to API (409 Conflict or validation message)

### Case Sensitivity

Tag names are **case-sensitive** by default:
- "Work" and "work" are different tags
- Consider normalizing to lowercase at application level for consistency

## Cascade Delete Behavior

When a task is deleted, all associated TaskTag records are **automatically deleted**:

```python
# Delete task
task = session.get(Task, task_id)
session.delete(task)
session.commit()

# All TaskTag records with task_id matching deleted task are automatically removed
# No orphaned tags remain
```

**Rationale**: Tags without tasks are meaningless, automatic cleanup simplifies application logic

## Table Name

**Database Table**: `task_tags`

## Indexes

- **idx_task_tags_pkey** (PRIMARY KEY) on `id`
- **idx_tasktag_task_id** (BTREE) on `task_id` - for finding all tags for a task
- **idx_tasktag_tag_name** (BTREE) on `tag_name` - for finding all tasks with a tag
- **uq_task_tag** (UNIQUE) on `(task_id, tag_name)` - prevents duplicates

## Migration

Table created by: `migrations/create_tables.py`

SQL equivalent:
```sql
CREATE TABLE task_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    tag_name VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(task_id, tag_name)
);

CREATE INDEX idx_tasktag_task_id ON task_tags(task_id);
CREATE INDEX idx_tasktag_tag_name ON task_tags(tag_name);
```

## Testing

Verify TaskTag model contract:

```python
# Test 1: Model importable
from backend.models import TaskTag

# Test 2: Unique constraint enforced
tag1 = TaskTag(task_id=task.id, tag_name="work")
session.add(tag1)
session.commit()  # Success

tag2 = TaskTag(task_id=task.id, tag_name="work")
session.add(tag2)
with pytest.raises(IntegrityError):
    session.commit()  # Should fail with unique violation

# Test 3: Cascade delete works
task = session.get(Task, task_id)
session.delete(task)
session.commit()

# Verify tags deleted
tags = session.exec(
    select(TaskTag).where(TaskTag.task_id == task_id)
).all()
assert len(tags) == 0  # All tags removed

# Test 4: Foreign key enforced
invalid_tag = TaskTag(task_id=uuid4(), tag_name="test")
session.add(invalid_tag)
with pytest.raises(IntegrityError):
    session.commit()  # Should fail with foreign key violation
```

## Common Query Patterns

### Get All Tags for a Task (Most Common)

```python
tags = session.exec(
    select(TaskTag).where(TaskTag.task_id == task.id)
).all()

# Or via relationship
tags = task.tags
```

**Performance**: O(log n) with index on task_id, typically < 10ms

### Get All Tasks with Specific Tag

```python
tasks = session.exec(
    select(Task)
    .join(TaskTag)
    .where(TaskTag.tag_name == "urgent")
).all()
```

**Performance**: O(log n + k) with index on tag_name, typically < 50ms for 100 matching tasks

### Add Multiple Tags to Task

```python
tag_names = ["work", "urgent", "client-meeting"]

for tag_name in tag_names:
    tag = TaskTag(task_id=task.id, tag_name=tag_name)
    session.add(tag)

session.commit()
```

### Update Task Tags (Replace All)

```python
# Delete existing tags
existing_tags = session.exec(
    select(TaskTag).where(TaskTag.task_id == task.id)
).all()

for tag in existing_tags:
    session.delete(tag)

# Add new tags
for tag_name in new_tag_names:
    tag = TaskTag(task_id=task.id, tag_name=tag_name)
    session.add(tag)

session.commit()
```

## Best Practices

1. **Always use unique constraint check**: Let database enforce uniqueness instead of application-level checking (prevents race conditions)

2. **Normalize tag names**: Consider lowercasing tag names at application level for consistency

3. **Batch tag operations**: When adding multiple tags, add all to session then commit once (not commit per tag)

4. **Use relationship access**: Prefer `task.tags` over manual joins when loading task with its tags

5. **Leverage cascade delete**: Don't manually delete tags when deleting task, let CASCADE handle it

6. **Index for tag search**: The tag_name index enables fast tag-based filtering across all tasks
