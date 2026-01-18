# Quickstart: MCP Server for Todo Management

**Feature**: 014-mcp-todo-server
**Date**: 2025-12-30

## Prerequisites

- Python 3.11+
- UV package manager
- Existing Phase II backend with Neon PostgreSQL connection
- Environment variables configured (DATABASE_URL)

## Installation

```bash
cd backend
uv add fastmcp
```

## Quick Test

### 1. Start the Server

```bash
cd backend
uv run uvicorn main:app --reload
```

The MCP server will be mounted at `/mcp` endpoint.

### 2. Test with FastMCP CLI

```bash
# List available tools
fastmcp dev backend/mcp_server/server.py

# Or test individual tool
python -c "
from backend.mcp_server.tools import create_task
result = create_task(
    user_id='test-user-id',
    title='Test Task',
    description='Testing MCP tool'
)
print(result)
"
```

### 3. Test via MCP Client

```python
from fastmcp.client import Client

async def test_tools():
    async with Client("http://localhost:8000/mcp") as client:
        # List tools
        tools = await client.list_tools()
        print(f"Available tools: {[t.name for t in tools]}")

        # Create a task
        result = await client.call_tool(
            "create_task",
            {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread"
            }
        )
        print(f"Created: {result.data}")

        # List tasks
        result = await client.call_tool(
            "list_tasks",
            {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "pending"
            }
        )
        print(f"Tasks: {result.data}")

import asyncio
asyncio.run(test_tools())
```

## Tool Reference

| Tool | Description | Required Params |
|------|-------------|-----------------|
| `create_task` | Create new task | user_id, title |
| `list_tasks` | List user tasks | user_id |
| `mark_complete` | Mark task done | user_id, task_id |
| `update_task` | Update task details | user_id, task_id, (title or description) |
| `delete_task` | Delete task | user_id, task_id |
| `search_tasks` | Search by keyword | user_id, query |

## Response Format

### Success Response
```json
{
  "task_id": "uuid",
  "status": "created|updated|deleted|completed",
  "title": "Task title"
}
```

### List Response
```json
{
  "tasks": [
    {
      "id": "uuid",
      "title": "Task title",
      "description": "Details",
      "completed": false,
      "priority": "medium",
      "created_at": "2025-12-30T00:00:00Z",
      "updated_at": "2025-12-30T00:00:00Z"
    }
  ],
  "total": 1
}
```

### Error Response
```json
{
  "error": "Task not found",
  "code": "NOT_FOUND",
  "task_id": "uuid"
}
```

## Integration with OpenAI Agents SDK

```python
from openai import OpenAI
from openai.agents import Agent

# Agent automatically discovers MCP tools
agent = Agent(
    name="TodoAssistant",
    mcp_servers=["http://localhost:8000/mcp"]
)

# Agent can now use create_task, list_tasks, etc.
response = agent.run("Create a task to buy groceries")
```

## Troubleshooting

### Database Connection Error
- Verify `DATABASE_URL` environment variable is set
- Check Neon PostgreSQL is accessible
- Ensure SSL mode is enabled for Neon

### Tool Not Found
- Verify MCP server is mounted at `/mcp`
- Check server logs for registration errors
- Ensure all tools have proper docstrings

### User Isolation Errors
- Verify user_id matches existing user in database
- Check task ownership before operations
