# Test Generation Skill

**Purpose**: Generate pytest unit tests for Python console apps with coverage.

## When to Use
- When creating unit tests for functions or classes.
- Autonomous trigger: If task involves test files or pytest.

## Instructions
Use this for comprehensive test coverage. Example patterns:

```python
import pytest
from src.todo_app import TodoApp

def test_add_task_success():
    app = TodoApp()
    task_id = app.add_task("Test task")
    assert task_id == 1
    assert len(app.tasks) == 1
```
