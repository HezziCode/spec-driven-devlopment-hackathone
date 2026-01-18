"""Chat context dataclass for passing request context to agent tools."""

import os
from dataclasses import dataclass, field


@dataclass
class ChatContext:
    """Context passed to agent tool invocations during chat sessions.

    Attributes:
        user_id: UUID of the authenticated user
        thread_id: UUID of the conversation thread (None for new threads)
        mcp_base_url: Base URL for MCP server (defaults to localhost:8000/mcp)
    """

    user_id: str
    thread_id: str | None = None
    mcp_base_url: str = field(default_factory=lambda: os.getenv("MCP_BASE_URL", "http://localhost:8000") + "/mcp")
