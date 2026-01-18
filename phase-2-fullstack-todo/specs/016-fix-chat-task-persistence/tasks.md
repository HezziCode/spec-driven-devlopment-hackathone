# Implementation Tasks: Fix Chat Task Persistence

**Feature**: 016-fix-chat-task-persistence
**Branch**: `016-fix-chat-task-persistence`
**Created**: 2026-01-05
**Status**: Ready for Implementation

## Task Format

Each task follows this format:
```
- [ ] [TaskID] [P?] [Story?] Description with file path
```

Where:
- `TaskID`: Unique identifier (T001, T002, etc.)
- `P?`: Parallelization marker (P1, P2, etc.) - tasks with same marker can run in parallel
- `Story?`: User story reference (S1, S2, etc.) - optional for foundational tasks
- Description: Clear, actionable task description
- File path: Specific file(s) to modify

## Phase 1: Setup and Prerequisites

**Goal**: Prepare environment and verify current state before implementation.

**Tasks**:
- [ ] [T001] [P1] Verify database schema for chat_threads and chat_messages tables - `backend/models.py`
- [ ] [T002] [P1] Verify foreign key constraints and cascade delete configuration - Database inspection
- [ ] [T003] [P1] Review current ThreadManager usage in chatkit service - `backend/services/chatkit_service.py`
- [ ] [T004] [P1] Review current SSE streaming implementation - `backend/routes/chatkit.py` or `backend/routes/custom_chat.py`
- [ ] [T005] [P1] Review frontend SSE parser implementation - `frontend/lib/sse-parser.ts`
- [ ] [T006] [P2] Create backup of current database state - Database backup
- [ ] [T007] [P2] Document current error patterns from logs - Documentation

**Completion Criteria**:
- All current implementations documented
- Database schema verified
- Backup created
- Ready to proceed with fixes

---

## Phase 2: Foundational Changes

**Goal**: Implement database schema updates and base service layer improvements that all user stories depend on.

### Database Migrations

- [ ] [T008] [P1] Add source and created_by_thread_id columns to tasks table - `backend/models.py`
- [ ] [T009] [P1] Create migration script for task source tracking - `backend/migrations/add_task_source.sql`
- [ ] [T010] [P2] Verify and fix chat_messages foreign key cascade delete - `backend/migrations/fix_cascade_delete.sql`
- [ ] [T011] [P2] Add indexes for performance (tasks.source, chat_messages.created_at) - Migration script
- [ ] [T012] [P3] Run migrations on development database - Database execution
- [ ] [T013] [P3] Verify migration success with test queries - Database verification

### Base Models and Services

- [ ] [T014] [P1] Update Task model with source and created_by_thread_id fields - `backend/models.py`
- [ ] [T015] [P1] Add validators for Task.source field (manual/chat) - `backend/models.py`
- [ ] [T016] [P1] Update ChatThread model with cascade delete relationships - `backend/models.py`
- [ ] [T017] [P1] Update ChatMessage model with proper foreign key constraints - `backend/models.py`
- [ ] [T018] [P2] Create ChatService base class with session management - `backend/services/chat_service.py`
- [ ] [T019] [P2] Implement ChatService.save_message() with transaction handling - `backend/services/chat_service.py`
- [ ] [T020] [P2] Implement ChatService.count_user_threads() for limit enforcement - `backend/services/chat_service.py`

**Completion Criteria**:
- Database schema updated with all required fields
- All migrations executed successfully
- Base models updated with proper relationships
- ChatService foundation ready for user story implementations

---

## Phase 3: User Story 1 - Chat Message Persistence (P1)

**Goal**: Ensure all chat messages persist to database and load correctly across sessions.

**Independent Test**: Send messages in a chat session, log out, log back in, verify all messages are visible.

### Tests (if TDD approach)

- [ ] [T021] [S1] Write test for saving user message to database - `backend/tests/test_chat_service.py`
- [ ] [T022] [S1] Write test for saving assistant message to database - `backend/tests/test_chat_service.py`
- [ ] [T023] [S1] Write test for loading thread with messages - `backend/tests/test_chat_service.py`
- [ ] [T024] [S1] Write test for message persistence across sessions - `backend/tests/test_chat_endpoints.py`

### Backend Implementation

- [ ] [T025] [P1] [S1] Fix ThreadManager.add_message() calls to include content parameter - `backend/services/chatkit_service.py`
- [ ] [T026] [P1] [S1] Add message persistence after user message received - `backend/routes/chatkit.py` or `backend/routes/custom_chat.py`
- [ ] [T027] [P1] [S1] Add message persistence after assistant response complete - `backend/routes/chatkit.py` or `backend/routes/custom_chat.py`
- [ ] [T028] [P2] [S1] Implement ChatService.get_thread_with_messages() - `backend/services/chat_service.py`
- [ ] [T029] [P2] [S1] Implement ChatService.get_user_threads() with pagination - `backend/services/chat_service.py`
- [ ] [T030] [P3] [S1] Fix GET /api/users/{user_id}/chat/threads endpoint error handling - `backend/routes/chatkit.py`
- [ ] [T031] [P3] [S1] Fix GET /api/users/{user_id}/chat/threads/{thread_id} endpoint - `backend/routes/chatkit.py`
- [ ] [T032] [P3] [S1] Add proper error handling for database operations (try-catch-rollback) - `backend/services/chat_service.py`
- [ ] [T033] [P3] [S1] Add user_id validation in all chat endpoints - `backend/routes/chatkit.py`

### Frontend Implementation

- [ ] [T034] [P1] [S1] Update chat interface to load thread history on mount - `frontend/components/CustomChatInterface.tsx`
- [ ] [T035] [P1] [S1] Add error handling for thread loading failures - `frontend/components/CustomChatInterface.tsx`
- [ ] [T036] [P2] [S1] Update API client to fetch thread messages - `frontend/lib/chatkit-api.ts`
- [ ] [T037] [P2] [S1] Display loading state while fetching thread history - `frontend/components/CustomChatInterface.tsx`

### Integration Testing

- [ ] [T038] [S1] Test end-to-end message persistence flow - Integration test
- [ ] [T039] [S1] Test message loading after page refresh - Integration test
- [ ] [T040] [S1] Test message loading after logout/login - Integration test
- [ ] [T041] [S1] Verify no HTTP 500 errors in thread loading - Integration test

**Completion Criteria**:
- All chat messages persist to database immediately
- Thread history loads without errors
- Messages visible across sessions
- SC-001, SC-002, SC-007, SC-008 satisfied

---

## Phase 4: User Story 2 - Task Creation from Chat (P1)

**Goal**: Ensure tasks mentioned in chat appear in task list immediately.

**Independent Test**: Tell chatbot "I need to buy groceries tomorrow", verify task appears in tasks page.

### Tests (if TDD approach)

- [ ] [T042] [S2] Write test for task creation via chat - `backend/tests/test_chat_service.py`
- [ ] [T043] [S2] Write test for task source tracking (chat vs manual) - `backend/tests/test_task_service.py`
- [ ] [T044] [S2] Write test for task-thread association - `backend/tests/test_chat_service.py`

### Backend Implementation

- [ ] [T045] [P1] [S2] Verify agent tool for task creation calls task_service correctly - `backend/mcp_server/tools/add_task.py` or agent tool definitions
- [ ] [T046] [P1] [S2] Update task creation tool to set source='chat' - Agent tool implementation
- [ ] [T047] [P1] [S2] Update task creation tool to set created_by_thread_id - Agent tool implementation
- [ ] [T048] [P2] [S2] Add database session commit after task creation in tool - Agent tool implementation
- [ ] [T049] [P2] [S2] Add error handling and rollback for task creation failures - Agent tool implementation
- [ ] [T050] [P2] [S2] Ensure user_id is correctly passed from JWT context to tool - `backend/middleware/auth_middleware.py`
- [ ] [T051] [P3] [S2] Update TaskService.create_task() to accept source and thread_id - `backend/services/task_service.py`
- [ ] [T052] [P3] [S2] Add validation for source field in task creation - `backend/services/task_service.py`

### Frontend Implementation

- [ ] [T053] [P1] [S2] Verify task list refreshes after chat task creation - `frontend/app/tasks/page.tsx`
- [ ] [T054] [P1] [S2] Add real-time task list update mechanism (polling or websocket) - `frontend/app/tasks/page.tsx`

### Integration Testing

- [ ] [T055] [S2] Test task creation through chat conversation - Integration test
- [ ] [T056] [S2] Test task appears in task list within 2 seconds - Integration test
- [ ] [T057] [S2] Test task persists after page refresh - Integration test
- [ ] [T058] [S2] Test multiple tasks created in same conversation - Integration test

**Completion Criteria**:
- Tasks created via chat appear in task list
- Task source tracked correctly (chat vs manual)
- Task-thread association maintained
- SC-003 satisfied

---

## Phase 5: User Story 3 - Clean Chat Response Format (P2)

**Goal**: Display chat responses as clean text without technical artifacts.

**Independent Test**: Send any message, verify response displays without "data:" prefixes or thread IDs.

### Tests (if TDD approach)

- [ ] [T059] [S3] Write test for SSE format generation - `backend/tests/test_chat_endpoints.py`
- [ ] [T060] [S3] Write test for SSE parser extracting clean content - `frontend/__tests__/sse-parser.test.ts`

### Backend Implementation

- [ ] [T061] [P1] [S3] Fix SSE response format to use proper `data: {json}\n\n` structure - `backend/routes/chatkit.py` or `backend/routes/custom_chat.py`
- [ ] [T062] [P1] [S3] Ensure each content chunk is JSON-encoded with content field - SSE streaming function
- [ ] [T063] [P1] [S3] Add event markers for done/error events - SSE streaming function
- [ ] [T064] [P2] [S3] Separate metadata (thread_id, message_id) into done event - SSE streaming function
- [ ] [T065] [P2] [S3] Add proper SSE headers (Cache-Control, Connection, X-Accel-Buffering) - Endpoint response

### Frontend Implementation

- [ ] [T066] [P1] [S3] Rewrite SSE parser to handle proper SSE format - `frontend/lib/sse-parser.ts`
- [ ] [T067] [P1] [S3] Implement buffer management for incomplete chunks - `frontend/lib/sse-parser.ts`
- [ ] [T068] [P1] [S3] Extract only content field from data chunks - `frontend/lib/sse-parser.ts`
- [ ] [T069] [P2] [S3] Filter out event markers and metadata from display - `frontend/components/CustomChatInterface.tsx`
- [ ] [T070] [P2] [S3] Handle done event to capture thread_id and message_id - `frontend/components/CustomChatInterface.tsx`
- [ ] [T071] [P2] [S3] Add error handling for malformed SSE data - `frontend/lib/sse-parser.ts`

### Integration Testing

- [ ] [T072] [S3] Test clean message display without artifacts - Integration test
- [ ] [T073] [S3] Test SSE parsing with various message lengths - Integration test
- [ ] [T074] [S3] Test SSE parsing with network delays/chunking - Integration test

**Completion Criteria**:
- Chat responses display as clean, readable text
- No technical artifacts visible to users
- SSE parsing handles all edge cases
- SC-004 satisfied

---

## Phase 6: User Story 4 - Thread Management with Limits (P2)

**Goal**: Enforce 20-thread limit with clear user notifications.

**Independent Test**: Create 20 threads, attempt 21st, verify clear notification to delete old threads.

### Tests (if TDD approach)

- [ ] [T075] [S4] Write test for thread count query - `backend/tests/test_chat_service.py`
- [ ] [T076] [S4] Write test for thread limit enforcement - `backend/tests/test_chat_endpoints.py`
- [ ] [T077] [S4] Write test for thread limit notification - `frontend/__tests__/CustomChatInterface.test.tsx`

### Backend Implementation

- [ ] [T078] [P1] [S4] Implement thread count check before creating new thread - `backend/services/chat_service.py`
- [ ] [T079] [P1] [S4] Return 400 Bad Request with clear message when limit reached - `backend/routes/chatkit.py`
- [ ] [T080] [P2] [S4] Update ChatService.create_thread() to enforce limit - `backend/services/chat_service.py`
- [ ] [T081] [P2] [S4] Add error code THREAD_LIMIT_REACHED to error responses - Error handling

### Frontend Implementation

- [ ] [T082] [P1] [S4] Add error handling for thread limit response - `frontend/components/CustomChatInterface.tsx`
- [ ] [T083] [P1] [S4] Display modal/notification when thread limit reached - `frontend/components/CustomChatInterface.tsx`
- [ ] [T084] [P2] [S4] Add "Delete old threads" button/link in limit notification - `frontend/components/CustomChatInterface.tsx`
- [ ] [T085] [P2] [S4] Update thread creation flow to check for limit errors - `frontend/lib/chatkit-api.ts`

### Integration Testing

- [ ] [T086] [S4] Test thread creation succeeds when under limit - Integration test
- [ ] [T087] [S4] Test thread creation blocked at 20 threads - Integration test
- [ ] [T088] [S4] Test clear notification displayed to user - Integration test
- [ ] [T089] [S4] Test thread creation succeeds after deletion - Integration test

**Completion Criteria**:
- 20-thread limit enforced at application level
- Clear user notification when limit reached
- Users can delete threads to make room
- SC-006 satisfied

---

## Phase 7: User Story 5 - Thread Deletion (P3)

**Goal**: Enable users to delete threads with proper cascade deletion.

**Independent Test**: Create thread, delete it, verify it's removed from list and database.

### Tests (if TDD approach)

- [ ] [T090] [S5] Write test for thread deletion - `backend/tests/test_chat_service.py`
- [ ] [T091] [S5] Write test for cascade message deletion - `backend/tests/test_chat_service.py`
- [ ] [T092] [S5] Write test for deletion error handling - `backend/tests/test_chat_endpoints.py`

### Backend Implementation

- [ ] [T093] [P1] [S5] Implement ChatService.delete_thread() with user_id validation - `backend/services/chat_service.py`
- [ ] [T094] [P1] [S5] Add transaction management for thread deletion - `backend/services/chat_service.py`
- [ ] [T095] [P1] [S5] Verify cascade delete removes all messages automatically - Database verification
- [ ] [T096] [P2] [S5] Fix DELETE /api/users/{user_id}/chat/threads/{thread_id} endpoint - `backend/routes/chatkit.py`
- [ ] [T097] [P2] [S5] Add proper error handling (404 if not found, 403 if wrong user) - `backend/routes/chatkit.py`
- [ ] [T098] [P2] [S5] Return success response with deletion confirmation - `backend/routes/chatkit.py`

### Frontend Implementation

- [ ] [T099] [P1] [S5] Add delete button to thread list items - `frontend/components/CustomChatInterface.tsx`
- [ ] [T100] [P1] [S5] Add confirmation dialog before deletion - `frontend/components/CustomChatInterface.tsx`
- [ ] [T101] [P2] [S5] Implement thread deletion API call - `frontend/lib/chatkit-api.ts`
- [ ] [T102] [P2] [S5] Update thread list after successful deletion - `frontend/components/CustomChatInterface.tsx`
- [ ] [T103] [P2] [S5] Add error handling for deletion failures - `frontend/components/CustomChatInterface.tsx`

### Integration Testing

- [ ] [T104] [S5] Test thread deletion removes thread from list - Integration test
- [ ] [T105] [S5] Test cascade deletion removes all messages - Integration test
- [ ] [T106] [S5] Test no HTTP 500 errors during deletion - Integration test
- [ ] [T107] [S5] Test deleted thread doesn't reappear after refresh - Integration test

**Completion Criteria**:
- Users can delete threads successfully
- Cascade deletion removes all associated messages
- No HTTP 500 errors during deletion
- SC-005 satisfied

---

## Phase 8: Polish and Final Integration

**Goal**: Ensure all components work together seamlessly with proper error handling.

### Error Handling and UX

- [ ] [T108] [P1] Add loading states for all async operations - `frontend/components/CustomChatInterface.tsx`
- [ ] [T109] [P1] Add user-friendly error messages for all failure scenarios - Frontend components
- [ ] [T110] [P1] Add retry mechanisms for transient failures - Frontend API client
- [ ] [T111] [P2] Add logging for all database operations - Backend services
- [ ] [T112] [P2] Add monitoring for error rates - Backend middleware

### Documentation

- [ ] [T113] [P1] Update API documentation with new endpoints and error codes - `specs/016-fix-chat-task-persistence/contracts/chat-api.md`
- [ ] [T114] [P1] Document database schema changes - `specs/016-fix-chat-task-persistence/data-model.md`
- [ ] [T115] [P2] Create deployment guide for migrations - Documentation
- [ ] [T116] [P2] Update README with chat feature documentation - `README.md`

### Final Testing

- [ ] [T117] Run full test suite (backend) - `pytest backend/tests/`
- [ ] [T118] Run full test suite (frontend) - `npm test`
- [ ] [T119] Verify all success criteria met (SC-001 through SC-008) - Manual verification
- [ ] [T120] Perform end-to-end user acceptance testing - Manual testing
- [ ] [T121] Test with production-like data volumes - Performance testing
- [ ] [T122] Verify no regressions in existing functionality - Regression testing

**Completion Criteria**:
- All tests passing
- All success criteria met
- Documentation complete
- Ready for deployment

---

## Dependency Graph

```
Phase 1 (Setup) → Phase 2 (Foundational)
                      ↓
        ┌─────────────┼─────────────┬─────────────┐
        ↓             ↓             ↓             ↓
    Phase 3 (S1)  Phase 4 (S2)  Phase 5 (S3)  Phase 6 (S4)
        ↓             ↓             ↓             ↓
        └─────────────┴─────────────┴─────────────┘
                      ↓
                  Phase 7 (S5)
                      ↓
                  Phase 8 (Polish)
```

**Critical Path**: Phase 1 → Phase 2 → Phase 3 (S1) → Phase 4 (S2) → Phase 8

**Parallel Execution Opportunities**:
- After Phase 2 completes, Phases 3-6 can be implemented in parallel by different developers
- Within each phase, tasks marked with same P? number can run in parallel
- Example: T025 (P1) and T026 (P1) in Phase 3 can run simultaneously

---

## Task Summary

**Total Tasks**: 122
- Phase 1 (Setup): 7 tasks
- Phase 2 (Foundational): 13 tasks
- Phase 3 (S1 - Chat Persistence): 21 tasks
- Phase 4 (S2 - Task Creation): 14 tasks
- Phase 5 (S3 - Clean Format): 14 tasks
- Phase 6 (S4 - Thread Limits): 12 tasks
- Phase 7 (S5 - Thread Deletion): 15 tasks
- Phase 8 (Polish): 15 tasks
- Integration Tests: 11 tasks (distributed across phases)

**Estimated Effort**: 5-6 days with 2-3 developers working in parallel

**Risk Level**: Medium (database changes, critical user flows)

---

## Implementation Notes

1. **Test-Driven Development**: Tests are listed first in each user story phase but can be written alongside implementation
2. **Parallelization**: Tasks with same P? marker can be executed in parallel
3. **User Story Independence**: Each user story phase (3-7) can be implemented and tested independently
4. **Database Migrations**: Must be executed in Phase 2 before any user story implementation
5. **Error Handling**: Critical for production readiness - don't skip error handling tasks
6. **Integration Testing**: Essential for verifying end-to-end flows work correctly

**Next Step**: Run `/sp.implement` to begin task execution
