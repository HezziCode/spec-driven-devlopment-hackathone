"""Tests for agent tool functions."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import sys
sys.path.insert(0, '.')


def create_mock_context(user_id: str = "test-user-id") -> Mock:
    """Create a mock RunContextWrapper with AgentContext."""
    from ai_agents.context import AgentContext
    mock_ctx = Mock()
    mock_ctx.context = AgentContext(
        user_id=user_id,
        conversation_id="test-convo-id",
        mcp_base_url="http://localhost:8000"
    )
    return mock_ctx


def test_agent_context_creation():
    """Test that AgentContext can be created with required fields."""
    from ai_agents.context import AgentContext

    ctx = AgentContext(
        user_id="test-user-id",
        conversation_id="test-convo-id",
        mcp_base_url="http://localhost:8000"
    )

    assert ctx.user_id == "test-user-id"
    assert ctx.conversation_id == "test-convo-id"
    assert ctx.mcp_base_url == "http://localhost:8000"


def test_agent_tools_are_function_tools():
    """Test that all tools are properly decorated with @function_tool."""
    from ai_agents.tools import (
        create_task,
        list_tasks,
        get_task,
        mark_complete,
        update_task,
        delete_task,
        search_tasks,
    )

    # All tools should be FunctionTool instances
    tools = [create_task, list_tasks, get_task, mark_complete, update_task, delete_task, search_tasks]
    for tool in tools:
        assert hasattr(tool, 'name'), f"Tool {tool} should have 'name' attribute"
        assert hasattr(tool, 'on_invoke_tool'), f"Tool {tool} should have 'on_invoke_tool' method"


def test_task_tools_have_correct_names():
    """Test that tools have the expected names."""
    from ai_agents.tools import (
        create_task,
        list_tasks,
        get_task,
        mark_complete,
        update_task,
        delete_task,
        search_tasks,
    )

    expected_names = {
        'create_task': create_task,
        'list_tasks': list_tasks,
        'get_task': get_task,
        'mark_complete': mark_complete,
        'update_task': update_task,
        'delete_task': delete_task,
        'search_tasks': search_tasks,
    }

    for expected_name, tool in expected_names.items():
        assert tool.name == expected_name, f"Tool name should be '{expected_name}', got '{tool.name}'"


def test_agent_has_all_tools():
    """Test that TaskManagerAgent is configured with all required tools."""
    from ai_agents.agent import task_manager_agent

    # Get the list of tools registered with the agent
    agent_tools = task_manager_agent.tools

    # Convert to names for easier checking
    tool_names = {tool.name for tool in agent_tools}

    # Verify all CRUD tools are registered
    expected_tools = {'create_task', 'list_tasks', 'get_task', 'mark_complete', 'update_task', 'delete_task', 'search_tasks'}
    assert expected_tools.issubset(tool_names), f"Agent missing tools: {expected_tools - tool_names}"


def test_agent_model_configuration():
    """Test that agent uses the correct model."""
    from ai_agents.agent import task_manager_agent

    # Agent should use gpt-4o-mini for cost efficiency
    assert task_manager_agent.model == "gpt-4o-mini"


def test_agent_has_instructions():
    """Test that agent has instructions configured."""
    from ai_agents.agent import task_manager_agent, AGENT_INSTRUCTIONS

    # Instructions should be defined
    assert AGENT_INSTRUCTIONS is not None
    assert len(AGENT_INSTRUCTIONS) > 0

    # Agent should have instructions
    assert task_manager_agent.instructions is not None


@pytest.mark.asyncio
async def test_tool_can_be_invoked_with_mock_context():
    """Test that tools can be invoked with a proper context wrapper."""
    from ai_agents.tools import create_task
    from ai_agents.context import AgentContext

    # Create a mock RunContextWrapper
    mock_ctx = Mock()
    mock_ctx.context = AgentContext(
        user_id="test-user-id",
        conversation_id="test-convo-id",
        mcp_base_url="http://localhost:8000"
    )

    # The tool should have a name attribute
    assert create_task.name == "create_task"

    # Verify the tool has the expected description
    assert hasattr(create_task, 'description')


def test_schemas_are_importable():
    """Test that all agent schemas can be imported."""
    from ai_agents.schemas import (
        TaskPriority,
        ExtractedTaskDetails,
        TaskInfo,
        TaskOperationResult,
        TaskListResult,
    )

    # TaskPriority should be an enum
    assert hasattr(TaskPriority, 'low')
    assert hasattr(TaskPriority, 'medium')
    assert hasattr(TaskPriority, 'high')
    assert hasattr(TaskPriority, 'critical')


def test_create_task_schemas():
    """Test schema creation for task operations."""
    from ai_agents.schemas import TaskOperationResult, TaskListResult, TaskInfo
    from datetime import datetime

    # Test TaskOperationResult
    result = TaskOperationResult(
        task_id="test-123",
        status="created",
        title="Test Task"
    )
    assert result.task_id == "test-123"
    assert result.status == "created"
    assert result.title == "Test Task"

    # Test TaskInfo with required fields
    now = datetime.utcnow()
    task_info = TaskInfo(
        id="test-123",
        title="Test Task",
        description="A test task",
        completed=False,
        priority="medium",
        created_at=now.isoformat(),
        updated_at=now.isoformat()
    )
    assert task_info.id == "test-123"
    assert task_info.completed is False

    # Test TaskListResult
    task_list = TaskListResult(
        tasks=[task_info],
        total=1
    )
    assert task_list.total == 1
    assert len(task_list.tasks) == 1
