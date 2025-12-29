# Tasks: Frontend-Backend Integration

**Input**: Design documents from `/specs/013-frontend-backend-integration/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `frontend/` - Next.js app with App Router
- **Backend**: `backend/` - FastAPI app (already complete)
- All frontend paths are relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Environment configuration and shared utilities

- [X] T001 [P] Verify BETTER_AUTH_SECRET is set in frontend/.env.local and matches backend
- [X] T002 [P] Verify API_URL environment variable in frontend/.env.local (default: http://localhost:8000)
- [X] T003 [P] Install required dependencies: Better Auth JWT plugin if not already installed

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core API client and authentication infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Configure Better Auth with JWT plugin in frontend/lib/auth.ts
  - Enable JWT plugin with shared secret (BETTER_AUTH_SECRET)
  - Set token expiration (7 days default)
  - Configure httpOnly cookie storage
  - Add token refresh configuration

- [X] T005 Create centralized API client in frontend/lib/api.ts
  - Base URL from environment (API_URL)
  - Automatic JWT token attachment from Better Auth session
  - Generic request wrapper with error handling
  - Type-safe response parsing

- [X] T006 [P] Create TypeScript types for API responses in frontend/types/api.ts
  - AuthResponse type (user + token)
  - TaskResponse type (matches backend schema)
  - TaskListResponse type (tasks + pagination)
  - UserResponse type (profile data)
  - ErrorResponse type (standardized errors)

- [X] T007 [P] Create error handling utilities in frontend/lib/errors.ts
  - Parse API error responses
  - Map error codes to user-friendly messages
  - Network error detection
  - Token expiration detection

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Authentication Flow (Priority: P1) 🎯 MVP

**Goal**: Users can signup, login, and access protected routes with JWT authentication

**Independent Test**: Complete signup → login → redirect to tasks page → see authenticated content

### Implementation for User Story 1

- [X] T008 [US1] Update Better Auth configuration for signup endpoint in frontend/lib/auth.ts
  - Add signup method calling POST /auth/signup
  - Handle 201 success response
  - Store JWT token on success
  - Handle 409 duplicate email error
  - Handle 422 validation errors

- [X] T009 [US1] Update Better Auth configuration for login endpoint in frontend/lib/auth.ts
  - Add login method calling POST /auth/login
  - Handle 200 success response
  - Store JWT token on success
  - Handle 401 invalid credentials error

- [X] T010 [US1] Update Better Auth configuration for logout endpoint in frontend/lib/auth.ts
  - Add logout method calling POST /auth/logout
  - Clear JWT token from storage
  - Handle 200 success response
  - Redirect to login page

- [X] T011 [US1] Create or update authentication pages in frontend/app/auth/
  - Signup form component with validation
  - Login form component with validation
  - Loading states during API calls
  - Error message display
  - Success redirects

- [X] T012 [US1] Update ProtectedRoute component in frontend/components/ProtectedRoute.tsx
  - Check JWT token validity from Better Auth
  - Redirect to /auth/login if no valid token
  - Show loading spinner during verification
  - Allow access to protected routes if authenticated

- [X] T013 [US1] Handle token expiration globally in frontend/lib/api.ts
  - Detect 401 responses
  - Clear expired token
  - Redirect to login
  - Show "Session expired" message

**Checkpoint**: Users can signup, login, logout, and protected routes are enforced

---

## Phase 4: User Story 2 - Task Management Integration (Priority: P1) 🎯 MVP

**Goal**: Users can create, view, update, and delete tasks with backend persistence

**Independent Test**: Create task → refresh page → task still exists → update task → delete task → all changes persist

### Implementation for User Story 2

- [ ] T014 [P] [US2] Add getTasks method to frontend/lib/api.ts
  - Call GET /users/{user_id}/tasks with JWT
  - Accept optional filters (completed, priority, tag, search, sort, limit, offset)
  - Return TaskListResponse with pagination
  - Handle 401, 403, 404 errors

- [ ] T015 [P] [US2] Add createTask method to frontend/lib/api.ts
  - Call POST /users/{user_id}/tasks with JWT
  - Send title, description, priority, tags
  - Return created TaskResponse
  - Handle 400, 422 validation errors

- [ ] T016 [P] [US2] Add updateTask method to frontend/lib/api.ts
  - Call PUT /users/{user_id}/tasks/{task_id} with JWT
  - Send full task update
  - Return updated TaskResponse
  - Handle 400, 404, 422 errors

- [ ] T017 [P] [US2] Add patchTask method to frontend/lib/api.ts
  - Call PATCH /users/{user_id}/tasks/{task_id} with JWT
  - Send partial task update
  - Return updated TaskResponse
  - Handle 400, 404, 422 errors

- [ ] T018 [P] [US2] Add deleteTask method to frontend/lib/api.ts
  - Call DELETE /users/{user_id}/tasks/{task_id} with JWT
  - Handle 200 success
  - Handle 403, 404 errors

- [ ] T019 [US2] Update TaskForm component in frontend/components/TaskForm.tsx
  - Call createTask() on submit
  - Show loading spinner during API call
  - Display success toast on 201
  - Display error toast on failure
  - Clear form on success
  - Refresh task list after creation

- [ ] T020 [US2] Update TaskCard component in frontend/components/TaskCard.tsx
  - Add edit functionality calling patchTask()
  - Add delete button calling deleteTask()
  - Add complete/uncomplete toggle calling patchTask({completed})
  - Show loading state during operations
  - Display error toast on failure
  - Optimistic UI updates (optional)

- [ ] T021 [US2] Update tasks page in frontend/app/tasks/page.tsx
  - Call getTasks() on page load
  - Display loading spinner while fetching
  - Render task list from API response
  - Handle empty state (no tasks)
  - Display error message on fetch failure
  - Refresh list after create/update/delete operations

**Checkpoint**: Full task CRUD working with backend persistence

---

## Phase 5: User Story 3 - Search and Filter Integration (Priority: P2)

**Goal**: Users can search and filter tasks through UI with backend queries

**Independent Test**: Enter search term → see only matching tasks → apply priority filter → see filtered results

### Implementation for User Story 3

- [ ] T022 [P] [US3] Update TaskFilters component in frontend/components/TaskFilters.tsx
  - Add search input field
  - Add priority dropdown (all, low, medium, high, critical)
  - Add completed status filter (all, pending, completed)
  - Add tag filter input
  - Add sort dropdown (created, title, priority, updated)

- [ ] T023 [US3] Connect TaskFilters to getTasks() in frontend/app/tasks/page.tsx
  - Build query parameters from filter state
  - Call getTasks() with filters on change
  - Debounce search input (300ms)
  - Show loading state during filter queries
  - Display "No results" when filters return empty

- [ ] T024 [US3] Add pagination controls in frontend/app/tasks/page.tsx
  - Display page number and total from TaskListResponse
  - Add "Previous" and "Next" buttons
  - Calculate offset from page number
  - Call getTasks() with new offset on page change
  - Disable buttons at boundaries (first/last page)

- [ ] T025 [US3] Add URL query parameters for filters in frontend/app/tasks/page.tsx
  - Sync filter state with URL search params
  - Load filters from URL on page load
  - Update URL when filters change (without page reload)
  - Enable shareable filtered views

**Checkpoint**: Search, filter, sort, and pagination all working with backend

---

## Phase 6: User Story 4 - Profile Management Integration (Priority: P3)

**Goal**: Users can view and update their profile information through UI

**Independent Test**: Navigate to profile → see username and email → update username → see change persist

### Implementation for User Story 4

- [ ] T026 [P] [US4] Add getProfile method to frontend/lib/api.ts
  - Call GET /users/{user_id} with JWT
  - Return UserResponse
  - Handle 401, 403, 404 errors

- [ ] T027 [P] [US4] Add updateProfile method to frontend/lib/api.ts
  - Call PUT /users/{user_id} with JWT
  - Send username and/or email updates
  - Return updated UserResponse
  - Handle 409 duplicate errors
  - Handle 422 validation errors

- [ ] T028 [US4] Create profile page in frontend/app/profile/page.tsx
  - Call getProfile() on page load
  - Display username and email
  - Show loading spinner while fetching
  - Handle 404 user not found

- [ ] T029 [US4] Add profile edit form in frontend/app/profile/page.tsx
  - Username input with validation (3-50 chars)
  - Email input with validation (valid email)
  - Save button calling updateProfile()
  - Show loading state during save
  - Display success toast on 200
  - Display error toast on 409 duplicate
  - Refresh profile data after successful update

**Checkpoint**: Profile view and update working end-to-end

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T030 [P] Add global loading indicator in frontend/components/LoadingIndicator.tsx
  - Show spinner for API calls >500ms
  - Integrate with API client

- [ ] T031 [P] Enhance error handling in frontend/lib/api.ts
  - Retry logic for network failures (optional)
  - Better error messages for common errors
  - Log errors to console for debugging

- [ ] T032 [P] Add toast notification system in frontend/components/Toast.tsx (if not exists)
  - Success toasts (green)
  - Error toasts (red)
  - Info toasts (blue)
  - Auto-dismiss after 5 seconds

- [ ] T033 Update navigation in frontend/components/Navbar.tsx
  - Add "Tasks" link
  - Add "Profile" link
  - Add "Logout" button
  - Show user info when authenticated

- [ ] T034 Add environment variable validation in frontend/lib/env.ts
  - Validate BETTER_AUTH_SECRET exists
  - Validate API_URL exists and is valid URL
  - Throw error on missing required vars
  - Log configuration on app start

- [ ] T035 [P] Add request/response logging in frontend/lib/api.ts (development only)
  - Log all API requests with method, URL, body
  - Log all responses with status, body
  - Only enable when NODE_ENV=development

- [ ] T036 Test complete user journey: signup → login → create task → filter → update → delete → profile → logout
  - Manual testing of all features
  - Verify all API calls working
  - Verify error handling
  - Verify loading states

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (US1 → US2 → US3 → US4)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (US1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (US2)**: Depends on US1 completion (needs authentication to work)
- **User Story 3 (US3)**: Depends on US2 completion (needs task list to filter)
- **User Story 4 (US4)**: Can start after Foundational (Phase 2) - Independent of US2/US3

### Within Each User Story

- API client methods (lib/api.ts) before UI components
- Forms before page integration
- Core functionality before error handling enhancements
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks (T001-T003) can run in parallel
- All Type definitions (T006-T007) can run in parallel within Foundational
- Within US2: All API methods (T014-T018) can be implemented in parallel
- Within US3: Filter UI (T022) and pagination (T024) can be done in parallel
- Within US4: getProfile (T026) and updateProfile (T027) can be done in parallel
- All Polish tasks (T030-T035) can run in parallel

---

## Implementation Strategy

### MVP First (US1 + US2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Authentication)
4. Complete Phase 4: User Story 2 (Task CRUD)
5. **STOP and VALIDATE**: Test signup → login → create/update/delete tasks
6. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test auth flow independently → Works!
3. Add User Story 2 → Test task CRUD independently → MVP complete! 🎯
4. Add User Story 3 → Test search/filter independently → Enhanced!
5. Add User Story 4 → Test profile independently → Complete!
6. Add Polish → Refined UX

### Sequential Strategy (Recommended)

Due to dependencies between stories, sequential implementation is recommended:

1. Setup (Phase 1) - 15 minutes
2. Foundational (Phase 2) - 2 hours
3. US1 Authentication (Phase 3) - 2 hours
4. US2 Task Management (Phase 4) - 3 hours
5. US3 Search/Filter (Phase 5) - 1 hour
6. US4 Profile (Phase 6) - 1 hour
7. Polish (Phase 7) - 2 hours

**Total Estimated Time**: ~11-12 hours

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- All API methods must attach JWT token from Better Auth session
- All API errors must be caught and displayed to user with friendly messages
- All API calls >500ms should show loading indicators
- Commit after each phase or logical group
- Test each user story independently before moving to next
- Backend is 100% complete - no backend changes needed
