"""Chat service for orchestrating agent conversations.

This service manages conversation persistence, message history,
and agent execution for natural language task management.
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import List, Optional

from agents import Runner
from sqlmodel import select

from ai_agents import task_manager_agent
from ai_agents.context import AgentContext
from db import get_session
from models import Conversation, Message

logger = logging.getLogger(__name__)

# Persistence is now synchronous - no background worker needed
# Functions kept for backward compatibility but are no-ops


async def start_persistence_worker():
    """No-op: Persistence is now synchronous and guaranteed."""
    logger.info("Persistence is synchronous - no background worker needed")


def stop_persistence_worker():
    """No-op: Persistence is now synchronous and guaranteed."""
    logger.info("Persistence worker not needed - using synchronous persistence")


async def create_conversation(user_id: str) -> str:
    """Create a new conversation for the user.

    Args:
        user_id: UUID of the authenticated user

    Returns:
        str: The new conversation ID
    """
    try:
        with get_session() as session:
            conversation = Conversation(user_id=user_id)
            session.add(conversation)
            session.commit()
            session.refresh(conversation)
            logger.info(f"Created conversation {conversation.id} for user {user_id}")
            return str(conversation.id)
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise


async def get_conversation_messages(
    conversation_id: str, limit: int = 20
) -> List[dict]:
    """Retrieve message history for a conversation.

    Args:
        conversation_id: UUID of the conversation
        limit: Maximum number of messages to retrieve (default: 20)

    Returns:
        List[dict]: Message history with role, content, and timestamp
    """
    try:
        with get_session() as session:
            messages = session.exec(
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.created_at)
                .limit(limit)
            ).all()

            return [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat(),
                }
                for msg in messages
            ]
    except Exception as e:
        logger.error(f"Error retrieving conversation messages: {e}")
        raise


def _store_message_sync(
    conversation_id: str, user_id: str, role: str, content: str
) -> bool:
    """Synchronously store a message in the database with retry.

    This is the CONTRACT-BASED guarantee: message WILL be persisted
    before this function returns, or an exception is raised.

    Args:
        conversation_id: UUID of the conversation
        user_id: UUID of the user
        role: 'user' or 'assistant'
        content: Message content

    Returns:
        bool: True if persisted successfully

    Raises:
        RuntimeError: If persistence fails after all retries
    """
    import time

    max_retries = 3
    last_error = None

    for attempt in range(max_retries):
        try:
            with get_session() as session:
                message = Message(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    role=role,
                    content=content,
                )
                session.add(message)
                session.commit()
                logger.info(
                    f"PERSISTED {role} message for conversation {conversation_id} "
                    f"(attempt {attempt + 1})"
                )
                return True
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 1s, 2s
                logger.warning(
                    f"Persistence failed (attempt {attempt + 1}), "
                    f"retrying in {wait_time}s: {e}"
                )
                time.sleep(wait_time)
            else:
                logger.error(
                    f"CRITICAL: Failed to persist {role} message after "
                    f"{max_retries} attempts: {e}"
                )

    # This is a critical failure - raise to signal the issue
    raise RuntimeError(
        f"Failed to persist {role} message after {max_retries} attempts: {last_error}"
    )


async def store_message(
    conversation_id: str, user_id: str, role: str, content: str
) -> None:
    """Store a user or assistant message in the database.

    CONTRACT: This function GUARANTEES the message is persisted before returning.
    Both user and assistant messages are stored synchronously to ensure durability.

    Args:
        conversation_id: UUID of the conversation
        user_id: UUID of the user
        role: 'user' or 'assistant'
        content: Message content

    Returns:
        None

    Raises:
        RuntimeError: If message cannot be persisted after retries
    """
    # Run synchronous persistence in thread pool to not block event loop
    # but WAIT for completion before returning
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        _store_message_sync,
        conversation_id,
        user_id,
        role,
        content,
    )
    logger.debug(f"Guaranteed persistence complete for {role} message")


async def process_message(
    user_id: str, conversation_id: Optional[str], message: str
) -> dict:
    """Process a user message through the agent.

    Args:
        user_id: UUID of the authenticated user
        conversation_id: Optional existing conversation ID
        message: User's natural language message

    Returns:
        dict with conversation_id, response, and tool_calls
    """
    try:
        # Create new conversation if not provided
        if conversation_id is None:
            conversation_id = await create_conversation(user_id)
            logger.info(f"Created new conversation {conversation_id}")

        # Get conversation history for context
        messages = await get_conversation_messages(conversation_id)

        # Build input messages for the agent
        input_messages = [
            {"role": msg["role"], "content": msg["content"]} for msg in messages
        ]
        input_messages.append({"role": "user", "content": message})

        # Store user message
        await store_message(conversation_id, user_id, "user", message)

        # Create agent context
        context = AgentContext(
            user_id=user_id,
            conversation_id=conversation_id,
            mcp_base_url=os.getenv("MCP_BASE_URL", "http://localhost:8000"),
        )

        # Run agent
        logger.info(f"Running agent for user {user_id}, conversation {conversation_id}")
        result = await Runner.run(
            task_manager_agent, input=input_messages, context=context
        )

        # Extract tool calls from result
        tool_calls = []
        if hasattr(result, "tool_calls"):
            for tool_call in result.tool_calls:
                tool_calls.append(
                    {
                        "tool_name": tool_call.name,
                        "arguments": tool_call.arguments,
                        "result": str(tool_call.output) if tool_call.output else None,
                    }
                )

        # Store assistant response with GUARANTEED persistence
        # This is synchronous and will NOT return until persisted
        await store_message(conversation_id, user_id, "assistant", result.final_output)
        logger.info(f"Assistant message GUARANTEED persisted for conversation {conversation_id}")

        # Update conversation timestamp
        try:
            with get_session() as session:
                conversation = session.get(Conversation, conversation_id)
                if conversation:
                    conversation.updated_at = datetime.utcnow()
                    session.commit()
        except Exception as e:
            logger.error(f"Error updating conversation timestamp: {e}")

        logger.info(f"Agent response: {result.final_output[:100]}")
        logger.debug(f"Tool calls: {len(tool_calls)}")

        return {
            "conversation_id": conversation_id,
            "response": result.final_output,
            "tool_calls": tool_calls,
        }
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise
