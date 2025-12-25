# Implementation Plan: Database Foundation for Phase II Backend

**Branch**: `005-database-foundation` | **Date**: 2025-12-23 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-database-foundation/spec.md`

## Summary

This implementation plan defines the technical approach for building the database foundation layer of the Phase II backend. The primary requirement is to establish three SQLModel data models (User, Task, TaskTag) with proper field definitions, type hints, relationships, and constraints, configure database connection to Neon PostgreSQL via environment variables, implement session management with dependency injection for FastAPI integration, and create a migration script that generates all tables with appropriate indexes and foreign key constraints. The technical approach involves using SQLModel as the ORM (combining SQLAlchemy and Pydantic), UUID primary keys for distributed system compatibility, explicit field definitions with SQLModel Field() for constraints, Relationship() for one-to-many and many-to-many associations, create_engine() for Neon PostgreSQL connection with connection pooling, and SQLModel.metadata.create_all() for idempotent table creation. This foundation enables all subsequent backend features including authentication endpoints, task CRUD operations, and user management by providing type-safe data models and reliable database access.

## Technical Context

**Language/Version**: Python 3.11+ (as specified in constitution for Phase II backend)
**Primary Dependencies**:
- SQLModel 0.0.14+ (ORM combining SQLAlchemy and Pydantic for type-safe models)
- psycopg2-binary 2.9+ (PostgreSQL adapter for Python)
- asyncpg 0.29+ (Async PostgreSQL driver for better performance)
- FastAPI 0.104+ (for dependency injection pattern in session management)
- pydantic 2.5+ (for data validation, included with SQLModel)
- python-dotenv 1.0+ (for loading DATABASE_URL from .env file)

**Storage**: Neon Serverless PostgreSQL (cloud-hosted PostgreSQL with connection pooling and SSL)
**Testing**: pytest 7.4+ with pytest-asyncio for async test support
**Target Platform**: Linux server environment (Neon PostgreSQL requires SSL connection)
**Project Type**: Web backend (part of monorepo with existing frontend)
**Performance Goals**:
- Database connection establishment < 5 seconds
- Simple CRUD operations < 100ms
- Migration script execution < 30 seconds for initial schema
- Type checking with mypy < 5 seconds

**Constraints**:
- Must use UUID for primary keys (not auto-increment integers)
- Must enforce foreign key constraints at database level
- Must create indexes for all foreign keys and frequently queried columns
- Must use complete type hints (no Any types)
- Must handle DATABASE_URL from environment variable
- Must support connection pooling for concurrent requests
- Must be compatible with FastAPI dependency injection

**Scale/Scope**:
- 3 data models (User, Task, TaskTag)
- 17 functional requirements from specification
- Expected to support 100+ concurrent database sessions
- Initial development supports single database instance (horizontal scaling in future)

## Constitution Check

### ✅ Principle I: Spec-Driven Development with Agents/Skills
**Status**: PASS
**Rationale**: Implementation will use database-architect agent with sqlmodel-database-modeling skill. All code generation will be automated via agents, no manual coding required.

### ✅ Principle II: Clean Code with Single Responsibility
**Status**: PASS
**Rationale**: Clear separation of concerns - models.py contains only model definitions, db.py contains only connection logic, migration script contains only table creation. Each model class represents single entity. All functions will have Google-style docstrings.

### ✅ Principle III: Type Safety (NON-NEGOTIABLE)
**Status**: PASS
**Rationale**: SQLModel inherently provides type safety by combining Pydantic validation with SQLAlchemy. All model fields will have explicit type hints (UUID, str, bool, datetime). Mypy strict mode will be enforced. No Any types allowed.

### ⚠️ Principle IV: Accessibility Compliance (WCAG 2.1 AA)
**Status**: NOT APPLICABLE
**Rationale**: Database foundation is backend infrastructure with no UI components. Accessibility requirements apply to frontend only (already complete).

### ✅ Principle V: Performance-First Architecture
**Status**: PASS
**Rationale**: Database queries will be O(1) for primary key lookups, O(log n) for indexed queries. Indexes on foreign keys (user_id, task_id), unique constraints (email, username), and composite indexes (user_id + completed) ensure efficient query performance. Connection pooling prevents resource exhaustion.

### ✅ Principle VI: Modular Architecture with Clear Boundaries
**Status**: PASS
**Rationale**: Database layer clearly separated from API routes and business logic. Models exported from models.py can be imported by any backend module. Session management via dependency injection decouples database access from route handlers. Migration script is standalone executable.

## Project Structure

### Documentation (this feature)

```text
specs/005-database-foundation/
├── plan.md              # This file (/sp.plan output)
├── spec.md              # Feature specification
├── research.md          # Technology research and decisions
├── data-model.md        # Entity relationship diagrams and definitions
├── quickstart.md        # Quick setup guide for developers
├── contracts/           # Model interface contracts
│   ├── user-model.md    # User model contract
│   ├── task-model.md    # Task model contract
│   └── tasktag-model.md # TaskTag model contract
├── checklists/          # Quality validation
│   └── requirements.md  # Spec validation
└── tasks.md             # Task breakdown (/sp.tasks - NOT created yet)
```

### Source Code (backend directory)

```text
backend/
├── models.py                # SQLModel model definitions
│                            # Contains: User, Task, TaskTag classes
│                            # All models with Field() configurations
│                            # Relationship() definitions
│                            # Complete type hints
│
├── db.py                    # Database connection and session
│                            # Contains: engine configuration
│                            # DATABASE_URL loading
│                            # get_session() dependency
│                            # Connection pooling
│
├── migrations/              # Database migration scripts
│   ├── __init__.py
│   └── create_tables.py     # Initial schema creation
│                            # Creates all tables
│                            # Creates indexes
│                            # Idempotent
│
├── scripts/                 # Utility scripts
│   ├── __init__.py
│   └── test_connection.py   # Connection verification
│
├── pyproject.toml           # Dependencies (UV managed)
├── .env                     # Environment variables
│
└── tests/                   # Test suite
    ├── __init__.py
    ├── conftest.py          # Pytest fixtures
    ├── test_models.py       # Model tests
    ├── test_connection.py   # Connection tests
    └── test_migration.py    # Migration tests
```

**Structure Decision**: Using web application structure with backend directory. Frontend is already complete, so this feature only touches backend files. Backend follows standard FastAPI structure with models at root, database in db.py, migrations in migrations/, and tests mirroring source.

## Complexity Tracking

> No constitution violations. All principles pass or not applicable to backend infrastructure.

---

## Implementation Strategy

### Phase 0: Research

*Output: research.md*

Research tasks to resolve technical unknowns:

1. **SQLModel Session Management Pattern**
   - Research recommended pattern for FastAPI dependency injection
   - Expected: Generator function with yield for automatic cleanup

2. **UUID Configuration in SQLModel**
   - Research correct Field() syntax for UUID primary keys
   - Expected: `Field(default_factory=uuid.uuid4, primary_key=True)`

3. **Neon PostgreSQL Connection Requirements**
   - Research connection string format and SSL requirements
   - Expected: `postgresql://...?sslmode=require`

4. **Relationship Configuration**
   - Research Relationship() syntax for bidirectional associations
   - Expected: `Relationship(back_populates="field_name")`

5. **Index Creation Methods**
   - Research how to create composite and unique indexes
   - Expected: Use `__table_args__` with SQLAlchemy Index()

6. **Migration Idempotency**
   - Research create_all() behavior with existing tables
   - Expected: `checkfirst=True` parameter

### Phase 1: Design

*Outputs: data-model.md, contracts/, quickstart.md*

#### Data Model Document

Create `data-model.md` with entity relationship diagram and detailed field specifications:

**User Entity**
- id: UUID, primary key, auto-generated with uuid4()
- username: String(50), unique, indexed, not null
- email: String(100), unique, indexed, not null
- password_hash: String(255), not null
- created_at: DateTime, default UTC now
- updated_at: DateTime, default UTC now
- Relationship: tasks (one-to-many with Task)

**Task Entity**
- id: UUID, primary key, auto-generated
- user_id: UUID, foreign key to users.id, indexed, not null
- title: String(200), not null
- description: Text, nullable
- completed: Boolean, default False, indexed
- priority: String(20), enum constraint, indexed, default 'medium'
- created_at: DateTime, default UTC now
- updated_at: DateTime, default UTC now
- Relationships: user (many-to-one with User), tags (many-to-many via TaskTag)

**TaskTag Entity**
- id: UUID, primary key, auto-generated
- task_id: UUID, foreign key to tasks.id, indexed, not null
- tag_name: String(50), indexed, not null
- created_at: DateTime, default UTC now
- Unique constraint: (task_id, tag_name)
- Relationship: task (many-to-one with Task)

#### Model Contracts

Create contract files documenting model interfaces:

**contracts/user-model.md**: User model public interface
**contracts/task-model.md**: Task model public interface
**contracts/tasktag-model.md**: TaskTag model public interface

#### Quickstart Guide

Create `quickstart.md` with step-by-step setup:
1. Install dependencies: `cd backend && uv sync`
2. Create .env file with DATABASE_URL
3. Run migration: `python migrations/create_tables.py`
4. Test connection: `python scripts/test_connection.py`
5. Verify schema: `psql $DATABASE_URL -c "\d users"`

---

## Implementation Files

### File 1: backend/models.py

**Purpose**: Define User, Task, and TaskTag SQLModel classes with complete type hints, field constraints, and relationships.

**Key Components**:
- Import statements (sqlmodel, uuid, datetime, typing, Optional)
- User model class with Field() configurations for all 6 fields
- Task model class with Field() configurations for all 8 fields
- TaskTag model class with Field() configurations for all 4 fields
- Relationship() definitions for User.tasks, Task.user, Task.tags, TaskTag.task
- __table_args__ for unique constraints and composite indexes
- Type hints on all fields (no Any types)
- Docstrings for each model class

**Dependencies**: sqlmodel, uuid, datetime, typing

**Tests**: tests/test_models.py (model instantiation, field types, relationships)

### File 2: backend/db.py

**Purpose**: Configure database connection to Neon PostgreSQL and provide session management via FastAPI dependency injection.

**Key Components**:
- Import statements (sqlmodel, os, python-dotenv, typing)
- Load environment variables with load_dotenv()
- Get DATABASE_URL from environment with validation
- Create SQLModel engine with create_engine(DATABASE_URL, echo=True)
- Configure connection pool (pool_size, max_overflow)
- Define get_session() generator function for dependency injection
- Error handling for missing/invalid DATABASE_URL
- Docstrings for all functions

**Dependencies**: sqlmodel, python-dotenv, os

**Tests**: tests/test_connection.py (connection establishment, session management)

### File 3: backend/migrations/create_tables.py

**Purpose**: Migration script to create all database tables with indexes and constraints.

**Key Components**:
- Import models (User, Task, TaskTag) from models.py
- Import engine from db.py
- Import SQLModel metadata
- Create main() function that calls SQLModel.metadata.create_all(engine, checkfirst=True)
- Add logging for table creation progress
- Add verification step to query database metadata
- Error handling for connection failures
- Script entry point with if __name__ == "__main__"

**Dependencies**: models.py, db.py, logging

**Tests**: tests/test_migration.py (table creation, indexes, constraints)

### File 4: backend/scripts/test_connection.py

**Purpose**: Utility script to test database connection and report status.

**Key Components**:
- Import engine from db.py
- Import SQLModel Session
- Create test_connection() function that attempts connection
- Execute simple query (SELECT 1) to verify connection
- Print success message with database host info
- Error handling for connection failures with helpful messages
- Script entry point

**Dependencies**: db.py, sqlmodel

**Tests**: tests/test_connection.py (script execution, error handling)

### File 5: backend/pyproject.toml

**Purpose**: Define Python project metadata and dependencies managed by UV.

**Key Components**:
- Project name and version
- Python version requirement (>=3.11)
- Dependencies: sqlmodel, psycopg2-binary, fastapi, python-dotenv
- Dev dependencies: pytest, pytest-asyncio, pytest-cov, mypy
- Build system configuration for UV
- Tool configurations for mypy (strict mode)

**Dependencies**: None (this file defines dependencies)

**Tests**: None (configuration file)

### File 6: backend/.env.example

**Purpose**: Template for environment variables showing required configuration.

**Key Components**:
- DATABASE_URL with example Neon connection string
- Comments explaining each variable
- Instructions for obtaining Neon credentials
- SSL requirement notice

**Dependencies**: None

**Tests**: None (documentation file)

### File 7: backend/tests/conftest.py

**Purpose**: Pytest fixtures for test database setup and teardown.

**Key Components**:
- Test database engine (SQLite in-memory for tests)
- Fixture for test session creation
- Fixture for table creation/cleanup
- Fixture for test user creation
- Fixture for test task creation

**Dependencies**: pytest, sqlmodel, models.py

**Tests**: None (test infrastructure)

### File 8: backend/tests/test_models.py

**Purpose**: Unit tests for model definitions, fields, and relationships.

**Key Components**:
- Test user model has all required fields
- Test task model has foreign key to user
- Test tasktag model has unique constraint
- Test user-task one-to-many relationship
- Test task-tags many-to-many relationship
- Test type hints are correct (using mypy or type inspection)
- Test model field constraints (max lengths, defaults)

**Dependencies**: pytest, models.py

**Tests**: Self-testing

### File 9: backend/tests/test_connection.py

**Purpose**: Integration tests for database connection and session management.

**Key Components**:
- Test database connection with valid DATABASE_URL
- Test connection failure with invalid DATABASE_URL
- Test get_session() returns valid Session
- Test session auto-closes after use
- Test concurrent session handling

**Dependencies**: pytest, db.py

**Tests**: Self-testing

### File 10: backend/tests/test_migration.py

**Purpose**: Integration tests for migration script execution and schema verification.

**Key Components**:
- Test migration creates all three tables
- Test migration creates all indexes (verify with database metadata queries)
- Test migration creates foreign key constraints
- Test migration is idempotent (run twice, no errors)
- Test unique constraints work (attempt duplicate, expect error)

**Dependencies**: pytest, migrations/create_tables.py, sqlmodel

**Tests**: Self-testing

---

## Phase 0: Research & Technical Decisions

### Research Findings

#### 1. SQLModel Session Management with FastAPI

**Decision**: Use generator function with yield for dependency injection
**Rationale**: FastAPI's Depends() system works seamlessly with generator functions that yield resources. The session is automatically closed when the request completes.

**Pattern**:
```python
def get_session():
    with Session(engine) as session:
        yield session
```

**Alternatives Considered**:
- Context manager approach (more verbose, requires explicit with blocks)
- Manual session management (error-prone, risk of connection leaks)

#### 2. UUID Primary Key Configuration

**Decision**: Use `Field(default_factory=uuid.uuid4, primary_key=True)`
**Rationale**: Client-side UUID generation with uuid4() provides random UUIDs with negligible collision probability. No database round-trip needed for ID generation.

**Pattern**:
```python
from uuid import UUID, uuid4
from sqlmodel import Field

id: UUID = Field(default_factory=uuid4, primary_key=True)
```

**Alternatives Considered**:
- Server-side generation with PostgreSQL gen_random_uuid() (requires database support)
- uuid1() with MAC address (privacy concerns)

#### 3. Neon PostgreSQL Connection String

**Decision**: Format: `postgresql://user:password@host:port/database?sslmode=require`
**Rationale**: Neon requires SSL for security. Standard PostgreSQL connection string format with sslmode parameter.

**Example**:
```
postgresql://neondb_owner:abc123@ep-cool-name-123.us-east-1.aws.neon.tech/neondb?sslmode=require
```

**Alternatives Considered**:
- Non-SSL connection (rejected, Neon requires SSL)
- Connection pooling via external PgBouncer (not needed, SQLAlchemy has built-in pooling)

#### 4. SQLModel Relationship Configuration

**Decision**: Use `Relationship(back_populates="field_name")` for bidirectional access
**Rationale**: Allows navigation in both directions (user.tasks and task.user). SQLModel automatically configures foreign keys.

**Pattern**:
```python
class User(SQLModel, table=True):
    tasks: List["Task"] = Relationship(back_populates="user")

class Task(SQLModel, table=True):
    user: User = Relationship(back_populates="tasks")
```

**Alternatives Considered**:
- Unidirectional relationship (limits query flexibility)
- Manual foreign key without Relationship (no ORM navigation)

#### 5. Index Creation in SQLModel

**Decision**: Use `Field(index=True)` for single-column indexes, `__table_args__` for composite indexes
**Rationale**: Field(index=True) is simple and declarative. For composite indexes, SQLAlchemy's Index() in __table_args__ provides full control.

**Pattern**:
```python
from sqlalchemy import Index

class Task(SQLModel, table=True):
    user_id: UUID = Field(foreign_key="users.id", index=True)
    completed: bool = Field(default=False, index=True)

    __table_args__ = (
        Index("idx_user_completed", "user_id", "completed"),
    )
```

**Alternatives Considered**:
- Manual index creation in SQL (not tracked in code)
- No composite indexes (slower queries for common filter combinations)

#### 6. Unique Constraint on (task_id, tag_name)

**Decision**: Use `__table_args__ = (UniqueConstraint('task_id', 'tag_name'),)`
**Rationale**: Prevents duplicate tags on same task at database level. More reliable than application-level checking.

**Pattern**:
```python
from sqlalchemy import UniqueConstraint

class TaskTag(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("task_id", "tag_name", name="uq_task_tag"),
    )
```

**Alternatives Considered**:
- Application-level duplicate checking (race conditions possible)
- Composite primary key (less flexible, complicates relationships)

#### 7. Migration Script Idempotency

**Decision**: Use `SQLModel.metadata.create_all(engine, checkfirst=True)`
**Rationale**: checkfirst=True makes the operation idempotent by checking table existence before creation. Safe to run multiple times.

**Pattern**:
```python
SQLModel.metadata.create_all(engine, checkfirst=True)
```

**Alternatives Considered**:
- Manual table existence checking (more complex)
- Alembic migrations (overkill for initial schema)

#### 8. Type Hints for Optional Fields

**Decision**: Use `Optional[str]` or `str | None` with `Field(default=None)`
**Rationale**: Python 3.11+ supports modern union syntax. Optional is clear and compatible with mypy strict mode.

**Pattern**:
```python
from typing import Optional

description: Optional[str] = Field(default=None)
# Or modern syntax:
description: str | None = Field(default=None)
```

**Alternatives Considered**:
- No type hint (violates constitution)
- Required field with empty string default (less semantic)

---

## Critical Decisions Summary

| Decision | Choice | Impact |
|----------|--------|--------|
| ORM | SQLModel | Type safety + simplicity |
| Primary Keys | UUID with uuid4() | Distributed system ready |
| Connection | psycopg2-binary | Stable, synchronous |
| Session Management | Generator with yield | Auto cleanup |
| Indexes | Field(index=True) + __table_args__ | Performance optimization |
| Migration | create_all with checkfirst | Idempotent execution |
| Type Checking | Mypy strict mode | Zero type errors |

---

## Success Metrics

### Functional Acceptance

| Requirement ID | Verification Method | Pass Criteria |
|----------------|---------------------|---------------|
| FR-001 | Import User model, inspect fields | All 6 fields present with correct types |
| FR-002 | Import Task model, inspect fields | All 8 fields present with foreign key |
| FR-003 | Import TaskTag model, inspect constraints | Unique constraint on (task_id, tag_name) |
| FR-004 | Access user.tasks relationship | Returns List[Task] type |
| FR-005 | Create task with tags via TaskTag | Many-to-many association works |
| FR-006 | Import db module, check engine | DATABASE_URL loaded correctly |
| FR-007 | Use get_session() with Depends() | Session provided and auto-closed |
| FR-008 | Run migration script | All three tables created |
| FR-009 | Query database metadata | Unique indexes on email and username exist |
| FR-010 | Query database metadata | Indexes on user_id, completed, priority exist |
| FR-011 | Query database metadata | Composite index on (user_id, completed) exists |
| FR-012 | Query database metadata | Indexes on task_id and tag_name exist |
| FR-013 | Attempt invalid foreign key insert | Database rejects with FK error |
| FR-014 | Attempt invalid task_id in TaskTag | Database rejects with FK error |
| FR-015 | Run mypy on models.py | Zero errors, no Any types |
| FR-016 | `from backend.models import *` | User, Task, TaskTag importable |
| FR-017 | Run test_connection.py script | Reports success with valid URL |

### Quality Gates

**Before Implementation Starts**:
- ✅ Constitution check passes
- ✅ All research questions answered
- ✅ Data model designed
- ✅ Contracts defined

**Before Testing Starts**:
- ✅ All models defined with type hints
- ✅ Database connection working
- ✅ Migration script created

**Before Feature Complete**:
- ✅ All 17 functional requirements verified
- ✅ 100% test coverage for models and db modules
- ✅ Mypy passes in strict mode
- ✅ Migration creates correct schema
- ✅ Test connection script works

---

## Risk Mitigation

| Risk | Mitigation Strategy |
|------|---------------------|
| DATABASE_URL format incorrect | Add validation with clear error message showing expected format |
| SSL requirement not met | Document sslmode=require in .env.example and error messages |
| Indexes not created | Verify indexes in migration tests by querying database metadata |
| Type hints incomplete | Run mypy in strict mode as part of test suite |
| Foreign key constraints missing | Test constraints by attempting invalid insertions |
| Migration not idempotent | Use checkfirst=True and test running migration twice |
| Connection pool exhausted | Configure pool_size and max_overflow appropriately |

---

## Next Steps

After this plan is approved, run:

```bash
/sp.tasks
```

This will generate the task breakdown in `tasks.md` following TDD approach (tests first, then implementation). Expected task phases:
1. **Setup**: Install dependencies, configure environment
2. **Test**: Write test fixtures and test cases
3. **Implement**: Create models, connection, migration
4. **Verify**: Run tests, check coverage, validate schema
5. **Document**: Update quickstart, create contracts
