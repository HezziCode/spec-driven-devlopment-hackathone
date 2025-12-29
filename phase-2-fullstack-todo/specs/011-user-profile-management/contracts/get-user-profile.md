# API Contract: GET /users/{user_id}

**Endpoint**: Get User Profile
**Method**: GET
**Path**: `/users/{user_id}`
**Purpose**: Retrieve authenticated user's profile information

---

## Request Specification

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | UUID | Yes | User's unique identifier (must match authenticated user) |

**Example**: `/users/3fa85f64-5717-4562-b3fc-2c963f66afa6`

---

### Headers

| Header | Value | Required | Description |
|--------|-------|----------|-------------|
| `Authorization` | `Bearer {jwt_token}` | Yes | JWT token for authentication |

**Example**:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

### Query Parameters

None

---

### Request Body

None (GET request)

---

## Response Specification

### Success Response (200 OK)

**Status Code**: 200
**Content-Type**: application/json

**Body Schema**:
```json
{
  "id": "string (UUID)",
  "username": "string",
  "email": "string",
  "created_at": "string (ISO 8601 datetime)",
  "updated_at": "string (ISO 8601 datetime)"
}
```

**Example**:
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "username": "john_doe",
  "email": "john@example.com",
  "created_at": "2025-12-25T10:00:00Z",
  "updated_at": "2025-12-25T15:30:00Z"
}
```

**Field Descriptions**:
- `id`: User's unique identifier (UUID v4 format)
- `username`: User's display name (3-50 characters)
- `email`: User's email address (valid email format)
- `created_at`: Account creation timestamp (UTC, ISO 8601)
- `updated_at`: Last profile modification timestamp (UTC, ISO 8601)

**Security Note**: `password_hash` field is **NEVER** included in response

---

### Error Responses

#### 401 Unauthorized

**Scenario**: Missing, invalid, or expired JWT token

**Body**:
```json
{
  "error": "Authentication required",
  "code": "AUTHENTICATION_ERROR",
  "timestamp": "2025-12-25T10:00:00Z"
}
```

**Triggers**:
- Missing `Authorization` header
- Invalid JWT token format
- Expired JWT token
- Invalid JWT signature

---

#### 403 Forbidden

**Scenario**: Authenticated user attempting to access another user's profile

**Body**:
```json
{
  "error": "Not authorized to view this profile",
  "code": "AUTHORIZATION_ERROR",
  "timestamp": "2025-12-25T10:00:00Z"
}
```

**Triggers**:
- Path `user_id` does not match authenticated user's ID from JWT token

**Example**:
- JWT contains `user_id=123`
- Request: `GET /users/456`
- Result: 403 Forbidden

---

#### 404 Not Found

**Scenario**: User ID does not exist in database

**Body**:
```json
{
  "error": "User not found",
  "code": "NOT_FOUND",
  "timestamp": "2025-12-25T10:00:00Z"
}
```

**Triggers**:
- Valid UUID format but user does not exist
- User was deleted

**Note**: This error occurs even if `user_id` matches authenticated user (e.g., after account deletion)

---

#### 422 Unprocessable Entity

**Scenario**: Invalid UUID format in path parameter

**Body**:
```json
{
  "error": "Invalid user ID format",
  "code": "VALIDATION_ERROR",
  "timestamp": "2025-12-25T10:00:00Z"
}
```

**Triggers**:
- `user_id` is not a valid UUID format
- Example: `/users/not-a-uuid`

---

## Request Flow

```
1. Client sends GET request with JWT token in Authorization header
   ↓
2. Middleware verifies JWT token and extracts user_id
   ↓
3. Route handler validates path user_id matches JWT user_id
   ↓
4. Service layer queries database for user by id
   ↓
5. Pydantic response_model excludes password_hash field
   ↓
6. Return 200 OK with user profile (without password_hash)
```

---

## Security Requirements

### Authentication

- **MUST** verify JWT token signature using `BETTER_AUTH_SECRET`
- **MUST** check token expiration
- **MUST** extract user_id from JWT payload

### Authorization

- **MUST** verify path `user_id` matches JWT `user_id`
- **MUST** return 403 if mismatch (not 404, to prevent user enumeration)

### Data Protection

- **MUST** exclude `password_hash` from response
- **MUST** use Pydantic `response_model` for automatic exclusion
- **MUST** never query or return sensitive fields

---

## Performance Requirements

- **Latency**: <1 second for 95th percentile requests
- **Concurrency**: Support 500 concurrent requests
- **Database Queries**: Exactly 1 query per request (no N+1)
- **Caching**: Optional (profile data changes infrequently)

---

## Example Requests

### Successful Request

**Request**:
```http
GET /users/3fa85f64-5717-4562-b3fc-2c963f66afa6 HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response**:
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "username": "john_doe",
  "email": "john@example.com",
  "created_at": "2025-12-25T10:00:00Z",
  "updated_at": "2025-12-25T15:30:00Z"
}
```

---

### Cross-User Access Attempt

**Request** (JWT contains user_id=123):
```http
GET /users/456 HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response**:
```http
HTTP/1.1 403 Forbidden
Content-Type: application/json

{
  "error": "Not authorized to view this profile",
  "code": "AUTHORIZATION_ERROR",
  "timestamp": "2025-12-25T10:00:00Z"
}
```

---

### Missing Authentication

**Request**:
```http
GET /users/3fa85f64-5717-4562-b3fc-2c963f66afa6 HTTP/1.1
Host: api.example.com
```

**Response**:
```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
  "error": "Authentication required",
  "code": "AUTHENTICATION_ERROR",
  "timestamp": "2025-12-25T10:00:00Z"
}
```

---

## Testing Checklist

- [ ] Successful profile retrieval (200)
- [ ] Password hash excluded from response
- [ ] Cross-user access blocked (403)
- [ ] Missing token returns 401
- [ ] Invalid token returns 401
- [ ] Expired token returns 401
- [ ] Non-existent user returns 404
- [ ] Invalid UUID format returns 422
- [ ] Response matches schema exactly
- [ ] Latency <1s for 95th percentile

---

## Implementation Notes

### Route Handler Pattern

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
        raise HTTPException(status_code=403, detail="Not authorized to view this profile")

    # Get profile
    user = get_user_profile(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user  # Pydantic excludes password_hash automatically
```

### Service Layer Pattern

```python
def get_user_profile(session: Session, user_id: UUID) -> Optional[User]:
    """Retrieve user profile by ID."""
    return session.get(User, user_id)
```

### Schema Pattern

```python
class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # SQLModel → Pydantic conversion
```
