# Implementation Plan: ChatKit AI Chat Server

**Feature Branch**: `016-chatkit-server`
**Created**: 2025-12-30
**Input**: `spec.md` (Feature specification)

---

## Technical Context

### Architecture Decisions

| Component | Decision | Rationale |
|-----------|----------|-----------|
| Streaming | `Runner.run_streamed()` + SSE | Agents SDK native streaming with `stream_events()` for text deltas |
| Thread Storage | SQLModel (Thread, ChatMessage) | Stateless architecture - all state persisted to DB |
| Thread Context | Last 20 messages sent to agent | Prevent context window overflow while maintaining relevance |
| Response Format | Server-Sent Events (text/event-stream) | Standard HTTP streaming, works with any frontend |
| Agent Tools | MCP tools from 014-mcp-todo-server | Reuse existing task management tools |

### Unknowns Resolved via Research

| Unknown | Resolution |
|---------|------------|
| Streaming implementation | Use `Runner.run_streamed()` with `stream_events()` filtering for `ResponseTextDeltaEvent` |
| SSE format | `data: <text>\n\n` format with optional `event: message` prefix |
| Context passing | `AgentContext` dataclass with user_id, thread_id passed via `context` param to Runner |

### Dependencies

- **Existing (015)**: `ai_agents/` package with TaskManagerAgent, @function_tool tools
- **Existing (014)**: MCP server tools at `/mcp` endpoint for task operations
- **New**: Thread/Message database models, FastAPI streaming endpoint

---

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Development | ✅ | Using /sp.specify, /sp.plan, /sp.tasks workflow |
| II. Clean Code (SRP) | ✅ | Separate classes: ChatKitServer, ThreadManager, StreamingResponse |
| III. Type Safety | ✅ | All functions typed, no 'any' types |
| IV. Accessibility | N/A | Backend-only feature |
| V. Performance (O(n)) | ✅ | Indexed queries, limited message history |
| VI. Modular Architecture | ✅ | Clear boundaries between chat, agents, database |
| VII. Stateless Server | ✅ | All thread state persisted to database |

**Gates**: All pass ✅

---

## Phase 0: Research Findings

### Streaming Implementation (from Context7/OpenAI docs)

**Decision**: Use `Runner.run_streamed()` for streaming responses.

```python
from agents import Agent, Runner
from openai.types.responses import ResponseTextDeltaEvent

result = Runner.run_streamed(agent, input=messages)
async for event in result.stream_events():
    if event.type == "raw_response_event":
        if isinstance(event.data, ResponseTextDeltaEvent):
            yield event.data.delta
```

### SSE Format for Streaming

**Decision**: Standard SSE format with text/event-stream content-type.

```
data: Hello\n\n
data: world\n\n
event: done\n\n
```

---

## Phase 1: Design Artifacts

### 1.1 Data Model (`data-model.md`)

See `data-model.md` for entity definitions:
- **Thread**: id, user_id, created_at, updated_at, title (optional)
- **ChatMessage**: id, thread_id, role (user/assistant), content, created_at
- **ThreadMessageIndex**: For efficient retrieval of recent messages

### 1.2 API Contracts (`contracts/`)

See `/contracts/` directory for:
- `chatkit-endpoint.yaml` - POST /chatkit OpenAPI spec
- `streaming-format.md` - SSE event format documentation

### 1.3 Quickstart Guide (`quickstart.md`)

See `quickstart.md` for:
- Running the server
- Testing streaming with curl
- Example requests/responses

---

## Phase 2: Implementation Notes

### Key Classes

| Class | Responsibility |
|-------|----------------|
| `ChatKitServer` | Main orchestrator - manages threads, runs agent |
| `ThreadManager` | CRUD operations for threads and messages |
| `StreamingResponse` | SSE formatting and event generation |
| `ChatAgent` | Agent configuration with chat-specific instructions |

### File Structure

```
backend/
├── chatkit/
│   ├── __init__.py
│   ├── server.py          # ChatKitServer class
│   ├── thread_manager.py  # Thread/Message persistence
│   ├── streaming.py       # SSE response handling
│   └── agent.py           # Chat-specific agent config
├── routes/
│   └── chatkit.py         # POST /chatkit endpoint
└── models.py              # Thread, ChatMessage (additions)
```

### Integration Points

- **Auth**: JWT via existing middleware (get_current_user)
- **MCP Tools**: Call via existing MCP client from ai_agents
- **Database**: SQLModel with Thread, ChatMessage tables

---

## Success Criteria Validation

| Criterion | Implementation Approach |
|-----------|------------------------|
| SC-001: First token < 2s | Stream immediately using `run_streamed()`, no waiting for complete response |
| SC-002: 100 concurrent | Stateless design allows horizontal scaling |
| SC-003: 99% success | Error handling with graceful streaming fallback |
| SC-004: 20 message context | Query last 20 messages before sending to agent |
| SC-005: SSE formatting | `StreamingResponse` class with proper event formatting |

---

## Next Steps

1. Run `.specify/scripts/bash/update-agent-context.sh claude` (if needed)
2. Generate tasks: `/sp.tasks` for implementation breakdown
3. Execute: `/sp.implement` for code generation
