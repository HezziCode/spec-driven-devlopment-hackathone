# Tasks: Fix Delete MCP Tool (001-fix-delete-mcp)

**Feature Branch**: 001-fix-delete-mcp
**Total Tasks**: 12
**User Stories**: 2 (P1: Delete by title, P2: Error handling)
**MVP Scope**: Complete US1 (P1) for viable delete-by-title

## Dependencies & Execution Order
- **Phase 1 → Phase 2** (sequential: setup blocks all)
- **Phase 2 → Phase 3** (US1 P1 first)
- **Phase 3 → Phase 4** (US2 depends on US1 success path)
- **Parallel Opportunities**: [P] tasks in Phases 3-4 (tests/docs independent)

**Story Dependencies**: US1 independent; US2 builds on US1.

## Phase 1: Setup (Project Initialization)
- [ ] T001 Verify MCP agent setup in backend/services/chatkit_service.py

## Phase 2: Foundational (Blocking Prerequisites)
- [ ] T002 Enhance agent instructions for title-to-ID resolution in backend/services/chatkit_service.py

## Phase 3: User Story 1 - Delete task via chatbot (P1)
**Goal**: User says \"delete [title]\" → agent searches → deletes → confirms.
**Independent Test**: Chat request deletes task; list excludes it.

- [ ] T003 [P] [US1] Add test for successful title delete in backend/tests/test_chatkit_service.py
- [ ] T004 [US1] Implement search_tasks → extract ID → delete_task chain in backend/services/chatkit_service.py
- [ ] T005 [P] [US1] Add logging for delete chain in backend/services/chatkit_service.py
- [ ] T006 [US1] Verify chat endpoint streams delete confirmation in backend/routes/chatkit.py

## Phase 4: User Story 2 - Handle deletion errors gracefully (P2)
**Goal**: No task/ambiguous → clear error + suggest list.
**Independent Test**: Invalid title → helpful response, no crash.

- [ ] T007 [P] [US2] Add test for no-match error in backend/tests/test_chatkit_service.py
- [ ] T008 [P] [US2] Add test for ambiguous titles in backend/tests/test_chatkit_service.py
- [ ] T009 [US2] Implement error handling (no match/ambiguous) in backend/services/chatkit_service.py
- [ ] T010 [US2] Enhance agent prompt for error suggestions in backend/services/chatkit_service.py

## Phase 5: Polish & Cross-Cutting
- [ ] T011 Run mypy and pytest on new code in backend/
- [ ] T012 [P] Update docs/comments in backend/services/chatkit_service.py
- [ ] T013 [P] Add integration test for full chat delete flow in backend/tests/test_chatkit.py

## Parallel Execution Examples
**US1**: T003/T005 (tests/docs) || T004/T006 (impl)
**US2**: T007/T008 (tests) || T009/T010 (impl)

## Implementation Strategy
1. MVP: Phase 1-3 (US1) → testable delete-by-title
2. Incremental: Phase 4 (errors) → robust
3. Validate: Manual chat test + pytest coverage >95% on changes