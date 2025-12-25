# Data Model: Database Foundation

**Feature**: 005-database-foundation
**Date**: 2025-12-23
**Status**: Design Complete

## Entity Relationship Diagram

```
┌─────────────────────────────────┐
│           User                   │
├─────────────────────────────────┤
│ id: UUID (PK)                    │
│ username: VARCHAR(50) UNIQUE     │
│ email: VARCHAR(100) UNIQUE       │
│ password_hash: VARCHAR(255)      │
│ created_at: TIMESTAMP            │
│ updated_at: TIMESTAMP            │
└─────────────────┬───────────────┘
                  │
                  │ 1:N (one user has many tasks)
                  │
                  ▼
┌─────────────────────────────────┐
│           Task                   │
├─────────────────────────────────┤
│ id: UUID (PK)                    │
│ user_id: UUID (FK → User.id)     │
│ title: VARCHAR(200)              │
│ description: TEXT                │
│ completed: BOOLEAN               │
│ priority: VARCHAR(20)            │
│ created_at: TIMESTAMP            │
│ updated_at: TIMESTAMP            │
└─────────────────┬───────────────┘
                  │
                  │ N:M (task has many tags via junction)
                  │
                  ▼
┌─────────────────────────────────┐
│         TaskTag                  │
│       (Junction Table)           │
├─────────────────────────────────┤
│ id: UUID (PK)                    │
│ task_id: UUID (FK → Task.id)     │
│ tag_name: VARCHAR(50)            │
│ created_at: TIMESTAMP            │
│ UNIQUE(task_id, tag_name)        │
└─────────────────────────────────┘
```

## Entity Definitions

### User Entity

**Purpose**: Represents a user account in the system with authentication credentials and audit timestamps.

**Fields**:

| Field Name | Type | Constraints | Default | Description |
|------------|------|-------------|---------|-------------|
| id | UUID | PRIMARY KEY, NOT NULL | uuid4() | Unique identifier for the user |
| username | VARCHAR(50) | UNIQUE, NOT NULL, INDEX | - | User's chosen username (3-50 chars) |
| email | VARCHAR(100) | UNIQUE, NOT NULL, INDEX | - | User's email address (valid format) |
| password_hash | VARCHAR(255) | NOT NULL | - | Bcrypt hashed password (never plain text) |
| created_at | TIMESTAMP | NOT NULL | NOW() | Account creation timestamp (UTC) |
| updated_at | TIMESTAMP | NOT NULL | NOW() | Last update timestamp (UTC) |

**Relationships**:
- **tasks**: One-to-many relationship with Task entity. One user can have many tasks. Accessible via `user.tasks` returning `List[Task]`.

**Indexes**:
- Primary key index on `id` (automatic)
- Unique index on `username` for fast username lookups and uniqueness enforcement
- Unique index on `email` for fast email lookups and uniqueness enforcement

**Constraints**:
- Username must be 3-50 characters (enforced at application level)
- Email must be valid format (enforced at application level)
- Password must meet complexity requirements (enforced at application level before hashing)

**Notes**:
- password_hash stores bcrypt hash output, never plain text password
- Timestamps use UTC for consistency across time zones
- UUID primary key enables distributed system architecture

---

### Task Entity

**Purpose**: Represents a todo item belonging to a user with descriptive information, completion status, priority level, and audit timestamps.

**Fields**:

| Field Name | Type | Constraints | Default | Description |
|------------|------|-------------|---------|-------------|
| id | UUID | PRIMARY KEY, NOT NULL | uuid4() | Unique identifier for the task |
| user_id | UUID | FOREIGN KEY (users.id), NOT NULL, INDEX | - | Reference to owning user |
| title | VARCHAR(200) | NOT NULL | - | Task title (1-200 chars) |
| description | TEXT | NULLABLE | NULL | Detailed task description (optional) |
| completed | BOOLEAN | NOT NULL, INDEX | FALSE | Task completion status |
| priority | VARCHAR(20) | NOT NULL, INDEX, CHECK IN ('low','medium','high','critical') | 'medium' | Task priority level |
| created_at | TIMESTAMP | NOT NULL | NOW() | Task creation timestamp (UTC) |
| updated_at | TIMESTAMP | NOT NULL | NOW() | Last update timestamp (UTC) |

**Relationships**:
- **user**: Many-to-one relationship with User entity. Each task belongs to exactly one user. Accessible via `task.user` returning `User`.
- **tags**: One-to-many relationship with TaskTag entity. One task can have many tags. Accessible via `task.tags` returning `List[TaskTag]`.

**Indexes**:
- Primary key index on `id` (automatic)
- Index on `user_id` for efficient user-based queries (find all tasks for a user)
- Index on `completed` for filtering completed/pending tasks
- Index on `priority` for priority-based filtering and sorting
- **Composite index on (user_id, completed)** for optimized queries filtering user's completed or pending tasks (common query pattern)

**Constraints**:
- Foreign key constraint from `user_id` to `users.id` ensures every task belongs to a valid user
- Title must be 1-200 characters (enforced at application level)
- Description maximum 1000 characters (enforced at application level)
- Priority must be one of: 'low', 'medium', 'high', 'critical' (CHECK constraint)

**Notes**:
- completed defaults to False for new tasks
- priority defaults to 'medium' if not specified
- Composite index on (user_id, completed) optimizes the common query "get my pending tasks"

---

### TaskTag Entity

**Purpose**: Junction table representing the many-to-many association between tasks and tag names, allowing multiple tags per task with prevention of duplicate tags.

**Fields**:

| Field Name | Type | Constraints | Default | Description |
|------------|------|-------------|---------|-------------|
| id | UUID | PRIMARY KEY, NOT NULL | uuid4() | Unique identifier for the tag association |
| task_id | UUID | FOREIGN KEY (tasks.id), NOT NULL, INDEX | - | Reference to the tagged task |
| tag_name | VARCHAR(50) | NOT NULL, INDEX | - | Name of the tag (1-50 chars) |
| created_at | TIMESTAMP | NOT NULL | NOW() | Tag association timestamp (UTC) |

**Relationships**:
- **task**: Many-to-one relationship with Task entity. Each tag association belongs to exactly one task. Accessible via `tasktag.task` returning `Task`.

**Indexes**:
- Primary key index on `id` (automatic)
- Index on `task_id` for efficient task-based queries (find all tags for a task)
- Index on `tag_name` for efficient tag-based queries (find all tasks with a specific tag)

**Constraints**:
- Foreign key constraint from `task_id` to `tasks.id` with CASCADE DELETE (when task deleted, its tags are automatically removed)
- **UNIQUE constraint on (task_id, tag_name)** prevents duplicate tags on the same task
- Tag name must be 1-50 characters (enforced at application level)

**Notes**:
- Unique constraint on (task_id, tag_name) enforces business rule at database level
- Cascade delete ensures no orphaned tags when tasks are deleted
- created_at provides audit trail for when tags were added

---

## Relationships Summary

### User ↔ Task (One-to-Many)

**Type**: One-to-Many
**Direction**: User (one) → Task (many)
**Foreign Key**: `tasks.user_id` → `users.id`
**Cascade**: No cascade on user deletion (tasks remain but become orphaned - handled at application level)
**Access Pattern**:
- From User: `user.tasks` returns `List[Task]`
- From Task: `task.user` returns `User`

**Query Examples**:
- Get all tasks for a user: `session.exec(select(Task).where(Task.user_id == user.id)).all()`
- Get task owner: `task.user` (lazy loaded)

---

### Task ↔ Tags (Many-to-Many via TaskTag)

**Type**: Many-to-Many
**Junction Table**: TaskTag
**Direction**: Task (many) ↔ Tags (many) via TaskTag
**Foreign Keys**:
- `task_tags.task_id` → `tasks.id` (CASCADE DELETE)
- Tag names are strings, not separate entity
**Access Pattern**:
- From Task: `task.tags` returns `List[TaskTag]`
- Tag names extracted: `[tag.tag_name for tag in task.tags]`

**Query Examples**:
- Get all tags for a task: `session.exec(select(TaskTag).where(TaskTag.task_id == task.id)).all()`
- Get all tasks with a specific tag: `session.exec(select(Task).join(TaskTag).where(TaskTag.tag_name == "work")).all()`

---

## Field Validation Rules

### User Model Validation

- **username**:
  - Minimum length: 3 characters
  - Maximum length: 50 characters
  - Unique across all users
  - Allowed characters: alphanumeric, underscore, hyphen

- **email**:
  - Valid email format (user@domain.tld)
  - Maximum length: 100 characters
  - Unique across all users
  - Case-insensitive uniqueness

- **password_hash**:
  - Stores bcrypt hash output (60 characters typically)
  - Maximum length: 255 characters for future algorithm flexibility
  - Never exposed in API responses

### Task Model Validation

- **title**:
  - Minimum length: 1 character (not empty)
  - Maximum length: 200 characters
  - Required field (cannot be null)

- **description**:
  - Optional field (can be null)
  - Maximum length: 1000 characters when provided
  - Empty string treated as null

- **priority**:
  - Must be one of: 'low', 'medium', 'high', 'critical'
  - Case-sensitive
  - Default: 'medium'
  - Enforced by CHECK constraint at database level

### TaskTag Model Validation

- **tag_name**:
  - Minimum length: 1 character (not empty)
  - Maximum length: 50 characters
  - Case-sensitive
  - No duplicates per task (enforced by unique constraint)

---

## Database Indexes Strategy

### Purpose of Each Index

| Table | Index | Columns | Type | Purpose |
|-------|-------|---------|------|---------|
| users | idx_users_email | email | UNIQUE | Fast email lookup during login, enforce uniqueness |
| users | idx_users_username | username | UNIQUE | Fast username lookup, enforce uniqueness, support username search |
| tasks | idx_tasks_user_id | user_id | BTREE | Efficient filtering of tasks by user (primary query pattern) |
| tasks | idx_tasks_completed | completed | BTREE | Fast filtering of completed vs pending tasks |
| tasks | idx_tasks_priority | priority | BTREE | Efficient sorting and filtering by priority level |
| tasks | idx_user_completed | (user_id, completed) | COMPOSITE | Optimized query for user's pending/completed tasks (very common pattern) |
| task_tags | idx_tasktag_task_id | task_id | BTREE | Fast lookup of all tags for a task |
| task_tags | idx_tasktag_tag_name | tag_name | BTREE | Fast lookup of all tasks with a specific tag |

### Index Selectivity Analysis

**High Selectivity** (efficient):
- users.email (unique, most selective)
- users.username (unique, most selective)
- task_tags(task_id, tag_name) (unique combination)

**Medium Selectivity** (useful):
- tasks.user_id (divides data by user count)
- tasks.priority (4 distinct values, but frequently filtered)

**Low Selectivity** (still beneficial):
- tasks.completed (only 2 values: true/false, but very frequently filtered)

**Composite Index Benefit**:
- (user_id, completed) covers both individual queries AND combined queries
- Eliminates need for separate completed index when user_id is also filtered
- PostgreSQL can use this for "user's pending tasks" without separate index scans

---

## Migration Strategy

### Initial Schema Creation

**Script**: `backend/migrations/create_tables.py`

**Execution**:
```bash
cd backend
python migrations/create_tables.py
```

**Behavior**:
1. Load DATABASE_URL from environment (.env file)
2. Create SQLAlchemy engine with connection pooling
3. Import all SQLModel models (User, Task, TaskTag)
4. Call `SQLModel.metadata.create_all(engine, checkfirst=True)`
5. Verify table creation by querying database metadata
6. Print success/failure status with details

**Idempotency**:
- `checkfirst=True` ensures tables are only created if they don't exist
- Safe to run multiple times without errors
- Useful for deployment automation and disaster recovery

**Verification**:
After migration, verify schema with SQL queries:
```sql
-- Check tables exist
SELECT table_name FROM information_schema.tables
WHERE table_schema='public';

-- Check indexes
SELECT indexname, indexdef FROM pg_indexes
WHERE tablename IN ('users', 'tasks', 'task_tags');

-- Check foreign keys
SELECT conname, conrelid::regclass, confrelid::regclass
FROM pg_constraint WHERE contype = 'f';
```

### Future Migration Strategy

For future schema changes (Phase 3+):
- Consider Alembic for versioned migrations
- Create migration files for each schema change
- Maintain forward and backward migration scripts
- Test migrations on staging database before production

---

## Performance Considerations

### Query Optimization

**Common Query Patterns** (optimized by indexes):

1. **Get user by email** (login scenario):
   ```sql
   SELECT * FROM users WHERE email = 'user@example.com';
   ```
   - Uses unique index on email → O(log n) lookup
   - Expected: < 5ms

2. **Get all tasks for a user** (dashboard):
   ```sql
   SELECT * FROM tasks WHERE user_id = '...';
   ```
   - Uses index on user_id → O(log n + k) where k = result count
   - Expected: < 50ms for 100 tasks

3. **Get user's pending tasks** (most common query):
   ```sql
   SELECT * FROM tasks WHERE user_id = '...' AND completed = false;
   ```
   - Uses composite index (user_id, completed) → O(log n + k)
   - Expected: < 30ms for 50 pending tasks

4. **Get all tasks with tag "work"** (tag filtering):
   ```sql
   SELECT t.* FROM tasks t
   JOIN task_tags tt ON t.id = tt.task_id
   WHERE tt.tag_name = 'work';
   ```
   - Uses index on tag_name → O(log n + k)
   - Expected: < 100ms for 50 matching tasks

5. **Add tag to task** (task update):
   ```sql
   INSERT INTO task_tags (id, task_id, tag_name, created_at)
   VALUES (...);
   ```
   - Checks unique constraint on (task_id, tag_name) → O(log n)
   - Expected: < 10ms

### Index Maintenance

- Indexes updated automatically on INSERT/UPDATE/DELETE
- Slight write performance penalty (~10-20%) for indexed columns
- Read performance gain (~10-100x) far outweighs write cost
- For Phase II scale (< 10k tasks per user), current indexes are sufficient

### Connection Pool Configuration

**Recommended Settings**:
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=5,          # Maintain 5 persistent connections
    max_overflow=10,      # Allow up to 10 additional connections under load
    pool_timeout=30,      # Wait 30 seconds for available connection
    pool_recycle=3600     # Recycle connections every hour
)
```

**Justification**:
- pool_size=5: Handles 5 concurrent requests efficiently
- max_overflow=10: Burst capacity for peak load (total 15 connections)
- pool_timeout=30: Prevents indefinite waiting with clear timeout error
- pool_recycle=3600: Prevents stale connections from database timeouts

---

## Data Integrity Constraints

### Foreign Key Constraints

**tasks.user_id → users.id**:
- **Purpose**: Ensures every task belongs to a valid user
- **Cascade Behavior**: No cascade (default) - deleting user does not cascade to tasks
- **Rationale**: Business decision to preserve task data even if user deleted (can be orphaned)
- **Enforcement**: Database level - invalid user_id rejected with error

**task_tags.task_id → tasks.id**:
- **Purpose**: Ensures every tag association references a valid task
- **Cascade Behavior**: CASCADE DELETE - deleting task automatically removes its tags
- **Rationale**: Tags without tasks are meaningless, automatic cleanup prevents orphaned data
- **Enforcement**: Database level - invalid task_id rejected with error

### Unique Constraints

**users.email (UNIQUE)**:
- **Purpose**: Prevents duplicate email addresses (used for login)
- **Enforcement**: Database level with unique index
- **Error Handling**: Application catches unique violation, returns 409 Conflict to API

**users.username (UNIQUE)**:
- **Purpose**: Prevents duplicate usernames (user-facing identifier)
- **Enforcement**: Database level with unique index
- **Error Handling**: Application catches unique violation, returns 409 Conflict to API

**task_tags(task_id, tag_name) UNIQUE**:
- **Purpose**: Prevents duplicate tags on the same task
- **Enforcement**: Database level with unique constraint
- **Error Handling**: Application can safely attempt insert, database prevents duplicates

### NOT NULL Constraints

All fields except nullable ones enforce NOT NULL at database level:
- User: All fields NOT NULL
- Task: All fields NOT NULL except `description` (nullable)
- TaskTag: All fields NOT NULL

**Rationale**: Prevents incomplete data, ensures data quality, simplifies query logic (no null checks needed)

### CHECK Constraints

**tasks.priority CHECK**:
- **Constraint**: `priority IN ('low', 'medium', 'high', 'critical')`
- **Purpose**: Ensures priority values are from defined enumeration
- **Enforcement**: Database level - invalid priority values rejected
- **Error Handling**: Application validation should prevent this, but database provides safety net

---

## Type Safety Requirements

### SQLModel Field Type Hints

All model fields must have explicit type hints from Python's typing system:

**Primitive Types**:
- `str` - for VARCHAR and TEXT columns
- `bool` - for BOOLEAN columns
- `UUID` - for UUID columns (from uuid module)
- `datetime` - for TIMESTAMP columns (from datetime module)

**Optional Types**:
- `Optional[str]` or `str | None` - for nullable columns like Task.description

**Collection Types**:
- `List["Task"]` - for one-to-many relationships like User.tasks
- `List["TaskTag"]` - for one-to-many relationships like Task.tags

**Forbidden Types**:
- `Any` - NEVER allowed (violates constitution)
- `object` - Not specific enough
- Untyped fields - All fields must have type hint

### Mypy Strict Mode Compliance

**Configuration** (mypy.ini):
```ini
[mypy]
python_version = 3.11
strict = True
disallow_untyped_defs = True
disallow_any_explicit = True
warn_return_any = True
no_implicit_optional = True
```

**Expected Result**: Zero mypy errors when running `mypy backend/models.py backend/db.py`

---

## Testing Requirements

### Test Coverage Targets

| Module | Target Coverage | Critical Paths |
|--------|----------------|----------------|
| models.py | 100% | Model instantiation, field access, relationships |
| db.py | 100% | Connection creation, session generation, error handling |
| migrations/create_tables.py | 100% | Table creation, idempotency |
| scripts/test_connection.py | 100% | Connection test, error reporting |

### Test Categories

**Model Tests** (tests/test_models.py):
- Model instantiation with all fields
- Model field type validation
- Relationship access (user.tasks, task.user, task.tags)
- Field constraint enforcement
- Type hint verification

**Connection Tests** (tests/test_connection.py):
- Successful connection with valid DATABASE_URL
- Connection failure with invalid DATABASE_URL
- Session creation via get_session()
- Session cleanup after use
- Concurrent session handling

**Migration Tests** (tests/test_migration.py):
- All tables created
- All indexes created
- Foreign key constraints created
- Unique constraints enforced
- Idempotency (run twice safely)

---

## Environment Configuration

### Required Environment Variables

**DATABASE_URL**:
- **Format**: `postgresql://user:password@host:port/database?sslmode=require`
- **Example**: `postgresql://neondb_owner:abc123@ep-cool-name.region.aws.neon.tech/neondb?sslmode=require`
- **Source**: Neon PostgreSQL dashboard connection string
- **Validation**: Must include `sslmode=require` for Neon compatibility

**.env.example** (template for developers):
```bash
# Neon PostgreSQL Connection String
# Get this from your Neon dashboard: https://neon.tech
# Format: postgresql://user:password@host:port/database?sslmode=require
DATABASE_URL=postgresql://neondb_owner:your-password@ep-your-instance.region.aws.neon.tech/neondb?sslmode=require

# Optional: Override connection pool settings
# DB_POOL_SIZE=5
# DB_MAX_OVERFLOW=10
```

### .gitignore Requirements

Ensure `.env` is excluded from version control:
```
# Environment variables
.env
.env.local
.env.*.local

# Python
__pycache__/
*.pyc
.venv/
venv/
```

---

## Next Steps

This plan is complete. Proceed to task generation:

```bash
/sp.tasks
```

Expected task breakdown:
1. Setup phase (install dependencies, configure .env)
2. Test phase (write test fixtures, test cases)
3. Implementation phase (models.py, db.py, migration script)
4. Verification phase (run tests, check coverage)
5. Documentation phase (quickstart guide, contracts)
