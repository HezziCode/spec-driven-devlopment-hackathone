# Tasks: MCP Server for Todo Management

**Feature**: 014-mcp-todo-server
**Input**: Design documents from `/specs/014-mcp-todo-server/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Test tasks included as specified in plan.md Phase 5.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/` at repository root
- All paths relative to `backend/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency setup

- [x] T001 Add `fastmcp>=2.0` dependency to backend/pyproject.toml
- [x] T002 Run `uv sync` to install FastMCP dependency
- [x] T003 Create directory structure: `backend/mcp_server/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core MCP server infrastructure that MUST be complete before ANY tool implementation

**⚠️ CRITICAL**: No tool implementation can begin until this phase is complete

- [x] T004 Create `backend/mcp_server/__init__.py` with package exports
- [x] T005 [P] Create `TaskStatus` enum (all, pending, completed) in `backend/mcp_server/schemas.py`
- [x] T006 [P] Create `TaskResponse` output schema in `backend/mcp_server/schemas.py`
- [x] T007 [P] Create `TaskDetail` output schema in `backend/mcp_server/schemas.py`
- [x] T008 [P] Create `TaskListResponse` output schema in `backend/mcp_server/schemas.py`
- [x] T009 [P] Create `ErrorResponse` output schema in `backend/mcp_server/schemas.py`
- [x] T010 Create FastMCP server instance in `backend/mcp_server/server.py`
- [x] T011 Implement database lifespan context manager in `backend/mcp_server/server.py`
- [x] T012 Create empty `backend/mcp_server/tools.py` with mcp import from server.py

**Checkpoint**: Foundation ready - tool implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create Task Tool (Priority: P1) 🎯 MVP

**Goal**: Enable AI agents to create new tasks for users via MCP tool

**Independent Test**: Invoke create_task with valid user_id and title, verify task created in database

### Input Schema for US1

- [x] T013 [US1] Create `CreateTaskInput` schema in `backend/mcp_server/schemas.py`

### Implementation for US1

- [x] T014 [US1] Implement `create_task` tool with @mcp.tool decorator in `backend/mcp_server/tools.py`
- [x] T015 [US1] Add input validation (title 1-200 chars, description max 2000) in create_task tool
- [x] T016 [US1] Add user_id validation and database task creation logic
- [x] T017 [US1] Return TaskResponse with task_id, status="created", and title

**Checkpoint**: create_task tool functional and independently testable

---

## Phase 4: User Story 2 - List Tasks Tool (Priority: P1) 🎯 MVP

**Goal**: Enable AI agents to retrieve user's tasks with optional status filtering

**Independent Test**: Create test tasks, invoke list_tasks with various status filters, verify correct results

### Input Schema for US2

- [x] T018 [US2] Create `ListTasksInput` schema in `backend/mcp_server/schemas.py`

### Implementation for US2

- [x] T019 [US2] Implement `list_tasks` tool with @mcp.tool decorator in `backend/mcp_server/tools.py`
- [x] T020 [US2] Add status filter logic (all/pending/completed) using SQLModel query
- [x] T021 [US2] Return TaskListResponse with tasks array and total count

**Checkpoint**: list_tasks tool functional and independently testable

---

## Phase 5: User Story 3 - Mark Complete Tool (Priority: P2)

**Goal**: Enable AI agents to mark tasks as completed (idempotent operation)

**Independent Test**: Create pending task, invoke mark_complete, verify completed=true in database

### Input Schema for US3

- [x] T022 [US3] Create `TaskIdInput` schema (user_id, task_id) in `backend/mcp_server/schemas.py`

### Implementation for US3

- [x] T023 [US3] Implement `mark_complete` tool with @mcp.tool decorator in `backend/mcp_server/tools.py`
- [x] T024 [US3] Add user isolation check (task.user_id == user_id)
- [x] T025 [US3] Return TaskResponse with status="completed" (idempotent for already-completed tasks)

**Checkpoint**: mark_complete tool functional and independently testable

---

## Phase 6: User Story 4 - Update Task Tool (Priority: P2)

**Goal**: Enable AI agents to modify task title and/or description

**Independent Test**: Create task, invoke update_task with new title, verify change persisted

### Input Schema for US4

- [x] T026 [US4] Create `UpdateTaskInput` schema with at-least-one-field validator in `backend/mcp_server/schemas.py`

### Implementation for US4

- [x] T027 [US4] Implement `update_task` tool with @mcp.tool decorator in `backend/mcp_server/tools.py`
- [x] T028 [US4] Add user isolation and task existence check
- [x] T029 [US4] Update only provided fields (title and/or description)
- [x] T030 [US4] Return TaskResponse with status="updated"

**Checkpoint**: update_task tool functional and independently testable

---

## Phase 7: User Story 5 - Delete Task Tool (Priority: P2)

**Goal**: Enable AI agents to permanently remove tasks

**Independent Test**: Create task, invoke delete_task, verify task no longer exists in database

### Implementation for US5

- [x] T031 [US5] Implement `delete_task` tool with @mcp.tool decorator in `backend/mcp_server/tools.py`
- [x] T032 [US5] Add user isolation and task existence check
- [x] T033 [US5] Delete task from database and return TaskResponse with status="deleted"

**Checkpoint**: delete_task tool functional and independently testable

---

## Phase 8: User Story 6 - Search Tasks Tool (Priority: P3)

**Goal**: Enable AI agents to search tasks by keyword in title or description

**Independent Test**: Create tasks with specific keywords, invoke search_tasks, verify matching results

### Input Schema for US6

- [x] T034 [US6] Create `SearchTasksInput` schema in `backend/mcp_server/schemas.py`

### Implementation for US6

- [x] T035 [US6] Implement `search_tasks` tool with @mcp.tool decorator in `backend/mcp_server/tools.py`
- [x] T036 [US6] Add PostgreSQL ILIKE search on title and description fields
- [x] T037 [US6] Return TaskListResponse with matching tasks and total count

**Checkpoint**: search_tasks tool functional and independently testable

---

## Phase 9: FastAPI Integration

**Purpose**: Mount MCP server in existing FastAPI application

- [x] T038 Import mcp_server in `backend/main.py`
- [x] T039 Create combined lifespan handler for FastAPI + MCP in `backend/main.py`
- [x] T040 Mount MCP app at `/mcp` endpoint in `backend/main.py`
- [x] T041 Verify existing API endpoints remain functional (health check)

**Checkpoint**: MCP server accessible at `/mcp`, existing API unaffected

---

## Phase 10: Testing

**Purpose**: Comprehensive test coverage for MCP tools

### Test Infrastructure

- [x] T042 [P] Create test file `backend/tests/test_mcp_tools.py`
- [x] T043 [P] Add pytest fixtures for test database session and test user

### US1 Tests - create_task

- [x] T044 [P] [US1] Test create_task success with valid input
- [x] T045 [P] [US1] Test create_task with title + description
- [x] T046 [P] [US1] Test create_task validation error (empty title)
- [x] T047 [P] [US1] Test create_task validation error (title > 200 chars)

### US2 Tests - list_tasks

- [x] T048 [P] [US2] Test list_tasks with status="all"
- [x] T049 [P] [US2] Test list_tasks with status="pending"
- [x] T050 [P] [US2] Test list_tasks with status="completed"
- [x] T051 [P] [US2] Test list_tasks returns empty list for user with no tasks

### US3 Tests - mark_complete

- [x] T052 [P] [US3] Test mark_complete success on pending task
- [x] T053 [P] [US3] Test mark_complete idempotent on already-completed task
- [x] T054 [P] [US3] Test mark_complete not found error
- [x] T055 [P] [US3] Test mark_complete user isolation (wrong user)

### US4 Tests - update_task

- [x] T056 [P] [US4] Test update_task with new title only
- [x] T057 [P] [US4] Test update_task with new description only
- [x] T058 [P] [US4] Test update_task with both title and description
- [x] T059 [P] [US4] Test update_task validation error (no fields provided)

### US5 Tests - delete_task

- [x] T060 [P] [US5] Test delete_task success
- [x] T061 [P] [US5] Test delete_task not found error
- [x] T062 [P] [US5] Test delete_task user isolation (wrong user)

### US6 Tests - search_tasks

- [x] T063 [P] [US6] Test search_tasks finds matches in title
- [x] T064 [P] [US6] Test search_tasks finds matches in description
- [x] T065 [P] [US6] Test search_tasks case-insensitive matching
- [x] T066 [P] [US6] Test search_tasks returns empty list when no matches

### Coverage Verification

- [x] T067 Run pytest with coverage report, verify >= 90% for mcp_server module

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T068 [P] Add docstrings to all tool functions in `backend/mcp_server/tools.py`
- [x] T069 [P] Add logging for database operations and errors
- [x] T070 Verify all tools return consistent ErrorResponse format
- [x] T071 Run quickstart.md validation scenarios
- [x] T072 Update backend/CLAUDE.md with MCP server documentation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 - BLOCKS all tool implementation
- **User Stories (Phases 3-8)**: All depend on Phase 2 completion
  - US1 (P1) and US2 (P1) are highest priority and should be done first
  - US3, US4, US5 (P2) can proceed after MVP is verified
  - US6 (P3) is enhancement priority
- **Integration (Phase 9)**: Depends on at least one tool being implemented (ideally after Phase 4)
- **Testing (Phase 10)**: Depends on tool implementations (can be done in parallel with later phases)
- **Polish (Phase 11)**: Depends on all core functionality being complete

### User Story Dependencies

- **US1 (create_task)**: Can start after Phase 2 - No dependencies on other stories
- **US2 (list_tasks)**: Can start after Phase 2 - No dependencies on other stories
- **US3 (mark_complete)**: Uses TaskIdInput schema - No story dependencies but reuses US3 schema
- **US4 (update_task)**: Uses UpdateTaskInput schema - No story dependencies
- **US5 (delete_task)**: Uses TaskIdInput schema from US3 - Depends on T022
- **US6 (search_tasks)**: Uses SearchTasksInput schema - No story dependencies

### Within Each User Story

- Schema tasks before implementation tasks
- Implementation tasks in logical order (tool → validation → database logic → response)
- Story checkpoint before moving to next priority

### Parallel Opportunities

**Phase 2 - All schemas can be created in parallel:**
```
T005, T006, T007, T008, T009 (all [P] marked)
```

**Phase 10 - All tests can be written in parallel:**
```
T044-T047 (US1 tests)
T048-T051 (US2 tests)
T052-T055 (US3 tests)
T056-T059 (US4 tests)
T060-T062 (US5 tests)
T063-T066 (US6 tests)
```

---

## Parallel Example: Phase 2 Foundation

```bash
# Launch all foundational schemas together:
Task: "Create TaskStatus enum in backend/mcp_server/schemas.py"
Task: "Create TaskResponse output schema in backend/mcp_server/schemas.py"
Task: "Create TaskDetail output schema in backend/mcp_server/schemas.py"
Task: "Create TaskListResponse output schema in backend/mcp_server/schemas.py"
Task: "Create ErrorResponse output schema in backend/mcp_server/schemas.py"
```

---

## Implementation Strategy

### MVP First (US1 + US2 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T012)
3. Complete Phase 3: US1 create_task (T013-T017)
4. Complete Phase 4: US2 list_tasks (T018-T021)
5. **STOP and VALIDATE**: Test both tools independently
6. Complete Phase 9: FastAPI Integration (T038-T041)
7. Deploy/demo if ready - **MVP Complete!**

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 + US2 → Test independently → **MVP!**
3. Add US3, US4, US5 → Test independently → **P2 Features!**
4. Add US6 → Test independently → **P3 Enhancement!**
5. Testing + Polish → **Production Ready!**

### Single Developer Strategy

1. Complete phases sequentially: 1 → 2 → 3 → 4 → 9 (MVP)
2. Then continue: 5 → 6 → 7 → 8 (P2 features)
3. Finally: 10 → 11 (Testing & Polish)

---

## Summary

| Phase | Tasks | Purpose |
|-------|-------|---------|
| Phase 1: Setup | T001-T003 | Dependencies and directory structure |
| Phase 2: Foundational | T004-T012 | Core schemas and server infrastructure |
| Phase 3: US1 | T013-T017 | create_task tool (P1) |
| Phase 4: US2 | T018-T021 | list_tasks tool (P1) |
| Phase 5: US3 | T022-T025 | mark_complete tool (P2) |
| Phase 6: US4 | T026-T030 | update_task tool (P2) |
| Phase 7: US5 | T031-T033 | delete_task tool (P2) |
| Phase 8: US6 | T034-T037 | search_tasks tool (P3) |
| Phase 9: Integration | T038-T041 | FastAPI mount at /mcp |
| Phase 10: Testing | T042-T067 | Comprehensive test coverage |
| Phase 11: Polish | T068-T072 | Documentation and verification |

**Total Tasks**: 72
**MVP Tasks**: 24 (Phases 1-4 + 9)
**P2 Tasks**: 20 (Phases 5-7)
**P3 Tasks**: 4 (Phase 8)
**Testing/Polish**: 31 (Phases 10-11)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All tools share the same schemas.py file but create different schema classes
