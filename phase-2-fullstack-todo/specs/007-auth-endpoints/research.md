# Technical Research: User Authentication Endpoints

**Feature**: 007-auth-endpoints
**Date**: 2025-12-24
**Status**: Complete

## Research Summary

This document captures technical research decisions for implementing three authentication endpoints (signup, login, logout) with password hashing and JWT token generation.

## Research Questions and Findings

### 1. Passlib CryptContext Configuration for Bcrypt

**Question**: How to configure passlib CryptContext for bcrypt with 12 rounds?

**Research Method**: Review passlib documentation and bcrypt best practices

**Finding**: Use `CryptContext(schemes=["bcrypt"], bcrypt__rounds=12, deprecated="auto")`

**Rationale**:
- bcrypt with 12 rounds provides 2^12 = 4096 iterations
- Balances security (resistant to brute force) and performance (~200ms)
- `deprecated="auto"` allows future algorithm upgrades without code changes
- Passlib provides unified interface for multiple hash schemes

**Implementation**:
```python
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    bcrypt__rounds=12,
    deprecated="auto"
)

# Hash password
password_hash = pwd_context.hash("SecurePassword123")
# Result: "$2b$12$..." (bcrypt identifier with 12 rounds)

# Verify password
is_valid = pwd_context.verify("SecurePassword123", password_hash)
# Result: True (constant-time comparison)
```

**Performance Considerations**:
- 12 rounds: ~200ms on modern CPU (acceptable for login/signup)
- 10 rounds: ~50ms (too fast, less secure)
- 14 rounds: ~800ms (too slow, poor UX)

**References**:
- passlib documentation: https://passlib.readthedocs.io/en/stable/lib/passlib.context.html
- OWASP password storage: Recommends bcrypt with 10+ rounds

---

### 2. Password Verification Pattern

**Question**: What's the correct pattern for verifying passwords with passlib?

**Research Method**: Review passlib CryptContext API

**Finding**: Use `pwd_context.verify(plain_password, password_hash)` returning boolean

**Rationale**:
- Single method call handles timing-safe comparison
- Returns boolean (True if match, False if mismatch)
- Prevents timing attacks by using constant-time comparison
- Handles different hash formats automatically (future-proof)

**Implementation**:
```python
# In login endpoint
user = session.exec(select(User).where(func.lower(User.email) == email.lower())).first()
if not user:
    return error_response(401, "Invalid credentials", "UNAUTHORIZED")

# Verify password
is_valid = pwd_context.verify(request.password, user.password_hash)
if not is_valid:
    return error_response(401, "Invalid credentials", "UNAUTHORIZED")

# Proceed with login
```

**Security Note**:
- Always use same error message for "user not found" and "wrong password"
- Prevents username enumeration attacks
- "Invalid credentials" is generic and secure

---

### 3. JWT Token Generation with 7-Day Expiration

**Question**: How to generate JWT tokens with python-jose including 7-day expiration?

**Research Method**: Review python-jose API and JWT RFC 7519

**Finding**: Use `jwt.encode()` with payload including sub, email, exp, iat claims

**Rationale**:
- `sub` (subject) claim for user_id (JWT standard)
- `email` claim for user identification
- `exp` (expiration) claim for automatic validation
- `iat` (issued-at) claim for audit trail
- HS256 algorithm matches JWT middleware configuration

**Implementation**:
```python
from jose import jwt
from datetime import datetime, timedelta
from uuid import UUID
import os

BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")

def create_jwt_token(user_id: UUID, email: str) -> str:
    """Generate JWT token with 7-day expiration."""
    now = datetime.utcnow()
    payload = {
        "sub": str(user_id),  # Convert UUID to string
        "email": email,
        "exp": now + timedelta(days=7),  # 7 days from now
        "iat": now  # Issued-at timestamp
    }
    token = jwt.encode(payload, BETTER_AUTH_SECRET, algorithm="HS256")
    return token
```

**Token Structure**:
```json
{
  "sub": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "exp": 1735084800,
  "iat": 1734480000
}
```

**Expiration Calculation**:
- Current time: `datetime.utcnow()`
- Expiration: `current + timedelta(days=7)`
- Automatic validation by JWT middleware (python-jose checks exp claim)

---

### 4. Case-Insensitive Email Lookup with SQLModel

**Question**: How to implement case-insensitive email uniqueness checking?

**Research Method**: Review SQLAlchemy func documentation and PostgreSQL LOWER() function

**Finding**: Use `func.lower(User.email) == email.lower()` with functional index

**Rationale**:
- Email addresses are case-insensitive per RFC 5321
- Users should be able to login with "TEST@Example.COM" or "test@example.com"
- Functional index on LOWER(email) provides performance
- Normalize email to lowercase before storage for consistency

**Implementation**:
```python
from sqlmodel import select, func

# Check email uniqueness (case-insensitive)
statement = select(User).where(func.lower(User.email) == request.email.lower())
existing_user = session.exec(statement).first()

if existing_user:
    return error_response(409, "Email already registered", "CONFLICT")

# Store email normalized to lowercase
new_user = User(
    username=request.username,
    email=request.email.lower(),  # Always store lowercase
    password_hash=password_hash
)
```

**Database Index** (add to migration if not exists):
```sql
CREATE INDEX idx_users_email_lower ON users(LOWER(email));
```

**Alternative Considered**:
- PostgreSQL ILIKE operator: `User.email.ilike(email)`
  - Pros: Simpler syntax
  - Cons: PostgreSQL-specific, no index usage
  - Decision: Rejected, prefer portable solution

---

### 5. Pydantic EmailStr Validation

**Question**: How to validate email format in Pydantic schemas?

**Research Method**: Review Pydantic field types documentation

**Finding**: Import `EmailStr` from pydantic and use as field type

**Rationale**:
- Built-in email validation using RFC 5322 regex
- Automatic validation error messages
- Type-safe (EmailStr is subclass of str)
- No external dependencies needed

**Implementation**:
```python
from pydantic import BaseModel, Field, EmailStr

class SignupRequest(BaseModel):
    """Signup request with validated email."""
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr  # Automatic email format validation
    password: str = Field(min_length=8)

# Usage
request = SignupRequest(
    username="johndoe",
    email="invalid-email",  # ValidationError: value is not a valid email address
    password="SecurePass123"
)
```

**Validation Errors**:
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

---

### 6. FastAPI Response Model Excluding password_hash

**Question**: How to ensure password_hash never appears in API responses?

**Research Method**: Review Pydantic model design patterns and FastAPI response_model

**Finding**: Create separate UserResponse schema excluding password_hash

**Rationale**:
- Pydantic schemas define explicit response structure
- Never include password_hash field in response schemas
- FastAPI automatically serializes using response_model
- Compile-time safety (no runtime risk of exposure)

**Implementation**:
```python
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class UserResponse(BaseModel):
    """User data for API responses - deliberately excludes password_hash."""
    id: UUID
    username: str
    email: str
    created_at: datetime
    # NOTE: password_hash NOT included for security

class AuthResponse(BaseModel):
    """Authentication success response."""
    user: UserResponse
    token: str

@router.post("/auth/signup", response_model=AuthResponse, status_code=201)
async def signup_user(request: SignupRequest, session: Session = Depends(get_session)):
    # ... create user with password_hash in database ...

    # Create response (password_hash not accessible)
    user_response = UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        created_at=user.created_at
    )
    return AuthResponse(user=user_response, token=token)
```

**Security Guarantee**:
- Even if User model has password_hash field, UserResponse doesn't
- FastAPI only serializes fields defined in response_model
- Impossible to accidentally leak password_hash

---

### 7. Duplicate Checking Strategy

**Question**: Should duplicate checking be done at application or database level?

**Research Method**: Review database transaction patterns and error handling

**Finding**: Check at application level for specific errors, enforce at database level for integrity

**Rationale**:
- Application-level checking provides specific error messages
- Database unique constraints prevent race conditions
- Two-layer defense (application + database)
- Better UX with specific error messages

**Implementation**:
```python
# Application-level duplicate checking (specific errors)
statement = select(User).where(User.username == request.username)
if session.exec(statement).first():
    return error_response(409, "Username already exists", "CONFLICT")

statement = select(User).where(func.lower(User.email) == request.email.lower())
if session.exec(statement).first():
    return error_response(409, "Email already registered", "CONFLICT")

# Database-level enforcement (data integrity)
# Unique constraints on users.username and users.email (already in schema)
```

**Race Condition Handling**:
- If two requests check simultaneously, both might pass application check
- Database unique constraint catches duplicate at commit time
- Catch IntegrityError and return 409

**Order of Checking**:
1. Check username first (faster, case-sensitive)
2. Check email second (requires LOWER() function)
3. Create user (database enforces uniqueness)

---

### 8. Error Response Standardization

**Question**: What format should authentication errors use?

**Research Method**: Review REST API best practices and existing JWT middleware format

**Finding**: Use standardized `{error, code, timestamp}` structure matching JWT middleware

**Rationale**:
- Consistency across all API endpoints
- Machine-parseable error codes
- Human-readable error messages
- Timestamp for debugging and audit

**Implementation**:
```python
from fastapi.responses import JSONResponse
from datetime import datetime

def error_response(status_code: int, message: str, code: str) -> JSONResponse:
    """Create standardized error response matching JWT middleware format."""
    return JSONResponse(
        status_code=status_code,
        content={
            "error": message,  # Human-readable message
            "code": code,       # Machine-parseable code
            "timestamp": datetime.utcnow().isoformat() + "Z"  # ISO 8601 UTC
        }
    )

# Usage examples
return error_response(409, "Username already exists", "CONFLICT")
return error_response(401, "Invalid credentials", "UNAUTHORIZED")
return error_response(422, "Password must be at least 8 characters", "VALIDATION_ERROR")
```

**Error Format Example**:
```json
{
  "error": "Username already exists",
  "code": "CONFLICT",
  "timestamp": "2025-12-24T04:30:00Z"
}
```

**Status Codes**:
- 401: Authentication failure (wrong credentials, missing token)
- 409: Conflict (duplicate username/email)
- 422: Validation error (invalid input format)
- 500: Internal server error (database failure, hashing failure)

---

## Technology Stack Decisions

### Core Dependencies

| Library | Version | Purpose | Rationale |
|---------|---------|---------|-----------|
| passlib[bcrypt] | 1.7+ | Password hashing | Industry standard, bcrypt with configurable rounds |
| python-jose[cryptography] | 3.3+ | JWT generation | Already installed, matches JWT middleware |
| FastAPI | 0.104+ | Route handlers | Already installed, async support |
| SQLModel | Latest | Database operations | Already installed, type-safe ORM |
| pydantic | 2.5+ | Schema validation | Included with FastAPI, EmailStr support |

### Why passlib over bcrypt library directly?

**Decision**: Use passlib[bcrypt]

**Rationale**:
- Unified interface (CryptContext) for multiple algorithms
- Supports algorithm migration (deprecated="auto")
- Automatic work factor configuration
- Built-in timing-safe verification
- More flexible than bcrypt library alone

**Example**:
```python
# passlib (chosen)
pwd_context = CryptContext(schemes=["bcrypt"], bcrypt__rounds=12)
password_hash = pwd_context.hash("password")
is_valid = pwd_context.verify("password", password_hash)

# bcrypt directly (rejected)
import bcrypt
password_hash = bcrypt.hashpw(b"password", bcrypt.gensalt(rounds=12))
is_valid = bcrypt.checkpw(b"password", password_hash)
# Less flexible, manual configuration, bytes handling
```

---

## Performance Analysis

### Password Hashing Performance

**Bcrypt Round Benchmarks** (on modern CPU):

| Rounds | Time | Security Level | Decision |
|--------|------|----------------|----------|
| 10 | ~50ms | Minimum acceptable | Too fast |
| 12 | ~200ms | Recommended 2025 | ✅ Chosen |
| 13 | ~400ms | High security | Too slow |
| 14 | ~800ms | Very high security | UX impact |

**Decision**: 12 rounds balances security and UX

### JWT Generation Performance

**Operation Timings**:
- JWT payload creation: < 1ms (dict operations)
- JWT encoding with HS256: ~5ms (HMAC-SHA256)
- Total JWT generation: < 10ms

**Decision**: JWT generation overhead negligible

### Database Query Performance

**Query Types**:
- Username lookup (indexed): ~2ms (indexed unique column)
- Email lookup (functional index): ~3ms (LOWER() with index)
- User creation: ~10ms (INSERT with UUID generation)

**Total Signup Time Estimate**: ~230ms
- Validation: 1ms (Pydantic)
- Username check: 2ms
- Email check: 3ms
- Password hashing: 200ms (bcrypt 12 rounds)
- User creation: 10ms
- JWT generation: 5ms
- Response formatting: 1ms

**Total Login Time Estimate**: ~215ms
- Validation: 1ms
- Email lookup: 3ms
- Password verification: 200ms (bcrypt)
- JWT generation: 5ms
- Response formatting: 1ms

**Decision**: Both endpoints meet < 500ms requirement

---

## Security Considerations

### Password Storage

**Requirement**: Never store plaintext passwords
**Solution**: Hash with bcrypt before storage
**Verification**: Check password_hash starts with "$2b$12$"

### Password Verification Timing

**Attack**: Timing attacks to enumerate users
**Solution**: Use same error message for "user not found" and "wrong password"
**Implementation**: Return "Invalid credentials" in both cases

### Email Enumeration Prevention

**Attack**: Signup with existing email to check if user exists
**Solution**: Return same 409 error for both username and email duplicates
**Note**: Some enumeration unavoidable (required for UX)

### JWT Token Security

**Secret Management**: BETTER_AUTH_SECRET in environment variables
**Algorithm**: HS256 (symmetric, no key rotation needed for Phase 2)
**Expiration**: 7 days (balance between security and convenience)
**Payload**: Include only non-sensitive data (user_id, email)

### Response Security

**Requirement**: Never expose password_hash
**Solution**: Use separate UserResponse schema excluding sensitive fields
**Verification**: Test all response bodies

---

## Testing Strategy

### Unit Tests

**schemas/auth.py**:
- Valid input passes validation
- Invalid input raises ValidationError
- Email format validation
- Username length validation
- Password length validation

**routes/auth.py** (mocked dependencies):
- JWT generation produces correct structure
- Error responses have correct format
- Duplicate checking logic

### Integration Tests

**POST /auth/signup**:
- Valid signup creates user and returns token
- Duplicate username returns 409
- Duplicate email (case-insensitive) returns 409
- Invalid input returns 422
- Password hashed correctly in database
- password_hash not in response

**POST /auth/login**:
- Correct credentials return token
- Wrong password returns 401
- Nonexistent email returns 401
- Case-insensitive email works

**POST /auth/logout**:
- Always returns 200 with success message

### Performance Tests

- Signup completes in < 500ms
- Login completes in < 300ms
- Bcrypt hashing takes ~200ms

---

## Open Questions and Answers

### Q: Should we implement rate limiting on authentication endpoints?

**Answer**: Not in scope for Phase 2. Authentication endpoints are vulnerable to brute force, but rate limiting is a separate security feature. Document as future enhancement.

### Q: Should we implement password strength requirements beyond length?

**Answer**: Not in scope. Spec only requires 8-character minimum. Password strength meter and complexity rules are future enhancements.

### Q: Should logout invalidate the JWT token?

**Answer**: No, JWT tokens are stateless. Logout returns success for frontend to clear local storage, but token remains valid until expiration. Token revocation/blacklisting is future feature.

### Q: How to handle database connection failures during signup/login?

**Answer**: Catch database exceptions, return 500 Internal Server Error with generic message. Log detailed error for debugging. Never expose database details to client.

### Q: Should we send email verification after signup?

**Answer**: Not in scope for Phase 2. Account is immediately active after signup. Email verification is future enhancement.

---

## Implementation Dependencies

### Prerequisites

- ✅ Database foundation complete (User model with password_hash field)
- ✅ JWT middleware complete (can verify tokens generated by auth endpoints)
- ✅ BETTER_AUTH_SECRET configured in backend/.env
- ✅ Database connection working (db.py with get_session())

### New Dependencies to Install

- passlib[bcrypt] 1.7+ (add with `uv add passlib[bcrypt]`)

### Files to Create

- backend/schemas/auth.py (Pydantic schemas)
- backend/routes/auth.py (authentication endpoints)
- backend/tests/test_auth_schemas.py (schema tests)
- backend/tests/test_auth_routes.py (endpoint tests)

### Files to Update

- backend/main.py (register auth router)
- backend/.env.example (document auth configuration)
- backend/tests/conftest.py (add auth test fixtures)
- backend/pyproject.toml (add passlib dependency)

---

## References

- passlib documentation: https://passlib.readthedocs.io/
- python-jose documentation: https://python-jose.readthedocs.io/
- JWT RFC 7519: https://datatracker.ietf.org/doc/html/rfc7519
- OWASP Password Storage: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
- FastAPI Security: https://fastapi.tiangolo.com/tutorial/security/
- Pydantic EmailStr: https://docs.pydantic.dev/latest/api/types/#pydantic.types.EmailStr

---

**Research Complete**: 2025-12-24
**Next Step**: Create contracts and quickstart documentation, then proceed to /sp.tasks
