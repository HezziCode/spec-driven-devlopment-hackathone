# API Contract: POST /auth/signup

**Endpoint**: `POST /auth/signup`
**Purpose**: Create a new user account with username, email, and password
**Authentication**: None required (public endpoint)

## Request

### Method
```
POST
```

### Path
```
/auth/signup
```

### Headers
```
Content-Type: application/json
```

### Body Schema
```json
{
  "username": "string (3-50 characters, required)",
  "email": "string (valid email format, required)",
  "password": "string (minimum 8 characters, required)"
}
```

### Body Example
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

### Validation Rules

| Field | Type | Constraints | Error Message |
|-------|------|-------------|---------------|
| username | string | 3-50 characters, required | "Username must be between 3 and 50 characters" |
| email | string | Valid email format (RFC 5322), required | "Invalid email format" |
| password | string | Minimum 8 characters, required | "Password must be at least 8 characters" |

## Response

### Success Response (201 Created)

**Status Code**: `201 Created`

**Body Schema**:
```json
{
  "user": {
    "id": "UUID (string format)",
    "username": "string",
    "email": "string (lowercase)",
    "created_at": "string (ISO 8601 datetime)"
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
    "email": "john@example.com",
    "created_at": "2025-12-24T04:30:00Z"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjNlNDU2Ny1lODliLTEyZDMtYTQ1Ni00MjY2MTQxNzQwMDAiLCJlbWFpbCI6ImpvaG5AZXhhbXBsZS5jb20iLCJleHAiOjE3MzU2ODQ4MDAsImlhdCI6MTczNTA4MDAwMH0.signature"
}
```

**Response Guarantees**:
- `user.email` always returned in lowercase (normalized)
- `password_hash` NEVER included in response (security)
- `token` is valid JWT signed with BETTER_AUTH_SECRET
- Token expires 7 days from `created_at`
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

#### 409 Conflict - Duplicate Username
**When**: Username already exists in database (case-sensitive match)

**Body**:
```json
{
  "error": "Username already exists",
  "code": "CONFLICT",
  "timestamp": "2025-12-24T04:30:00Z"
}
```

#### 409 Conflict - Duplicate Email
**When**: Email already exists in database (case-insensitive match)

**Body**:
```json
{
  "error": "Email already registered",
  "code": "CONFLICT",
  "timestamp": "2025-12-24T04:30:00Z"
}
```

**Note**: If both username AND email are duplicates, only the first duplicate encountered is reported (username checked first).

#### 422 Unprocessable Entity
**When**: Request body passes JSON parsing but fails validation rules

**Body** (example - short username):
```json
{
  "detail": [
    {
      "loc": ["body", "username"],
      "msg": "ensure this value has at least 3 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

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

**Body** (example - short password):
```json
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "ensure this value has at least 8 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

#### 500 Internal Server Error
**When**: Unexpected server error (database failure, hashing failure, JWT generation failure)

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
   - Check username length 3-50 characters
   - Validate email format with EmailStr
   - Check password minimum 8 characters
   - Return 422 if validation fails

2. **Duplicate Checking** (Application layer)
   - Query database for existing username (case-sensitive)
   - Return 409 "Username already exists" if found
   - Query database for existing email (case-insensitive using LOWER())
   - Return 409 "Email already registered" if found

3. **Password Hashing** (passlib bcrypt)
   - Hash password with bcrypt scheme, 12 rounds
   - Hashing takes ~200ms
   - Result format: "$2b$12$[salt][hash]"

4. **User Creation** (Database)
   - Create User record with id (auto-generated UUID), username, email (lowercase), password_hash, created_at, updated_at
   - Insert into database
   - Return 500 if database failure
   - Catch IntegrityError if race condition on unique constraint

5. **JWT Token Generation** (python-jose)
   - Create payload: {"sub": str(user.id), "email": user.email, "exp": now + 7 days, "iat": now}
   - Encode with BETTER_AUTH_SECRET and HS256 algorithm
   - Token generation takes ~5ms

6. **Response Construction**
   - Create UserResponse from User (excluding password_hash)
   - Create AuthResponse with UserResponse and token
   - Return 201 Created

### Database Operations

**Tables Modified**: `users`

**Query 1 - Check Username**:
```sql
SELECT * FROM users WHERE username = $1 LIMIT 1;
```

**Query 2 - Check Email**:
```sql
SELECT * FROM users WHERE LOWER(email) = LOWER($1) LIMIT 1;
```

**Query 3 - Insert User**:
```sql
INSERT INTO users (id, username, email, password_hash, created_at, updated_at)
VALUES ($1, $2, $3, $4, $5, $6)
RETURNING *;
```

### Security Considerations

- **Password Security**: Password hashed with bcrypt 12 rounds before storage. Plaintext password NEVER stored.
- **Email Normalization**: Email stored as lowercase to prevent duplicate accounts with different casing.
- **Token Security**: JWT signed with BETTER_AUTH_SECRET. Token contains user_id and email but no sensitive data.
- **Response Security**: password_hash field NEVER included in any response.
- **Error Messages**: Generic error messages prevent information leakage (e.g., don't reveal if username vs email is duplicate).

### Performance Expectations

- **Total Response Time**: < 500ms (95th percentile)
- **Breakdown**:
  - Validation: ~1ms
  - Username check: ~2ms
  - Email check: ~3ms
  - Password hashing: ~200ms (bcrypt 12 rounds)
  - User creation: ~10ms
  - JWT generation: ~5ms
  - Response formatting: ~1ms

## Testing Examples

### Test Case 1: Valid Signup

**Request**:
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123"
  }'
```

**Expected Response**: 201 Created with user and token

### Test Case 2: Duplicate Username

**Setup**: Create user with username "testuser"

**Request**:
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "different@example.com",
    "password": "SecurePass123"
  }'
```

**Expected Response**: 409 Conflict "Username already exists"

### Test Case 3: Duplicate Email (Case-Insensitive)

**Setup**: Create user with email "test@example.com"

**Request**:
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "differentuser",
    "email": "TEST@Example.COM",
    "password": "SecurePass123"
  }'
```

**Expected Response**: 409 Conflict "Email already registered"

### Test Case 4: Invalid Email Format

**Request**:
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "notanemail",
    "password": "SecurePass123"
  }'
```

**Expected Response**: 422 Unprocessable Entity with email validation error

### Test Case 5: Short Password

**Request**:
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Short1"
  }'
```

**Expected Response**: 422 Unprocessable Entity with password length error

## Notes

- Email addresses are case-insensitive for uniqueness (per RFC 5321)
- Usernames are case-sensitive (allows "JohnDoe" and "johndoe" as different users if desired)
- JWT tokens are stateless and cannot be revoked until expiration
- Frontend should store token securely (e.g., httpOnly cookie or secure localStorage)
- Token should be included in Authorization header for protected endpoints: `Authorization: Bearer <token>`
