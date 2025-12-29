---
name: python-type-safety
description: Ensure complete type safety in Python code with mypy static type checking. Use when adding type hints, configuring type checkers, setting up linters, or enforcing code quality standards.
---

# Python Type Safety

## Purpose

Ensure complete type safety in Python code with mypy static type checking.

## Context

Used for adding type hints and configuring type checkers.

## Pattern

```python
from typing import Optional, List, Dict, Union
from sqlmodel import Session, select
from app.models import Task, User
from app.schemas.task import TaskCreateRequest, TaskResponse

def create_task(
    session: Session,
    user_id: str,
    request: TaskCreateRequest
) -> Task:
    """
    Create a new task for the specified user.

    Args:
        session: Database session
        user_id: UUID of the user creating the task
        request: Task creation request with title, description, priority, tags

    Returns:
        Created Task object with generated ID and timestamps

    Raises:
        ValueError: If user_id is invalid or user not found
    """
    task = Task(
        user_id=user_id,
        title=request.title,
        description=request.description,
        priority=request.priority,
        completed=False
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

def get_tasks(
    session: Session,
    user_id: str,
    filters: Optional[Dict[str, Union[str, bool]]] = None
) -> List[Task]:
    """
    Retrieve tasks for a user with optional filters.

    Args:
        session: Database session
        user_id: UUID of the user
        filters: Optional dictionary of filter parameters

    Returns:
        List of Task objects matching the filters
    """
    query = select(Task).where(Task.user_id == user_id)

    if filters:
        if "completed" in filters:
            query = query.where(Task.completed == filters["completed"])
        if "priority" in filters:
            query = query.where(Task.priority == filters["priority"])

    tasks: List[Task] = session.exec(query).all()
    return tasks