---
name: chatkit-server-streaming
description: Build ChatKit Python server backends with streaming responses. Use when implementing chat backends, handling thread management, integrating with OpenAI Agents, or setting up SSE streaming endpoints.
---

# ChatKit Server Streaming Skill

## Purpose
Implement ChatKit Python server backends that handle chat sessions, thread management, and streaming responses for real-time AI interactions.

## Context
Used for building chat backend services that integrate with ChatKit React frontend and OpenAI Agents SDK.

## Pattern

### Basic ChatKit Server
```python
from typing import AsyncIterator
from chatkit.server import ChatKitServer, StreamingResult
from chatkit.types import (
    ThreadMetadata,
    UserMessageItem,
    ThreadStreamEvent,
    AssistantMessageEvent,
)

class MyChatKitServer(ChatKitServer[MyRequestContext]):
    async def respond(
        self,
        thread: ThreadMetadata,
        input_user_message: UserMessageItem | None,
        context: MyRequestContext,
    ) -> AsyncIterator[ThreadStreamEvent]:
        """Handle incoming chat messages and stream responses."""
        
        # Get user message text
        user_text = input_user_message.text if input_user_message else ""
        
        # Process with AI agent
        agent_context = AgentContext(
            user_id=context.user_id,
            thread_id=thread.id,
        )
        
        result = await Runner.run(
            task_agent,
            input=user_text,
            context=agent_context,
        )
        
        # Stream response
        yield AssistantMessageEvent(
            text=result.final_output
        )
```

### FastAPI Integration
```python
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
from chatkit.server import StreamingResult

app = FastAPI()
server = MyChatKitServer(store=PostgresThreadStore())

@app.post("/chatkit")
async def chatkit_endpoint(request: Request):
    """ChatKit endpoint for chat interactions."""
    context = MyRequestContext(
        user_id=request.state.user_id,
        session_id=request.headers.get("X-Session-ID"),
    )
    
    result = await server.process(await request.body(), context)
    
    if isinstance(result, StreamingResult):
        return StreamingResponse(
            result,
            media_type="text/event-stream"
        )
    return Response(
        content=result.json,
        media_type="application/json"
    )
```

### Streaming Events
```python
from chatkit.types import (
    AssistantMessageEvent,
    ProgressUpdateEvent,
    ClientEffectEvent,
)

async def respond(...) -> AsyncIterator[ThreadStreamEvent]:
    # Progress update
    yield ProgressUpdateEvent(
        icon="search",
        text="Searching your tasks..."
    )
    
    # Perform operation
    tasks = await search_tasks(query)
    
    # Client effect (trigger UI update)
    yield ClientEffectEvent(
        name="refresh_task_list",
        data={"count": len(tasks)}
    )
    
    # Final response
    yield AssistantMessageEvent(
        text=f"Found {len(tasks)} matching tasks."
    )
```

### Thread Store Implementation
```python
from chatkit.server import ThreadStore
from sqlmodel import Session

class PostgresThreadStore(ThreadStore):
    async def get_thread(self, thread_id: str) -> ThreadMetadata | None:
        with Session(engine) as session:
            thread = session.get(Thread, thread_id)
            return ThreadMetadata(id=thread.id, ...) if thread else None
    
    async def save_thread(self, thread: ThreadMetadata) -> None:
        with Session(engine) as session:
            db_thread = Thread(**thread.dict())
            session.merge(db_thread)
            session.commit()
```

## Key Principles
1. Async Everything: Use async/await for all I/O operations
2. Stream Early: Yield progress updates to keep UI responsive
3. Context Propagation: Pass user context through to agents
4. Error Handling: Catch and yield error events, don't crash
5. Thread Persistence: Store threads for conversation continuity

## References
- references/event-types.md - All ThreadStreamEvent types
- references/thread-store-patterns.md - Storage implementations
- examples/complete-chatkit-server.py - Full example
```
