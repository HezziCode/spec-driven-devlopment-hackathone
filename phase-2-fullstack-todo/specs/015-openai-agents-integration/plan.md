# Implementation Plan: OpenAI Agents SDK Integration

**Branch**: `015-openai-agents-integration` | **Date**: 2025-12-30 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/015-openai-agents-integration/spec.md`

## Summary

Integrate OpenAI Agents SDK to create a TaskManagerAgent that enables natural language task management. The agent uses `@function_tool` decorators to expose task operations and calls the existing MCP server tools for all database operations. Runner.run() handles async execution with proper context passing for user isolation.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: OpenAI Agents SDK (openai-agents), httpx, FastAPI, SQLModel
**Storage**: Neon Serverless PostgreSQL (existing)
**Testing**: Pytest with pytest-asyncio
**Target Platform**: Linux server (Vercel/Railway compatible)
**Project Type**: Web application (backend extension)
**Performance Goals**: 95% of chat responses < 3 seconds
**Constraints**: Stateless server architecture, user isolation required
**Scale/Scope**: Same as existing backend (~100 concurrent users)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Development | ✅ Pass | Using agents/skills, no manual coding |
| II. Clean Code (SRP) | ✅ Pass | Agent, tools, context, service separated |
| III. Type Safety | ✅ Pass | Full type hints, Pydantic models |
| IV. Accessibility | N/A | Backend only |
| V. Performance-First | ✅ Pass | Async operations, O(n) queries |
| VI. Modular Architecture | ✅ Pass | Clear boundaries: agent → MCP → DB |
| VII. Stateless Server | ✅ Pass | All state persisted to database |

## Project Structure

### Documentation (this feature)

```text
specs/015-openai-agents-integration/
├── plan.md              # This file
├── research.md          # Phase 0 output (completed)
├── data-model.md        # Phase 1 output (completed)
├── quickstart.md        # Phase 1 output (completed)
├── contracts/
│   ├── chat-api.md      # Chat endpoint contract
│   └── agent-tools.md   # Tool function contracts
└── tasks.md             # Phase 2 output (via /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── agents/                    # NEW: OpenAI Agents SDK integration
│   ├── __init__.py            # Package exports
│   ├── agent.py               # TaskManagerAgent definition
│   ├── tools.py               # @function_tool implementations
│   ├── context.py             # AgentContext dataclass
│   └── schemas.py             # Agent-specific Pydantic models
├── routes/
│   └── chat.py                # NEW: Chat endpoint
├── services/
│   └── chat_service.py        # NEW: Chat orchestration service
├── schemas/
│   └── chat.py                # NEW: ChatRequest/ChatResponse
├── models.py                  # MODIFY: Add Conversation, Message models
├── mcp_server/                # Existing MCP server (called by agent)
│   ├── server.py
│   ├── schemas.py
│   └── tools.py
└── tests/
    ├── test_agent_tools.py    # NEW: Tool unit tests
    ├── test_chat_endpoint.py  # NEW: Chat endpoint tests
    └── test_chat_service.py   # NEW: Service integration tests
```

**Structure Decision**: Extending existing backend with new `agents/` directory. Agent tools call existing MCP server tools via internal HTTP, maintaining separation of concerns.

## Implementation Phases

### Phase 1: Setup and Dependencies (Est. tasks: 3)

1. **Add OpenAI Agents SDK dependency**
   - `uv add openai-agents httpx`
   - Verify installation

2. **Add environment variable**
   - Add `OPENAI_API_KEY` to `.env.example`
   - Document in backend/CLAUDE.md

3. **Create agents package structure**
   - Create `backend/agents/__init__.py`
   - Create empty module files

### Phase 2: Database Models (Est. tasks: 2)

1. **Add Conversation model to models.py**
   - SQLModel table definition
   - Relationship to User

2. **Add Message model to models.py**
   - SQLModel table definition
   - Relationships to User and Conversation

### Phase 3: Agent Context and Schemas (Est. tasks: 3)

1. **Create AgentContext dataclass**
   - `backend/agents/context.py`
   - user_id, conversation_id, mcp_base_url

2. **Create agent schemas**
   - `backend/agents/schemas.py`
   - ExtractedTaskDetails, TaskInfo, etc.

3. **Create chat request/response schemas**
   - `backend/schemas/chat.py`
   - ChatRequest, ChatResponse, ToolCall

### Phase 4: Agent Tools Implementation (Est. tasks: 7)

1. **Implement create_task tool**
2. **Implement list_tasks tool**
3. **Implement get_task tool**
4. **Implement mark_complete tool**
5. **Implement update_task tool**
6. **Implement delete_task tool**
7. **Implement search_tasks tool**

Each tool:
- Uses `@function_tool` decorator
- Receives `RunContextWrapper[AgentContext]`
- Calls existing MCP server via httpx
- Returns structured dict response

### Phase 5: TaskManagerAgent Definition (Est. tasks: 2)

1. **Create agent instructions**
   - `backend/agents/agent.py`
   - Define AGENT_INSTRUCTIONS constant

2. **Create TaskManagerAgent instance**
   - Configure with gpt-4o-mini
   - Register all tools

### Phase 6: Chat Service Layer (Est. tasks: 4)

1. **Create chat_service.py**
   - `backend/services/chat_service.py`

2. **Implement create_conversation function**
   - Creates new conversation in database

3. **Implement get_conversation_messages function**
   - Retrieves message history for context

4. **Implement process_message function**
   - Orchestrates agent execution
   - Stores user and assistant messages
   - Returns ChatResponse

### Phase 7: Chat Endpoint (Est. tasks: 3)

1. **Create chat router**
   - `backend/routes/chat.py`
   - POST /api/users/{user_id}/chat

2. **Implement chat endpoint**
   - JWT authentication
   - User ID validation
   - Delegates to chat_service

3. **Register router in main.py**
   - Add chat router to app

### Phase 8: Error Handling (Est. tasks: 2)

1. **Add tool error handling**
   - Custom `failure_error_function` for tools
   - User-friendly error messages

2. **Add API error handling**
   - Handle OpenAI API errors
   - Handle rate limits with retry logic

### Phase 9: Testing (Est. tasks: 5)

1. **Unit tests for agent tools**
   - Mock HTTP calls to MCP server
   - Test each tool in isolation

2. **Unit tests for chat service**
   - Mock agent execution
   - Test conversation creation/retrieval

3. **Integration tests for chat endpoint**
   - End-to-end chat flow
   - Authentication tests

4. **Test conversation context persistence**
   - Multi-turn conversations
   - Context maintained across messages

5. **Test user isolation**
   - Verify users can only access own conversations

### Phase 10: Documentation Updates (Est. tasks: 2)

1. **Update backend/CLAUDE.md**
   - Document agents/ directory
   - Document chat endpoint

2. **Update .env.example**
   - Add OPENAI_API_KEY placeholder

## Dependencies

| Dependency | Version | Status |
|------------|---------|--------|
| openai-agents | ^0.2.0 | To install |
| httpx | ^0.27.0 | To install |
| FastAPI | Existing | Available |
| SQLModel | Existing | Available |
| pytest-asyncio | Existing | Available |

## Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| OpenAI API rate limits | Medium | High | Implement exponential backoff |
| Slow AI responses | Medium | Medium | Set 30s timeout, show loading state |
| MCP server unavailable | Low | High | Health check, fallback error message |
| Context token limits | Low | Medium | Limit conversation history to last 20 messages |

## Success Criteria Alignment

| Spec Criteria | Implementation |
|---------------|----------------|
| SC-001: 90% detail extraction accuracy | Agent instructions + tool design |
| SC-002: 95% < 3 second responses | Async execution, gpt-4o-mini |
| SC-003: 95% intent identification | Clear tool descriptions, examples |
| SC-004: 100 concurrent conversations | Stateless architecture |
| SC-005: User-friendly errors | Custom error handlers |
| SC-006: Clarification for ambiguous | Agent instructions |

## Estimated Task Count

| Phase | Tasks |
|-------|-------|
| Phase 1: Setup | 3 |
| Phase 2: Database Models | 2 |
| Phase 3: Schemas | 3 |
| Phase 4: Agent Tools | 7 |
| Phase 5: Agent Definition | 2 |
| Phase 6: Chat Service | 4 |
| Phase 7: Chat Endpoint | 3 |
| Phase 8: Error Handling | 2 |
| Phase 9: Testing | 5 |
| Phase 10: Documentation | 2 |
| **Total** | **33** |

## Next Steps

1. Run `/sp.tasks` to generate detailed task list with test cases
2. Execute tasks via `/sp.implement`
3. Create PR for review
