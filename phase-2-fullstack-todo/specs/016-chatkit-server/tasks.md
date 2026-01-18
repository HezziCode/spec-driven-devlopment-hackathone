# Tasks: ChatKit AI Chat Server

**Input**: Design documents from `/specs/016-chatkit-server/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), data-model.md, contracts/

**Tests**: Not explicitly requested in feature specification

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/`, `backend/tests/`
- ChatKit: `backend/chatkit/`
- Routes: `backend/routes/`
- Services: `backend/services/`
- Models: `backend/models.py`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Add httpx dependency for streaming HTTP client in backend/pyproject.toml
- [ ] T002 Add SSE (sse-starlette) dependency for Server-Sent Events support in backend/pyproject.toml
- [ ] T003 Create backend/chatkit/ package structure with __init__.py, server.py, thread_manager.py, streaming.py, and agent.py files

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 [P] Add Thread SQLModel table to backend/models.py (id, user_id, title, created_at, updated_at)
- [ ] T005 [P] Add ChatMessage SQLModel table to backend/models.py (id, thread_id, role, content, created_at)
- [ ] T006 [P] Create ChatContext dataclass in backend/chatkit/context.py (user_id, thread_id, mcp_base_url)
- [ ] T007 [P] Create ChatRequest and StreamingResponse schemas in backend/schemas/chatkit.py
- [ ] T008 [P] Create backend/services/chatkit_service.py with empty module structure
- [ ] T009 [P] Create backend/routes/chatkit.py with empty router
- [ ] T010 [P] Create backend/tests/test_chatkit_server.py with empty test file
- [ ] T011 [P] Create backend/tests/test_chatkit_thread_manager.py with empty test file

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Send Chat Message with Streaming Response (Priority: P1) 🎯 MVP

**Goal**: Users can send a message and receive AI response via streaming. System uses Runner.run_streamed() with SSE format.

**Independent Test**: Send message to POST /chatkit, verify streaming response with content-type text/event-stream, confirm tokens arrive incrementally.

### Implementation for User Story 1

- [ ] T012 [US1] Implement ThreadManager class in backend/chatkit/thread_manager.py with create_thread() method
- [ ] T013 [US1] Implement add_message() method in ThreadManager for persisting user/assistant messages
- [ ] T014 [US1] Implement get_recent_messages() in ThreadManager to retrieve last 20 messages per thread
- [ ] T015 [US1] Implement ChatAgent class in backend/chatkit/agent.py with chat-specific instructions
- [ ] T016 [US1] Implement ChatKitServer class in backend/chatkit/server.py with respond() using Runner.run_streamed()
- [ ] T017 [US1] Implement StreamingResponse generator in backend/chatkit/streaming.py for SSE format
- [ ] T018 [US1] Implement process_message() in backend/services/chatkit_service.py (orchestrates agent + thread)
- [ ] T019 [US1] Implement POST /chatkit endpoint in backend/routes/chatkit.py (JWT auth, delegates to chatkit_service)
- [ ] T020 [US1] Register chatkit router in backend/main.py (include in API app)
- [ ] T021 [US1] Add logging for streaming operations in backend/chatkit/streaming.py

**Checkpoint**: At this point, User Story 1 should be fully functional - users can send messages and receive streaming AI responses

---

## Phase 4: User Story 2 - Manage Conversation Threads (Priority: P1)

**Goal**: Users can create threads, list their threads, and continue existing conversations. Each thread maintains independent context.

**Independent Test**: Create thread, send multiple messages, verify context maintained. Create second thread, verify no message leakage.

### Implementation for User Story 2

- [ ] T022 [US2] Implement list_threads() in ThreadManager to get user's threads with metadata
- [ ] T023 [US2] Implement get_thread() in ThreadManager to retrieve thread with messages
- [ ] T024 [US2] Implement delete_thread() in ThreadManager to remove thread and all messages
- [ ] T025 [US2] Update ThreadManager to auto-generate thread titles from first message
- [ ] T026 [US2] Implement GET /chatkit/threads endpoint in backend/routes/chatkit.py
- [ ] T027 [US2] Implement GET /chatkit/threads/{thread_id} endpoint in backend/routes/chatkit.py
- [ ] T028 [US2] Implement DELETE /chatkit/threads/{thread_id} endpoint in backend/routes/chatkit.py
- [ ] T029 [US2] Add user isolation validation in all thread endpoints (verify user owns thread)

**Checkpoint**: Users can now create AND manage conversation threads

---

## Phase 5: User Story 3 - Context-Aware AI Responses (Priority: P2)

**Goal**: AI agent uses tools to perform actions. User can ask about tasks, create tasks, etc. through natural conversation.

**Independent Test**: Send message requiring tool usage ("List my tasks"), verify tool is called and results included in response.

### Implementation for User Story 3

- [ ] T030 [US3] Create ChatAgentContext extending AgentContext in backend/chatkit/context.py
- [ ] T031 [US3] Update ChatAgent instructions to include tool usage guidance for task operations
- [ ] T032 [US3] Update ChatKitServer to pass ChatAgentContext with user_id to Runner.run_streamed()
- [ ] T033 [US3] Implement tool result formatting in streaming.py for tool_call and tool_result events
- [ ] T034 [US3] Add tool call logging in backend/chatkit/server.py

**Checkpoint**: Agent can now use tools to perform actions on behalf of user

---

## Phase 6: User Story 4 - Stream Processing and Error Handling (Priority: P2)

**Goal**: System handles errors gracefully during streaming. Users receive meaningful feedback without corrupted responses.

**Independent Test**: Trigger errors (invalid thread, service unavailable), verify error events in streaming format.

### Implementation for User Story 4

- [ ] T035 [US4] Add error handling wrapper in streaming.py for graceful SSE error events
- [ ] T036 [US4] Implement retry logic for transient failures in ChatKitServer.respond()
- [ ] T037 [US4] Add timeout handling for long-running agent responses
- [ ] T038 [US4] Implement connection cleanup on client disconnect in streaming generator

**Checkpoint**: All user stories complete - full chat functionality available

---

## Phase 7: Cross-Cutting Concerns (Error Handling & User Isolation)

**Purpose**: Improvements that affect multiple user stories

- [ ] T039 [P] Add user isolation validation in ThreadManager for all operations
- [ ] T040 [P] Add conversation context limit (last 20 messages) in ThreadManager
- [ ] T041 [P] Add logging for agent decisions and tool calls in chatkit_service.py
- [ ] T042 [P] Add rate limiting considerations for /chatkit endpoint

---

## Phase 8: Testing (Cross-Story Integration)

**Purpose**: Comprehensive test coverage across all user stories

- [ ] T043 [P] Add integration test for streaming response in backend/tests/test_chatkit_server.py
- [ ] T044 [P] Add test for thread context preservation in backend/tests/test_chatkit_thread_manager.py
- [ ] T045 [P] Add test for user isolation across threads in backend/tests/test_chatkit_server.py
- [ ] T046 [P] Add unit test for ChatContext in backend/tests/test_chatkit_server.py
- [ ] T047 [P] Add test for error handling during streaming in backend/tests/test_chatkit_server.py

---

## Phase 9: Polish & Documentation

**Purpose**: Final improvements and documentation

- [ ] T048 [P] Update backend/CLAUDE.md with chatkit/ directory documentation
- [ ] T049 [P] Add docstrings to all chatkit classes and methods
- [ ] T050 [P] Run all tests with pytest and ensure 90% pass rate

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (US1 → US2 → US3 → US4)
- **Cross-Cutting (Phase 7)**: Depends on relevant user stories being complete
- **Testing (Phase 8)**: Depends on implementation being complete
- **Polish (Phase 9)**: Depends on all desired features being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Depends on US1 for context passing
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Can be done in parallel with other stories

**Note**: All user stories are designed to be independently testable. They share the same ChatKitServer, ThreadManager, and endpoint, but each adds distinct functionality.

### Within Each User Story

- Core implementation before endpoint usage
- ThreadManager functions must exist before ChatKitServer uses them
- ChatKitServer must exist before chat_service uses it
- Chat service functions must exist before endpoint calls them
- Core implementation before integration

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational is done, ALL user stories (3-6) can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members
- Cross-cutting concern tests marked [P] can run in parallel

---

## Parallel Example: User Story 1 Implementation

```bash
# Launch these together (different files, no dependencies):
Task: "Implement ThreadManager class in backend/chatkit/thread_manager.py"
Task: "Implement ChatAgent class in backend/chatkit/agent.py"
Task: "Implement StreamingResponse generator in backend/chatkit/streaming.py"

# After ThreadManager and ChatAgent ready:
Task: "Implement ChatKitServer class in backend/chatkit/server.py"

# Now implement chat service:
Task: "Implement process_message() in backend/services/chatkit_service.py"

# Finally implement endpoint:
Task: "Implement POST /chatkit endpoint in backend/routes/chatkit.py"
```

---

## Parallel Example: Multiple User Stories (Team Approach)

Once Foundational (Phase 2) is complete:

**Developer A works on User Story 1 (Streaming)**:
- Task: "Implement ThreadManager with create_thread, add_message, get_recent_messages"
- Task: "Implement ChatKitServer with respond() using Runner.run_streamed()"
- ... (rest of US1 tasks)

**Developer B works on User Story 2 (Thread Management)**:
- Task: "Implement list_threads() in ThreadManager"
- Task: "Implement GET /chatkit/threads endpoint"
- ... (rest of US2 tasks)

**Developer C works on User Story 3 (Tool Usage)**:
- Task: "Create ChatAgentContext extending AgentContext"
- Task: "Update ChatAgent instructions for tool usage"
- ... (rest of US3 tasks)

# Merge when all complete
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T011) - **CRITICAL - blocks all stories**
3. Complete Phase 3: User Story 1 (T012-T021)
4. **STOP and VALIDATE**: Test streaming response via curl
5. Demo: User can send message and see streaming AI response
6. Optionally add User Story 2 for thread management

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (P1) → Test independently → Demo (MVP!)
3. Add User Story 2 (P1) → Test independently → Demo
4. Add User Story 3 (P2) → Test independently → Demo
5. Add User Story 4 (P2) → Test independently → Demo
6. Complete cross-cutting, testing, and polish
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup (T001-T003) together
2. Team completes Foundational (T004-T011) together
3. Once Foundational is done:
   - Developer A: User Story 1 (T012-T021)
   - Developer B: User Story 2 (T022-T029)
   - Developer C: User Story 3 (T030-T034)
4. Team integrates and resolves conflicts
5. Continue with remaining stories or cross-cutting concerns
6. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests are not explicitly requested but can be added
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- All tools call MCP server via httpx, never access database directly
- User isolation is enforced at multiple levels: endpoint validation, context passing, ThreadManager checks
