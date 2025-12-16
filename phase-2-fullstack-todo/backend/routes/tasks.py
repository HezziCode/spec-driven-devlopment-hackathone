from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List, Optional
from uuid import UUID

from db import get_session
from middleware.auth_middleware import get_user_id_from_token
from services.task_service import (
    create_task, get_user_tasks, get_task_by_id,
    update_task, delete_task, validate_task_data
)
from schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse, PriorityEnum

router = APIRouter(prefix="/users/{user_id}", tags=["tasks"])


@router.post("/tasks", response_model=TaskResponse, status_code=201)
async def create_user_task(
    user_id: UUID,
    task_data: TaskCreate,
    current_user_id: str = Depends(get_user_id_from_token),
    session: Session = Depends(get_session)
):
    """
    Create a new task for the authenticated user.
    """
    # Verify that the user_id in the path matches the authenticated user
    if str(user_id) != current_user_id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to create tasks for this user"
        )

    # Validate task data
    validation_errors = validate_task_data(task_data)
    if validation_errors:
        raise HTTPException(
            status_code=422,
            detail={"errors": validation_errors}
        )

    try:
        task = create_task(session, task_data, user_id)
        return task
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating task: {str(e)}"
        )


@router.get("/tasks", response_model=TaskListResponse)
async def get_user_tasks_list(
    user_id: UUID,
    current_user_id: str = Depends(get_user_id_from_token),
    session: Session = Depends(get_session),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    priority: Optional[PriorityEnum] = Query(None, description="Filter by priority"),
    tag: Optional[str] = Query(None, description="Filter by tag name"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    limit: int = Query(20, ge=1, le=100, description="Number of tasks to return"),
    offset: int = Query(0, ge=0, description="Number of tasks to skip")
):
    """
    Get all tasks for the authenticated user with optional filtering and pagination.
    """
    # Verify that the user_id in the path matches the authenticated user
    if str(user_id) != current_user_id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view tasks for this user"
        )

    try:
        tasks, total = get_user_tasks(
            session, user_id, completed, priority, tag, search, limit, offset
        )
        return TaskListResponse(tasks=tasks, total=total)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving tasks: {str(e)}"
        )


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_user_task(
    user_id: UUID,
    task_id: UUID,
    current_user_id: str = Depends(get_user_id_from_token),
    session: Session = Depends(get_session)
):
    """
    Get a specific task for the authenticated user.
    """
    # Verify that the user_id in the path matches the authenticated user
    if str(user_id) != current_user_id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view tasks for this user"
        )

    try:
        task = get_task_by_id(session, task_id, user_id)
        if not task:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )
        return task
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving task: {str(e)}"
        )


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_user_task(
    user_id: UUID,
    task_id: UUID,
    task_data: TaskUpdate,
    current_user_id: str = Depends(get_user_id_from_token),
    session: Session = Depends(get_session)
):
    """
    Update an existing task for the authenticated user.
    """
    # Verify that the user_id in the path matches the authenticated user
    if str(user_id) != current_user_id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to update tasks for this user"
        )

    try:
        task = update_task(session, task_id, task_data, user_id)
        if not task:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )
        return task
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating task: {str(e)}"
        )


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def partial_update_user_task(
    user_id: UUID,
    task_id: UUID,
    task_data: TaskUpdate,
    current_user_id: str = Depends(get_user_id_from_token),
    session: Session = Depends(get_session)
):
    """
    Partially update an existing task for the authenticated user.
    """
    # Verify that the user_id in the path matches the authenticated user
    if str(user_id) != current_user_id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to update tasks for this user"
        )

    try:
        task = update_task(session, task_id, task_data, user_id)
        if not task:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )
        return task
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating task: {str(e)}"
        )


@router.delete("/tasks/{task_id}")
async def delete_user_task(
    user_id: UUID,
    task_id: UUID,
    current_user_id: str = Depends(get_user_id_from_token),
    session: Session = Depends(get_session)
):
    """
    Delete a specific task for the authenticated user.
    """
    # Verify that the user_id in the path matches the authenticated user
    if str(user_id) != current_user_id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to delete tasks for this user"
        )

    try:
        success = delete_task(session, task_id, user_id)
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )
        return {"message": "Task deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting task: {str(e)}"
        )