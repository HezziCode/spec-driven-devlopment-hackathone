# Research: OpenAI Agents SDK Integration

**Feature**: 015-openai-agents-integration
**Date**: 2025-12-30
**Status**: Complete

## Research Questions Resolved

### Q1: How to structure @function_tool decorators?

**Finding**: The OpenAI Agents SDK provides a `@function_tool` decorator that:
- Automatically generates tool schema from type hints and docstrings
- Supports both sync and async functions
- Docstrings become the tool description (LLM reads these)
- Type hints define parameter schema
- Can return Pydantic models for structured output

**Code Pattern**:
```python
from agents import Agent, Runner, function_tool
from typing import Optional

@function_tool
def create_task(user_id: str, title: str, description: str = "") -> dict:
    """Create a new task for the user.

    Args:
        user_id: UUID of the user who owns the task
        title: Task title (required)
        description: Optional task description

    Returns:
        dict with task_id, status, and title
    """
    # Implementation calls existing MCP tools
    return {"task_id": "...", "status": "created", "title": title}
```

### Q2: How to pass user context to tools?

**Finding**: Use `RunContextWrapper` to pass context to tools:

```python
from agents import RunContextWrapper, function_tool
from dataclasses import dataclass

@dataclass
class AgentContext:
    user_id: str
    api_base_url: str

@function_tool
async def list_tasks(ctx: RunContextWrapper[AgentContext], status: str = "all") -> dict:
    """List tasks for the authenticated user."""
    user_id = ctx.context.user_id  # Access context
    # Call backend API
    return {"tasks": [...], "total": 5}
```

### Q3: How to use Runner.run() for async execution?

**Finding**: `Runner.run()` is the primary method for executing agents:

```python
from agents import Agent, Runner

agent = Agent(
    name="TaskManager",
    instructions="You are a helpful task management assistant...",
    model="gpt-4o-mini",
    tools=[create_task, list_tasks, mark_complete, ...]
)

async def handle_chat(user_id: str, message: str):
    context = AgentContext(user_id=user_id, api_base_url="http://localhost:8000")
    result = await Runner.run(
        agent,
        input=message,
        context=context,
        max_turns=10  # Prevent infinite loops
    )
    return result.final_output
```

### Q4: How should the agent call existing MCP tools vs direct DB access?

**Finding**: Per FR-004, agent tools should call the existing MCP tools via HTTP, NOT directly access the database. This maintains separation of concerns and allows the MCP server to handle validation/user isolation.

**Integration Pattern**:
```python
import httpx

@function_tool
async def create_task_tool(
    ctx: RunContextWrapper[AgentContext],
    title: str,
    description: str = ""
) -> dict:
    """Create a new task."""
    # Call existing MCP server endpoint
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{ctx.context.api_base_url}/mcp/tools/create_task",
            json={
                "user_id": ctx.context.user_id,
                "title": title,
                "description": description
            }
        )
        return response.json()
```

**Alternative**: Use MCP client to connect directly to MCP server for tool invocation.

### Q5: How to handle conversation context within session?

**Finding**: The SDK supports sessions via `SQLiteSession` or manual conversation management:

```python
# Option 1: Built-in session (stores in SQLite)
from agents import SQLiteSession

session = SQLiteSession("conversation_123")
result = await Runner.run(agent, "Add a task", session=session)

# Option 2: Manual conversation management (DB-backed)
# Store messages in database, build input list for each request
new_input = previous_messages + [{"role": "user", "content": message}]
result = await Runner.run(agent, new_input)
```

For Phase III (stateless architecture), Option 2 is preferred - store messages in the existing `messages` table.

### Q6: Error handling patterns?

**Finding**: Use `failure_error_function` parameter for custom error handling:

```python
from agents import function_tool, RunContextWrapper

def handle_tool_error(context: RunContextWrapper, error: Exception) -> str:
    """Return user-friendly error message."""
    return f"I couldn't complete that action: {str(error)}"

@function_tool(failure_error_function=handle_tool_error)
async def risky_operation() -> str:
    # If this fails, handle_tool_error returns the message
    ...
```

## Design Decisions

### D1: Tool Invocation Strategy
**Decision**: Agent tools will call the existing MCP server tools via internal HTTP calls.
**Rationale**:
- Reuses existing validation and user isolation logic
- Maintains single source of truth for task operations
- Allows MCP tools to evolve independently
- Easier testing (mock HTTP calls)

### D2: Conversation Context
**Decision**: Use database-backed conversation history (manual management).
**Rationale**:
- Aligns with Phase III stateless architecture requirement
- Reuses existing `conversations` and `messages` tables
- Server can restart without losing context
- Multiple server instances can handle same conversation

### D3: Model Selection
**Decision**: Use `gpt-4o-mini` as default, with option for `gpt-4o` for complex reasoning.
**Rationale**:
- Cost efficiency for routine task operations
- gpt-4o-mini handles NLU well for task management
- Option to escalate for complex multi-step operations

### D4: Agent Instructions Focus
**Decision**: Instructions will emphasize:
- Extract task details from casual conversation
- Ask for clarification when intent is ambiguous
- Confirm actions with user-friendly responses
- Handle multiple tasks in one message

### D5: Session Scope
**Decision**: Maintain context within single conversation_id.
**Rationale**:
- User can start fresh conversation anytime
- Previous conversation context is preserved per conversation
- Aligns with existing database schema

## Dependencies Confirmed

| Dependency | Version | Status |
|------------|---------|--------|
| openai-agents | 0.2.x+ | To be added |
| httpx | Latest | To be added (async HTTP client) |
| Existing MCP Server | Implemented | Available at `/mcp` |
| Conversations table | Defined | Schema in constitution |
| Messages table | Defined | Schema in constitution |

## Unknowns Resolved

- [x] @function_tool decorator patterns
- [x] Context passing mechanism
- [x] Runner.run() async execution
- [x] Error handling patterns
- [x] Session/conversation management
- [x] Integration with existing MCP tools

## Next Steps

1. **Phase 1**: Design data model (AgentContext, tool schemas)
2. **Phase 1**: Define API contracts (chat endpoint request/response)
3. **Phase 1**: Create quickstart guide for agent usage
4. **Write plan.md**: Complete implementation plan
