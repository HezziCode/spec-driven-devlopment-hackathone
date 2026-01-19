"""
Schemas package for Phase 2 Todo API.

This package contains Pydantic schemas for request/response validation.
"""

from .chat import ChatRequest, ChatResponse, ToolCall
from .chatkit import (
    ChatMessageResponse,
    ErrorResponse,
    StreamingResponse,
    ThreadListItem,
    ThreadListResponse,
    ThreadResponse,
)
from .chatkit import (
    ChatRequest as ChatKitRequest,
)

__all__ = [
    "task",
    "auth",
    "chat",
    "ChatRequest",
    "ChatResponse",
    "ToolCall",
    "ChatKitRequest",
    "ChatMessageResponse",
    "ThreadResponse",
    "ThreadListItem",
    "ThreadListResponse",
    "StreamingResponse",
    "ErrorResponse",
]
