import enum
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import validator
from sqlalchemy import JSON, Index, UniqueConstraint
from sqlmodel import Column, Field, Relationship, SQLModel


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
        password_hash: Hashed password for authentication (max 255 characters, nullable for OAuth users).
        auth_provider: Authentication method ('local' for email/password, 'google' for Google OAuth).
        google_id: Google user ID from OAuth (unique, nullable).
        oauth_data: JSON data storing Google profile information (nullable).
        created_at: Timestamp when the user was created.
        updated_at: Timestamp when the user was last updated.
        tasks: Relationship to user's tasks (one-to-many).
    """

    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(unique=True, max_length=50, nullable=False, index=True)
    email: str = Field(unique=True, max_length=100, nullable=False, index=True)
    password_hash: Optional[str] = Field(default=None, max_length=255, nullable=True)
    auth_provider: str = Field(
        default="local", max_length=20, nullable=False, index=True
    )
    google_id: Optional[str] = Field(
        default=None, max_length=255, unique=True, nullable=True, index=True
    )
    oauth_data: Optional[str] = Field(
        default=None, sa_column=Column(JSON, nullable=True)
    )
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)

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
        source: Creation source ('manual' for user-created, 'chat' for AI-created).
        created_by_thread_id: Optional reference to chat thread that created this task.
        created_at: Timestamp when the task was created.
        updated_at: Timestamp when the task was last updated.
        user: Relationship to the task owner (many-to-one).
        tags: Relationship to task tags (one-to-many).
        created_by_thread: Optional relationship to the chat thread that created this task.
    """

    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    title: str = Field(max_length=200, nullable=False)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False, nullable=False, index=True)
    priority: str = Field(default="medium", max_length=20, nullable=False, index=True)
    source: str = Field(default="manual", max_length=50, nullable=False, index=True)
    created_by_thread_id: Optional[str] = Field(
        default=None, foreign_key="chat_threads.id", nullable=True, max_length=100
    )
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)

    # Relationship to user
    user: User = Relationship(back_populates="tasks")

    # Relationship to tags through task_tags table
    tags: List["TaskTag"] = Relationship(back_populates="task")

    # Relationship to chat thread (optional, for chat-created tasks)
    created_by_thread: Optional["ChatThread"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Task.created_by_thread_id]"}
    )

    # Composite index for efficient filtering by user_id and completed status
    __table_args__ = (
        Index("idx_user_completed", "user_id", "completed"),
        Index("idx_task_source", "source"),
    )

    @validator("source")
    def validate_source(cls, v):
        """Validate that source is either 'manual' or 'chat'."""
        if v not in ["manual", "chat"]:
            raise ValueError("Source must be 'manual' or 'chat'")
        return v


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
    __table_args__ = (UniqueConstraint("task_id", "tag_name", name="uq_task_tag"),)


class Conversation(SQLModel, table=True):
    """
    Conversation model for chat sessions between users and AI agent.

    Attributes:
        id: Unique identifier for conversation (UUID).
        user_id: Foreign key reference to user who owns this conversation.
        created_at: Timestamp when conversation was created.
        updated_at: Timestamp when conversation was last updated.
        messages: Relationship to conversation messages (one-to-many).
    """

    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)

    # Relationship to messages
    messages: List["Message"] = Relationship(back_populates="conversation")


class Message(SQLModel, table=True):
    """
    Message model for conversation history.

    Attributes:
        id: Unique identifier for message (UUID).
        user_id: Foreign key reference to user who sent this message.
        conversation_id: Foreign key reference to conversation this message belongs to.
        role: Role of message sender ('user' or 'assistant').
        content: Text content of the message.
        created_at: Timestamp when message was created.
        conversation: Relationship to parent conversation (many-to-one).
    """

    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    conversation_id: UUID = Field(
        foreign_key="conversations.id", nullable=False, index=True
    )
    role: str = Field(max_length=20, nullable=False)
    content: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship to conversation
    conversation: Optional[Conversation] = Relationship(back_populates="messages")

    # Composite index for efficient conversation retrieval by user
    __table_args__ = (Index("idx_conversation_user", "conversation_id", "user_id"),)


class Thread(SQLModel, table=True):
    """Thread model for ChatKit conversation threads.

    Note: This is a legacy model. Use ChatThread for new implementations.

    Attributes:
        id: Unique identifier for thread (UUID).
        user_id: Foreign key reference to user who owns this thread.
        title: Thread title (auto-generated from first message).
        created_at: Timestamp when thread was created.
        updated_at: Timestamp when thread was last updated.
    """

    __tablename__ = "threads"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    title: str = Field(max_length=200, nullable=False)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)

    # Index for user's threads ordered by updated_at
    __table_args__ = (Index("idx_thread_user_updated", "user_id", "updated_at"),)


class ChatMessage(SQLModel, table=True):
    """ChatMessage model for ChatKit conversation messages.

    Attributes:
        id: Unique identifier for message (UUID).
        thread_id: Foreign key reference to chat_threads table (string to match ChatThread.id).
        user_id: Foreign key reference to user who owns this message (for isolation).
        role: Role of message sender ('user' or 'assistant').
        content: Text content of the message.
        created_at: Timestamp when message was created.
        thread: Relationship to parent thread (many-to-one).
    """

    __tablename__ = "chat_messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    thread_id: str = Field(
        foreign_key="chat_threads.id", nullable=False, index=True, max_length=100
    )
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    role: str = Field(max_length=20, nullable=False)
    content: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship to thread (will be cascade deleted when thread is deleted)
    thread: Optional["ChatThread"] = Relationship(back_populates="messages")

    # Index for efficient message retrieval within thread
    __table_args__ = (
        Index("idx_chatmessage_thread_created", "thread_id", "created_at"),
        Index("idx_chatmessage_user", "user_id"),
    )

    @validator("role")
    def validate_role(cls, v):
        """Validate that role is either 'user' or 'assistant'."""
        if v not in ["user", "assistant"]:
            raise ValueError("Role must be 'user' or 'assistant'")
        return v

    @validator("content")
    def validate_content(cls, v):
        """Validate that content is not empty."""
        if not v or not v.strip():
            raise ValueError("Content cannot be empty")
        return v.strip()


# REMOVED: ChatKitSession model - not needed for basic chat functionality


class ChatThread(SQLModel, table=True):
    """
    ChatThread model for persisting chat thread metadata.

    Attributes:
        id: Thread identifier from ChatKit (string, not UUID).
        user_id: Foreign key reference to user who owns this thread.
        name: Display name for the thread (max 100 characters).
        last_message_preview: Preview of the last message (max 200 characters, nullable).
        message_count: Total number of messages in thread.
        created_at: Timestamp when thread was created.
        updated_at: Timestamp when thread was last updated.
        messages: Relationship to thread messages (one-to-many, cascade delete).
        tasks: Relationship to tasks created from this thread (one-to-many).
    """

    __tablename__ = "chat_threads"

    id: str = Field(primary_key=True, max_length=100)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    name: str = Field(default="New Chat", max_length=100, nullable=False)
    last_message_preview: Optional[str] = Field(default=None, max_length=200)
    message_count: int = Field(default=0, ge=0, nullable=False)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)

    # Relationships
    messages: List["ChatMessage"] = Relationship(
        back_populates="thread",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "passive_deletes": True,
            "order_by": "ChatMessage.created_at",
        },
    )

    tasks: List["Task"] = Relationship(
        back_populates="created_by_thread",
        sa_relationship_kwargs={"passive_deletes": True},
    )

    # Index for efficient thread list retrieval sorted by updated_at
    __table_args__ = (Index("idx_chat_thread_user_updated", "user_id", "updated_at"),)


# REMOVED: ClientEffectEvent and ChatTool models - not needed for basic chat functionality


# Export all models for easy importing
__all__ = [
    "User",
    "Task",
    "TaskTag",
    "PriorityEnum",
    "ChatMessage",
    "ChatThread",
]
