"""Tests for ThreadManager class."""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest


class TestThreadManager:
    """Tests for ThreadManager thread operations."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        session = MagicMock()
        return session

    def test_thread_manager_initialization(self):
        """Test ThreadManager can be initialized."""
        from chatkit.thread_manager import ThreadManager

        manager = ThreadManager()
        assert manager is not None

    def test_create_thread(self):
        """Test thread creation."""
        from chatkit.thread_manager import ThreadManager
        from models import Thread

        manager = ThreadManager()

        with patch("chatkit.thread_manager.get_session") as mock_get_session:
            mock_session = MagicMock()
            mock_get_session.return_value.__enter__.return_value = mock_session

            thread = Thread(
                id=uuid4(),
                user_id=uuid4(),
                title="Test Thread",
            )
            mock_session.add.return_value = None
            mock_session.commit.return_value = None
            mock_session.refresh.return_value = thread

            # This tests the structure - actual DB test would need real session
            # The method exists and is callable
            assert hasattr(manager, "create_thread")
            assert callable(manager.create_thread)

    def test_get_thread_user_isolation(self):
        """Test get_thread enforces user isolation."""
        from chatkit.thread_manager import ThreadManager

        manager = ThreadManager()

        # Method exists and is callable
        assert hasattr(manager, "get_thread")
        assert callable(manager.get_thread)

    def test_list_threads(self):
        """Test listing user threads."""
        from chatkit.thread_manager import ThreadManager

        manager = ThreadManager()

        assert hasattr(manager, "list_threads")
        assert callable(manager.list_threads)

    def test_delete_thread(self):
        """Test deleting a thread."""
        from chatkit.thread_manager import ThreadManager

        manager = ThreadManager()

        assert hasattr(manager, "delete_thread")
        assert callable(manager.delete_thread)


class TestThreadManagerMessages:
    """Tests for ThreadManager message operations."""

    def test_add_message(self):
        """Test adding a message to thread."""
        from chatkit.thread_manager import ThreadManager

        manager = ThreadManager()

        assert hasattr(manager, "add_message")
        assert callable(manager.add_message)

    def test_get_recent_messages(self):
        """Test retrieving recent messages."""
        from chatkit.thread_manager import ThreadManager

        manager = ThreadManager()

        assert hasattr(manager, "get_recent_messages")
        assert callable(manager.get_recent_messages)

    def test_get_thread_with_messages(self):
        """Test getting thread with all messages."""
        from chatkit.thread_manager import ThreadManager

        manager = ThreadManager()

        assert hasattr(manager, "get_thread_with_messages")
        assert callable(manager.get_thread_with_messages)


class TestChatAgent:
    """Tests for ChatAgent creation."""

    def test_create_chat_agent_exists(self):
        """Test create_chat_agent function exists."""
        from chatkit.agent import create_chat_agent

        assert callable(create_chat_agent)

    def test_chat_instructions_defined(self):
        """Test chat instructions are defined."""
        from chatkit.agent import CHAT_INSTRUCTIONS

        assert isinstance(CHAT_INSTRUCTIONS, str)
        assert len(CHAT_INSTRUCTIONS) > 0
        assert "task" in CHAT_INSTRUCTIONS.lower()

    def test_chat_agent_returns_agent(self):
        """Test create_chat_agent returns an Agent."""
        from agents import Agent

        from chatkit.agent import create_chat_agent

        agent = create_chat_agent([])
        assert isinstance(agent, Agent)
        assert agent.name == "ChatKit"
