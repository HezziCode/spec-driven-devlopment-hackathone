"""Streaming utilities for SSE response handling."""

import logging
from typing import AsyncGenerator

logger = logging.getLogger(__name__)


async def format_sse_event(
    event_type: str, data: str | dict[str, str]
) -> str:
    """Format data as an SSE event.

    Args:
        event_type: Type of the event (e.g., "message", "done", "error")
        data: Data to send (string or dict for JSON serialization)

    Returns:
        SSE-formatted event string
    """
    import json

    if isinstance(data, dict):
        data = json.dumps(data)

    return f"event: {event_type}\ndata: {data}\n\n"


class StreamingResponse:
    """Helper class for managing streaming responses.

    Provides utilities for creating and formatting SSE events.
    """

    @staticmethod
    async def text_event(content: str) -> str:
        """Create a text content event.

        Args:
            content: Text content to send

        Returns:
            SSE-formatted event
        """
        return f"data: {content}\n\n"

    @staticmethod
    async def tool_call_event(tool_name: str, arguments: dict[str, str]) -> str:
        """Create a tool call event.

        Args:
            tool_name: Name of the tool being called
            arguments: Tool arguments as dictionary

        Returns:
            SSE-formatted tool call event
        """
        import json

        return await format_sse_event(
            "tool_call",
            {"tool": tool_name, "arguments": arguments},
        )

    @staticmethod
    async def tool_result_event(
        tool_name: str, result: dict[str, str]
    ) -> str:
        """Create a tool result event.

        Args:
            tool_name: Name of the tool
            result: Tool result as dictionary

        Returns:
            SSE-formatted tool result event
        """
        import json

        return await format_sse_event(
            "tool_result",
            {"tool": tool_name, "result": result},
        )

    @staticmethod
    async def done_event(metadata: dict[str, str]) -> str:
        """Create a done event with metadata.

        Args:
            metadata: Response metadata (e.g., thread_id)

        Returns:
            SSE-formatted done event
        """
        return await format_sse_event("done", metadata)

    @staticmethod
    async def error_event(error_message: str) -> str:
        """Create an error event.

        Args:
            error_message: Error description

        Returns:
            SSE-formatted error event
        """
        return await format_sse_event("error", {"message": error_message})


async def stream_context(
    message: str, context: dict[str, str]
) -> AsyncGenerator[str, None]:
    """Stream a message with context information.

    Args:
        message: Main message content
        context: Additional context as key-value pairs

    Yields:
        SSE-formatted event strings
    """
    # Yield main message
    yield await StreamingResponse.text_event(message)

    # Yield context as metadata event
    yield await format_sse_event("context", context)
