from typing import List, Optional
from .models import Task
from .utils import (
    generate_next_id,
    validate_task_title,
    validate_task_description,
    validate_task_id,
    find_task_by_id
)

class TodoApp:
    """
    Main todo application class managing in-memory task storage.
    """
    def __init__(self):
        self.tasks: List[Task] = []  # In-memory storage for tasks

    def add_task(self, title: str, description: Optional[str] = None) -> int:
        """
        Add a new task to the todo list.

        Args:
            title: Task title (required)
            description: Task description (optional)

        Returns:
            int: ID of the newly created task

        Raises:
            ValueError: If title is invalid
        """
        validated_title = validate_task_title(title)
        validated_description = validate_task_description(description)

        new_id = generate_next_id(self.tasks)
        new_task = Task(
            id=new_id,
            title=validated_title,
            description=validated_description,
            completed=False
        )

        self.tasks.append(new_task)
        return new_id

    def get_all_tasks(self) -> List[Task]:
        """
        Get all tasks in the todo list.

        Returns:
            List[Task]: All tasks in the list
        """
        return self.tasks.copy()

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """
        Get a specific task by its ID.

        Args:
            task_id: ID of the task to retrieve

        Returns:
            Task if found, None otherwise
        """
        validate_task_id(task_id)
        return find_task_by_id(self.tasks, task_id)

    def update_task(self, task_id: int, title: Optional[str] = None, description: Optional[str] = None) -> bool:
        """
        Update an existing task's title and/or description.

        Args:
            task_id: ID of the task to update
            title: New title (optional)
            description: New description (optional)

        Returns:
            bool: True if task was updated, False otherwise

        Raises:
            ValueError: If task with given ID doesn't exist or if provided title is invalid
        """
        validate_task_id(task_id)

        task = find_task_by_id(self.tasks, task_id)
        if task is None:
            raise ValueError(f"Task with ID {task_id} does not exist")

        # Update title if provided
        if title is not None:
            validated_title = validate_task_title(title)
            task.title = validated_title

        # Update description if provided
        if description is not None:
            validated_description = validate_task_description(description)
            task.description = validated_description

        return True

    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task by its ID.

        Args:
            task_id: ID of the task to delete

        Returns:
            bool: True if task was deleted, False otherwise

        Raises:
            ValueError: If task with given ID doesn't exist
        """
        validate_task_id(task_id)

        task = find_task_by_id(self.tasks, task_id)
        if task is None:
            raise ValueError(f"Task with ID {task_id} does not exist")

        self.tasks.remove(task)
        return True

    def toggle_task_completion(self, task_id: int) -> bool:
        """
        Toggle the completion status of a task.

        Args:
            task_id: ID of the task to toggle

        Returns:
            bool: True if task status was toggled, False otherwise

        Raises:
            ValueError: If task with given ID doesn't exist
        """
        validate_task_id(task_id)

        task = find_task_by_id(self.tasks, task_id)
        if task is None:
            raise ValueError(f"Task with ID {task_id} does not exist")

        task.completed = not task.completed
        return True

    def get_completed_tasks(self) -> List[Task]:
        """
        Get all completed tasks.

        Returns:
            List[Task]: All completed tasks
        """
        return [task for task in self.tasks if task.completed]

    def get_pending_tasks(self) -> List[Task]:
        """
        Get all pending (not completed) tasks.

        Returns:
            List[Task]: All pending tasks
        """
        return [task for task in self.tasks if not task.completed]
