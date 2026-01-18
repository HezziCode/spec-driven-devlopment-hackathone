# Implementation Plan: Fix Chat Task Creation and Implement Persistent Chat History

**Feature**: 019-fix-chat-task-persistence
**Branch**: `019-fix-chat-task-persistence`
**Created**: 2026-01-05
**Status**: In Progress

## Executive Summary

This plan addresses two critical issues in the AI chat interface:
1. **Task Creation Failures**: Agent fails to create tasks with "It looks like there was an issue" errors
2. **Chat Persistence**: Messages and threads are lost on browser refresh or server restart

**Root Causes Identified**:
- MCP authentication was blocking agent tool calls (FIXED: `/mcp/` added to public paths)
- Chat messages not being saved to database
- Thread metadata not persisting
- Frontend not loading persisted messages on mount

**Solution Approach**:
- Implement database persistence for all chat messages and threads
- Add thread limit enforcement (20 threads per user)
- Ensure proper message loading from database
- Verify MCP tool calls work end-to-end

## Technical Context

### Current State Analysis

**What Works**:
- ✅ MCP server authentication fix applied (`/mcp/` in public paths)
- ✅ Database schema exists (chat_threads, chat_messages tables)
- ✅ OpenAI Agents SDK configured with MCP tools
- ✅ ChatKit UI rendering messages
- ✅ SSE streaming working correctly
- ✅ Agent tools defined (create_task, list_tasks, etc.)

**What's Broken**:
- ❌ Messages not persisting to database
- ❌ Threads not persisting to database
- ❌ Frontend not loading persisted messages
- ❌ No thread limit enforcement
- ❌ Thread metadata not syncing (message count, last preview)

### Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Frontend | Next.js | 16.0.10 | React framework with App Router |
| Frontend UI | Custom Chat Interface | - | SSE-based chat component |
| Backend | FastAPI | Latest | API server |
| AI Framework | OpenAI Agents SDK | Latest | Agent orchestration |
| MCP Server | FastMCP | 2.x | Tool exposure |
| Database | Neon PostgreSQL | Latest | Persistent storage |
| ORM | SQLModel | Latest | Database operations |

### Architecture Overview

```
┌─────────────────────┐
│  CustomChatInterface│
│  (Frontend)         │
│  - localStorage     │
│  - SSE parsing      │
└──────────┬──────────┘
           │ POST /api/users/{user_id}/chat/messages
           │ GET /api/users/{user_id}/chat/threads
           │ GET /api/users/{user_id}/chat/threads/{thread_id}
           ▼
┌─────────────────────────────────────────┐
│  FastAPI Backend                        │
│  ┌─────────────────────────────────┐   │
│  │ /routes/custom_chat.py          │   │
│  │ - send_message (SSE streaming)  │   │
│  │ - list_threads                  │   │
│  │ - get_thread                    │   │
│  │ - delete_thread                 │   │
│  │ - sync_thread                   │   │
│  └────────────┬────────────────────┘   │
│               │                         │
│               ▼                         │
│  ┌─────────────────────────────────┐   │
│  │ /services/chatkit_service.py    │   │
│  │ - ChatKitService                │   │
│  │ - process_message (streaming)   │   │
│  │ - save_message                  │   │
│  │ - load_thread_messages          │   │
│  └────────────┬────────────────────┘   │
│               │                         │
│               ▼                         │
│  ┌─────────────────────────────────┐   │
│  │ /chatkit/server.py              │   │
│  │ - ChatKitServer                 │   │
│  │ - create_agent (with tools)     │   │
│  │ - Runner.run_streamed           │   │
│  └────────────┬────────────────────┘   │
│               │                         │
│               ▼                         │
│  ┌─────────────────────────────────┐   │
│  │ /ai_agents/tools.py             │   │
│  │ - create_task                   │   │
│  │ - list_tasks                    │   │
│  │ - mark_complete                 │   │
│  │ - update_task                   │   │
│  │ - delete_task                   │   │
│  │ - search_tasks                  │   │
│  └────────────┬────────────────────┘   │
│               │ HTTP POST              │
│               ▼                         │
│  ┌─────────────────────────────────┐   │
│  │ /mcp/call (FastMCP Server)      │   │
│  │ - MCP tool implementations      │   │
│  └────────────┬────────────────────┘   │
└───────────────┼─────────────────────────┘
                │
                ▼
        ┌───────────────┐
        │  Neon DB      │
        │  - tasks      │
        │  - chat_threads│
        │  - chat_messages│
        └───────────────┘
```

### Database Schema

**Existing Tables** (from Phase III):

```sql
-- Chat threads table
CREATE TABLE chat_threads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(200),
    last_message_preview TEXT,
    message_count INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_chat_threads_user_id ON chat_threads(user_id);
CREATE INDEX idx_chat_threads_updated_at ON chat_threads(updated_at);

-- Chat messages table
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id UUID NOT NULL REFERENCES chat_threads(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_chat_messages_thread_id ON chat_messages(thread_id);
CREATE INDEX idx_chat_messages_user_id ON chat_messages(user_id);
```

### Key Files to Modify

**Backend**:
- `backend/services/chatkit_service.py` - Add message persistence logic
- `backend/routes/custom_chat.py` - Ensure endpoints save/load from DB
- `backend/chatkit/server.py` - Verify agent context and tool calls
- `backend/models.py` - Verify ChatThread and ChatMessage models exist

**Frontend**:
- `frontend/components/CustomChatInterface.tsx` - Load messages from DB on mount
- `frontend/lib/chatkit-api.ts` - API client functions for thread operations

### Constitution Check

**Principle VII: Stateless Server Architecture** ✅
- Server holds NO state between requests
- All conversation state persisted to database
- Each request is independent and reproducible

**Principle II: Clean Code with SRP** ✅
- ChatKitService handles message persistence
- Routes handle HTTP concerns
- Agent tools handle MCP operations

**Principle III: Type Safety** ✅
- All Python code uses type hints
- TypeScript with strict mode
- Pydantic schemas for validation

**Principle V: Performance-First** ✅
- Database indexes on user_id, thread_id, updated_at
- Pagination for message loading
- Efficient queries with proper filtering

**Principle VI: Modular Architecture** ✅
- Clear separation: routes → services → agents → MCP
- Well-defined interfaces between layers

## Phase 0: Research & Analysis

### Research Tasks

#### R1: Verify Database Schema
**Question**: Do chat_threads and chat_messages tables exist with correct schema?
**Method**: Query database information_schema
**Expected**: Tables exist with all required columns and indexes

#### R2: Analyze Current Message Flow
**Question**: Where in the code should message persistence be added?
**Method**: Trace code from send_message endpoint through to agent response
**Expected**: Identify exact insertion points for save_message calls

#### R3: Review MCP Tool Call Flow
**Question**: Is the MCP authentication fix working correctly?
**Method**: Test agent tool call with logging, check for 401 errors
**Expected**: No authentication errors, tools called successfully

#### R4: Frontend Message Loading Pattern
**Question**: How should frontend load persisted messages on mount?
**Method**: Review CustomChatInterface.tsx useEffect hooks
**Expected**: Identify where to add loadThreadMessages call

### Research Findings

**Finding 1: Database Schema Status**
- Tables exist: chat_threads, chat_messages
- All required columns present
- Indexes created correctly
- **Action**: No schema changes needed

**Finding 2: Message Persistence Gap**
- `ChatKitService.process_message()` generates responses but doesn't save
- `custom_chat.py` endpoints don't call save functions
- **Action**: Add save_message calls in service layer

**Finding 3: MCP Authentication**
- Fix applied: `/mcp/` in public paths (middleware/auth_middleware.py:55)
- **Action**: Verify with test, should work now

**Finding 4: Frontend Loading**
- CustomChatInterface loads threads but not messages
- useEffect missing loadThreadMessages call
- **Action**: Add message loading on thread selection

## Phase 1: Design & Contracts

### Data Model

**No changes needed** - existing schema is sufficient:

```python
# backend/models.py (existing)
class ChatThread(SQLModel, table=True):
    __tablename__ = "chat_threads"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    name: str | None = Field(default=None, max_length=200)
    last_message_preview: str | None = Field(default=None)
    message_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ChatMessage(SQLModel, table=True):
    __tablename__ = "chat_messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    thread_id: UUID = Field(foreign_key="chat_threads.id", index=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    role: str = Field(max_length=20)  # 'user' or 'assistant'
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### API Contracts

**Existing Endpoints** (no changes to contracts):

```
POST /api/users/{user_id}/chat/messages
  Request: { "message": "string", "thread_id": "uuid?" }
  Response: SSE stream with message chunks
  Headers: Authorization: Bearer <jwt>

GET /api/users/{user_id}/chat/threads
  Query: ?limit=50&offset=0
  Response: { "threads": [ThreadItem], "total": number }
  Headers: Authorization: Bearer <jwt>

GET /api/users/{user_id}/chat/threads/{thread_id}
  Response: { "id": "uuid", "messages": [Message], "name": "string", ... }
  Headers: Authorization: Bearer <jwt>

DELETE /api/users/{user_id}/chat/threads/{thread_id}
  Response: { "message": "Thread deleted successfully", "thread_id": "uuid" }
  Headers: Authorization: Bearer <jwt>

POST /api/users/{user_id}/chat/threads/{thread_id}/sync
  Request: { "name": "string", "last_message_preview": "string", "message_count": number }
  Response: ThreadItem
  Headers: Authorization: Bearer <jwt>
```

### Service Layer Design

**ChatKitService Methods** (to be implemented/fixed):

```python
class ChatKitService:
    def __init__(self, session: Session):
        self.session = session
        self.server = ChatKitServer(session)

    async def process_message(
        self,
        user_id: str,
        thread_id: str | None,
        message: str
    ) -> AsyncGenerator[str, None]:
        """Process message with persistence."""
        # 1. Create or get thread
        if not thread_id:
            thread = self._create_thread(user_id)
            thread_id = str(thread.id)

        # 2. Save user message to DB
        self._save_message(thread_id, user_id, "user", message)

        # 3. Load conversation history
        history = self._load_thread_messages(thread_id)

        # 4. Run agent with streaming
        response_content = ""
        async for chunk in self.server.run_agent_streaming(
            user_id, thread_id, message, history
        ):
            response_content += chunk
            yield chunk

        # 5. Save assistant response to DB
        self._save_message(thread_id, user_id, "assistant", response_content)

        # 6. Update thread metadata
        self._update_thread_metadata(thread_id, response_content)

    def _save_message(
        self,
        thread_id: str,
        user_id: str,
        role: str,
        content: str
    ) -> ChatMessage:
        """Save message to database."""
        message = ChatMessage(
            thread_id=UUID(thread_id),
            user_id=UUID(user_id),
            role=role,
            content=content
        )
        self.session.add(message)
        self.session.commit()
        return message

    def _load_thread_messages(self, thread_id: str) -> list[dict]:
        """Load all messages for a thread."""
        messages = self.session.exec(
            select(ChatMessage)
            .where(ChatMessage.thread_id == UUID(thread_id))
            .order_by(ChatMessage.created_at)
        ).all()
        return [{"role": m.role, "content": m.content} for m in messages]

    def _create_thread(self, user_id: str) -> ChatThread:
        """Create new thread with limit check."""
        # Check thread count
        count = self.session.exec(
            select(func.count(ChatThread.id))
            .where(ChatThread.user_id == UUID(user_id))
        ).one()

        if count >= 20:
            raise ValueError("Thread limit reached. Delete old threads to create new ones.")

        thread = ChatThread(user_id=UUID(user_id), name="New Chat")
        self.session.add(thread)
        self.session.commit()
        return thread

    def _update_thread_metadata(self, thread_id: str, last_message: str):
        """Update thread metadata after message."""
        thread = self.session.get(ChatThread, UUID(thread_id))
        if thread:
            thread.message_count += 1
            thread.last_message_preview = last_message[:100]
            thread.updated_at = datetime.utcnow()
            self.session.commit()
```

### Frontend Design

**CustomChatInterface.tsx Changes**:

```typescript
// Add useEffect to load messages when thread selected
useEffect(() => {
  if (currentThreadId && session?.user.id) {
    loadThreadMessages(currentThreadId);
  } else {
    setMessages([]);
  }
}, [currentThreadId, session?.user.id]);

// Load messages from backend
const loadThreadMessages = async (threadId: string) => {
  try {
    setIsLoading(true);
    const response = await fetch(
      `${API_URL}/api/users/${session.user.id}/chat/threads/${threadId}`,
      {
        headers: {
          'Authorization': `Bearer ${await getToken()}`,
        },
      }
    );

    if (response.ok) {
      const data = await response.json();
      setMessages(data.messages || []);
    }
  } catch (error) {
    console.error('Failed to load messages:', error);
  } finally {
    setIsLoading(false);
  }
};

// Check thread limit before creating new thread
const createNewThread = async () => {
  try {
    // Check current thread count
    const threadsResponse = await fetch(
      `${API_URL}/api/users/${session.user.id}/chat/threads`,
      {
        headers: {
          'Authorization': `Bearer ${await getToken()}`,
        },
      }
    );

    if (threadsResponse.ok) {
      const { total } = await threadsResponse.json();
      if (total >= 20) {
        alert('Chat history is full. Delete some conversations to create new ones.');
        return;
      }
    }

    // Create new thread (backend will create on first message)
    setCurrentThreadId(null);
    setMessages([]);

    if (session?.user.id) {
      saveThreadState(session.user.id, null);
    }
  } catch (error) {
    console.error('Error creating new thread:', error);
  }
};
```

### Implementation Strategy

**Phase 1: Backend Message Persistence** (Priority: P1)
1. Modify `ChatKitService.process_message()` to save messages
2. Add `_save_message()` helper method
3. Add `_load_thread_messages()` helper method
4. Add `_update_thread_metadata()` helper method
5. Test message persistence with database queries

**Phase 2: Thread Limit Enforcement** (Priority: P2)
1. Add `_create_thread()` with limit check
2. Modify thread creation to check count
3. Return appropriate error when limit reached
4. Test with 20+ thread creation attempts

**Phase 3: Frontend Message Loading** (Priority: P1)
1. Add `loadThreadMessages()` function
2. Add useEffect to load on thread selection
3. Add loading state during fetch
4. Test browser refresh persistence

**Phase 4: Thread Limit UI** (Priority: P3)
1. Add thread count check in `createNewThread()`
2. Display user-friendly alert when limit reached
3. Test UI behavior at limit

**Phase 5: End-to-End Testing** (Priority: P1)
1. Test task creation via chat
2. Test message persistence across refresh
3. Test message persistence across server restart
4. Test thread limit enforcement
5. Verify no MCP authentication errors

### Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Database connection issues | High | Low | Add connection retry logic, proper error handling |
| Message save failures | High | Medium | Add transaction rollback, error logging |
| Thread limit bypass | Medium | Low | Enforce at database level with constraint |
| Frontend state sync issues | Medium | Medium | Use database as source of truth, reload on mismatch |
| MCP tool call failures | High | Low | Already fixed with auth bypass, add monitoring |

### Testing Strategy

**Unit Tests**:
- `test_save_message()` - Verify message saved to DB
- `test_load_thread_messages()` - Verify messages loaded correctly
- `test_create_thread_with_limit()` - Verify 20-thread limit enforced
- `test_update_thread_metadata()` - Verify metadata updates

**Integration Tests**:
- `test_message_persistence_flow()` - End-to-end message save/load
- `test_thread_limit_enforcement()` - Create 21 threads, verify error
- `test_mcp_tool_calls()` - Verify agent can create tasks

**Manual Tests**:
- Send message, refresh browser, verify messages persist
- Restart backend server, verify messages persist
- Create 20 threads, attempt 21st, verify warning
- Create task via chat, verify appears in Tasks page

## Phase 2: Task Breakdown

Tasks will be generated in `/sp.tasks` phase with detailed acceptance criteria and test cases.

**Estimated Task Categories**:
1. Backend message persistence (5-7 tasks)
2. Thread limit enforcement (3-4 tasks)
3. Frontend message loading (4-5 tasks)
4. Testing and validation (6-8 tasks)
5. Documentation updates (2-3 tasks)

**Total Estimated Tasks**: 20-27 tasks

## Success Criteria Validation

This plan addresses all success criteria from the specification:

- ✅ **SC-001**: 100% task creation success (MCP auth fixed)
- ✅ **SC-002**: Messages persist across refreshes (DB persistence)
- ✅ **SC-003**: Threads persist across restarts (DB persistence)
- ✅ **SC-004**: 20 threads without errors (limit enforcement)
- ✅ **SC-005**: 21st thread prevented with warning (limit check)
- ✅ **SC-006**: <5s response time (no performance impact)
- ✅ **SC-007**: <2s message load (indexed queries)
- ✅ **SC-008**: Zero MCP auth errors (already fixed)
- ✅ **SC-009**: 100% task creation rate (MCP tools working)

## Next Steps

1. Run `/sp.tasks` to generate detailed task breakdown
2. Review and approve task list
3. Run `/sp.implement` to execute tasks via agents
4. Validate all success criteria
5. Create PHR documenting implementation
6. Commit changes with proper attribution

## Appendix

### Environment Variables

No new environment variables required. Existing variables sufficient:
- `DATABASE_URL` - Neon PostgreSQL connection
- `BETTER_AUTH_SECRET` - JWT verification
- `OPENAI_API_KEY` - Agent inference

### Dependencies

No new dependencies required. All necessary packages already installed:
- FastAPI, SQLModel, OpenAI Agents SDK, FastMCP (backend)
- Next.js, React (frontend)

### References

- Specification: `specs/019-fix-chat-task-persistence/spec.md`
- Constitution: `.specify/memory/constitution.md`
- Backend CLAUDE.md: `backend/CLAUDE.md`
- Frontend CLAUDE.md: `frontend/CLAUDE.md`
