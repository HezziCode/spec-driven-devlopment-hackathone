"""Agent function tools for task management operations.

All tools call the existing MCP server via httpx, maintaining separation of concerns.
Tools use @function_tool decorator from OpenAI Agents SDK.
"""

import logging

import httpx
from agents import RunContextWrapper, function_tool

from .context import AgentContext
from .schemas import TaskInfo, TaskListResult, TaskOperationResult

logger = logging.getLogger(__name__)


def _generate_fallback_tags(title: str) -> list[str]:
    """Generate fallback tags based on task title keywords."""
    title_lower = title.lower()
    tags = []

    # Category detection
    category_keywords = {
        "shopping": ["buy", "purchase", "shop", "order", "groceries", "store"],
        "work": ["report", "meeting", "email", "project", "deadline", "presentation", "office"],
        "personal": ["call", "visit", "meet", "friend", "family", "mom", "dad", "birthday"],
        "health": ["doctor", "gym", "exercise", "workout", "medicine", "appointment", "dentist"],
        "finance": ["pay", "bill", "bank", "transfer", "budget", "invoice", "tax"],
        "study": ["exam", "study", "learn", "course", "homework", "assignment", "research"],
        "home": ["clean", "fix", "repair", "organize", "laundry", "cook"],
        "travel": ["book", "flight", "hotel", "trip", "vacation", "pack"],
    }

    for category, keywords in category_keywords.items():
        if any(kw in title_lower for kw in keywords):
            tags.append(category)
            break

    # Action type detection
    action_keywords = {
        "errands": ["buy", "pick", "get", "drop"],
        "communication": ["call", "email", "text", "message", "contact"],
        "planning": ["plan", "schedule", "organize", "prepare"],
        "tasks": ["finish", "complete", "do", "make", "create"],
    }

    for action, keywords in action_keywords.items():
        if any(kw in title_lower for kw in keywords):
            tags.append(action)
            break

    # Ensure at least 2 tags
    if len(tags) < 2:
        tags.append("general")
    if len(tags) < 2:
        tags.append("todo")

    return tags[:3]  # Max 3 tags


def _generate_fallback_description(title: str) -> str:
    """Generate a simple fallback description from the title."""
    # Capitalize first letter and ensure it ends properly
    desc = title.strip()
    if desc:
        desc = desc[0].upper() + desc[1:] if len(desc) > 1 else desc.upper()
        if not desc.endswith((".", "!", "?")):
            desc = f"Task: {desc}"
    return desc or "Task created via chat"


@function_tool
async def create_task(
    ctx: RunContextWrapper[AgentContext],
    title: str,
    description: str = "",
    tags: list[str] = None,
    priority: str = "medium",
) -> TaskOperationResult:
    """Create a new task for the user from chat conversation.

    IMPORTANT AUTO-ENRICHMENT RULES (MANDATORY):
    1. If tags are None/empty, YOU MUST generate at least 2 relevant tags based on task context
    2. If description is empty, YOU MUST generate a short, meaningful description
    3. NEVER create a task with empty description or no tags

    Args:
        ctx: RunContextWrapper containing AgentContext with user_id and conversation_id
        title: Task title (1-200 characters)
        description: Optional task description - generate meaningful one if empty
        tags: Optional list of tags for the task - generate at least 2 if empty
        priority: Task priority (low, medium, high, critical) - defaults to medium

    Returns:
        TaskOperationResult with task_id, status, and title
    """
    # Fallback tag generation if LLM doesn't provide tags
    final_tags = tags if tags and len(tags) >= 1 else _generate_fallback_tags(title)
    final_description = description if description else _generate_fallback_description(title)

    target_url = f"{ctx.context.mcp_base_url}/api/ai/tasks"
    payload = {
        "user_id": ctx.context.user_id,
        "title": title,
        "description": final_description,
        "tags": final_tags,
        "priority": priority,
        "source": "chat",
        "thread_id": ctx.context.conversation_id,
    }
    logger.info(
        f"🔥 create_task: Calling {target_url} for user {ctx.context.user_id}"
    )
    logger.info(f"🔥 create_task: Payload = {payload}")

    # Call direct AI tools endpoint for task creation
    # Timeout: 60s for production (Render cold start), localhost is fast
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(target_url, json=payload)
            logger.info(f"🔥 create_task: Response status = {response.status_code}")
            response.raise_for_status()

            if response.status_code == 200:
                data = response.json()
                logger.info(
                    f"create_task: Successfully created task {data.get('task_id')} for user {ctx.context.user_id}"
                )
                return TaskOperationResult(
                    task_id=data.get("task_id", ""),
                    status=data.get("status", "created"),
                    title=data.get("title", title),
                )
            else:
                error_msg = f"Failed to create task: HTTP {response.status_code}"
                logger.error(f"create_task: {error_msg}")
                raise RuntimeError(error_msg)
        except httpx.HTTPStatusError as e:
            logger.error(f"🔥 create_task: HTTP STATUS ERROR - {e}")
            logger.error(f"🔥 create_task: Response body = {e.response.text if e.response else 'N/A'}")
            raise RuntimeError(f"HTTP error creating task: {e}")
        except httpx.RequestError as e:
            logger.error(f"🔥 create_task: REQUEST ERROR (connection issue) - {type(e).__name__}: {e}")
            raise RuntimeError(f"Request error creating task: {e}")
        except Exception as e:
            logger.error(f"🔥 create_task: UNEXPECTED ERROR - {type(e).__name__}: {e}")
            raise RuntimeError(f"Error creating task: {e}")


@function_tool
async def list_tasks(
    ctx: RunContextWrapper[AgentContext], status: str = "all"
) -> TaskListResult:
    """List all tasks for the user.

    Args:
        ctx: RunContextWrapper containing AgentContext with user_id
        status: Filter by status: "all", "pending", or "completed"

    Returns:
        TaskListResult with tasks list and total count
    """
    logger.info(
        f"list_tasks: Listing tasks for user {ctx.context.user_id} with status={status}"
    )
    # Call AI tools endpoint (no auth required)
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{ctx.context.mcp_base_url}/api/ai/tasks/list",
                json={"user_id": ctx.context.user_id, "status": status},
            )
            response.raise_for_status()

            if response.status_code == 200:
                data = response.json()
                tasks = [
                    TaskInfo(
                        id=task.get("id", ""),
                        title=task.get("title", ""),
                        description=task.get("description"),
                        completed=task.get("completed", False),
                        priority=task.get("priority", "medium"),
                        created_at=task.get("created_at", ""),
                        updated_at=task.get("updated_at", ""),
                    )
                    for task in data.get("tasks", [])
                ]
                logger.info(
                    f"list_tasks: Successfully listed {len(tasks)} tasks for user {ctx.context.user_id}"
                )
                return TaskListResult(tasks=tasks, total=data.get("total", len(tasks)))
            else:
                error_msg = "Failed to list tasks"
                logger.error(f"list_tasks: {error_msg}")
                raise RuntimeError(error_msg)
        except httpx.HTTPStatusError as e:
            logger.error(f"list_tasks: HTTP error - {e}")
            raise RuntimeError(f"HTTP error listing tasks: {e}")
        except httpx.RequestError as e:
            logger.error(f"list_tasks: Request error - {e}")
            raise RuntimeError(f"Request error listing tasks: {e}")
        except Exception as e:
            logger.error(f"list_tasks: Unexpected error - {e}")
            raise RuntimeError(f"Error listing tasks: {e}")


@function_tool
async def get_task(ctx: RunContextWrapper[AgentContext], task_id: str) -> TaskInfo:
    """Retrieve a specific task for the user.

    Args:
        ctx: RunContextWrapper containing AgentContext with user_id
        task_id: UUID of the task to retrieve

    Returns:
        TaskInfo with task details
    """
    logger.info(f"get_task: Retrieving task {task_id} for user {ctx.context.user_id}")
    # Call AI tools endpoint (no auth required)
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{ctx.context.mcp_base_url}/api/ai/tasks/{task_id}/get",
                json={"user_id": ctx.context.user_id},
            )
            response.raise_for_status()

            if response.status_code == 200:
                data = response.json()
                logger.info(
                    f"get_task: Successfully retrieved task {task_id} for user {ctx.context.user_id}"
                )
                return TaskInfo(
                    id=data.get("id", task_id),
                    title=data.get("title", ""),
                    description=data.get("description"),
                    completed=data.get("completed", False),
                    priority=data.get("priority", "medium"),
                    created_at=data.get("created_at", ""),
                    updated_at=data.get("updated_at", ""),
                )
            else:
                error_msg = "Task not found"
                logger.error(f"get_task: {error_msg}")
                raise RuntimeError(error_msg)
        except httpx.HTTPStatusError as e:
            logger.error(f"get_task: HTTP error - {e}")
            raise RuntimeError(f"HTTP error retrieving task: {e}")
        except httpx.RequestError as e:
            logger.error(f"get_task: Request error - {e}")
            raise RuntimeError(f"Request error retrieving task: {e}")
        except Exception as e:
            logger.error(f"get_task: Unexpected error - {e}")
            raise RuntimeError(f"Error retrieving task: {e}")


@function_tool
async def mark_complete(
    ctx: RunContextWrapper[AgentContext], task_id: str
) -> TaskOperationResult:
    """Mark a task as completed.

    Args:
        ctx: RunContextWrapper containing AgentContext with user_id
        task_id: UUID of the task to mark complete

    Returns:
        TaskOperationResult with task_id, status, and title
    """
    logger.info(
        f"mark_complete: Marking task {task_id} as complete for user {ctx.context.user_id}"
    )
    # Call AI tools endpoint (no auth required)
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{ctx.context.mcp_base_url}/api/ai/tasks/{task_id}/complete",
                json={"user_id": ctx.context.user_id},
            )
            response.raise_for_status()

            if response.status_code == 200:
                data = response.json()
                logger.info(
                    f"mark_complete: Successfully marked task {task_id} as complete for user {ctx.context.user_id}"
                )
                return TaskOperationResult(
                    task_id=task_id, status="completed", title=data.get("title", "Task")
                )
            else:
                error_msg = "Task not found"
                logger.error(f"mark_complete: {error_msg}")
                raise RuntimeError(error_msg)
        except httpx.HTTPStatusError as e:
            logger.error(f"mark_complete: HTTP error - {e}")
            raise RuntimeError(f"HTTP error marking task complete: {e}")
        except httpx.RequestError as e:
            logger.error(f"mark_complete: Request error - {e}")
            raise RuntimeError(f"Request error marking task complete: {e}")
        except Exception as e:
            logger.error(f"mark_complete: Unexpected error - {e}")
            raise RuntimeError(f"Error marking task complete: {e}")


@function_tool
async def update_task(
    ctx: RunContextWrapper[AgentContext],
    task_id: str,
    title: str = None,
    description: str = None,
) -> TaskOperationResult:
    """Update an existing task.

    Args:
        ctx: RunContextWrapper containing AgentContext with user_id
        task_id: UUID of the task to update
        title: New task title (optional)
        description: New task description (optional)

    Returns:
        TaskOperationResult with task_id, status, and title
    """
    logger.info(f"update_task: Updating task {task_id} for user {ctx.context.user_id}")
    # Call AI tools endpoint (no auth required)
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.put(
                f"{ctx.context.mcp_base_url}/api/ai/tasks/{task_id}",
                json={
                    "user_id": ctx.context.user_id,
                    "title": title,
                    "description": description,
                },
            )
            response.raise_for_status()

            if response.status_code == 200:
                data = response.json()
                logger.info(
                    f"update_task: Successfully updated task {task_id} for user {ctx.context.user_id}"
                )
                return TaskOperationResult(
                    task_id=task_id,
                    status="updated",
                    title=data.get("title", title or "Task"),
                )
            else:
                error_msg = "Task not found"
                logger.error(f"update_task: {error_msg}")
                raise RuntimeError(error_msg)
        except httpx.HTTPStatusError as e:
            logger.error(f"update_task: HTTP error - {e}")
            raise RuntimeError(f"HTTP error updating task: {e}")
        except httpx.RequestError as e:
            logger.error(f"update_task: Request error - {e}")
            raise RuntimeError(f"Request error updating task: {e}")
        except Exception as e:
            logger.error(f"update_task: Unexpected error - {e}")
            raise RuntimeError(f"Error updating task: {e}")


@function_tool
async def delete_task(
    ctx: RunContextWrapper[AgentContext], task_id: str
) -> TaskOperationResult:
    """Delete a task.

    Args:
        ctx: RunContextWrapper containing AgentContext with user_id
        task_id: UUID of the task to delete

    Returns:
        TaskOperationResult with task_id and deletion status
    """
    logger.info(f"delete_task: Deleting task {task_id} for user {ctx.context.user_id}")
    # Call AI tools endpoint (no auth required)
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.request(
                method="DELETE",
                url=f"{ctx.context.mcp_base_url}/api/ai/tasks/{task_id}",
                json={"user_id": ctx.context.user_id},
            )
            response.raise_for_status()

            if response.status_code == 200:
                data = response.json()
                logger.info(
                    f"delete_task: Successfully deleted task {task_id} for user {ctx.context.user_id}"
                )
                return TaskOperationResult(
                    task_id=task_id, status="deleted", title=data.get("title", "Task")
                )
            else:
                error_msg = "Task not found"
                logger.error(f"delete_task: {error_msg}")
                raise RuntimeError(error_msg)
        except httpx.HTTPStatusError as e:
            logger.error(f"delete_task: HTTP error - {e}")
            raise RuntimeError(f"HTTP error deleting task: {e}")
        except httpx.RequestError as e:
            logger.error(f"delete_task: Request error - {e}")
            raise RuntimeError(f"Request error deleting task: {e}")
        except Exception as e:
            logger.error(f"delete_task: Unexpected error - {e}")
            raise RuntimeError(f"Error deleting task: {e}")


@function_tool
async def delete_task_by_name(
    ctx: RunContextWrapper[AgentContext], task_name: str
) -> TaskOperationResult:
    """Delete a task by its name.

    Args:
        ctx: RunContextWrapper containing AgentContext with user_id
        task_name: Name/title of the task to delete

    Returns:
        TaskOperationResult with task_id and deletion status
    """
    logger.info(
        f"delete_task_by_name: Deleting task '{task_name}' for user {ctx.context.user_id}"
    )
    # Call AI tools endpoint (no auth required)
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{ctx.context.mcp_base_url}/api/ai/tasks/delete-by-name",
                json={"user_id": ctx.context.user_id, "task_name": task_name},
            )
            response.raise_for_status()

            if response.status_code == 200:
                data = response.json()
                logger.info(
                    f"delete_task_by_name: Successfully deleted task '{task_name}' for user {ctx.context.user_id}"
                )
                return TaskOperationResult(
                    task_id=data.get("task_id", ""),
                    status="deleted",
                    title=data.get("title", task_name),
                )
            else:
                error_msg = f"Task '{task_name}' not found"
                logger.error(f"delete_task_by_name: {error_msg}")
                raise RuntimeError(error_msg)
        except httpx.HTTPStatusError as e:
            logger.error(f"delete_task_by_name: HTTP error - {e}")
            raise RuntimeError(f"HTTP error deleting task by name: {e}")
        except httpx.RequestError as e:
            logger.error(f"delete_task_by_name: Request error - {e}")
            raise RuntimeError(f"Request error deleting task by name: {e}")
        except Exception as e:
            logger.error(f"delete_task_by_name: Unexpected error - {e}")
            raise RuntimeError(f"Error deleting task by name: {e}")


@function_tool
async def search_tasks(
    ctx: RunContextWrapper[AgentContext], query: str
) -> TaskListResult:
    """Search tasks by keyword.

    Args:
        ctx: RunContextWrapper containing AgentContext with user_id
        query: Search term for task title/description

    Returns:
        TaskListResult with matching tasks list and total count
    """
    logger.info(
        f"search_tasks: Searching tasks with query '{query}' for user {ctx.context.user_id}"
    )
    # Call AI tools endpoint (no auth required)
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{ctx.context.mcp_base_url}/api/ai/tasks/search",
                json={"user_id": ctx.context.user_id, "query": query},
            )
            response.raise_for_status()

            if response.status_code == 200:
                data = response.json()
                tasks = [
                    TaskInfo(
                        id=task.get("id", ""),
                        title=task.get("title", ""),
                        description=task.get("description"),
                        completed=task.get("completed", False),
                        priority=task.get("priority", "medium"),
                        created_at=task.get("created_at", ""),
                        updated_at=task.get("updated_at", ""),
                    )
                    for task in data.get("tasks", [])
                ]
                logger.info(
                    f"search_tasks: Found {len(tasks)} tasks matching '{query}' for user {ctx.context.user_id}"
                )
                return TaskListResult(tasks=tasks, total=data.get("total", len(tasks)))
            else:
                error_msg = "Failed to search tasks"
                logger.error(f"search_tasks: {error_msg}")
                raise RuntimeError(error_msg)
        except httpx.HTTPStatusError as e:
            logger.error(f"search_tasks: HTTP error - {e}")
            raise RuntimeError(f"HTTP error searching tasks: {e}")
        except httpx.RequestError as e:
            logger.error(f"search_tasks: Request error - {e}")
            raise RuntimeError(f"Request error searching tasks: {e}")
        except Exception as e:
            logger.error(f"search_tasks: Unexpected error - {e}")
            raise RuntimeError(f"Error searching tasks: {e}")
