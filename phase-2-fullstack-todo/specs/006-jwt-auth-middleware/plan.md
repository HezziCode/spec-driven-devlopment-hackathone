# Implementation Plan: JWT Authentication Middleware

**Branch**: `006-jwt-auth-middleware` | **Date**: 2025-12-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-jwt-auth-middleware/spec.md`

## Summary

This implementation plan defines the technical approach for building JWT authentication middleware for the FastAPI backend. The primary requirement is to create middleware that intercepts all API requests (except `/auth/*` routes), extracts and verifies JWT tokens from the Authorization header using the BETTER_AUTH_SECRET environment variable, decodes token payload to extract user identity (user_id and email), validates token expiration, attaches authenticated user context to request.state for route handler access, and returns standardized error responses (401 Unauthorized, 400 Bad Request) for authentication failures. The technical approach involves using FastAPI middleware decorators with python-jose[cryptography] for JWT operations, implementing token verification with HS256 algorithm, creating utility functions for token decoding and user extraction, using request.state for user context attachment, and following the standardized error response format with error/code/timestamp fields. This middleware provides centralized authentication enforcement across all protected API endpoints, enabling user isolation in task CRUD operations and ensuring only authenticated requests access protected resources.

## Technical Context

**Language/Version**: Python 3.11+ (as specified in constitution for Phase II backend)
**Primary Dependencies**:
- python-jose[cryptography] 3.3+ (JWT encoding/decoding with cryptographic signature verification)
- FastAPI 0.104+ (middleware support and request.state access)
- pydantic 2.5+ (for validation, included with FastAPI)
- python-dotenv 1.0+ (for loading BETTER_AUTH_SECRET from .env file)

**Storage**: N/A (stateless JWT verification, no token storage)
**Testing**: pytest 7.4+ with pytest-asyncio for async middleware tests
**Target Platform**: Linux server environment (part of FastAPI backend)
**Project Type**: Web backend middleware (security layer)
**Performance Goals**:
- JWT verification < 5ms per request
- Middleware overhead < 10ms per request
- Token decoding < 2ms
- Zero false positives (valid tokens rejected) or false negatives (invalid tokens accepted)

**Constraints**:
- Must use python-jose for JWT operations (not PyJWT or other libraries)
- Must verify signature with HS256 algorithm only
- Must attach user_id and email to request.state (no other storage mechanism)
- Must skip authentication for `/auth/*`, `/docs`, `/redoc`, `/openapi.json` routes
- Must return standardized error format with error/code/timestamp fields
- Must handle all JWTError exceptions gracefully
- Must complete type hints (no Any types)
- Must not cache or store tokens (stateless verification)

**Scale/Scope**:
- 2 main implementation files (auth_middleware.py, jwt_utils.py)
- 17 functional requirements from specification
- Expected to process 100+ requests per second
- Middleware runs on every API request (except public routes)

## Constitution Check

### ✅ Principle I: Spec-Driven Development with Agents/Skills
**Status**: PASS
**Rationale**: Implementation will use auth-security-engineer agent with jwt-middleware skill. All code generation automated via agents, no manual coding required. Skill provides proven patterns for JWT verification.

### ✅ Principle II: Clean Code with Single Responsibility
**Status**: PASS
**Rationale**: Clear separation of concerns - auth_middleware.py contains only middleware logic (request interception, route filtering, error responses), jwt_utils.py contains only JWT operations (decode, verify, user extraction). Each utility function has single purpose. All functions will have Google-style docstrings.

### ✅ Principle III: Type Safety (NON-NEGOTIABLE)
**Status**: PASS
**Rationale**: All functions will have explicit type hints for parameters and return values. JWT payload typed as dict[str, Any] (unavoidable due to JWT spec flexibility). All other types fully specified (str, bool, Optional[User], datetime). Mypy strict mode will be enforced.

### ⚠️ Principle IV: Accessibility Compliance (WCAG 2.1 AA)
**Status**: NOT APPLICABLE
**Rationale**: Authentication middleware is backend security infrastructure with no UI components. Accessibility requirements apply to frontend only.

### ✅ Principle V: Performance-First Architecture
**Status**: PASS
**Rationale**: JWT verification is O(1) cryptographic operation. Token decoding is O(1). Middleware adds < 10ms overhead per request. No database queries in middleware (stateless). User extraction utility makes single O(1) database lookup by primary key when needed.

### ✅ Principle VI: Modular Architecture with Clear Boundaries
**Status**: PASS
**Rationale**: Middleware layer clearly separated from route handlers and business logic. JWT utilities decoupled from middleware (can be used independently). Middleware uses dependency injection pattern. Error responses follow standardized format across application.

## Project Structure

### Documentation (this feature)

```text
specs/006-jwt-auth-middleware/
├── plan.md              # This file (/sp.plan output)
├── spec.md              # Feature specification
├── research.md          # Technology research and decisions
├── quickstart.md        # Quick setup guide for developers
├── contracts/           # Interface contracts
│   ├── middleware-contract.md   # Middleware interface
│   └── jwt-utils-contract.md    # Utility functions interface
├── checklists/          # Quality validation
│   └── requirements.md  # Spec validation (already exists)
└── tasks.md             # Task breakdown (/sp.tasks - NOT created yet)
```

### Source Code (backend directory)

```text
backend/
├── middleware/              # Custom middleware
│   ├── __init__.py          # Export auth_middleware
│   └── auth_middleware.py   # JWT verification middleware
│                            # Contains: verify_jwt_middleware() function
│                            # Request path checking
│                            # Token extraction and verification
│                            # User context attachment
│                            # Error response formatting
│
├── utils/                   # Utility functions
│   ├── __init__.py          # Export JWT utilities
│   └── jwt_utils.py         # JWT token utilities
│                            # Contains: decode_token()
│                            # verify_token()
│                            # extract_user_from_token()
│                            # JWTError handling
│
├── main.py                  # FastAPI app (update to register middleware)
│
├── .env                     # Environment variables (BETTER_AUTH_SECRET)
│
└── tests/                   # Test suite
    ├── __init__.py
    ├── conftest.py          # Pytest fixtures (update with JWT fixtures)
    ├── test_auth_middleware.py  # Middleware tests
    └── test_jwt_utils.py        # JWT utility tests
```

**Structure Decision**: Using web application structure with backend directory. Middleware goes in middleware/ subdirectory following FastAPI conventions. Utilities in utils/ subdirectory for reusable functions. Tests mirror source structure.

## Complexity Tracking

> No constitution violations. All principles pass or not applicable to backend middleware infrastructure.

---

## Implementation Strategy

### Phase 0: Research

*Output: research.md*

Research tasks to resolve technical unknowns:

1. **FastAPI Middleware Pattern**
   - Research correct pattern for middleware function (async def with call_next)
   - Expected: `async def middleware(request: Request, call_next) -> Response`

2. **python-jose JWT Verification**
   - Research jwt.decode() signature with secret and algorithms
   - Expected: `jwt.decode(token, secret, algorithms=["HS256"])`

3. **Token Expiration Handling**
   - Research how python-jose handles expired tokens (automatic or manual check)
   - Expected: Automatic check, raises ExpiredSignatureError

4. **Request State Attachment**
   - Research FastAPI request.state usage for request-scoped data
   - Expected: `request.state.user_id = value` (any attribute name works)

5. **Error Response Format**
   - Research JSONResponse creation with custom status codes and body
   - Expected: `JSONResponse(status_code=401, content={...})`

6. **Middleware Registration**
   - Research FastAPI app.middleware() decorator usage
   - Expected: `@app.middleware("http")` decorator on middleware function

### Phase 1: Design

*Outputs: quickstart.md, contracts/*

#### Quickstart Guide

Create `quickstart.md` with step-by-step setup:
1. Verify BETTER_AUTH_SECRET in backend/.env (must match frontend)
2. Install dependencies: `cd backend && uv add python-jose[cryptography]`
3. Test token verification: `python -m pytest tests/test_jwt_utils.py`
4. Start server: `uvicorn main:app --reload`
5. Test middleware: `curl -H "Authorization: Bearer <token>" http://localhost:8000/api/users/me`
6. Generate test JWT: `python scripts/generate_test_token.py`

#### Middleware Contract

Create `contracts/middleware-contract.md` documenting middleware interface:
- Function signature: `async def verify_jwt_middleware(request: Request, call_next: Callable) -> Response`
- Input: FastAPI Request object with headers
- Output: Response from downstream handler or error JSONResponse
- Behavior: Extracts token, verifies, attaches user context, handles errors
- Public routes: `/auth/*`, `/docs`, `/redoc`, `/openapi.json` bypass middleware

#### JWT Utils Contract

Create `contracts/jwt-utils-contract.md` documenting utility functions:
- `decode_token(token: str) -> dict[str, Any]`: Decode JWT without verification (for inspection)
- `verify_token(token: str) -> bool`: Verify JWT signature and expiration, return True/False
- `extract_user_from_token(token: str, session: Session) -> Optional[User]`: Decode token, extract user_id from "sub" claim, query database, return User or None

---

## Implementation Files

### File 1: backend/middleware/auth_middleware.py

**Purpose**: FastAPI middleware function that intercepts requests, verifies JWT tokens, and attaches user context to request.state.

**Key Components**:
- Import statements (fastapi, jose, datetime, os, typing)
- Load BETTER_AUTH_SECRET from environment with validation
- Public routes list: ["/auth", "/docs", "/redoc", "/openapi.json"]
- verify_jwt_middleware() async function with Request and call_next parameters
- Path checking logic to bypass public routes
- Authorization header extraction and Bearer prefix validation
- Token extraction from "Bearer <token>" format
- JWT verification with jwt.decode() using BETTER_AUTH_SECRET and HS256
- Payload extraction for "sub" (user_id) and "email" claims
- request.state.user_id and request.state.email attachment
- Error handling for missing token (401), malformed header (400), invalid signature (401), expired token (401)
- Standardized error response formatting with error/code/timestamp fields
- Type hints on all functions and variables (no Any except JWT payload)
- Docstrings for middleware function

**Dependencies**: fastapi, python-jose, os, datetime, typing

**Tests**: tests/test_auth_middleware.py (valid token passes, expired token fails, missing token fails, malformed token fails, public routes bypass)

### File 2: backend/utils/jwt_utils.py

**Purpose**: Utility functions for JWT token operations including decoding, verification, and user extraction.

**Key Components**:
- Import statements (jose, os, typing, Optional, datetime, sqlmodel)
- Import User model from models.py
- Load BETTER_AUTH_SECRET from environment with validation
- decode_token(token: str) -> dict[str, Any] function
  - Uses jwt.decode() with secret and HS256
  - Returns payload dictionary
  - Raises JWTError for invalid tokens
  - Docstring with parameter and return type documentation
- verify_token(token: str) -> bool function
  - Calls decode_token() internally
  - Checks expiration manually if needed (python-jose may handle automatically)
  - Returns True for valid non-expired tokens
  - Returns False for expired tokens (catches ExpiredSignatureError)
  - Raises JWTError for invalid signatures (lets error propagate)
  - Docstring explaining behavior
- extract_user_from_token(token: str, session: Session) -> Optional[User] function
  - Calls decode_token() to get payload
  - Extracts user_id from payload["sub"]
  - Queries database: session.get(User, user_id)
  - Returns User object if found, None if not found
  - Handles JWTError and database errors
  - Docstring with examples
- Type hints on all parameters and return values
- Error handling for missing BETTER_AUTH_SECRET (raise ValueError on import)

**Dependencies**: python-jose, os, typing, sqlmodel, models.py

**Tests**: tests/test_jwt_utils.py (decode valid token, decode invalid token raises error, verify valid token returns True, verify expired token returns False, extract existing user returns User, extract nonexistent user returns None)

### File 3: backend/main.py (update)

**Purpose**: Register JWT middleware in FastAPI application.

**Key Components**:
- Import verify_jwt_middleware from middleware.auth_middleware
- Add middleware registration: `app.middleware("http")(verify_jwt_middleware)`
- Place middleware registration before route definitions
- Ensure middleware runs on all requests
- Docstring update noting JWT authentication is enabled

**Dependencies**: middleware/auth_middleware.py

**Tests**: Integration tests in test_auth_middleware.py verify middleware is active

### File 4: backend/.env.example (update)

**Purpose**: Document BETTER_AUTH_SECRET requirement in environment template.

**Key Components**:
- Add BETTER_AUTH_SECRET line with example value
- Comment explaining it must match frontend secret
- Comment showing how to generate secure secret (openssl rand -base64 32)
- Minimum length warning (32 characters)

**Dependencies**: None

**Tests**: None (documentation file)

### File 5: backend/tests/conftest.py (update)

**Purpose**: Add pytest fixtures for JWT token generation and test user creation.

**Key Components**:
- Fixture generate_valid_jwt(user_id: str, email: str) -> str
  - Uses python-jose to create test JWT
  - Signs with test BETTER_AUTH_SECRET
  - Sets expiration 1 hour in future
  - Returns token string
- Fixture generate_expired_jwt(user_id: str, email: str) -> str
  - Creates JWT with expiration in past
  - Used for testing expired token rejection
- Fixture test_user_with_token(session: Session) -> tuple[User, str]
  - Creates test user in database
  - Generates valid JWT for that user
  - Returns (user, token) tuple
- Set environment variable BETTER_AUTH_SECRET for tests
  - Use monkeypatch or os.environ
  - Ensure consistent secret across test suite

**Dependencies**: pytest, python-jose, models.py

**Tests**: None (test infrastructure)

### File 6: backend/tests/test_auth_middleware.py

**Purpose**: Integration tests for JWT authentication middleware.

**Key Components**:
- Test middleware allows valid token
  - Create test user and JWT
  - Make request with Authorization header
  - Verify request succeeds (200 status)
  - Verify request.state.user_id matches user
- Test middleware rejects missing token
  - Make request without Authorization header
  - Verify 401 Unauthorized response
  - Verify error response format (error, code, timestamp fields)
- Test middleware rejects expired token
  - Generate expired JWT
  - Make request with expired token
  - Verify 401 Unauthorized response
  - Verify error message mentions expiration
- Test middleware rejects invalid signature
  - Create JWT signed with wrong secret
  - Make request with invalid token
  - Verify 401 Unauthorized response
  - Verify error message mentions invalid signature
- Test middleware rejects malformed header
  - Make request with Authorization header missing "Bearer " prefix
  - Verify 400 Bad Request response
  - Verify error message mentions malformed header
- Test middleware bypasses public routes
  - Make requests to /auth/login, /docs, /redoc without token
  - Verify requests succeed (not rejected by middleware)
- Test middleware attaches user context
  - Create protected endpoint that accesses request.state.user_id
  - Make request with valid token
  - Verify endpoint receives correct user_id from state
- Use FastAPI TestClient for request simulation
- Use test fixtures for user and token generation

**Dependencies**: pytest, fastapi.testclient, conftest fixtures

**Tests**: Self-testing

### File 7: backend/tests/test_jwt_utils.py

**Purpose**: Unit tests for JWT utility functions.

**Key Components**:
- Test decode_token with valid token
  - Generate valid JWT
  - Call decode_token()
  - Verify returned payload contains sub, email, exp, iat fields
  - Verify values match expected values
- Test decode_token with invalid token
  - Create malformed JWT string
  - Call decode_token()
  - Verify JWTError is raised
- Test verify_token with valid token
  - Generate valid non-expired JWT
  - Call verify_token()
  - Verify returns True
- Test verify_token with expired token
  - Generate expired JWT
  - Call verify_token()
  - Verify returns False (not raises exception)
- Test verify_token with invalid signature
  - Create JWT signed with wrong secret
  - Call verify_token()
  - Verify raises JWTError
- Test extract_user_from_token with existing user
  - Create test user in database
  - Generate JWT with user's ID
  - Call extract_user_from_token()
  - Verify returns User object with correct ID
- Test extract_user_from_token with nonexistent user
  - Generate JWT with random UUID
  - Call extract_user_from_token()
  - Verify returns None
- Test extract_user_from_token with invalid token
  - Pass malformed token
  - Verify raises JWTError or returns None gracefully
- Use test database session fixture
- Use JWT generation fixtures

**Dependencies**: pytest, conftest fixtures, jwt_utils module

**Tests**: Self-testing

### File 8: backend/scripts/generate_test_token.py (optional utility)

**Purpose**: Utility script to generate test JWT tokens for manual testing with curl.

**Key Components**:
- Import python-jose and os
- Load BETTER_AUTH_SECRET from environment
- Accept command-line arguments for user_id and email
- Generate JWT with 1 hour expiration
- Print token to stdout
- Usage: `python scripts/generate_test_token.py --user-id <uuid> --email test@example.com`
- Helpful for testing with curl or Postman

**Dependencies**: python-jose, argparse, os

**Tests**: None (utility script for manual testing)

---

## Phase 0: Research & Technical Decisions

### Research Findings

#### 1. FastAPI Middleware Pattern

**Decision**: Use `@app.middleware("http")` decorator with async function
**Rationale**: FastAPI's HTTP middleware pattern intercepts all requests before route handlers. Async functions support FastAPI's async request handling.

**Pattern**:
```python
@app.middleware("http")
async def verify_jwt_middleware(request: Request, call_next):
    # Middleware logic
    response = await call_next(request)
    return response
```

**Alternatives Considered**:
- Dependency injection with Depends() (cleaner but requires adding to every route)
- Custom middleware class (more verbose, no advantages for this use case)

#### 2. python-jose JWT Verification

**Decision**: Use `jwt.decode(token, secret, algorithms=["HS256"])` for verification
**Rationale**: Single function call handles signature verification, expiration checking, and payload decoding. Raises specific exceptions for different failure modes.

**Pattern**:
```python
from jose import jwt, JWTError, ExpiredSignatureError

try:
    payload = jwt.decode(token, BETTER_AUTH_SECRET, algorithms=["HS256"])
except ExpiredSignatureError:
    # Token expired
except JWTError:
    # Invalid signature or malformed token
```

**Alternatives Considered**:
- Manual signature verification (complex, error-prone)
- PyJWT library (python-jose is Better Auth compatible)

#### 3. Token Expiration Handling

**Decision**: python-jose automatically checks expiration, raises ExpiredSignatureError
**Rationale**: No manual date comparison needed. Library handles edge cases (timezone, clock skew).

**Pattern**:
```python
try:
    payload = jwt.decode(token, secret, algorithms=["HS256"])
    # Token is valid and not expired
except ExpiredSignatureError:
    # Token expired - return False or raise 401
except JWTError:
    # Other JWT errors
```

**Alternatives Considered**:
- Manual expiration checking (reinventing the wheel)
- No expiration checking (security vulnerability)

#### 4. Request State Attachment

**Decision**: Use `request.state.user_id` and `request.state.email` for user context
**Rationale**: FastAPI request.state is designed for request-scoped data. No serialization overhead. Type-safe access in route handlers.

**Pattern**:
```python
# In middleware
request.state.user_id = payload.get("sub")
request.state.email = payload.get("email")

# In route handler
@app.get("/api/users/{user_id}/tasks")
async def get_tasks(request: Request, user_id: str):
    authenticated_user_id = request.state.user_id
    if user_id != authenticated_user_id:
        raise HTTPException(403, "Forbidden")
```

**Alternatives Considered**:
- Thread-local storage (not compatible with async)
- Custom context manager (more complex)

#### 5. Error Response Format

**Decision**: Use JSONResponse with standardized {error, code, timestamp} structure
**Rationale**: Consistent error format across API. Includes timestamp for debugging. Machine-parseable error codes.

**Pattern**:
```python
from fastapi.responses import JSONResponse
from datetime import datetime

def error_response(status_code: int, message: str, code: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": message,
            "code": code,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    )

# Usage
return error_response(401, "Missing authentication token", "UNAUTHORIZED")
```

**Alternatives Considered**:
- Plain HTTPException (less structured)
- Custom exception classes (more complex for simple errors)

#### 6. Middleware Registration

**Decision**: Use `app.middleware("http")(verify_jwt_middleware)` in main.py
**Rationale**: Explicit registration makes middleware visible in application setup. Runs on all HTTP requests automatically.

**Pattern**:
```python
from fastapi import FastAPI
from middleware.auth_middleware import verify_jwt_middleware

app = FastAPI()
app.middleware("http")(verify_jwt_middleware)

# Or with decorator at definition
@app.middleware("http")
async def verify_jwt_middleware(request: Request, call_next):
    pass
```

**Alternatives Considered**:
- Decorator at definition (couples middleware to app instance)
- Manual middleware list (not idiomatic FastAPI)

#### 7. Public Route Filtering

**Decision**: Check `request.url.path.startswith()` for known public prefixes
**Rationale**: Simple and explicit. Easy to add new public routes. No regex complexity.

**Pattern**:
```python
PUBLIC_PATHS = ["/auth", "/docs", "/redoc", "/openapi.json"]

if any(request.url.path.startswith(path) for path in PUBLIC_PATHS):
    return await call_next(request)  # Bypass authentication
```

**Alternatives Considered**:
- Regex patterns (overkill for simple prefixes)
- Route metadata (requires modifying route definitions)

#### 8. BETTER_AUTH_SECRET Loading

**Decision**: Load from environment at module import time with validation
**Rationale**: Fail fast if secret is missing. No repeated environment lookups per request.

**Pattern**:
```python
import os
from dotenv import load_dotenv

load_dotenv()
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")

if not BETTER_AUTH_SECRET:
    raise ValueError(
        "BETTER_AUTH_SECRET environment variable is required for JWT authentication. "
        "Set it in backend/.env file and ensure it matches the frontend secret."
    )

if len(BETTER_AUTH_SECRET) < 32:
    raise ValueError(
        "BETTER_AUTH_SECRET must be at least 32 characters for security. "
        "Generate with: openssl rand -base64 32"
    )
```

**Alternatives Considered**:
- Load per request (performance overhead)
- No validation (harder to debug misconfigurations)

---

## Critical Decisions Summary

| Decision | Choice | Impact |
|----------|--------|--------|
| JWT Library | python-jose[cryptography] | Better Auth compatibility |
| Middleware Pattern | @app.middleware("http") | Runs on all requests |
| User Context Storage | request.state | Request-scoped, type-safe |
| Error Format | Standardized JSON | Consistent API responses |
| Public Route Filtering | Prefix matching | Simple, explicit |
| Secret Loading | Module-level with validation | Fail fast on misconfiguration |
| Token Expiration | Automatic via python-jose | No manual date checks |

---

## Success Metrics

### Functional Acceptance

| Requirement ID | Verification Method | Pass Criteria |
|----------------|---------------------|---------------|
| FR-001 | Make request to protected endpoint with valid token | Request succeeds, middleware doesn't reject |
| FR-002 | Make request to /auth/login without token | Request succeeds, middleware bypasses |
| FR-003 | Check request headers for Authorization | Middleware extracts "Bearer <token>" correctly |
| FR-004 | Make request without Authorization header | 401 response with "Missing authentication token" error |
| FR-005 | Create JWT with wrong secret, send request | 401 response with "Invalid token signature" error |
| FR-006 | Create expired JWT, send request | 401 response with token expiration error |
| FR-007 | Inspect JWT payload from valid request | Middleware extracts "sub" and "email" claims |
| FR-008 | Access request.state.user_id in route handler | user_id and email available on request.state |
| FR-009 | Send request with tampered JWT | 401 response with signature error |
| FR-010 | Send request with "Authorization: <token>" (no Bearer) | 400 response with "Malformed authorization header" |
| FR-011 | Call decode_token() with valid JWT | Returns dict with sub, email, exp, iat |
| FR-012 | Call verify_token() with valid/expired tokens | Returns True for valid, False for expired |
| FR-013 | Call extract_user_from_token() with valid user | Returns User object from database |
| FR-014 | Make requests to /docs, /redoc without token | Requests succeed, middleware bypasses |
| FR-015 | Check all error responses | All have error, code, timestamp fields in ISO8601 format |
| FR-016 | Send various invalid tokens | JWTError caught and converted to 401 or 400 |
| FR-017 | Run mypy on middleware and utils | Zero errors, no Any types (except JWT payload) |

### Quality Gates

**Before Implementation Starts**:
- ✅ Constitution check passes
- ✅ All research questions answered
- ✅ Contracts defined
- ✅ Quickstart guide created

**Before Testing Starts**:
- ✅ Middleware function implemented
- ✅ JWT utilities implemented
- ✅ Middleware registered in main.py
- ✅ BETTER_AUTH_SECRET validation working

**Before Feature Complete**:
- ✅ All 17 functional requirements verified
- ✅ 100% test coverage for middleware and jwt_utils modules
- ✅ Mypy passes in strict mode
- ✅ Valid tokens authenticate correctly
- ✅ Invalid tokens rejected with proper errors
- ✅ Public routes bypass middleware
- ✅ User context accessible in route handlers

---

## Risk Mitigation

| Risk | Mitigation Strategy |
|------|---------------------|
| BETTER_AUTH_SECRET mismatch | Validate secret format at startup, document in .env.example |
| Token expiration edge cases | Use python-jose automatic expiration checking |
| Request state not attached | Write integration test verifying state access in route |
| Middleware blocks public routes | Test public routes explicitly without tokens |
| Type hints incomplete | Run mypy strict mode as part of test suite |
| Performance degradation | Profile middleware overhead, ensure < 10ms |
| Invalid error response format | Create error response helper function, test format |

---

## Next Steps

After this plan is approved, run:

```bash
/sp.tasks
```

This will generate the task breakdown in `tasks.md` following TDD approach (tests first, then implementation). Expected task phases:
1. **Setup**: Install python-jose, update .env.example
2. **Test**: Write JWT fixtures, middleware tests, utility tests
3. **Implement**: Create jwt_utils.py, auth_middleware.py
4. **Integrate**: Register middleware in main.py
5. **Verify**: Run tests, check coverage, validate with manual requests
6. **Document**: Update quickstart, create contracts
