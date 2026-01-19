"""Context dataclass for agent execution."""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class AgentContext:
    """Context passed to all agent tool invocations.

    Attributes:
        user_id: UUID of authenticated user
        jwt_token: JWT token for authenticating internal API calls
        conversation_id: Optional conversation ID for context
        mcp_base_url: Base URL for MCP server (internal, configurable via env)
    """

    user_id: str
    jwt_token: Optional[str] = None
    conversation_id: Optional[str] = None
    mcp_base_url: str = None

    def __post_init__(self):
        """Set default mcp_base_url from environment if not provided."""
        if self.mcp_base_url is None:
            self.mcp_base_url = os.getenv("MCP_BASE_URL", "http://localhost:8000")
