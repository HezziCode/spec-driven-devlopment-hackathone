"""Pydantic schemas for agent tool inputs and outputs."""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class TaskPriority(str, Enum):
    """Task priority levels."""

    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class ExtractedTaskDetails(BaseModel):
    """Task details extracted from natural language."""

    title: str = Field(..., description="Task title extracted from message")
    description: Optional[str] = Field(None, description="Task description if provided")
    priority: TaskPriority = Field(
        default=TaskPriority.medium, description="Inferred priority level"
    )
    due_date: Optional[str] = Field(
        None, description="Due date if mentioned (ISO 8601 format)"
    )


class TaskInfo(BaseModel):
    """Task information returned from tools."""

    id: str
    title: str
    description: Optional[str] = None
    completed: bool
    priority: str
    created_at: str
    updated_at: str


class TaskOperationResult(BaseModel):
    """Result of a task operation."""

    task_id: str
    status: str  # created, updated, deleted, completed
    title: str


class TaskListResult(BaseModel):
    """Result of listing tasks."""

    tasks: List[TaskInfo]
    total: int
