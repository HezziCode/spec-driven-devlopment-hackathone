"""
OpenAI Agents SDK integration package.

This package provides the TaskManagerAgent for natural language task management,
along with function tools that call the existing MCP server for CRUD operations.
"""

from .agent import task_manager_agent, AGENT_INSTRUCTIONS
from .tools import (
    create_task,
    list_tasks,
    get_task,
    mark_complete,
    update_task,
    delete_task,
    search_tasks,
)
from .context import AgentContext

__all__ = [
    "task_manager_agent",
    "AGENT_INSTRUCTIONS",
    "AgentContext",
    "create_task",
    "list_tasks",
    "get_task",
    "mark_complete",
    "update_task",
    "delete_task",
    "search_tasks",
]
