# JWT Utilities Contract

**Module**: `backend/utils/jwt_utils.py`
**Version**: 1.0.0
**Status**: Draft

## Overview

This contract defines the public interface for JWT utility functions that provide token decoding, verification, and user extraction capabilities. These utilities are used by the authentication middleware and can be reused across the application for JWT operations.

---

## Public Functions

### Function: decode_token

**Signature**:
```python
def decode_token(token: str) -> dict[str, Any]
```

**Purpose**: Decode and verify JWT token, returning payload dictionary.

**Parameters**:
- `token: str` - JWT token string (without "Bearer " prefix)

**Returns**:
- `dict[str, Any]` - JWT payload containing claims (sub, email, exp, iat, etc.)

**Raises**:
- `jose.JWTError` - If token signature is invalid or token is malformed
- `jose.ExpiredSignatureError` (subclass of JWTError) - If token has expired

**Behavior**:
- Verifies JWT signature using BETTER_AUTH_SECRET
- Checks token expiration automatically (raises ExpiredSignatureError if expired)
- Decodes payload and returns as dictionary
- Uses HS256 algorithm for signature verification

**Example**:
```python
from utils.jwt_utils import decode_token
from jose import JWTError, ExpiredSignatureError

try:
    payload = decode_token("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    user_id = payload.get("sub")
    email = payload.get("email")
    exp = payload.get("exp")
except ExpiredSignatureError:
    print("Token has expired")
except JWTError:
    print("Invalid token signature or format")
```

**Type Safety**:
- Input: Fully typed (`str`)
- Output: `dict[str, Any]` (Any is necessary due to dynamic JWT payload structure)
- Exceptions: Explicitly documented

---

### Function: verify_token

**Signature**:
```python
def verify_token(token: str) -> bool
```

**Purpose**: Verify JWT token signature and expiration without raising exceptions.

**Parameters**:
- `token: str` - JWT token string (without "Bearer " prefix)

**Returns**:
- `bool` - True if token is valid and not expired, False otherwise

**Raises**:
- Does NOT raise exceptions; catches all JWTError internally and returns False

**Behavior**:
- Calls `decode_token()` internally
- Returns True if decoding succeeds (token valid and not expired)
- Returns False if ExpiredSignatureError is raised (token expired)
- Returns False if JWTError is raised (invalid signature or malformed)

**Example**:
```python
from utils.jwt_utils import verify_token

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

if verify_token(token):
    print("Token is valid")
else:
    print("Token is invalid or expired")
```

**Use Cases**:
- Quick token validation without exception handling
- Conditional logic based on token validity
- Logging and monitoring (count valid vs invalid tokens)

---

### Function: extract_user_from_token

**Signature**:
```python
def extract_user_from_token(token: str, session: Session) -> Optional[User]
```

**Purpose**: Decode JWT token, extract user_id from payload, query database, and return User object.

**Parameters**:
- `token: str` - JWT token string (without "Bearer " prefix)
- `session: Session` - SQLModel database session for querying User table

**Returns**:
- `Optional[User]` - User model instance if found in database, None if not found or token invalid

**Raises**:
- Does NOT raise exceptions for JWT errors; returns None for invalid tokens
- MAY raise database exceptions (connection errors, etc.)

**Behavior**:
1. Call `decode_token()` to get JWT payload
2. Extract user_id from payload `"sub"` claim (UUID string)
3. Query database: `session.get(User, user_id)`
4. Return User object if found, None if not found
5. Return None if token is invalid or expired (catches JWTError)

**Example**:
```python
from utils.jwt_utils import extract_user_from_token
from db import get_session
from models import User

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

with get_session() as session:
    user = extract_user_from_token(token, session)
    if user:
        print(f"User found: {user.username} ({user.email})")
    else:
        print("User not found or token invalid")
```

**Use Cases**:
- Retrieve full User object from JWT token
- Validate that user_id in token still exists in database
- Access user attributes beyond JWT claims (e.g., password_hash, created_at)

**Type Safety**:
- Input: Fully typed (`str`, `Session`)
- Output: `Optional[User]` (None if not found)
- Handles None gracefully (no NoneType errors)

---

## JWT Payload Structure

All functions expect JWT tokens with the following payload claims:

### Required Claims

| Claim | Type | Description | Example |
|-------|------|-------------|---------|
| `sub` | string (UUID) | User ID (subject) | "123e4567-e89b-12d3-a456-426614174000" |
| `email` | string | User email address | "user@example.com" |
| `exp` | number (Unix timestamp) | Expiration time | 1703462400 |
| `iat` | number (Unix timestamp) | Issued at time | 1703376000 |

### Optional Claims

| Claim | Type | Description |
|-------|------|-------------|
| `username` | string | Username (if included by Better Auth) |
| `jti` | string | JWT ID (unique token identifier) |
| `aud` | string | Audience (intended recipient) |

**Example Payload**:
```json
{
  "sub": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "exp": 1703462400,
  "iat": 1703376000,
  "jti": "unique-token-id"
}
```

---

## Environment Variables

### BETTER_AUTH_SECRET

**Type**: `str`
**Required**: Yes
**Minimum Length**: 32 characters
**Purpose**: Shared secret for JWT signature verification
**Validation**: Module MUST validate secret presence and length at import time

**Validation Code**:
```python
import os
from dotenv import load_dotenv

load_dotenv()
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")

if not BETTER_AUTH_SECRET:
    raise ValueError(
        "BETTER_AUTH_SECRET environment variable is required. "
        "Set it in backend/.env file."
    )

if len(BETTER_AUTH_SECRET) < 32:
    raise ValueError(
        "BETTER_AUTH_SECRET must be at least 32 characters. "
        "Generate with: openssl rand -base64 32"
    )
```

---

## Error Handling

### Exception Hierarchy

```
Exception
└── jose.JWTError (base exception for all JWT errors)
    ├── jose.ExpiredSignatureError (token expired)
    ├── jose.JWTClaimsError (invalid claims)
    └── jose.JWSError (signature verification failed)
```

### Error Handling Strategy

| Function | Error Handling | Rationale |
|----------|----------------|-----------|
| decode_token() | Raises exceptions | Caller decides how to handle errors |
| verify_token() | Returns False | Simple boolean API, no exception handling needed |
| extract_user_from_token() | Returns None | Graceful failure for missing users or invalid tokens |

---

## Performance Guarantees

| Operation | Target | Measurement Method |
|-----------|--------|-------------------|
| decode_token() | < 2ms | Time for jwt.decode() execution |
| verify_token() | < 2ms | Same as decode_token() (calls it internally) |
| extract_user_from_token() | < 50ms | Includes database query (O(1) primary key lookup) |

---

## Testing Requirements

### Unit Tests for decode_token()

- Test with valid token → returns payload dict with correct claims
- Test with expired token → raises ExpiredSignatureError
- Test with invalid signature → raises JWTError
- Test with malformed token → raises JWTError
- Test payload contains expected fields (sub, email, exp, iat)

### Unit Tests for verify_token()

- Test with valid token → returns True
- Test with expired token → returns False
- Test with invalid signature → returns False
- Test with malformed token → returns False

### Unit Tests for extract_user_from_token()

- Test with valid token and existing user → returns User object
- Test with valid token but nonexistent user → returns None
- Test with expired token → returns None
- Test with invalid token → returns None
- Test User object has correct attributes (id, email, username)

---

## Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| python-jose[cryptography] | 3.3+ | JWT decoding and verification |
| sqlmodel | Latest | Session type, User model |
| python-dotenv | 1.0+ | Environment variable loading |

---

## Import Structure

### Module Exports

```python
# In utils/jwt_utils.py
__all__ = ["decode_token", "verify_token", "extract_user_from_token"]
```

### Import Examples

```python
# Import all utilities
from utils.jwt_utils import decode_token, verify_token, extract_user_from_token

# Import specific utility
from utils.jwt_utils import verify_token

# Import with alias
from utils.jwt_utils import extract_user_from_token as get_user_from_jwt
```

---

## Usage Examples

### Example 1: Token Validation

```python
from utils.jwt_utils import verify_token

def is_authenticated(auth_header: str) -> bool:
    if not auth_header or not auth_header.startswith("Bearer "):
        return False

    token = auth_header.split(" ")[1]
    return verify_token(token)
```

### Example 2: User Extraction in Route Handler

```python
from fastapi import Request, Depends
from utils.jwt_utils import extract_user_from_token
from db import get_session

@app.get("/api/profile")
async def get_profile(request: Request, session: Session = Depends(get_session)):
    # Extract token from request (already validated by middleware)
    auth_header = request.headers.get("Authorization")
    token = auth_header.split(" ")[1]

    # Get full User object from database
    user = extract_user_from_token(token, session)
    if not user:
        raise HTTPException(404, "User not found")

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at
    }
```

### Example 3: Manual Token Inspection

```python
from utils.jwt_utils import decode_token
from jose import JWTError

def inspect_token(token: str):
    try:
        payload = decode_token(token)
        print(f"User ID: {payload.get('sub')}")
        print(f"Email: {payload.get('email')}")
        print(f"Expires: {payload.get('exp')}")
    except JWTError as e:
        print(f"Invalid token: {e}")
```

---

## Type Annotations

All functions MUST have complete type annotations:

```python
from typing import Optional, Any
from sqlmodel import Session
from models import User
from jose import JWTError, ExpiredSignatureError

def decode_token(token: str) -> dict[str, Any]:
    """Decode and verify JWT token."""
    ...

def verify_token(token: str) -> bool:
    """Verify JWT token validity."""
    ...

def extract_user_from_token(token: str, session: Session) -> Optional[User]:
    """Extract User from JWT token."""
    ...
```

**Mypy Compliance**: All type hints MUST pass mypy strict mode with zero errors.

---

## Security Considerations

### Token Handling
- MUST verify signature with BETTER_AUTH_SECRET
- MUST check expiration automatically
- MUST use HS256 algorithm exclusively
- MUST NOT log or store token strings

### Error Messages
- MUST NOT reveal if user exists in database
- MUST use generic error messages
- MAY log detailed errors for debugging (server-side only)

### Database Queries
- User lookup by primary key (UUID) is O(1) with proper indexing
- MUST NOT execute N+1 queries in loops
- Consider caching User objects if called frequently (future optimization)

---

## Change Log

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-24 | Initial contract definition |

---

## Related Contracts

- [Middleware Contract](./middleware-contract.md) - JWT authentication middleware
- [User Model Contract](/specs/005-database-foundation/contracts/user-model.md) - User data structure
- [REST API Endpoints](/specs/api/rest-endpoints.md) - Protected endpoint definitions

---

## Compliance

This contract MUST comply with:
- Constitution Principle III: Type Safety (NON-NEGOTIABLE)
- Constitution Principle II: Clean Code with Single Responsibility
- Better Auth JWT format and claims structure
- python-jose API and exception handling patterns
