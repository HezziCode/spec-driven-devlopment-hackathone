---
name: mcp-server-tools
description: Create MCP servers with FastMCP for exposing tools to AI agents. Use when building MCP tool servers, defining tool schemas, implementing database-connected tools, setting up MCP transport layers, or when the user mentions FastMCP or Model Context Protocol. MCP tool servers, defining tool schemas, implementing database-connected tools, or setting up MCP transport layers.
---

# MCP Server Tools Skill

## Purpose
Build Model Context Protocol (MCP) servers using FastMCP that expose tools for AI agent consumption with proper schema validation and database integration.

## Context
Used for creating MCP servers that provide tools for task management, database operations, and AI agent integrations.

## Pattern

### Basic MCP Server with Tools
```python
from mcp.server.fastmcp import FastMCP

# Create MCP server instance
mcp = FastMCP("TaskManager", json_response=True)

@mcp.tool()
def create_task(title: str, description: str = "", priority: str = "medium") -> dict:
    """Create a new task with the given details.
    
    Args:
        title: The task title (required)
        description: Optional task description
        priority: Task priority (low, medium, high, critical)
    
    Returns:
        Created task object with id, title, and metadata
    """
    # Implementation here
    return {"id": "uuid", "title": title, "priority": priority}

@mcp.tool()
def list_tasks(
    user_id: str,
    status: str = "all",
    limit: int = 20
) -> dict:
    """List tasks for a user with optional filtering.
    
    Args:
        user_id: The user's UUID
        status: Filter by status (all, completed, pending)
        limit: Maximum number of tasks to return
    
    Returns:
        List of tasks with total count
    """
    return {"tasks": [], "total": 0}

# Run server with transport
if __name__ == "__main__":
    mcp.run(transport="streamable-http")
```

### MCP Server with Database Lifespan
```python
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from mcp.server.fastmcp import FastMCP
from sqlmodel import Session, create_engine

@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[dict]:
    """Manage database connection lifecycle."""
    engine = create_engine(DATABASE_URL)
    try:
        yield {"engine": engine}
    finally:
        engine.dispose()

mcp = FastMCP("TaskManager", lifespan=server_lifespan)

@mcp.tool()
async def get_task(task_id: str, ctx: Context) -> dict:
    """Retrieve a task by ID using database connection from lifespan."""
    engine = ctx.request_context.lifespan_context["engine"]
    with Session(engine) as session:
        task = session.get(Task, task_id)
        return task.model_dump() if task else None
```

### Tool Input/Output Schema Validation
```python
from pydantic import BaseModel, Field
from typing import Optional, List

class TaskInput(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: str = Field("medium", pattern="^(low|medium|high|critical)$")
    tags: List[str] = Field(default_factory=list)

class TaskOutput(BaseModel):
    id: str
    title: str
    completed: bool
    created_at: str

@mcp.tool()
def create_task_validated(task: TaskInput) -> TaskOutput:
    """Create task with Pydantic validation."""
    # Validation happens automatically
    return TaskOutput(...)
```

## Key Principles
1. Schema Validation: Always define inputSchema/outputSchema for tools
2. Lifespan Management: Use async context managers for database connections
3. Error Handling: Return structured errors, don't raise exceptions in tools
4. Documentation: Docstrings become tool descriptions for AI agents
5. Type Safety: Use Pydantic models for complex inputs/outputs

## References
- references/mcp-transport-options.md - HTTP vs stdio transport
- references/tool-schema-patterns.md - Advanced schema patterns
- examples/complete-mcp-server.py - Full working example
```
