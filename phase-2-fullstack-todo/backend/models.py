from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4
import enum

class PriorityEnum(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class User(SQLModel, table=True):
    """
    User model representing a registered user in the system.
    """
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(unique=True, max_length=50, nullable=False)
    email: str = Field(unique=True, max_length=100, nullable=False)
    password_hash: str = Field(max_length=255, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship to tasks
    tasks: List["Task"] = Relationship(back_populates="user")

class Task(SQLModel, table=True):
    """
    Task model representing a todo task in the system.
    """
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", nullable=False)
    title: str = Field(max_length=200, nullable=False)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False, nullable=False)
    priority: PriorityEnum = Field(default=PriorityEnum.medium, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship to user
    user: User = Relationship(back_populates="tasks")

    # Relationship to tags through task_tags table
    tags: List["TaskTag"] = Relationship(back_populates="task")

class TaskTag(SQLModel, table=True):
    """
    TaskTag model representing the many-to-many relationship between tasks and tags.
    """
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    task_id: UUID = Field(foreign_key="task.id", nullable=False)
    tag_name: str = Field(max_length=50, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    task: Task = Relationship(back_populates="tags")