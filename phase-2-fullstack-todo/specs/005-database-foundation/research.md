# Research: Database Foundation Technical Decisions

**Feature**: Database Foundation for Phase II Backend
**Date**: 2025-12-23
**Status**: Complete

## Research Questions and Findings

### 1. SQLModel Session Management with FastAPI Dependency Injection

**Question**: What is the recommended pattern for SQLModel session management with FastAPI dependency injection to ensure automatic session cleanup?

**Research Findings**:
- FastAPI's `Depends()` system works with generator functions using `yield`
- The code before `yield` runs before the request
- The code after `yield` runs after the request (cleanup)
- SQLModel Session has built-in context manager support

**Decision**: Use generator function pattern with Session context manager

**Implementation**:
```python
from sqlmodel import Session, create_engine

def get_session():
    with Session(engine) as session:
        yield session
```

**Source**: FastAPI documentation on dependencies, SQLModel documentation on session management

---

### 2. UUID Primary Key Configuration in SQLModel

**Question**: What is the correct syntax for configuring UUID primary keys in SQLModel with automatic generation?

**Research Findings**:
- SQLModel Field() supports `default_factory` parameter for dynamic defaults
- Python's uuid.uuid4() generates random UUIDs (Type 4)
- UUID type from Python's uuid module works with PostgreSQL UUID type
- Default factory is called when creating new instances

**Decision**: Use `Field(default_factory=uuid.uuid4, primary_key=True)`

**Implementation**:
```python
from uuid import UUID, uuid4
from sqlmodel import Field

id: UUID = Field(default_factory=uuid4, primary_key=True)
```

**Alternatives Rejected**:
- Server-side generation with PostgreSQL `gen_random_uuid()` - requires database support configuration
- String representation of UUID - loses type safety
- Auto-increment Integer - not suitable for distributed systems

**Source**: SQLModel documentation, PostgreSQL UUID documentation

---

### 3. Neon PostgreSQL Connection String Format and Requirements

**Question**: What is the exact connection string format for Neon Serverless PostgreSQL including SSL and security requirements?

**Research Findings**:
- Neon PostgreSQL uses standard PostgreSQL connection string format
- SSL is required for all Neon connections (sslmode=require parameter)
- Connection string format: `postgresql://user:password@host:port/database?sslmode=require`
- Neon provides connection pooling automatically
- Connection strings are provided in Neon dashboard for each database

**Decision**: Use standard PostgreSQL URL with sslmode=require parameter

**Implementation**:
```python
DATABASE_URL = "postgresql://neondb_owner:password@ep-name-123.region.aws.neon.tech/neondb?sslmode=require"
```

**Security Notes**:
- Never commit DATABASE_URL to version control
- Store in .env file (excluded from git)
- Rotate passwords periodically
- Use connection pooling to prevent exhaustion

**Source**: Neon documentation, PostgreSQL connection string specification

---

### 4. SQLModel Relationship Configuration for One-to-Many and Many-to-Many

**Question**: How to properly configure bidirectional relationships in SQLModel for one-to-many and many-to-many associations?

**Research Findings**:
- Use `Relationship()` from sqlmodel for ORM navigation
- `back_populates` parameter creates bidirectional access
- For one-to-many: List[Model] on "one" side, single Model on "many" side
- For many-to-many: Use junction table with two foreign keys
- SQLModel automatically configures foreign keys when using Relationship()

**Decision**: Use Relationship(back_populates="field_name") for bidirectional associations

**Implementation**:
```python
# One-to-many: User -> Tasks
class User(SQLModel, table=True):
    tasks: List["Task"] = Relationship(back_populates="user")

class Task(SQLModel, table=True):
    user_id: UUID = Field(foreign_key="users.id")
    user: User = Relationship(back_populates="tasks")

# Many-to-many: Task <-> Tags via TaskTag
class Task(SQLModel, table=True):
    tags: List["TaskTag"] = Relationship(back_populates="task")

class TaskTag(SQLModel, table=True):
    task_id: UUID = Field(foreign_key="tasks.id")
    task: Task = Relationship(back_populates="tags")
```

**Source**: SQLModel relationships documentation, SQLAlchemy ORM tutorial

---

### 5. Index Creation Methods in SQLModel

**Question**: What is the recommended way to create single-column and composite indexes in SQLModel?

**Research Findings**:
- Single-column indexes: Use `Field(index=True)` parameter
- Composite indexes: Use `__table_args__` with SQLAlchemy Index()
- Unique indexes: Use `Field(unique=True)` or UniqueConstraint
- Index names can be specified for clarity
- Indexes are created during create_all() migration

**Decision**: Use Field(index=True) for single columns, __table_args__ for composite

**Implementation**:
```python
from sqlalchemy import Index

class Task(SQLModel, table=True):
    user_id: UUID = Field(foreign_key="users.id", index=True)
    completed: bool = Field(default=False, index=True)

    __table_args__ = (
        Index("idx_user_completed", "user_id", "completed"),
    )
```

**Source**: SQLModel Field documentation, SQLAlchemy Index documentation

---

### 6. Unique Constraint on Multiple Columns

**Question**: How to enforce unique constraints on combinations of columns (e.g., task_id + tag_name in TaskTag)?

**Research Findings**:
- Use `__table_args__` with SQLAlchemy UniqueConstraint
- Constraint enforced at database level (more reliable than application logic)
- Named constraints make error messages clearer
- Prevents race conditions with concurrent inserts

**Decision**: Use UniqueConstraint in __table_args__

**Implementation**:
```python
from sqlalchemy import UniqueConstraint

class TaskTag(SQLModel, table=True):
    task_id: UUID = Field(foreign_key="tasks.id")
    tag_name: str = Field(max_length=50)

    __table_args__ = (
        UniqueConstraint("task_id", "tag_name", name="uq_task_tag"),
    )
```

**Source**: SQLAlchemy constraints documentation

---

### 7. Migration Script Idempotency

**Question**: How to make migration scripts idempotent so they can run multiple times safely without errors?

**Research Findings**:
- SQLModel.metadata.create_all() accepts `checkfirst=True` parameter
- With checkfirst=True, only missing tables are created
- Existing tables are not modified or recreated
- Indexes and constraints are also checked before creation

**Decision**: Use create_all(engine, checkfirst=True) for safe migrations

**Implementation**:
```python
from sqlmodel import SQLModel, create_engine

def run_migration():
    engine = create_engine(DATABASE_URL)
    SQLModel.metadata.create_all(engine, checkfirst=True)
    print("Migration complete: all tables created")
```

**Alternatives Considered**:
- Manual table existence checking (more code, error-prone)
- Alembic migration framework (too complex for initial schema)
- One-time migrations (not safe for deployment automation)

**Source**: SQLModel metadata documentation, SQLAlchemy create_all API

---

### 8. Type Hints for Optional/Nullable Fields

**Question**: What is the correct type hint syntax for optional/nullable fields in SQLModel compatible with mypy strict mode?

**Research Findings**:
- Python 3.11+ supports Union type with pipe operator: `str | None`
- typing.Optional[str] is equivalent to `str | None`
- SQLModel Field(default=None) marks column as nullable
- Mypy requires explicit None in type hint for nullable fields

**Decision**: Use `Optional[str]` or `str | None` with `Field(default=None)`

**Implementation**:
```python
from typing import Optional

# Option 1: typing.Optional
description: Optional[str] = Field(default=None)

# Option 2: Modern union syntax (Python 3.11+)
description: str | None = Field(default=None)
```

**Mypy Compatibility**: Both pass mypy strict mode with `no_implicit_optional = True`

**Source**: Python typing documentation, mypy documentation, SQLModel nullable fields

---

## Technology Choices

| Decision | Chosen Option | Rationale | Alternatives Considered |
|----------|---------------|-----------|------------------------|
| **ORM** | SQLModel | Required by specification. Combines SQLAlchemy with Pydantic for type safety. Simplifies model definitions. Best FastAPI integration. | Raw SQLAlchemy (more verbose, no Pydantic validation), Tortoise ORM (lacks Pydantic integration), Django ORM (not compatible with FastAPI) |
| **Primary Key Type** | UUID (uuid.uuid4) | Better for distributed systems, no collision risk, specified in requirements. Client-side generation reduces database round-trips. | Auto-increment Integer (not suitable for distributed systems, sequential IDs expose record counts), ULID (less standard, not natively supported) |
| **PostgreSQL Driver** | psycopg2-binary | Standard driver, synchronous, works with SQLModel out of the box. Mature and stable. | asyncpg (async, requires different session management), psycopg3 (newer, less ecosystem support) |
| **Connection Pooling** | SQLAlchemy default pool | Built into create_engine(), handles concurrent connections automatically. Configurable pool_size and max_overflow. | External pool like PgBouncer (adds deployment complexity), No pooling (connection exhaustion risk) |
| **Environment Variables** | python-dotenv | Standard Python library, loads .env files automatically, simple to use. Zero configuration. | python-decouple (more features than needed for this use case), os.environ only (requires manual setup, no .env support) |
| **Migration Strategy** | Manual scripts with create_all() | Simple for initial setup, explicit control over schema. Idempotent with checkfirst=True. | Alembic (overkill for initial schema, adds complexity), SQLAlchemy-migrate (deprecated, not maintained) |
| **Type Hint Style** | Optional[T] / T \| None | Compatible with mypy strict mode, clear semantics for nullable fields. Python 3.11+ pipe syntax preferred. | No type hints (violates constitution), Any type (violates constitution) |
| **Index Strategy** | Declarative with Field() and __table_args__ | Indexes defined in code alongside models. Version controlled. Created automatically during migration. | Manual SQL index creation (not tracked in code), Separate index migration files (adds complexity) |

---

## Implementation Checklist

**Research Complete** ✅
- [X] All 8 research questions answered
- [X] Technology choices documented with rationale
- [X] Alternatives considered and rejected
- [X] Best practices identified

**Ready for Task Generation** ✅
- [X] Technical context fully specified
- [X] File structure defined
- [X] Dependencies identified
- [X] Testing strategy outlined
- [X] Success metrics defined

**Next Command**: `/sp.tasks`
