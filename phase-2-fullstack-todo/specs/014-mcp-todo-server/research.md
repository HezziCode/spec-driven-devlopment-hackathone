# Research: MCP Server for Todo Management

**Feature**: 014-mcp-todo-server
**Date**: 2025-12-30

## Research Topics

### 1. FastMCP Framework Pattern

**Decision**: Use FastMCP 2.x with `@mcp.tool` decorator pattern

**Rationale**:
- FastMCP provides a Pythonic interface for creating MCP servers
- The `@mcp.tool` decorator automatically generates tool schemas from type hints
- Built-in support for Pydantic validation
- Supports both sync and async tools
- High source reputation (79.6 benchmark score) per Context7

**Alternatives Considered**:
- Official MCP SDK (lower-level, more boilerplate)
- Custom implementation (unnecessary complexity)

**Pattern**:
```python
from fastmcp import FastMCP

mcp = FastMCP("TodoManager", json_response=True)

@mcp.tool
def create_task(user_id: str, title: str, description: str = "") -> dict:
    """Create a new task for the user."""
    return {"task_id": "...", "status": "created", "title": title}
```

### 2. Database Connection Management

**Decision**: Use `Depends()` pattern with async context manager for database sessions

**Rationale**:
- FastMCP supports dependency injection via `Depends()` from `fastmcp.dependencies`
- Async context managers ensure proper cleanup even on errors
- Dependencies are automatically excluded from MCP schema (hidden from LLM)
- Matches existing FastAPI patterns in Phase II backend

**Pattern**:
```python
from contextlib import asynccontextmanager
from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from sqlmodel import Session

mcp = FastMCP("TodoManager")

@asynccontextmanager
async def get_db_session():
    """Provide database session with automatic cleanup."""
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise

@mcp.tool
async def create_task(
    user_id: str,
    title: str,
    db: Session = Depends(get_db_session)
) -> dict:
    """Create task - db parameter hidden from LLM."""
    # Implementation
```

### 3. FastAPI Integration

**Decision**: Mount MCP server as sub-application within existing FastAPI app

**Rationale**:
- Reuses existing FastAPI infrastructure (CORS, middleware, etc.)
- Combined lifespan management for both apps
- Single deployment unit
- Consistent error handling and logging

**Pattern**:
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastmcp import FastMCP

mcp = FastMCP("TodoManager")
mcp_app = mcp.http_app(path='/mcp')

@asynccontextmanager
async def combined_lifespan(app: FastAPI):
    # Existing app startup (DB connections, etc.)
    async with mcp_app.lifespan(app):
        yield
    # Cleanup

app = FastAPI(lifespan=combined_lifespan)
app.mount("/mcp", mcp_app)
```

### 4. Tool Response Format

**Decision**: Use standardized dictionary responses with status, data, and error fields

**Rationale**:
- Consistent format for all tools aids AI agent understanding
- `json_response=True` on FastMCP ensures proper serialization
- Include task_id, status, title for confirmation messages
- Include error details for graceful error handling

**Pattern**:
```python
# Success response
{"task_id": "uuid", "status": "created", "title": "Buy groceries"}

# Error response
{"error": "Task not found", "code": "NOT_FOUND", "task_id": "uuid"}
```

### 5. Input Validation Strategy

**Decision**: Use Pydantic models for complex inputs, type hints for simple inputs

**Rationale**:
- Pydantic provides automatic validation with clear error messages
- Type hints generate JSON schemas for MCP tools
- FastMCP automatically converts Pydantic validation errors to tool errors
- Consistent with Phase II backend patterns

**Pattern**:
```python
from pydantic import BaseModel, Field

class CreateTaskInput(BaseModel):
    user_id: str = Field(..., description="User UUID")
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field("", max_length=2000)

@mcp.tool
def create_task(input: CreateTaskInput) -> dict:
    """Create a new task."""
    # Validation happens automatically
```

### 6. User Isolation Implementation

**Decision**: Validate user_id in every tool and filter queries by user_id

**Rationale**:
- MCP tools receive user_id as parameter (passed by AI agent)
- Each tool must verify user owns the resource before modification
- Use SQLModel queries with user_id filter
- Return "not found" for resources belonging to other users (don't reveal existence)

**Pattern**:
```python
@mcp.tool
async def get_task(
    user_id: str,
    task_id: str,
    db: Session = Depends(get_db_session)
) -> dict:
    # Query with user_id filter ensures isolation
    task = db.exec(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    ).first()

    if not task:
        return {"error": "Task not found", "code": "NOT_FOUND"}

    return task.model_dump()
```

### 7. Search Implementation

**Decision**: Use PostgreSQL ILIKE for case-insensitive text search

**Rationale**:
- Simple and effective for keyword search
- Supported natively by PostgreSQL
- No additional infrastructure needed
- Sufficient for Phase III requirements

**Pattern**:
```python
from sqlalchemy import or_

@mcp.tool
async def search_tasks(
    user_id: str,
    query: str,
    db: Session = Depends(get_db_session)
) -> dict:
    search_pattern = f"%{query}%"
    tasks = db.exec(
        select(Task).where(
            Task.user_id == user_id,
            or_(
                Task.title.ilike(search_pattern),
                Task.description.ilike(search_pattern)
            )
        )
    ).all()
    return {"tasks": [t.model_dump() for t in tasks], "total": len(tasks)}
```

### 8. Error Handling Strategy

**Decision**: Return error dictionaries instead of raising exceptions in tools

**Rationale**:
- MCP tools should return structured errors for AI agent to understand
- Prevents server crashes from propagating to clients
- Consistent error format aids agent response generation
- FastMCP handles exceptions but structured returns are cleaner

**Pattern**:
```python
@mcp.tool
async def delete_task(user_id: str, task_id: str, db: Session = Depends(get_db_session)) -> dict:
    try:
        task = db.exec(select(Task).where(Task.id == task_id, Task.user_id == user_id)).first()
        if not task:
            return {"error": "Task not found", "code": "NOT_FOUND", "task_id": task_id}

        db.delete(task)
        return {"task_id": str(task.id), "status": "deleted", "title": task.title}
    except Exception as e:
        return {"error": str(e), "code": "DATABASE_ERROR"}
```

## Dependencies to Add

```toml
# In backend/pyproject.toml
[project]
dependencies = [
    # Existing dependencies...
    "fastmcp>=2.0",
]
```

## Files to Create

| File | Purpose |
|------|---------|
| `backend/mcp_server/__init__.py` | Package initialization |
| `backend/mcp_server/server.py` | MCP server setup and configuration |
| `backend/mcp_server/tools.py` | MCP tool implementations |
| `backend/mcp_server/schemas.py` | Pydantic models for tool inputs/outputs |
| `backend/tests/test_mcp_tools.py` | Unit tests for MCP tools |

## Integration Points

1. **main.py**: Mount MCP app with combined lifespan
2. **db.py**: Reuse existing engine and session patterns
3. **models.py**: Reuse existing Task model (no changes needed)
