from sqlmodel import Session, select
from sqlalchemy import func, case, desc, asc
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from models import Task, TaskTag, User
from schemas.task import TaskCreate, TaskUpdate, PriorityEnum


def create_task(
    session: Session,
    task_data: TaskCreate,
    user_id: UUID,
    source: str = "manual",
    thread_id: Optional[str] = None
) -> Task:
    """
    Create a new task for a user.

    Args:
        session: Database session
        task_data: Task creation data
        user_id: User UUID
        source: Task creation source ('manual' or 'chat')
        thread_id: Optional chat thread ID if created from chat
    """
    # Create the task with source tracking
    task = Task(
        title=task_data.title,
        description=task_data.description,
        completed=False,  # Default to not completed
        priority=task_data.priority or PriorityEnum.medium,
        user_id=user_id,
        source=source,
        created_by_thread_id=thread_id if source == "chat" else None
    )

    session.add(task)
    session.flush()  # Get the task ID without committing

    # Add tags if provided
    if task_data.tags:
        for tag_name in task_data.tags:
            if tag_name.strip():  # Only add non-empty tags
                tag = TaskTag(
                    task_id=task.id,
                    tag_name=tag_name.strip()
                )
                session.add(tag)

    session.commit()
    session.refresh(task)

    return task


def get_user_tasks(
    session: Session,
    user_id: UUID,
    completed: Optional[bool] = None,
    priority: Optional[PriorityEnum] = None,
    tag: Optional[str] = None,
    search: Optional[str] = None,
    sort: str = "created",
    limit: int = 20,
    offset: int = 0
) -> tuple[List[Task], int]:
    """
    Get tasks for a specific user with optional filters.
    Returns a tuple of (tasks, total_count).
    """
    # Start with the base query
    query = select(Task).where(Task.user_id == user_id)

    # Apply filters
    if completed is not None:
        query = query.where(Task.completed == completed)

    if priority is not None:
        query = query.where(Task.priority == priority)

    if search is not None:
        search_pattern = f"%{search}%"
        query = query.where(
            (Task.title.ilike(search_pattern)) |
            (Task.description.ilike(search_pattern))
        )

    # Apply tag filter if needed
    if tag is not None:
        # Join with TaskTag to filter by tag
        query = query.join(TaskTag).where(TaskTag.tag_name == tag)

    # Get total count
    total_query = select(func.count()).select_from(query.subquery())
    total_count = session.exec(total_query).one()

    # Apply sorting
    if sort == "created":
        query = query.order_by(desc(Task.created_at))
    elif sort == "title":
        query = query.order_by(asc(Task.title))
    elif sort == "priority":
        # Custom order: critical > high > medium > low
        query = query.order_by(
            case(
                (Task.priority == "critical", 1),
                (Task.priority == "high", 2),
                (Task.priority == "medium", 3),
                (Task.priority == "low", 4),
                else_=5
            )
        )
    elif sort == "updated":
        query = query.order_by(desc(Task.updated_at))
    else:  # Default to created descending
        query = query.order_by(desc(Task.created_at))

    # Apply pagination
    query = query.offset(offset).limit(limit)

    tasks = session.exec(query).all()

    # Load tags for each task (tags are TaskTag objects loaded via relationship)
    # No need to manually query - SQLModel relationships handle this automatically
    # The tags will be converted to strings in the route handler

    return tasks, total_count


def get_task_by_id(session: Session, task_id: UUID, user_id: UUID) -> Optional[Task]:
    """
    Get a specific task by ID for a user.

    Returns the task with its tags loaded if it exists and belongs to the user.
    Returns None if task doesn't exist or belongs to a different user.
    """
    task = session.get(Task, task_id)

    # Verify that the task belongs to the user
    if task and task.user_id == user_id:
        # Tags are automatically loaded via SQLModel relationship
        # No need to manually query - task.tags will contain TaskTag objects
        return task

    return None


def update_task(
    session: Session,
    task_id: UUID,
    task_data: TaskUpdate,
    user_id: UUID
) -> Optional[Task]:
    """
    Update an existing task.
    """
    task = session.get(Task, task_id)

    # Verify that the task belongs to the user
    if not task or task.user_id != user_id:
        return None

    # Update fields that are provided
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.completed is not None:
        task.completed = task_data.completed
    if task_data.priority is not None:
        task.priority = task_data.priority

    # Update the timestamp
    task.updated_at = datetime.utcnow()

    # Handle tags if provided
    if task_data.tags is not None:
        # Delete all existing tags for this task first
        from sqlalchemy import delete as sql_delete
        delete_stmt = sql_delete(TaskTag).where(TaskTag.task_id == task.id)
        session.exec(delete_stmt)

        # Flush to ensure delete completes before inserts
        session.flush()

        # Add new tags
        for tag_name in task_data.tags:
            if tag_name.strip():  # Only add non-empty tags
                tag = TaskTag(
                    task_id=task.id,
                    tag_name=tag_name.strip()
                )
                session.add(tag)

    session.add(task)
    session.commit()
    session.refresh(task)

    # Force load the tags relationship to ensure they're TaskTag objects
    # This prevents lazy loading issues when the task is accessed outside the session
    _ = task.tags  # Access tags to trigger loading if not already loaded

    return task


def delete_task(session: Session, task_id: UUID, user_id: UUID) -> bool:
    """
    Delete a task by ID for a user.
    """
    task = session.get(Task, task_id)

    # Verify that the task belongs to the user
    if not task or task.user_id != user_id:
        return False

    # Delete associated tags first
    task_tags = session.exec(
        select(TaskTag).where(TaskTag.task_id == task.id)
    ).all()
    for tag in task_tags:
        session.delete(tag)

    # Delete the task
    session.delete(task)
    session.commit()

    return True


def validate_task_data(task_data: TaskCreate) -> List[str]:
    """
    Validate task data and return a list of error messages.
    """
    errors = []

    # Validate title length
    if task_data.title and len(task_data.title) > 200:
        errors.append("Title must be 200 characters or less")

    # Validate description length
    if task_data.description and len(task_data.description) > 1000:
        errors.append("Description must be 1000 characters or less")

    # Validate tags
    if task_data.tags:
        if len(task_data.tags) > 10:
            errors.append("A task can have at most 10 tags")

        for tag in task_data.tags:
            if len(tag) > 50:
                errors.append("Each tag must be 50 characters or less")
            if not tag.strip():
                errors.append("Tags cannot be empty")

    return errors