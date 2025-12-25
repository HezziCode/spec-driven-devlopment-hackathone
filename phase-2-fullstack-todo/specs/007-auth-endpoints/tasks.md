# Implementation Tasks: User Authentication Endpoints

**Feature**: 007-auth-endpoints | **Branch**: `007-auth-endpoints` | **Date**: 2025-12-24
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md) | **Contracts**: [contracts/](./contracts/)

## Overview

This task breakdown follows Test-Driven Development (TDD) approach for implementing three authentication endpoints (POST /auth/signup, POST /auth/login, POST /auth/logout) with password hashing using bcrypt and JWT token generation with 7-day expiration.

**Key Principles**:
- Write tests BEFORE implementation (Red-Green-Refactor)
- Mark parallelizable tasks with [P]
- Each task has clear acceptance criteria
- Phase dependencies clearly stated

---

## Phase 1: Setup and Dependencies

### Task 1.1: Install passlib with bcrypt [P]
**Description**: Install passlib library with bcrypt extra for password hashing

**Steps**:
1. Navigate to backend directory: `cd backend`
2. Install passlib with bcrypt: `uv add "passlib[bcrypt]"`
3. Verify installation: `python -c "from passlib.context import CryptContext; print('passlib installed')"`

**Acceptance Criteria**:
- [ ] passlib[bcrypt] added to backend/pyproject.toml dependencies
- [ ] Can import CryptContext from passlib.context without errors
- [ ] uv.lock file updated with passlib and bcrypt dependencies

**Dependencies**: None (can run first)
**Estimated Time**: 2 minutes
**Files Modified**: `backend/pyproject.toml`, `backend/uv.lock`

---

### Task 1.2: Verify Environment Configuration [P]
**Description**: Ensure BETTER_AUTH_SECRET is configured in backend/.env

**Steps**:
1. Check backend/.env for BETTER_AUTH_SECRET: `cat backend/.env | grep BETTER_AUTH_SECRET`
2. If missing, generate and add: `echo "BETTER_AUTH_SECRET=$(openssl rand -base64 32)" >> backend/.env`
3. Verify length is at least 32 characters

**Acceptance Criteria**:
- [ ] BETTER_AUTH_SECRET exists in backend/.env
- [ ] Secret is at least 32 characters long
- [ ] Secret is not committed to git (verify in .gitignore)

**Dependencies**: None (can run first)
**Estimated Time**: 2 minutes
**Files Modified**: `backend/.env` (if missing)

---

### Task 1.3: Verify Database User Model [P]
**Description**: Confirm User model exists with required fields for authentication

**Steps**:
1. Read backend/models.py to verify User model exists
2. Check User model has fields: id (UUID), username (str), email (str), password_hash (str), created_at (datetime), updated_at (datetime)
3. Verify database table exists: `python -c "from db import engine; from sqlmodel import inspect; print('users' in inspect(engine).get_table_names())"`

**Acceptance Criteria**:
- [ ] User model exists in backend/models.py with all required fields
- [ ] password_hash field is present (type: str)
- [ ] users table exists in database
- [ ] Unique constraints on username and email (check model or migration)

**Dependencies**: Database foundation feature (005-database-foundation) must be complete
**Estimated Time**: 3 minutes
**Files Read**: `backend/models.py`, `backend/db.py`

---

## Phase 2: Foundational Components (TDD - Write Tests First)

### Task 2.1: Create Authentication Test Fixtures
**Description**: Add pytest fixtures for authentication testing in conftest.py

**Steps**:
1. Read existing backend/tests/conftest.py
2. Add fixture `create_test_user(session, username="testuser", email="test@example.com", password="TestPass123")` that:
   - Hashes password with passlib bcrypt 12 rounds
   - Creates User in database
   - Returns tuple: (user, plain_password)
3. Add fixture `valid_signup_data()` returning dict with valid signup fields
4. Add fixture `valid_login_data()` returning dict with valid login fields
5. Add docstrings to all fixtures

**Acceptance Criteria**:
- [ ] create_test_user fixture creates user with hashed password
- [ ] Fixture returns both user object and original plaintext password for testing
- [ ] valid_signup_data returns dict with username, email, password
- [ ] valid_login_data returns dict with email, password
- [ ] All fixtures have clear docstrings

**Dependencies**: Task 1.1 (passlib installed)
**Estimated Time**: 10 minutes
**Files Modified**: `backend/tests/conftest.py`

**Test Code**:
```python
from passlib.context import CryptContext
from models import User

pwd_context = CryptContext(schemes=["bcrypt"], bcrypt__rounds=12, deprecated="auto")

def create_test_user(session, username="testuser", email="test@example.com", password="TestPass123"):
    """Create a test user with hashed password. Returns (user, plaintext_password)."""
    password_hash = pwd_context.hash(password)
    user = User(
        username=username,
        email=email.lower(),
        password_hash=password_hash
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user, password

def valid_signup_data():
    """Valid signup request data for testing."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass123"
    }

def valid_login_data():
    """Valid login request data for testing."""
    return {
        "email": "test@example.com",
        "password": "SecurePass123"
    }
```

---

### Task 2.2: Create Pydantic Schema Tests (RED Phase)
**Description**: Write tests for authentication Pydantic schemas BEFORE implementing schemas

**Steps**:
1. Create backend/tests/test_auth_schemas.py
2. Import pytest, ValidationError from pydantic
3. Write test functions (these WILL FAIL initially - RED phase):
   - `test_signup_request_valid()`: Create SignupRequest with valid data, verify fields
   - `test_signup_request_short_username()`: Expect ValidationError for 2-char username
   - `test_signup_request_long_username()`: Expect ValidationError for 51-char username
   - `test_signup_request_invalid_email()`: Expect ValidationError for "notanemail"
   - `test_signup_request_short_password()`: Expect ValidationError for 7-char password
   - `test_login_request_valid()`: Create LoginRequest with valid email and password
   - `test_login_request_invalid_email()`: Expect ValidationError for invalid email
   - `test_user_response_excludes_password_hash()`: Verify password_hash not in model_dump()
   - `test_auth_response_structure()`: Create AuthResponse, verify user and token fields
4. Add imports for schemas (will fail until schemas exist)
5. Run tests: `pytest backend/tests/test_auth_schemas.py` (EXPECT ALL TO FAIL)

**Acceptance Criteria**:
- [ ] Test file created with 9 test functions
- [ ] Tests use pytest.raises() for ValidationError cases
- [ ] Tests verify field values for valid cases
- [ ] All tests currently FAIL (RED phase - schemas not implemented yet)
- [ ] Test coverage plan for all schema validation rules

**Dependencies**: None (tests written before implementation)
**Estimated Time**: 20 minutes
**Files Created**: `backend/tests/test_auth_schemas.py`

**Test Code Template**:
```python
import pytest
from pydantic import ValidationError
from uuid import uuid4
from datetime import datetime

def test_signup_request_valid():
    from schemas.auth import SignupRequest
    request = SignupRequest(
        username="testuser",
        email="test@example.com",
        password="SecurePass123"
    )
    assert request.username == "testuser"
    assert request.email == "test@example.com"
    assert request.password == "SecurePass123"

def test_signup_request_short_username():
    from schemas.auth import SignupRequest
    with pytest.raises(ValidationError) as exc_info:
        SignupRequest(username="ab", email="test@example.com", password="SecurePass123")
    assert "min_length" in str(exc_info.value)

# ... 7 more test functions
```

---

### Task 2.3: Implement Authentication Pydantic Schemas (GREEN Phase)
**Description**: Create schemas/auth.py to make schema tests pass

**Steps**:
1. Create backend/schemas/auth.py
2. Import: BaseModel, Field, EmailStr from pydantic; UUID, datetime
3. Implement SignupRequest class:
   - username: str = Field(min_length=3, max_length=50)
   - email: EmailStr
   - password: str = Field(min_length=8)
   - Add docstring
4. Implement LoginRequest class:
   - email: EmailStr
   - password: str (no min_length for login)
   - Add docstring
5. Implement UserResponse class:
   - id: UUID, username: str, email: str, created_at: datetime
   - Docstring noting password_hash exclusion
6. Implement AuthResponse class:
   - user: UserResponse, token: str
   - Add docstring
7. Add module-level docstring explaining schema purposes
8. Run tests: `pytest backend/tests/test_auth_schemas.py` (EXPECT ALL TO PASS)

**Acceptance Criteria**:
- [ ] All 4 schemas implemented with correct field types
- [ ] SignupRequest validates username 3-50 chars, email format, password 8+ chars
- [ ] LoginRequest validates email format, password required (no length check)
- [ ] UserResponse excludes password_hash field
- [ ] All schema tests pass (9/9)
- [ ] Type hints on all fields (no Any types)
- [ ] Docstrings on all schemas

**Dependencies**: Task 2.2 (tests written)
**Estimated Time**: 15 minutes
**Files Created**: `backend/schemas/auth.py`

**Success Indicator**: `pytest backend/tests/test_auth_schemas.py -v` shows 9 passed

---

## Phase 3: User Story 1 - Signup Endpoint (P1)

### Task 3.1: Write Signup Endpoint Tests (RED Phase)
**Description**: Write comprehensive tests for POST /auth/signup BEFORE implementing endpoint

**Steps**:
1. Create backend/tests/test_auth_routes.py
2. Import TestClient from fastapi.testclient, main app, models, jwt decoder
3. Write test functions (WILL FAIL initially):
   - `test_signup_success()`: POST valid data, expect 201 with user and token
   - `test_signup_duplicate_username()`: Create user, signup with same username, expect 409
   - `test_signup_duplicate_email_case_insensitive()`: Create "test@example.com", signup with "TEST@Example.COM", expect 409
   - `test_signup_short_username()`: POST username "ab", expect 422
   - `test_signup_invalid_email()`: POST email "notanemail", expect 422
   - `test_signup_short_password()`: POST password "Short1", expect 422
   - `test_signup_password_hashed_in_db()`: Signup, query DB, verify password_hash starts with "$2b$12$"
   - `test_signup_password_not_in_response()`: Verify password_hash NOT in response JSON
   - `test_signup_jwt_token_structure()`: Decode token, verify sub, email, exp (7 days), iat fields
   - `test_signup_email_normalized_lowercase()`: Signup with "Test@EXAMPLE.com", verify stored as "test@example.com"
4. Use TestClient for requests
5. Use session fixture for database operations
6. Run tests: `pytest backend/tests/test_auth_routes.py::test_signup*` (EXPECT ALL TO FAIL)

**Acceptance Criteria**:
- [ ] 10 signup test functions written
- [ ] Tests cover success case, duplicate checking, validation, security
- [ ] Tests verify password hashing, JWT structure, email normalization
- [ ] All tests currently FAIL (RED phase - endpoint not implemented)
- [ ] Tests use database session for verification

**Dependencies**: Task 2.1 (fixtures), Task 2.3 (schemas implemented)
**Estimated Time**: 30 minutes
**Files Modified**: `backend/tests/test_auth_routes.py`

**Test Code Template**:
```python
from fastapi.testclient import TestClient
from main import app
from jose import jwt
import os

client = TestClient(app)

def test_signup_success(session, valid_signup_data):
    response = client.post("/auth/signup", json=valid_signup_data)
    assert response.status_code == 201
    data = response.json()
    assert "user" in data
    assert "token" in data
    assert data["user"]["username"] == valid_signup_data["username"]
    assert data["user"]["email"] == valid_signup_data["email"].lower()
    assert "password_hash" not in data["user"]

def test_signup_duplicate_username(session, create_test_user):
    user, _ = create_test_user(session, username="testuser")
    response = client.post("/auth/signup", json={
        "username": "testuser",
        "email": "different@example.com",
        "password": "SecurePass123"
    })
    assert response.status_code == 409
    assert "Username already exists" in response.json()["error"]

# ... 8 more test functions
```

---

### Task 3.2: Implement Signup Endpoint (GREEN Phase)
**Description**: Create POST /auth/signup route handler to make tests pass

**Steps**:
1. Create backend/routes/auth.py
2. Import: FastAPI, APIRouter, Depends, HTTPException, JSONResponse; sqlmodel; passlib; jose; datetime; schemas; models; db
3. Create CryptContext: `pwd_context = CryptContext(schemes=["bcrypt"], bcrypt__rounds=12, deprecated="auto")`
4. Load BETTER_AUTH_SECRET from environment with validation
5. Implement helper `create_jwt_token(user_id: UUID, email: str) -> str`:
   - Create payload with sub (str(user_id)), email, exp (now + 7 days), iat (now)
   - Encode with jwt.encode(payload, BETTER_AUTH_SECRET, algorithm="HS256")
   - Return token string
6. Implement helper `error_response(status_code: int, message: str, code: str) -> JSONResponse`:
   - Return JSONResponse with {error, code, timestamp} format
7. Implement POST /auth/signup handler `signup_user(request: SignupRequest, session: Session = Depends(get_session)) -> AuthResponse`:
   - Check username uniqueness: query User by username, return 409 if exists
   - Check email uniqueness (case-insensitive): query User by LOWER(email), return 409 if exists
   - Hash password: `password_hash = pwd_context.hash(request.password)`
   - Create User with normalized email (lowercase), hashed password
   - session.add(), commit(), refresh()
   - Generate JWT token
   - Create UserResponse (exclude password_hash)
   - Return AuthResponse with 201 status
   - Catch database exceptions, return 500
8. Create router: `router = APIRouter(prefix="/auth", tags=["authentication"])`
9. Register signup route on router
10. Add type hints and docstrings
11. Run tests: `pytest backend/tests/test_auth_routes.py::test_signup*` (EXPECT ALL TO PASS)

**Acceptance Criteria**:
- [ ] POST /auth/signup endpoint functional
- [ ] Password hashed with bcrypt 12 rounds before storage
- [ ] Username and email uniqueness checked (409 on duplicate)
- [ ] Email normalized to lowercase before storage
- [ ] JWT token generated with 7-day expiration
- [ ] UserResponse excludes password_hash
- [ ] All 10 signup tests pass
- [ ] Error responses use standardized format

**Dependencies**: Task 3.1 (tests written), Task 2.3 (schemas)
**Estimated Time**: 45 minutes
**Files Created**: `backend/routes/auth.py`

**Success Indicator**: `pytest backend/tests/test_auth_routes.py::test_signup* -v` shows 10 passed

---

### Task 3.3: Register Auth Routes in Main App
**Description**: Include auth router in FastAPI application

**Steps**:
1. Read backend/main.py
2. Import auth router: `from routes.auth import router as auth_router`
3. Register router: `app.include_router(auth_router)`
4. Ensure /auth/* routes are accessible without JWT middleware (verify middleware config)
5. Add comment documenting authentication endpoints
6. Test endpoint accessible: `curl -X POST http://localhost:8000/auth/signup -H "Content-Type: application/json" -d '{"username":"test","email":"test@example.com","password":"password123"}'`

**Acceptance Criteria**:
- [ ] Auth router imported in main.py
- [ ] Router registered with app.include_router()
- [ ] /auth/* routes bypass JWT middleware (verify middleware configuration)
- [ ] Signup endpoint returns response (201 or 422, not 404)
- [ ] Integration tests pass

**Dependencies**: Task 3.2 (signup endpoint implemented)
**Estimated Time**: 5 minutes
**Files Modified**: `backend/main.py`

---

## Phase 4: User Story 2 - Login Endpoint (P2)

### Task 4.1: Write Login Endpoint Tests (RED Phase)
**Description**: Write comprehensive tests for POST /auth/login BEFORE implementing

**Steps**:
1. Open backend/tests/test_auth_routes.py
2. Write test functions (WILL FAIL initially):
   - `test_login_success()`: Create user, login with correct credentials, expect 200 with user and token
   - `test_login_wrong_password()`: Create user, login with wrong password, expect 401 "Invalid credentials"
   - `test_login_nonexistent_email()`: Login with email not in DB, expect 401 "Invalid credentials"
   - `test_login_case_insensitive_email()`: Create user "test@example.com", login with "TEST@Example.COM", expect 200
   - `test_login_invalid_email_format()`: POST invalid email, expect 422
   - `test_login_missing_password()`: POST without password field, expect 422
   - `test_login_jwt_token_valid()`: Login, decode token, verify sub is user_id, email matches, exp is 7 days
   - `test_login_password_verification()`: Create user with known password, login, verify token issued only on correct password
3. Use create_test_user fixture to setup users with known passwords
4. Verify error message is "Invalid credentials" for both wrong password and nonexistent user (security)
5. Run tests: `pytest backend/tests/test_auth_routes.py::test_login*` (EXPECT ALL TO FAIL)

**Acceptance Criteria**:
- [ ] 8 login test functions written
- [ ] Tests cover success, wrong password, nonexistent user, case-insensitive email
- [ ] Tests verify same error message for wrong password and nonexistent user (security)
- [ ] Tests verify JWT token structure and expiration
- [ ] All tests currently FAIL (RED phase)

**Dependencies**: Task 2.1 (fixtures), Task 3.2 (signup endpoint for token comparison)
**Estimated Time**: 25 minutes
**Files Modified**: `backend/tests/test_auth_routes.py`

**Test Code Template**:
```python
def test_login_success(session, create_test_user):
    user, plain_password = create_test_user(session, email="test@example.com", password="SecurePass123")
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "SecurePass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert "token" in data
    assert data["user"]["email"] == "test@example.com"

def test_login_wrong_password(session, create_test_user):
    user, _ = create_test_user(session, email="test@example.com", password="SecurePass123")
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "WrongPassword"
    })
    assert response.status_code == 401
    assert response.json()["error"] == "Invalid credentials"

# ... 6 more test functions
```

---

### Task 4.2: Implement Login Endpoint (GREEN Phase)
**Description**: Add POST /auth/login route handler to make tests pass

**Steps**:
1. Open backend/routes/auth.py
2. Implement POST /auth/login handler `login_user(request: LoginRequest, session: Session = Depends(get_session)) -> AuthResponse`:
   - Query User by email (case-insensitive): `select(User).where(func.lower(User.email) == request.email.lower())`
   - Return 401 "Invalid credentials" if user not found
   - Verify password: `is_valid = pwd_context.verify(request.password, user.password_hash)`
   - Return 401 "Invalid credentials" if password mismatch (SAME message as user not found)
   - Generate JWT token with create_jwt_token()
   - Create UserResponse (exclude password_hash and created_at for login)
   - Return AuthResponse with 200 status
   - Catch database exceptions, return 500
3. Register login route on router
4. Add type hints and docstring
5. Run tests: `pytest backend/tests/test_auth_routes.py::test_login*` (EXPECT ALL TO PASS)

**Acceptance Criteria**:
- [ ] POST /auth/login endpoint functional
- [ ] Email lookup is case-insensitive (LOWER() function)
- [ ] Password verified with passlib constant-time comparison
- [ ] Same error message ("Invalid credentials") for wrong password and nonexistent user
- [ ] JWT token generated with 7-day expiration
- [ ] All 8 login tests pass
- [ ] Response excludes password_hash and created_at

**Dependencies**: Task 4.1 (tests written), Task 3.2 (signup endpoint, helper functions)
**Estimated Time**: 30 minutes
**Files Modified**: `backend/routes/auth.py`

**Success Indicator**: `pytest backend/tests/test_auth_routes.py::test_login* -v` shows 8 passed

---

## Phase 5: User Story 3 - Logout Endpoint (P3)

### Task 5.1: Write Logout Endpoint Tests (RED Phase)
**Description**: Write tests for POST /auth/logout BEFORE implementing

**Steps**:
1. Open backend/tests/test_auth_routes.py
2. Write test functions (WILL FAIL initially):
   - `test_logout_success()`: POST to /auth/logout, expect 200 with success message
   - `test_logout_with_token()`: POST with Authorization header, expect 200 (token optional)
   - `test_logout_without_token()`: POST without Authorization header, expect 200 (stateless)
   - `test_logout_idempotent()`: Call logout multiple times, all return 200
3. Verify response message is "Successfully logged out"
4. Run tests: `pytest backend/tests/test_auth_routes.py::test_logout*` (EXPECT ALL TO FAIL)

**Acceptance Criteria**:
- [ ] 4 logout test functions written
- [ ] Tests verify 200 OK always returned
- [ ] Tests verify success message format
- [ ] Tests verify logout works with or without Authorization header
- [ ] All tests currently FAIL (RED phase)

**Dependencies**: Task 2.1 (fixtures)
**Estimated Time**: 10 minutes
**Files Modified**: `backend/tests/test_auth_routes.py`

**Test Code Template**:
```python
def test_logout_success():
    response = client.post("/auth/logout")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Successfully logged out"

def test_logout_idempotent():
    response1 = client.post("/auth/logout")
    response2 = client.post("/auth/logout")
    response3 = client.post("/auth/logout")
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response3.status_code == 200

# ... 2 more test functions
```

---

### Task 5.2: Implement Logout Endpoint (GREEN Phase)
**Description**: Add POST /auth/logout route handler (simple stateless operation)

**Steps**:
1. Open backend/routes/auth.py
2. Implement POST /auth/logout handler `logout_user() -> dict`:
   - Return {"message": "Successfully logged out"}
   - No authentication required (stateless JWT)
   - No database operations
   - Total implementation: ~5 lines
3. Add docstring noting stateless behavior and client responsibility
4. Register logout route on router
5. Run tests: `pytest backend/tests/test_auth_routes.py::test_logout*` (EXPECT ALL TO PASS)

**Acceptance Criteria**:
- [ ] POST /auth/logout endpoint functional
- [ ] Always returns 200 OK with success message
- [ ] No authentication required
- [ ] No database operations
- [ ] All 4 logout tests pass
- [ ] Response time < 50ms

**Dependencies**: Task 5.1 (tests written)
**Estimated Time**: 10 minutes
**Files Modified**: `backend/routes/auth.py`

**Success Indicator**: `pytest backend/tests/test_auth_routes.py::test_logout* -v` shows 4 passed

---

## Phase 6: Integration and Polish

### Task 6.1: Run Full Test Suite and Verify Coverage
**Description**: Execute all authentication tests and verify 100% code coverage

**Steps**:
1. Run all auth tests: `pytest backend/tests/test_auth_schemas.py backend/tests/test_auth_routes.py -v`
2. Check test coverage: `pytest --cov=routes.auth --cov=schemas.auth --cov-report=term-missing backend/tests/test_auth_*`
3. Verify coverage is 100% for routes/auth.py and schemas/auth.py
4. If coverage < 100%, identify missing test cases and add them
5. Generate HTML coverage report: `pytest --cov=routes.auth --cov=schemas.auth --cov-report=html backend/tests/test_auth_*`
6. Review coverage report in htmlcov/index.html

**Acceptance Criteria**:
- [ ] All 31+ tests pass (9 schema + 10 signup + 8 login + 4 logout)
- [ ] Test coverage 100% for routes/auth.py
- [ ] Test coverage 100% for schemas/auth.py
- [ ] No uncovered lines in coverage report
- [ ] HTML coverage report generated

**Dependencies**: All implementation tasks (3.2, 4.2, 5.2) complete
**Estimated Time**: 15 minutes
**Files Verified**: `backend/routes/auth.py`, `backend/schemas/auth.py`

**Success Indicator**: Coverage report shows 100% for both files, all tests passing

---

### Task 6.2: Type Checking with Mypy [P]
**Description**: Run mypy strict mode to verify type safety

**Steps**:
1. Run mypy on auth modules: `mypy backend/routes/auth.py backend/schemas/auth.py --strict`
2. Fix any type errors (e.g., missing return type hints, Any types)
3. Verify no "Any" types used (except unavoidable JWT payload dict)
4. Add type: ignore comments only if absolutely necessary with justification
5. Re-run mypy until no errors

**Acceptance Criteria**:
- [ ] mypy --strict passes for routes/auth.py
- [ ] mypy --strict passes for schemas/auth.py
- [ ] No "Any" types except JWT payload (unavoidable)
- [ ] All function signatures have return type hints
- [ ] All parameters have type hints

**Dependencies**: Task 3.2, 4.2, 5.2 (all endpoints implemented)
**Estimated Time**: 10 minutes
**Files Verified**: `backend/routes/auth.py`, `backend/schemas/auth.py`

---

### Task 6.3: Manual Testing with Curl [P]
**Description**: Perform manual end-to-end testing using curl commands

**Steps**:
1. Start backend server: `cd backend && uvicorn main:app --reload --port 8000`
2. Test signup: `curl -X POST http://localhost:8000/auth/signup -H "Content-Type: application/json" -d '{"username":"manualtest","email":"manual@example.com","password":"SecurePass123"}'`
   - Verify 201 response with user and token
   - Copy token for next test
3. Test login: `curl -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d '{"email":"manual@example.com","password":"SecurePass123"}'`
   - Verify 200 response with user and token
4. Test duplicate signup: `curl -X POST http://localhost:8000/auth/signup -H "Content-Type: application/json" -d '{"username":"manualtest","email":"manual2@example.com","password":"SecurePass123"}'`
   - Verify 409 "Username already exists"
5. Test wrong password: `curl -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d '{"email":"manual@example.com","password":"WrongPassword"}'`
   - Verify 401 "Invalid credentials"
6. Test logout: `curl -X POST http://localhost:8000/auth/logout`
   - Verify 200 "Successfully logged out"
7. Decode JWT token: `python -c "from jose import jwt; print(jwt.get_unverified_claims('TOKEN_HERE'))"`
   - Verify payload has sub, email, exp, iat

**Acceptance Criteria**:
- [ ] Signup creates user and returns token
- [ ] Login with correct credentials returns token
- [ ] Duplicate username returns 409
- [ ] Wrong password returns 401
- [ ] Logout returns 200
- [ ] JWT token has correct structure (sub, email, exp 7 days, iat)
- [ ] All response times < 500ms for signup/login

**Dependencies**: Task 3.3 (routes registered in main.py)
**Estimated Time**: 15 minutes
**Manual Testing**: Requires running backend server

---

### Task 6.4: Update API Documentation [P]
**Description**: Verify FastAPI auto-generated docs include auth endpoints

**Steps**:
1. Start backend server: `uvicorn main:app --reload --port 8000`
2. Open browser to http://localhost:8000/docs
3. Verify three auth endpoints visible:
   - POST /auth/signup with SignupRequest schema
   - POST /auth/login with LoginRequest schema
   - POST /auth/logout (no request body)
4. Verify response schemas show AuthResponse structure
5. Test each endpoint using Swagger UI "Try it out" feature
6. Verify error responses documented (400, 401, 409, 422, 500)

**Acceptance Criteria**:
- [ ] /docs page shows all three auth endpoints
- [ ] Request schemas displayed correctly
- [ ] Response schemas displayed correctly
- [ ] "Try it out" feature works for all endpoints
- [ ] Error responses documented

**Dependencies**: Task 3.3 (routes registered)
**Estimated Time**: 10 minutes
**Manual Testing**: Requires browser

---

### Task 6.5: Update Environment Configuration Documentation [P]
**Description**: Document authentication configuration in .env.example

**Steps**:
1. Read backend/.env.example
2. Verify BETTER_AUTH_SECRET documented (should exist from jwt-auth-middleware)
3. Add comment section for authentication configuration
4. Document bcrypt rounds (hardcoded to 12)
5. Document JWT expiration (hardcoded to 7 days)
6. Add security note about changing BETTER_AUTH_SECRET invalidating tokens

**Acceptance Criteria**:
- [ ] .env.example documents BETTER_AUTH_SECRET
- [ ] Comments explain bcrypt rounds configuration
- [ ] Comments explain JWT expiration
- [ ] Security notes about secret rotation
- [ ] Example secret format shown

**Dependencies**: None (documentation task)
**Estimated Time**: 5 minutes
**Files Modified**: `backend/.env.example`

---

## Phase 7: Final Verification

### Task 7.1: Complete Feature Checklist
**Description**: Verify all functional requirements and success criteria met

**Steps**:
1. Review spec.md functional requirements (FR-001 through FR-025)
2. Check each requirement against implementation
3. Run automated tests for each requirement
4. Verify success criteria (SC-001 through SC-014)
5. Document any deviations or incomplete items

**Acceptance Criteria**:
- [ ] All 25 functional requirements implemented
- [ ] All 14 success criteria verified
- [ ] POST /auth/signup functional with validation
- [ ] POST /auth/login functional with verification
- [ ] POST /auth/logout functional
- [ ] Password hashing with bcrypt 12 rounds
- [ ] JWT generation with 7-day expiration
- [ ] Duplicate checking returns 409
- [ ] Invalid input returns 422
- [ ] No password_hash in responses
- [ ] 100% test coverage
- [ ] All tests passing

**Dependencies**: All previous tasks complete
**Estimated Time**: 20 minutes
**Verification**: Review against spec.md requirements

---

### Task 7.2: Create Feature Summary Document
**Description**: Document implementation completion and known limitations

**Steps**:
1. Create specs/007-auth-endpoints/IMPLEMENTATION_COMPLETE.md
2. Document what was implemented (3 endpoints, schemas, tests)
3. List files created/modified
4. Document test coverage statistics
5. List known limitations (e.g., no token revocation, no rate limiting)
6. Add performance benchmarks (signup/login response times)
7. Document next steps (integration with frontend, rate limiting future)

**Acceptance Criteria**:
- [ ] Summary document created
- [ ] All implemented features listed
- [ ] File manifest included
- [ ] Test statistics documented
- [ ] Known limitations documented
- [ ] Performance metrics recorded

**Dependencies**: Task 7.1 (verification complete)
**Estimated Time**: 15 minutes
**Files Created**: `specs/007-auth-endpoints/IMPLEMENTATION_COMPLETE.md`

---

## Task Summary

| Phase | Tasks | Estimated Time | Dependencies |
|-------|-------|----------------|--------------|
| Phase 1: Setup | 3 tasks | 7 minutes | None (all parallelizable) |
| Phase 2: Foundation | 3 tasks | 45 minutes | Passlib installed |
| Phase 3: Signup (P1) | 3 tasks | 80 minutes | Foundation complete |
| Phase 4: Login (P2) | 2 tasks | 55 minutes | Signup complete |
| Phase 5: Logout (P3) | 2 tasks | 20 minutes | Login complete |
| Phase 6: Polish | 5 tasks | 55 minutes | All endpoints complete (4 parallelizable) |
| Phase 7: Verification | 2 tasks | 35 minutes | Polish complete |
| **TOTAL** | **20 tasks** | **~5 hours** | Sequential + parallel |

---

## Test Execution Plan

### Red-Green-Refactor Cycle

1. **RED**: Write tests (Tasks 2.2, 3.1, 4.1, 5.1) - Tests FAIL
2. **GREEN**: Implement features (Tasks 2.3, 3.2, 4.2, 5.2) - Tests PASS
3. **REFACTOR**: Polish and optimize (Phase 6)

### Test Coverage Targets

| Module | Target Coverage | Test File |
|--------|----------------|-----------|
| schemas/auth.py | 100% | test_auth_schemas.py |
| routes/auth.py | 100% | test_auth_routes.py |
| Combined | 100% | Both files |

---

## Definition of Done

- [ ] All 20 tasks completed
- [ ] All 31+ tests passing
- [ ] 100% code coverage for auth modules
- [ ] Mypy strict mode passes
- [ ] Manual testing with curl successful
- [ ] FastAPI docs show all endpoints
- [ ] No password_hash in any response
- [ ] Password hashing with bcrypt 12 rounds verified
- [ ] JWT tokens have 7-day expiration verified
- [ ] Duplicate checking returns 409 verified
- [ ] Invalid credentials return 401 verified
- [ ] Performance < 500ms for signup/login verified
- [ ] Feature summary document created

---

## Notes

- TDD approach ensures tests are written BEFORE implementation
- Parallel tasks marked with [P] can be executed simultaneously
- Each phase has clear dependencies and cannot start until prerequisites met
- RED-GREEN-REFACTOR cycle enforced (write failing tests, make them pass, polish)
- 100% test coverage is non-negotiable per constitution
- Type safety enforced with mypy strict mode
- Security verified: no password_hash exposure, bcrypt 12 rounds, JWT 7-day exp
