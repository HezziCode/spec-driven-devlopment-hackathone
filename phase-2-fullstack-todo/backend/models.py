from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import Index, UniqueConstraint
import enum


class PriorityEnum(str, enum.Enum):
    """Enumeration for task priority levels."""
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class User(SQLModel, table=True):
    """
    User model representing a registered user in the system.

    Attributes:
        id: Unique identifier for the user (UUID).
        username: Unique username for the user (max 50 characters).
        email: Unique email address for the user (max 100 characters).
        password_hash: Hashed password for authentication (max 255 characters).
        created_at: Timestamp when the user was created.
        updated_at: Timestamp when the user was last updated.
        tasks: Relationship to user's tasks (one-to-many).
    """
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(unique=True, max_length=50, nullable=False, index=True)
    email: str = Field(unique=True, max_length=100, nullable=False, index=True)
    password_hash: str = Field(max_length=255, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship to tasks
    tasks: List["Task"] = Relationship(back_populates="user")


class Task(SQLModel, table=True):
    """
    Task model representing a todo task in the system.

    Attributes:
        id: Unique identifier for the task (UUID).
        user_id: Foreign key reference to the user who owns this task.
        title: Title/summary of the task (max 200 characters).
        description: Optional detailed description of the task (max 1000 characters).
        completed: Boolean flag indicating if the task is completed.
        priority: Priority level of the task (low, medium, high, critical).
        created_at: Timestamp when the task was created.
        updated_at: Timestamp when the task was last updated.
        user: Relationship to the task owner (many-to-one).
        tags: Relationship to task tags (one-to-many).
    """
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    title: str = Field(max_length=200, nullable=False)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False, nullable=False, index=True)
    priority: str = Field(default="medium", max_length=20, nullable=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship to user
    user: User = Relationship(back_populates="tasks")

    # Relationship to tags through task_tags table
    tags: List["TaskTag"] = Relationship(back_populates="task")

    # Composite index for efficient filtering by user_id and completed status
    __table_args__ = (
        Index("idx_user_completed", "user_id", "completed"),
    )


class TaskTag(SQLModel, table=True):
    """
    TaskTag model representing the many-to-many relationship between tasks and tags.

    Attributes:
        id: Unique identifier for the task-tag association (UUID).
        task_id: Foreign key reference to the associated task.
        tag_name: Name of the tag (max 50 characters).
        created_at: Timestamp when the association was created.
        task: Relationship to the associated task (many-to-one).
    """
    __tablename__ = "task_tags"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    task_id: UUID = Field(foreign_key="tasks.id", nullable=False, index=True)
    tag_name: str = Field(max_length=50, nullable=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship to task
    task: Task = Relationship(back_populates="tags")

    # Unique constraint to prevent duplicate tag assignments to the same task
    __table_args__ = (
        UniqueConstraint("task_id", "tag_name", name="uq_task_tag"),
    )


# Export all models for easy importing
__all__ = ["User", "Task", "TaskTag", "PriorityEnum"]