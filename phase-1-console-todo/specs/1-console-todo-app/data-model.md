# Data Model: Console Todo App

## Task Entity

The primary data model for the Console Todo App is the Task entity, implemented as a Python dataclass.

### Attributes

- **id**: `int` - Unique identifier for the task (positive integer)
- **title**: `str` - Task title (required, non-empty, max 200 characters)
- **description**: `Optional[str]` - Task description (optional, max 1000 characters)
- **completed**: `bool` - Completion status (default: False)

### Validation Rules

- ID must be a positive integer (> 0)
- Title cannot be empty or contain only whitespace
- Title cannot exceed 200 characters
- Description cannot exceed 1000 characters (if provided)
- Completed status defaults to False when creating new tasks

### Dataclass Features

- Automatic generation of `__init__`, `__repr__`, `__eq__` methods
- Type hints for better IDE support and code clarity
- Built-in support for default values
- Post-initialization validation using `__post_init__` method

### Relationships

The Task entity exists independently within the application's in-memory storage. Tasks are stored in a list within the TodoApp class and accessed by their unique ID.

### Example

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class Task:
    id: int
    title: str
    description: Optional[str] = None
    completed: bool = False
```

This data model provides a clean, type-safe foundation for the todo application while maintaining simplicity and performance for in-memory operations.