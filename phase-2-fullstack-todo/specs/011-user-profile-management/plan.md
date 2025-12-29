# Implementation Plan: User Profile Management Endpoints

**Feature**: User Profile Management Endpoints (GET and PUT)
**Branch**: `011-user-profile-management`
**Created**: 2025-12-25
**Status**: Planning

---

## Executive Summary

This plan outlines the implementation of two secure user profile management endpoints: GET for retrieving user profiles and PUT for updating username/email with duplicate checking. The implementation follows existing patterns from task CRUD operations (CHUNK 4-6) while adding duplicate validation logic and password exclusion security measures.

**Key Design Decisions**:
1. Password exclusion via Pydantic response_model (not manual filtering)
2. Duplicate checking excludes current user in WHERE clause
3. Case-sensitive username, case-insensitive email comparison
4. Atomic updates with database transactions
5. Service layer handles business logic, routes handle HTTP concerns

---

## Technical Context

### Existing Infrastructure (Already Implemented)

**Authentication & Middleware**:
- JWT middleware at `backend/middleware/auth_middleware.py`
- `get_user_id_from_token()` dependency returns authenticated user ID
- Token verification using `BETTER_AUTH_SECRET` from environment

**Database Layer**:
- SQLModel ORM with Neon PostgreSQL
- User model exists in `backend/models.py` with fields: id, username, email, password_hash, created_at, updated_at
- Database session management via `get_session()` dependency in `backend/db.py`
- Unique constraints on username and email (database level)

**Project Structure**:
```
backend/
├── routes/          # API endpoints
│   ├── auth.py      # Authentication routes (existing)
│   └── tasks.py     # Task CRUD routes (existing pattern to follow)
├── schemas/         # Pydantic request/response models
│   ├── auth.py      # Auth schemas (existing)
│   └── task.py      # Task schemas (existing pattern to follow)
├── services/        # Business logic layer
│   └── task_service.py  # Task operations (existing pattern to follow)
├── models.py        # SQLModel database models
├── db.py            # Database session management
└── main.py          # FastAPI application entry point
```

**Testing Infrastructure**:
- Pytest with test fixtures for users and authentication
- TestClient for endpoint testing
- Database rollback after each test (via conftest.py)
- JWT token generation helpers in conftest.py

### New Components to Create

1. **Schemas** (`backend/schemas/user.py`):
   - `UserResponse`: Excludes password_hash, includes all other User fields
   - `UpdateUserRequest`: Optional username (3-50 chars) and email (valid format)

2. **Service Layer** (`backend/services/user_service.py`):
   - `get_user_profile(session, user_id)`: Query and return User
   - `update_user_profile(session, user_id, request)`: Update with duplicate checking

3. **Routes** (`backend/routes/users.py` - NEW FILE):
   - `GET /users/{user_id}`: Retrieve profile
   - `PUT /users/{user_id}`: Update profile

4. **Tests** (`backend/tests/test_user_profile.py` - NEW FILE):
   - Security tests (cross-user access, JWT validation)
   - Duplicate detection tests
   - Validation tests
   - Integration tests

---

## Constitution Check

### Compliance Review

**✅ I. Spec-Driven Development (SDD) with Agents/Skills**:
- Implementation follows spec-driven workflow
- Uses `user-management-specialist` agent
- Reuses patterns from task CRUD implementation

**✅ II. Clean Code with Single Responsibility Principle**:
- Service layer: Business logic and database operations
- Route layer: HTTP concerns and request/response handling
- Schema layer: Data validation and serialization
- Each function has single, clear responsibility

**✅ III. Type Safety and Strict Typing (NON-NEGOTIABLE)**:
- All functions use type hints
- Pydantic models for request/response validation
- SQLModel for database type safety
- No 'any' or untyped code

**✅ IV. Accessibility Compliance (WCAG 2.1 AA)**:
- N/A for backend API endpoints
- (Frontend profile UI would need accessibility compliance)

**✅ V. Performance-First Architecture**:
- Database queries use indexed fields (id, username, email)
- O(1) lookups by primary key (user_id)
- O(1) duplicate checks using unique index lookups
- Target: <1s for GET (95th percentile), <2s for PUT (95th percentile)

**✅ VI. Modular Architecture with Clear Boundaries**:
- Clear separation: routes → services → models
- Service functions reusable across different routes
- Schemas define API contract boundaries
- Follows existing FastAPI project structure

### Non-Functional Requirements Alignment

**Security**:
- Password hash never exposed (Pydantic response_model enforcement)
- User isolation enforced at route level (JWT user_id verification)
- Cross-user access blocked with 403 Forbidden
- SQL injection prevented by SQLModel parameterized queries

**Reliability**:
- Atomic database transactions (all-or-nothing updates)
- Proper error handling with appropriate status codes
- Database connection pooling handled by existing infrastructure
- Rollback on errors to maintain data consistency

**Performance**:
- Single database query for profile retrieval
- Duplicate checks use database indexes (username/email unique constraints)
- No N+1 query problems
- Efficient WHERE clauses with indexed columns

**Maintainability**:
- Follows established patterns from task CRUD endpoints
- Clear function naming and docstrings
- Testable design with dependency injection
- Separation of concerns (routes/services/schemas)

---

## Phase 0: Research & Design Decisions

### Research Summary

#### Decision 1: Password Exclusion Strategy

**Decision**: Use Pydantic `response_model` with `Config.from_attributes = True`

**Rationale**:
- Automatic field exclusion at serialization time
- Type-safe (ensures password_hash field cannot be accidentally included)
- Follows FastAPI best practices
- No manual filtering required in route handlers
- Compile-time safety (Pydantic validation catches schema mismatches)

**Alternatives Considered**:
- Manual deletion: `del user.password_hash` (error-prone, easy to forget)
- Dictionary filtering: `{k: v for k, v in user.dict().items() if k != 'password_hash'}` (verbose, not type-safe)
- SQLModel exclude parameter: Less explicit than dedicated response model

**Implementation**:
```python
class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Allows SQLModel → Pydantic conversion
```

#### Decision 2: Duplicate Checking Logic

**Decision**: Database-level unique constraints + explicit query check excluding current user

**Rationale**:
- Database enforces uniqueness (prevents race conditions)
- Explicit check provides better error messages (409 vs generic database error)
- Excluding current user allows updating username/email to same value (idempotent)
- Case-sensitive for username (industry standard for identifiers)
- Case-insensitive for email (RFC 5321 standard)

**Query Pattern**:
```python
# Check username duplicate (case-sensitive)
existing = session.exec(
    select(User).where(
        User.username == new_username,
        User.id != current_user_id
    )
).first()

# Check email duplicate (case-insensitive)
existing = session.exec(
    select(User).where(
        func.lower(User.email) == func.lower(new_email),
        User.id != current_user_id
    )
).first()
```

**Alternatives Considered**:
- Rely only on database constraints: Poor UX (generic error messages, no distinction between validation vs duplicate)
- Check without excluding current user: Users couldn't update email/username to current value (not idempotent)

#### Decision 3: Partial Update Handling

**Decision**: Use optional fields in `UpdateUserRequest`, update only provided fields

**Rationale**:
- Follows REST PUT semantics for partial updates
- More flexible than requiring both fields
- Validates at least one field provided (prevent empty updates)
- Matches user stories (update username only, email only, or both)

**Implementation**:
```python
class UpdateUserRequest(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None

# Validation: at least one field required
if not request.username and not request.email:
    raise HTTPException(status_code=422, detail="At least one field (username or email) must be provided")
```

**Alternatives Considered**:
- PATCH for partial, PUT for full replacement: Over-engineering for two fields
- Require both fields: Less flexible, doesn't match user needs (user stories show independent updates)

#### Decision 4: Transaction Management

**Decision**: Database session commits in service layer, route layer handles HTTP responses

**Rationale**:
- Service layer owns database transaction lifecycle
- Rollback on error handled by SQLModel session context
- Route layer focuses on HTTP concerns (status codes, error messages)
- Consistent with existing task service implementation

**Pattern**:
```python
# Service layer (user_service.py)
def update_user_profile(session: Session, user_id: UUID, request: UpdateUserRequest) -> Optional[User]:
    # Check duplicates, update user, commit
    session.commit()
    session.refresh(user)
    return user

# Route layer (users.py)
user = update_user_profile(session, user_id, request)
if not user:
    raise HTTPException(status_code=404, detail="User not found")
return UserResponse.from_orm(user)
```

---

## Phase 1: Data Model & Contracts

### Data Model

**Existing Model** (`backend/models.py`):
```python
class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(unique=True, index=True, min_length=3, max_length=50)
    email: str = Field(unique=True, index=True)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**No changes required** - Model already exists with all necessary fields and constraints.

### API Contracts

#### Contract 1: GET /users/{user_id}

**Purpose**: Retrieve authenticated user's profile information

**Request**:
- **Method**: GET
- **Path**: `/users/{user_id}`
- **Path Parameters**:
  - `user_id`: UUID (must match authenticated user from JWT)
- **Headers**:
  - `Authorization`: Bearer {jwt_token} (required)
- **Body**: None

**Response Success (200 OK)**:
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "username": "john_doe",
  "email": "john@example.com",
  "created_at": "2025-12-25T10:00:00Z",
  "updated_at": "2025-12-25T15:30:00Z"
}
```

**Response Errors**:
- `401 Unauthorized`: Missing or invalid JWT token
  ```json
  {"error": "Authentication required", "code": "AUTHENTICATION_ERROR", "timestamp": "2025-12-25T10:00:00Z"}
  ```
- `403 Forbidden`: user_id in path doesn't match authenticated user
  ```json
  {"error": "Not authorized to view this profile", "code": "AUTHORIZATION_ERROR", "timestamp": "2025-12-25T10:00:00Z"}
  ```
- `404 Not Found`: User ID doesn't exist
  ```json
  {"error": "User not found", "code": "NOT_FOUND", "timestamp": "2025-12-25T10:00:00Z"}
  ```

**Security Notes**:
- password_hash field NEVER included in response
- Cross-user profile access blocked
- JWT token required and verified

---

#### Contract 2: PUT /users/{user_id}

**Purpose**: Update authenticated user's username and/or email

**Request**:
- **Method**: PUT
- **Path**: `/users/{user_id}`
- **Path Parameters**:
  - `user_id`: UUID (must match authenticated user from JWT)
- **Headers**:
  - `Authorization`: Bearer {jwt_token} (required)
  - `Content-Type`: application/json
- **Body** (JSON, at least one field required):
```json
{
  "username": "new_username",  // Optional: 3-50 characters
  "email": "new@example.com"   // Optional: valid email format
}
```

**Examples**:
```json
// Update username only
{"username": "john_doe_2025"}

// Update email only
{"email": "john.new@example.com"}

// Update both
{"username": "john_new", "email": "john.new@example.com"}
```

**Response Success (200 OK)**:
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "username": "new_username",
  "email": "new@example.com",
  "created_at": "2025-12-25T10:00:00Z",
  "updated_at": "2025-12-25T16:45:00Z"
}
```

**Response Errors**:
- `401 Unauthorized`: Missing or invalid JWT token
- `403 Forbidden`: user_id in path doesn't match authenticated user
- `404 Not Found`: User ID doesn't exist
- `409 Conflict`: Username or email already taken by another user
  ```json
  {"error": "Username 'new_username' is already taken", "code": "DUPLICATE_USERNAME", "timestamp": "2025-12-25T10:00:00Z"}
  ```
  ```json
  {"error": "Email 'new@example.com' is already taken", "code": "DUPLICATE_EMAIL", "timestamp": "2025-12-25T10:00:00Z"}
  ```
- `422 Unprocessable Entity`: Validation errors
  ```json
  {"error": "At least one field (username or email) must be provided", "code": "VALIDATION_ERROR", "timestamp": "2025-12-25T10:00:00Z"}
  ```
  ```json
  {"error": "Username must be between 3 and 50 characters", "code": "VALIDATION_ERROR", "timestamp": "2025-12-25T10:00:00Z"}
  ```
  ```json
  {"error": "Invalid email format", "code": "VALIDATION_ERROR", "timestamp": "2025-12-25T10:00:00Z"}
  ```

**Security Notes**:
- password_hash never exposed
- Duplicate checking prevents account enumeration through different error responses (409 for duplicates vs 404 for non-existent users keeps cross-user access attempt ambiguous)
- Updated_at timestamp automatically set

---

## Phase 2: Implementation Strategy

### Architecture Overview

```
Request Flow:
┌────────────┐     ┌──────────────┐     ┌────────────────┐     ┌──────────┐
│   Client   │────→│ JWT Middleware│────→│  Route Layer   │────→│ Service  │
│  (Bearer   │     │ (verify token)│     │ (HTTP logic)   │     │  Layer   │
│   token)   │     └──────────────┘     └────────────────┘     └──────────┘
└────────────┘             │                      │                    │
                           ↓                      ↓                    ↓
                    user_id from JWT    Validate user_id match    Query/Update DB
                                        Return HTTP response      Return models
```

### Component Implementation Order

#### 1. Schemas (`backend/schemas/user.py`)

**Priority**: First (defines API contract)

**File Structure**:
```python
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID

class UserResponse(BaseModel):
    """User profile response (excludes password_hash)."""
    id: UUID
    username: str
    email: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UpdateUserRequest(BaseModel):
    """Request to update user profile."""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
```

**Tests to Write**:
- Schema validation (username length, email format)
- At least one field required validation
- Password_hash exclusion verification

---

#### 2. Service Layer (`backend/services/user_service.py`)

**Priority**: Second (business logic before routes)

**Functions**:

```python
def get_user_profile(session: Session, user_id: UUID) -> Optional[User]:
    """
    Retrieve user profile by ID.

    Args:
        session: Database session
        user_id: User UUID

    Returns:
        User model if found, None otherwise
    """
    return session.get(User, user_id)


def update_user_profile(
    session: Session,
    user_id: UUID,
    request: UpdateUserRequest
) -> Optional[User]:
    """
    Update user profile with duplicate checking.

    Args:
        session: Database session
        user_id: User UUID
        request: Update request with username/email

    Returns:
        Updated User model if successful, None if user not found

    Raises:
        HTTPException: 409 if username/email already taken
        HTTPException: 422 if validation fails
    """
    # Get user
    user = session.get(User, user_id)
    if not user:
        return None

    # Validate at least one field provided
    if not request.username and not request.email:
        raise HTTPException(
            status_code=422,
            detail="At least one field (username or email) must be provided"
        )

    # Check username duplicate (case-sensitive)
    if request.username:
        existing = session.exec(
            select(User).where(
                User.username == request.username,
                User.id != user_id
            )
        ).first()
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Username '{request.username}' is already taken"
            )
        user.username = request.username

    # Check email duplicate (case-insensitive)
    if request.email:
        existing = session.exec(
            select(User).where(
                func.lower(User.email) == func.lower(request.email),
                User.id != user_id
            )
        ).first()
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Email '{request.email}' is already taken"
            )
        user.email = request.email

    # Update timestamp and commit
    user.updated_at = datetime.utcnow()
    session.add(user)
    session.commit()
    session.refresh(user)

    return user
```

**Tests to Write**:
- Get profile success
- Get profile not found (returns None)
- Update username success
- Update email success
- Update both success
- Duplicate username detection (409)
- Duplicate email detection (409)
- Case-insensitive email duplicate checking
- No fields provided (422)
- Current user can update to same username/email (idempotent)

---

#### 3. Routes (`backend/routes/users.py`)

**Priority**: Third (after schemas and services)

**Router Setup**:
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from uuid import UUID

from db import get_session
from middleware.auth_middleware import get_user_id_from_token
from services.user_service import get_user_profile, update_user_profile
from schemas.user import UserResponse, UpdateUserRequest

router = APIRouter(prefix="/users", tags=["users"])
```

**GET Endpoint**:
```python
@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    current_user_id: str = Depends(get_user_id_from_token),
    session: Session = Depends(get_session)
):
    """Get user profile (must be own profile)."""
    # Verify user_id matches JWT
    if str(user_id) != current_user_id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view this profile"
        )

    # Get profile
    user = get_user_profile(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
```

**PUT Endpoint**:
```python
@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    request: UpdateUserRequest,
    current_user_id: str = Depends(get_user_id_from_token),
    session: Session = Depends(get_session)
):
    """Update user profile (must be own profile)."""
    # Verify user_id matches JWT
    if str(user_id) != current_user_id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to update this profile"
        )

    # Update profile (service handles duplicates and validation)
    try:
        user = update_user_profile(session, user_id, request)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise  # Re-raise 409/422 from service layer
```

**Router Registration** (`backend/main.py`):
```python
from routes import users

app.include_router(users.router)
```

**Tests to Write**:
- GET success (authenticated, own profile)
- GET cross-user access blocked (403)
- GET unauthenticated (401)
- GET non-existent user (404)
- PUT username success
- PUT email success
- PUT both success
- PUT duplicate username (409)
- PUT duplicate email (409)
- PUT cross-user blocked (403)
- PUT validation errors (422)
- Password hash never in response

---

#### 4. Integration Tests (`backend/tests/test_user_profile.py`)

**Priority**: Fourth (test all layers together)

**Test Structure**:
```python
import pytest
from fastapi.testclient import TestClient
from uuid import UUID, uuid4

# Test fixtures in conftest.py:
# - client: TestClient
# - session: Database session
# - test_user: User with JWT token
# - auth_headers: {"Authorization": "Bearer <token>"}

def test_get_profile_success(client, test_user, auth_headers):
    """Test successful profile retrieval."""
    user, password, token = test_user
    response = client.get(f"/users/{user.id}", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(user.id)
    assert data["username"] == user.username
    assert data["email"] == user.email
    assert "password_hash" not in data  # CRITICAL SECURITY CHECK

def test_get_profile_cross_user_blocked(client, test_user, auth_headers):
    """Test cross-user access blocked."""
    other_user_id = uuid4()
    response = client.get(f"/users/{other_user_id}", headers=auth_headers)
    assert response.status_code == 403

def test_update_username_duplicate(client, test_user, auth_headers, session):
    """Test duplicate username detection."""
    # Create another user
    other_user = User(username="existing_user", email="other@example.com", password_hash="hash")
    session.add(other_user)
    session.commit()

    user, _, _ = test_user
    response = client.put(
        f"/users/{user.id}",
        json={"username": "existing_user"},
        headers=auth_headers
    )
    assert response.status_code == 409
    assert "already taken" in response.json()["error"]

# ... more tests covering all scenarios
```

**Test Categories**:
1. **Security Tests** (8 tests):
   - Password exclusion in all responses
   - Cross-user access blocked (GET and PUT)
   - JWT validation (401 errors)
   - User isolation enforcement

2. **Duplicate Detection Tests** (6 tests):
   - Duplicate username (409)
   - Duplicate email (409)
   - Case-insensitive email duplicates
   - Idempotent updates (same username/email allowed)

3. **Validation Tests** (4 tests):
   - Username length validation
   - Email format validation
   - At least one field required
   - Invalid UUID format

4. **Integration Tests** (6 tests):
   - Full GET flow (auth → route → service → DB)
   - Full PUT flow (auth → route → service → duplicate check → DB update)
   - Updated_at timestamp verification
   - Transaction rollback on error

**Total**: 24 tests minimum

---

## Phase 3: Testing Strategy

### Unit Tests

**Schemas** (`test_user_schemas.py`):
- Validate UserResponse excludes password_hash
- Validate UpdateUserRequest field constraints
- Test Pydantic validation errors

**Services** (`test_user_service.py`):
- Test get_user_profile with existing/non-existent users
- Test update_user_profile success cases
- Test duplicate detection logic
- Test validation errors
- Mock database session

**Routes** (`test_user_routes.py`):
- Test endpoint responses
- Test JWT verification
- Test user_id matching
- Mock service layer

### Integration Tests

**Full Flow** (`test_user_profile.py`):
- Test complete request → response cycle
- Use real database (test database)
- Test transactions and rollbacks
- Test concurrent requests

### Test Coverage Target

- **Minimum**: 95% code coverage
- **Critical Paths**: 100% coverage for:
  - Password exclusion logic
  - Duplicate checking logic
  - User isolation verification
  - Error handling paths

---

## Phase 4: Deployment Checklist

### Pre-Deployment Validation

- [ ] All 24+ tests passing
- [ ] Code coverage ≥95%
- [ ] Type checking passes (mypy)
- [ ] Linting passes (ruff/black)
- [ ] No security vulnerabilities (password_hash never exposed)
- [ ] API documentation generated (OpenAPI/Swagger)

### Database Verification

- [ ] User model has username unique constraint
- [ ] User model has email unique constraint
- [ ] Indexes exist on username and email fields
- [ ] updated_at field has default value

### Environment Variables

- [ ] `DATABASE_URL` configured
- [ ] `BETTER_AUTH_SECRET` configured
- [ ] Connection pool settings optimized

### Performance Validation

- [ ] GET endpoint <1s (95th percentile)
- [ ] PUT endpoint <2s (95th percentile)
- [ ] Concurrent request handling (500 users)
- [ ] No N+1 query issues

---

## Architecture Decision Records (ADRs)

### ADR-001: Password Exclusion via Pydantic Response Model

**Status**: Accepted

**Context**: Need to ensure password_hash field is never exposed in API responses while maintaining type safety.

**Decision**: Use Pydantic `response_model` parameter on FastAPI routes with a dedicated `UserResponse` schema that excludes password_hash.

**Consequences**:
- ✅ Type-safe (compile-time verification)
- ✅ Automatic exclusion (no manual filtering)
- ✅ Clear API contract (schema documents excluded fields)
- ✅ Follows FastAPI best practices
- ⚠️ Requires separate response schema (slight overhead)

**Alternatives**:
- Manual deletion: Error-prone, not type-safe
- Dictionary filtering: Verbose, not type-safe
- SQLModel exclude: Less explicit

---

### ADR-002: Duplicate Checking Strategy

**Status**: Accepted

**Context**: Need to prevent duplicate usernames/emails while allowing users to update to their current values (idempotent).

**Decision**: Implement explicit database queries that exclude the current user from duplicate checks.

**Consequences**:
- ✅ Better error messages (409 vs generic DB error)
- ✅ Idempotent updates (user can update to same value)
- ✅ Case-sensitive username, case-insensitive email
- ✅ Prevents race conditions (database enforces uniqueness)
- ⚠️ Requires two database queries for updates with both fields

**Alternatives**:
- Database-only enforcement: Poor UX, no idempotency
- Application-level only: Race condition risk

---

### ADR-003: Partial Update Semantics

**Status**: Accepted

**Context**: Users need to update username only, email only, or both fields independently.

**Decision**: Use PUT with optional fields, validate at least one field provided.

**Consequences**:
- ✅ Flexible (supports all user stories)
- ✅ REST-compliant (PUT for updates)
- ✅ Simple validation
- ⚠️ Deviates slightly from strict PUT semantics (typically full replacement)

**Alternatives**:
- PATCH for partial, PUT for full: Over-engineering
- Require both fields: Less flexible

---

## Risk Assessment

### High Risk Items

**R1: Password Hash Exposure**
- **Impact**: Critical security breach
- **Mitigation**: Pydantic response_model enforcement + comprehensive tests
- **Verification**: Test coverage 100% for password exclusion paths

**R2: Race Conditions in Duplicate Checking**
- **Impact**: Multiple users could get same username/email
- **Mitigation**: Database unique constraints + explicit checks
- **Verification**: Concurrent update tests

**R3: Cross-User Profile Access**
- **Impact**: Privacy violation
- **Mitigation**: JWT verification + user_id matching in routes
- **Verification**: Security tests covering all cross-user scenarios

### Medium Risk Items

**R4: Performance Degradation Under Load**
- **Impact**: Slow responses, poor UX
- **Mitigation**: Database indexes, connection pooling
- **Verification**: Load testing with 500 concurrent users

**R5: Incomplete Validation**
- **Impact**: Invalid data in database
- **Mitigation**: Pydantic validation + database constraints
- **Verification**: Validation test suite

---

## Success Metrics

### Functional Metrics

- ✅ All 17 functional requirements implemented
- ✅ All 4 user stories testable and passing
- ✅ All 7 edge cases handled
- ✅ All 24+ tests passing

### Performance Metrics

- ✅ GET requests <1s (95th percentile)
- ✅ PUT requests <2s (95th percentile)
- ✅ 500 concurrent users supported
- ✅ 99.9% success rate (excluding user errors)

### Security Metrics

- ✅ 100% password exclusion (zero breaches)
- ✅ 100% cross-user access blocked
- ✅ 100% duplicate detection accuracy
- ✅ All validation errors return correct status codes

### Code Quality Metrics

- ✅ 95%+ code coverage
- ✅ Zero type errors (mypy)
- ✅ Zero linting errors
- ✅ All docstrings present

---

## Next Steps

After this plan is approved:

1. **Create tasks.md**: Break down implementation into atomic tasks
2. **Run /sp.tasks**: Generate detailed task list with test cases
3. **Run /sp.implement**: Execute implementation with user-management-specialist agent
4. **Verify tests**: Ensure all 24+ tests passing
5. **Create PR**: Merge 011-user-profile-management → main

**Estimated Implementation Time**:
- Schemas: 30 minutes
- Services: 1 hour (duplicate logic)
- Routes: 45 minutes
- Tests: 2 hours (comprehensive coverage)
- **Total**: ~4-5 hours

---

## Appendix: File Checklist

### Files to Create

- [ ] `backend/schemas/user.py` - UserResponse, UpdateUserRequest
- [ ] `backend/services/user_service.py` - get_user_profile, update_user_profile
- [ ] `backend/routes/users.py` - GET and PUT endpoints
- [ ] `backend/tests/test_user_profile.py` - Integration tests

### Files to Modify

- [ ] `backend/main.py` - Register users router
- [ ] `backend/tests/conftest.py` - Add user fixtures (if needed)

### Files to Reference (No Changes)

- ✅ `backend/models.py` - User model (already exists)
- ✅ `backend/db.py` - Database session (already exists)
- ✅ `backend/middleware/auth_middleware.py` - JWT verification (already exists)
