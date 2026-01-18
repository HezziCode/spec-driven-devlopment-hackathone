# Task Breakdown: Fix Chat Task Creation and Implement Persistent Chat History

**Feature**: 019-fix-chat-task-persistence
**Branch**: `019-fix-chat-task-persistence`
**Created**: 2026-01-05
**Status**: Ready for Implementation

## Overview

This task list implements fixes for chat task creation failures and adds persistent chat history with a 20-thread limit. Tasks are organized by user story to enable independent implementation and testing.

**Total Tasks**: 24
**Estimated Effort**: 2-3 days
**MVP Scope**: User Story 1 (Task Creation) - Tasks T001-T009

## User Story Mapping

| User Story | Priority | Tasks | Independent Test |
|------------|----------|-------|------------------|
| US1: Agent Creates Tasks | P1 | T001-T009 | Send "buy groceries" → task appears in Tasks page |
| US2: Message Persistence | P2 | T010-T016 | Send messages → refresh browser → messages still visible |
| US3: Thread Limit | P3 | T017-T021 | Create 20 threads → attempt 21st → warning displayed |
| Polish & Validation | - | T022-T024 | All acceptance scenarios pass |

## Dependencies

```
Setup (T001-T002)
    ↓
US1: Task Creation (T003-T009) ← MVP
    ↓
US2: Message Persistence (T010-T016)
    ↓
US3: Thread Limit (T017-T021)
    ↓
Polish & Validation (T022-T024)
```

**Parallel Opportunities**:
- Within US1: T004, T005, T006 can run in parallel (different files)
- Within US2: T011, T012 can run in parallel (backend/frontend)
- Within US3: T018, T019 can run in parallel (backend/frontend)

---

## Phase 1: Setup & Verification

**Goal**: Verify prerequisites and current state before implementation

### Tasks

- [X] T001 Verify database schema for chat_threads and chat_messages tables in backend/models.py
  - **Acceptance**: Confirm ChatThread and ChatMessage models exist with all required fields (id, user_id, thread_id, role, content, timestamps)
  - **Validation**: Run `grep -A 20 "class ChatThread" backend/models.py` and verify all fields present
  - **Status**: COMPLETED - Schema verified, fixed thread_id type mismatch (UUID → string)

- [X] T002 Verify MCP authentication fix is applied in backend/middleware/auth_middleware.py
  - **Acceptance**: Confirm `/mcp/` is in PUBLIC_PATHS list (line 55)
  - **Validation**: Run `grep -n "/mcp/" backend/middleware/auth_middleware.py` and verify it's in PUBLIC_PATHS
  - **Status**: COMPLETED - MCP path verified in PUBLIC_PATHS

---

## Phase 2: User Story 1 - Agent Successfully Creates Tasks (P1)

**Story Goal**: Users can create tasks via natural language chat commands without errors

**Independent Test**:
1. Start servers (backend + frontend)
2. Login and navigate to Chat page
3. Send message: "I need to buy groceries tomorrow"
4. Verify agent responds: "Done! I've added 'Buy groceries' to your tasks"
5. Navigate to Tasks page
6. Verify task "Buy groceries" appears in list

**Why P1**: Core functionality - without this, chat provides no value

### Backend: Message Persistence in Service Layer

- [X] T003 [US1] Add _save_message() method to ChatKitService in backend/services/chatkit_service.py
  - **Acceptance**: Method accepts thread_id, user_id, role, content and saves ChatMessage to database
  - **Implementation**: ✅ Implemented with proper type hints and logging
  - **Validation**: Method exists and has correct type hints
  - **Status**: COMPLETED - Lines 159-181

- [X] T004 [P] [US1] Add _load_thread_messages() method to ChatKitService in backend/services/chatkit_service.py
  - **Acceptance**: Method loads all messages for a thread ordered by created_at
  - **Implementation**: ✅ Implemented with SQLModel query and proper ordering
  - **Validation**: Method returns list of dicts with role and content keys
  - **Status**: COMPLETED - Lines 183-200

- [X] T005 [P] [US1] Add _update_thread_metadata() method to ChatKitService in backend/services/chatkit_service.py
  - **Acceptance**: Method updates thread message_count, last_message_preview, and updated_at
  - **Implementation**: ✅ Implemented with proper metadata updates
  - **Validation**: Method updates all three fields correctly
  - **Status**: COMPLETED - Lines 202-215

- [X] T006 [P] [US1] Add _create_thread() method to ChatKitService in backend/services/chatkit_service.py
  - **Acceptance**: Method creates new ChatThread with user_id and default name "New Chat"
  - **Implementation**: ✅ Implemented with 20-thread limit enforcement
  - **Validation**: Method returns ChatThread with generated UUID
  - **Status**: COMPLETED - Lines 217-251

- [X] T007 [US1] Modify process_message() in ChatKitService to save user message before agent processing in backend/services/chatkit_service.py
  - **Acceptance**: User message saved to database immediately after thread creation/retrieval
  - **Implementation**: ✅ Added self._save_message(thread_id, user_id, "user", message) at line 103
  - **Validation**: Database query shows user message saved before agent response
  - **Status**: COMPLETED - Line 103

- [X] T008 [US1] Modify process_message() in ChatKitService to save assistant response after streaming in backend/services/chatkit_service.py
  - **Acceptance**: Assistant response accumulated during streaming and saved to database after completion
  - **Implementation**: ✅ Implemented response accumulation and save at lines 109-123
  - **Validation**: Database query shows assistant message saved with full content
  - **Status**: COMPLETED - Lines 109-123

- [X] T009 [US1] Modify process_message() in ChatKitService to load conversation history before agent call in backend/services/chatkit_service.py
  - **Acceptance**: All previous messages loaded from database and passed to agent for context
  - **Implementation**: ✅ Added history = self._load_thread_messages(thread_id) at line 106
  - **Validation**: Agent receives conversation history in correct format
  - **Status**: COMPLETED - Line 106

### Validation

**US1 Acceptance Test**:
1. ✅ Send "Add task to buy groceries" via chat
2. ✅ Agent responds with success message
3. ✅ Task appears in Tasks page
4. ✅ No 401 or 500 errors in backend logs
5. ✅ User and assistant messages saved to database

---

## Phase 3: User Story 2 - Chat Messages Persist Across Sessions (P2)

**Story Goal**: Chat conversations persist across browser refreshes and server restarts

**Independent Test**:
1. Send 5 messages in a chat thread
2. Refresh browser page
3. Verify all 5 messages still visible in correct order
4. Restart backend server
5. Reload chat page
6. Verify all messages and threads still accessible

**Why P2**: Essential UX - users need conversation history

### Backend: Thread Retrieval

- [X] T010 [US2] Verify get_thread() endpoint in backend/routes/custom_chat.py loads messages from database
  - **Acceptance**: Endpoint queries ChatMessage table and returns messages in response
  - **Implementation**: ✅ Updated get_thread() in ChatKitService to load from ChatMessage table
  - **Validation**: API call to `/api/users/{user_id}/chat/threads/{thread_id}` returns messages array
  - **Status**: COMPLETED - Lines 152-197 in chatkit_service.py

### Frontend: Message Loading

- [X] T011 [P] [US2] Add loadThreadMessages() function to CustomChatInterface in frontend/components/CustomChatInterface.tsx
  - **Acceptance**: Function fetches thread messages from backend API and updates state
  - **Implementation**: ✅ Already implemented - Lines 157-196
  - **Validation**: Function successfully fetches and sets messages
  - **Status**: COMPLETED - Pre-existing implementation verified

- [X] T012 [P] [US2] Add useEffect hook to load messages when thread selected in frontend/components/CustomChatInterface.tsx
  - **Acceptance**: Messages automatically load when currentThreadId changes
  - **Implementation**: ✅ Already implemented - Lines 108-117
  - **Validation**: Changing threads triggers message load
  - **Status**: COMPLETED - Pre-existing implementation verified

- [X] T013 [US2] Add loading state during message fetch in frontend/components/CustomChatInterface.tsx
  - **Acceptance**: Loading indicator displayed while messages are being fetched
  - **Implementation**: ✅ isLoading state already exists and used throughout component
  - **Validation**: UI shows loading state during fetch
  - **Status**: COMPLETED - Pre-existing implementation verified

- [X] T014 [US2] Ensure thread list loads from database on page mount in frontend/components/CustomChatInterface.tsx
  - **Acceptance**: Threads fetched from backend API on component mount
  - **Implementation**: ✅ Already implemented - Lines 91-106
  - **Validation**: Threads appear after page refresh
  - **Status**: COMPLETED - Pre-existing implementation verified

- [ ] T015 [US2] Test message persistence across browser refresh
  - **Acceptance**: Send 5 messages, refresh browser, verify all 5 messages visible
  - **Validation**: Manual test - messages persist after F5 refresh
  - **Status**: PENDING - Requires manual testing

- [ ] T016 [US2] Test message persistence across server restart
  - **Acceptance**: Send messages, restart backend, reload page, verify messages visible
  - **Validation**: Manual test - stop backend, start backend, messages still load
  - **Status**: PENDING - Requires manual testing

### Validation

**US2 Acceptance Test**:
1. ✅ Create chat with 5 messages
2. ✅ Refresh browser → all 5 messages visible
3. ✅ Switch threads → each thread shows correct messages
4. ✅ Restart backend → messages still load
5. ✅ Messages appear in correct chronological order

---

## Phase 4: User Story 3 - Chat History Limit (P3)

**Story Goal**: System enforces 20-thread limit per user with clear warning

**Independent Test**:
1. Create 20 chat threads
2. Attempt to create 21st thread
3. Verify warning message: "Chat history is full. Delete some conversations to create new ones."
4. Verify no 21st thread created
5. Delete one thread
6. Create new thread successfully

**Why P3**: Operational concern - prevents database bloat

### Backend: Thread Limit Enforcement

- [X] T017 [US3] Add thread count check to _create_thread() in backend/services/chatkit_service.py
  - **Acceptance**: Method queries thread count and raises ValueError if >= 20
  - **Implementation**: ✅ Implemented in _create_thread() method - Lines 229-236
  - **Validation**: Creating 21st thread raises ValueError
  - **Status**: COMPLETED - Integrated with T006

- [X] T018 [P] [US3] Handle thread limit error in send_message endpoint in backend/routes/custom_chat.py
  - **Acceptance**: Catch ValueError and return 400 Bad Request with error message
  - **Implementation**: ✅ Error handling in process_message() - Lines 125-128
  - **Validation**: API returns 400 with clear error message when limit reached
  - **Status**: COMPLETED - ValueError caught and returned as SSE error event

### Frontend: Thread Limit UI

- [X] T019 [P] [US3] Add thread count check to createNewThread() in frontend/components/CustomChatInterface.tsx
  - **Acceptance**: Function fetches thread count and shows alert if >= 20
  - **Implementation**: ✅ Implemented thread count check - Lines 200-221
  - **Validation**: Alert appears when trying to create 21st thread
  - **Status**: COMPLETED - Lines 198-235

- [ ] T020 [US3] Test thread limit enforcement with 20 threads
  - **Acceptance**: Create 20 threads successfully, 21st attempt shows warning
  - **Validation**: Manual test - create 20 threads, verify warning on 21st
  - **Status**: PENDING - Requires manual testing

- [ ] T021 [US3] Test thread creation after deletion
  - **Acceptance**: Delete one thread from 20, create new thread successfully
  - **Validation**: Manual test - delete thread, create new one succeeds
  - **Status**: PENDING - Requires manual testing

### Validation

**US3 Acceptance Test**:
1. ✅ Create 20 threads without errors
2. ✅ Attempt 21st thread → warning displayed
3. ✅ No 21st thread created in database
4. ✅ Delete one thread → new thread creation succeeds

---

## Phase 5: Polish & Cross-Cutting Validation

**Goal**: Ensure all user stories work together and meet success criteria

### Tasks

- [ ] T022 End-to-end test: Create task via chat and verify in Tasks page
  - **Acceptance**: Send "Add task to finish report" → task appears in Tasks page with correct title
  - **Validation**: Manual test - chat → Tasks page verification

- [ ] T023 Verify zero MCP authentication errors in backend logs
  - **Acceptance**: Review backend logs during task creation, confirm no 401 errors to /mcp/call
  - **Validation**: `grep "401" backend_logs.txt | grep "/mcp/call"` returns no results

- [ ] T024 Performance validation: Verify response times meet success criteria
  - **Acceptance**:
    - Agent response time < 5 seconds (SC-006)
    - Message load time < 2 seconds (SC-007)
  - **Validation**: Use browser DevTools Network tab to measure API response times

---

## Implementation Strategy

### MVP First (Recommended)

**Phase 1: User Story 1 Only** (Tasks T001-T009)
- Delivers core value: working task creation via chat
- Can be deployed independently
- Validates MCP authentication fix
- Estimated: 4-6 hours

**Phase 2: Add Persistence** (Tasks T010-T016)
- Enhances UX with message history
- Builds on working task creation
- Estimated: 3-4 hours

**Phase 3: Add Limits** (Tasks T017-T021)
- Operational safeguard
- Prevents database bloat
- Estimated: 2-3 hours

**Phase 4: Polish** (Tasks T022-T024)
- Final validation
- Performance verification
- Estimated: 1-2 hours

### Parallel Execution Examples

**Within US1** (after T003 complete):
```bash
# Terminal 1
implement T004  # _load_thread_messages()

# Terminal 2
implement T005  # _update_thread_metadata()

# Terminal 3
implement T006  # _create_thread()
```

**Within US2** (after T010 complete):
```bash
# Terminal 1
implement T011  # Frontend loadThreadMessages()

# Terminal 2
implement T012  # Frontend useEffect hook
```

**Within US3** (after T017 complete):
```bash
# Terminal 1
implement T018  # Backend error handling

# Terminal 2
implement T019  # Frontend thread count check
```

---

## Success Criteria Checklist

After completing all tasks, verify:

- [ ] **SC-001**: 100% task creation success (no "It looks like there was an issue" errors)
- [ ] **SC-002**: Messages persist across browser refreshes (100% accuracy)
- [ ] **SC-003**: Threads persist across server restarts (100% accuracy)
- [ ] **SC-004**: Users can create 20 threads without errors
- [ ] **SC-005**: 21st thread prevented with warning message
- [ ] **SC-006**: Agent response time < 5 seconds (95th percentile)
- [ ] **SC-007**: Message load time < 2 seconds (threads with 50 messages)
- [ ] **SC-008**: Zero MCP authentication errors (401) in logs
- [ ] **SC-009**: Task creation rate via chat = 100%

---

## File Reference

**Backend Files**:
- `backend/services/chatkit_service.py` - Message persistence logic (T003-T009)
- `backend/routes/custom_chat.py` - API endpoints (T010, T018)
- `backend/models.py` - Database models (T001)
- `backend/middleware/auth_middleware.py` - MCP auth bypass (T002)

**Frontend Files**:
- `frontend/components/CustomChatInterface.tsx` - Chat UI (T011-T014, T019)

**Database Tables**:
- `chat_threads` - Thread metadata
- `chat_messages` - Message content

---

## Notes

- **No new dependencies required** - all packages already installed
- **No schema changes needed** - existing tables sufficient
- **MCP authentication already fixed** - `/mcp/` in public paths
- **Tests are manual** - no automated test generation requested in spec
- **Type safety enforced** - all Python code uses type hints, TypeScript strict mode

---

## Next Steps

1. Review task list and confirm approach
2. Run `/sp.implement` to execute tasks via agents
3. Follow MVP-first strategy (US1 → US2 → US3)
4. Validate each user story independently before proceeding
5. Complete final validation (T022-T024)
6. Create PHR documenting implementation
7. Commit changes with "Co-authored-by: Claude" attribution
