# Tasks: OpenAI Agents SDK Integration

**Input**: Design documents from `/specs/015-openai-agents-integration/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are included in this feature specification - each user story has acceptance scenarios that will be verified.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/`, `backend/tests/`
- Agents: `backend/agents/`
- Routes: `backend/routes/`
- Services: `backend/services/`
- Schemas: `backend/schemas/`, `backend/agents/schemas/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Add OpenAI Agents SDK and httpx dependencies in backend/pyproject.toml
- [X] T002 Add OPENAI_API_KEY placeholder to backend/.env
- [X] T003 Create backend/agents/ package structure with __init__.py, agent.py, tools.py, context.py, and schemas.py files

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Add Conversation SQLModel table to backend/models.py (id, user_id, created_at, updated_at, messages relationship)
- [X] T005 Add Message SQLModel table to backend/models.py (id, user_id, conversation_id, role, content, conversation relationship)
- [X] T006 [P] Create AgentContext dataclass in backend/agents/context.py (user_id, conversation_id, mcp_base_url)
- [X] T007 [P] Create ChatRequest and ChatResponse schemas in backend/schemas/chat.py
- [X] T008 [P] Create agent-specific schemas in backend/agents/schemas.py (TaskPriority, ExtractedTaskDetails, TaskInfo, TaskOperationResult, TaskListResult)
- [X] T009 [P] Create backend/services/chat_service.py with empty module structure
- [X] T010 [P] Create backend/routes/chat.py with empty router
- [X] T011 [P] Create backend/tests/test_agent_tools.py with empty test file
- [X] T012 [P] Create backend/tests/test_chat_service.py with empty test file
- [X] T013 [P] Create backend/tests/test_chat_endpoint.py with empty test file

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create Tasks via Natural Conversation (Priority: P1) 🎯 MVP

**Goal**: Users can create tasks through natural language conversation. Agent extracts details like title, date, priority from casual messages (e.g., "I have a doctor's appointment on Friday") and creates tasks in the system.

**Independent Test**: Send a natural language message containing task information, verify the agent extracts details correctly and creates a task in the database with appropriate attributes.

### Tests for User Story 1

- [X] T014 [P] [US1] Create test for create_task tool in backend/tests/test_agent_tools.py
- [X] T015 [P] [US1] Create test for chat endpoint creating task in backend/tests/test_chat_endpoint.py

### Implementation for User Story 1

- [X] T016 [US1] Implement create_task @function_tool in backend/agents/tools.py (calls MCP server via httpx, returns TaskOperationResult)
- [X] T017 [US1] Implement AGENT_INSTRUCTIONS constant in backend/agents/agent.py with task creation guidance
- [X] T018 [US1] Create TaskManagerAgent in backend/agents/agent.py with create_task tool registered (gpt-4o-mini model)
- [X] T019 [US1] Implement create_conversation function in backend/services/chat_service.py (creates Conversation in DB, returns conversation_id)
- [X] T020 [US1] Implement get_conversation_messages function in backend/services/chat_service.py (retrieves Message history)
- [X] T021 [US1] Implement store_message function in backend/services/chat_service.py (saves user/assistant Message to DB)
- [X] T022 [US1] Implement process_message function in backend/services/chat_service.py (orchestrates agent execution via Runner.run)
- [X] T023 [US1] Implement POST /api/users/{user_id}/chat endpoint in backend/routes/chat.py (JWT auth, user validation, delegates to chat_service)
- [X] T024 [US1] Register chat router in backend/main.py (include in API app)
- [X] T025 [US1] Add logging for task creation operations in backend/agents/tools.py

**Checkpoint**: At this point, User Story 1 should be fully functional - users can create tasks via natural language chat

---

## Phase 4: User Story 2 - View and List Tasks Conversationally (Priority: P1)

**Goal**: Users can query their tasks naturally (e.g., "What do I need to do today?" or "Show me urgent tasks"). Agent retrieves relevant tasks and presents them conversationally.

**Independent Test**: Send a query message, verify the agent retrieves tasks from the backend and formats them in a readable response.

### Tests for User Story 2

- [X] T026 [P] [US2] Create test for list_tasks tool in backend/tests/test_agent_tools.py
- [X] T027 [P] [US2] Create test for chat endpoint listing tasks in backend/tests/test_chat_endpoint.py

### Implementation for User Story 2

- [X] T028 [US2] Implement list_tasks @function_tool in backend/agents/tools.py (calls MCP server with optional status filter)
- [X] T029 [US2] Implement get_task @function_tool in backend/agents/tools.py (calls MCP server for single task retrieval)
- [X] T030 [US2] Register list_tasks and get_task tools in backend/agents/agent.py (update TaskManagerAgent tools list)
- [X] T031 [US2] Update AGENT_INSTRUCTIONS in backend/agents/agent.py with task listing guidance

**Checkpoint**: Users can now create AND list tasks via conversation

---

## Phase 5: User Story 3 - Mark Tasks Complete via Conversation (Priority: P2)

**Goal**: Users can mark tasks as complete through conversation (e.g., "I finished the grocery shopping"). Agent identifies which task and updates its status.

**Independent Test**: Send a completion message, verify the correct task is identified and marked as complete in the database.

### Tests for User Story 3

- [X] T032 [P] [US3] Create test for mark_complete tool in backend/tests/test_agent_tools.py
- [X] T033 [P] [US3] Create test for chat endpoint marking task complete in backend/tests/test_chat_endpoint.py

### Implementation for User Story 3

- [X] T034 [US3] Implement mark_complete @function_tool in backend/agents/tools.py (calls MCP server with idempotency)
- [X] T035 [US3] Register mark_complete tool in backend/agents/agent.py (update TaskManagerAgent tools list)
- [X] T036 [US3] Update AGENT_INSTRUCTIONS in backend/agents/agent.py with task completion guidance

**Checkpoint**: Users can now create, list, and complete tasks via conversation

---

## Phase 6: User Story 4 - Update Task Details via Conversation (Priority: P2)

**Goal**: Users can modify existing tasks through conversation (e.g., "Change my meeting to 3pm instead"). Agent identifies task and applies changes.

**Independent Test**: Send an update message, verify the correct task is identified and modified in the database.

### Tests for User Story 4

- [X] T037 [P] [US4] Create test for update_task tool in backend/tests/test_agent_tools.py
- [X] T038 [P] [US4] Create test for chat endpoint updating task in backend/tests/test_chat_endpoint.py

### Implementation for User Story 4

- [X] T039 [US4] Implement update_task @function_tool in backend/agents/tools.py (calls MCP server with partial updates)
- [X] T040 [US4] Register update_task tool in backend/agents/agent.py (update TaskManagerAgent tools list)
- [X] T041 [US4] Update AGENT_INSTRUCTIONS in backend/agents/agent.py with task update guidance

**Checkpoint**: Users can now create, list, complete, and update tasks via conversation

---

## Phase 7: User Story 5 - Delete Tasks via Conversation (Priority: P3)

**Goal**: Users can remove tasks through conversation (e.g., "Delete the grocery task"). Agent handles deletion with confirmation.

**Independent Test**: Send a deletion message, verify the task is removed from the database.

### Tests for User Story 5

- [X] T042 [P] [US5] Create test for delete_task tool in backend/tests/test_agent_tools.py
- [X] T043 [P] [US5] Create test for chat endpoint deleting task in backend/tests/test_chat_endpoint.py

### Implementation for User Story 5

- [X] T044 [US5] Implement delete_task @function_tool in backend/agents/tools.py (calls MCP server for permanent deletion)
- [X] T045 [US5] Register delete_task tool in backend/agents/agent.py (update TaskManagerAgent tools list)
- [X] T046 [US5] Update AGENT_INSTRUCTIONS in backend/agents/agent.py with task deletion guidance

**Checkpoint**: Users can now perform all CRUD operations on tasks via conversation

---

## Phase 8: User Story 6 - Search Tasks via Conversation (Priority: P3)

**Goal**: Users can search through tasks using natural language (e.g., "Find anything about the project"). Agent returns matching tasks.

**Independent Test**: Send a search query, verify matching tasks are returned based on keyword matching.

### Tests for User Story 6

- [X] T047 [P] [US6] Create test for search_tasks tool in backend/tests/test_agent_tools.py
- [X] T048 [P] [US6] Create test for chat endpoint searching tasks in backend/tests/test_chat_endpoint.py

### Implementation for User Story 6

- [X] T049 [US6] Implement search_tasks @function_tool in backend/agents/tools.py (calls MCP server with keyword search)
- [X] T050 [US6] Register search_tasks tool in backend/agents/agent.py (update TaskManagerAgent tools list)
- [X] T051 [US6] Update AGENT_INSTRUCTIONS in backend/agents/agent.py with task search guidance

**Checkpoint**: All user story features complete - full conversational task management available

---

## Phase 9: Cross-Cutting Concerns (Error Handling & User Isolation)

**Purpose**: Improvements that affect multiple user stories

- [X] T052 [P] Add custom failure_error_function to tools in backend/agents/tools.py for user-friendly error messages
- [X] T053 [P] Add OpenAI API error handling in backend/services/chat_service.py (retry with exponential backoff for rate limits)
- [X] T054 [P] Add conversation context limit in backend/services/chat_service.py (limit to last 20 messages)
- [X] T055 [P] Add user isolation validation in backend/services/chat_service.py (verify user owns conversation)
- [X] T056 [P] Add logging for agent decisions in backend/services/chat_service.py (log tool calls and responses)

---

## Phase 10: Testing (Cross-Story Integration)

**Purpose**: Comprehensive test coverage across all user stories

- [X] T057 [P] Add integration test for multi-turn conversations in backend/tests/test_chat_endpoint.py
- [X] T058 [P] Add test for conversation context persistence in backend/tests/test_chat_service.py
- [X] T059 [P] Add test for user isolation across conversations in backend/tests/test_chat_endpoint.py
- [X] T060 [P] Add unit test for AgentContext in backend/tests/test_agent_tools.py
- [X] T061 [P] Add unit test for schema validation in backend/tests/test_chat_service.py

---

## Phase 11: Polish & Documentation

**Purpose**: Final improvements and documentation

- [X] T062 [P] Update backend/CLAUDE.md with agents/ directory documentation and chat endpoint reference
- [X] T063 [P] Add docstrings to all agent tools in backend/agents/tools.py
- [ ] T064 Add comments to AGENT_INSTRUCTIONS in backend/agents/agent.py with inline examples
- [ ] T065 Run all tests with pytest and ensure 100% pass rate

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Cross-Cutting (Phase 9)**: Depends on relevant user stories being complete
- **Testing (Phase 10)**: Depends on implementation being complete
- **Polish (Phase 11)**: Depends on all desired features being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 5 (P3)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 6 (P3)**: Can start after Foundational (Phase 2) - No dependencies on other stories

**Note**: All user stories are designed to be independently testable. They share the same agent, chat service, and endpoint, but each adds a distinct tool capability.

### Within Each User Story

- Tests for a story MUST be written before implementation tasks
- Tool implementation before agent registration
- Agent registration before chat endpoint usage
- Chat service functions must exist before endpoint calls them
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, ALL user stories (3-8) can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members
- Cross-cutting concern tests marked [P] can run in parallel

---

## Parallel Example: User Story 1 Implementation

```bash
# Launch both tests together:
Task: "Create test for create_task tool in backend/tests/test_agent_tools.py"
Task: "Create test for chat endpoint creating task in backend/tests/test_chat_endpoint.py"

# Tests complete, now implement:
Task: "Implement create_task @function_tool in backend/agents/tools.py"
Task: "Implement AGENT_INSTRUCTIONS constant in backend/agents/agent.py with task creation guidance"

# After tool and instructions ready:
Task: "Create TaskManagerAgent in backend/agents/agent.py with create_task tool registered"

# Now implement chat service functions:
Task: "Implement create_conversation function in backend/services/chat_service.py"
Task: "Implement get_conversation_messages function in backend/services/chat_service.py"
Task: "Implement store_message function in backend/services/chat_service.py"
```

---

## Parallel Example: Multiple User Stories (Team Approach)

```bash
# Once Foundational (Phase 2) is complete:

# Developer A works on User Story 1 (Create Tasks):
Task: "Implement create_task @function_tool in backend/agents/tools.py"
Task: "Implement AGENT_INSTRUCTIONS constant in backend/agents/agent.py"
... (rest of US1 tasks)

# Developer B works on User Story 2 (List Tasks) in parallel:
Task: "Implement list_tasks @function_tool in backend/agents/tools.py"
Task: "Implement get_task @function_tool in backend/agents/tools.py"
... (rest of US2 tasks)

# Developer C works on User Story 3 (Mark Complete) in parallel:
Task: "Implement mark_complete @function_tool in backend/agents/tools.py"
... (rest of US3 tasks)

# Merge when all complete
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T013) - **CRITICAL - blocks all stories**
3. Complete Phase 3: User Story 1 (T014-T025)
4. **STOP and VALIDATE**: Test User Story 1 independently via chat endpoint
5. Demo: User can create tasks via natural language conversation
6. Optionally add User Story 2 for basic list capability

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (P1) → Test independently → Demo (MVP!)
3. Add User Story 2 (P1) → Test independently → Demo
4. Add User Story 3 (P2) → Test independently → Demo
5. Add User Story 4 (P2) → Test independently → Demo
6. Add User Story 5 (P3) → Test independently → Demo
7. Add User Story 6 (P3) → Test independently → Demo
8. Complete cross-cutting, testing, and polish
9. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup (T001-T003) together
2. Team completes Foundational (T004-T013) together
3. Once Foundational is done:
   - Developer A: User Story 1 (T014-T025)
   - Developer B: User Story 2 (T026-T031)
   - Developer C: User Story 3 (T032-T036)
4. Team integrates and resolves conflicts
5. Continue with remaining stories or cross-cutting concerns
6. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests are written first (TDD) but can be adapted to write tests during/after implementation
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- All tools call MCP server via httpx, never access database directly
- User isolation is enforced at multiple levels: endpoint validation, context passing, MCP tool calls
