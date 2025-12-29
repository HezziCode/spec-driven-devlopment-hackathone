# API Contract: PUT /users/{user_id}

**Endpoint**: Update User Profile
**Method**: PUT
**Path**: `/users/{user_id}`
**Purpose**: Update authenticated user's username and/or email

---

## Request

### Path Parameters
- `user_id` (UUID, required): Must match authenticated user

### Headers
- `Authorization: Bearer {jwt_token}` (required)
- `Content-Type: application/json`

### Body (at least one field required)
```json
{
  "username": "new_username",  // Optional: 3-50 characters
  "email": "new@example.com"   // Optional: valid email format
}
```

---

## Response

### 200 OK - Success
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "username": "new_username",
  "email": "new@example.com",
  "created_at": "2025-12-25T10:00:00Z",
  "updated_at": "2025-12-25T16:45:00Z"
}
```

### 409 Conflict - Duplicate Username/Email
```json
{
  "error": "Username 'new_username' is already taken",
  "code": "DUPLICATE_USERNAME",
  "timestamp": "2025-12-25T10:00:00Z"
}
```

### 422 Unprocessable Entity - Validation Errors
```json
{
  "error": "At least one field (username or email) must be provided",
  "code": "VALIDATION_ERROR",
  "timestamp": "2025-12-25T10:00:00Z"
}
```

### Other Errors
- 401: Missing/invalid JWT token
- 403: Cross-user access attempt
- 404: User not found

---

## Validation Rules

**Username**:
- Length: 3-50 characters
- Uniqueness: Case-sensitive, must not be taken by another user
- Current user can update to same value (idempotent)

**Email**:
- Format: Valid email per RFC 5321
- Uniqueness: Case-insensitive, must not be taken by another user
- Current user can update to same value (idempotent)

**Request**:
- At least one field (username or email) must be provided
- Both fields can be updated simultaneously

---

## Security

- Password hash never exposed in response
- User isolation enforced (403 for cross-user access)
- Duplicate checking excludes current user
- Atomic database transactions

---

## Performance

- Target latency: <2s (95th percentile)
- Database queries: 2-3 per request (duplicate checks + update)
- Indexed lookups for duplicate detection

---

## Examples

**Update username only**:
```http
PUT /users/3fa85f64-5717-4562-b3fc-2c963f66afa6
Authorization: Bearer {token}

{"username": "john_new"}
```

**Update email only**:
```http
PUT /users/3fa85f64-5717-4562-b3fc-2c963f66afa6
Authorization: Bearer {token}

{"email": "john.new@example.com"}
```

**Update both**:
```http
PUT /users/3fa85f64-5717-4562-b3fc-2c963f66afa6
Authorization: Bearer {token}

{"username": "john_new", "email": "john.new@example.com"}
```
