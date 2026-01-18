# Implementation Tasks: ChatKit Frontend-Backend Integration

**Feature**: 017-chatkit-integration | **Branch**: `017-chatkit-integration` | **Date**: 2026-01-01
**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

## Overview

This document breaks down the ChatKit Frontend-Backend Integration feature implementation into concrete, executable tasks organized by user story. Each user story represents an independently testable increment of functionality.

**Implementation Approach**: Test-Driven Development (TDD) with incremental delivery per user story.

**Total Estimated Time**: 12-18 hours
- Phase 1 (Setup): 1 hour
- Phase 2 (Foundational): 3-4 hours
- Phase 3 (US1 - AI Responses): 2-3 hours
- Phase 4 (US2 - Task Sync): 2-3 hours
- Phase 5 (US3 - Tools): 1-2 hours
- Phase 6 (US4 - Session Auth): 1-2 hours
- Phase 7 (US5 - UI Feedback): 1 hour
- Phase 8 (Polish): 1-2 hours

---

## Phase 1: Setup & Dependencies

**Goal**: Install packages and configure environment for ChatKit integration

**Duration**: 1 hour

### Tasks

- [X] T001 Install @openai/chatkit-react package in frontend (npm install @openai/chatkit-react)
- [X] T002 Install openai Python package in backend (uv add openai)
- [X] T003 [P] Add NEXT_PUBLIC_CHATKIT_URL=http://localhost:8000/api/chatkit to frontend/.env
- [X] T004 [P] Add OPENAI_API_KEY to backend/.env
- [X] T005 [P] Verify frontend dependencies installed (check package.json)
- [X] T006 [P] Verify backend dependencies installed (uv pip list | grep openai)

**Validation**: All packages installed, environment variables configured

---

## Phase 2: Foundational Backend Infrastructure

**Goal**: Create backend API endpoints for ChatKit session management and thread persistence (blocking prerequisites for all user stories)

**Duration**: 3-4 hours

**Independent Test**: Backend tests pass, OpenAPI docs show new endpoints at /docs

### Backend Models & Schemas

- [X] T007 Add ChatSession model to backend/models.py (table: chat_sessions)  # Already exists as ChatKitSession
- [X] T008 Add ChatThread model to backend/models.py (table: chat_threads)   # Already exists
- [X] T009 Add ChatMessage model to backend/models.py (table: chat_messages) # Already exists
- [X] T010 [P] Add ClientEffectEvent model to backend/models.py (table: client_effects)
- [X] T011 [P] Add ChatTool model to backend/models.py (table: chat_tools)
- [X] T012 [P] Create backend/schemas/chatkit.py with SessionResponse schema

### Backend Services

- [X] T013 Create backend/services/chatkit_service.py with create_chatkit_session function
- [X] T014 Add create_thread function to backend/services/chatkit_service.py
- [X] T015 Add get_thread function to backend/services/chatkit_service.py
- [X] T016 [P] Add save_thread function to backend/services/chatkit_service.py
- [X] T017 [P] Add list_threads function to backend/services/chatkit_service.py
- [X] T018 [P] Add send_message function to backend/services/chatkit_service.py

### Backend API Routes

- [X] T019 Create backend/routes/chatkit.py with POST /api/chatkit/session endpoint
- [X] T020 Add GET /api/users/{user_id}/chat/threads endpoint to backend/routes/chatkit.py
- [X] T021 Add POST /api/users/{user_id}/chat/threads endpoint to backend/routes/chatkit.py
- [X] T022 [P] Add POST /api/users/{user_id}/chat/messages endpoint to backend/routes/chatkit.py
- [X] T023 [P] Add GET /api/users/{user_id}/chat/messages endpoint to backend/routes/chatkit.py
- [X] T024 [P] Register chatkit router in backend/main.py (app.include_router(chatkit.router))  # Already registered

### Backend Database Setup

- [X] T025 Run database migration to create chat_sessions table (alembic revision --autogenerate)
- [X] T026 Run database migration to create chat_threads table (alembic upgrade head)
- [X] T027 [P] Run database migration to create chat_messages table (alembic upgrade head)
- [X] T028 [P] Run database migration to create client_effects table (alembic upgrade head)

### Backend Testing

- [ ] T029 Create backend/tests/test_chatkit.py with test_create_session test case
- [ ] T030 Add test_list_threads to backend/tests/test_chatkit.py
- [ ] T031 [P] Add test_create_thread to backend/tests/test_chatkit.py
- [ ] T032 [P] Add test_send_message to backend/tests/test_chatkit.py
- [ ] T033 [P] Add test_user_isolation to backend/tests/test_chatkit.py (verify user A cannot access user B's threads)
- [ ] T034 Run backend tests to verify all endpoints pass (pytest backend/tests/test_chatkit.py -v)

**Validation**: All backend tests pass (100% coverage for ChatKit endpoints), OpenAPI docs accessible at http://localhost:8000/docs

---

## Phase 3: User Story 1 - Send Messages and Receive AI Responses (P1)

**Story Goal**: As an authenticated user, I want to send messages to the AI assistant and receive intelligent responses so that I can manage my tasks through natural language conversation.

**Duration**: 2-3 hours

**Independent Test**: Open chat interface at /chat, send message "Create a task to buy groceries", verify AI responds appropriately and creates the task

**Agent**: chatkit-frontend-builder
**Skills**: chatkit-react-components, frontend-types, frontend-api-client

### Frontend ChatInterface Enhancement

- [ ] T035 [US1] Update frontend/components/ChatInterface.tsx with proper API configuration for session endpoint
- [ ] T036 [US1] Implement getClientSecret API call to POST /api/chatkit/session
- [ ] T037 [US1] Add onMessage handler to process AI responses
- [ ] T038 [US1] Configure streaming responses from AI backend
- [ ] T039 [US1] Add loading state for AI processing ("AI is thinking..." indicator)

### Frontend Chat Page

- [ ] T040 [US1] Update frontend/app/chat/page.tsx to handle session initialization
- [ ] T041 [US1] Add error handling for session initialization failures
- [ ] T042 [US1] Implement proper authentication token passing

### Backend AI Integration

- [ ] T043 [US1] Create backend/ai_agents/taskwave_agent.py with TaskWaveAgent implementation
- [ ] T044 [US1] Implement AI response streaming in backend/routes/chatkit.py
- [ ] T045 [US1] Connect to OpenAI Agents SDK for natural language processing

### User Story 1 Acceptance Tests:

- [ ] Send message "Hello", verify AI responds appropriately
- [ ] Send message "Create a task to buy groceries", verify AI responds and creates task
- [ ] Verify AI responses appear within 5 seconds (Success Criterion SC-001)
- [ ] Verify loading indicators appear during AI processing
- [ ] Send multiple messages, verify conversation history maintained

**US1 Validation**: Messages send successfully, AI responses stream correctly, conversation history maintained

---

## Phase 4: User Story 2 - Experience Task List Synchronization (P1)

**Story Goal**: As a user, I want the task list to automatically update when I perform task operations through the chat so that I see consistent information across the UI without manual refresh.

**Duration**: 2-3 hours

**Independent Test**: Create a task via chat, immediately see it appear in the task list without manual refresh

**Agent**: chatkit-frontend-builder
**Skills**: chatkit-react-components, frontend-api-client

### Frontend Task List Synchronization

- [ ] T046 [US2] Add refetchTasks function to ChatInterface component
- [ ] T047 [US2] Implement onClientEffect handler in ChatInterface for task events
- [ ] T048 [US2] Handle task_created event to update task list
- [ ] T049 [US2] Handle task_updated event to update specific task
- [ ] T050 [US2] Handle task_deleted event to remove from task list
- [ ] T051 [US2] Handle task_completed event to update completion status

### Frontend Task Context Integration

- [ ] T052 [US2] Connect ChatInterface to TaskList context or state management
- [ ] T053 [US2] Implement optimistic updates with rollback capability
- [ ] T054 [US2] Add success notifications for task operations

### Backend Client Effect Events

- [ ] T055 [US2] Add client effect event emission in backend/services/chatkit_service.py
- [ ] T056 [US2] Emit task_created event when tasks are created via chat
- [ ] T057 [US2] Emit task_updated event when tasks are updated via chat
- [ ] T058 [US2] Emit task_deleted event when tasks are deleted via chat
- [ ] T059 [US2] Emit task_completed event when tasks are completed via chat

### User Story 2 Acceptance Tests:

- [ ] Create task via chat, verify it appears in task list automatically
- [ ] Update task via chat, verify it updates in task list automatically
- [ ] Complete task via chat, verify it shows as completed in task list
- [ ] Task list updates within 1 second (Success Criterion SC-002)
- [ ] Verify no manual refresh required for updates

**US2 Validation**: Task list updates automatically without manual refresh, optimistic updates working

---

## Phase 5: User Story 3 - Use Contextual Tools in Chat (P2)

**Story Goal**: As a user, I want to access contextual tools in the chat composer that allow me to perform specific task operations so that I can quickly manage my tasks without typing full commands.

**Duration**: 1-2 hours

**Independent Test**: Click tool menu button in composer, verify 4 tools appear (Create Task, Search Tasks, View Tasks, Analytics), select each tool and verify AI prompts correctly

**Agent**: chatkit-frontend-builder
**Skills**: chatkit-react-components

### Frontend Composer Tool Configuration

- [ ] T060 [US3] Add composer configuration to ChatInterface with tools array
- [ ] T061 [US3] Configure "create_task" tool with icon="plus", label="Create Task", placeholderOverride="What would you like to add?"
- [ ] T062 [P] [US3] Configure "search_tasks" tool with icon="search", label="Search Tasks", placeholderOverride="Search by title or tag..."
- [ ] T063 [P] [US3] Configure "list_tasks" tool with icon="list", label="View All Tasks"
- [ ] T064 [P] [US3] Configure "analytics" tool with icon="bar-chart", label="Statistics"

### Frontend Example Prompts

- [ ] T065 [US3] Add example prompts to ChatInterface when chat is empty
- [ ] T066 [US3] Show prompts: 'Create a task for my meeting tomorrow', 'Show me all urgent tasks', 'What tasks do I have this week?', 'Mark my report task as complete'

### Backend Tool Integration

- [ ] T067 [US3] Update backend/ai_agents/taskwave_agent.py to handle tool calls
- [ ] T068 [US3] Implement create_task tool function in backend
- [ ] T069 [US3] Implement search_tasks tool function in backend
- [ ] T070 [US3] Implement list_tasks tool function in backend

### User Story 3 Acceptance Tests:

- [ ] Click tool menu button, verify 4 tools display
- [ ] Select "Create Task" tool, verify AI prompts for task details
- [ ] Select "Search Tasks" tool, verify AI asks for search criteria
- [ ] Select "View Tasks" tool, verify AI displays task list
- [ ] Verify 90% of users successfully use contextual tools (Success Criterion SC-003)

**US3 Validation**: Tool menu displays 4 tools, each tool triggers correct AI behavior

---

## Phase 6: User Story 4 - Access Session and Authentication (P2)

**Story Goal**: As an authenticated user, I want to establish a secure chat session that connects to the AI backend so that my conversations are properly authenticated and routed to the correct AI agent.

**Duration**: 1-2 hours

**Independent Test**: Navigate to chat interface, verify secure session established with backend using JWT credentials

**Agent**: backend-api-builder
**Skills**: fastapi-auth-endpoints, jwt-middleware

### Backend Session Endpoint

- [ ] T071 [US4] Implement POST /api/chatkit/session endpoint in backend/routes/chatkit.py
- [ ] T072 [US4] Add JWT authentication validation to session endpoint
- [ ] T073 [US4] Generate client secret from JWT token in session endpoint
- [ ] T074 [US4] Return proper response format with client_secret

### Backend Authentication Integration

- [ ] T075 [US4] Verify session endpoint uses existing Better Auth JWT verification
- [ ] T076 [US4] Add proper error handling for invalid JWT tokens
- [ ] T077 [US4] Implement token expiration checks

### Frontend Session Integration

- [ ] T078 [US4] Update ChatInterface to call POST /api/chatkit/session endpoint
- [ ] T079 [US4] Handle authentication errors gracefully with user redirection
- [ ] T080 [US4] Implement session refresh on JWT expiry

### User Story 4 Acceptance Tests:

- [ ] Navigate to chat interface, verify secure session established
- [ ] Verify session uses valid JWT token
- [ ] Send message with valid session, verify successful communication
- [ ] Test with expired JWT, verify appropriate error and re-authentication prompt
- [ ] Session establishment completes within 2 seconds (Success Criterion SC-010)

**US4 Validation**: Secure session established with proper JWT authentication, errors handled gracefully

---

## Phase 7: User Story 5 - Experience Enhanced UI Feedback (P3)

**Story Goal**: As a user, I want to see clear visual feedback during AI processing, tool operations, and other interactions so that I understand the system is working and know when to wait.

**Duration**: 1 hour

**Independent Test**: Send message, switch thread, verify loading indicators appear/disappear correctly within 200ms

**Agent**: chatkit-frontend-builder
**Skills**: page-animation

### Frontend Loading State Enhancements

- [ ] T081 [US5] Add AI thinking indicator ("AI is thinking..." badge at top center)
- [ ] T082 [US5] Add tool-specific loading indicators ("Creating task...", "Searching...")
- [ ] T083 [US5] Style loading indicators with TaskWave theme (cyan-500/20 background, backdrop-blur)
- [ ] T084 [US5] Add transition animations for loading indicators (fade in/out with duration-300)
- [ ] T085 [US5] Add thread switching loading skeleton

### Frontend Error Handling

- [ ] T086 [US5] Add error boundary to ChatInterface component (catch rendering errors)
- [ ] T087 [US5] Add network error handling with user-friendly messages
- [ ] T088 [US5] Implement rate limiting error handling with appropriate user feedback

### User Story 5 Acceptance Tests:

- [ ] Send message, verify loading indicator appears within 200ms (Success Criterion SC-005)
- [ ] Verify "AI is thinking..." text during response generation
- [ ] Use tool, verify tool-specific loading indicator
- [ ] Trigger rate limiting, verify appropriate feedback
- [ ] Verify 60fps performance during loading transitions (Success Criterion SC-006)

**US5 Validation**: Loading states appear immediately, animations smooth, clear feedback for all operations

---

## Phase 8: Polish & Cross-Cutting Concerns

**Goal**: Final refinements, error boundaries, responsive design, documentation

**Duration**: 1-2 hours

### Error Handling & Boundaries

- [ ] T089 Add error boundary to ChatInterface component (catch rendering errors)
- [ ] T090 Add network error handling with user-friendly messages
- [ ] T091 Implement session refresh on JWT expiry (auto-retry with new token)
- [ ] T092 Handle authentication errors gracefully with 100% user feedback (Success Criterion SC-004)

### Responsive Design

- [ ] T093 Test chat interface on mobile viewport (320px-768px)
- [ ] T094 Test chat interface on tablet viewport (768px-1024px)
- [ ] T095 Test chat interface on desktop viewport (>1024px)
- [ ] T096 Adjust ChatKit height for mobile (use vh units instead of fixed px)

### Documentation

- [ ] T097 Update main README.md with ChatKit integration section
- [ ] T098 Document environment variables in README (OPENAI_API_KEY, NEXT_PUBLIC_CHATKIT_URL)
- [ ] T099 Add ChatKit usage instructions to README

### Integration Testing

- [ ] T100 Test end-to-end flow: Login → Navigate to /chat → Send message → Create task via tool
- [ ] T101 Test error recovery: Disconnect network → Send message → Reconnect → Verify no context loss (Success Criterion SC-009)
- [ ] T102 Performance test: Send 10 messages rapidly, verify UI remains responsive
- [ ] T103 Verify responsive design on all devices (Success Criterion SC-008)
- [ ] T104 Test 95% of users can create task on first attempt (Success Criterion SC-009)

**Phase 8 Validation**: All edge cases handled, responsive design works, documentation complete

---

## Task Summary

**Total Tasks**: 104

### Tasks by Phase
- Phase 1 (Setup): 6 tasks
- Phase 2 (Foundational): 30 tasks
- Phase 3 (US1): 9 tasks
- Phase 4 (US2): 13 tasks
- Phase 5 (US3): 11 tasks
- Phase 6 (US4): 11 tasks
- Phase 7 (US5): 9 tasks
- Phase 8 (Polish): 15 tasks

### Tasks by User Story
- US1 (AI Responses): 9 tasks
- US2 (Task Sync): 13 tasks
- US3 (Tools): 11 tasks
- US4 (Session Auth): 11 tasks
- US5 (UI Feedback): 9 tasks
- Foundational/Setup/Polish: 51 tasks

### Parallel Opportunities
- Tasks marked [P] can be executed in parallel: 28 tasks
- Most US tasks within same story can run in parallel (different files)
- Backend tests (T029-T034) can run in parallel after T028
- Frontend type definitions (T012) can run in parallel with model definitions
- Theme styling tasks can run in parallel
- Error handling tasks (T086-T092) can run in parallel

---

## User Story Dependency Graph

```
Setup (Phase 1)
  ↓
Foundational Backend (Phase 2)
  ↓
US4: Session Auth (Phase 6) ← MUST complete before US1
  ↓
US1: AI Responses (Phase 3) ← MUST complete before US2
  ↓
US2: Task Sync (Phase 4) [INDEPENDENT after US1]
  ↓
US3: Tools (Phase 5) [INDEPENDENT after US1]
  ↓
US5: UI Feedback (Phase 7) [INDEPENDENT, can run parallel with US3]
  ↓
Polish (Phase 8)
```

**Key Dependencies**:
- US4 MUST complete before US1 (session required for chat)
- US1 MUST complete before US2 (AI responses required for task operations)
- US2, US3, US5 are INDEPENDENT after US1 completes
- US3 and US5 can run in PARALLEL (different concerns)

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)
**Deliver First**: Phase 1-3 (Setup + Foundational + US4 + US1)
- Provides core chat functionality: session init + AI messaging
- Estimated time: 6-8 hours
- Enables early testing and feedback

### Incremental Delivery
**Second Delivery**: Phase 4 (US2 - Task Sync)
- Adds task list synchronization
- Estimated time: 2-3 hours

**Third Delivery**: Phase 5-6 (US3 + US5)
- Adds tools and enhanced UI feedback
- Estimated time: 2-3 hours

**Fourth Delivery**: Phase 7-8 (Polish)
- Adds final refinements and testing
- Estimated time: 2-3 hours

### Parallel Execution Examples

**Example 1: Backend Tests (After T028)**
```bash
# Run these tests in parallel
pytest backend/tests/test_chatkit.py::test_list_threads &
pytest backend/tests/test_chatkit.py::test_create_thread &
pytest backend/tests/test_chatkit.py::test_send_message &
pytest backend/tests/test_chatkit.py::test_user_isolation &
wait
```

**Example 2: Frontend Components (US1)**
```bash
# Create these files in parallel
# Terminal 1: T035
# Terminal 2: T036
# Terminal 3: T037
# Terminal 4: T038
```

**Example 3: UI Enhancement (US5)**
```bash
# Apply these enhancements in parallel (different components)
# Developer 1: T081-T082 (loading indicators)
# Developer 2: T083-T085 (styling and animations)
# Developer 3: T086-T088 (error handling)
```

---

## Success Criteria Validation

| Success Criterion | Validation Task | Phase |
|-------------------|-----------------|-------|
| SC-001: AI responses <5s | US1 Acceptance Tests | Phase 3 |
| SC-002: Task sync <1s | US2 Acceptance Tests | Phase 4 |
| SC-003: 90% tool usage | US3 Acceptance Tests | Phase 5 |
| SC-004: Auth error handling | US4, T086-T092 (Phase 8) | Phase 8 |
| SC-005: Loading states <200ms | US5 Acceptance Tests | Phase 7 |
| SC-006: 60fps during streaming | US5 Acceptance Tests | Phase 7 |
| SC-007: 90% task operation success | T100-T104 (Phase 8) | Phase 8 |
| SC-008: Responsive design | T093-T096, T103 (Phase 8) | Phase 8 |
| SC-009: Error recovery | T101 (Phase 8) | Phase 8 |
| SC-010: Session <2s | US4 Acceptance Tests | Phase 6 |

---

## Agents & Skills Mapping

### Phase 2 (Foundational Backend)
- **Agent**: backend-api-builder
- **Skills**: fastapi-crud-endpoints, jwt-middleware, pytest-api-testing

### Phase 3 (US1 - AI Responses)
- **Agent**: chatkit-frontend-builder (PRIMARY)
- **Skills**: chatkit-react-components, frontend-types, frontend-api-client
- **Agent**: backend-api-builder
- **Skills**: openai-agent-tools

### Phase 4 (US2 - Task Sync)
- **Agent**: chatkit-frontend-builder
- **Skills**: chatkit-react-components, frontend-api-client

### Phase 5 (US3 - Tools)
- **Agent**: chatkit-frontend-builder
- **Skills**: chatkit-react-components

### Phase 6 (US4 - Session Auth)
- **Agent**: backend-api-builder
- **Skills**: fastapi-auth-endpoints, jwt-middleware

### Phase 7 (US5 - UI Feedback)
- **Agent**: chatkit-frontend-builder
- **Skills**: page-animation

### Phase 8 (Polish)
- **Agent**: frontend-feature-builder
- **Skills**: frontend-component

---

## Notes

- **Tests**: Test tasks are NOT included by default. Add test tasks (marked with [TEST]) if TDD approach is requested.
- **Time Estimates**: Based on quickstart.md guidance (12-18 hours total). Adjust per team velocity.
- **Parallel [P] Marker**: Tasks marked [P] can run in parallel (different files, no blocking dependencies).
- **Story Labels**: Tasks marked [US#] belong to specific user stories for traceability.
- **Task IDs**: Sequential T001-T104 for execution tracking and progress reporting.

---

**Tasks Document Version**: 1.0.0
**Created**: 2026-01-01
**Ready for**: `/sp.implement` command to execute with designated agents