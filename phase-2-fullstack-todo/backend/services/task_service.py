from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from models import Task, TaskTag, User
from schemas.task import TaskCreate, TaskUpdate, PriorityEnum


def create_task(session: Session, task_data: TaskCreate, user_id: UUID) -> Task:
    """
    Create a new task for a user.
    """
    # Create the task
    task = Task(
        title=task_data.title,
        description=task_data.description,
        completed=False,  # Default to not completed
        priority=task_data.priority or PriorityEnum.medium,
        user_id=user_id
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

    # Add tags to the task response
    task.tags = [tag.tag_name for tag in task.tags]

    return task


def get_user_tasks(
    session: Session,
    user_id: UUID,
    completed: Optional[bool] = None,
    priority: Optional[PriorityEnum] = None,
    tag: Optional[str] = None,
    search: Optional[str] = None,
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
        from sqlalchemy import func
        query = query.join(TaskTag).where(TaskTag.tag_name == tag)

    # Get total count
    total_query = select(func.count()).select_from(query.subquery())
    total_count = session.exec(total_query).one()

    # Apply pagination
    query = query.offset(offset).limit(limit).order_by(Task.created_at.desc())

    tasks = session.exec(query).all()

    # Add tags to each task
    for task in tasks:
        task_tags = session.exec(
            select(TaskTag).where(TaskTag.task_id == task.id)
        ).all()
        task.tags = [tag.tag_name for tag in task_tags]

    return tasks, total_count


def get_task_by_id(session: Session, task_id: UUID, user_id: UUID) -> Optional[Task]:
    """
    Get a specific task by ID for a user.
    """
    task = session.get(Task, task_id)

    # Verify that the task belongs to the user
    if task and task.user_id == user_id:
        # Add tags to the task
        task_tags = session.exec(
            select(TaskTag).where(TaskTag.task_id == task.id)
        ).all()
        task.tags = [tag.tag_name for tag in task_tags]
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
        # Remove existing tags
        existing_tags = session.exec(
            select(TaskTag).where(TaskTag.task_id == task.id)
        ).all()
        for tag in existing_tags:
            session.delete(tag)

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

    # Add tags to the task response
    task_tags = session.exec(
        select(TaskTag).where(TaskTag.task_id == task.id)
    ).all()
    task.tags = [tag.tag_name for tag in task_tags]

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