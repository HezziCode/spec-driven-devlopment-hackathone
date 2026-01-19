"""ChatKitServer class for handling chat requests with streaming responses."""

import json
import logging
from typing import AsyncGenerator

from agents import Agent
from sqlmodel import Session

from ai_agents.context import AgentContext
from chatkit.thread_manager import ThreadManager

logger = logging.getLogger(__name__)


class ChatKitServer:
    """Server for handling AI chat requests with streaming responses.

    Uses OpenAI Agents SDK's Runner.run_streamed() for streaming inference
    and maintains conversation context via ThreadManager.
    """

    def __init__(self, agent: Agent, session: Session) -> None:
        """Initialize the chat server.

        Args:
            agent: The OpenAI Agents SDK agent to use for responses
            session: SQLModel Session for database operations
        """
        self.agent = agent
        self.thread_manager = ThreadManager(session)

    async def respond(
        self, user_id: str, thread_id: str | None, message: str, jwt_token: str
    ) -> AsyncGenerator[str, None]:
        """Generate streaming response to a user message.

        Uses Runner.run_streamed() with AgentContext to pass user_id, jwt_token,
        and thread_id to all tool invocations.

        Args:
            user_id: UUID of the authenticated user
            thread_id: UUID of existing thread or None for new thread
            message: User's message content
            jwt_token: JWT token for authenticating internal API calls

        Yields:
            SSE-formatted text events containing response tokens
        """
        # Get or create thread
        if thread_id:
            thread = self.thread_manager.get_thread(user_id, thread_id)
            if not thread:
                raise ValueError(f"Thread {thread_id} not found")
        else:
            thread = self.thread_manager.create_thread(user_id, title=message[:50])
            thread_id = str(thread.id)

        # Add user message to thread (FIXED: added missing user_id parameter)
        self.thread_manager.add_message(thread_id, user_id, "user", message)

        # Get conversation history (last 20 messages)
        history = self.thread_manager.get_recent_messages(thread_id)

        # Create agent context with user_id, jwt_token, thread_id, and mcp_base_url
        # AgentContext is required for agent tools to call MCP server with proper auth
        agent_context = AgentContext(
            user_id=user_id, jwt_token=jwt_token, conversation_id=thread_id
        )

        # Build conversation messages
        messages = [{"role": msg["role"], "content": msg["content"]} for msg in history]

        logger.info(f"Starting streaming response for thread {thread_id}")

        try:
            # Use the OpenAI Agents SDK Runner for streaming
            from agents import Runner
            from openai.types.responses import ResponseTextDeltaEvent

            # Use the agent passed in constructor
            # Runner.run_streamed() automatically picks up OPENAI_API_KEY from environment
            result = Runner.run_streamed(
                self.agent, input=message, context=agent_context
            )

            # Stream the response with proper SSE format
            assistant_response = ""
            async for event in result.stream_events():
                # Handle raw response events with text deltas
                if event.type == "raw_response_event":
                    if isinstance(event.data, ResponseTextDeltaEvent):
                        delta = event.data.delta
                        assistant_response += delta
                        # FIXED: Use proper SSE format with JSON-encoded content
                        yield f"data: {json.dumps({'content': delta})}\n\n"

            # Add assistant message to thread (FIXED: added missing user_id parameter)
            if assistant_response:
                self.thread_manager.add_message(
                    thread_id, user_id, "assistant", assistant_response
                )

            # Send completion event with thread_id and message metadata
            yield "event: done\n"
            yield f"data: {json.dumps({'thread_id': thread_id, 'message_id': str(thread.id)})}\n\n"

        except Exception as e:
            logger.error(f"Error in streaming response: {e}")
            yield f"event: error\ndata: {str(e)}\n\n"
