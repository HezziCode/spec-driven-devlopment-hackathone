"""
OpenAI Agents SDK integration package.

This package provides the TaskManagerAgent for natural language task management,
along with function tools that call the existing MCP server for CRUD operations.
"""

from .agent import AGENT_INSTRUCTIONS, task_manager_agent
from .context import AgentContext
from .tools import (
    create_task,
    delete_task,
    get_task,
    list_tasks,
    mark_complete,
    search_tasks,
    update_task,
)

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
