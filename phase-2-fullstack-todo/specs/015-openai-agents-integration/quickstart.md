# Quickstart Guide: OpenAI Agents SDK Integration

**Feature**: 015-openai-agents-integration
**Date**: 2025-12-30

## Prerequisites

Before implementing the agent integration:

1. **Existing MCP Server**: The MCP server at `/mcp` must be operational
2. **Database Tables**: `conversations` and `messages` tables must exist
3. **Authentication**: JWT middleware must be working
4. **Environment Variables**:
   ```bash
   OPENAI_API_KEY=sk-...  # Required for OpenAI Agents SDK
   DATABASE_URL=postgresql://...  # Existing
   BETTER_AUTH_SECRET=...  # Existing
   ```

## Installation

Add the required dependencies:

```bash
cd backend
uv add openai-agents httpx
```

## File Structure

```
backend/
├── agents/
│   ├── __init__.py
│   ├── agent.py          # TaskManagerAgent definition
│   ├── tools.py          # @function_tool implementations
│   ├── context.py        # AgentContext dataclass
│   └── schemas.py        # Agent-specific Pydantic models
├── routes/
│   └── chat.py           # Chat endpoint
├── services/
│   └── chat_service.py   # Chat orchestration
└── schemas/
    └── chat.py           # ChatRequest/ChatResponse
```

## Basic Usage

### 1. Define the Agent

```python
# backend/agents/agent.py
from agents import Agent
from .tools import (
    create_task, list_tasks, get_task,
    mark_complete, update_task, delete_task, search_tasks
)

AGENT_INSTRUCTIONS = """
You are TaskWave, a helpful task management assistant.
... (full instructions from data-model.md)
"""

task_manager_agent = Agent(
    name="TaskManager",
    instructions=AGENT_INSTRUCTIONS,
    model="gpt-4o-mini",
    tools=[
        create_task,
        list_tasks,
        get_task,
        mark_complete,
        update_task,
        delete_task,
        search_tasks,
    ],
)
```

### 2. Define Tools

```python
# backend/agents/tools.py
from agents import function_tool, RunContextWrapper
from .context import AgentContext
import httpx

@function_tool
async def create_task(
    ctx: RunContextWrapper[AgentContext],
    title: str,
    description: str = ""
) -> dict:
    """Create a new task for the user.

    Args:
        title: Task title (1-200 characters)
        description: Optional task description

    Returns:
        dict with task_id, status, and title
    """
    async with httpx.AsyncClient() as client:
        # Call existing MCP tool via internal HTTP
        response = await client.post(
            f"{ctx.context.mcp_base_url}/mcp",
            json={
                "method": "tools/call",
                "params": {
                    "name": "create_task",
                    "arguments": {
                        "user_id": ctx.context.user_id,
                        "title": title,
                        "description": description
                    }
                }
            }
        )
        return response.json()
```

### 3. Create Chat Endpoint

```python
# backend/routes/chat.py
from fastapi import APIRouter, Depends, HTTPException
from agents import Runner
from ..agents.agent import task_manager_agent
from ..agents.context import AgentContext
from ..schemas.chat import ChatRequest, ChatResponse
from ..middleware.auth_middleware import get_current_user

router = APIRouter()

@router.post("/users/{user_id}/chat", response_model=ChatResponse)
async def chat(
    user_id: str,
    request: ChatRequest,
    current_user = Depends(get_current_user)
):
    # Verify user owns this conversation
    if str(current_user.id) != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Create or get conversation
    conversation_id = request.conversation_id or create_new_conversation(user_id)

    # Build message history from database
    messages = get_conversation_messages(conversation_id)

    # Store user message
    store_message(conversation_id, user_id, "user", request.message)

    # Create agent context
    context = AgentContext(
        user_id=user_id,
        conversation_id=conversation_id,
        mcp_base_url="http://localhost:8000"
    )

    # Run agent
    input_messages = messages + [{"role": "user", "content": request.message}]
    result = await Runner.run(
        task_manager_agent,
        input=input_messages,
        context=context
    )

    # Store assistant response
    store_message(conversation_id, user_id, "assistant", result.final_output)

    # Return response
    return ChatResponse(
        conversation_id=conversation_id,
        response=result.final_output,
        tool_calls=extract_tool_calls(result)
    )
```

### 4. Run the Agent

```python
# Test the agent directly
import asyncio
from agents import Runner
from backend.agents.agent import task_manager_agent
from backend.agents.context import AgentContext

async def test_agent():
    context = AgentContext(
        user_id="test-user-uuid",
        conversation_id="test-convo-uuid",
        mcp_base_url="http://localhost:8000"
    )

    result = await Runner.run(
        task_manager_agent,
        input="Add a task to buy groceries",
        context=context
    )

    print(result.final_output)

asyncio.run(test_agent())
```

## Testing

### Unit Tests

```python
# backend/tests/test_agent_tools.py
import pytest
from unittest.mock import patch, AsyncMock
from backend.agents.tools import create_task
from backend.agents.context import AgentContext

@pytest.mark.asyncio
async def test_create_task():
    # Mock the HTTP client
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "task_id": "123",
            "status": "created",
            "title": "Buy groceries"
        }
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(
            return_value=mock_response
        )

        # Create mock context
        context = AgentContext(
            user_id="test-user",
            conversation_id="test-convo",
            mcp_base_url="http://localhost:8000"
        )

        # Test tool
        result = await create_task(
            ctx=MockRunContext(context),
            title="Buy groceries"
        )

        assert result["status"] == "created"
        assert result["title"] == "Buy groceries"
```

### Integration Tests

```python
# backend/tests/test_chat_endpoint.py
import pytest
from fastapi.testclient import TestClient
from backend.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_chat_creates_task(client, auth_token):
    response = client.post(
        "/api/users/test-user-id/chat",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"message": "Add a task to buy groceries"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    assert "groceries" in data["response"].lower()
    assert len(data["tool_calls"]) > 0
```

## Troubleshooting

### Common Issues

1. **OpenAI API Key Not Set**
   ```
   Error: OPENAI_API_KEY environment variable not set
   ```
   Solution: Add `OPENAI_API_KEY=sk-...` to `.env`

2. **MCP Server Not Running**
   ```
   Error: Connection refused to localhost:8000/mcp
   ```
   Solution: Ensure backend is running with MCP server mounted

3. **Tool Not Found**
   ```
   Error: Tool 'create_task' not registered
   ```
   Solution: Ensure all tools are passed to Agent's `tools` parameter

4. **Context Not Available**
   ```
   Error: context.user_id is None
   ```
   Solution: Ensure AgentContext is properly created and passed to Runner.run()

## Next Steps

After basic integration:

1. Add conversation persistence to database
2. Implement message history retrieval
3. Add error handling for AI service unavailability
4. Implement rate limiting
5. Add logging for debugging
6. Create frontend ChatKit integration
