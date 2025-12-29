from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from enum import Enum

class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class SortEnum(str, Enum):
    """Sort options for task lists."""
    created = "created"
    title = "title"
    priority = "priority"
    updated = "updated"

class StatusEnum(str, Enum):
    """Status filter options."""
    pending = "pending"
    completed = "completed"
    all = "all"

class TaskBase(BaseModel):
    """
    Base schema for task operations.
    """
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    priority: Optional[PriorityEnum] = Field(default=PriorityEnum.medium)

class TaskCreate(TaskBase):
    """
    Schema for creating a new task.
    """
    tags: Optional[List[str]] = Field(default=[], max_length=10)

class TaskUpdate(TaskBase):
    """
    Schema for updating an existing task.
    """
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    completed: Optional[bool] = None
    tags: Optional[List[str]] = Field(default=[], max_length=10)

class TaskResponse(TaskBase):
    """
    Schema for task response.
    """
    id: UUID
    completed: bool
    tags: List[str]
    user_id: UUID
    created_at: datetime
    updated_at: datetime

class TaskListResponse(BaseModel):
    """
    Schema for task list response with pagination metadata.
    """
    tasks: List[TaskResponse]
    total: int
    page: int = Field(..., description="Current page number (1-indexed)")
    limit: int = Field(..., description="Items per page")