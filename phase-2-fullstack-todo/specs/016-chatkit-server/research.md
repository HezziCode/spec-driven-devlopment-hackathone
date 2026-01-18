# Research: ChatKit AI Chat Server

## Streaming Implementation (OpenAI Agents SDK)

**Decision**: Use `Runner.run_streamed()` with `stream_events()` filtering.

**Rationale**: The OpenAI Agents SDK provides native streaming support through `run_streamed()`. This returns a `RunResultStreaming` object with `stream_events()` that yields `StreamEvent` objects. For text responses, filter for `ResponseTextDeltaEvent`.

**Implementation Pattern**:
```python
from agents import Agent, Runner
from openai.types.responses import ResponseTextDeltaEvent

result = Runner.run_streamed(agent, input=messages)
async for event in result.stream_events():
    if event.type == "raw_response_event":
        if isinstance(event.data, ResponseTextDeltaEvent):
            yield event.data.delta
```

**Alternatives Considered**:
- `Runner.run()` (blocking) - Waits for complete response, no streaming
- Custom polling - Complex, no real benefit

## Server-Sent Events (SSE) Format

**Decision**: Standard SSE format with `text/event-stream` content-type.

**Format**:
```
data: Hello world\n\n
event: message\n
data: {"thread_id": "..."}\n\n
```

**Rationale**: SSE is the standard HTTP streaming format, supported by all browsers and works with any frontend framework.

**Implementation**:
```python
from fastapi.responses import StreamingResponse
import asyncio

async def generate_events():
    result = Runner.run_streamed(agent, input=messages)
    async for event in result.stream_events():
        if event.type == "raw_response_event":
            if isinstance(event.data, ResponseTextDeltaEvent):
                yield f"data: {event.data.delta}\n\n"

return StreamingResponse(generate_events(), media_type="text/event-stream")
```

## Agent Context for Tools

**Decision**: Use dataclass passed via Runner's context parameter.

**Implementation**:
```python
from dataclasses import dataclass
from agents import Agent

@dataclass
class AgentContext:
    user_id: str
    thread_id: str
    mcp_base_url: str = "http://localhost:8000/mcp"

context = AgentContext(user_id="...", thread_id="...")
result = Runner.run_streamed(agent, input=messages, context=context)
```

**Rationale**: The AgentContext provides user isolation and passes request metadata to all tool invocations. This ensures tools always have the correct user_id.

## Thread Message History

**Decision**: Query last 20 messages, send as conversation history.

**Rationale**:
- Prevents context window overflow
- Maintains recent context for coherent conversations
- 20 messages = ~10 exchanges = sufficient context

**Implementation**:
```python
# Get recent messages for thread
messages = session.exec(
    select(ChatMessage)
    .where(ChatMessage.thread_id == thread_id)
    .order_by(ChatMessage.created_at)
    .limit(20)
).all()

# Format for agent
conversation_history = [
    {"role": msg.role, "content": msg.content}
    for msg in messages
]
```

## Error Handling During Streaming

**Decision**: Graceful degradation with error events.

**Strategy**:
1. Try/catch around agent execution
2. On error, yield error event instead of crashing
3. Ensure proper cleanup of resources

**Implementation**:
```python
async def generate_events():
    try:
        result = Runner.run_streamed(agent, input=messages)
        async for event in result.stream_events():
            yield format_event(event)
    except Exception as e:
        yield f"event: error\ndata: {str(e)}\n\n"
```

## Dependencies and Integration Points

| Component | Integration Method |
|-----------|-------------------|
| Existing TaskManagerAgent (015) | Extend instructions for chat-specific behavior |
| MCP Tools (014) | Call via existing MCP client pattern |
| JWT Auth | Use existing `get_current_user` dependency |
| Database | SQLModel with Thread, ChatMessage tables |

## References

- [OpenAI Agents SDK Streaming Documentation](https://github.com/openai/openai-agents-python/blob/main/docs/streaming.md)
- [Server-Sent Events Spec](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- [FastAPI StreamingResponse](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
