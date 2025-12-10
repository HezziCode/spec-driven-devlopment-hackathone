from typing import List
from .models import Task


def generate_next_id(tasks: List[Task]) -> int:
    """
    Generate the next available ID for a new task.

    Args:
        tasks: List of existing tasks

    Returns:
        int: The next available ID
    """
    if not tasks:
        return 1
    return max(task.id for task in tasks) + 1


def validate_task_title(title: str) -> str:
    """
    Validate a task title.

    Args:
        title: Title to validate

    Returns:
        str: Validated title with whitespace stripped

    Raises:
        ValueError: If title is invalid
    """
    if not title:
        raise ValueError("Title cannot be empty")
    
    stripped_title = title.strip()
    if not stripped_title:
        raise ValueError("Title cannot contain only whitespace")
    
    if len(stripped_title) > 200:
        raise ValueError("Title cannot exceed 200 characters")
    
    return stripped_title


def validate_task_description(description: str) -> str:
    """
    Validate a task description.

    Args:
        description: Description to validate

    Returns:
        str: Validated description

    Raises:
        ValueError: If description is invalid
    """
    if description is None:
        return None
    
    if len(description) > 1000:
        raise ValueError("Description cannot exceed 1000 characters")
    
    return description


def validate_task_id(task_id: int) -> None:
    """
    Validate a task ID.

    Args:
        task_id: ID to validate

    Raises:
        ValueError: If ID is invalid
    """
    if not isinstance(task_id, int):
        raise ValueError("Task ID must be an integer")
    if task_id <= 0:
        raise ValueError("Task ID must be a positive integer")


def find_task_by_id(tasks: List[Task], task_id: int) -> Task:
    """
    Find a task by its ID.

    Args:
        tasks: List of tasks to search
        task_id: ID to search for

    Returns:
        Task if found, None otherwise
    """
    for task in tasks:
        if task.id == task_id:
            return task
    return None
