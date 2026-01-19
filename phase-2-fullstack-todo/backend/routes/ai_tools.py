"""Direct HTTP endpoints for AI agent tool calls.

These endpoints provide a simple HTTP interface for AI agents to call
task management operations, bypassing the MCP server complexity.
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from db import get_session
from schemas.task import TaskCreate, TaskUpdate
from services import task_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai", tags=["AI Tools"])


class CreateTaskRequest(BaseModel):
    """Request model for creating a task via AI agent."""

    user_id: str
    title: str
    description: Optional[str] = ""
    tags: Optional[list[str]] = []
    priority: Optional[str] = "medium"
    source: str = "chat"
    thread_id: Optional[str] = None


class UpdateTaskRequest(BaseModel):
    """Request model for updating a task via AI agent."""

    user_id: str
    title: Optional[str] = None
    description: Optional[str] = None


class DeleteTaskRequest(BaseModel):
    """Request model for deleting a task via AI agent."""

    user_id: str


class DeleteTaskByNameRequest(BaseModel):
    """Request model for deleting a task by name via AI agent."""

    user_id: str
    task_name: str


class TaskResponse(BaseModel):
    """Response model for task operations."""

    task_id: str
    status: str
    title: str


@router.post("/tasks", response_model=TaskResponse)
async def create_task_for_ai(
    request: CreateTaskRequest, session: Session = Depends(get_session)
) -> TaskResponse:
    """
    Create a new task via AI agent.

    This endpoint is called by AI agents to create tasks from chat conversations.
    It bypasses authentication since the AI agent provides the user_id directly.
    """
    try:
        logger.info(
            f"AI agent creating task '{request.title}' for user {request.user_id}"
        )

        # Convert user_id string to UUID
        user_uuid = UUID(request.user_id)

        # Create task data
        task_data = TaskCreate(
            title=request.title,
            description=request.description or "",
            priority=request.priority or "medium",
            tags=request.tags or [],
        )

        # Create task using task service function
        task = task_service.create_task(
            session=session,
            task_data=task_data,
            user_id=user_uuid,
            source=request.source,
            thread_id=request.thread_id,
        )

        logger.info(f"AI agent created task {task.id} for user {request.user_id}")

        return TaskResponse(task_id=str(task.id), status="created", title=task.title)
    except ValueError as e:
        logger.error(f"Invalid user_id format: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid user_id: {str(e)}")
    except Exception as e:
        logger.error(f"Error creating task via AI agent: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create task: {str(e)}")


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task_for_ai(
    task_id: str, request: UpdateTaskRequest, session: Session = Depends(get_session)
) -> TaskResponse:
    """
    Update an existing task via AI agent.

    This endpoint is called by AI agents to update tasks from chat conversations.
    It bypasses authentication since the AI agent provides the user_id directly.
    """
    try:
        logger.info(f"AI agent updating task {task_id} for user {request.user_id}")

        # Convert user_id and task_id strings to UUIDs
        user_uuid = UUID(request.user_id)
        task_uuid = UUID(task_id)

        # Prepare update data
        update_data = TaskUpdate(
            title=request.title,
            description=request.description,
            completed=None,
            priority=None,
            tags=None,
        )

        # Update task using task service function
        task = task_service.update_task(
            session=session, task_id=task_uuid, task_data=update_data, user_id=user_uuid
        )

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        logger.info(f"AI agent updated task {task.id} for user {request.user_id}")

        return TaskResponse(task_id=str(task.id), status="updated", title=task.title)
    except ValueError as e:
        logger.error(f"Invalid user_id or task_id format: {e}")
        raise HTTPException(
            status_code=400, detail=f"Invalid user_id or task_id: {str(e)}"
        )
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Error updating task via AI agent: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update task: {str(e)}")


@router.delete("/tasks/{task_id}", response_model=TaskResponse)
async def delete_task_for_ai(
    task_id: str, request: DeleteTaskRequest, session: Session = Depends(get_session)
) -> TaskResponse:
    """
    Delete a task via AI agent.

    This endpoint is called by AI agents to delete tasks from chat conversations.
    It bypasses authentication since the AI agent provides the user_id directly.
    """
    try:
        logger.info(f"AI agent deleting task {task_id} for user {request.user_id}")

        # Convert user_id and task_id strings to UUIDs
        user_uuid = UUID(request.user_id)
        task_uuid = UUID(task_id)

        # Get task first to retrieve title before deletion
        task = task_service.get_task_by_id(
            session=session, task_id=task_uuid, user_id=user_uuid
        )

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Store title before deletion
        task_title = task.title

        # Delete task using task service function
        deleted = task_service.delete_task(
            session=session, task_id=task_uuid, user_id=user_uuid
        )

        if not deleted:
            raise HTTPException(status_code=404, detail="Task not found")

        logger.info(f"AI agent deleted task {task_uuid} for user {request.user_id}")

        return TaskResponse(task_id=str(task_uuid), status="deleted", title=task_title)
    except ValueError as e:
        logger.error(f"Invalid user_id or task_id format: {e}")
        raise HTTPException(
            status_code=400, detail=f"Invalid user_id or task_id: {str(e)}"
        )
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Error deleting task via AI agent: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to delete task: {str(e)}")


@router.post("/tasks/delete-by-name", response_model=TaskResponse)
async def delete_task_by_name_for_ai(
    request: DeleteTaskByNameRequest, session: Session = Depends(get_session)
) -> TaskResponse:
    """
    Delete a task by name via AI agent.

    This endpoint is called by AI agents to delete tasks by name from chat conversations.
    It bypasses authentication since the AI agent provides the user_id directly.
    """
    try:
        logger.info(
            f"AI agent deleting task by name '{request.task_name}' for user {request.user_id}"
        )

        # Convert user_id string to UUID
        user_uuid = UUID(request.user_id)

        # Get all tasks and find by name (case-insensitive)
        tasks, _ = task_service.get_user_tasks(session=session, user_id=user_uuid)

        # Find task by name (case-insensitive, trimmed)
        task_name_lower = request.task_name.lower().strip()
        matching_task = None
        for task in tasks:
            if task.title.lower().strip() == task_name_lower:
                matching_task = task
                break

        if not matching_task:
            raise HTTPException(
                status_code=404, detail=f"Task '{request.task_name}' not found"
            )

        # Store title before deletion
        task_title = matching_task.title
        task_id = matching_task.id

        # Delete task using task service function
        deleted = task_service.delete_task(
            session=session, task_id=task_id, user_id=user_uuid
        )

        if not deleted:
            raise HTTPException(status_code=404, detail="Task not found")

        logger.info(
            f"AI agent deleted task '{task_title}' (ID: {task_id}) for user {request.user_id}"
        )

        return TaskResponse(task_id=str(task_id), status="deleted", title=task_title)
    except ValueError as e:
        logger.error(f"Invalid user_id format: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid user_id: {str(e)}")
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Error deleting task by name via AI agent: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to delete task: {str(e)}")


class ListTasksRequest(BaseModel):
    """Request model for listing tasks via AI agent."""

    user_id: str
    status: Optional[str] = "all"  # all, pending, completed


@router.post("/tasks/list", response_model=dict)
async def list_tasks_for_ai(
    request: ListTasksRequest, session: Session = Depends(get_session)
) -> dict:
    """
    List tasks for a user via AI agent.

    This endpoint is called by AI agents to list tasks from chat conversations.
    It bypasses authentication since the AI agent provides the user_id directly.
    """
    try:
        logger.info(
            f"AI agent listing tasks for user {request.user_id} with status={request.status}"
        )

        # Convert user_id string to UUID
        user_uuid = UUID(request.user_id)

        # Map status to completed filter
        completed_filter = None
        if request.status == "pending":
            completed_filter = False
        elif request.status == "completed":
            completed_filter = True

        # Get tasks using task service function
        tasks, total = task_service.get_user_tasks(
            session=session, user_id=user_uuid, completed=completed_filter
        )

        logger.info(f"AI agent listed {len(tasks)} tasks for user {request.user_id}")

        return {
            "tasks": [
                {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "priority": task.priority,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat(),
                }
                for task in tasks
            ],
            "total": total,
        }
    except ValueError as e:
        logger.error(f"Invalid user_id format: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid user_id: {str(e)}")
    except Exception as e:
        logger.error(f"Error listing tasks via AI agent: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list tasks: {str(e)}")


class MarkCompleteRequest(BaseModel):
    """Request model for marking a task complete via AI agent."""

    user_id: str


@router.post("/tasks/{task_id}/complete", response_model=TaskResponse)
async def mark_task_complete_for_ai(
    task_id: str, request: MarkCompleteRequest, session: Session = Depends(get_session)
) -> TaskResponse:
    """
    Mark a task as completed via AI agent.

    This endpoint is called by AI agents to mark tasks complete from chat conversations.
    It bypasses authentication since the AI agent provides the user_id directly.
    """
    try:
        logger.info(
            f"AI agent marking task {task_id} complete for user {request.user_id}"
        )

        # Convert user_id and task_id strings to UUIDs
        user_uuid = UUID(request.user_id)
        task_uuid = UUID(task_id)

        # Update task using task service function
        update_data = TaskUpdate(completed=True)
        task = task_service.update_task(
            session=session, task_id=task_uuid, task_data=update_data, user_id=user_uuid
        )

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        logger.info(
            f"AI agent marked task {task.id} complete for user {request.user_id}"
        )

        return TaskResponse(task_id=str(task.id), status="completed", title=task.title)
    except ValueError as e:
        logger.error(f"Invalid user_id or task_id format: {e}")
        raise HTTPException(
            status_code=400, detail=f"Invalid user_id or task_id: {str(e)}"
        )
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Error marking task complete via AI agent: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to mark task complete: {str(e)}"
        )


class GetTaskRequest(BaseModel):
    """Request model for getting a specific task via AI agent."""

    user_id: str


@router.post("/tasks/{task_id}/get", response_model=dict)
async def get_task_for_ai(
    task_id: str, request: GetTaskRequest, session: Session = Depends(get_session)
) -> dict:
    """
    Get a specific task via AI agent.

    This endpoint is called by AI agents to retrieve task details from chat conversations.
    It bypasses authentication since the AI agent provides the user_id directly.
    """
    try:
        logger.info(f"AI agent getting task {task_id} for user {request.user_id}")

        # Convert user_id and task_id strings to UUIDs
        user_uuid = UUID(request.user_id)
        task_uuid = UUID(task_id)

        # Get task using task service function
        task = task_service.get_task_by_id(
            session=session, task_id=task_uuid, user_id=user_uuid
        )

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        logger.info(f"AI agent retrieved task {task.id} for user {request.user_id}")

        return {
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "priority": task.priority,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
        }
    except ValueError as e:
        logger.error(f"Invalid user_id or task_id format: {e}")
        raise HTTPException(
            status_code=400, detail=f"Invalid user_id or task_id: {str(e)}"
        )
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Error getting task via AI agent: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get task: {str(e)}")


class SearchTasksRequest(BaseModel):
    """Request model for searching tasks via AI agent."""

    user_id: str
    query: str


@router.post("/tasks/search", response_model=dict)
async def search_tasks_for_ai(
    request: SearchTasksRequest, session: Session = Depends(get_session)
) -> dict:
    """
    Search tasks via AI agent.

    This endpoint is called by AI agents to search tasks from chat conversations.
    It bypasses authentication since the AI agent provides the user_id directly.
    """
    try:
        logger.info(
            f"AI agent searching tasks for user {request.user_id} with query='{request.query}'"
        )

        # Convert user_id string to UUID
        user_uuid = UUID(request.user_id)

        # Use task service search functionality
        tasks, total = task_service.get_user_tasks(
            session=session, user_id=user_uuid, search=request.query
        )

        logger.info(
            f"AI agent found {len(tasks)} tasks matching '{request.query}' for user {request.user_id}"
        )

        return {
            "tasks": [
                {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "priority": task.priority,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat(),
                }
                for task in tasks
            ],
            "total": total,
        }
    except ValueError as e:
        logger.error(f"Invalid user_id format: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid user_id: {str(e)}")
    except Exception as e:
        logger.error(f"Error searching tasks via AI agent: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to search tasks: {str(e)}")
