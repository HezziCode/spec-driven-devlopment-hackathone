"""ThreadManager for managing chat conversation threads and messages."""

import logging
import uuid
from datetime import datetime
from typing import Any

from sqlmodel import Session, select

from models import ChatMessage, ChatThread

logger = logging.getLogger(__name__)


class ThreadManager:
    """Manages conversation threads and messages for ChatKit.

    Provides CRUD operations for threads and messages, enforcing user
    isolation at the database level.
    """

    def __init__(self, session: Session):
        """Initialize ThreadManager with a database session.

        Args:
            session: SQLModel Session for database operations
        """
        self.session = session

    def create_thread(
        self, user_id: str, title: str | None = None, first_message: str | None = None
    ) -> ChatThread:
        """Create a new conversation thread.

        Args:
            user_id: UUID of the thread owner
            title: Optional thread title (auto-generated from first message if None)
            first_message: Optional first message to generate title from

        Returns:
            Created ChatThread instance
        """
        # Auto-generate title from first message if no title provided
        final_title = title
        if not final_title and first_message:
            # Clean and truncate the first message for thread name
            final_title = first_message.strip()
            # Remove common prefixes/suffixes
            final_title = re.sub(
                r"^(hi|hello|hey|help|can you|please)[,\s!?]*",
                "",
                final_title,
                flags=re.IGNORECASE,
            )
            # Truncate to reasonable length
            if len(final_title) > 50:
                final_title = final_title[:47] + "..."
            # Fallback if message is too short/empty
            if len(final_title) < 3:
                final_title = "New Conversation"

        thread = ChatThread(
            id=str(uuid.uuid4()),
            user_id=user_id,
            name=final_title or "New Conversation",
        )
        self.session.add(thread)
        self.session.commit()
        self.session.refresh(thread)
        logger.info(
            f"Created thread {thread.id} for user {user_id} with title: {thread.name}"
        )
        return thread

    def get_thread(self, user_id: str, thread_id: str) -> ChatThread | None:
        """Retrieve a thread by ID with user isolation.

        Args:
            user_id: UUID of the authenticated user
            thread_id: String ID of the thread to retrieve

        Returns:
            ChatThread instance if found and owned by user, None otherwise
        """
        thread = self.session.get(ChatThread, thread_id)
        if thread and str(thread.user_id) == user_id:
            return thread
        return None

    def list_threads(self, user_id: str, limit: int = 50) -> list[dict[str, Any]]:
        """List all threads for a user with metadata.

        Args:
            user_id: UUID of the user
            limit: Maximum number of threads to return

        Returns:
            List of thread dictionaries with id, title, message_count, timestamps
        """
        threads = self.session.exec(
            select(ChatThread)
            .where(ChatThread.user_id == user_id)
            .order_by(ChatThread.updated_at.desc())
            .limit(limit)
        ).all()

        result = []
        for thread in threads:
            message_count = self.session.exec(
                select(ChatMessage).where(ChatMessage.thread_id == thread.id)
            ).count()
            result.append(
                {
                    "id": str(thread.id),
                    "title": thread.name,
                    "message_count": message_count,
                    "created_at": thread.created_at.isoformat(),
                    "updated_at": thread.updated_at.isoformat(),
                }
            )
        return result

    def delete_thread(self, user_id: str, thread_id: str) -> bool:
        """Delete a thread and all its messages.

        Args:
            user_id: UUID of the authenticated user
            thread_id: String ID of the thread to delete

        Returns:
            True if deleted, False if not found or not owned by user
        """
        thread = self.session.get(ChatThread, thread_id)
        if not thread or str(thread.user_id) != user_id:
            return False

        # Delete all messages in thread
        self.session.exec(
            select(ChatMessage).where(ChatMessage.thread_id == thread_id)
        ).delete()

        # Delete thread
        self.session.delete(thread)
        self.session.commit()
        logger.info(f"Deleted thread {thread_id} for user {user_id}")
        return True

    def add_message(
        self, thread_id: str, user_id: str, role: str, content: str
    ) -> ChatMessage:
        """Add a message to a thread.

        Args:
            thread_id: String ID of the conversation thread
            user_id: UUID of the user who owns this message
            role: Message role ("user" or "assistant")
            content: Message content

        Returns:
            Created ChatMessage instance
        """
        from uuid import UUID

        message = ChatMessage(
            thread_id=thread_id,
            user_id=UUID(user_id),
            role=role,
            content=content,
        )
        self.session.add(message)
        self.session.commit()
        self.session.refresh(message)

        # Update thread's updated_at timestamp
        thread = self.session.get(ChatThread, thread_id)
        if thread:
            thread.updated_at = datetime.utcnow()
            self.session.commit()

        logger.debug(f"Added {role} message to thread {thread_id}")
        return message

    def get_recent_messages(
        self, thread_id: str, limit: int = 20
    ) -> list[dict[str, str]]:
        """Get recent messages for a thread.

        Args:
            thread_id: UUID of the conversation thread
            limit: Maximum number of messages to return (default 20)

        Returns:
            List of message dictionaries with role and content
        """
        messages = self.session.exec(
            select(ChatMessage)
            .where(ChatMessage.thread_id == thread_id)
            .order_by(ChatMessage.created_at)
            .limit(limit)
        ).all()

        return [{"role": msg.role, "content": msg.content} for msg in messages]

    def get_thread_with_messages(
        self, user_id: str, thread_id: str
    ) -> dict[str, Any] | None:
        """Get a thread with all its messages.

        Args:
            user_id: UUID of the authenticated user
            thread_id: String ID of the thread

        Returns:
            Dictionary with thread info and messages, or None if not found
        """
        thread = self.get_thread(user_id, thread_id)
        if not thread:
            return None

        messages = self.session.exec(
            select(ChatMessage)
            .where(ChatMessage.thread_id == thread_id)
            .order_by(ChatMessage.created_at)
        ).all()

        return {
            "id": str(thread.id),
            "title": thread.name,
            "user_id": str(thread.user_id),
            "created_at": thread.created_at.isoformat(),
            "updated_at": thread.updated_at.isoformat(),
            "messages": [
                {
                    "id": str(msg.id),
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat(),
                }
                for msg in messages
            ],
        }
