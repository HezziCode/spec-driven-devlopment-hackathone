"""Tests for ChatKit server and streaming functionality."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from uuid import uuid4


class TestChatKitSchemas:
    """Tests for ChatKit Pydantic schemas."""

    def test_chat_request_valid(self):
        """Test valid ChatRequest creation."""
        from schemas.chatkit import ChatRequest

        request = ChatRequest(message="Hello, help me with tasks")
        assert request.message == "Hello, help me with tasks"
        assert request.thread_id is None

    def test_chat_request_with_thread(self):
        """Test ChatRequest with existing thread."""
        from schemas.chatkit import ChatRequest

        thread_id = str(uuid4())
        request = ChatRequest(thread_id=thread_id, message="Continue our conversation")
        assert request.thread_id == thread_id
        assert request.message == "Continue our conversation"

    def test_chat_request_message_required(self):
        """Test that message field is required."""
        from pydantic import ValidationError
        from schemas.chatkit import ChatRequest

        with pytest.raises(ValidationError):
            ChatRequest()

    def test_chat_request_message_min_length(self):
        """Test message minimum length validation."""
        from pydantic import ValidationError
        from schemas.chatkit import ChatRequest

        with pytest.raises(ValidationError):
            ChatRequest(message="")

    def test_chat_request_message_max_length(self):
        """Test message maximum length validation."""
        from pydantic import ValidationError
        from schemas.chatkit import ChatRequest

        long_message = "x" * 4001
        with pytest.raises(ValidationError):
            ChatRequest(message=long_message)

    def test_thread_response(self):
        """Test ThreadResponse schema."""
        from schemas.chatkit import ThreadResponse, ChatMessageResponse

        thread = ThreadResponse(
            id=str(uuid4()),
            title="Test Thread",
            user_id=str(uuid4()),
            created_at="2025-01-01T00:00:00",
            updated_at="2025-01-01T00:00:00",
            messages=[
                ChatMessageResponse(
                    id=str(uuid4()),
                    role="user",
                    content="Hello",
                    created_at="2025-01-01T00:00:00",
                )
            ],
        )
        assert thread.title == "Test Thread"
        assert len(thread.messages) == 1

    def test_thread_list_item(self):
        """Test ThreadListItem schema."""
        from schemas.chatkit import ThreadListItem

        item = ThreadListItem(
            id=str(uuid4()),
            title="My Thread",
            message_count=5,
            created_at="2025-01-01T00:00:00",
            updated_at="2025-01-01T00:00:00",
        )
        assert item.message_count == 5

    def test_thread_list_response(self):
        """Test ThreadListResponse schema."""
        from schemas.chatkit import ThreadListResponse, ThreadListItem

        response = ThreadListResponse(
            threads=[
                ThreadListItem(
                    id=str(uuid4()),
                    title="Thread 1",
                    message_count=3,
                    created_at="2025-01-01T00:00:00",
                    updated_at="2025-01-01T00:00:00",
                )
            ],
            total=1,
        )
        assert response.total == 1
        assert len(response.threads) == 1


class TestChatContext:
    """Tests for ChatContext dataclass."""

    def test_chat_context_default_values(self):
        """Test ChatContext with default values."""
        from chatkit.context import ChatContext

        context = ChatContext(user_id=str(uuid4()))
        assert context.thread_id is None
        assert context.mcp_base_url == "http://localhost:8000/mcp"

    def test_chat_context_custom_values(self):
        """Test ChatContext with custom values."""
        from chatkit.context import ChatContext

        context = ChatContext(
            user_id=str(uuid4()),
            thread_id=str(uuid4()),
            mcp_base_url="http://custom:9000/mcp",
        )
        assert context.thread_id is not None
        assert context.mcp_base_url == "http://custom:9000/mcp"


class TestStreamingResponse:
    """Tests for streaming response utilities."""

    @pytest.mark.asyncio
    async def test_text_event_format(self):
        """Test SSE text event formatting."""
        from chatkit.streaming import StreamingResponse

        result = await StreamingResponse.text_event("Hello world")
        assert result == "data: Hello world\n\n"

    @pytest.mark.asyncio
    async def test_tool_call_event_format(self):
        """Test SSE tool call event formatting."""
        from chatkit.streaming import StreamingResponse

        result = await StreamingResponse.tool_call_event(
            "list_tasks", {"status": "pending"}
        )
        assert "event: tool_call\n" in result
        assert '"tool": "list_tasks"' in result
        assert '"arguments": {"status": "pending"}' in result

    @pytest.mark.asyncio
    async def test_done_event_format(self):
        """Test SSE done event formatting."""
        from chatkit.streaming import StreamingResponse

        result = await StreamingResponse.done_event({"thread_id": "test-id"})
        assert "event: done\n" in result
        assert '"thread_id": "test-id"' in result

    @pytest.mark.asyncio
    async def test_error_event_format(self):
        """Test SSE error event formatting."""
        from chatkit.streaming import StreamingResponse

        result = await StreamingResponse.error_event("Something went wrong")
        assert "event: error\n" in result
        assert "Something went wrong" in result


class TestChatKitServer:
    """Tests for ChatKitServer class."""

    @pytest.mark.asyncio
    async def test_server_initialization(self):
        """Test ChatKitServer can be initialized."""
        from chatkit.server import ChatKitServer
        from chatkit.thread_manager import ThreadManager

        mock_agent = MagicMock()
        mock_thread_manager = MagicMock()

        server = ChatKitServer(agent=mock_agent, thread_manager=mock_thread_manager)
        assert server.agent == mock_agent
        assert server.thread_manager == mock_thread_manager


class TestChatKitService:
    """Tests for ChatKitService class."""

    def test_service_initialization(self):
        """Test ChatKitService can be initialized."""
        from services.chatkit_service import ChatKitService

        service = ChatKitService()
        assert service.thread_manager is not None

    def test_create_server(self):
        """Test ChatKitService.create_server returns ChatKitServer."""
        from services.chatkit_service import ChatKitService
        from chatkit.server import ChatKitServer

        service = ChatKitService()
        server = service.create_server([])
        assert isinstance(server, ChatKitServer)

    def test_get_chatkit_service_singleton(self):
        """Test get_chatkit_service returns singleton."""
        from services.chatkit_service import get_chatkit_service

        service1 = get_chatkit_service()
        service2 = get_chatkit_service()
        assert service1 is service2
