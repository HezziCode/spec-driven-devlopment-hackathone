# Implementation Plan: User Authentication Endpoints

**Branch**: `007-auth-endpoints` | **Date**: 2025-12-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-auth-endpoints/spec.md`

## Summary

This implementation plan defines the technical approach for building three user authentication API endpoints in the FastAPI backend. The primary requirement is to create POST /auth/signup (accepts username, email, password with Pydantic validation, checks uniqueness returning 409 on duplicates, hashes password with bcrypt 12 rounds via passlib, creates User record, generates JWT token with 7-day expiration, returns 201 with user and token), POST /auth/login (accepts email and password, finds user returning 401 if not found, verifies password hash returning 401 on mismatch, generates JWT token, returns 200 with user and token), and POST /auth/logout (returns 200 with success message for stateless JWT). The technical approach involves creating Pydantic schemas in schemas/auth.py (SignupRequest with field validation, LoginRequest, UserResponse excluding password_hash, AuthResponse), implementing route handlers in routes/auth.py using passlib CryptContext with bcrypt for hashing, python-jose for JWT generation with BETTER_AUTH_SECRET and 7-day expiration, SQLModel queries for user creation and lookup with case-insensitive email handling, and standardized error responses (409 Conflict for duplicates, 401 Unauthorized for invalid credentials, 422 for validation errors). This feature completes the authentication flow by enabling user registration and login, issuing JWT tokens that will be verified by the existing JWT middleware for protected endpoints.

## Technical Context

**Language/Version**: Python 3.11+ (as specified in constitution for Phase II backend)
**Primary Dependencies**:
- passlib[bcrypt] 1.7+ (password hashing with bcrypt scheme)
- python-jose[cryptography] 3.3+ (JWT token generation, already installed)
- FastAPI 0.104+ (route handlers and dependency injection)
- SQLModel (database operations with User model, already installed)
- pydantic 2.5+ (schema validation with EmailStr, included with FastAPI)

**Storage**: Neon Serverless PostgreSQL (User model already created in database-foundation)
**Testing**: pytest 7.4+ with pytest-asyncio for async route tests
**Target Platform**: Linux server environment (part of FastAPI backend)
**Project Type**: Web backend API endpoints (authentication layer)
**Performance Goals**:
- Signup endpoint < 500ms response time (includes bcrypt hashing)
- Login endpoint < 300ms response time
- Logout endpoint < 50ms response time
- Password hashing with bcrypt 12 rounds < 200ms
- JWT token generation < 10ms

**Constraints**:
- Must use passlib with bcrypt scheme and 12 rounds (no other hashing algorithms)
- Must use python-jose for JWT generation (not PyJWT or other libraries)
- Must generate JWT with HS256 algorithm using BETTER_AUTH_SECRET
- Must set JWT expiration to 7 days from issuance
- Must check username uniqueness case-sensitive
- Must check email uniqueness case-insensitive (normalize to lowercase)
- Must never include password_hash in any API response
- Must return standardized error format {error, code, timestamp}
- Must use complete type hints (no Any types)
- Must follow Pydantic validation patterns with Field() constraints

**Scale/Scope**:
- 3 API endpoints (signup, login, logout)
- 4 Pydantic schemas (SignupRequest, LoginRequest, UserResponse, AuthResponse)
- 25 functional requirements from specification
- Expected to handle 10+ concurrent authentication requests
- Signup/login operations are write-heavy (database inserts/queries)

## Constitution Check

### ✅ Principle I: Spec-Driven Development with Agents/Skills
**Status**: PASS
**Rationale**: Implementation will use authentication-specialist agent with fastapi-auth-endpoints skill. All code generation automated via agents, no manual coding required. Agent provides proven patterns for authentication endpoints with password hashing and JWT generation.

### ✅ Principle II: Clean Code with Single Responsibility
**Status**: PASS
**Rationale**: Clear separation of concerns - routes/auth.py contains only route handler logic (request/response, orchestration), schemas/auth.py contains only Pydantic validation models. Password hashing abstracted via passlib CryptContext. JWT generation uses existing jwt_utils module. Each function has single purpose (signup, login, logout). All functions will have Google-style docstrings.

### ✅ Principle III: Type Safety (NON-NEGOTIABLE)
**Status**: PASS
**Rationale**: All route functions will have explicit type hints for parameters and return values. Pydantic schemas provide automatic type validation. All database operations typed with SQLModel. JWT payload typed as dict[str, Any] (unavoidable due to JWT spec). All other types fully specified (str, UUID, datetime, User, AuthResponse). Mypy strict mode will be enforced.

### ⚠️ Principle IV: Accessibility Compliance (WCAG 2.1 AA)
**Status**: NOT APPLICABLE
**Rationale**: Authentication endpoints are backend API with no UI components. Accessibility requirements apply to frontend only.

### ✅ Principle V: Performance-First Architecture
**Status**: PASS
**Rationale**: Database queries are O(1) lookups by primary key or indexed email/username fields. Bcrypt hashing is O(1) with configurable work factor (12 rounds balances security and performance). JWT generation is O(1) cryptographic operation. Uniqueness checks use database unique indexes for efficiency. No N+1 query problems. Case-insensitive email lookup uses LOWER() function with functional index.

### ✅ Principle VI: Modular Architecture with Clear Boundaries
**Status**: PASS
**Rationale**: Authentication routes clearly separated from other route modules. Schemas in dedicated schemas/auth.py file. Password hashing logic encapsulated in CryptContext. JWT generation reuses existing jwt_utils module. Database session management via FastAPI dependency injection. Error responses follow standardized format across application.

## Project Structure

### Documentation (this feature)

```text
specs/007-auth-endpoints/
├── plan.md              # This file (/sp.plan output)
├── spec.md              # Feature specification (already exists)
├── research.md          # Technology research and decisions
├── quickstart.md        # Quick setup guide for developers
├── contracts/           # Interface contracts
│   ├── signup-endpoint.md       # POST /auth/signup contract
│   ├── login-endpoint.md        # POST /auth/login contract
│   ├── logout-endpoint.md       # POST /auth/logout contract
│   └── schemas-contract.md      # Pydantic schemas interface
├── checklists/          # Quality validation
│   └── requirements.md  # Spec validation (already exists)
└── tasks.md             # Task breakdown (/sp.tasks - NOT created yet)
```

### Source Code (backend directory)

```text
backend/
├── routes/              # API route handlers
│   ├── __init__.py      # Already exists
│   └── auth.py          # NEW: Authentication endpoints
│                        # Contains: signup_user()
│                        # login_user()
│                        # logout_user()
│                        # Password hashing with passlib
│                        # JWT token generation
│                        # Duplicate checking
│                        # Error handling
│
├── schemas/             # Pydantic request/response schemas
│   ├── __init__.py      # Already exists
│   └── auth.py          # NEW: Authentication schemas
│                        # Contains: SignupRequest
│                        # LoginRequest
│                        # UserResponse
│                        # AuthResponse
│                        # Field validation
│
├── utils/               # Utility functions
│   ├── __init__.py      # Already exists
│   └── jwt_utils.py     # Already exists (reuse for JWT generation)
│
├── models.py            # SQLModel models (already exists with User model)
├── db.py                # Database session (already exists)
├── main.py              # FastAPI app (update to register auth routes)
├── .env                 # Environment variables (BETTER_AUTH_SECRET exists)
│
└── tests/               # Test suite
    ├── __init__.py      # Already exists
    ├── conftest.py      # Update with auth test fixtures
    ├── test_auth_routes.py    # NEW: Auth endpoint tests
    └── test_auth_schemas.py   # NEW: Schema validation tests
```

**Structure Decision**: Using web application structure with backend directory. Authentication routes go in routes/auth.py following FastAPI conventions. Schemas in schemas/auth.py for Pydantic models. Tests mirror source structure. Reuse existing jwt_utils.py for JWT generation. Database foundation and JWT middleware already complete.

## Complexity Tracking

> No constitution violations. All principles pass or not applicable to backend API endpoints.

---

## Implementation Strategy

### Phase 0: Research

*Output: research.md*

Research tasks to resolve technical unknowns:

1. **Passlib CryptContext Configuration**
   - Research correct setup for bcrypt with 12 rounds
   - Expected: `CryptContext(schemes=["bcrypt"], bcrypt__rounds=12)`

2. **Password Verification Pattern**
   - Research passlib verify() method usage
   - Expected: `pwd_context.verify(plain_password, password_hash)`

3. **JWT Token Generation with Expiration**
   - Research python-jose encode pattern with 7-day expiration
   - Expected: `jwt.encode({"sub": user_id, "exp": datetime.utcnow() + timedelta(days=7)}, SECRET, algorithm="HS256")`

4. **Case-Insensitive Email Lookup**
   - Research SQLModel/SQLAlchemy pattern for case-insensitive email queries
   - Expected: Use `func.lower(User.email) == email.lower()` with functional index

5. **Pydantic EmailStr Validation**
   - Research EmailStr field type for email validation
   - Expected: Import from pydantic and use as field type

6. **FastAPI Response Model with Exclusion**
   - Research how to exclude password_hash from response automatically
   - Expected: Use response_model with Pydantic schema excluding sensitive fields

### Phase 1: Design

*Outputs: quickstart.md, contracts/*

#### Quickstart Guide

Create `quickstart.md` with step-by-step setup:
1. Install passlib: `cd backend && uv add passlib[bcrypt]`
2. Verify BETTER_AUTH_SECRET in backend/.env (must be 32+ characters)
3. Test signup: `curl -X POST http://localhost:8000/auth/signup -H "Content-Type: application/json" -d '{"username":"testuser","email":"test@example.com","password":"SecurePass123"}'`
4. Test login: `curl -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d '{"email":"test@example.com","password":"SecurePass123"}'`
5. Test logout: `curl -X POST http://localhost:8000/auth/logout`
6. Verify JWT token: Copy token from signup/login response and use in protected endpoint

#### Endpoint Contracts

Create contract files documenting endpoint interfaces:

**contracts/signup-endpoint.md**: POST /auth/signup contract
- Method: POST
- Path: /auth/signup
- Request Body: `{"username": string, "email": string, "password": string}`
- Response (201): `{"user": {"id": UUID, "username": string, "email": string, "created_at": ISO8601}, "token": string}`
- Errors: 400 (bad request), 409 (duplicate), 422 (validation)

**contracts/login-endpoint.md**: POST /auth/login contract
- Method: POST
- Path: /auth/login
- Request Body: `{"email": string, "password": string}`
- Response (200): `{"user": {"id": UUID, "username": string, "email": string}, "token": string}`
- Errors: 400 (bad request), 401 (invalid credentials), 422 (validation)

**contracts/logout-endpoint.md**: POST /auth/logout contract
- Method: POST
- Path: /auth/logout
- Request Body: (empty)
- Response (200): `{"message": "Successfully logged out"}`
- Errors: None (always returns 200)

**contracts/schemas-contract.md**: Pydantic schemas interface
- SignupRequest: username (3-50 chars), email (EmailStr), password (min 8 chars)
- LoginRequest: email (EmailStr), password (str)
- UserResponse: id (UUID), username (str), email (str), created_at (datetime)
- AuthResponse: user (UserResponse), token (str)

---

## Implementation Files

### File 1: backend/schemas/auth.py

**Purpose**: Pydantic schemas for authentication request validation and response formatting.

**Key Components**:
- Import statements (pydantic, datetime, UUID, Field, EmailStr)
- SignupRequest schema with Field() constraints
  - username: str = Field(min_length=3, max_length=50)
  - email: EmailStr
  - password: str = Field(min_length=8)
  - Docstring with field descriptions
- LoginRequest schema
  - email: EmailStr
  - password: str
  - Docstring
- UserResponse schema (safe user data without password_hash)
  - id: UUID
  - username: str
  - email: str
  - created_at: datetime
  - Docstring noting password_hash exclusion
- AuthResponse schema
  - user: UserResponse
  - token: str
  - Docstring explaining usage in signup/login
- Type hints on all fields (no Any types)
- Config class for ORM mode if needed

**Dependencies**: pydantic, datetime, uuid

**Tests**: tests/test_auth_schemas.py (validation errors for invalid input, valid input passes, email format validation, password length validation)

### File 2: backend/routes/auth.py

**Purpose**: FastAPI route handlers for authentication endpoints (signup, login, logout).

**Key Components**:
- Import statements (fastapi, sqlmodel, passlib, jose, datetime, typing, models, schemas, db)
- CryptContext configuration for bcrypt
  - `pwd_context = CryptContext(schemes=["bcrypt"], bcrypt__rounds=12, deprecated="auto")`
  - Module-level constant
- Load BETTER_AUTH_SECRET from environment with validation
- Helper function: create_jwt_token(user_id: UUID, email: str) -> str
  - Creates payload with sub, email, exp (7 days), iat
  - Uses jwt.encode() with BETTER_AUTH_SECRET and HS256
  - Returns token string
  - Docstring
- Helper function: error_response(status_code: int, message: str, code: str) -> JSONResponse
  - Creates standardized error response with timestamp
  - Returns JSONResponse
  - Docstring
- POST /auth/signup route handler: signup_user(request: SignupRequest, session: Session = Depends(get_session)) -> AuthResponse
  - Pydantic validates request automatically
  - Check username uniqueness: query User by username
  - Check email uniqueness: query User by email (case-insensitive)
  - Return 409 Conflict if duplicate found
  - Hash password: pwd_context.hash(request.password)
  - Create User record with hashed password
  - Normalize email to lowercase before storage
  - session.add() and session.commit()
  - session.refresh(user) to get created_at
  - Generate JWT token with create_jwt_token()
  - Create UserResponse (excluding password_hash)
  - Return AuthResponse with 201 status
  - Error handling for database errors (return 500)
  - Docstring with parameters and response
- POST /auth/login route handler: login_user(request: LoginRequest, session: Session = Depends(get_session)) -> AuthResponse
  - Pydantic validates request
  - Query User by email (case-insensitive)
  - Return 401 "Invalid credentials" if user not found
  - Verify password: pwd_context.verify(request.password, user.password_hash)
  - Return 401 "Invalid credentials" if verification fails
  - Generate JWT token
  - Create UserResponse
  - Return AuthResponse with 200 status
  - Error handling for database errors
  - Docstring
- POST /auth/logout route handler: logout_user() -> dict
  - Returns {"message": "Successfully logged out"}
  - No authentication required (stateless JWT)
  - 200 OK status
  - Docstring noting stateless behavior
- Type hints on all parameters and return values
- Router object at end: router = APIRouter(prefix="/auth", tags=["authentication"])
- Register routes on router

**Dependencies**: fastapi, sqlmodel, passlib, python-jose, datetime, models, schemas, db

**Tests**: tests/test_auth_routes.py (signup success, signup duplicate username, signup duplicate email, signup invalid input, login success, login wrong password, login nonexistent user, logout always succeeds, password hashing verification, JWT token structure)

### File 3: backend/main.py (update)

**Purpose**: Register authentication routes in FastAPI application.

**Key Components**:
- Import auth router from routes.auth
- Register router: `app.include_router(auth.router)`
- Place registration with other route registrations
- Ensure /auth/* routes are accessible without JWT middleware (middleware already configured to bypass /auth/*)
- Docstring update noting authentication endpoints available

**Dependencies**: routes/auth.py

**Tests**: Integration tests in test_auth_routes.py verify routes are accessible

### File 4: backend/.env.example (update)

**Purpose**: Document password hashing configuration in environment template.

**Key Components**:
- Existing BETTER_AUTH_SECRET line (already documented in jwt-middleware)
- Add comment about bcrypt work factor (12 rounds hardcoded)
- Add comment about JWT expiration (7 days hardcoded)
- Security note about changing BETTER_AUTH_SECRET invalidating all tokens

**Dependencies**: None

**Tests**: None (documentation file)

### File 5: backend/tests/conftest.py (update)

**Purpose**: Add pytest fixtures for authentication testing.

**Key Components**:
- Fixture: create_test_user(session: Session, username: str = "testuser", email: str = "test@example.com", password: str = "TestPass123") -> tuple[User, str]
  - Hashes password with passlib
  - Creates User in database
  - Returns (user, plain_password) tuple for testing
  - Used in login tests
- Fixture: valid_signup_data() -> dict
  - Returns valid signup request payload
  - Used in signup tests
- Fixture: valid_login_data() -> dict
  - Returns valid login request payload
  - Used in login tests
- Fixture: authenticated_headers(test_user: User) -> dict
  - Generates JWT token for test user
  - Returns headers dict with Authorization bearer token
  - Used in protected endpoint tests (future)
- Update existing test database setup if needed

**Dependencies**: pytest, passlib, python-jose, models, schemas

**Tests**: None (test infrastructure)

### File 6: backend/tests/test_auth_schemas.py

**Purpose**: Unit tests for authentication Pydantic schemas.

**Key Components**:
- Test SignupRequest with valid data
  - Create schema with valid username, email, password
  - Verify fields populated correctly
  - Verify no validation errors
- Test SignupRequest with short username
  - Create schema with 2-character username
  - Verify ValidationError raised
  - Verify error message mentions min_length
- Test SignupRequest with long username
  - Create schema with 51-character username
  - Verify ValidationError raised
- Test SignupRequest with invalid email
  - Create schema with "notanemail" email
  - Verify ValidationError raised
  - Verify error message mentions email format
- Test SignupRequest with short password
  - Create schema with 7-character password
  - Verify ValidationError raised
  - Verify error message mentions min_length
- Test LoginRequest with valid data
  - Verify email and password fields work
- Test UserResponse excludes password_hash
  - Create UserResponse from User object
  - Verify password_hash not in schema dict
  - Verify id, username, email, created_at present
- Test AuthResponse structure
  - Create AuthResponse with UserResponse and token
  - Verify nested structure correct
  - Verify token field is string

**Dependencies**: pytest, pydantic, schemas/auth, models

**Tests**: Self-testing

### File 7: backend/tests/test_auth_routes.py

**Purpose**: Integration tests for authentication API endpoints.

**Key Components**:
- Test POST /auth/signup with valid data
  - Send signup request with valid username, email, password
  - Verify 201 Created status
  - Verify response contains user (id, username, email, created_at) and token
  - Verify user exists in database
  - Verify password_hash in database starts with "$2b$12$" (bcrypt 12 rounds)
  - Verify password_hash NOT in response
  - Verify JWT token can be decoded
  - Verify token contains sub (user_id) and email
  - Verify token exp is 7 days from now
- Test POST /auth/signup with duplicate username
  - Create test user
  - Send signup request with same username, different email
  - Verify 409 Conflict status
  - Verify error message mentions username already exists
- Test POST /auth/signup with duplicate email (case-insensitive)
  - Create test user with "test@example.com"
  - Send signup request with "TEST@Example.COM"
  - Verify 409 Conflict status
  - Verify error message mentions email already registered
- Test POST /auth/signup with invalid username (too short)
  - Send signup request with 2-character username
  - Verify 422 Unprocessable Entity status
  - Verify error details mention username validation
- Test POST /auth/signup with invalid email
  - Send signup request with "notanemail"
  - Verify 422 status
  - Verify error details mention email format
- Test POST /auth/signup with short password
  - Send signup request with 7-character password
  - Verify 422 status
  - Verify error details mention password length
- Test POST /auth/login with correct credentials
  - Create test user with known password
  - Send login request with correct email and password
  - Verify 200 OK status
  - Verify response contains user and token
  - Verify JWT token valid and contains user_id
- Test POST /auth/login with wrong password
  - Create test user
  - Send login request with wrong password
  - Verify 401 Unauthorized status
  - Verify error message is "Invalid credentials"
- Test POST /auth/login with nonexistent email
  - Send login request with "nonexistent@example.com"
  - Verify 401 Unauthorized status
  - Verify error message is "Invalid credentials"
- Test POST /auth/login with case-insensitive email
  - Create user with "test@example.com"
  - Login with "TEST@Example.COM"
  - Verify login succeeds
- Test POST /auth/logout
  - Send logout request
  - Verify 200 OK status
  - Verify response message is "Successfully logged out"
- Test password hashing verification
  - Signup user with password "TestPass123"
  - Query database for user
  - Verify password_hash != "TestPass123"
  - Verify pwd_context.verify("TestPass123", password_hash) returns True
- Test JWT token structure
  - Signup or login to get token
  - Decode token with python-jose
  - Verify payload has sub, email, exp, iat fields
  - Verify sub is UUID string
  - Verify exp is approximately 7 days from now (within 1 minute tolerance)
- Use FastAPI TestClient for requests
- Use test database fixtures
- Use create_test_user fixture

**Dependencies**: pytest, fastapi.testclient, conftest fixtures, routes/auth, schemas/auth

**Tests**: Self-testing

### File 8: backend/pyproject.toml (update)

**Purpose**: Add passlib[bcrypt] dependency to project.

**Key Components**:
- Add to dependencies section: `passlib = {extras = ["bcrypt"], version = "^1.7"}`
- Or update existing dependencies if passlib already present
- No other changes needed (python-jose already installed)

**Dependencies**: None (this file defines dependencies)

**Tests**: None (configuration file)

---

## Phase 0: Research & Technical Decisions

### Research Findings

#### 1. Passlib CryptContext Configuration for Bcrypt

**Decision**: Use `CryptContext(schemes=["bcrypt"], bcrypt__rounds=12, deprecated="auto")`
**Rationale**: Passlib's CryptContext provides unified interface for password hashing. Specifying bcrypt scheme with 12 rounds balances security (2^12 iterations) and performance (~200ms on modern hardware). The `deprecated="auto"` allows future algorithm upgrades.

**Pattern**:
```python
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    bcrypt__rounds=12,
    deprecated="auto"
)

# Hash password
password_hash = pwd_context.hash("user_password")

# Verify password
is_valid = pwd_context.verify("user_password", password_hash)
```

**Alternatives Considered**:
- bcrypt library directly (less flexible, no context management)
- argon2 (newer but requires different library, not specified in spec)
- 10 rounds (too weak for 2025 standards)
- 14 rounds (too slow, >500ms)

#### 2. Password Verification Pattern

**Decision**: Use `pwd_context.verify(plain_password, password_hash)` returning boolean
**Rationale**: Single method call handles constant-time comparison preventing timing attacks. Returns boolean for easy conditional checks.

**Pattern**:
```python
# In login handler
is_valid = pwd_context.verify(request.password, user.password_hash)
if not is_valid:
    return error_response(401, "Invalid credentials", "UNAUTHORIZED")
```

**Alternatives Considered**:
- Manual hash comparison (timing attack vulnerability)
- Exception-based verification (less idiomatic)

#### 3. JWT Token Generation with 7-Day Expiration

**Decision**: Use `jwt.encode()` with payload including sub, email, exp, iat claims
**Rationale**: JWT standard claims provide interoperability. 7-day expiration balances security and user convenience. HS256 algorithm matches JWT middleware configuration.

**Pattern**:
```python
from jose import jwt
from datetime import datetime, timedelta

def create_jwt_token(user_id: UUID, email: str) -> str:
    payload = {
        "sub": str(user_id),  # Standard subject claim
        "email": email,
        "exp": datetime.utcnow() + timedelta(days=7),
        "iat": datetime.utcnow()  # Issued-at timestamp
    }
    token = jwt.encode(payload, BETTER_AUTH_SECRET, algorithm="HS256")
    return token
```

**Alternatives Considered**:
- Shorter expiration (less convenient for users)
- No expiration (security risk)
- Refresh token pattern (out of scope for Phase 2)

#### 4. Case-Insensitive Email Lookup with SQLModel

**Decision**: Use `func.lower(User.email) == email.lower()` in query with functional index
**Rationale**: Normalizing to lowercase in application and using database function ensures case-insensitive uniqueness. Functional index on `LOWER(email)` provides performance.

**Pattern**:
```python
from sqlmodel import select, func

# Check email uniqueness (case-insensitive)
statement = select(User).where(func.lower(User.email) == email.lower())
existing_user = session.exec(statement).first()

if existing_user:
    return error_response(409, "Email already registered", "CONFLICT")

# Store email normalized to lowercase
new_user = User(
    username=request.username,
    email=request.email.lower(),  # Normalize before storage
    password_hash=password_hash
)
```

**Database Index** (create in migration if not exists):
```sql
CREATE INDEX idx_users_email_lower ON users(LOWER(email));
```

**Alternatives Considered**:
- ILIKE operator (PostgreSQL-specific, less portable)
- Application-only normalization (no database-level enforcement)
- Case-sensitive email (user-unfriendly)

#### 5. Pydantic EmailStr Validation

**Decision**: Import `EmailStr` from pydantic and use as field type
**Rationale**: Built-in email validation using RFC 5322 regex. Automatic validation error messages. Type-safe.

**Pattern**:
```python
from pydantic import BaseModel, Field, EmailStr

class SignupRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr  # Automatic email format validation
    password: str = Field(min_length=8)
```

**Alternatives Considered**:
- Manual regex validation (reinventing wheel)
- No email validation (allows invalid emails)
- Third-party email validator library (unnecessary)

#### 6. FastAPI Response Model Excluding password_hash

**Decision**: Use Pydantic schema for response_model that explicitly excludes password_hash
**Rationale**: Pydantic schemas define response structure explicitly. Never include password_hash field in response schemas. FastAPI serializes using response schema, ensuring password_hash never sent.

**Pattern**:
```python
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class UserResponse(BaseModel):
    """User data for API responses - excludes password_hash."""
    id: UUID
    username: str
    email: str
    created_at: datetime
    # NOTE: password_hash deliberately excluded for security

class AuthResponse(BaseModel):
    user: UserResponse
    token: str

@router.post("/auth/signup", response_model=AuthResponse, status_code=201)
async def signup_user(request: SignupRequest, session: Session = Depends(get_session)):
    # ... create user with password_hash ...
    user_response = UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        created_at=user.created_at
        # password_hash not accessed here
    )
    return AuthResponse(user=user_response, token=token)
```

**Alternatives Considered**:
- Manual dict construction (error-prone)
- SQLModel model_dump() with exclude (verbose)
- Custom JSON serializer (unnecessary complexity)

#### 7. Duplicate Checking Strategy

**Decision**: Check username and email uniqueness separately, return first duplicate found
**Rationale**: Provides specific error messages. Prevents both duplicates in single request. Database unique constraints provide secondary enforcement.

**Pattern**:
```python
# Check username uniqueness (case-sensitive)
statement = select(User).where(User.username == request.username)
existing_user = session.exec(statement).first()
if existing_user:
    return error_response(409, "Username already exists", "CONFLICT")

# Check email uniqueness (case-insensitive)
statement = select(User).where(func.lower(User.email) == request.email.lower())
existing_user = session.exec(statement).first()
if existing_user:
    return error_response(409, "Email already registered", "CONFLICT")

# Proceed with user creation
```

**Alternatives Considered**:
- Single query checking both (less specific error)
- Rely only on database constraints (generic error message)
- Check after insert attempt (requires rollback)

#### 8. Error Response Standardization

**Decision**: Use helper function returning JSONResponse with {error, code, timestamp} structure
**Rationale**: Consistent error format across API. Matches JWT middleware error format. Includes timestamp for debugging.

**Pattern**:
```python
from fastapi.responses import JSONResponse
from datetime import datetime

def error_response(status_code: int, message: str, code: str) -> JSONResponse:
    """Create standardized error response."""
    return JSONResponse(
        status_code=status_code,
        content={
            "error": message,
            "code": code,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    )

# Usage
return error_response(409, "Username already exists", "CONFLICT")
```

**Alternatives Considered**:
- HTTPException (less control over format)
- Custom exception handlers (more complex)
- Plain dict responses (inconsistent)

---

## Critical Decisions Summary

| Decision | Choice | Impact |
|----------|--------|--------|
| Password Hashing | passlib bcrypt 12 rounds | Security + performance balance |
| JWT Expiration | 7 days | User convenience + security |
| Email Uniqueness | Case-insensitive with LOWER() | User-friendly, prevents duplicates |
| Response Schema | Pydantic excluding password_hash | Security, never expose hashes |
| Error Format | Standardized {error, code, timestamp} | Consistent API experience |
| Duplicate Checking | Application + database constraints | Specific errors + data integrity |
| Validation | Pydantic Field() constraints | Type safety + auto error messages |

---

## Success Metrics

### Functional Acceptance

| Requirement ID | Verification Method | Pass Criteria |
|----------------|---------------------|---------------|
| FR-001 | POST to /auth/signup with valid data | Returns 201 with user and token |
| FR-002 | Inspect signup request validation | Pydantic validates username 3-50 chars, email format, password 8+ chars |
| FR-003 | POST with invalid input | Returns 422 with detailed validation errors |
| FR-004 | Create user, signup with same username | Returns 409 "Username already exists" |
| FR-005 | Create user, signup with same email different case | Returns 409 "Email already registered" |
| FR-006 | Verify email in database | Email stored as lowercase |
| FR-007 | Verify password_hash in database | Starts with "$2b$12$" (bcrypt 12 rounds) |
| FR-008 | Query database after signup | User record exists with hashed password |
| FR-009 | Decode JWT token from signup | Contains sub (user_id), email, exp (7 days), iat |
| FR-010 | Inspect signup response | Has user {id, username, email, created_at} and token, no password_hash |
| FR-011 | POST to /auth/login with valid credentials | Returns 200 with user and token |
| FR-012 | Inspect login request validation | Pydantic requires email and password fields |
| FR-013 | Login with nonexistent email | Returns 401 "Invalid credentials" |
| FR-014 | Login with wrong password | Returns 401 "Invalid credentials" (same message as nonexistent) |
| FR-015 | Decode JWT from login | Same structure as signup token |
| FR-016 | Inspect login response | Same structure as signup response |
| FR-017 | POST to /auth/logout | Returns 200 {"message": "Successfully logged out"} |
| FR-018 | Check all responses | No password_hash field in any response |
| FR-019 | Import SignupRequest | Schema with username, email, password fields and constraints |
| FR-020 | Import LoginRequest | Schema with email, password fields |
| FR-021 | Import UserResponse | Schema with id, username, email, created_at (no password_hash) |
| FR-022 | Import AuthResponse | Schema with user (UserResponse) and token (str) |
| FR-023 | Simulate database connection failure | Returns 500 Internal Server Error |
| FR-024 | Mock passlib hash failure | Returns 500 Internal Server Error |
| FR-025 | Mock JWT encode failure | Returns 500 Internal Server Error |

### Quality Gates

**Before Implementation Starts**:
- ✅ Constitution check passes
- ✅ All research questions answered
- ✅ Contracts defined
- ✅ Quickstart guide created

**Before Testing Starts**:
- ✅ Pydantic schemas implemented
- ✅ Auth route handlers implemented
- ✅ Routes registered in main.py
- ✅ passlib configured correctly

**Before Feature Complete**:
- ✅ All 25 functional requirements verified
- ✅ 100% test coverage for routes/auth.py and schemas/auth.py
- ✅ Mypy passes in strict mode
- ✅ Valid signup creates user and returns token
- ✅ Duplicate username/email returns 409
- ✅ Invalid input returns 422 with details
- ✅ Valid login returns token
- ✅ Wrong credentials return 401
- ✅ Logout returns success message
- ✅ Password hashing uses bcrypt 12 rounds
- ✅ JWT tokens have 7-day expiration
- ✅ No password_hash in any response

---

## Risk Mitigation

| Risk | Mitigation Strategy |
|------|---------------------|
| Bcrypt rounds too high/low | Use 12 rounds as specified, test performance < 500ms |
| JWT expiration miscalculated | Use timedelta(days=7), test token exp claim |
| Email case-sensitivity issues | Normalize to lowercase, use LOWER() in queries, document behavior |
| Password_hash leaked in response | Never include in UserResponse schema, test responses |
| Duplicate check race condition | Database unique constraints as secondary enforcement |
| passlib import failure | Add to dependencies early, verify in tests |
| BETTER_AUTH_SECRET mismatch | Reuse from JWT middleware, validate at startup |
| Type hints incomplete | Run mypy strict mode as part of test suite |

---

## Next Steps

After this plan is approved, run:

```bash
/sp.tasks
```

This will generate the task breakdown in `tasks.md` following TDD approach (tests first, then implementation). Expected task phases:
1. **Setup**: Install passlib[bcrypt], verify environment
2. **Test**: Write schema tests, route tests, fixtures
3. **Implement**: Create schemas/auth.py, routes/auth.py
4. **Integrate**: Register routes in main.py
5. **Verify**: Run tests, check coverage, manual testing with curl
6. **Document**: Update quickstart, create contracts
