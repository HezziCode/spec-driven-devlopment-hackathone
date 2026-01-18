# Implementation Plan: Fix Chat Task Persistence

**Feature Branch**: `016-fix-chat-task-persistence`
**Created**: 2026-01-05
**Status**: In Progress
**Spec Reference**: [spec.md](./spec.md)

## Executive Summary

This plan addresses critical bugs in the chat functionality that prevent proper persistence of conversations, task creation, and thread management. The issues stem from incorrect parameter handling in the OpenAI Agent SDK integration, missing database operations, improper SSE response parsing, and lack of thread limit enforcement.

**Key Issues to Resolve**:
1. HTTP 500 errors when loading threads and deleting threads
2. Missing `content` parameter in ThreadManager.add_message() calls
3. Tasks created via chat not persisting to database
4. Chat messages not persisting across sessions
5. SSE streaming responses displaying technical artifacts
6. No enforcement of 20-thread limit per user
7. Thread deletion not removing data from database

## Technical Context

### Current Architecture

**Frontend Stack**:
- Next.js 16+ with App Router
- TypeScript with strict mode
- Custom chat interface component (CustomChatInterface.tsx)
- SSE parser for streaming responses
- Better Auth for authentication (JWT tokens)

**Backend Stack**:
- FastAPI with Python 3.11+
- OpenAI Agents SDK for AI logic
- SQLModel ORM with Neon PostgreSQL
- JWT middleware for authentication
- SSE streaming for chat responses

**Database Schema** (Existing):
```sql
-- Users table (existing)
users (id, username, email, password_hash, created_at, updated_at)

-- Tasks table (existing)
tasks (id, user_id, title, description, completed, priority, created_at, updated_at)

-- Chat threads table (needs verification/fixes)
chat_threads (id, user_id, name, created_at, updated_at)

-- Chat messages table (needs verification/fixes)
chat_messages (id, thread_id, user_id, role, content, created_at)
```

### Known Issues Analysis

#### Issue 1: HTTP 500 Errors in Thread Operations

**Root Cause**: Backend endpoints likely have:
- Missing error handling for database operations
- Incorrect query construction (missing user_id filters)
- Foreign key constraint violations
- Unhandled exceptions in thread retrieval/deletion

**Location**: `backend/routes/chatkit.py` or `backend/routes/custom_chat.py`

**Fix Strategy**:
- Add proper try-catch blocks with specific exception handling
- Ensure all queries filter by authenticated user_id
- Add database transaction management
- Return appropriate HTTP status codes (not 500 for expected errors)

#### Issue 2: ThreadManager.add_message() Missing Content Parameter

**Root Cause**: OpenAI Agents SDK ThreadManager API requires specific parameters:
```python
# INCORRECT (current)
thread_manager.add_message(role="user")  # Missing content!

# CORRECT (needed)
thread_manager.add_message(role="user", content=message_text)
```

**Location**: `backend/services/chatkit_service.py` or agent initialization code

**Fix Strategy**:
- Locate all ThreadManager.add_message() calls
- Add required `content` parameter with actual message text
- Ensure proper parameter order and types

#### Issue 3: Tasks Not Persisting from Chat

**Root Cause**: Agent tool for task creation either:
- Not calling the database properly
- Not using the correct user_id
- Returning success but not committing transaction
- Tool not properly integrated with task service

**Location**: `backend/mcp_server/tools/add_task.py` or agent tool definitions

**Fix Strategy**:
- Verify tool calls task_service.create_task()
- Ensure user_id is passed correctly from JWT context
- Add database session commit after task creation
- Add error handling and rollback on failure

#### Issue 4: Chat History Not Persisting

**Root Cause**: Messages not being saved to database:
- Missing database insert operations after message exchange
- Transaction not being committed
- Messages saved but not retrieved correctly
- User_id not being associated with messages

**Location**: Chat endpoint handler and message persistence logic

**Fix Strategy**:
- Add database insert for user messages before agent processing
- Add database insert for assistant responses after agent completes
- Ensure proper user_id and thread_id associations
- Implement message retrieval with proper ordering (by created_at)

#### Issue 5: SSE Streaming Format Issues

**Root Cause**: Frontend SSE parser not correctly handling server-sent events:
```
Current output: "data: Hidata:  theredata: !event: donedata: {...}"
Expected output: "Hi there!"
```

**Location**: `frontend/lib/sse-parser.ts` and chat interface component

**Fix Strategy**:
- Parse SSE format correctly: each line starts with "data: "
- Extract only the content field from each data chunk
- Filter out event markers and metadata
- Accumulate text chunks and display only message content

#### Issue 6: No Thread Limit Enforcement

**Root Cause**: No validation when creating new threads:
- Missing count query before thread creation
- No user feedback when limit reached
- No enforcement mechanism

**Location**: Thread creation endpoint

**Fix Strategy**:
- Add query to count user's existing threads
- Return 400 Bad Request with clear message if limit reached
- Add frontend handling to display limit message
- Suggest thread deletion in error message

#### Issue 7: Thread Deletion Not Removing Data

**Root Cause**: Database cascade delete not configured or:
- DELETE query not executing
- Transaction not committing
- Only soft-deleting (marking as deleted)
- Foreign key constraints preventing deletion

**Location**: Thread deletion endpoint and database schema

**Fix Strategy**:
- Verify CASCADE DELETE on foreign keys
- Use proper DELETE query with user_id filter
- Commit transaction after deletion
- Return 200 OK only after successful deletion

## Constitution Compliance Check

### Principle I: Spec-Driven Development ✅
- Following SDD workflow: spec → plan → tasks → implement
- Using agents and skills for implementation
- No manual code writing

### Principle II: Clean Code ✅
- Each fix targets single responsibility
- Comprehensive error handling
- Clear function names and documentation

### Principle III: Type Safety ✅
- All Python code will use type hints
- TypeScript strict mode maintained
- No 'any' types in fixes

### Principle IV: Accessibility ✅
- Chat interface maintains WCAG 2.1 AA compliance
- Error messages are screen-reader friendly
- Keyboard navigation preserved

### Principle V: Performance ✅
- Database queries optimized with indexes
- SSE streaming maintains low latency
- Thread limit prevents database bloat

### Principle VI: Modular Architecture ✅
- Frontend/backend separation maintained
- Clear API contracts
- Service layer for business logic

### Principle VII: Stateless Server Architecture ✅
- All conversation state persisted to database
- No in-memory state between requests
- Server can restart without data loss

## Phase 0: Research & Discovery

### Research Tasks

#### R1: OpenAI Agents SDK ThreadManager API
**Question**: What are the correct parameters and usage patterns for ThreadManager.add_message()?

**Research Approach**:
- Review OpenAI Agents SDK documentation
- Check example code in existing codebase
- Verify parameter requirements and types

**Expected Findings**:
```python
# Correct usage pattern
thread_manager.add_message(
    role="user",  # or "assistant"
    content="message text here",  # REQUIRED
    metadata={}  # optional
)
```

#### R2: FastAPI SSE Streaming Best Practices
**Question**: What is the correct format for server-sent events in FastAPI?

**Research Approach**:
- Review SSE specification (text/event-stream)
- Check FastAPI streaming response patterns
- Analyze current backend implementation

**Expected Findings**:
```python
# Correct SSE format
async def stream_response():
    yield f"data: {json.dumps({'content': 'Hello'})}\n\n"
    yield f"data: {json.dumps({'content': ' there'})}\n\n"
    yield f"event: done\n"
    yield f"data: {json.dumps({'thread_id': 'abc123'})}\n\n"
```

#### R3: SQLModel Cascade Delete Configuration
**Question**: How to properly configure CASCADE DELETE for thread-message relationships?

**Research Approach**:
- Review SQLModel relationship documentation
- Check current database schema
- Verify foreign key constraints in Neon DB

**Expected Findings**:
```python
# Correct relationship configuration
class ChatThread(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    messages: List["ChatMessage"] = Relationship(
        back_populates="thread",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

class ChatMessage(SQLModel, table=True):
    thread_id: UUID = Field(foreign_key="chat_threads.id", ondelete="CASCADE")
```

#### R4: Frontend SSE Parsing Patterns
**Question**: How to correctly parse SSE streams in TypeScript/React?

**Research Approach**:
- Review EventSource API and fetch streaming
- Check existing sse-parser.ts implementation
- Identify parsing logic errors

**Expected Findings**:
```typescript
// Correct SSE parsing
const lines = chunk.split('\n');
for (const line of lines) {
  if (line.startsWith('data: ')) {
    const data = JSON.parse(line.slice(6));
    if (data.content) {
      accumulatedText += data.content;
    }
  }
}
```

#### R5: Database Transaction Management in FastAPI
**Question**: How to properly manage database transactions for chat operations?

**Research Approach**:
- Review SQLModel session management
- Check current database session configuration
- Identify transaction commit patterns

**Expected Findings**:
```python
# Correct transaction pattern
async with get_session() as session:
    try:
        # Create message
        message = ChatMessage(...)
        session.add(message)
        await session.commit()
        await session.refresh(message)
        return message
    except Exception as e:
        await session.rollback()
        raise
```

### Research Output Location
All research findings will be documented in: `specs/016-fix-chat-task-persistence/research.md`

## Phase 1: Design & Contracts

### Data Model Updates

See detailed data model documentation in: `specs/016-fix-chat-task-persistence/data-model.md`

### API Contract Updates

See detailed API contracts in: `specs/016-fix-chat-task-persistence/contracts/`

### Service Layer Design

#### ChatService (backend/services/chat_service.py)
```python
class ChatService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_threads(
        self, user_id: UUID, limit: int = 50, offset: int = 0
    ) -> Tuple[List[ChatThread], int]:
        """Get all threads for user with pagination"""

    async def get_thread_with_messages(
        self, user_id: UUID, thread_id: UUID
    ) -> Tuple[ChatThread, List[ChatMessage]]:
        """Get thread and all its messages"""

    async def create_thread(
        self, user_id: UUID, name: Optional[str] = None
    ) -> ChatThread:
        """Create new thread (enforces 20-thread limit)"""

    async def delete_thread(
        self, user_id: UUID, thread_id: UUID
    ) -> bool:
        """Delete thread and all messages (cascade)"""

    async def save_message(
        self, thread_id: UUID, user_id: UUID, role: str, content: str
    ) -> ChatMessage:
        """Save message to database"""

    async def count_user_threads(self, user_id: UUID) -> int:
        """Count total threads for user"""
```

## Phase 2: Implementation Strategy

### Implementation Order (Priority-Based)

#### Priority 1: Fix Critical Errors (P1 User Stories)
1. **Fix ThreadManager.add_message() calls** - Prevents message sending
2. **Fix HTTP 500 errors in thread loading** - Prevents chat page access
3. **Fix message persistence** - Ensures chat history saves
4. **Fix task creation from chat** - Core value proposition

#### Priority 2: Fix User Experience (P2 User Stories)
5. **Fix SSE streaming format** - Clean message display
6. **Implement thread limit enforcement** - Prevent database bloat
7. **Fix thread deletion** - Enable thread management

#### Priority 3: Polish and Edge Cases (P3 User Stories)
8. **Add error handling and user feedback** - Graceful degradation
9. **Add loading states and confirmations** - Better UX
10. **Add integration tests** - Ensure reliability

### File Changes Required

#### Backend Files
```
backend/
├── routes/
│   ├── chatkit.py (or custom_chat.py)     # Fix endpoints, add error handling
│   └── chat.py                             # Verify/update if exists
├── services/
│   ├── chat_service.py                     # Add/fix message persistence
│   ├── chatkit_service.py                  # Fix ThreadManager calls
│   └── task_service.py                     # Verify task creation
├── models.py                                # Add source field to Task
├── middleware/
│   └── auth_middleware.py                  # Verify JWT extraction
└── tests/
    ├── test_chat_endpoints.py              # Add comprehensive tests
    └── test_chat_service.py                # Add service tests
```

#### Frontend Files
```
frontend/
├── components/
│   └── CustomChatInterface.tsx             # Fix SSE parsing, add error handling
├── lib/
│   ├── sse-parser.ts                       # Fix SSE parsing logic
│   └── chatkit-api.ts                      # Fix API calls
└── __tests__/
    └── CustomChatInterface.test.tsx        # Add component tests
```

### Database Migrations

#### Migration 1: Add Task Source Tracking
```sql
ALTER TABLE tasks
ADD COLUMN source VARCHAR(50) DEFAULT 'manual',
ADD COLUMN created_by_thread_id UUID REFERENCES chat_threads(id) ON DELETE SET NULL;

CREATE INDEX idx_tasks_source ON tasks(source);
```

#### Migration 2: Verify/Fix Foreign Key Cascades
```sql
-- Check existing foreign keys
SELECT
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name,
    rc.delete_rule
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
JOIN information_schema.referential_constraints AS rc
  ON tc.constraint_name = rc.constraint_name
WHERE tc.table_name = 'chat_messages';

-- If CASCADE not set, recreate constraint
ALTER TABLE chat_messages
DROP CONSTRAINT IF EXISTS chat_messages_thread_id_fkey;

ALTER TABLE chat_messages
ADD CONSTRAINT chat_messages_thread_id_fkey
FOREIGN KEY (thread_id)
REFERENCES chat_threads(id)
ON DELETE CASCADE;
```

### Testing Strategy

#### Unit Tests
- ChatService methods (CRUD operations)
- AgentService message processing
- SSE parser functions
- Thread limit validation

#### Integration Tests
- End-to-end message flow (send → persist → retrieve)
- Task creation from chat
- Thread deletion with cascade
- Thread limit enforcement

#### Test Coverage Goals
- Backend: 100% coverage for chat services
- Frontend: 90% coverage for chat components
- Integration: All user stories have E2E tests

## Risk Assessment

### High Risk Items
1. **Database schema changes** - Could break existing data
   - Mitigation: Test migrations on staging first, backup production

2. **SSE parsing changes** - Could break message display
   - Mitigation: Add comprehensive tests, gradual rollout

3. **Thread deletion cascade** - Could accidentally delete data
   - Mitigation: Add confirmation dialogs, test thoroughly

### Medium Risk Items
4. **Thread limit enforcement** - Could frustrate users
   - Mitigation: Clear error messages, suggest deletion

5. **Agent SDK parameter changes** - Could break AI responses
   - Mitigation: Test with various message types

### Low Risk Items
6. **Error message improvements** - Low impact if wrong
7. **Loading states** - Cosmetic changes

## Success Metrics

### Technical Metrics
- 0% HTTP 500 error rate for chat operations
- 100% message persistence rate
- < 200ms response time for thread loading
- 100% test coverage for critical paths

### User Experience Metrics
- Users can send messages without errors
- Chat history persists across sessions
- Tasks appear in task list within 2 seconds
- Clean message display without artifacts
- Thread limit enforced with clear feedback

## Rollout Plan

### Phase 1: Backend Fixes (Days 1-2)
1. Fix ThreadManager.add_message() calls
2. Fix HTTP 500 errors with proper error handling
3. Implement message persistence
4. Fix task creation from chat
5. Add thread limit enforcement
6. Fix thread deletion cascade

### Phase 2: Frontend Fixes (Days 3-4)
7. Fix SSE parsing for clean display
8. Add error handling and user feedback
9. Implement thread limit modal
10. Add loading states and confirmations

### Phase 3: Testing & Polish (Day 5)
11. Write comprehensive tests
12. Fix any bugs found in testing
13. Update documentation
14. Deploy to staging for validation

### Phase 4: Production Deployment (Day 6)
15. Deploy backend changes
16. Deploy frontend changes
17. Monitor error rates and user feedback
18. Hot-fix any critical issues

## Next Steps

After this plan is approved:
1. Run `/sp.tasks` to generate detailed task breakdown
2. Execute tasks using `/sp.implement`
3. Validate each fix with tests
4. Deploy incrementally with monitoring

---

**Plan Status**: Ready for task generation
**Estimated Effort**: 5-6 days
**Risk Level**: Medium (database changes, critical user flows)
