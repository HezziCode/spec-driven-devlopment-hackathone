"""Agent function tools for task management operations.

All tools call the existing MCP server via httpx, maintaining separation of concerns.
Tools use @function_tool decorator from OpenAI Agents SDK.
"""

import logging
import httpx
from agents import function_tool, RunContextWrapper
from .context import AgentContext
from .schemas import TaskOperationResult, TaskListResult, TaskInfo

logger = logging.getLogger(__name__)


@function_tool
async def create_task(
    ctx: RunContextWrapper[AgentContext],
    title: str,
    description: str = ""
) -> TaskOperationResult:
    """Create a new task for the user from chat conversation.

    Args:
        ctx: RunContextWrapper containing AgentContext with user_id and conversation_id
        title: Task title (1-200 characters)
        description: Optional task description

    Returns:
        TaskOperationResult with task_id, status, and title
    """
    logger.info(f"create_task: Creating task '{title}' for user {ctx.context.user_id} from chat")
    # Call direct AI tools endpoint for task creation
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{ctx.context.mcp_base_url}/api/ai/tasks",
                headers={
                    "Authorization": f"Bearer {ctx.context.jwt_token}"
                },
                json={
                    "user_id": ctx.context.user_id,
                    "title": title,
                    "description": description,
                    "source": "chat",  # Mark as chat-created
                    "thread_id": ctx.context.conversation_id  # Link to chat thread
                }
            )
            response.raise_for_status()

            if response.status_code == 200:
                data = response.json()
                logger.info(f"create_task: Successfully created task {data.get('task_id')} for user {ctx.context.user_id}")
                return TaskOperationResult(
                    task_id=data.get("task_id", ""),
                    status=data.get("status", "created"),
                    title=data.get("title", title)
                )
            else:
                error_msg = f"Failed to create task: HTTP {response.status_code}"
                logger.error(f"create_task: {error_msg}")
                raise RuntimeError(error_msg)
        except httpx.HTTPStatusError as e:
            logger.error(f"create_task: HTTP error - {e}")
            raise RuntimeError(f"HTTP error creating task: {e}")
        except httpx.RequestError as e:
            logger.error(f"create_task: Request error - {e}")
            raise RuntimeError(f"Request error creating task: {e}")
        except Exception as e:
            logger.error(f"create_task: Unexpected error - {e}")
            raise RuntimeError(f"Error creating task: {e}")


@function_tool
async def list_tasks(
    ctx: RunContextWrapper[AgentContext],
    status: str = "all"
) -> TaskListResult:
    """List all tasks for the user.

    Args:
        ctx: RunContextWrapper containing AgentContext with user_id
        status: Filter by status: "all", "pending", or "completed"

    Returns:
        TaskListResult with tasks list and total count
    """
    # Build query parameters based on status filter
    params = {"user_id": ctx.context.user_id}
    if status != "all":
        params["status"] = status

    # Call direct AI tools endpoint for task listing
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(
                f"{ctx.context.mcp_base_url}/users/{ctx.context.user_id}/tasks",
                headers={
                    "Authorization": f"Bearer {ctx.context.jwt_token}"
                },
                params=params
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
                        updated_at=task.get("updated_at", "")
                    )
                    for task in data.get("tasks", [])
                ]
                return TaskListResult(tasks=tasks, total=data.get("total", 0))
            else:
                error_msg = f"Failed to list tasks: HTTP {response.status_code}"
                raise RuntimeError(error_msg)
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"HTTP error listing tasks: {e}")
        except httpx.RequestError as e:
            raise RuntimeError(f"Request error listing tasks: {e}")
        except Exception as e:
            raise RuntimeError(f"Error listing tasks: {e}")


@function_tool
async def get_task(
    ctx: RunContextWrapper[AgentContext],
    task_id: str
) -> TaskInfo:
    """Retrieve a specific task for the user.

    Args:
        ctx: RunContextWrapper containing AgentContext with user_id
        task_id: UUID of the task to retrieve

    Returns:
        TaskInfo with task details
    """
    # Call direct AI tools endpoint for task retrieval
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(
                f"{ctx.context.mcp_base_url}/users/{ctx.context.user_id}/tasks/{task_id}",
                headers={
                    "Authorization": f"Bearer {ctx.context.jwt_token}"
                }
            )
            response.raise_for_status()

            if response.status_code == 200:
                data = response.json()
                return TaskInfo(
                    id=data.get("id", task_id),
                    title=data.get("title", ""),
                    description=data.get("description"),
                    completed=data.get("completed", False),
                    priority=data.get("priority", "medium"),
                    created_at=data.get("created_at", ""),
                    updated_at=data.get("updated_at", "")
                )
            else:
                error_msg = f"Task not found: HTTP {response.status_code}"
                raise RuntimeError(error_msg)
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"HTTP error retrieving task: {e}")
        except httpx.RequestError as e:
            raise RuntimeError(f"Request error retrieving task: {e}")
        except Exception as e:
            raise RuntimeError(f"Error retrieving task: {e}")


@function_tool
async def mark_complete(
    ctx: RunContextWrapper[AgentContext],
    task_id: str
) -> TaskOperationResult:
    """Mark a task as completed.

    Args:
        ctx: RunContextWrapper containing AgentContext with user_id
        task_id: UUID of the task to mark complete

    Returns:
        TaskOperationResult with task_id, status, and title
    """
    # Prepare update payload to mark task as completed
    update_payload = {
        "completed": True
    }

    # Call direct AI tools endpoint for task updates
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.patch(
                f"{ctx.context.mcp_base_url}/api/ai/tasks/{task_id}",
                headers={
                    "Authorization": f"Bearer {ctx.context.jwt_token}",
                    "Content-Type": "application/json"
                },
                json=update_payload
            )
            response.raise_for_status()

            if response.status_code == 200:
                data = response.json()
                return TaskOperationResult(
                    task_id=task_id,
                    status="completed",
                    title=data.get("title", "Task")
                )
            else:
                error_msg = f"Failed to mark task complete: HTTP {response.status_code}"
                raise RuntimeError(error_msg)
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"HTTP error marking task complete: {e}")
        except httpx.RequestError as e:
            raise RuntimeError(f"Request error marking task complete: {e}")
        except Exception as e:
            raise RuntimeError(f"Error marking task complete: {e}")


@function_tool
async def update_task(
    ctx: RunContextWrapper[AgentContext],
    task_id: str,
    title: str = None,
    description: str = None
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
    # Build update payload
    update_payload = {}
    if title is not None:
        update_payload["title"] = title
    if description is not None:
        update_payload["description"] = description

    # If no fields to update, raise error
    if not update_payload:
        raise RuntimeError("At least one field (title or description) must be provided for update")

    # Call direct AI tools endpoint for task updates
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.put(
                f"{ctx.context.mcp_base_url}/api/ai/tasks/{task_id}",
                headers={
                    "Authorization": f"Bearer {ctx.context.jwt_token}",
                    "Content-Type": "application/json"
                },
                json=update_payload
            )
            response.raise_for_status()

            if response.status_code == 200:
                data = response.json()
                return TaskOperationResult(
                    task_id=task_id,
                    status="updated",
                    title=data.get("title", title or "Task")
                )
            else:
                error_msg = f"Failed to update task: HTTP {response.status_code}"
                raise RuntimeError(error_msg)
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"HTTP error updating task: {e}")
        except httpx.RequestError as e:
            raise RuntimeError(f"Request error updating task: {e}")
        except Exception as e:
            raise RuntimeError(f"Error updating task: {e}")


@function_tool
async def delete_task(
    ctx: RunContextWrapper[AgentContext],
    task_id: str
) -> TaskOperationResult:
    """Delete a task.

    Args:
        ctx: RunContextWrapper containing AgentContext with user_id
        task_id: UUID of the task to delete

    Returns:
        TaskOperationResult with task_id and deletion status
    """
    # Call direct AI tools endpoint for task deletion
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.delete(
                f"{ctx.context.mcp_base_url}/api/ai/tasks/{task_id}",
                headers={
                    "Authorization": f"Bearer {ctx.context.jwt_token}"
                }
            )
            response.raise_for_status()

            if response.status_code == 200:
                data = response.json()
                return TaskOperationResult(
                    task_id=task_id,
                    status="deleted",
                    title=data.get("title", "Task")
                )
            else:
                error_msg = f"Failed to delete task: HTTP {response.status_code}"
                raise RuntimeError(error_msg)
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"HTTP error deleting task: {e}")
        except httpx.RequestError as e:
            raise RuntimeError(f"Request error deleting task: {e}")
        except Exception as e:
            raise RuntimeError(f"Error deleting task: {e}")


@function_tool
async def search_tasks(
    ctx: RunContextWrapper[AgentContext],
    query: str
) -> TaskListResult:
    """Search tasks by keyword.

    Args:
        ctx: RunContextWrapper containing AgentContext with user_id
        query: Search term for task title/description

    Returns:
        TaskListResult with matching tasks list and total count
    """
    # First, get all tasks for the user
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(
                f"{ctx.context.mcp_base_url}/users/{ctx.context.user_id}/tasks",
                headers={
                    "Authorization": f"Bearer {ctx.context.jwt_token}"
                }
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
                        updated_at=task.get("updated_at", "")
                    )
                    for task in data.get("tasks", [])
                ]
                return TaskListResult(tasks=tasks, total=data.get("total", 0))
            else:
                error_msg = f"Failed to search tasks: HTTP {response.status_code}"
                raise RuntimeError(error_msg)
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"HTTP error searching tasks: {e}")
        except httpx.RequestError as e:
            raise RuntimeError(f"Request error searching tasks: {e}")
        except Exception as e:
            raise RuntimeError(f"Error searching tasks: {e}")
