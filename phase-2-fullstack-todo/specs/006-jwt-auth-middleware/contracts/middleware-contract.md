# JWT Authentication Middleware Contract

**Module**: `backend/middleware/auth_middleware.py`
**Version**: 1.0.0
**Status**: Draft

## Overview

This contract defines the public interface for the JWT authentication middleware that intercepts all HTTP requests to FastAPI application, verifies JWT tokens from Authorization headers, attaches authenticated user context to request state, and returns standardized error responses for authentication failures.

---

## Public Interface

### Function: verify_jwt_middleware

**Signature**:
```python
async def verify_jwt_middleware(request: Request, call_next: Callable) -> Response
```

**Purpose**: FastAPI HTTP middleware that verifies JWT tokens on all requests except public routes.

**Parameters**:
- `request: Request` - FastAPI/Starlette Request object containing HTTP headers, URL path, and state
- `call_next: Callable` - Async function to invoke next middleware or route handler

**Returns**:
- `Response` - Either the response from downstream handler (if authentication passes) or JSONResponse with error details (if authentication fails)

**Side Effects**:
- Attaches `user_id` and `email` to `request.state` for authenticated requests
- Modifies request state that persists throughout request lifecycle

**Exceptions**:
- Does not raise exceptions; returns JSONResponse with appropriate HTTP status codes

---

## Behavior Specification

### Public Routes (Bypass Authentication)

The middleware MUST bypass JWT verification for the following route prefixes:

| Route Prefix | Purpose |
|--------------|---------|
| `/auth` | Authentication endpoints (signup, login, logout) |
| `/docs` | OpenAPI/Swagger documentation |
| `/redoc` | ReDoc API documentation |
| `/openapi.json` | OpenAPI JSON schema |

**Implementation**: Check if `request.url.path` starts with any public prefix. If match found, immediately call `await call_next(request)` without token verification.

### Protected Routes (Require JWT)

All routes NOT matching public prefixes require valid JWT token in Authorization header.

---

## Authentication Flow

### 1. Request Interception

Middleware intercepts ALL incoming HTTP requests before they reach route handlers.

### 2. Public Route Check

```
IF request.url.path starts with any PUBLIC_PATHS:
    RETURN await call_next(request)  # Bypass authentication
```

### 3. Token Extraction

Extract Authorization header from request:
```
auth_header = request.headers.get("Authorization")
```

**Expected Format**: `Bearer <jwt_token>`

**Validation**:
- Header MUST be present
- Header MUST start with "Bearer " prefix (case-sensitive)
- Token MUST follow "Bearer " prefix

### 4. Token Verification

Verify JWT token using python-jose:
```python
payload = jwt.decode(token, BETTER_AUTH_SECRET, algorithms=["HS256"])
```

**Validation**:
- Signature MUST match BETTER_AUTH_SECRET
- Algorithm MUST be HS256
- Token MUST NOT be expired (automatic check via python-jose)

### 5. User Context Attachment

Extract user information from JWT payload and attach to request state:
```python
request.state.user_id = payload.get("sub")  # User ID from "sub" claim
request.state.email = payload.get("email")  # Email from "email" claim
```

**Guarantees**:
- `request.state.user_id` is available to all route handlers after middleware
- `request.state.email` is available to all route handlers after middleware
- State persists throughout request lifecycle

### 6. Error Handling

Return appropriate error responses for authentication failures.

---

## Error Responses

All error responses MUST follow standardized format:

```json
{
  "error": "Human-readable error message",
  "code": "MACHINE_READABLE_CODE",
  "timestamp": "2025-12-24T12:34:56.789Z"
}
```

### Error Scenarios

| Scenario | HTTP Status | Error Message | Error Code |
|----------|-------------|---------------|------------|
| Missing Authorization header | 401 | "Missing authentication token" | UNAUTHORIZED |
| Authorization header without "Bearer " prefix | 400 | "Malformed authorization header" | MALFORMED_TOKEN |
| Invalid JWT signature (tampered or wrong secret) | 401 | "Invalid token signature" | INVALID_SIGNATURE |
| Expired JWT token | 401 | "Token has expired" | TOKEN_EXPIRED |
| Malformed JWT (invalid format) | 400 | "Invalid token format" | INVALID_TOKEN |

### Error Response Implementation

```python
from fastapi.responses import JSONResponse
from datetime import datetime

def create_error_response(status_code: int, message: str, code: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": message,
            "code": code,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    )
```

---

## Request State Contract

After successful authentication, the following attributes MUST be available on `request.state`:

### request.state.user_id

**Type**: `str` (UUID format)
**Source**: JWT payload `"sub"` claim
**Availability**: All protected routes after middleware
**Usage**: Identify authenticated user, enforce user isolation

**Example**:
```python
@app.get("/api/users/{user_id}/tasks")
async def get_tasks(request: Request, user_id: str):
    authenticated_user_id = request.state.user_id
    if user_id != authenticated_user_id:
        raise HTTPException(403, "Forbidden")
    # Proceed with authenticated user's tasks
```

### request.state.email

**Type**: `str`
**Source**: JWT payload `"email"` claim
**Availability**: All protected routes after middleware
**Usage**: User identification, logging, audit trails

---

## Environment Variables

### BETTER_AUTH_SECRET

**Type**: `str`
**Required**: Yes
**Minimum Length**: 32 characters
**Purpose**: Shared secret for JWT signature verification (must match frontend Better Auth secret)
**Validation**: Middleware MUST validate secret presence and length at module import time
**Error Handling**: Raise `ValueError` with clear message if secret is missing or too short

**Example Validation**:
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

---

## Performance Guarantees

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Middleware overhead | < 10ms per request | Time from middleware entry to call_next() or error response |
| JWT verification | < 5ms per token | Time for jwt.decode() execution |
| Token extraction | < 1ms | Time to extract and parse Authorization header |
| Public route bypass | < 1ms | Time to check path prefix and skip auth |

---

## Security Guarantees

### Token Verification
- MUST verify signature with BETTER_AUTH_SECRET
- MUST check token expiration automatically via python-jose
- MUST specify algorithm explicitly (HS256 only)
- MUST reject tokens signed with different algorithms

### Error Messages
- MUST NOT leak sensitive information (e.g., don't reveal if user exists)
- MUST provide enough information for client-side debugging
- MUST use different error codes for different failure modes

### Stateless Authentication
- MUST NOT store tokens in memory or cache
- MUST verify token on every request (no session caching)
- MUST NOT persist user state between requests

---

## Testing Requirements

### Unit Tests

Middleware function MUST be testable in isolation:
- Mock `request.headers.get()` to simulate different Authorization headers
- Mock `jwt.decode()` to simulate valid/invalid/expired tokens
- Verify error responses match expected format
- Verify public routes bypass authentication

### Integration Tests

Middleware MUST be testable with FastAPI TestClient:
- Test with real JWT tokens generated via python-jose
- Test all error scenarios (missing, expired, invalid tokens)
- Test public routes without tokens
- Test protected routes with valid tokens
- Verify `request.state` attributes accessible in route handlers

---

## Usage Example

### Middleware Registration

```python
# In main.py
from fastapi import FastAPI
from middleware.auth_middleware import verify_jwt_middleware

app = FastAPI()

# Register middleware (runs on all HTTP requests)
app.middleware("http")(verify_jwt_middleware)

# Include routers after middleware
from routes import tasks, users, auth
app.include_router(auth.router)  # Public routes
app.include_router(tasks.router)  # Protected routes
app.include_router(users.router)  # Protected routes
```

### Route Handler Access

```python
# In routes/tasks.py
from fastapi import Request, APIRouter

router = APIRouter()

@router.get("/api/users/{user_id}/tasks")
async def get_tasks(request: Request, user_id: str):
    # Access authenticated user from request state
    authenticated_user_id = request.state.user_id
    authenticated_email = request.state.email

    # Verify user_id in path matches authenticated user
    if user_id != authenticated_user_id:
        raise HTTPException(403, "Forbidden: Cannot access other user's tasks")

    # Query tasks for authenticated user
    tasks = await task_service.get_user_tasks(user_id)
    return {"tasks": tasks}
```

---

## Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| fastapi | 0.104+ | Request/Response objects, middleware support |
| python-jose[cryptography] | 3.3+ | JWT decoding and signature verification |
| python-dotenv | 1.0+ | Environment variable loading |

---

## Change Log

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-24 | Initial contract definition |

---

## Related Contracts

- [JWT Utils Contract](./jwt-utils-contract.md) - Utility functions for token operations
- [REST API Endpoints](/specs/api/rest-endpoints.md) - Protected endpoint definitions
- [User Model Contract](/specs/005-database-foundation/contracts/user-model.md) - User data structure

---

## Compliance

This contract MUST comply with:
- Constitution Principle III: Type Safety (NON-NEGOTIABLE)
- Constitution Principle V: Performance-First Architecture
- REST API Spec: Error Response Format
- Better Auth JWT format and claims structure
