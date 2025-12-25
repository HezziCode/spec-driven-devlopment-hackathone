# Contract: User Model

**Module**: `backend.models`
**Class**: `User`
**Type**: SQLModel (table=True)
**Purpose**: Represents a user account with authentication credentials

## Public Interface

### Import

```python
from backend.models import User
```

### Class Definition

```python
class User(SQLModel, table=True):
    """
    User account model with authentication credentials.

    Attributes:
        id: Unique UUID identifier (auto-generated)
        username: Unique username (3-50 characters)
        email: Unique email address (valid format)
        password_hash: Bcrypt hashed password (never plain text)
        created_at: Account creation timestamp (UTC)
        updated_at: Last modification timestamp (UTC)
        tasks: One-to-many relationship to Task model
    """
```

### Fields

| Field | Type | Nullable | Default | Constraints |
|-------|------|----------|---------|-------------|
| id | UUID | No | uuid4() | PRIMARY KEY |
| username | str | No | - | UNIQUE, MAX_LENGTH=50 |
| email | str | No | - | UNIQUE, MAX_LENGTH=100 |
| password_hash | str | No | - | MAX_LENGTH=255 |
| created_at | datetime | No | UTC now | - |
| updated_at | datetime | No | UTC now | - |

### Relationships

| Relationship | Type | Target Model | Access Pattern |
|--------------|------|--------------|----------------|
| tasks | List[Task] | Task | `user.tasks` returns all tasks for this user |

### Usage Examples

**Create User Instance**:
```python
from backend.models import User
from datetime import datetime

user = User(
    username="johndoe",
    email="john@example.com",
    password_hash="$2b$12$hashed_password_here",
    created_at=datetime.utcnow(),
    updated_at=datetime.utcnow()
)
```

**Access User's Tasks**:
```python
# Assuming user is loaded from database
for task in user.tasks:
    print(task.title)
```

**Query User by Email**:
```python
from sqlmodel import Session, select

user = session.exec(
    select(User).where(User.email == "john@example.com")
).first()
```

## Constraints

### Database Level

- **UNIQUE constraint** on `username` (enforced by unique index)
- **UNIQUE constraint** on `email` (enforced by unique index)
- **NOT NULL constraints** on all fields
- **Primary Key constraint** on `id`

### Application Level (recommended)

- Username validation: 3-50 characters, alphanumeric + underscore/hyphen
- Email validation: Valid email format (use pydantic EmailStr)
- Password validation before hashing: Minimum 8 characters, complexity requirements

## Type Hints

All fields have complete type hints:

```python
id: UUID
username: str
email: str
password_hash: str
created_at: datetime
updated_at: datetime
tasks: List["Task"]  # Forward reference resolved at runtime
```

**Mypy Compliance**: Passes strict mode with zero errors

## Security Considerations

- **password_hash** stores bcrypt output, NEVER plain text password
- Never expose password_hash in API responses
- Use `exclude={"password_hash"}` when serializing to JSON
- Email should be treated as case-insensitive for lookups (lowercase before storage)

## Table Name

**Database Table**: `users`

## Indexes

- **idx_users_pkey** (PRIMARY KEY) on `id`
- **idx_users_email** (UNIQUE) on `email`
- **idx_users_username** (UNIQUE) on `username`

## Migration

Table created by: `migrations/create_tables.py`

SQL equivalent:
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE UNIQUE INDEX idx_users_username ON users(username);
```

## Testing

Verify User model contract:

```python
# Test 1: Model importable
from backend.models import User

# Test 2: All fields accessible
user = User(username="test", email="test@example.com", password_hash="hash")
assert user.username == "test"
assert user.email == "test@example.com"

# Test 3: Type hints correct
from typing import get_type_hints
hints = get_type_hints(User)
assert hints["id"] == UUID
assert hints["username"] == str
assert hints["tasks"] == List[Task]
```
