# Tasks: User Profile Management Endpoints

**Feature**: User Profile Management Endpoints (GET and PUT)
**Branch**: `011-user-profile-management`
**Created**: 2025-12-25
**Status**: Ready for Implementation

---

## Overview

This document breaks down the User Profile Management feature into atomic, executable tasks organized by user story. Each user story represents an independently testable increment of functionality.

**User Stories from Spec**:
- **US1 (P1)**: View Own Profile - Core read operation
- **US2 (P2)**: Update Username - Independent username modification
- **US3 (P2)**: Update Email - Independent email modification
- **US4 (P3)**: Update Both Fields - Convenience feature

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)
**US1 only**: Implement GET endpoint for profile viewing
- Delivers immediate value (users can see their profile)
- No dependencies on update logic
- Tests password exclusion and user isolation
- Can be deployed independently

### Incremental Delivery
1. **Iteration 1**: US1 (View Profile) - GET endpoint
2. **Iteration 2**: US2 (Update Username) - PUT endpoint with username support
3. **Iteration 3**: US3 (Update Email) - Extend PUT endpoint with email support
4. **Iteration 4**: US4 (Update Both) - Already works if US2+US3 complete

### Parallel Execution Opportunities
- **Phase 2**: All foundational tasks can run in parallel (different files)
- **Within US1**: Schema and service can be developed in parallel (T005, T006)
- **Between Stories**: US2 and US3 are independent (can be developed in parallel after US1)

---

## Dependencies

### Story Completion Order

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational - BLOCKING)
    ↓
US1 (View Profile) ← MUST complete first (foundational for all updates)
    ↓
US2 (Update Username) ← Can run in parallel with US3
US3 (Update Email)    ← Can run in parallel with US2
    ↓
US4 (Update Both) ← Depends on US2 + US3 (no new code, just validation)
```

### Critical Path
Phase 1 → Phase 2 → US1 → (US2 || US3) → US4 → Polish

**Estimated Timeline**:
- Phase 1: 15 min
- Phase 2: 30 min
- US1: 1.5 hours
- US2: 1 hour (parallel with US3)
- US3: 1 hour (parallel with US2)
- US4: 30 min
- Polish: 30 min
**Total**: ~5 hours (or ~4 hours with parallelization)

---

## Phase 1: Setup & Prerequisites

**Goal**: Ensure environment and dependencies are ready

**Tasks**:

- [X] T001 Verify User model exists in backend/models.py with required fields (id, username, email, password_hash, created_at, updated_at)
- [X] T002 Verify JWT middleware functional at backend/middleware/auth_middleware.py with get_user_id_from_token dependency
- [X] T003 Verify database has unique constraints on username and email fields
- [X] T004 Verify test fixtures exist in backend/tests/conftest.py for user creation and JWT token generation

**Acceptance**: All prerequisites verified, no blockers for implementation

---

## Phase 2: Foundational Components (BLOCKING)

**Goal**: Create shared components needed by all user stories

**Independent Test**: Schemas validate correctly, imports work, no syntax errors

**Foundational Tasks**:

- [X] T005 [P] Create UserResponse schema in backend/schemas/user.py (excludes password_hash, includes id/username/email/created_at/updated_at with Config.from_attributes=True)
- [X] T006 [P] Create UpdateUserRequest schema in backend/schemas/user.py (optional username Field(None, min_length=3, max_length=50), optional email EmailStr)
- [X] T007 [P] Create user service file backend/services/user_service.py with imports (Session, User, UpdateUserRequest, Optional, UUID, HTTPException, select, func)
- [X] T008 [P] Create users router file backend/routes/users.py with router setup (APIRouter(prefix="/users", tags=["users"]))

**Validation Tasks**:

- [X] T009 Test UserResponse schema excludes password_hash field
- [X] T010 Test UpdateUserRequest validates username length (3-50 characters)
- [X] T011 Test UpdateUserRequest validates email format with EmailStr

**Acceptance**: All schemas created and validated, service and route files initialized

---

## Phase 3: User Story 1 - View Own Profile (P1)

**Story Goal**: Authenticated users can retrieve their profile information via GET endpoint

**Why P1**: Core read operation, foundational for all profile management features, no dependencies

**Independent Test**: User can authenticate, request their profile, and receive profile data (without password_hash)

**Service Layer**:

- [X] T012 [US1] Implement get_user_profile function in backend/services/user_service.py (takes session and user_id, returns session.get(User, user_id))

**Route Layer**:

- [X] T013 [US1] Implement GET /users/{user_id} endpoint in backend/routes/users.py (verify user_id matches JWT, call get_user_profile, return 200 with UserResponse or 404 if not found, return 403 if user_id mismatch)
- [X] T014 [US1] Register users router in backend/main.py (app.include_router(users.router))

**Integration Tests**:

- [X] T015 [US1] Create test file backend/tests/test_user_profile.py with fixtures and imports
- [X] T016 [US1] Test GET profile success returns 200 with correct fields (id, username, email, timestamps)
- [X] T017 [US1] Test GET profile excludes password_hash from response (assert "password_hash" not in response.json())
- [X] T018 [US1] Test GET profile with cross-user access returns 403 Forbidden
- [X] T019 [US1] Test GET profile with missing JWT token returns 401 Unauthorized
- [X] T020 [US1] Test GET profile with non-existent user_id returns 404 Not Found
- [X] T021 [US1] Test GET profile with invalid UUID format returns 422

**Acceptance Criteria**:
- ✅ GET /users/{user_id} endpoint functional
- ✅ Password hash never exposed in response (100% test coverage)
- ✅ Cross-user access blocked (403 returned)
- ✅ JWT authentication required (401 for missing token)
- ✅ All 7 tests passing

---

## Phase 4: User Story 2 - Update Username (P2)

**Story Goal**: Authenticated users can update their username via PUT endpoint

**Why P2**: Common user need for identity customization, independent of email updates

**Independent Test**: User can update only username field and see the change persist

**Service Layer - Username Logic**:

- [X] T022 [US2] Add username duplicate checking in backend/services/user_service.py (query User where username = new_username AND id != user_id, raise 409 if exists)
- [X] T023 [US2] Implement update_user_profile function in backend/services/user_service.py (validate user exists, check at least one field provided, handle username updates with duplicate check, update updated_at timestamp, commit and refresh)

**Route Layer - PUT Endpoint**:

- [X] T024 [US2] Implement PUT /users/{user_id} endpoint in backend/routes/users.py (verify user_id matches JWT, call update_user_profile with UpdateUserRequest, return 200 with UserResponse or 404/403/409/422 for errors)

**Integration Tests - Username**:

- [X] T025 [US2] Test PUT update username success returns 200 with updated profile
- [X] T026 [US2] Test PUT update username to duplicate returns 409 Conflict with error message
- [X] T027 [US2] Test PUT update username with length < 3 returns 422 validation error
- [X] T028 [US2] Test PUT update username with length > 50 returns 422 validation error
- [X] T029 [US2] Test PUT update username for cross-user returns 403 Forbidden
- [X] T030 [US2] Test PUT update username to same value succeeds (idempotent)
- [X] T031 [US2] Test PUT with neither username nor email returns 422 "at least one field required"

**Acceptance Criteria**:
- ✅ PUT /users/{user_id} endpoint accepts username updates
- ✅ Duplicate usernames detected and rejected (409)
- ✅ Username validation enforced (3-50 characters)
- ✅ Idempotent updates allowed (same username accepted)
- ✅ Cross-user updates blocked (403)
- ✅ All 7 tests passing

---

## Phase 5: User Story 3 - Update Email (P2)

**Story Goal**: Authenticated users can update their email address via PUT endpoint

**Why P2**: Important for maintaining communication channels, independent of username updates

**Independent Test**: User can update only email field and see the change persist

**Service Layer - Email Logic**:

- [X] T032 [US3] Add email duplicate checking in backend/services/user_service.py (query User where func.lower(email) = func.lower(new_email) AND id != user_id, raise 409 if exists with case-insensitive comparison)
- [X] T033 [US3] Extend update_user_profile function in backend/services/user_service.py to handle email updates with duplicate check

**Integration Tests - Email**:

- [X] T034 [US3] Test PUT update email success returns 200 with updated profile
- [X] T035 [US3] Test PUT update email to duplicate returns 409 Conflict with error message
- [X] T036 [US3] Test PUT update email with invalid format returns 422 validation error
- [X] T037 [US3] Test PUT update email case-insensitive duplicate detection (EMAIL@TEST.COM == email@test.com)
- [X] T038 [US3] Test PUT update email to same value succeeds (idempotent)
- [X] T039 [US3] Test PUT update email for cross-user returns 403 Forbidden

**Acceptance Criteria**:
- ✅ PUT /users/{user_id} endpoint accepts email updates
- ✅ Duplicate emails detected with case-insensitive comparison (409)
- ✅ Email format validation enforced (EmailStr)
- ✅ Idempotent updates allowed (same email accepted)
- ✅ Cross-user updates blocked (403)
- ✅ All 6 tests passing

---

## Phase 6: User Story 4 - Update Both Fields (P3)

**Story Goal**: Authenticated users can update username and email in a single request

**Why P3**: Convenience feature reducing API calls, depends on US2+US3 working independently

**Independent Test**: User can provide both username and email in single request and both fields update

**Note**: No new service/route code required - update_user_profile already handles multiple fields. This phase focuses on edge case testing.

**Integration Tests - Both Fields**:

- [X] T040 [US4] Test PUT update both username and email success returns 200 with both updated
- [X] T041 [US4] Test PUT update username to duplicate with valid email returns 409 for username (neither field updated - transaction rollback)
- [X] T042 [US4] Test PUT update email to duplicate with valid username returns 409 for email (neither field updated - transaction rollback)

**Acceptance Criteria**:
- ✅ Single PUT request can update both fields
- ✅ Duplicate in either field prevents entire update (atomic transaction)
- ✅ All 3 tests passing

---

## Phase 7: Polish & Cross-Cutting Concerns

**Goal**: Code quality, performance, and deployment readiness

**Code Quality**:

- [X] T043 Run type checking with mypy on backend/ directory (0 errors)
- [X] T044 Run linting with ruff/black on backend/ directory (0 errors)
- [X] T045 Verify code coverage ≥95% for backend/schemas/user.py, backend/services/user_service.py, backend/routes/users.py

**Performance Validation**:

- [X] T046 Test GET endpoint latency <1s for 95th percentile (measure with 100 requests)
- [X] T047 Test PUT endpoint latency <2s for 95th percentile (measure with 100 requests)
- [X] T048 Test concurrent requests (500 simultaneous users) complete without errors

**Security Audit**:

- [X] T049 Verify password_hash never appears in any API response (grep test outputs for "password_hash")
- [X] T050 Verify all cross-user access attempts return 403 Forbidden (not 404, prevents enumeration)
- [X] T051 Verify duplicate checking excludes current user in queries (idempotent updates work)

**Documentation**:

- [X] T052 Generate OpenAPI/Swagger documentation for new endpoints (verify schema matches contracts)
- [X] T053 Update API documentation with GET and PUT examples
- [X] T054 Create IMPLEMENTATION_COMPLETE.md in specs/011-user-profile-management/ with summary of changes

**Deployment Checklist**:

- [X] T055 Verify all 24+ tests passing (pytest backend/tests/test_user_profile.py)
- [X] T056 Verify database indexes exist on username and email fields
- [X] T057 Verify environment variables configured (DATABASE_URL, BETTER_AUTH_SECRET)

**Acceptance**: All quality gates passed, feature ready for deployment

---

## Task Summary

### Total Tasks: 57

**By Phase**:
- Phase 1 (Setup): 4 tasks
- Phase 2 (Foundational): 7 tasks
- Phase 3 (US1 - View Profile): 10 tasks
- Phase 4 (US2 - Update Username): 10 tasks
- Phase 5 (US3 - Update Email): 8 tasks
- Phase 6 (US4 - Update Both): 3 tasks
- Phase 7 (Polish): 15 tasks

**By Type**:
- Setup/Validation: 11 tasks
- Implementation (Service/Route/Schema): 12 tasks
- Tests: 24 tasks
- Quality/Performance: 10 tasks

**Parallelization Opportunities**:
- Phase 2: All 7 foundational tasks (T005-T008 are [P])
- Within US1: Schema + Service development can overlap
- US2 and US3: Can be developed in parallel (independent)

---

## Test Coverage Summary

### Critical Security Tests (100% Coverage Required)
- Password hash exclusion: 1 test (T017)
- Cross-user access prevention: 4 tests (T018, T029, T039, T043)
- JWT authentication: 1 test (T019)
**Total**: 6 critical security tests

### Duplicate Detection Tests
- Username duplicates: 2 tests (T026, T030)
- Email duplicates: 3 tests (T035, T037, T038)
- Both fields duplicates: 2 tests (T041, T042)
**Total**: 7 duplicate detection tests

### Validation Tests
- Username validation: 2 tests (T027, T028)
- Email validation: 1 test (T036)
- Field requirements: 1 test (T031)
**Total**: 4 validation tests

### Integration Tests
- Success paths: 4 tests (T016, T025, T034, T040)
- Error paths: 3 tests (T020, T021, T043)
**Total**: 7 integration tests

**Grand Total**: 24 tests

---

## File Manifest

### Files to Create (4 new files)
- [ ] `backend/schemas/user.py` - UserResponse and UpdateUserRequest schemas
- [ ] `backend/services/user_service.py` - get_user_profile and update_user_profile functions
- [ ] `backend/routes/users.py` - GET and PUT endpoints for user profile
- [ ] `backend/tests/test_user_profile.py` - Comprehensive test suite (24 tests)

### Files to Modify (1 file)
- [ ] `backend/main.py` - Register users router (app.include_router(users.router))

### Files to Reference (No Changes)
- ✅ `backend/models.py` - User model (already exists)
- ✅ `backend/db.py` - Database session management (already exists)
- ✅ `backend/middleware/auth_middleware.py` - JWT middleware (already exists)
- ✅ `backend/tests/conftest.py` - Test fixtures (already exists)

---

## Success Metrics

### Functional Requirements (17 total)
- [ ] FR-001 to FR-017: All functional requirements from spec.md implemented and tested

### Performance Metrics
- [ ] GET requests <1s (95th percentile)
- [ ] PUT requests <2s (95th percentile)
- [ ] 500 concurrent users supported

### Security Metrics
- [ ] 100% password hash exclusion (zero breaches)
- [ ] 100% cross-user access blocked
- [ ] 100% duplicate detection accuracy

### Code Quality Metrics
- [ ] 95%+ code coverage
- [ ] Zero type errors (mypy)
- [ ] Zero linting errors
- [ ] All docstrings present

---

## Implementation Notes

### Agent & Skills to Use

**Primary Agent**: `user-management-specialist`
- Location: `backend/.claude/agents/user-management-specialist.md`
- Expertise: User profile CRUD, duplicate checking, secure responses

**Skills**:
- user-profile-management
- duplicate-checking
- secure-responses

### Execution Strategy

**For /sp.implement**:
1. Start with Phase 1 (verification)
2. Complete Phase 2 (all foundational tasks in parallel if possible)
3. Implement US1 fully (tests passing) before moving to US2/US3
4. US2 and US3 can be done in parallel or sequentially
5. US4 is mostly validation (minimal new code)
6. Run Phase 7 after all user stories complete

**For Manual Implementation**:
1. Follow task order within each phase
2. Run tests after each user story phase completes
3. Fix any failures before proceeding to next story
4. Use parallel execution where tasks are marked [P]

---

## Risk Mitigation

### High-Risk Tasks
- **T017** (Password exclusion test): MUST pass - critical security
- **T018, T029, T039** (Cross-user access): MUST pass - privacy violation prevention
- **T026, T035** (Duplicate detection): MUST pass - data integrity

**Mitigation**: Run these tests first in each phase, block progression if any fail

### Medium-Risk Tasks
- **T046, T047** (Performance tests): May fail under load
- **T048** (Concurrency test): Database connection limits

**Mitigation**: Run in isolation, adjust connection pool settings if needed

---

## Next Steps

After tasks are approved:

1. Run `/sp.implement` to execute implementation with user-management-specialist agent
2. Or implement manually following task order in each phase
3. Verify all 24+ tests passing after US1, US2, US3, US4
4. Complete Phase 7 (polish) before creating PR
5. Create pull request: 011-user-profile-management → main

**Ready for Implementation** ✅
