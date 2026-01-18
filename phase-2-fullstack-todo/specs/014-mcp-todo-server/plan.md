# Implementation Plan: MCP Server for Todo Management

**Feature**: 014-mcp-todo-server
**Date**: 2025-12-30
**Status**: Draft

## Technical Context

### Stack
- **Runtime**: Python 3.11+
- **MCP Framework**: FastMCP 2.x
- **Database ORM**: SQLModel (existing)
- **Database**: Neon Serverless PostgreSQL (existing)
- **Web Framework**: FastAPI (existing)
- **Package Manager**: UV

### Dependencies
```toml
# New dependency to add
fastmcp>=2.0
```

### Existing Infrastructure (Reused)
- `backend/db.py`: Database engine and session management
- `backend/models.py`: Task, User, TaskTag models
- `backend/main.py`: FastAPI application entry point

## Constitution Compliance Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Clean Code | ✅ Pass | Single responsibility per tool, clear docstrings |
| II. Type Safety | ✅ Pass | Full type hints, Pydantic validation |
| III. Accessibility | N/A | Backend MCP server, no UI |
| IV. Performance | ✅ Pass | O(n) queries with indexes, efficient patterns |
| V. Modularity | ✅ Pass | Separate schemas, tools, server modules |
| VI. Security | ✅ Pass | User isolation via user_id filter |
| VII. Stateless | ✅ Pass | No in-memory state, DB as source of truth |

## Project Structure

```
backend/
├── mcp_server/
│   ├── __init__.py           # Package initialization with mcp instance
│   ├── server.py             # FastMCP server setup and configuration
│   ├── tools.py              # MCP tool implementations (6 tools)
│   └── schemas.py            # Pydantic input/output schemas
├── tests/
│   └── test_mcp_tools.py     # Unit tests for MCP tools
└── main.py                   # Updated with MCP server mount
```

## Implementation Phases

### Phase 1: Package Setup and Schemas
**Objective**: Create mcp_server package with Pydantic schemas

**Tasks**:
1. Add `fastmcp>=2.0` to pyproject.toml
2. Create `backend/mcp_server/__init__.py`
3. Create `backend/mcp_server/schemas.py` with:
   - `TaskStatus` enum (all, pending, completed)
   - `CreateTaskInput` model
   - `UpdateTaskInput` model with at-least-one validator
   - `ListTasksInput` model
   - `SearchTasksInput` model
   - `TaskIdInput` model
   - `TaskResponse` model
   - `TaskListResponse` model
   - `TaskDetail` model
   - `ErrorResponse` model

**Validation Criteria**:
- All schemas pass mypy type checking
- Pydantic validation works correctly
- Import succeeds without errors

### Phase 2: MCP Server Core
**Objective**: Create FastMCP server with database lifespan

**Tasks**:
1. Create `backend/mcp_server/server.py` with:
   - FastMCP instance initialization
   - Database lifespan context manager
   - Combined lifespan for FastAPI integration
   - HTTP app creation with `/mcp` path

**Pattern** (from research.md):
```python
from contextlib import asynccontextmanager
from fastmcp import FastMCP
from sqlmodel import Session

mcp = FastMCP("TodoManager", json_response=True)

@asynccontextmanager
async def get_db_session():
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
```

**Validation Criteria**:
- MCP server initializes without errors
- Lifespan properly manages database connections
- Server can be imported by main.py

### Phase 3: Tool Implementation
**Objective**: Implement all 6 MCP tools

**Tasks**:
1. Create `backend/mcp_server/tools.py` with:
   - `create_task`: Create new task for user
   - `list_tasks`: List tasks with status filter
   - `mark_complete`: Mark task as completed (idempotent)
   - `update_task`: Update title/description
   - `delete_task`: Delete task permanently
   - `search_tasks`: Search by keyword (ILIKE)

**Tool Signatures**:
```python
@mcp.tool
async def create_task(user_id: str, title: str, description: str = "") -> dict:
    """Create a new task for the user."""

@mcp.tool
async def list_tasks(user_id: str, status: str = "all") -> dict:
    """List tasks for a user with optional filtering."""

@mcp.tool
async def mark_complete(user_id: str, task_id: str) -> dict:
    """Mark a task as completed."""

@mcp.tool
async def update_task(user_id: str, task_id: str, title: str = None, description: str = None) -> dict:
    """Update task title and/or description."""

@mcp.tool
async def delete_task(user_id: str, task_id: str) -> dict:
    """Permanently delete a task."""

@mcp.tool
async def search_tasks(user_id: str, query: str) -> dict:
    """Search tasks by keyword in title or description."""
```

**Validation Criteria**:
- Each tool returns correct response format
- User isolation enforced (all queries filter by user_id)
- Error responses follow ErrorResponse schema
- Search is case-insensitive

### Phase 4: FastAPI Integration
**Objective**: Mount MCP server in existing FastAPI application

**Tasks**:
1. Update `backend/main.py` to:
   - Import MCP server
   - Create combined lifespan handler
   - Mount MCP app at `/mcp` endpoint

**Pattern**:
```python
from mcp_server.server import mcp, mcp_app

@asynccontextmanager
async def combined_lifespan(app: FastAPI):
    # Existing startup logic
    async with mcp_app.lifespan(app):
        yield
    # Cleanup

app = FastAPI(lifespan=combined_lifespan)
app.mount("/mcp", mcp_app)
```

**Validation Criteria**:
- Server starts without errors
- MCP endpoint accessible at `/mcp`
- Existing API endpoints unaffected
- Health check passes

### Phase 5: Testing
**Objective**: Comprehensive test coverage for MCP tools

**Tasks**:
1. Create `backend/tests/test_mcp_tools.py` with:
   - Test fixtures for database and user setup
   - Tests for each tool (success and error cases)
   - User isolation tests
   - Idempotency tests for mark_complete

**Test Cases**:
| Tool | Test Cases |
|------|------------|
| create_task | Success, validation error, empty title |
| list_tasks | All, pending only, completed only, empty list |
| mark_complete | Success, already complete, not found, wrong user |
| update_task | Title only, description only, both, neither (error) |
| delete_task | Success, not found, wrong user |
| search_tasks | Found results, no results, empty query |

**Validation Criteria**:
- All tests pass
- Coverage >= 90% for mcp_server module
- No flaky tests

## Key Design Decisions

### 1. Error Handling Strategy
**Decision**: Return error dictionaries instead of raising exceptions
**Rationale**: MCP tools should return structured errors for AI agents to understand and handle gracefully

### 2. Database Session Management
**Decision**: Use Depends() with async context manager
**Rationale**: Automatic cleanup, consistent with FastAPI patterns, hidden from MCP schema

### 3. User Isolation
**Decision**: Filter all queries by user_id parameter
**Rationale**: Prevents cross-user access, follows existing Phase II patterns

### 4. Search Implementation
**Decision**: PostgreSQL ILIKE for case-insensitive search
**Rationale**: Simple, effective, no additional infrastructure needed

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| FastMCP version incompatibility | Low | High | Pin version, test thoroughly |
| Database connection leaks | Medium | High | Use context managers, test cleanup |
| Performance with large task lists | Low | Medium | Use pagination in list_tasks |

## Integration Points

1. **main.py**: Mount MCP app, combined lifespan
2. **db.py**: Reuse existing engine
3. **models.py**: Reuse Task model (no changes)

## Success Criteria

1. All 6 tools functional and returning correct response formats
2. User isolation verified through tests
3. MCP server accessible at `/mcp` endpoint
4. No breaking changes to existing API
5. Test coverage >= 90%
6. All tests pass in CI

## References

- [Spec](./spec.md): Feature specification
- [Data Model](./data-model.md): Schema definitions
- [Contracts](./contracts/mcp-tools.yaml): API contract
- [Research](./research.md): Technical research and decisions
- [Quickstart](./quickstart.md): Testing guide
- [MCP Server Builder Agent](/.claude/agents/mcp-server-builder.md): Implementation agent
- [MCP Server Tools Skill](/.claude/skills/mcp-server-tools/SKILL.md): Implementation patterns
