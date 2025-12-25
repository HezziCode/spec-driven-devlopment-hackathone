---
description: "Task breakdown for JWT Authentication Middleware implementation"
---

# Tasks: JWT Authentication Middleware

**Input**: Design documents from `/specs/006-jwt-auth-middleware/`
**Prerequisites**: plan.md, spec.md, research.md, contracts/middleware-contract.md, contracts/jwt-utils-contract.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1=Middleware, US2=Utilities)
- Include exact file paths in descriptions

## Path Conventions

- Backend: `backend/` at repository root
- All paths shown are absolute from repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency verification

- [ ] T001 Verify python-jose[cryptography] is installed in backend/pyproject.toml dependencies
- [ ] T002 [P] Update backend/.env.example to document BETTER_AUTH_SECRET requirement with usage instructions
- [ ] T003 [P] Verify BETTER_AUTH_SECRET exists in backend/.env (must be at least 32 characters)
- [ ] T004 Create backend/middleware/ directory if it doesn't exist (with __init__.py)
- [ ] T005 Create backend/utils/ directory if it doesn't exist (with __init__.py)

**Checkpoint**: Environment and directory structure ready for implementation

---

## Phase 2: Foundational (Test Infrastructure)

**Purpose**: Core test infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Update backend/tests/conftest.py to add JWT test fixtures (generate_valid_jwt, generate_expired_jwt, generate_invalid_signature_jwt)
- [ ] T007 [P] Create backend/tests/test_auth_middleware.py file with test class structure and imports
- [ ] T008 [P] Create backend/tests/test_jwt_utils.py file with test class structure and imports
- [ ] T009 Create backend/scripts/generate_test_token.py utility script for manual JWT token generation

**Checkpoint**: Test infrastructure ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - JWT Middleware (Priority: P1) 🎯 MVP

**Goal**: Implement FastAPI middleware that automatically validates JWT tokens on protected endpoints, extracts user context, and returns standardized error responses

**Independent Test**: Make API requests with valid JWT tokens (should pass through middleware), invalid tokens (should reject with 401), missing tokens (should reject with 401), malformed tokens (should reject with 400), to authentication endpoints (should bypass middleware), verifying user context is attached to request.state for protected endpoints

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T010 [P] [US1] Write test for valid JWT token passes middleware in backend/tests/test_auth_middleware.py::test_valid_token_passes
- [ ] T011 [P] [US1] Write test for missing Authorization header returns 401 in backend/tests/test_auth_middleware.py::test_missing_token_returns_401
- [ ] T012 [P] [US1] Write test for expired JWT token returns 401 in backend/tests/test_auth_middleware.py::test_expired_token_returns_401
- [ ] T013 [P] [US1] Write test for invalid JWT signature returns 401 in backend/tests/test_auth_middleware.py::test_invalid_signature_returns_401
- [ ] T014 [P] [US1] Write test for malformed Authorization header returns 400 in backend/tests/test_auth_middleware.py::test_malformed_header_returns_400
- [ ] T015 [P] [US1] Write test for /auth/* routes bypass authentication in backend/tests/test_auth_middleware.py::test_auth_routes_bypass
- [ ] T016 [P] [US1] Write test for user context attached to request.state in backend/tests/test_auth_middleware.py::test_user_context_attached

**Checkpoint**: Run tests with `pytest backend/tests/test_auth_middleware.py` - ALL SHOULD FAIL

### Implementation for User Story 1

- [ ] T017 [US1] Create backend/middleware/auth_middleware.py with imports and BETTER_AUTH_SECRET loading/validation
- [ ] T018 [US1] Implement create_error_response() helper function in backend/middleware/auth_middleware.py
- [ ] T019 [US1] Define PUBLIC_PATHS constant list in backend/middleware/auth_middleware.py
- [ ] T020 [US1] Implement verify_jwt_middleware() async function signature in backend/middleware/auth_middleware.py
- [ ] T021 [US1] Add public route bypass logic (check if request.url.path starts with PUBLIC_PATHS)
- [ ] T022 [US1] Add Authorization header extraction and "Bearer " prefix validation
- [ ] T023 [US1] Add JWT token verification with jwt.decode() using BETTER_AUTH_SECRET and HS256
- [ ] T024 [US1] Add user context extraction from payload (sub -> user_id, email -> email)
- [ ] T025 [US1] Attach user_id and email to request.state (request.state.user_id, request.state.email)
- [ ] T026 [US1] Add error handling for missing token (return 401 with create_error_response)
- [ ] T027 [US1] Add error handling for malformed Authorization header (return 400)
- [ ] T028 [US1] Add error handling for ExpiredSignatureError (return 401 with "Token has expired")
- [ ] T029 [US1] Add error handling for JWTError (return 401 with "Invalid token signature")
- [ ] T030 [US1] Add complete type hints to all functions (no Any except JWT payload dict)
- [ ] T031 [US1] Add Google-style docstrings to verify_jwt_middleware() and create_error_response()
- [ ] T032 [US1] Update backend/middleware/__init__.py to export verify_jwt_middleware

**Checkpoint**: Run tests with `pytest backend/tests/test_auth_middleware.py` - ALL SHOULD PASS

---

## Phase 4: User Story 2 - JWT Utility Functions (Priority: P2)

**Goal**: Provide comprehensive JWT token validation utilities for secure token handling, user information extraction, and support for token operations across the application

**Independent Test**: Call utility functions with various token inputs: valid tokens return correct user data, expired tokens return False on verification, invalid signatures fail verification, malformed tokens raise appropriate exceptions, user extraction from token returns User model or None

### Tests for User Story 2 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T033 [P] [US2] Write test for decode_token with valid token in backend/tests/test_jwt_utils.py::test_decode_valid_token
- [ ] T034 [P] [US2] Write test for decode_token with invalid signature raises JWTError in backend/tests/test_jwt_utils.py::test_decode_invalid_signature
- [ ] T035 [P] [US2] Write test for decode_token with expired token raises ExpiredSignatureError in backend/tests/test_jwt_utils.py::test_decode_expired_token
- [ ] T036 [P] [US2] Write test for verify_token with valid token returns True in backend/tests/test_jwt_utils.py::test_verify_valid_token
- [ ] T037 [P] [US2] Write test for verify_token with expired token returns False in backend/tests/test_jwt_utils.py::test_verify_expired_token
- [ ] T038 [P] [US2] Write test for verify_token with invalid signature returns False in backend/tests/test_jwt_utils.py::test_verify_invalid_signature
- [ ] T039 [P] [US2] Write test for extract_user_from_token with existing user returns User in backend/tests/test_jwt_utils.py::test_extract_existing_user
- [ ] T040 [P] [US2] Write test for extract_user_from_token with nonexistent user returns None in backend/tests/test_jwt_utils.py::test_extract_nonexistent_user

**Checkpoint**: Run tests with `pytest backend/tests/test_jwt_utils.py` - ALL SHOULD FAIL

### Implementation for User Story 2

- [ ] T041 [US2] Create backend/utils/jwt_utils.py with imports and BETTER_AUTH_SECRET loading/validation
- [ ] T042 [P] [US2] Implement decode_token(token: str) -> dict[str, Any] function in backend/utils/jwt_utils.py
- [ ] T043 [P] [US2] Implement verify_token(token: str) -> bool function in backend/utils/jwt_utils.py
- [ ] T044 [US2] Implement extract_user_from_token(token: str, session: Session) -> Optional[User] function in backend/utils/jwt_utils.py
- [ ] T045 [US2] Add complete type hints to all utility functions (decode_token, verify_token, extract_user_from_token)
- [ ] T046 [US2] Add Google-style docstrings with parameter and return type documentation to all functions
- [ ] T047 [US2] Update backend/utils/__init__.py to export JWT utility functions

**Checkpoint**: Run tests with `pytest backend/tests/test_jwt_utils.py` - ALL SHOULD PASS

---

## Phase 5: Integration (Connect Middleware to FastAPI)

**Purpose**: Register middleware in FastAPI application and verify end-to-end functionality

- [ ] T048 Update backend/main.py to import verify_jwt_middleware from middleware.auth_middleware
- [ ] T049 Register middleware in backend/main.py with app.middleware("http")(verify_jwt_middleware)
- [ ] T050 Ensure middleware registration happens before route inclusion (middleware should run first)
- [ ] T051 [P] Create integration test in backend/tests/test_auth_middleware.py::test_middleware_registered_in_app
- [ ] T052 [P] Create end-to-end test that makes real HTTP request with JWT token to protected endpoint

**Checkpoint**: At this point, middleware is active and protecting all API routes automatically

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validation, documentation, and final quality checks

- [ ] T053 [P] Run full test suite with `pytest backend/tests/` and verify 100% pass rate
- [ ] T054 [P] Run mypy type checking with `mypy backend/` in strict mode and verify zero errors
- [ ] T055 [P] Verify test coverage with `pytest --cov=backend/middleware --cov=backend/utils backend/tests/` (target: 100%)
- [ ] T056 Test middleware with curl using valid JWT token: `curl -H "Authorization: Bearer <token>" http://localhost:8000/api/users/me`
- [ ] T057 Test middleware with curl missing token: `curl http://localhost:8000/api/users/me` (expect 401)
- [ ] T058 Test middleware with curl expired token (expect 401 with "Token has expired")
- [ ] T059 Test public routes with curl without token: `curl http://localhost:8000/auth/login` (expect success)
- [ ] T060 [P] Update backend/.env.example with complete BETTER_AUTH_SECRET documentation
- [ ] T061 [P] Validate backend/scripts/generate_test_token.py works correctly for manual testing
- [ ] T062 Run quickstart.md validation from /specs/006-jwt-auth-middleware/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3, 4)**: All depend on Foundational phase completion
  - User Story 1 (Middleware) and User Story 2 (Utilities) can proceed in parallel (different files)
- **Integration (Phase 5)**: Depends on User Story 1 completion (middleware must exist to register)
- **Polish (Phase 6)**: Depends on all user stories and integration being complete

### User Story Dependencies

- **User Story 1 (P1 - Middleware)**: Can start after Foundational (Phase 2) - No dependencies on US2
- **User Story 2 (P2 - Utilities)**: Can start after Foundational (Phase 2) - No dependencies on US1 (though US1 may use these utilities later)

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD approach)
- Test writing tasks (T010-T016, T033-T040) can run in parallel (marked with [P])
- Implementation tasks run sequentially to build functionality step by step
- Tests verify implementation after completion

### Parallel Opportunities

- Phase 1: T002 and T003 can run in parallel (marked with [P])
- Phase 2: T007 and T008 can run in parallel (creating separate test files)
- User Story 1 Tests: T010-T016 can all run in parallel (different test functions)
- User Story 2 Tests: T033-T040 can all run in parallel (different test functions)
- User Story 2 Implementation: T042 and T043 can run in parallel (independent functions)
- User Stories 1 and 2 can be worked on in parallel by different team members
- Phase 5: T051 and T052 can run in parallel (different test files)
- Phase 6: T053, T054, T055, T060, T061 can all run in parallel (independent validation tasks)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Middleware)
4. Complete Phase 5: Integration
5. **STOP and VALIDATE**: Test middleware with curl and pytest
6. Deploy/demo if ready (core authentication working)

### Full Implementation (Both Stories)

1. Complete Phase 1: Setup + Phase 2: Foundational → Foundation ready
2. Parallel: User Story 1 (Phase 3) AND User Story 2 (Phase 4)
3. Complete Phase 5: Integration
4. Complete Phase 6: Polish → Feature complete

### Parallel Team Strategy

With two developers:

1. Both complete Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Middleware) → Phase 3
   - Developer B: User Story 2 (Utilities) → Phase 4
3. Developer A: Integration (Phase 5)
4. Both: Polish and validation (Phase 6)

---

## Test Execution Checkpoints

### After Phase 2 (Foundational)
```bash
# Test infrastructure exists
ls backend/tests/test_auth_middleware.py
ls backend/tests/test_jwt_utils.py
ls backend/tests/conftest.py
```

### After Phase 3 (User Story 1)
```bash
# All middleware tests pass
pytest backend/tests/test_auth_middleware.py -v
# Expected: 7 tests passed
```

### After Phase 4 (User Story 2)
```bash
# All utility tests pass
pytest backend/tests/test_jwt_utils.py -v
# Expected: 8 tests passed
```

### After Phase 5 (Integration)
```bash
# Full test suite passes
pytest backend/tests/ -v
# Expected: 17+ tests passed

# Type checking passes
mypy backend/middleware/auth_middleware.py backend/utils/jwt_utils.py
# Expected: Success: no issues found
```

### After Phase 6 (Polish)
```bash
# Full validation
pytest backend/tests/ --cov=backend/middleware --cov=backend/utils -v
# Expected: 100% coverage, all tests passed

# Manual curl tests
curl -H "Authorization: Bearer $(python backend/scripts/generate_test_token.py)" http://localhost:8000/api/users/me
# Expected: 200 OK or proper error if endpoint not implemented
```

---

## Task File Mapping

### Phase 1: Setup
- T001: backend/pyproject.toml (verify)
- T002: backend/.env.example (update)
- T003: backend/.env (verify)
- T004: backend/middleware/__init__.py (create)
- T005: backend/utils/__init__.py (create)

### Phase 2: Foundational
- T006: backend/tests/conftest.py (update)
- T007: backend/tests/test_auth_middleware.py (create)
- T008: backend/tests/test_jwt_utils.py (create)
- T009: backend/scripts/generate_test_token.py (create)

### Phase 3: User Story 1 - Tests
- T010-T016: backend/tests/test_auth_middleware.py (7 test functions)

### Phase 3: User Story 1 - Implementation
- T017-T032: backend/middleware/auth_middleware.py (all implementation)

### Phase 4: User Story 2 - Tests
- T033-T040: backend/tests/test_jwt_utils.py (8 test functions)

### Phase 4: User Story 2 - Implementation
- T041-T047: backend/utils/jwt_utils.py (all implementation)

### Phase 5: Integration
- T048-T050: backend/main.py (updates)
- T051-T052: backend/tests/test_auth_middleware.py (integration tests)

### Phase 6: Polish
- T053-T062: Various validation and documentation tasks

---

## Acceptance Criteria Summary

### User Story 1 (Middleware)
- [x] Middleware registered in FastAPI app via app.middleware("http")
- [x] JWT tokens verified correctly using BETTER_AUTH_SECRET with HS256 algorithm
- [x] User context (user_id, email) attached to all protected requests via request.state
- [x] Proper error responses for auth failures: 401 for missing/expired/invalid tokens, 400 for malformed headers
- [x] Error format: {error: string, code: string, timestamp: ISO8601}
- [x] Valid token passes middleware and proceeds to route handler
- [x] Expired token fails with 401 Unauthorized
- [x] Missing token fails with 401 Unauthorized
- [x] Malformed token fails with 400 Bad Request
- [x] Middleware bypasses /auth/* routes

### User Story 2 (Utilities)
- [x] decode_token(token: str) returns dict with payload claims
- [x] verify_token(token: str) returns bool (True for valid, False for expired/invalid)
- [x] extract_user_from_token(token: str, session: Session) returns User object or None
- [x] All functions have complete type hints (no Any except JWT payload dict)
- [x] All functions have Google-style docstrings
- [x] Utility functions handle all error cases gracefully
- [x] Valid tokens decode correctly
- [x] Expired tokens raise ExpiredSignatureError in decode_token, return False in verify_token
- [x] Invalid signatures raise JWTError in decode_token, return False in verify_token

---

## Notes

- [P] tasks = different files or independent operations, no dependencies
- [Story] label maps task to specific user story (US1 or US2) for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD approach)
- Commit after each task or logical group
- Stop at any checkpoint to validate independently
- Run mypy and pytest frequently during implementation
- Middleware is foundational security infrastructure - must be 100% reliable
- Type safety is NON-NEGOTIABLE per constitution
- Performance target: < 10ms middleware overhead per request
