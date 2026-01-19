"""Pydantic schemas for ChatKit chat endpoint."""

from typing import List, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request body for ChatKit streaming chat endpoint.

    Attributes:
        thread_id: Optional existing thread ID to continue conversation.
        message: User's message content (required).
    """

    thread_id: Optional[str] = Field(
        None,
        description="Existing thread ID to continue conversation. Creates new thread if not provided.",
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="User's natural language message",
    )


class ChatMessageResponse(BaseModel):
    """Individual message in a thread response.

    Attributes:
        id: Message unique identifier.
        role: Message sender role ('user' or 'assistant').
        content: Message text content.
        created_at: Timestamp when message was created.
    """

    id: str = Field(..., description="Message unique identifier")
    role: str = Field(..., description="Message sender role ('user' or 'assistant')")
    content: str = Field(..., description="Message text content")
    created_at: str = Field(..., description="ISO timestamp of message creation")


class ThreadResponse(BaseModel):
    """Thread with its messages for GET thread/{id} endpoint.

    Attributes:
        id: Thread unique identifier.
        name: Thread name/title.
        user_id: Owner user ID.
        created_at: Thread creation timestamp.
        updated_at: Last update timestamp.
        messages: List of messages in the thread.
    """

    id: str = Field(..., description="Thread unique identifier")
    name: str = Field(..., description="Thread name/title")
    user_id: str = Field(..., description="Owner user ID")
    created_at: str = Field(..., description="ISO timestamp of thread creation")
    updated_at: str = Field(..., description="ISO timestamp of last update")
    messages: List[ChatMessageResponse] = Field(
        ..., description="List of messages in the thread"
    )


class ThreadListItem(BaseModel):
    """Thread metadata for list endpoint.

    Attributes:
        id: Thread unique identifier.
        name: Thread name/title.
        message_count: Number of messages in thread.
        created_at: Thread creation timestamp.
        updated_at: Last update timestamp.
    """

    id: str = Field(..., description="Thread unique identifier")
    name: str = Field(..., description="Thread name/title")
    message_count: int = Field(..., description="Number of messages in thread")
    created_at: str = Field(..., description="ISO timestamp of thread creation")
    updated_at: str = Field(..., description="ISO timestamp of last update")


class ThreadListResponse(BaseModel):
    """Response for listing user's threads.

    Attributes:
        threads: List of thread metadata.
        total: Total number of threads.
    """

    threads: List[ThreadListItem] = Field(..., description="List of user's threads")
    total: int = Field(..., description="Total number of threads")


class StreamingResponse(BaseModel):
    """Schema for streaming response metadata (sent in 'done' event).

    Attributes:
        thread_id: ID of the thread where message was added.
    """

    thread_id: str = Field(..., description="Thread ID where message was added")


class ErrorResponse(BaseModel):
    """Error response schema.

    Attributes:
        error: Error message.
        code: Error code for programmatic handling.
    """

    error: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")


# ==================== ChatKit Session Management Schemas ====================


class SessionResponse(BaseModel):
    """
    Response schema for ChatKit session creation.

    Attributes:
        client_secret: ChatKit client secret for establishing session.
        expires_at: ISO 8601 timestamp when session expires.
    """

    client_secret: str = Field(
        ...,
        description="ChatKit client secret for session establishment",
        examples=["cs_1234567890abcdef"],
    )
    expires_at: str = Field(
        ...,
        description="ISO 8601 timestamp when session expires",
        examples=["2025-12-31T23:59:59Z"],
    )


class ThreadSyncRequest(BaseModel):
    """
    Request schema for syncing thread metadata to backend.

    Attributes:
        thread_id: ChatKit thread identifier.
        name: Display name for the thread.
        last_message_preview: Preview of the last message (optional).
        message_count: Total number of messages in thread.
    """

    thread_id: str = Field(
        ...,
        max_length=100,
        description="ChatKit thread identifier",
        examples=["thread_abc123"],
    )
    name: str = Field(
        ...,
        max_length=100,
        description="Display name for the thread",
        examples=["Task Planning Discussion"],
    )
    last_message_preview: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Preview of the last message",
        examples=["Can you help me create a task for..."],
    )
    message_count: int = Field(
        ..., ge=0, description="Total number of messages in thread", examples=[15]
    )


class ThreadItemResponse(BaseModel):
    """
    Schema for a single thread in list responses.

    Attributes:
        id: Unique thread identifier from ChatKit.
        name: Display name for the thread.
        last_message_preview: Preview of the last message (nullable).
        message_count: Total number of messages in thread.
        created_at: Thread creation timestamp.
        updated_at: Last update timestamp.
    """

    id: str = Field(
        ...,
        description="Unique thread identifier from ChatKit",
        examples=["thread_abc123"],
    )
    name: str = Field(
        ...,
        description="Display name for the thread",
        examples=["Task Planning Discussion"],
    )
    last_message_preview: Optional[str] = Field(
        default=None,
        description="Preview of the last message in thread",
        examples=["Can you help me create a task for..."],
    )
    message_count: int = Field(
        ..., description="Total number of messages in thread", examples=[15]
    )
    created_at: str = Field(
        ..., description="Thread creation timestamp", examples=["2025-12-30T10:00:00Z"]
    )
    updated_at: str = Field(
        ..., description="Last update timestamp", examples=["2025-12-31T14:30:00Z"]
    )


class ThreadListResponseV2(BaseModel):
    """
    Response schema for ChatKit thread list endpoint.

    Attributes:
        threads: Array of thread objects.
        total: Total number of threads for this user.
    """

    threads: List[ThreadItemResponse] = Field(
        ..., description="Array of thread objects"
    )
    total: int = Field(
        ..., ge=0, description="Total number of threads for this user", examples=[25]
    )
