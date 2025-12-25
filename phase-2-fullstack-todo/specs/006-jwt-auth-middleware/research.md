# Research: JWT Authentication Middleware Technical Decisions

**Feature**: JWT Authentication Middleware
**Date**: 2025-12-24
**Status**: Complete

## Overview

This document captures technical research and decisions for implementing JWT authentication middleware in FastAPI. The research focused on identifying the most reliable and performant patterns for JWT verification, middleware implementation, error handling, and user context management.

---

## Research Questions

### 1. FastAPI Middleware Pattern

**Question**: What is the correct pattern for implementing HTTP middleware in FastAPI?

**Research Findings**:
- FastAPI supports two middleware patterns: decorator-based (`@app.middleware("http")`) and class-based (BaseHTTPMiddleware)
- Decorator pattern is recommended for simple middleware with minimal state
- Middleware functions must be async and accept `request: Request` and `call_next: Callable` parameters
- Middleware executes before and after route handlers (full request/response cycle)

**Decision**: Use decorator-based middleware with `@app.middleware("http")`

**Rationale**:
- Simpler implementation for stateless authentication
- Better performance than BaseHTTPMiddleware (no additional coroutine overhead)
- Direct access to request and response objects
- Idiomatic FastAPI pattern used in official documentation

**Pattern**:
```python
from fastapi import FastAPI, Request
from fastapi.responses import Response

app = FastAPI()

@app.middleware("http")
async def verify_jwt_middleware(request: Request, call_next):
    # Pre-processing logic
    response = await call_next(request)
    # Post-processing logic (if needed)
    return response
```

**Alternatives Considered**:
- **BaseHTTPMiddleware class**: More verbose, adds coroutine overhead, better for stateful middleware
- **Dependency injection with Depends()**: Cleaner but requires adding to every route individually

**References**:
- FastAPI Middleware Documentation: https://fastapi.tiangolo.com/tutorial/middleware/
- Starlette Middleware: https://www.starlette.io/middleware/

---

### 2. python-jose JWT Verification

**Question**: How to verify JWT tokens with python-jose, including signature and expiration?

**Research Findings**:
- python-jose provides `jwt.decode()` function that handles signature verification and expiration checking in single call
- Must specify `algorithms` parameter (HS256 for symmetric signing)
- Raises `ExpiredSignatureError` for expired tokens
- Raises `JWTError` for invalid signature or malformed tokens
- Supports automatic expiration checking via `exp` claim

**Decision**: Use `jwt.decode(token, secret, algorithms=["HS256"])` for all verification

**Rationale**:
- Single function call handles both signature and expiration
- Clear exception types for different error conditions
- No manual date comparison needed
- Compatible with Better Auth JWT format

**Pattern**:
```python
from jose import jwt, JWTError, ExpiredSignatureError

BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")

try:
    payload = jwt.decode(token, BETTER_AUTH_SECRET, algorithms=["HS256"])
    user_id = payload.get("sub")
    email = payload.get("email")
except ExpiredSignatureError:
    # Handle expired token (401 Unauthorized)
    raise HTTPException(status_code=401, detail="Token has expired")
except JWTError:
    # Handle invalid signature or malformed token (401 Unauthorized)
    raise HTTPException(status_code=401, detail="Invalid token")
```

**Alternatives Considered**:
- **PyJWT library**: Similar API but less commonly used with Better Auth
- **Manual verification**: Complex, error-prone, reinvents the wheel
- **authlib library**: More features but overkill for simple JWT verification

**References**:
- python-jose Documentation: https://python-jose.readthedocs.io/
- JWT Spec (RFC 7519): https://datatracker.ietf.org/doc/html/rfc7519

---

### 3. Token Expiration Handling

**Question**: Does python-jose automatically check token expiration or do we need manual checking?

**Research Findings**:
- python-jose automatically validates `exp` claim during `jwt.decode()`
- Raises `ExpiredSignatureError` if current time > exp timestamp
- Handles timezone and clock skew automatically
- No need for manual `datetime.now()` comparison

**Decision**: Rely on python-jose automatic expiration checking

**Rationale**:
- Automatic checking is more reliable (handles edge cases)
- No risk of timezone bugs or clock skew issues
- Cleaner code (no manual date logic)
- Standard JWT verification behavior

**Pattern**:
```python
try:
    payload = jwt.decode(token, secret, algorithms=["HS256"])
    # If we reach here, token is not expired
except ExpiredSignatureError:
    # Token expired - handle gracefully
    return False  # or raise 401
```

**Alternatives Considered**:
- **Manual expiration check**: More code, prone to timezone bugs
- **No expiration check**: Security vulnerability (tokens never expire)

**References**:
- python-jose source code: https://github.com/mpdavis/python-jose/blob/master/jose/jwt.py

---

### 4. Request State Attachment

**Question**: How to attach authenticated user context to FastAPI requests for access in route handlers?

**Research Findings**:
- FastAPI/Starlette provides `request.state` for request-scoped arbitrary data
- `request.state` is a namespace object that accepts any attribute
- Each request has isolated state (no cross-request contamination)
- State persists throughout request lifecycle (middleware → route handler → response)
- Type-safe access in route handlers

**Decision**: Use `request.state.user_id` and `request.state.email` for user context

**Rationale**:
- Designed explicitly for request-scoped data
- No serialization or storage overhead
- Type-safe and intuitive access pattern
- Standard FastAPI pattern for middleware-to-handler communication

**Pattern**:
```python
# In middleware
async def verify_jwt_middleware(request: Request, call_next):
    payload = jwt.decode(token, secret, algorithms=["HS256"])
    request.state.user_id = payload.get("sub")
    request.state.email = payload.get("email")
    return await call_next(request)

# In route handler
@app.get("/api/users/{user_id}/tasks")
async def get_tasks(request: Request, user_id: str):
    authenticated_user_id = request.state.user_id
    if user_id != authenticated_user_id:
        raise HTTPException(403, "Forbidden")
    # Proceed with authenticated user's tasks
```

**Alternatives Considered**:
- **Thread-local storage (contextvars)**: More complex, not needed for request-scoped data
- **Custom context manager**: Reinvents request.state functionality
- **Database lookup per request**: Inefficient, JWT already contains user info

**References**:
- Starlette Request State: https://www.starlette.io/requests/#other-state

---

### 5. Error Response Format

**Question**: How to create standardized error responses with custom status codes and JSON body?

**Research Findings**:
- FastAPI provides `JSONResponse` class for custom JSON responses
- Can set custom `status_code` and `content` (dict)
- Constitution requires error format: `{error: string, code: string, timestamp: ISO8601}`
- HTTPException provides simple error responses but less structured

**Decision**: Create helper function that returns `JSONResponse` with standardized format

**Rationale**:
- Consistent error format across all authentication failures
- Includes timestamp for debugging and logging
- Machine-parseable error codes for client-side handling
- Easy to extend with additional error fields if needed

**Pattern**:
```python
from fastapi.responses import JSONResponse
from datetime import datetime

def create_error_response(status_code: int, message: str, code: str) -> JSONResponse:
    """Create standardized error response.

    Args:
        status_code: HTTP status code (401, 400, etc.)
        message: Human-readable error message
        code: Machine-readable error code (UNAUTHORIZED, MALFORMED_TOKEN, etc.)

    Returns:
        JSONResponse with error, code, and timestamp fields
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "error": message,
            "code": code,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    )

# Usage in middleware
return create_error_response(401, "Missing authentication token", "UNAUTHORIZED")
```

**Alternatives Considered**:
- **HTTPException**: Less structured, doesn't include timestamp or error codes
- **Custom exception classes**: More complex, overkill for simple errors
- **Plain dict response**: Works but less explicit about JSON format

**References**:
- FastAPI JSONResponse: https://fastapi.tiangolo.com/advanced/custom-response/

---

### 6. Middleware Registration

**Question**: How to register middleware in FastAPI application to run on all requests?

**Research Findings**:
- Two registration methods: decorator at definition or explicit registration after definition
- `@app.middleware("http")` decorator at function definition couples function to app instance
- `app.middleware("http")(function_name)` allows decoupled definition and registration
- Middleware registration order matters (last registered runs first)

**Decision**: Use explicit registration in `main.py` with `app.middleware("http")(verify_jwt_middleware)`

**Rationale**:
- Decouples middleware definition from FastAPI app instance
- Easier to test middleware in isolation
- Clear visibility in main.py where middleware is registered
- Allows middleware to be imported and used in multiple apps if needed

**Pattern**:
```python
# In middleware/auth_middleware.py
async def verify_jwt_middleware(request: Request, call_next):
    # Middleware logic
    pass

# In main.py
from fastapi import FastAPI
from middleware.auth_middleware import verify_jwt_middleware

app = FastAPI()
app.middleware("http")(verify_jwt_middleware)

# Register routes after middleware
from routes import tasks, users
app.include_router(tasks.router)
app.include_router(users.router)
```

**Alternatives Considered**:
- **Decorator at definition**: Couples middleware to app instance, harder to test
- **Manual middleware stack**: Not idiomatic FastAPI

**References**:
- FastAPI Middleware Registration: https://fastapi.tiangolo.com/tutorial/middleware/

---

### 7. Public Route Filtering

**Question**: How to bypass authentication for public routes like `/auth/*`, `/docs`, `/redoc`?

**Research Findings**:
- Can check `request.url.path` to get request path string
- `str.startswith()` method efficient for prefix matching
- List comprehension with `any()` checks multiple prefixes
- Alternative: regex patterns (more complex, no performance benefit)

**Decision**: Use `request.url.path.startswith()` with list of public path prefixes

**Rationale**:
- Simple and readable
- Efficient (O(n) where n is number of prefixes, typically < 5)
- Easy to add new public routes
- No regex complexity for simple prefix matching

**Pattern**:
```python
PUBLIC_PATHS = ["/auth", "/docs", "/redoc", "/openapi.json"]

async def verify_jwt_middleware(request: Request, call_next):
    # Check if request path starts with any public prefix
    if any(request.url.path.startswith(path) for path in PUBLIC_PATHS):
        return await call_next(request)  # Bypass authentication

    # Proceed with JWT verification for protected routes
    # ...
```

**Alternatives Considered**:
- **Regex patterns**: Overkill for simple prefix matching, harder to maintain
- **Route metadata (tags/dependencies)**: Requires modifying all route definitions
- **Separate middleware instances**: More complex configuration

**References**:
- Starlette URL: https://www.starlette.io/requests/#url

---

### 8. BETTER_AUTH_SECRET Environment Variable

**Question**: When and how to load BETTER_AUTH_SECRET from environment variables?

**Research Findings**:
- Environment variables can be loaded at module import time or per-request
- Per-request loading adds overhead (disk I/O or environment lookup)
- Module-level loading happens once at startup
- Can validate secret format at startup to fail fast on misconfiguration

**Decision**: Load BETTER_AUTH_SECRET at module import time with validation

**Rationale**:
- Fail fast if secret is missing (before any requests are processed)
- No per-request overhead (loaded once at startup)
- Validation ensures secret meets minimum security requirements
- Clear error messages guide developers to fix configuration

**Pattern**:
```python
import os
from dotenv import load_dotenv

load_dotenv()
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")

# Validate secret presence
if not BETTER_AUTH_SECRET:
    raise ValueError(
        "BETTER_AUTH_SECRET environment variable is required for JWT authentication. "
        "Set it in backend/.env file and ensure it matches the frontend secret."
    )

# Validate secret length
if len(BETTER_AUTH_SECRET) < 32:
    raise ValueError(
        "BETTER_AUTH_SECRET must be at least 32 characters for security. "
        "Generate a secure secret with: openssl rand -base64 32"
    )
```

**Alternatives Considered**:
- **Load per request**: Performance overhead, same validation repeated
- **No validation**: Harder to debug misconfiguration errors
- **Lazy loading on first use**: Delays error detection until first request

**References**:
- python-dotenv: https://github.com/theskumar/python-dotenv

---

## Architecture Decisions

### Decision 1: Middleware vs Dependency Injection

**Context**: Two approaches to enforce authentication:
1. Middleware that runs on all requests automatically
2. Dependency injection (Depends()) added to each protected route

**Decision**: Use middleware approach

**Rationale**:
- Centralized authentication logic (single source of truth)
- Automatically protects all routes without requiring developers to remember adding Depends()
- Easier to add public route exceptions (single list in middleware)
- Less code duplication across route handlers
- Matches constitution requirement for "centralized authentication enforcement"

**Trade-offs**:
- Middleware runs on all requests (minimal overhead for public routes)
- Dependency injection would be more explicit per-route but requires coordination

---

### Decision 2: Stateless JWT Verification vs Session Storage

**Context**: Could verify JWT and store user in session/cache for subsequent requests

**Decision**: Stateless verification on every request (no session storage)

**Rationale**:
- JWT designed for stateless authentication
- No need for shared session store (Redis, database)
- Scales horizontally without session affinity
- No session cleanup or expiration management
- JWT verification is fast (< 5ms) so overhead is acceptable
- Matches constitution performance requirements

**Trade-offs**:
- Slightly higher CPU usage per request (crypto verification)
- Cannot revoke tokens without blacklist (acceptable for initial implementation)

---

### Decision 3: Error Response Helper Function

**Context**: Need consistent error format across multiple error conditions

**Decision**: Create `create_error_response()` helper function

**Rationale**:
- DRY principle (single function for all auth errors)
- Enforces standardized format (no format drift)
- Easy to update format globally if needed
- Improves code readability (semantic function name)
- Matches constitution clean code principles

---

## Performance Analysis

### JWT Verification Performance

**Estimated Performance**:
- JWT decode with signature verification: ~2-5ms
- Token extraction from header: < 1ms
- Request state attachment: < 1ms
- **Total middleware overhead: < 10ms per request**

**Validation**:
- Meets constitution requirement: "Middleware overhead < 10ms per request"
- Acceptable for API latency budget (target: 200ms p95)
- No database queries in middleware (stateless verification)

### Scalability

**Horizontal Scaling**:
- Stateless authentication allows any backend instance to verify any JWT
- No shared session state required
- No database lookups in middleware

**Bottlenecks**:
- CPU for cryptographic verification (negligible with modern CPUs)
- BETTER_AUTH_SECRET must be consistent across all instances

---

## Security Considerations

### Token Verification

**Security Measures**:
- Signature verification prevents token tampering
- Expiration checking prevents replay attacks with old tokens
- Algorithm specified explicitly (prevents algorithm substitution attacks)
- Secret validated for minimum length (32 characters)

**Known Limitations**:
- No token revocation mechanism (tokens valid until expiration)
- No rate limiting on authentication failures (future feature)

### Error Messages

**Security Measures**:
- Generic error messages don't leak sensitive information
- Different error codes for different failure modes (client debugging without exposing internals)
- Timestamps allow audit logging without exposing user data

---

## Testing Strategy

### Unit Tests (jwt_utils.py)

**Test Cases**:
- decode_token with valid token → returns payload dict
- decode_token with invalid signature → raises JWTError
- decode_token with expired token → raises ExpiredSignatureError
- verify_token with valid token → returns True
- verify_token with expired token → returns False
- extract_user_from_token with existing user → returns User object
- extract_user_from_token with nonexistent user → returns None

### Integration Tests (auth_middleware.py)

**Test Cases**:
- Valid JWT token → request proceeds, user context attached
- Missing token → 401 Unauthorized response
- Expired token → 401 Unauthorized with expiration message
- Invalid signature → 401 Unauthorized with signature error
- Malformed header (no "Bearer") → 400 Bad Request
- Public routes (/auth/*, /docs) → bypass authentication
- Protected route with valid token → request.state.user_id accessible

### Performance Tests

**Test Cases**:
- Measure middleware overhead with 1000 requests
- Verify p95 latency < 10ms for middleware execution
- Concurrent requests with different tokens (no state leakage)

---

## Dependencies

### Required Packages

| Package | Version | Purpose |
|---------|---------|---------|
| python-jose[cryptography] | 3.3+ | JWT encoding/decoding |
| FastAPI | 0.104+ | Web framework |
| pydantic | 2.5+ | Validation (included with FastAPI) |
| python-dotenv | 1.0+ | Environment variable loading |

### Installation Command

```bash
cd backend
uv add python-jose[cryptography]
# Other dependencies already installed
```

---

## References

### Official Documentation
- FastAPI Middleware: https://fastapi.tiangolo.com/tutorial/middleware/
- python-jose Documentation: https://python-jose.readthedocs.io/
- JWT Specification (RFC 7519): https://datatracker.ietf.org/doc/html/rfc7519
- Better Auth JWT Plugin: https://www.better-auth.com/docs/plugins/jwt

### Related Specifications
- Feature Spec: `/specs/006-jwt-auth-middleware/spec.md`
- REST API Endpoints: `/specs/api/rest-endpoints.md`
- Database Schema (User model): `/specs/005-database-foundation/spec.md`
- Constitution: `/.specify/memory/constitution.md`

---

## Conclusion

All research questions have been answered with clear technical decisions. The chosen patterns prioritize:
- **Security**: Cryptographic verification, expiration checking, algorithm specification
- **Performance**: Stateless verification, module-level secret loading, minimal overhead
- **Maintainability**: Helper functions, standardized error format, clear separation of concerns
- **Testability**: Decoupled middleware, injectable utilities, comprehensive test coverage

Ready to proceed with implementation in Phase 1 (Design) and Phase 2 (Tasks).
