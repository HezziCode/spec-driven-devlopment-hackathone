# API Contract: POST /auth/login

**Endpoint**: `POST /auth/login`
**Purpose**: Authenticate existing user with email and password
**Authentication**: None required (public endpoint)

## Request

### Method
```
POST
```

### Path
```
/auth/login
```

### Headers
```
Content-Type: application/json
```

### Body Schema
```json
{
  "email": "string (valid email format, required)",
  "password": "string (required)"
}
```

### Body Example
```json
{
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

### Validation Rules

| Field | Type | Constraints | Error Message |
|-------|------|-------------|---------------|
| email | string | Valid email format (RFC 5322), required | "Invalid email format" |
| password | string | Required (no minimum length for login) | "Field required" |

**Note**: Password length validation only applies to signup, not login. Users who created accounts before potential rule changes should still be able to login.

## Response

### Success Response (200 OK)

**Status Code**: `200 OK`

**Body Schema**:
```json
{
  "user": {
    "id": "UUID (string format)",
    "username": "string",
    "email": "string (lowercase)"
  },
  "token": "string (JWT token)"
}
```

**Body Example**:
```json
{
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "johndoe",
    "email": "john@example.com"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjNlNDU2Ny1lODliLTEyZDMtYTQ1Ni00MjY2MTQxNzQwMDAiLCJlbWFpbCI6ImpvaG5AZXhhbXBsZS5jb20iLCJleHAiOjE3MzU2ODQ4MDAsImlhdCI6MTczNTA4MDAwMH0.signature"
}
```

**Response Guarantees**:
- `user` object does NOT include `created_at` (differs from signup response)
- `password_hash` NEVER included in response (security)
- `token` is valid JWT signed with BETTER_AUTH_SECRET
- Token expires 7 days from login time
- Token payload includes `{"sub": user.id, "email": user.email, "exp": timestamp, "iat": timestamp}`

### Error Responses

#### 400 Bad Request
**When**: Malformed JSON or invalid request body structure

**Body**:
```json
{
  "error": "Request body is not valid JSON",
  "code": "BAD_REQUEST",
  "timestamp": "2025-12-24T04:30:00Z"
}
```

#### 401 Unauthorized - Invalid Credentials
**When**: User not found OR password mismatch (same error message for both)

**Body**:
```json
{
  "error": "Invalid credentials",
  "code": "UNAUTHORIZED",
  "timestamp": "2025-12-24T04:30:00Z"
}
```

**Security Note**: Same error message for "user not found" and "wrong password" prevents username enumeration attacks.

#### 422 Unprocessable Entity
**When**: Request body passes JSON parsing but fails validation rules

**Body** (example - invalid email):
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

**Body** (example - missing password):
```json
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

#### 500 Internal Server Error
**When**: Unexpected server error (database failure, password verification failure)

**Body**:
```json
{
  "error": "An unexpected error occurred. Please try again later.",
  "code": "INTERNAL_SERVER_ERROR",
  "timestamp": "2025-12-24T04:30:00Z"
}
```

**Note**: Detailed error logged on server, not exposed to client for security.

## Business Logic

### Execution Flow

1. **Request Validation** (Pydantic automatic)
   - Validate email format with EmailStr
   - Check password field exists (no length validation)
   - Return 422 if validation fails

2. **User Lookup** (Database)
   - Query database for user by email (case-insensitive using LOWER())
   - Return 401 "Invalid credentials" if user not found
   - **Important**: Generic error message prevents revealing if email exists

3. **Password Verification** (passlib bcrypt)
   - Verify password against stored password_hash using passlib
   - Verification takes ~200ms (bcrypt constant-time comparison)
   - Return 401 "Invalid credentials" if password mismatch
   - **Important**: Same error message as user not found (security)

4. **JWT Token Generation** (python-jose)
   - Create payload: {"sub": str(user.id), "email": user.email, "exp": now + 7 days, "iat": now}
   - Encode with BETTER_AUTH_SECRET and HS256 algorithm
   - Token generation takes ~5ms

5. **Response Construction**
   - Create UserResponse from User (excluding password_hash and created_at)
   - Create AuthResponse with UserResponse and token
   - Return 200 OK

### Database Operations

**Tables Queried**: `users`

**Query - Find User by Email**:
```sql
SELECT * FROM users WHERE LOWER(email) = LOWER($1) LIMIT 1;
```

**Note**: Uses functional index on LOWER(email) for performance

### Security Considerations

- **Timing Attack Prevention**: Use constant-time password comparison (passlib handles this)
- **Username Enumeration Prevention**: Same error message for "user not found" and "wrong password"
- **Email Case Handling**: Case-insensitive lookup allows users to login with any casing
- **Token Security**: JWT signed with BETTER_AUTH_SECRET. Token contains user_id and email but no sensitive data.
- **Response Security**: password_hash field NEVER included in any response.
- **No Rate Limiting**: Not implemented in Phase 2 (future security enhancement)

### Performance Expectations

- **Total Response Time**: < 300ms (95th percentile)
- **Breakdown**:
  - Validation: ~1ms
  - Email lookup: ~3ms (indexed query)
  - Password verification: ~200ms (bcrypt constant-time)
  - JWT generation: ~5ms
  - Response formatting: ~1ms

### Case-Insensitive Email Examples

User can login with any of these email variants (if registered as "john@example.com"):
- john@example.com
- JOHN@EXAMPLE.COM
- John@Example.com
- jOhN@eXaMpLe.CoM

All variants find the same user record.

## Testing Examples

### Test Case 1: Valid Login

**Setup**: Create user with email "test@example.com" and password "SecurePass123"

**Request**:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123"
  }'
```

**Expected Response**: 200 OK with user and token

### Test Case 2: Case-Insensitive Email

**Setup**: Create user with email "test@example.com"

**Request**:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "TEST@Example.COM",
    "password": "SecurePass123"
  }'
```

**Expected Response**: 200 OK with user and token (same user found)

### Test Case 3: Wrong Password

**Setup**: Create user with password "SecurePass123"

**Request**:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "WrongPassword"
  }'
```

**Expected Response**: 401 Unauthorized "Invalid credentials"

### Test Case 4: Nonexistent Email

**Request**:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "nonexistent@example.com",
    "password": "SecurePass123"
  }'
```

**Expected Response**: 401 Unauthorized "Invalid credentials" (same as wrong password)

### Test Case 5: Invalid Email Format

**Request**:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "notanemail",
    "password": "SecurePass123"
  }'
```

**Expected Response**: 422 Unprocessable Entity with email validation error

### Test Case 6: Missing Password

**Request**:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com"
  }'
```

**Expected Response**: 422 Unprocessable Entity with "field required" error

## JWT Token Usage

After successful login, the client should:

1. **Store Token Securely**
   - Option 1: httpOnly cookie (recommended for web apps)
   - Option 2: localStorage (easier but less secure)
   - Option 3: sessionStorage (clears on tab close)

2. **Include Token in API Requests**
   ```bash
   curl -X GET http://localhost:8000/api/users/{user_id}/tasks \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
   ```

3. **Handle Token Expiration**
   - Token expires 7 days after issuance
   - Backend returns 401 Unauthorized if token expired
   - Client should redirect to login page and clear stored token

4. **Token Verification**
   - Backend JWT middleware automatically verifies all tokens
   - No manual verification needed in route handlers
   - User context available in `request.state.user_id` and `request.state.email`

## Notes

- Login does NOT require minimum password length validation (only signup does)
- Email lookup is case-insensitive for better UX
- Password verification uses constant-time comparison to prevent timing attacks
- JWT tokens are stateless and cannot be revoked until expiration
- Token contains user_id in "sub" claim for identification
- Same error message for "user not found" and "wrong password" prevents enumeration
- created_at field NOT included in login response (differs from signup)
