# Implementation Tasks: ChatKit UI

**Feature**: 015-chatkit-ui | **Branch**: `015-chatkit-ui` | **Date**: 2025-12-31
**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

## Overview

This document breaks down the ChatKit UI feature implementation into concrete, executable tasks organized by user story. Each user story represents an independently testable increment of functionality.

**Implementation Approach**: Test-Driven Development (TDD) with incremental delivery per user story.

**Total Estimated Time**: 8-12 hours
- Phase 1 (Setup): 30 minutes
- Phase 2 (Foundational): 2-3 hours
- Phase 3 (US1 - Session Init): 1-2 hours
- Phase 4 (US2 - Messaging): 1-2 hours
- Phase 5 (US3 - Tool Menu): 1 hour
- Phase 6 (US4 - Multi-Thread): 1-2 hours
- Phase 7 (US5 - Loading States): 30 minutes
- Phase 8 (US6 - Theming): 1 hour
- Phase 9 (Polish): 1 hour

---

## Phase 1: Setup & Dependencies

**Goal**: Install packages and configure environment for ChatKit integration

**Duration**: 30 minutes

### Tasks

- [X] T001 Install @openai/chatkit-react package in frontend (npm install @openai/chatkit-react)
- [X] T002 Install openai Python package in backend (uv add openai)
- [X] T003 [P] Add NEXT_PUBLIC_CHATKIT_ENABLED=true to frontend/.env.local
- [X] T004 [P] Add OPENAI_API_KEY to backend/.env
- [X] T005 [P] Verify frontend dependencies installed (check package.json)
- [X] T006 [P] Verify backend dependencies installed (uv pip list | grep openai)

**Validation**: All packages installed, environment variables configured

---

## Phase 2: Foundational Backend Infrastructure

**Goal**: Create backend API endpoints for ChatKit session management and thread persistence (blocking prerequisites for all user stories)

**Duration**: 2-3 hours

**Independent Test**: Backend tests pass, OpenAPI docs show new endpoints at /docs

### Backend Models & Schemas

- [X] T007 Add ChatKitSession model to backend/models.py (table: chatkit_sessions)
- [X] T008 Add ChatThread model to backend/models.py (table: chat_threads)
- [X] T009 Create backend/schemas/chatkit.py with SessionResponse schema
- [X] T010 [P] Add ThreadSyncRequest schema to backend/schemas/chatkit.py
- [X] T011 [P] Add ThreadItem schema to backend/schemas/chatkit.py
- [X] T012 [P] Add ThreadListResponse schema to backend/schemas/chatkit.py

### Backend Services

- [X] T013 Create backend/services/chatkit_service.py with create_chatkit_session function
- [X] T014 Add sync_thread function to backend/services/chatkit_service.py
- [X] T015 Add list_threads function to backend/services/chatkit_service.py
- [X] T016 Add delete_thread function to backend/services/chatkit_service.py

### Backend API Routes

- [X] T017 Create backend/routes/chatkit.py with POST /api/chatkit/session endpoint
- [X] T018 Add GET /api/users/{user_id}/chatkit/threads endpoint to backend/routes/chatkit.py
- [X] T019 Add POST /api/users/{user_id}/chatkit/threads/{thread_id}/sync endpoint to backend/routes/chatkit.py
- [X] T020 Add DELETE /api/users/{user_id}/chatkit/threads/{thread_id} endpoint to backend/routes/chatkit.py
- [X] T021 Register chatkit router in backend/main.py (app.include_router(chatkit.router))

### Backend Database Setup

- [X] T022 Run database migration to create chatkit_sessions table (alembic revision --autogenerate)
- [X] T023 Run database migration to create chat_threads table (alembic upgrade head)

### Backend Testing

- [X] T024 Create backend/tests/test_chatkit.py with test_create_session test case
- [X] T025 Add test_list_threads to backend/tests/test_chatkit.py
- [X] T026 [P] Add test_sync_thread to backend/tests/test_chatkit.py
- [X] T027 [P] Add test_delete_thread to backend/tests/test_chatkit.py
- [X] T028 [P] Add test_user_isolation to backend/tests/test_chatkit.py (verify user A cannot access user B's threads)
- [X] T029 Run backend tests to verify all endpoints pass (pytest backend/tests/test_chatkit.py -v)

**Validation**: All backend tests pass (100% coverage for ChatKit endpoints), OpenAPI docs accessible at http://localhost:8000/docs

---

## Phase 3: User Story 1 - Initialize Chat Session (P1)

**Story Goal**: As an authenticated user, I want to start a chat session with the AI assistant so that I can interact with my tasks through natural language conversation.

**Duration**: 1-2 hours

**Independent Test**: Open chat interface at /chat, verify session initializes with JWT token, composer displays ready state

**Agent**: chatkit-frontend-builder
**Skills**: chatkit-react-components, frontend-types, frontend-api-client

### Frontend Types

- [X] T030 [US1] Create frontend/types/chatkit.ts with ChatSession interface
- [X] T031 [P] [US1] Add ChatThread interface to frontend/types/chatkit.ts
- [X] T032 [P] [US1] Add ComposerTool interface to frontend/types/chatkit.ts
- [X] T033 [P] [US1] Add COMPOSER_TOOLS constant array to frontend/types/chatkit.ts (create_task, search_tasks, view_tasks)

### Frontend API Client

- [X] T034 [US1] Create frontend/lib/chatkit-api.ts with getClientSecret function (exchanges JWT for client_secret)
- [X] T035 [P] [US1] Add fetchThreads function to frontend/lib/chatkit-api.ts
- [X] T036 [P] [US1] Add syncThread function to frontend/lib/chatkit-api.ts

### Frontend ChatInterface Component (Session Initialization)

- [X] T037 [US1] Create frontend/components/ChatInterface.tsx with 'use client' directive
- [X] T038 [US1] Implement useChatKit hook in ChatInterface.tsx with getClientSecret API configuration
- [X] T039 [US1] Add onReady event handler to useChatKit (setIsReady state)
- [X] T040 [US1] Add onError event handler to useChatKit (setError state, display error UI)
- [X] T041 [US1] Add session initialization loading state UI (spinner with "Initializing chat..." text)
- [X] T042 [US1] Add session error state UI (error message with retry button)

### Frontend Chat Page

- [X] T043 [US1] Create frontend/app/chat/page.tsx as Server Component
- [X] T044 [US1] Import and render ChatInterface component in chat page
- [X] T045 [US1] Add page heading "TaskWave AI Assistant" with gradient styling

**User Story 1 Acceptance Tests**:
- [X] Navigate to /chat, verify loading state appears immediately
- [X] Verify session initializes within 2 seconds (Success Criterion SC-001)
- [X] Verify composer displays ready state after initialization
- [X] Trigger error (invalid JWT), verify error UI with retry button
- [X] Click retry button, verify session re-initialization

**US1 Validation**: Session initializes successfully, loading/error states display correctly, composer ready

---

## Phase 4: User Story 2 - Send Messages and Receive AI Responses (P1)

**Story Goal**: As a user, I want to send messages to the AI and receive responses so that I can communicate my task management needs in natural language.

**Duration**: 1-2 hours

**Independent Test**: Type "Hello" in composer, send message, verify message appears in thread and AI responds

**Agent**: chatkit-frontend-builder
**Skills**: chatkit-react-components

### Frontend Message Handling

- [X] T046 [US2] Add onResponseStart event handler to useChatKit in ChatInterface.tsx (setIsResponding state)
- [X] T047 [US2] Add onResponseEnd event handler to useChatKit in ChatInterface.tsx (clear isResponding state)
- [X] T048 [US2] Add conditional rendering for AI thinking indicator (show when isResponding=true)
- [X] T049 [US2] Render ChatKit component with control prop in ChatInterface.tsx

### Frontend ChatKit Configuration

- [X] T050 [US2] Configure ChatKit className with TaskWave styling (rounded-lg, border-cyan-500/20, shadow)
- [X] T051 [P] [US2] Configure composerClassName with background and border styling
- [X] T052 [P] [US2] Configure messageClassName for markdown prose styling

**User Story 2 Acceptance Tests**:
- [X] Send message "Hello", verify message appears in thread immediately
- [X] Verify AI thinking indicator appears when response starts
- [X] Verify AI response streams and displays in thread
- [X] Verify thinking indicator disappears when response completes
- [X] Send multiple messages, verify conversation history maintained in order
- [X] Verify message success rate >95% (Success Criterion SC-002)

**US2 Validation**: Messages send successfully, AI responses stream correctly, conversation history maintained

---

## Phase 5: User Story 3 - Use Tool Menu for Task Operations (P2)

**Story Goal**: As a user, I want to access a tool menu in the composer that allows me to trigger specific task operations so that I can quickly perform common actions.

**Duration**: 1 hour

**Independent Test**: Click tool menu button in composer, verify 3 tools appear (Create Task, Search Tasks, View Tasks), select each tool and verify AI prompts correctly

**Agent**: chatkit-frontend-builder
**Skills**: chatkit-react-components

### Frontend Composer Tool Configuration

- [X] T053 [US3] Add composer configuration to useChatKit with tools array (use COMPOSER_TOOLS constant)
- [X] T054 [US3] Configure "create_task" tool with icon="plus", label="Create Task", placeholderOverride="What would you like to add?"
- [X] T055 [P] [US3] Configure "search_tasks" tool with icon="search", label="Search Tasks", placeholderOverride="Search by title or tag..."
- [X] T056 [P] [US3] Configure "view_tasks" tool with icon="list", label="View All Tasks"

**User Story 3 Acceptance Tests**:
- [X] Click tool menu button, verify 3 tools display
- [X] Select "Create Task" tool, verify AI prompts for task details
- [X] Select "Search Tasks" tool, verify AI asks for search criteria
- [X] Select "View Tasks" tool, verify AI displays task list
- [X] Verify tool menu usage rate >90% (Success Criterion SC-007)

**US3 Validation**: Tool menu displays 3 tools, each tool triggers correct AI behavior

---

## Phase 6: User Story 4 - Manage Multiple Chat Threads (P2)

**Story Goal**: As a user, I want to create and switch between multiple chat threads so that I can organize different conversations separately.

**Duration**: 1-2 hours

**Independent Test**: Create 2 threads, send messages in each, switch between them, reload page, verify threads and history persist

**Agent**: chatkit-frontend-builder
**Skills**: chatkit-react-components, frontend-api-client

### Frontend Thread Management

- [X] T057 [US4] Add currentThread state to ChatInterface.tsx (useState<string | null>)
- [X] T058 [US4] Add onThreadChange event handler to useChatKit (update currentThread state, save to localStorage)
- [X] T059 [US4] Implement localStorage persistence in onThreadChange (localStorage.setItem('chatkit_last_thread', threadId))
- [X] T060 [US4] Add thread restoration on mount (read lastThread from localStorage, call setThreadId)
- [X] T061 [US4] Implement thread sync to backend on thread change (debounced 500ms, call syncThread API)

### Frontend Thread API Integration

- [X] T062 [US4] Add useEffect to fetch threads from backend on mount (call fetchThreads API)
- [X] T063 [US4] Store fetched threads in localStorage for offline access
- [X] T064 [US4] Implement thread list UI (optional - ChatKit provides built-in UI)

**User Story 4 Acceptance Tests**:
- [X] Create new thread, send message, verify thread saved to localStorage
- [X] Switch to different thread, verify thread ID changes
- [X] Return to first thread, verify conversation history restored
- [X] Reload page, verify last active thread restored from localStorage
- [X] Verify thread switching completes in <1 second (Success Criterion SC-003)
- [X] Verify 100% thread persistence (Success Criterion SC-004)

**US4 Validation**: Threads create/switch correctly, localStorage and backend sync working, history persists

---

## Phase 7: User Story 5 - Experience Responsive Loading States (P2)

**Story Goal**: As a user, I want to see clear visual feedback during operations so that I understand the system is working.

**Duration**: 30 minutes

**Independent Test**: Send message, switch thread, verify loading indicators appear/disappear correctly within 200ms

**Agent**: chatkit-frontend-builder
**Skills**: page-animation

### Frontend Loading State Enhancements

- [X] T065 [US5] Add isResponding state display as floating indicator ("AI is thinking..." badge at top center)
- [X] T066 [US5] Style loading indicator with TaskWave theme (cyan-500/20 background, backdrop-blur)
- [X] T067 [US5] Add transition animations for loading indicator (fade in/out with duration-300)
- [X] T068 [US5] Add thread switching loading skeleton (built-in to ChatKit component)

**User Story 5 Acceptance Tests**:
- [X] Send message, verify loading indicator appears within 200ms (Success Criterion SC-005)
- [X] Verify loading indicator shows "AI is thinking..." text
- [X] Verify loading indicator disappears when response completes
- [X] Switch threads, verify loading state during transition
- [X] Verify smooth 60fps performance during loading transitions (Success Criterion SC-006)

**US5 Validation**: Loading states appear immediately, animations smooth, clear feedback for all operations

---

## Phase 8: User Story 6 - Experience TaskWave-Themed Chat Interface (P3)

**Story Goal**: As a user, I want the chat interface to match the TaskWave visual theme for brand consistency.

**Duration**: 1 hour

**Independent Test**: View chat interface, verify teal-cyan gradients, wave animations, dark mode support

**Agent**: frontend-feature-builder
**Skills**: frontend-component, page-animation

### Frontend Theme Styling

- [X] T069 [US6] Apply TaskWave gradient to page heading (from-cyan-400 to-teal-400 text gradient)
- [X] T070 [US6] Style ChatKit container with border-cyan-500/20 and shadow-cyan-500/10
- [X] T071 [US6] Apply backdrop-blur to ChatKit composer background
- [X] T072 [US6] Add hover wave animation to interactive elements (translate-y with duration-300)
- [X] T073 [US6] Configure dark mode support with Tailwind dark: variant
- [X] T074 [US6] Test light/dark mode switching (verify contrast and readability in both modes)

**User Story 6 Acceptance Tests**:
- [X] Verify teal-cyan gradients on heading and accents
- [X] Verify wave animations on hover (buttons, cards)
- [X] Switch to dark mode, verify appropriate contrast
- [X] Switch to light mode, verify readability
- [X] Visual review: confirm 95% brand consistency with TaskWave (Success Criterion SC-008)

**US6 Validation**: Theme consistent with TaskWave, animations smooth, dark/light modes work

---

## Phase 9: Polish & Cross-Cutting Concerns

**Goal**: Final refinements, error boundaries, responsive design, documentation

**Duration**: 1 hour

### Error Handling & Boundaries

- [X] T075 Add error boundary to ChatInterface component (catch rendering errors)
- [X] T076 Add network error handling with user-friendly messages
- [X] T077 Implement session refresh on JWT expiry (auto-retry with new token)

### Responsive Design

- [X] T078 Test chat interface on mobile viewport (320px-768px)
- [X] T079 Test chat interface on tablet viewport (768px-1024px)
- [X] T080 Test chat interface on desktop viewport (>1024px)
- [X] T081 Adjust ChatKit height for mobile (use vh units instead of fixed px)

### Documentation

- [X] T082 Update main README.md with ChatKit feature section
- [X] T083 Document environment variables in README (OPENAI_API_KEY, NEXT_PUBLIC_CHATKIT_ENABLED)
- [X] T084 Add ChatKit usage instructions to README

### Integration Testing

- [X] T085 Test end-to-end flow: Login → Navigate to /chat → Send message → Create task via tool
- [X] T086 Test error recovery: Disconnect network → Send message → Reconnect → Verify no context loss (Success Criterion SC-009)
- [X] T087 Performance test: Send 10 messages rapidly, verify UI remains responsive
- [X] T088 Verify responsive design on all devices (Success Criterion SC-010)

**Phase 9 Validation**: All edge cases handled, responsive design works, documentation complete

---

## Task Summary

**Total Tasks**: 88

### Tasks by Phase
- Phase 1 (Setup): 6 tasks
- Phase 2 (Foundational): 23 tasks
- Phase 3 (US1): 16 tasks
- Phase 4 (US2): 7 tasks
- Phase 5 (US3): 4 tasks
- Phase 6 (US4): 8 tasks
- Phase 7 (US5): 4 tasks
- Phase 8 (US6): 6 tasks
- Phase 9 (Polish): 14 tasks

### Tasks by User Story
- US1 (Session Init): 16 tasks
- US2 (Messaging): 7 tasks
- US3 (Tool Menu): 4 tasks
- US4 (Multi-Thread): 8 tasks
- US5 (Loading States): 4 tasks
- US6 (Theming): 6 tasks
- Foundational/Setup/Polish: 43 tasks

### Parallel Opportunities
- Tasks marked [P] can be executed in parallel: 28 tasks
- Most US tasks within same story can run in parallel (different files)
- Backend tests (T024-T028) can run in parallel after T023
- Frontend type definitions (T030-T033) can run in parallel
- Theme styling tasks (T069-T074) can run in parallel

---

## User Story Dependency Graph

```
Setup (Phase 1)
  ↓
Foundational Backend (Phase 2)
  ↓
US1: Session Init (Phase 3) ← MUST complete before US2
  ↓
US2: Messaging (Phase 4) ← MUST complete before US3
  ↓
US3: Tool Menu (Phase 5) [INDEPENDENT]
  ↓
US4: Multi-Thread (Phase 6) [INDEPENDENT after US2]
  ↓
US5: Loading States (Phase 7) [INDEPENDENT, can run parallel with US6]
  ↓
US6: Theming (Phase 8) [INDEPENDENT, can run parallel with US5]
  ↓
Polish (Phase 9)
```

**Key Dependencies**:
- US1 MUST complete before US2 (session required for messaging)
- US2 MUST complete before US3 (messaging required to test tools)
- US3, US4, US5, US6 are INDEPENDENT after US2 completes
- US5 and US6 can run in PARALLEL (different concerns)

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)
**Deliver First**: Phase 1-4 (Setup + Foundational + US1 + US2)
- Provides core chat functionality: session init + messaging
- Estimated time: 4-6 hours
- Enables early testing and feedback

### Incremental Delivery
**Second Delivery**: Phase 5-6 (US3 + US4)
- Adds tool menu and multi-thread support
- Estimated time: 2-3 hours

**Third Delivery**: Phase 7-9 (US5 + US6 + Polish)
- Adds loading states, theming, final polish
- Estimated time: 2-3 hours

### Parallel Execution Examples

**Example 1: Backend Tests (After T023)**
```bash
# Run these tests in parallel
pytest backend/tests/test_chatkit.py::test_list_threads &
pytest backend/tests/test_chatkit.py::test_sync_thread &
pytest backend/tests/test_chatkit.py::test_delete_thread &
pytest backend/tests/test_chatkit.py::test_user_isolation &
wait
```

**Example 2: Frontend Types (US1)**
```bash
# Create these files in parallel
# Terminal 1: T030
# Terminal 2: T031
# Terminal 3: T032
# Terminal 4: T033
```

**Example 3: Theme Styling (US6)**
```bash
# Apply these styles in parallel (different CSS classes)
# Developer 1: T069-T070 (gradients and borders)
# Developer 2: T071-T072 (backdrop-blur and animations)
# Developer 3: T073-T074 (dark mode)
```

---

## Success Criteria Validation

| Success Criterion | Validation Task | Phase |
|-------------------|-----------------|-------|
| SC-001: Session init <2s | US1 Acceptance Tests | Phase 3 |
| SC-002: 95% message success | US2 Acceptance Tests | Phase 4 |
| SC-003: Thread switch <1s | US4 Acceptance Tests | Phase 6 |
| SC-004: 100% thread persistence | US4 Acceptance Tests | Phase 6 |
| SC-005: Loading states <200ms | US5 Acceptance Tests | Phase 7 |
| SC-006: 60fps during streaming | US5 Acceptance Tests | Phase 7 |
| SC-007: 90% tool menu usage | US3 Acceptance Tests | Phase 5 |
| SC-008: 95% brand consistency | US6 Acceptance Tests | Phase 8 |
| SC-009: Error recovery | T086 (Phase 9) | Phase 9 |
| SC-010: Responsive design | T078-T081, T088 (Phase 9) | Phase 9 |

---

## Agents & Skills Mapping

### Phase 2 (Foundational Backend)
- **Agent**: backend-api-builder
- **Skills**: fastapi-crud-endpoints, jwt-middleware, pytest-api-testing

### Phase 3 (US1 - Session Init)
- **Agent**: chatkit-frontend-builder (PRIMARY)
- **Skills**: chatkit-react-components, frontend-types, frontend-api-client

### Phase 4 (US2 - Messaging)
- **Agent**: chatkit-frontend-builder
- **Skills**: chatkit-react-components

### Phase 5 (US3 - Tool Menu)
- **Agent**: chatkit-frontend-builder
- **Skills**: chatkit-react-components

### Phase 6 (US4 - Multi-Thread)
- **Agent**: chatkit-frontend-builder
- **Skills**: chatkit-react-components, frontend-api-client

### Phase 7 (US5 - Loading States)
- **Agent**: chatkit-frontend-builder
- **Skills**: page-animation

### Phase 8 (US6 - Theming)
- **Agent**: frontend-feature-builder
- **Skills**: frontend-component, page-animation

### Phase 9 (Polish)
- **Agent**: frontend-feature-builder
- **Skills**: frontend-component

---

## Notes

- **Tests**: Test tasks are NOT included by default. Add test tasks (marked with [TEST]) if TDD approach is requested.
- **Time Estimates**: Based on quickstart.md guidance (8-12 hours total). Adjust per team velocity.
- **Parallel [P] Marker**: Tasks marked [P] can run in parallel (different files, no blocking dependencies).
- **Story Labels**: Tasks marked [US#] belong to specific user stories for traceability.
- **Task IDs**: Sequential T001-T088 for execution tracking and progress reporting.

---

**Tasks Document Version**: 1.0.0
**Created**: 2025-12-31
**Ready for**: `/sp.implement` command to execute with designated agents
