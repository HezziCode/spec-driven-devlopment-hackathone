# Tasks: Fix Chat SSE Parsing

**Input**: Design documents from `/specs/018-fix-chat-sse-parsing/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), data-model.md, contracts/, quickstart.md

**Tests**: Tests are included following TDD approach as specified in the implementation plan.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/` for all frontend code
- All paths are relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and verification

- [x] T001 Verify no additional npm dependencies required for SSE parsing (uses native browser APIs)
- [x] T002 [P] Set up Jest/Vitest test environment for frontend SSE testing in frontend/__tests__/
- [x] T003 [P] Configure TypeScript strict mode validation for new SSE files

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core type definitions that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Create SSE type definitions in frontend/types/sse.ts with all interfaces from data-model.md
- [x] T005 [P] Create type exports and type guards in frontend/types/sse.ts (isTextDeltaData, isDoneData, isErrorData)
- [x] T006 [P] Validate TypeScript compilation passes for new type definitions

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Clean Chat Message Display (Priority: P1) 🎯 MVP

**Goal**: Display chat responses as clean, readable text without any SSE protocol artifacts (data:, event:, thread_id)

**Independent Test**: Send a chat message and verify the response displays as "Hi there!" instead of "data: Hidata:  theredata: !event: donedata: {\"thread_id\": \"abc123\"}"

### Tests for User Story 1 (TDD - Write First)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T007 [P] [US1] Unit test for parseSSELine() function in frontend/__tests__/lib/sse-parser.test.ts
- [ ] T008 [P] [US1] Unit test for parseSSEEvent() function in frontend/__tests__/lib/sse-parser.test.ts
- [ ] T009 [P] [US1] Unit test for extractTextContent() function in frontend/__tests__/lib/sse-parser.test.ts
- [ ] T010 [P] [US1] Unit test for filterMetadata() function in frontend/__tests__/lib/sse-parser.test.ts
- [ ] T011 [P] [US1] Unit test for parseSSEStream() main function in frontend/__tests__/lib/sse-parser.test.ts
- [ ] T012 [P] [US1] Test case: verify "data:" prefixes are removed from output
- [ ] T013 [P] [US1] Test case: verify "event:" markers are removed from output
- [ ] T014 [P] [US1] Test case: verify thread_id metadata is separated and not displayed
- [ ] T015 [P] [US1] Test case: verify multi-line data fields are combined with proper spacing

### Implementation for User Story 1

- [x] T016 [US1] Implement parseSSELine() to parse single SSE protocol line in frontend/lib/sse-parser.ts
- [x] T017 [US1] Implement parseSSEEvent() to parse complete SSE event in frontend/lib/sse-parser.ts
- [x] T018 [US1] Implement extractTextContent() to extract clean text from data field in frontend/lib/sse-parser.ts
- [x] T019 [US1] Implement filterMetadata() to separate metadata from content in frontend/lib/sse-parser.ts
- [x] T020 [US1] Implement parseSSEStream() main parsing function in frontend/lib/sse-parser.ts
- [x] T021 [US1] Add JSDoc documentation to all parser functions in frontend/lib/sse-parser.ts
- [x] T022 [US1] Create MessageDisplay component for clean message rendering in frontend/components/MessageDisplay.tsx
- [x] T023 [US1] Update ChatInterface component to use sse-parser utility in frontend/components/ChatInterface.tsx
- [x] T024 [US1] Add integration test for ChatInterface with clean text display in frontend/__tests__/components/ChatInterface.test.tsx
- [x] T025 [US1] Verify all tests pass and clean text displays without protocol artifacts

**Checkpoint**: At this point, User Story 1 should be fully functional - chat displays clean text without "data:", "event:", or thread_id visible

---

## Phase 4: User Story 2 - Streaming Message Display (Priority: P2)

**Goal**: Display chat responses progressively as they stream in, maintaining proper formatting throughout

**Independent Test**: Send a message that generates a longer response and observe text appearing word-by-word with proper spacing, not all at once

### Tests for User Story 2 (TDD - Write First)

- [ ] T026 [P] [US2] Unit test for useSSEStream hook connection management in frontend/__tests__/hooks/useSSEStream.test.ts
- [ ] T027 [P] [US2] Unit test for useSSEStream hook stream reading in frontend/__tests__/hooks/useSSEStream.test.ts
- [ ] T028 [P] [US2] Unit test for useSSEStream hook progressive text accumulation in frontend/__tests__/hooks/useSSEStream.test.ts
- [ ] T029 [P] [US2] Unit test for useSSEStream hook cleanup on unmount in frontend/__tests__/hooks/useSSEStream.test.ts
- [ ] T030 [P] [US2] Test case: verify text appears progressively chunk-by-chunk
- [ ] T031 [P] [US2] Test case: verify proper word spacing maintained during streaming
- [ ] T032 [P] [US2] Test case: verify no duplicate content in progressive display

### Implementation for User Story 2

- [ ] T033 [US2] Create useSSEStream custom hook skeleton in frontend/hooks/useSSEStream.ts
- [ ] T034 [US2] Implement SSE connection management with fetch API in frontend/hooks/useSSEStream.ts
- [ ] T035 [US2] Implement ReadableStream reader setup and text decoder in frontend/hooks/useSSEStream.ts
- [ ] T036 [US2] Implement progressive text accumulation logic in frontend/hooks/useSSEStream.ts
- [ ] T037 [US2] Implement streaming state management (isActive, accumulatedContent) in frontend/hooks/useSSEStream.ts
- [ ] T038 [US2] Implement cleanup logic for stream closure on unmount in frontend/hooks/useSSEStream.ts
- [ ] T039 [US2] Update ChatInterface to use useSSEStream hook in frontend/components/ChatInterface.tsx
- [ ] T040 [US2] Update MessageDisplay to show streaming indicator (cursor) in frontend/components/MessageDisplay.tsx
- [ ] T041 [US2] Add integration test for progressive streaming display in frontend/__tests__/components/ChatInterface.test.tsx
- [ ] T042 [US2] Verify streaming works smoothly with proper formatting at each stage

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - clean text displays progressively as it streams

---

## Phase 5: User Story 3 - Error Message Clarity (Priority: P3)

**Goal**: Display user-friendly error messages when chat communication fails, without exposing technical details

**Independent Test**: Simulate network failure and verify error message shows "Connection lost. Please try again." instead of raw error data

### Tests for User Story 3 (TDD - Write First)

- [ ] T043 [P] [US3] Unit test for error handling in parseSSEStream in frontend/__tests__/lib/sse-parser.test.ts
- [ ] T044 [P] [US3] Unit test for error handling in useSSEStream hook in frontend/__tests__/hooks/useSSEStream.test.ts
- [ ] T045 [P] [US3] Test case: verify network error shows user-friendly message
- [ ] T046 [P] [US3] Test case: verify parse error shows user-friendly message
- [ ] T047 [P] [US3] Test case: verify timeout error shows user-friendly message
- [ ] T048 [P] [US3] Test case: verify no raw error data or stack traces visible to user

### Implementation for User Story 3

- [ ] T049 [US3] Add error handling to parseSSEStream with ParserError types in frontend/lib/sse-parser.ts
- [ ] T050 [US3] Add error state management to useSSEStream hook in frontend/hooks/useSSEStream.ts
- [ ] T051 [US3] Implement user-friendly error message mapping in frontend/hooks/useSSEStream.ts
- [ ] T052 [US3] Add error display to MessageDisplay component in frontend/components/MessageDisplay.tsx
- [ ] T053 [US3] Update ChatInterface to handle and display errors in frontend/components/ChatInterface.tsx
- [ ] T054 [US3] Add integration test for error scenarios in frontend/__tests__/components/ChatInterface.test.tsx
- [ ] T055 [US3] Verify all error messages are user-friendly without technical details

**Checkpoint**: All user stories should now be independently functional - clean text, streaming, and error handling all work

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Edge cases, performance, and final validation

- [ ] T056 [P] Test SSE parser with special characters (emojis, Unicode) in frontend/__tests__/lib/sse-parser.test.ts
- [ ] T057 [P] Test SSE parser with very long messages (>10KB) in frontend/__tests__/lib/sse-parser.test.ts
- [ ] T058 [P] Test SSE parser with rapid message succession in frontend/__tests__/lib/sse-parser.test.ts
- [ ] T059 [P] Test SSE parser with empty or whitespace-only responses in frontend/__tests__/lib/sse-parser.test.ts
- [ ] T060 [P] Test SSE parser with interrupted streaming connection in frontend/__tests__/hooks/useSSEStream.test.ts
- [ ] T061 [P] Verify accessibility with screen readers (ARIA labels, semantic HTML) in frontend/components/MessageDisplay.tsx
- [ ] T062 [P] Performance benchmark: measure chunk display latency (<100ms target) in frontend/__tests__/lib/sse-parser.test.ts
- [ ] T063 [P] Browser compatibility testing (Chrome, Firefox, Safari, Edge)
- [ ] T064 [P] Update CustomChatInterface component if it exists in frontend/components/CustomChatInterface.tsx
- [ ] T065 [P] Code review and refactoring for clean code principles
- [ ] T066 [P] Add JSDoc comments to all public functions and types
- [ ] T067 Run full test suite and verify 100% pass rate
- [ ] T068 Validate against quickstart.md implementation checklist
- [ ] T069 Final integration test with real backend SSE endpoint
- [ ] T070 Verify all success criteria from spec.md are met

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P2): Can start after Foundational - Builds on US1 but independently testable
  - User Story 3 (P3): Can start after Foundational - Builds on US1/US2 but independently testable
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
  - Delivers: Clean text display without protocol artifacts
  - MVP: This story alone makes chat usable

- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Enhances US1
  - Depends on: US1 parser functions (reuses parseSSEStream)
  - Delivers: Progressive streaming display
  - Independently testable: Can verify streaming works even if US3 not done

- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Enhances US1/US2
  - Depends on: US1 parser and US2 hook (adds error handling)
  - Delivers: User-friendly error messages
  - Independently testable: Can simulate errors and verify messages

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD)
- Parser functions before hook implementation
- Hook implementation before component updates
- Component updates before integration tests
- Story complete and validated before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**: All 3 tasks can run in parallel
```bash
Task T001: Verify dependencies
Task T002: Set up test environment
Task T003: Configure TypeScript
```

**Phase 2 (Foundational)**: Tasks T005-T006 can run in parallel after T004
```bash
Task T004: Create type definitions (MUST complete first)
Then parallel:
  Task T005: Create type guards
  Task T006: Validate TypeScript
```

**Phase 3 (User Story 1)**: All tests (T007-T015) can run in parallel
```bash
# Write all tests together:
Task T007: Test parseSSELine
Task T008: Test parseSSEEvent
Task T009: Test extractTextContent
Task T010: Test filterMetadata
Task T011: Test parseSSEStream
Task T012-T015: Test cases
```

**Phase 4 (User Story 2)**: All tests (T026-T032) can run in parallel
```bash
# Write all tests together:
Task T026: Test connection management
Task T027: Test stream reading
Task T028: Test text accumulation
Task T029: Test cleanup
Task T030-T032: Test cases
```

**Phase 5 (User Story 3)**: All tests (T043-T048) can run in parallel
```bash
# Write all tests together:
Task T043: Test error handling in parser
Task T044: Test error handling in hook
Task T045-T048: Test cases
```

**Phase 6 (Polish)**: Most tasks (T056-T066) can run in parallel
```bash
# All edge case tests and improvements:
Task T056: Special characters test
Task T057: Long messages test
Task T058: Rapid succession test
Task T059: Empty responses test
Task T060: Interrupted connection test
Task T061: Accessibility verification
Task T062: Performance benchmark
Task T063: Browser compatibility
Task T064: Update CustomChatInterface
Task T065: Code review
Task T066: JSDoc comments
```

---

## Parallel Example: User Story 1

```bash
# Step 1: Write all tests in parallel (TDD)
Task: "Unit test for parseSSELine() in frontend/__tests__/lib/sse-parser.test.ts"
Task: "Unit test for parseSSEEvent() in frontend/__tests__/lib/sse-parser.test.ts"
Task: "Unit test for extractTextContent() in frontend/__tests__/lib/sse-parser.test.ts"
Task: "Unit test for filterMetadata() in frontend/__tests__/lib/sse-parser.test.ts"
Task: "Unit test for parseSSEStream() in frontend/__tests__/lib/sse-parser.test.ts"
Task: "Test case: verify data: prefixes removed"
Task: "Test case: verify event: markers removed"
Task: "Test case: verify thread_id separated"
Task: "Test case: verify multi-line data combined"

# Step 2: Implement parser functions sequentially (dependencies)
Task: "Implement parseSSELine() in frontend/lib/sse-parser.ts"
Task: "Implement parseSSEEvent() in frontend/lib/sse-parser.ts"
Task: "Implement extractTextContent() in frontend/lib/sse-parser.ts"
Task: "Implement filterMetadata() in frontend/lib/sse-parser.ts"
Task: "Implement parseSSEStream() in frontend/lib/sse-parser.ts"

# Step 3: Update components and test
Task: "Create MessageDisplay component in frontend/components/MessageDisplay.tsx"
Task: "Update ChatInterface in frontend/components/ChatInterface.tsx"
Task: "Integration test in frontend/__tests__/components/ChatInterface.test.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T006) - CRITICAL
3. Complete Phase 3: User Story 1 (T007-T025)
4. **STOP and VALIDATE**: Test User Story 1 independently
   - Send chat message
   - Verify clean text displays
   - Verify no "data:", "event:", or thread_id visible
5. Deploy/demo if ready - **Chat is now usable!**

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP! ✅)
3. Add User Story 2 → Test independently → Deploy/Demo (Streaming! ✅)
4. Add User Story 3 → Test independently → Deploy/Demo (Error handling! ✅)
5. Add Polish → Final validation → Deploy/Demo (Production ready! ✅)
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T006)
2. Once Foundational is done:
   - Developer A: User Story 1 (T007-T025) - Core parsing
   - Developer B: User Story 2 (T026-T042) - Streaming (can start in parallel)
   - Developer C: User Story 3 (T043-T055) - Errors (can start in parallel)
3. Stories complete and integrate independently
4. Team completes Polish together (T056-T070)

---

## Task Summary

**Total Tasks**: 70
- Phase 1 (Setup): 3 tasks
- Phase 2 (Foundational): 3 tasks (BLOCKING)
- Phase 3 (User Story 1 - MVP): 19 tasks (9 tests + 10 implementation)
- Phase 4 (User Story 2): 17 tasks (7 tests + 10 implementation)
- Phase 5 (User Story 3): 13 tasks (6 tests + 7 implementation)
- Phase 6 (Polish): 15 tasks

**Parallel Opportunities**: 45 tasks marked [P] can run in parallel within their phase

**Independent Test Criteria**:
- US1: Send message → Verify clean text without protocol artifacts
- US2: Send message → Verify progressive streaming display
- US3: Simulate error → Verify user-friendly error message

**Suggested MVP Scope**: Phase 1 + Phase 2 + Phase 3 (User Story 1 only) = 25 tasks

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- TDD approach: Write tests first, verify they fail, then implement
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All tasks follow strict checklist format with IDs, labels, and file paths
- Frontend-only changes - no backend modifications required
