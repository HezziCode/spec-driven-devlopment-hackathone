"""
MCP Server for Todo Management.

This package provides an MCP (Model Context Protocol) server that exposes
todo CRUD operations as tools for AI agents to use.

Tools:
    - create_task: Create a new task for a user
    - list_tasks: List tasks with optional status filtering
    - mark_complete: Mark a task as completed
    - update_task: Update task title and/or description
    - delete_task: Permanently delete a task
    - search_tasks: Search tasks by keyword
"""

from mcp_server.server import mcp
from mcp_server.schemas import (
    TaskStatus,
    CreateTaskInput,
    ListTasksInput,
    TaskIdInput,
    UpdateTaskInput,
    SearchTasksInput,
    TaskResponse,
    TaskDetail,
    TaskListResponse,
    ErrorResponse,
)

__all__ = [
    "mcp",
    "TaskStatus",
    "CreateTaskInput",
    "ListTasksInput",
    "TaskIdInput",
    "UpdateTaskInput",
    "SearchTasksInput",
    "TaskResponse",
    "TaskDetail",
    "TaskListResponse",
    "ErrorResponse",
]
