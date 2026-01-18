"""
Schemas package for Phase 2 Todo API.

This package contains Pydantic schemas for request/response validation.
"""

from .chat import ChatRequest, ChatResponse, ToolCall
from .chatkit import (
    ChatRequest as ChatKitRequest,
    ChatMessageResponse,
    ThreadResponse,
    ThreadListItem,
    ThreadListResponse,
    StreamingResponse,
    ErrorResponse,
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
