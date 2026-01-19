"""ChatKit service for orchestrating chat operations.

This module provides the high-level service interface for ChatKit,
orchestrating between the ThreadManager and ChatKitServer.
"""

import logging
from datetime import datetime
from typing import AsyncGenerator
from uuid import UUID

from sqlmodel import Session, func, select

# Import agent tools for task management
from ai_agents.tools import (
    create_task,
    delete_task,
    delete_task_by_name,
    get_task,
    list_tasks,
    mark_complete,
    search_tasks,
    update_task,
)
from chatkit.agent import create_chat_agent
from chatkit.server import ChatKitServer
from chatkit.thread_manager import ThreadManager

# Import models for message persistence
from models import ChatMessage, ChatThread

logger = logging.getLogger(__name__)


class ChatKitService:
    """Service interface for ChatKit chat operations.

    Provides thread management and streaming chat functionality
    by coordinating ThreadManager and ChatKitServer.
    """

    def __init__(self, session: Session) -> None:
        """Initialize the ChatKit service.

        Args:
            session: SQLModel Session for database operations
        """
        self.session = session
        self.thread_manager = ThreadManager(session)
        logger.info("ChatKitService initialized")

    def create_server(self, tools: list = None) -> ChatKitServer:
        """Create a ChatKitServer with the given tools.

        Args:
            tools: List of @function_tool decorated functions

        Returns:
            Configured ChatKitServer instance
        """

        agent = create_chat_agent(tools or [])
        return ChatKitServer(agent=agent, session=self.session)

    async def process_message(
        self, user_id: str, thread_id: str | None, message: str, jwt_token: str
    ) -> AsyncGenerator[str, None]:
        """Process a user message and stream the AI response with persistence.

        Args:
            user_id: UUID of the authenticated user
            thread_id: Optional existing thread ID (creates new if None)
            message: User's message content
            jwt_token: JWT token for authenticating internal API calls

        Yields:
            SSE-formatted text events with response tokens
        """
        # Wire all 7 agent tools for task management
        tools = [
            create_task,
            list_tasks,
            get_task,
            mark_complete,
            update_task,
            delete_task,
            delete_task_by_name,
            search_tasks,
        ]
        server = self.create_server(tools)

        try:
            # Step 1: Create or get thread
            if not thread_id:
                try:
                    thread = self._create_thread(user_id, first_message=message)
                    thread_id = thread.id
                    # Commit the thread to database before saving messages
                    self.session.commit()
                    # Ensure the transaction is fully committed and visible
                    self.session.expire_all()
                    logger.info(f"Created new thread {thread_id} for user {user_id}")

                    # Yield the thread ID in a special event so frontend knows about the new thread
                    yield f'event: thread_created\ndata: {{"threadId":"{thread_id}"}}\n\n'
                except ValueError as e:
                    # Thread limit reached
                    yield f"event: error\ndata: {str(e)}\n\n"
                    return
            else:
                # Validate that the provided thread_id exists in the database
                existing_thread = self.session.get(ChatThread, thread_id)
                if not existing_thread:
                    logger.error(f"Thread {thread_id} does not exist in database")
                    yield "event: error\ndata: Thread not found\n\n"
                    return
                # Verify user ownership of the thread
                if str(existing_thread.user_id) != user_id:
                    logger.error(f"User {user_id} does not own thread {thread_id}")
                    yield "event: error\ndata: Not authorized to access this thread\n\n"
                    return

            # Step 2: Save user message to database
            self._save_message(thread_id, user_id, "user", message)

            # Step 3: Load conversation history for context
            history = self._load_thread_messages(thread_id)

            # Step 4: Stream agent response and accumulate content
            response_content = ""
            async for event in server.respond(user_id, thread_id, message, jwt_token):
                # Extract text content from SSE events for accumulation
                if event.startswith("data: "):
                    content = event[6:].strip()
                    if content and not content.startswith("{"):  # Skip JSON events
                        response_content += content
                yield event

            # Step 5: Save assistant response to database
            if response_content:
                self._save_message(thread_id, user_id, "assistant", response_content)

                # Step 6: Update thread metadata
                self._update_thread_metadata(thread_id, response_content)

        except ValueError as e:
            # Thread limit or validation error
            logger.error(f"Validation error: {e}")
            yield f"event: error\ndata: {str(e)}\n\n"
        except Exception as e:
            logger.exception(f"Error processing message: {e}")
            yield f"event: error\ndata: Failed to process message: {str(e)}\n\n"

    def create_thread(self, user_id: str, title: str | None = None):
        """Create a new conversation thread.

        Args:
            user_id: UUID of the thread owner
            title: Optional thread title

        Returns:
            Created thread data dictionary
        """
        thread = self.thread_manager.create_thread(user_id, title)
        return {
            "id": str(thread.id),
            "title": thread.title,
            "user_id": str(thread.user_id),
            "created_at": thread.created_at.isoformat(),
            "updated_at": thread.updated_at.isoformat(),
        }

    def get_thread(self, user_id: str, thread_id: str):
        """Get a thread by ID with all messages.

        Args:
            user_id: UUID of the authenticated user
            thread_id: Thread ID (string format)

        Returns:
            Thread data dictionary with messages or None if not found
        """
        try:
            # Try to get thread from ChatThread table
            thread = self.session.get(ChatThread, thread_id)

            if not thread:
                # Add a small delay and retry to handle race conditions in serverless environments
                import time

                time.sleep(
                    0.1
                )  # Small delay to allow database transaction to propagate
                # Refresh the session to ensure we get the latest data from the database
                self.session.expire_all()
                thread = self.session.get(ChatThread, thread_id)

            if not thread:
                # Try one more time with a slightly longer delay and forced commit
                time.sleep(0.2)
                self.session.commit()  # Ensure any pending transactions are committed
                self.session.expire_all()
                thread = self.session.get(ChatThread, thread_id)

            if not thread:
                return None

            # Verify user ownership
            if str(thread.user_id) != user_id:
                return None

            # Load messages from ChatMessage table
            messages = self.session.exec(
                select(ChatMessage)
                .where(ChatMessage.thread_id == thread_id)
                .order_by(ChatMessage.created_at)
            ).all()

            # Format response
            return {
                "id": thread.id,
                "name": thread.name,
                "user_id": str(thread.user_id),
                "created_at": thread.created_at.isoformat(),
                "updated_at": thread.updated_at.isoformat(),
                "message_count": thread.message_count,
                "last_message_preview": thread.last_message_preview,
                "messages": [
                    {
                        "id": str(m.id),
                        "role": m.role,
                        "content": m.content,
                        "created_at": m.created_at.isoformat(),
                    }
                    for m in messages
                ],
            }
        except Exception as e:
            logger.error(f"Error getting thread {thread_id} for user {user_id}: {e}")
            return None

    def list_threads(self, user_id: str, limit: int = 50):
        """List all threads for a user.

        Args:
            user_id: UUID of the user
            limit: Maximum threads to return

        Returns:
            ThreadListResponse with threads and total count
        """
        threads = self.thread_manager.list_threads(user_id, limit)
        return {
            "threads": threads,
            "total": len(threads),
        }

    def delete_thread(self, user_id: str, thread_id: str) -> bool:
        """Delete a thread.

        Args:
            user_id: UUID of the authenticated user
            thread_id: UUID of the thread to delete

        Returns:
            True if deleted, False if not found
        """
        return self.thread_manager.delete_thread(user_id, thread_id)

    # ==================== Message Persistence Helper Methods ====================

    def _save_message(
        self, thread_id: str, user_id: str, role: str, content: str
    ) -> ChatMessage:
        """Save a message to the database.

        Args:
            thread_id: Thread ID (string format for ChatThread compatibility)
            user_id: User UUID as string
            role: Message role ('user' or 'assistant')
            content: Message content

        Returns:
            Saved ChatMessage instance
        """
        message = ChatMessage(
            thread_id=thread_id, user_id=UUID(user_id), role=role, content=content
        )
        self.session.add(message)
        self.session.commit()
        self.session.refresh(message)
        # Ensure the message is properly synchronized with the database
        self.session.expunge(message)
        logger.info(f"Saved {role} message to thread {thread_id}")
        return message

    def _load_thread_messages(self, thread_id: str) -> list[dict]:
        """Load all messages for a thread ordered by created_at.

        Args:
            thread_id: Thread ID (string format)

        Returns:
            List of message dictionaries with role and content keys
        """
        messages = self.session.exec(
            select(ChatMessage)
            .where(ChatMessage.thread_id == thread_id)
            .order_by(ChatMessage.created_at)
        ).all()

        result = [{"role": m.role, "content": m.content} for m in messages]
        logger.info(f"Loaded {len(result)} messages from thread {thread_id}")
        return result

    def _update_thread_metadata(self, thread_id: str, last_message: str):
        """Update thread metadata after a message exchange.

        Args:
            thread_id: Thread ID (string format)
            last_message: Content of the last message for preview
        """
        thread = self.session.get(ChatThread, thread_id)
        if thread:
            thread.message_count += 1
            thread.last_message_preview = last_message[:100]
            thread.updated_at = datetime.now()
            self.session.commit()
            # Ensure the thread metadata update is properly synchronized
            self.session.expunge(thread)
            logger.info(f"Updated metadata for thread {thread_id}")

    def _create_thread(
        self, user_id: str, first_message: str | None = None
    ) -> ChatThread:
        """Create a new chat thread with limit enforcement and auto-generated title.

        Args:
            user_id: User UUID as string
            first_message: Optional first message to generate title from

        Returns:
            Created ChatThread instance

        Raises:
            ValueError: If user has reached the 20-thread limit
        """
        # Check thread count for this user
        count = self.session.exec(
            select(func.count(ChatThread.id)).where(ChatThread.user_id == UUID(user_id))
        ).one()

        if count >= 20:
            raise ValueError(
                "Thread limit reached. Delete old threads to create new ones."
            )

        # Auto-generate title from first message if provided
        thread_name = "New Chat"
        if first_message:
            # Clean and truncate the first message for thread name
            thread_name = first_message.strip()
            # Remove common prefixes/suffixes
            import re

            thread_name = re.sub(
                r"^(hi|hello|hey|help|can you|please)[,\s!?]*",
                "",
                thread_name,
                flags=re.IGNORECASE,
            )
            # Truncate to reasonable length
            if len(thread_name) > 50:
                thread_name = thread_name[:47] + "..."
            # Fallback if message is too short/empty
            if len(thread_name) < 3:
                thread_name = "New Chat"

        # Generate a unique thread ID (using UUID format as string)
        from uuid import uuid4

        thread_id = str(uuid4())

        thread = ChatThread(id=thread_id, user_id=UUID(user_id), name=thread_name)
        self.session.add(thread)
        self.session.commit()
        self.session.refresh(thread)
        # Ensure the thread is properly synchronized with the database
        self.session.expunge(thread)

        # Additional synchronization to ensure database visibility
        self.session.expire_all()

        logger.info(
            f"Created new thread {thread_id} for user {user_id} with title: {thread_name}"
        )

        # Verify the thread exists in database before returning
        verified_thread = self.session.get(ChatThread, thread_id)
        if not verified_thread:
            import time

            time.sleep(0.1)  # Brief delay
            self.session.expire_all()
            verified_thread = self.session.get(ChatThread, thread_id)

        if not verified_thread:
            logger.error(f"Thread {thread_id} was not found in database after creation")
            raise ValueError(f"Failed to create thread {thread_id}")

        return thread


# Singleton service instance
_chatkit_service: ChatKitService | None = None


def get_chatkit_service(session: Session) -> ChatKitService:
    """Get or create the ChatKitService instance.

    Args:
        session: SQLModel Session for database operations

    Returns:
        ChatKitService instance
    """
    return ChatKitService(session)


# ==================== ChatKit Session Management Functions ====================


async def create_chatkit_session(user_id: UUID, session: "Session") -> dict:
    """
    Generate ChatKit client secret for user and store in database.

    Args:
        user_id: User UUID from JWT token.
        session: SQLModel database session.

    Returns:
        Dictionary with client_secret and expires_at.
    """
    import hashlib
    import secrets
    from datetime import datetime, timedelta

    from models import ChatKitSession

    # Generate a unique client secret
    client_secret = f"cs_{secrets.token_urlsafe(32)}"

    # Set expiry to 24 hours from now
    expires_at = datetime.now() + timedelta(hours=24)

    # Hash the client secret for storage
    client_secret_hash = hashlib.sha256(client_secret.encode()).hexdigest()

    # Create session record in database
    db_session = ChatKitSession(
        user_id=user_id,
        client_secret_hash=client_secret_hash,
        expires_at=expires_at,
        status="active",
    )
    session.add(db_session)
    session.commit()
    session.refresh(db_session)

    logger.info(f"Created ChatKit session for user {user_id}")

    return {"client_secret": client_secret, "expires_at": expires_at.isoformat() + "Z"}


async def sync_thread(
    user_id: UUID, thread_data: dict, session: "Session"
) -> "ChatThread":
    """
    Sync thread metadata to database (create or update).

    Args:
        user_id: User UUID from JWT token.
        thread_data: Dictionary with thread_id, name, last_message_preview, message_count.
        session: SQLModel database session.

    Returns:
        ChatThread model instance.
    """
    from datetime import datetime

    from models import ChatThread

    thread_id = thread_data["thread_id"]

    # Check if thread already exists
    existing_thread = session.get(ChatThread, thread_id)

    if existing_thread:
        # Update existing thread
        existing_thread.name = thread_data["name"]
        existing_thread.last_message_preview = thread_data.get("last_message_preview")
        existing_thread.message_count = thread_data["message_count"]
        existing_thread.updated_at = datetime.now()
        thread = existing_thread
        logger.info(f"Updated ChatThread {thread_id} for user {user_id}")
    else:
        # Create new thread
        thread = ChatThread(
            id=thread_id,
            user_id=user_id,
            name=thread_data["name"],
            last_message_preview=thread_data.get("last_message_preview"),
            message_count=thread_data["message_count"],
        )
        session.add(thread)
        logger.info(f"Created ChatThread {thread_id} for user {user_id}")

    session.commit()
    session.refresh(thread)
    return thread


async def list_threads(
    user_id: UUID, session: "Session", limit: int = 50, offset: int = 0
) -> tuple[list, int]:
    """
    List all chat threads for a user.

    Args:
        user_id: User UUID from JWT token.
        session: SQLModel database session.
        limit: Maximum number of threads to return.
        offset: Number of threads to skip (pagination).

    Returns:
        Tuple of (list of ChatThread models, total count).
    """
    from sqlmodel import select

    from models import ChatThread

    # Query threads for this user, ordered by updated_at descending
    query = (
        select(ChatThread)
        .where(ChatThread.user_id == user_id)
        .order_by(ChatThread.updated_at.desc())
        .offset(offset)
        .limit(limit)
    )
    threads = session.exec(query).all()

    # Get total count
    count_query = select(ChatThread).where(ChatThread.user_id == user_id)
    total = len(session.exec(count_query).all())

    logger.info(f"Listed {len(threads)} threads for user {user_id} (total: {total})")
    return list(threads), total


async def delete_thread(user_id: UUID, thread_id: str, session: "Session") -> bool:
    """
    Delete a chat thread.

    Args:
        user_id: User UUID from JWT token (for authorization).
        thread_id: Thread ID to delete.
        session: SQLModel database session.

    Returns:
        True if deleted, False if not found or not authorized.
    """
    from models import ChatThread

    # Get thread and verify ownership
    thread = session.get(ChatThread, thread_id)
    if not thread:
        logger.warning(f"Thread {thread_id} not found")
        return False

    if thread.user_id != user_id:
        logger.warning(f"User {user_id} not authorized to delete thread {thread_id}")
        return False

    # Delete thread
    session.delete(thread)
    session.commit()

    logger.info(f"Deleted ChatThread {thread_id} for user {user_id}")
    return True
