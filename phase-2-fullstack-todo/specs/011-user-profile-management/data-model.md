# Data Model: User Profile Management

**Feature**: User Profile Management Endpoints
**Created**: 2025-12-25

---

## Overview

This feature uses the existing `User` model from the database foundation (CHUNK 1). No new database tables or models are required. The implementation focuses on secure retrieval and updates of existing User records.

---

## Entities

### User (Existing Model)

**Table**: `users`
**Purpose**: Store user account information including credentials and profile data

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique user identifier |
| `username` | VARCHAR(50) | UNIQUE, NOT NULL, INDEX | User's display name (3-50 chars) |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL, INDEX | User's email address |
| `password_hash` | VARCHAR(255) | NOT NULL | Bcrypt hashed password |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Account creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last profile update timestamp |

**Indexes**:
- PRIMARY KEY on `id` (automatic)
- UNIQUE INDEX on `username` (for duplicate detection)
- UNIQUE INDEX on `email` (for duplicate detection)

**Relationships**:
- ONE-TO-MANY with `Task` (user owns multiple tasks)

---

## Field Validation Rules

### Username

**Constraints**:
- Minimum length: 3 characters
- Maximum length: 50 characters
- Must be unique across all users
- Case-sensitive for uniqueness check
- Required for user creation, optional for updates

**Examples**:
- ✅ Valid: "john_doe", "user123", "alice-2025"
- ❌ Invalid: "ab" (too short), "a" * 51 (too long), "" (empty)

**Duplicate Check**:
```sql
SELECT id FROM users
WHERE username = :new_username
  AND id != :current_user_id
LIMIT 1
```

---

### Email

**Constraints**:
- Must be valid email format (RFC 5321)
- Must be unique across all users
- Case-insensitive for uniqueness check
- Required for user creation, optional for updates

**Examples**:
- ✅ Valid: "user@example.com", "john.doe+tag@mail.co.uk"
- ❌ Invalid: "notanemail", "missing@domain", "@example.com"

**Duplicate Check** (case-insensitive):
```sql
SELECT id FROM users
WHERE LOWER(email) = LOWER(:new_email)
  AND id != :current_user_id
LIMIT 1
```

---

### Password Hash

**Constraints**:
- Never exposed in any API response
- Bcrypt hashed with salt
- Modified only through separate password change endpoint (out of scope)

**Security**:
- Field excluded from `UserResponse` schema
- No read access via GET endpoint
- No write access via PUT endpoint

---

### Timestamps

**created_at**:
- Set automatically on user creation
- Immutable (never updated)
- Timezone: UTC

**updated_at**:
- Set automatically on user creation
- Updated on every profile modification
- Timezone: UTC
- Update trigger: Any change to username or email

---

## State Transitions

### User Profile States

**Active User**:
```
Initial State: User exists in database
    ↓
GET /users/{user_id}
    ↓
Return profile (read-only, no state change)
    ↓
Final State: User unchanged
```

**Profile Update**:
```
Initial State: User with username="john", email="john@old.com", updated_at=T1
    ↓
PUT /users/{user_id} {username: "john_new"}
    ↓
Validate: Check "john_new" not taken by other users
    ↓
Update: username="john_new", updated_at=T2
    ↓
Commit: Save to database
    ↓
Final State: User with username="john_new", email="john@old.com", updated_at=T2
```

**Update Rollback** (on duplicate):
```
Initial State: User with username="john", email="john@old.com"
    ↓
PUT /users/{user_id} {username: "existing_user"}
    ↓
Validate: "existing_user" already taken
    ↓
Rollback: No database changes
    ↓
Return 409 Conflict
    ↓
Final State: User unchanged (username="john", email="john@old.com")
```

---

## Data Access Patterns

### Read Operations

**Get Single User by ID**:
```sql
SELECT id, username, email, created_at, updated_at
FROM users
WHERE id = :user_id
```

**Performance**: O(1) lookup via primary key index
**Expected Latency**: <10ms

---

### Write Operations

**Update Username**:
```sql
-- Step 1: Check duplicate (excluding current user)
SELECT id FROM users
WHERE username = :new_username
  AND id != :user_id
LIMIT 1

-- Step 2: Update if no duplicate
UPDATE users
SET username = :new_username,
    updated_at = NOW()
WHERE id = :user_id
RETURNING id, username, email, created_at, updated_at
```

**Performance**: O(1) lookup via unique index, O(1) update via primary key
**Expected Latency**: <50ms

**Update Email**:
```sql
-- Step 1: Check duplicate (case-insensitive, excluding current user)
SELECT id FROM users
WHERE LOWER(email) = LOWER(:new_email)
  AND id != :user_id
LIMIT 1

-- Step 2: Update if no duplicate
UPDATE users
SET email = :new_email,
    updated_at = NOW()
WHERE id = :user_id
RETURNING id, username, email, created_at, updated_at
```

**Performance**: O(1) lookup via unique index, O(1) update via primary key
**Expected Latency**: <50ms

**Update Both Fields**:
```sql
-- Step 1: Check username duplicate
SELECT id FROM users WHERE username = :new_username AND id != :user_id LIMIT 1

-- Step 2: Check email duplicate
SELECT id FROM users WHERE LOWER(email) = LOWER(:new_email) AND id != :user_id LIMIT 1

-- Step 3: Update both if no duplicates
UPDATE users
SET username = :new_username,
    email = :new_email,
    updated_at = NOW()
WHERE id = :user_id
RETURNING id, username, email, created_at, updated_at
```

**Performance**: 2 index lookups + 1 update = O(1) overall
**Expected Latency**: <100ms

---

## Concurrency Considerations

### Race Conditions

**Scenario**: Two users attempt to update username to "john_doe" simultaneously

**Protection**:
1. Database unique constraint prevents duplicate usernames
2. Explicit check provides better error message (409 vs generic DB error)
3. Transaction isolation ensures consistency

**Resolution**:
- First request succeeds (username updated)
- Second request fails (409 Conflict returned)
- No data corruption

**Implementation**:
```python
# Transaction with rollback on error
try:
    # Check duplicate
    if duplicate_exists:
        raise HTTPException(status_code=409)

    # Update user
    user.username = new_username
    session.commit()  # Atomic commit
except IntegrityError:
    session.rollback()  # Explicit rollback
    raise HTTPException(status_code=409)
```

---

### Concurrent Updates by Same User

**Scenario**: User submits two update requests simultaneously

**Behavior**:
- Both requests validated independently
- Both attempt to update same record
- Last write wins (database-level locking)
- `updated_at` reflects last successful update

**Not a Problem**:
- Updates are atomic (single user can't create inconsistent state)
- No data loss (both updates succeed, last one persists)
- Frontend should prevent this (disable button during request)

---

## Data Validation Layers

### Layer 1: Pydantic Schema Validation

**Location**: `schemas/user.py` - `UpdateUserRequest`

**Validations**:
- Username length (3-50 characters) via `Field(min_length=3, max_length=50)`
- Email format via `EmailStr` type
- At least one field provided (custom validation in service layer)

**When**: Request parsing (before service layer)

---

### Layer 2: Service Layer Validation

**Location**: `services/user_service.py` - `update_user_profile()`

**Validations**:
- At least one field provided (raises 422 if both None)
- Username not taken by another user (raises 409)
- Email not taken by another user (raises 409)

**When**: Business logic execution (after schema validation)

---

### Layer 3: Database Constraints

**Location**: Database table definition

**Validations**:
- Username UNIQUE constraint
- Email UNIQUE constraint
- NOT NULL constraints on required fields

**When**: Database commit (final safety net)

---

## Security Considerations

### Password Hash Exclusion

**Risk**: Exposing password_hash allows offline brute force attacks

**Mitigation**:
- Never query password_hash in SELECT statements for profile endpoints
- Use Pydantic `UserResponse` schema without password_hash field
- `response_model=UserResponse` on FastAPI routes enforces exclusion
- Test coverage: 100% verification that password_hash never in response

**Implementation**:
```python
# Schema excludes password_hash
class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    created_at: datetime
    updated_at: datetime
    # password_hash: NOT INCLUDED

# Route uses response_model for automatic exclusion
@router.get("/{user_id}", response_model=UserResponse)
async def get_user(...):
    user = session.get(User, user_id)  # Includes all fields
    return user  # Pydantic excludes password_hash automatically
```

---

### User Isolation

**Risk**: User A accessing or modifying User B's profile

**Mitigation**:
- JWT token verification extracts authenticated user_id
- Route layer validates path `user_id` matches JWT `user_id`
- Service layer operates on verified user_id only
- 403 Forbidden returned on mismatch

**Flow**:
```
Request: PUT /users/123 (JWT contains user_id=456)
    ↓
Middleware: Extract user_id=456 from JWT
    ↓
Route: Compare path user_id (123) != JWT user_id (456)
    ↓
Return: 403 Forbidden (block access before service layer)
```

---

### Duplicate Detection

**Risk**: Username/email enumeration through duplicate checks

**Mitigation**:
- Both authenticated users attempting same username get 409
- Non-authenticated users get 401 (no information leaked)
- Cross-user access attempts get 403 (no information leaked)
- Only user updating own profile gets duplicate feedback

**Not a Problem**:
- Usernames/emails are non-sensitive (used for login)
- Enumeration requires authentication (rate-limited)
- Better UX: Immediate feedback vs generic "update failed"

---

## Performance Optimization

### Database Indexes

**Current Indexes** (already exist):
- PRIMARY KEY (`id`) - Clustered index
- UNIQUE INDEX (`username`) - For duplicate checks and lookups
- UNIQUE INDEX (`email`) - For duplicate checks and lookups

**Query Performance**:
- `SELECT ... WHERE id = ?` → O(1) via primary key
- `SELECT ... WHERE username = ?` → O(1) via unique index
- `SELECT ... WHERE LOWER(email) = ?` → O(1) via unique index (case-insensitive)

**No Additional Indexes Needed**

---

### Connection Pooling

**Already Configured** in `backend/db.py`:
- Pool size: 10 connections
- Max overflow: 20 connections
- Recycle timeout: 3600 seconds

**Profile Endpoint Load**:
- GET: 1 database query per request
- PUT: 2-3 database queries per request (duplicate checks + update)
- Concurrent capacity: ~500 users with current pool

---

## Data Migration

**Not Required**: User model already exists from CHUNK 1 (Database Foundation)

**Verification Checklist**:
- [ ] User table exists in database
- [ ] `username` field has UNIQUE constraint
- [ ] `email` field has UNIQUE constraint
- [ ] Indexes exist on `username` and `email`
- [ ] `updated_at` has default value (NOW())

---

## Monitoring & Observability

### Metrics to Track

**Query Performance**:
- `user_profile_get_latency_ms` (p50, p95, p99)
- `user_profile_update_latency_ms` (p50, p95, p99)
- `user_duplicate_check_latency_ms`

**Error Rates**:
- `user_profile_409_errors_total` (duplicate attempts)
- `user_profile_403_errors_total` (unauthorized access)
- `user_profile_422_errors_total` (validation errors)

**Business Metrics**:
- `username_updates_total`
- `email_updates_total`
- `profile_views_total`

### Alerts

**Critical**:
- GET latency p95 > 1 second
- PUT latency p95 > 2 seconds
- Error rate > 10% (excluding 409/422 user errors)

**Warning**:
- Duplicate attempt rate > 20% (possible enumeration attack)
- 403 error rate > 5% (possible attack on other profiles)
