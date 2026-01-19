"""
Pydantic schemas for MCP tool inputs and outputs.

This module defines all input validation schemas and response models
used by the MCP tools for todo management.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class TaskStatus(str, Enum):
    """Filter status for listing tasks."""

    all = "all"
    pending = "pending"
    completed = "completed"


# =============================================================================
# Input Schemas
# =============================================================================


class CreateTaskInput(BaseModel):
    """Input schema for create_task tool."""

    user_id: str = Field(..., description="User UUID who owns the task")
    title: str = Field(
        ..., min_length=1, max_length=200, description="Task title (1-200 characters)"
    )
    description: str = Field(
        "",
        max_length=2000,
        description="Optional task description (max 2000 characters)",
    )


class ListTasksInput(BaseModel):
    """Input schema for list_tasks tool."""

    user_id: str = Field(..., description="User UUID")
    status: TaskStatus = Field(
        TaskStatus.all,
        description="Filter by completion status: all, pending, or completed",
    )


class TaskIdInput(BaseModel):
    """Input schema for single task operations (mark_complete, delete)."""

    user_id: str = Field(..., description="User UUID who owns the task")
    task_id: str = Field(..., description="Task UUID to operate on")


class UpdateTaskInput(BaseModel):
    """Input schema for update_task tool."""

    user_id: str = Field(..., description="User UUID who owns the task")
    task_id: str = Field(..., description="Task UUID to update")
    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="New task title (1-200 characters)",
    )
    description: Optional[str] = Field(
        None, max_length=2000, description="New task description (max 2000 characters)"
    )

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "UpdateTaskInput":
        """Validate that at least one of title or description is provided."""
        if self.title is None and self.description is None:
            raise ValueError("At least one of title or description must be provided")
        return self


class SearchTasksInput(BaseModel):
    """Input schema for search_tasks tool."""

    user_id: str = Field(..., description="User UUID")
    query: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Search query string (1-100 characters)",
    )


# =============================================================================
# Output Schemas
# =============================================================================


class TaskResponse(BaseModel):
    """Standard response for single task operations."""

    task_id: str = Field(..., description="UUID of the task")
    status: str = Field(
        ..., description="Operation status: created, updated, deleted, or completed"
    )
    title: str = Field(..., description="Task title for confirmation")


class TaskDetail(BaseModel):
    """Task details in list responses."""

    id: str = Field(..., description="Task UUID")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    completed: bool = Field(..., description="Whether task is completed")
    priority: str = Field(..., description="Task priority level")
    created_at: str = Field(..., description="ISO 8601 creation timestamp")
    updated_at: str = Field(..., description="ISO 8601 last update timestamp")


class TaskListResponse(BaseModel):
    """Response for list/search operations."""

    tasks: list[TaskDetail] = Field(
        default_factory=list, description="List of task details"
    )
    total: int = Field(..., description="Total count of tasks in result")


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str = Field(..., description="Human-readable error message")
    code: str = Field(
        ...,
        description="Error code: NOT_FOUND, VALIDATION_ERROR, DATABASE_ERROR, USER_NOT_FOUND",
    )
    task_id: Optional[str] = Field(
        None, description="Task ID if applicable to the error"
    )
