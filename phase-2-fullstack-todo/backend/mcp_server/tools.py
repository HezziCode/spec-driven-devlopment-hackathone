"""
MCP tool implementations for Todo management.

This module contains all MCP tool functions that are exposed to AI agents
for managing user tasks. Each tool enforces user isolation by requiring
and validating user_id on all operations.
"""

import logging
from datetime import datetime
from uuid import UUID

from sqlmodel import or_, select

from mcp_server.schemas import TaskStatus
from mcp_server.server import get_sync_session, mcp
from models import Task

# Configure logging
logger = logging.getLogger(__name__)


def _validate_uuid(uuid_str: str, field_name: str) -> UUID | None:
    """Validate and convert UUID string to UUID object."""
    try:
        return UUID(uuid_str)
    except (ValueError, AttributeError):
        return None


def _task_to_detail(task: Task) -> dict:
    """Convert Task model to TaskDetail dict."""
    return {
        "id": str(task.id),
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "priority": task.priority,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
    }


# =============================================================================
# Tool Implementations
# =============================================================================


@mcp.tool()
def create_task(
    user_id: str,
    title: str,
    description: str = "",
    source: str = "manual",
    thread_id: str = None,
) -> dict:
    """
    Create a new task for the user.

    Args:
        user_id: UUID of the user who owns the task
        title: Task title (1-200 characters, required)
        description: Optional task description (max 2000 characters)
        source: Task creation source ('manual' or 'chat'), defaults to 'manual'
        thread_id: Optional chat thread ID if created from chat

    Returns:
        dict: TaskResponse with task_id, status="created", and title
              OR ErrorResponse with error details
    """
    # Validate user_id
    user_uuid = _validate_uuid(user_id, "user_id")
    if not user_uuid:
        return {
            "error": "Invalid user_id format",
            "code": "VALIDATION_ERROR",
            "task_id": None,
        }

    # Validate title
    if not title or len(title.strip()) == 0:
        return {
            "error": "Title is required and cannot be empty",
            "code": "VALIDATION_ERROR",
            "task_id": None,
        }

    if len(title) > 200:
        return {
            "error": "Title must be 200 characters or less",
            "code": "VALIDATION_ERROR",
            "task_id": None,
        }

    # Validate description
    if description and len(description) > 2000:
        return {
            "error": "Description must be 2000 characters or less",
            "code": "VALIDATION_ERROR",
            "task_id": None,
        }

    # Validate source
    if source not in ["manual", "chat"]:
        return {
            "error": "Source must be 'manual' or 'chat'",
            "code": "VALIDATION_ERROR",
            "task_id": None,
        }

    session = get_sync_session()
    try:
        # Create task with source tracking
        task = Task(
            user_id=user_uuid,
            title=title.strip(),
            description=description.strip() if description else None,
            source=source,
            created_by_thread_id=thread_id if source == "chat" else None,
            completed=False,
            priority="medium",
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        logger.info(f"Created task {task.id} for user {user_id}")

        return {"task_id": str(task.id), "status": "created", "title": task.title}
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to create task: {str(e)}")
        return {
            "error": f"Database error: {str(e)}",
            "code": "DATABASE_ERROR",
            "task_id": None,
        }
    finally:
        session.close()


@mcp.tool()
def list_tasks(user_id: str, status: str = "all") -> dict:
    """
    List tasks for a user with optional filtering.

    Args:
        user_id: UUID of the user
        status: Filter by completion status - "all", "pending", or "completed"

    Returns:
        dict: TaskListResponse with tasks array and total count
              OR ErrorResponse with error details
    """
    # Validate user_id
    user_uuid = _validate_uuid(user_id, "user_id")
    if not user_uuid:
        return {
            "error": "Invalid user_id format",
            "code": "VALIDATION_ERROR",
            "task_id": None,
        }

    # Validate status
    try:
        task_status = TaskStatus(status)
    except ValueError:
        return {
            "error": f"Invalid status '{status}'. Must be: all, pending, or completed",
            "code": "VALIDATION_ERROR",
            "task_id": None,
        }

    session = get_sync_session()
    try:
        # Build query based on status filter
        query = select(Task).where(Task.user_id == user_uuid)

        if task_status == TaskStatus.pending:
            query = query.where(Task.completed == False)  # noqa: E712
        elif task_status == TaskStatus.completed:
            query = query.where(Task.completed == True)  # noqa: E712

        # Order by creation date (newest first)
        query = query.order_by(Task.created_at.desc())

        tasks = session.exec(query).all()

        return {"tasks": [_task_to_detail(task) for task in tasks], "total": len(tasks)}
    except Exception as e:
        logger.error(f"Failed to list tasks: {str(e)}")
        return {
            "error": f"Database error: {str(e)}",
            "code": "DATABASE_ERROR",
            "task_id": None,
        }
    finally:
        session.close()


@mcp.tool()
def mark_complete(user_id: str, task_id: str) -> dict:
    """
    Mark a task as completed.

    This operation is idempotent - marking an already completed task
    will return success without error.

    Args:
        user_id: UUID of the user who owns the task
        task_id: UUID of the task to mark complete

    Returns:
        dict: TaskResponse with task_id, status="completed", and title
              OR ErrorResponse with error details
    """
    # Validate UUIDs
    user_uuid = _validate_uuid(user_id, "user_id")
    if not user_uuid:
        return {
            "error": "Invalid user_id format",
            "code": "VALIDATION_ERROR",
            "task_id": task_id,
        }

    task_uuid = _validate_uuid(task_id, "task_id")
    if not task_uuid:
        return {
            "error": "Invalid task_id format",
            "code": "VALIDATION_ERROR",
            "task_id": task_id,
        }

    session = get_sync_session()
    try:
        # Find task with user isolation
        task = session.exec(
            select(Task).where(Task.id == task_uuid, Task.user_id == user_uuid)
        ).first()

        if not task:
            return {"error": "Task not found", "code": "NOT_FOUND", "task_id": task_id}

        # Mark as complete (idempotent)
        task.completed = True
        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()

        logger.info(f"Marked task {task_id} as complete for user {user_id}")

        return {"task_id": str(task.id), "status": "completed", "title": task.title}
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to mark task complete: {str(e)}")
        return {
            "error": f"Database error: {str(e)}",
            "code": "DATABASE_ERROR",
            "task_id": task_id,
        }
    finally:
        session.close()


@mcp.tool()
def update_task(
    user_id: str, task_id: str, title: str | None = None, description: str | None = None
) -> dict:
    """
    Update task title and/or description.

    At least one of title or description must be provided.

    Args:
        user_id: UUID of the user who owns the task
        task_id: UUID of the task to update
        title: New task title (1-200 characters, optional)
        description: New task description (max 2000 characters, optional)

    Returns:
        dict: TaskResponse with task_id, status="updated", and title
              OR ErrorResponse with error details
    """
    # Validate at least one field is provided
    if title is None and description is None:
        return {
            "error": "At least one of title or description must be provided",
            "code": "VALIDATION_ERROR",
            "task_id": task_id,
        }

    # Validate UUIDs
    user_uuid = _validate_uuid(user_id, "user_id")
    if not user_uuid:
        return {
            "error": "Invalid user_id format",
            "code": "VALIDATION_ERROR",
            "task_id": task_id,
        }

    task_uuid = _validate_uuid(task_id, "task_id")
    if not task_uuid:
        return {
            "error": "Invalid task_id format",
            "code": "VALIDATION_ERROR",
            "task_id": task_id,
        }

    # Validate title if provided
    if title is not None:
        if len(title.strip()) == 0:
            return {
                "error": "Title cannot be empty",
                "code": "VALIDATION_ERROR",
                "task_id": task_id,
            }
        if len(title) > 200:
            return {
                "error": "Title must be 200 characters or less",
                "code": "VALIDATION_ERROR",
                "task_id": task_id,
            }

    # Validate description if provided
    if description is not None and len(description) > 2000:
        return {
            "error": "Description must be 2000 characters or less",
            "code": "VALIDATION_ERROR",
            "task_id": task_id,
        }

    session = get_sync_session()
    try:
        # Find task with user isolation
        task = session.exec(
            select(Task).where(Task.id == task_uuid, Task.user_id == user_uuid)
        ).first()

        if not task:
            return {"error": "Task not found", "code": "NOT_FOUND", "task_id": task_id}

        # Update fields
        if title is not None:
            task.title = title.strip()
        if description is not None:
            task.description = description.strip() if description else None

        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()

        logger.info(f"Updated task {task_id} for user {user_id}")

        return {"task_id": str(task.id), "status": "updated", "title": task.title}
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to update task: {str(e)}")
        return {
            "error": f"Database error: {str(e)}",
            "code": "DATABASE_ERROR",
            "task_id": task_id,
        }
    finally:
        session.close()


@mcp.tool()
def delete_task(user_id: str, task_id: str) -> dict:
    """
    Permanently delete a task.

    This operation cannot be undone.

    Args:
        user_id: UUID of the user who owns the task
        task_id: UUID of the task to delete

    Returns:
        dict: TaskResponse with task_id, status="deleted", and title
              OR ErrorResponse with error details
    """
    # Validate UUIDs
    user_uuid = _validate_uuid(user_id, "user_id")
    if not user_uuid:
        return {
            "error": "Invalid user_id format",
            "code": "VALIDATION_ERROR",
            "task_id": task_id,
        }

    task_uuid = _validate_uuid(task_id, "task_id")
    if not task_uuid:
        return {
            "error": "Invalid task_id format",
            "code": "VALIDATION_ERROR",
            "task_id": task_id,
        }

    session = get_sync_session()
    try:
        # Find task with user isolation
        task = session.exec(
            select(Task).where(Task.id == task_uuid, Task.user_id == user_uuid)
        ).first()

        if not task:
            return {"error": "Task not found", "code": "NOT_FOUND", "task_id": task_id}

        # Store title before deletion
        title = task.title

        # Delete task
        session.delete(task)
        session.commit()

        logger.info(f"Deleted task {task_id} for user {user_id}")

        return {"task_id": task_id, "status": "deleted", "title": title}
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to delete task: {str(e)}")
        return {
            "error": f"Database error: {str(e)}",
            "code": "DATABASE_ERROR",
            "task_id": task_id,
        }
    finally:
        session.close()


@mcp.tool()
def search_tasks(user_id: str, query: str) -> dict:
    """
    Search tasks by keyword in title or description.

    Performs case-insensitive search using PostgreSQL ILIKE.

    Args:
        user_id: UUID of the user
        query: Search query string (1-100 characters)

    Returns:
        dict: TaskListResponse with matching tasks and total count
              OR ErrorResponse with error details
    """
    # Validate user_id
    user_uuid = _validate_uuid(user_id, "user_id")
    if not user_uuid:
        return {
            "error": "Invalid user_id format",
            "code": "VALIDATION_ERROR",
            "task_id": None,
        }

    # Validate query
    if not query or len(query.strip()) == 0:
        return {
            "error": "Search query is required",
            "code": "VALIDATION_ERROR",
            "task_id": None,
        }

    if len(query) > 100:
        return {
            "error": "Search query must be 100 characters or less",
            "code": "VALIDATION_ERROR",
            "task_id": None,
        }

    session = get_sync_session()
    try:
        # Build search pattern for ILIKE
        search_pattern = f"%{query.strip()}%"

        # Search in title and description
        tasks = session.exec(
            select(Task)
            .where(
                Task.user_id == user_uuid,
                or_(
                    Task.title.ilike(search_pattern),
                    Task.description.ilike(search_pattern),
                ),
            )
            .order_by(Task.created_at.desc())
        ).all()

        return {"tasks": [_task_to_detail(task) for task in tasks], "total": len(tasks)}
    except Exception as e:
        logger.error(f"Failed to search tasks: {str(e)}")
        return {
            "error": f"Database error: {str(e)}",
            "code": "DATABASE_ERROR",
            "task_id": None,
        }
    finally:
        session.close()
