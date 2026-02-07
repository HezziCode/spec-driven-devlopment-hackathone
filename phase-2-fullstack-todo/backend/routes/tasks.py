from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from db import get_session
from middleware.auth_middleware import get_user_id_from_token
from schemas.task import (
    PriorityEnum,
    SortEnum,
    TaskCreate,
    TaskListResponse,
    TaskResponse,
    TaskUpdate,
)
from services.task_service import (
    create_task,
    delete_task,
    get_task_by_id,
    get_user_tasks,
    update_task,
    validate_task_data,
)
from middleware.rate_limiter_simple import rate_limit_task_write, rate_limit_task_delete

router = APIRouter(prefix="/users/{user_id}", tags=["tasks"])


@router.post("/tasks", response_model=TaskResponse, status_code=201, dependencies=[Depends(rate_limit_task_write)])
async def create_user_task(
    user_id: UUID,
    task_data: TaskCreate,
    current_user_id: str = Depends(get_user_id_from_token),
    session: Session = Depends(get_session),
):
    """
    Create a new task for the authenticated user.
    """
    # Verify that the user_id in the path matches the authenticated user
    if str(user_id) != current_user_id:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "You can only create tasks for your own account",
                "code": "FORBIDDEN"
            }
        )

    # Validate task data
    validation_errors = validate_task_data(task_data)
    if validation_errors:
        error_message = ". ".join(validation_errors)
        raise HTTPException(
            status_code=422,
            detail={
                "error": f"Please fix the following: {error_message}",
                "code": "VALIDATION_ERROR"
            }
        )

    try:
        task = create_task(session, task_data, user_id)
        # Convert TaskTag objects to tag name strings
        task_dict = task.model_dump()
        task_dict["tags"] = [tag.tag_name for tag in task.tags] if task.tags else []
        return TaskResponse(**task_dict)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Unable to create task. Please try again.",
                "code": "SERVER_ERROR"
            }
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
    sort: SortEnum = Query(
        SortEnum.created, description="Sort by created/title/priority/updated"
    ),
    limit: int = Query(20, ge=1, le=100, description="Number of tasks to return"),
    offset: int = Query(0, ge=0, description="Number of tasks to skip"),
):
    """
    Get all tasks for the authenticated user with filtering, search, sorting, and pagination.
    """
    # Verify that the user_id in the path matches the authenticated user
    if str(user_id) != current_user_id:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "You can only view your own tasks",
                "code": "FORBIDDEN"
            }
        )

    try:
        tasks, total = get_user_tasks(
            session,
            user_id,
            completed,
            priority,
            tag,
            search,
            sort.value,
            limit,
            offset,
        )

        # Convert tasks to response format with string tags
        task_responses = []
        for task in tasks:
            task_dict = task.model_dump()
            task_dict["tags"] = [tag.tag_name for tag in task.tags] if task.tags else []
            task_responses.append(TaskResponse(**task_dict))

        # Calculate page number
        page = (offset // limit) + 1 if limit > 0 else 1

        return TaskListResponse(
            tasks=task_responses, total=total, page=page, limit=limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Unable to retrieve tasks. Please try again later.",
                "code": "SERVER_ERROR"
            }
        )


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_user_task(
    user_id: UUID,
    task_id: UUID,
    current_user_id: str = Depends(get_user_id_from_token),
    session: Session = Depends(get_session),
):
    """
    Get a specific task for the authenticated user.
    """
    # Verify that the user_id in the path matches the authenticated user
    if str(user_id) != current_user_id:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "You can only view your own tasks",
                "code": "FORBIDDEN"
            }
        )

    try:
        task = get_task_by_id(session, task_id, user_id)
        if not task:
            raise HTTPException(
            status_code=404,
            detail={
                "error": "Task not found or you don't have permission to access it",
                "code": "NOT_FOUND"
            }
        )
        # Convert TaskTag objects to tag name strings
        task_dict = task.model_dump()
        task_dict["tags"] = [tag.tag_name for tag in task.tags] if task.tags else []
        return TaskResponse(**task_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Unable to retrieve task. Please try again later.",
                "code": "SERVER_ERROR"
            }
        )


@router.put("/tasks/{task_id}", response_model=TaskResponse, dependencies=[Depends(rate_limit_task_write)])
async def update_user_task(
    user_id: UUID,
    task_id: UUID,
    task_data: TaskUpdate,
    current_user_id: str = Depends(get_user_id_from_token),
    session: Session = Depends(get_session),
):
    """
    Update an existing task for the authenticated user.
    """
    # Verify that the user_id in the path matches the authenticated user
    if str(user_id) != current_user_id:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "You can only update your own tasks",
                "code": "FORBIDDEN"
            }
        )

    try:
        task = update_task(session, task_id, task_data, user_id)
        if not task:
            raise HTTPException(
            status_code=404,
            detail={
                "error": "Task not found or you don't have permission to access it",
                "code": "NOT_FOUND"
            }
        )

        # Refresh to ensure tags are loaded from database
        session.refresh(task)

        # Build response dict manually to avoid SQLAlchemy state issues
        task_dict = {
            "id": task.id,
            "user_id": task.user_id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "priority": task.priority,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "tags": [],
        }

        # Safely convert TaskTag objects to strings
        if task.tags:
            task_dict["tags"] = [
                tag.tag_name if hasattr(tag, "tag_name") else str(tag)
                for tag in task.tags
            ]

        return TaskResponse(**task_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Unable to update task. Please try again later.",
                "code": "SERVER_ERROR"
            }
        )


@router.patch("/tasks/{task_id}", response_model=TaskResponse, dependencies=[Depends(rate_limit_task_write)])
async def partial_update_user_task(
    user_id: UUID,
    task_id: UUID,
    task_data: TaskUpdate,
    current_user_id: str = Depends(get_user_id_from_token),
    session: Session = Depends(get_session),
):
    """
    Partially update an existing task for the authenticated user.
    """
    # Verify that the user_id in the path matches the authenticated user
    if str(user_id) != current_user_id:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "You can only update your own tasks",
                "code": "FORBIDDEN"
            }
        )

    try:
        task = update_task(session, task_id, task_data, user_id)
        if not task:
            raise HTTPException(
            status_code=404,
            detail={
                "error": "Task not found or you don't have permission to access it",
                "code": "NOT_FOUND"
            }
        )

        # Refresh to ensure tags are loaded from database
        session.refresh(task)

        # Build response dict manually to avoid SQLAlchemy state issues
        task_dict = {
            "id": task.id,
            "user_id": task.user_id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "priority": task.priority,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "tags": [],
        }

        # Safely convert TaskTag objects to strings
        if task.tags:
            task_dict["tags"] = [
                tag.tag_name if hasattr(tag, "tag_name") else str(tag)
                for tag in task.tags
            ]

        return TaskResponse(**task_dict)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Unable to update task. Please try again later.",
                "code": "SERVER_ERROR"
            }
        )


@router.delete("/tasks/{task_id}", dependencies=[Depends(rate_limit_task_delete)])
async def delete_user_task(
    user_id: UUID,
    task_id: UUID,
    current_user_id: str = Depends(get_user_id_from_token),
    session: Session = Depends(get_session),
):
    """
    Delete a specific task for the authenticated user.
    """
    # Verify that the user_id in the path matches the authenticated user
    if str(user_id) != current_user_id:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "You can only delete your own tasks",
                "code": "FORBIDDEN"
            }
        )

    try:
        success = delete_task(session, task_id, user_id)
        if not success:
            raise HTTPException(
            status_code=404,
            detail={
                "error": "Task not found or you don't have permission to access it",
                "code": "NOT_FOUND"
            }
        )
        return {"message": "Task deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Unable to delete task. Please try again later.",
                "code": "SERVER_ERROR"
            }
        )
