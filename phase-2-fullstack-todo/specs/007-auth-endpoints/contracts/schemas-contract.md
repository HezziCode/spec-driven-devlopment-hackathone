# Schema Contract: Authentication Pydantic Models

**Module**: `backend/schemas/auth.py`
**Purpose**: Pydantic schemas for authentication request validation and response formatting

## Overview

This module defines four Pydantic schemas used by authentication endpoints:

1. **SignupRequest**: Validates user registration input
2. **LoginRequest**: Validates login credentials
3. **UserResponse**: Formats safe user data for responses (excludes password_hash)
4. **AuthResponse**: Combines user and JWT token for auth success responses

All schemas use Pydantic v2 with type hints and Field() constraints.

---

## Schema 1: SignupRequest

### Purpose
Validates user input for POST /auth/signup endpoint.

### Class Definition
```python
from pydantic import BaseModel, Field, EmailStr

class SignupRequest(BaseModel):
    """
    User registration request schema.

    Validates username length, email format, and password minimum length.
    Used by POST /auth/signup endpoint.
    """
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8)
```

### Fields

| Field | Type | Constraints | Validation Error |
|-------|------|-------------|------------------|
| username | str | 3-50 characters, required | "ensure this value has at least 3 characters" |
| email | EmailStr | Valid RFC 5322 email, required | "value is not a valid email address" |
| password | str | Minimum 8 characters, required | "ensure this value has at least 8 characters" |

### Usage Example

**Valid Request**:
```python
request = SignupRequest(
    username="johndoe",
    email="john@example.com",
    password="SecurePass123"
)
# ✓ Passes validation
```

**Invalid Request - Short Username**:
```python
request = SignupRequest(
    username="ab",  # Only 2 characters
    email="john@example.com",
    password="SecurePass123"
)
# ✗ ValidationError: username too short
```

**Invalid Request - Invalid Email**:
```python
request = SignupRequest(
    username="johndoe",
    email="notanemail",  # Not valid email format
    password="SecurePass123"
)
# ✗ ValidationError: invalid email
```

**Invalid Request - Short Password**:
```python
request = SignupRequest(
    username="johndoe",
    email="john@example.com",
    password="Short1"  # Only 6 characters
)
# ✗ ValidationError: password too short
```

### JSON Schema (Auto-Generated)

```json
{
  "properties": {
    "username": {
      "type": "string",
      "minLength": 3,
      "maxLength": 50
    },
    "email": {
      "type": "string",
      "format": "email"
    },
    "password": {
      "type": "string",
      "minLength": 8
    }
  },
  "required": ["username", "email", "password"]
}
```

---

## Schema 2: LoginRequest

### Purpose
Validates user credentials for POST /auth/login endpoint.

### Class Definition
```python
from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    """
    User authentication request schema.

    Validates email format. No password length validation for login
    (users with old passwords should still be able to login).
    Used by POST /auth/login endpoint.
    """
    email: EmailStr
    password: str
```

### Fields

| Field | Type | Constraints | Validation Error |
|-------|------|-------------|------------------|
| email | EmailStr | Valid RFC 5322 email, required | "value is not a valid email address" |
| password | str | Required (no length constraint) | "field required" |

**Note**: No minimum password length for login. This allows users who created accounts before potential rule changes to still login.

### Usage Example

**Valid Request**:
```python
request = LoginRequest(
    email="john@example.com",
    password="SecurePass123"
)
# ✓ Passes validation
```

**Valid Request - Short Password Allowed**:
```python
request = LoginRequest(
    email="john@example.com",
    password="abc"  # Short password OK for login
)
# ✓ Passes validation (password verification happens server-side)
```

**Invalid Request - Missing Password**:
```python
request = LoginRequest(
    email="john@example.com"
)
# ✗ ValidationError: password field required
```

### JSON Schema (Auto-Generated)

```json
{
  "properties": {
    "email": {
      "type": "string",
      "format": "email"
    },
    "password": {
      "type": "string"
    }
  },
  "required": ["email", "password"]
}
```

---

## Schema 3: UserResponse

### Purpose
Formats safe user data for API responses. **Excludes password_hash for security.**

### Class Definition
```python
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class UserResponse(BaseModel):
    """
    User data for API responses.

    SECURITY: Deliberately excludes password_hash field.
    Only includes safe, non-sensitive user information.
    Used in signup and login success responses.
    """
    id: UUID
    username: str
    email: str
    created_at: datetime  # Optional: included in signup, excluded in login
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | User's unique identifier |
| username | str | Yes | User's chosen username |
| email | str | Yes | User's email (always lowercase) |
| created_at | datetime | Optional | Account creation timestamp (ISO 8601) |

**Security Note**: This schema NEVER includes `password_hash` field. If User model from database has password_hash, it must not be passed to this schema.

### Usage Example

**Create from User Model**:
```python
from models import User

# Fetch user from database
user = session.get(User, user_id)

# Create safe response (exclude password_hash)
user_response = UserResponse(
    id=user.id,
    username=user.username,
    email=user.email,
    created_at=user.created_at
    # NOTE: password_hash NOT included
)
```

**JSON Output**:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "johndoe",
  "email": "john@example.com",
  "created_at": "2025-12-24T04:30:00Z"
}
```

**Invalid Usage - Including password_hash**:
```python
# ✗ NEVER DO THIS
user_response = UserResponse(
    id=user.id,
    username=user.username,
    email=user.email,
    created_at=user.created_at,
    password_hash=user.password_hash  # ✗ Security violation!
)
# ValidationError: unexpected field (password_hash not in schema)
```

### JSON Schema (Auto-Generated)

```json
{
  "properties": {
    "id": {
      "type": "string",
      "format": "uuid"
    },
    "username": {
      "type": "string"
    },
    "email": {
      "type": "string"
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    }
  },
  "required": ["id", "username", "email"]
}
```

---

## Schema 4: AuthResponse

### Purpose
Combines user data and JWT token for successful authentication responses.

### Class Definition
```python
from pydantic import BaseModel

class AuthResponse(BaseModel):
    """
    Authentication success response schema.

    Returned by both POST /auth/signup and POST /auth/login
    on successful authentication.

    Contains safe user data and JWT token for subsequent API requests.
    """
    user: UserResponse
    token: str
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| user | UserResponse | Safe user data (excludes password_hash) |
| token | str | JWT token for authorization (7-day expiration) |

### Usage Example

**Create Auth Response**:
```python
# After signup or login success
user_response = UserResponse(
    id=user.id,
    username=user.username,
    email=user.email,
    created_at=user.created_at
)

token = create_jwt_token(user.id, user.email)

auth_response = AuthResponse(
    user=user_response,
    token=token
)
```

**JSON Output**:
```json
{
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "johndoe",
    "email": "john@example.com",
    "created_at": "2025-12-24T04:30:00Z"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjNlNDU2Ny1lODliLTEyZDMtYTQ1Ni00MjY2MTQxNzQwMDAiLCJlbWFpbCI6ImpvaG5AZXhhbXBsZS5jb20iLCJleHAiOjE3MzU2ODQ4MDAsImlhdCI6MTczNTA4MDAwMH0.signature"
}
```

### JSON Schema (Auto-Generated)

```json
{
  "properties": {
    "user": {
      "$ref": "#/definitions/UserResponse"
    },
    "token": {
      "type": "string"
    }
  },
  "required": ["user", "token"]
}
```

---

## Module Structure

### Complete Module Code

```python
"""
Authentication Pydantic schemas for request validation and response formatting.

This module defines schemas used by authentication endpoints:
- SignupRequest: Validates user registration input
- LoginRequest: Validates login credentials
- UserResponse: Formats safe user data (excludes password_hash)
- AuthResponse: Combines user and JWT token

All schemas use Pydantic v2 for automatic validation.
"""

from pydantic import BaseModel, Field, EmailStr
from uuid import UUID
from datetime import datetime


class SignupRequest(BaseModel):
    """User registration request schema with field validation."""
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    """User authentication request schema."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Safe user data for API responses - excludes password_hash."""
    id: UUID
    username: str
    email: str
    created_at: datetime


class AuthResponse(BaseModel):
    """Authentication success response with user data and JWT token."""
    user: UserResponse
    token: str
```

---

## Validation Behavior

### Automatic Validation by FastAPI

When schemas are used in FastAPI route handlers, validation is automatic:

```python
from fastapi import APIRouter
from schemas.auth import SignupRequest, AuthResponse

router = APIRouter()

@router.post("/auth/signup", response_model=AuthResponse, status_code=201)
async def signup_user(request: SignupRequest):
    # If we get here, request is valid (Pydantic validated)
    # request.username is 3-50 characters
    # request.email is valid email format
    # request.password is 8+ characters
    ...
```

### Validation Error Format

FastAPI returns 422 Unprocessable Entity with detailed errors:

```json
{
  "detail": [
    {
      "loc": ["body", "username"],
      "msg": "ensure this value has at least 3 characters",
      "type": "value_error.any_str.min_length",
      "ctx": {"limit_value": 3}
    }
  ]
}
```

---

## Testing Examples

### Test SignupRequest Validation

```python
import pytest
from pydantic import ValidationError
from schemas.auth import SignupRequest

def test_valid_signup_request():
    request = SignupRequest(
        username="testuser",
        email="test@example.com",
        password="SecurePass123"
    )
    assert request.username == "testuser"
    assert request.email == "test@example.com"

def test_short_username():
    with pytest.raises(ValidationError) as exc_info:
        SignupRequest(
            username="ab",
            email="test@example.com",
            password="SecurePass123"
        )
    assert "min_length" in str(exc_info.value)

def test_invalid_email():
    with pytest.raises(ValidationError) as exc_info:
        SignupRequest(
            username="testuser",
            email="notanemail",
            password="SecurePass123"
        )
    assert "email" in str(exc_info.value)
```

### Test UserResponse Excludes password_hash

```python
from schemas.auth import UserResponse
from uuid import uuid4
from datetime import datetime

def test_user_response_no_password_hash():
    user_data = {
        "id": uuid4(),
        "username": "testuser",
        "email": "test@example.com",
        "created_at": datetime.utcnow()
    }

    user_response = UserResponse(**user_data)

    # Verify password_hash not in schema
    assert "password_hash" not in user_response.model_dump()

    # Verify expected fields present
    assert user_response.username == "testuser"
    assert user_response.email == "test@example.com"
```

---

## Security Checklist

- ✅ **password_hash** NEVER included in UserResponse
- ✅ **password** field validated on signup (min 8 characters)
- ✅ **email** format validated with EmailStr (RFC 5322)
- ✅ **username** length constrained (3-50 characters)
- ✅ Pydantic automatic validation prevents invalid data
- ✅ Type hints on all fields (no Any types)
- ✅ Docstrings explain security considerations

---

## Notes

- All schemas use Pydantic v2 (included with FastAPI 0.104+)
- EmailStr requires email-validator library (installed with pydantic[email])
- FastAPI automatically converts Pydantic schemas to OpenAPI/JSON Schema
- Schemas are reusable across different route handlers
- created_at field optional in UserResponse (included in signup, excluded in login)
- No config class needed (Pydantic v2 uses model_config)
