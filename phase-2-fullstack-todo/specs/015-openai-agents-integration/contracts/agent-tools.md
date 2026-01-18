# Agent Tools Contract

**Feature**: 015-openai-agents-integration
**Version**: 1.0.0
**Date**: 2025-12-30

## Overview

This document defines the function tool contracts for the TaskManagerAgent. Each tool wraps an existing MCP server tool, adding natural language context handling.

## Tool Definitions

### create_task

Creates a new task from extracted details.

```python
@function_tool
async def create_task(
    ctx: RunContextWrapper[AgentContext],
    title: str,
    description: str = ""
) -> dict:
    """Create a new task for the user.

    Use this when the user mentions adding, creating, or remembering
    something they need to do.

    Args:
        ctx: Agent context with user_id
        title: Task title (1-200 characters)
        description: Optional task description

    Returns:
        dict with task_id, status ("created"), and title
    """
```

**Example Invocations:**
| User Says | Title Extracted |
|-----------|-----------------|
| "Add a task to buy groceries" | "Buy groceries" |
| "I need to call mom" | "Call mom" |
| "Remind me to finish the report" | "Finish the report" |

---

### list_tasks

Lists user's tasks with optional filtering.

```python
@function_tool
async def list_tasks(
    ctx: RunContextWrapper[AgentContext],
    status: str = "all"
) -> dict:
    """List tasks for the user.

    Use this when the user asks to see, show, or list their tasks.

    Args:
        ctx: Agent context with user_id
        status: Filter - "all", "pending", or "completed"

    Returns:
        dict with tasks array and total count
    """
```

**Status Mapping:**
| User Says | Status Value |
|-----------|--------------|
| "Show all my tasks" | "all" |
| "What's pending?" | "pending" |
| "What have I completed?" | "completed" |
| "What do I need to do?" | "pending" |

---

### get_task

Gets details of a specific task.

```python
@function_tool
async def get_task(
    ctx: RunContextWrapper[AgentContext],
    task_id: str
) -> dict:
    """Get details of a specific task.

    Use this when the user asks about a specific task by ID.

    Args:
        ctx: Agent context with user_id
        task_id: UUID of the task

    Returns:
        dict with full task details
    """
```

---

### mark_complete

Marks a task as completed.

```python
@function_tool
async def mark_complete(
    ctx: RunContextWrapper[AgentContext],
    task_id: str
) -> dict:
    """Mark a task as completed.

    Use this when the user indicates they've finished, done, or completed
    a task. First use search_tasks if you need to find the task ID.

    Args:
        ctx: Agent context with user_id
        task_id: UUID of the task to complete

    Returns:
        dict with task_id, status ("completed"), and title
    """
```

**Example Invocations:**
| User Says | Action |
|-----------|--------|
| "I finished the groceries" | Search for "groceries", then mark complete |
| "Mark task 123 as done" | Direct mark_complete with ID |
| "Done with the report" | Search for "report", then mark complete |

---

### update_task

Updates task title and/or description.

```python
@function_tool
async def update_task(
    ctx: RunContextWrapper[AgentContext],
    task_id: str,
    title: str | None = None,
    description: str | None = None
) -> dict:
    """Update a task's title or description.

    Use this when the user wants to change, rename, or update a task.
    At least one of title or description must be provided.

    Args:
        ctx: Agent context with user_id
        task_id: UUID of the task to update
        title: New title (optional)
        description: New description (optional)

    Returns:
        dict with task_id, status ("updated"), and title
    """
```

---

### delete_task

Permanently deletes a task.

```python
@function_tool
async def delete_task(
    ctx: RunContextWrapper[AgentContext],
    task_id: str
) -> dict:
    """Delete a task permanently.

    Use this when the user wants to remove, delete, or cancel a task.
    This action cannot be undone.

    Args:
        ctx: Agent context with user_id
        task_id: UUID of the task to delete

    Returns:
        dict with task_id, status ("deleted"), and title
    """
```

---

### search_tasks

Searches tasks by keyword.

```python
@function_tool
async def search_tasks(
    ctx: RunContextWrapper[AgentContext],
    query: str
) -> dict:
    """Search tasks by keyword in title or description.

    Use this when the user mentions a specific task by name or keyword,
    especially before completing, updating, or deleting.

    Args:
        ctx: Agent context with user_id
        query: Search keyword (1-100 characters)

    Returns:
        dict with matching tasks array and total count
    """
```

## Tool Chaining Patterns

### Pattern 1: Complete by Name

User: "I finished the grocery shopping"

```
1. search_tasks(query="grocery") → finds task
2. mark_complete(task_id=found_id) → marks complete
```

### Pattern 2: Delete by Name

User: "Delete the meeting task"

```
1. search_tasks(query="meeting") → finds task
2. delete_task(task_id=found_id) → deletes task
```

### Pattern 3: Update by Name

User: "Change 'Call mom' to 'Call mom at 5pm'"

```
1. search_tasks(query="Call mom") → finds task
2. update_task(task_id=found_id, title="Call mom at 5pm") → updates
```

### Pattern 4: Multiple Tasks

User: "Add tasks for groceries, laundry, and cleaning"

```
1. create_task(title="Groceries")
2. create_task(title="Laundry")
3. create_task(title="Cleaning")
```

## Error Handling

### Not Found Errors

When a task is not found:
- Agent should respond: "I couldn't find a task matching 'X'. Would you like me to list your tasks?"

### Validation Errors

When input is invalid:
- Agent should respond with a helpful message about what's wrong

### Database Errors

When database operation fails:
- Agent should respond: "I'm having trouble right now. Please try again in a moment."

## Context Injection

All tools receive context via `RunContextWrapper[AgentContext]`:

```python
@dataclass
class AgentContext:
    user_id: str           # From authenticated user
    conversation_id: str   # Current conversation
    mcp_base_url: str      # Backend URL for MCP calls
```

The `user_id` is automatically injected from the chat endpoint's authenticated user, ensuring all tool operations are user-isolated.
