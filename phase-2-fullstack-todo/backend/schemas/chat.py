"""Pydantic schemas for chat endpoint."""

from typing import List, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request body for chat endpoint."""

    conversation_id: Optional[str] = Field(
        None, description="Existing conversation ID. Creates new if not provided."
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="User's natural language message",
    )


class ToolCall(BaseModel):
    """Record of a tool invocation by the agent."""

    tool_name: str = Field(..., description="Name of tool called")
    arguments: dict = Field(
        default_factory=dict, description="Arguments passed to tool"
    )
    result: dict = Field(default_factory=dict, description="Result returned by tool")


class ChatResponse(BaseModel):
    """Response from chat endpoint."""

    conversation_id: str = Field(..., description="Conversation ID")
    response: str = Field(..., description="AI assistant's response")
    tool_calls: List[ToolCall] = Field(
        default_factory=list, description="List of MCP tools invoked"
    )
