# Tasks: Database Foundation for Phase II Backend

**Input**: Design documents from `/specs/005-database-foundation/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not explicitly requested in specification - following implementation-first approach

**Organization**: Tasks grouped by user story (P1, P2, P3) to enable independent implementation and testing

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story label (US1, US2, US3)
- File paths: `backend/` prefix for all backend files

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, dependency installation, and environment configuration

- [ ] T001 Verify backend directory exists at backend/ and navigate to it
- [ ] T002 Install SQLModel dependency: `cd backend && uv add sqlmodel`
- [ ] T003 [P] Install psycopg2-binary dependency: `cd backend && uv add psycopg2-binary`
- [ ] T004 [P] Install python-dotenv dependency: `cd backend && uv add python-dotenv`
- [ ] T005 [P] Install pytest development dependency: `cd backend && uv add --dev pytest`
- [ ] T006 [P] Install pytest-cov development dependency: `cd backend && uv add --dev pytest-cov`
- [ ] T007 [P] Install mypy development dependency: `cd backend && uv add --dev mypy`
- [ ] T008 Create backend/.env.example template file with DATABASE_URL format and comments
- [ ] T009 Create backend/migrations/__init__.py empty file for package structure
- [ ] T010 [P] Create backend/scripts/__init__.py empty file for package structure
- [ ] T011 [P] Create backend/tests/__init__.py empty file for package structure
- [ ] T012 Verify pyproject.toml updated with all dependencies by UV

**Checkpoint**: All dependencies installed, project structure initialized

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T013 Configure mypy.ini in backend/ with strict mode enabled: python_version=3.11, strict=True, disallow_untyped_defs=True, disallow_any_explicit=True, warn_return_any=True, no_implicit_optional=True
- [ ] T014 Create backend/tests/conftest.py with pytest fixtures: test database engine using SQLite in-memory, fixture for creating test tables, fixture for test session creation and cleanup
- [ ] T015 Verify .gitignore excludes backend/.env, backend/__pycache__/, backend/.venv/, backend/*.pyc

**Checkpoint**: Foundation ready - user story implementation can begin

---

## Phase 3: User Story 1 - Backend Developer Defines Data Models (Priority: P1) 🎯 MVP

**Goal**: Define User, Task, and TaskTag SQLModel classes with complete fields, type hints, relationships, and constraints

**Independent Test**: Import models from models.py, verify all three classes exist with proper fields and type hints, instantiate models without errors

### Implementation for User Story 1

- [ ] T016 [US1] Create backend/models.py with imports: from sqlmodel import SQLModel, Field, Relationship; from uuid import UUID, uuid4; from datetime import datetime; from typing import Optional, List
- [ ] T017 [US1] Implement User model class in backend/models.py: inherit from SQLModel with table=True, add __tablename__ = "users", define id field as UUID with Field(default_factory=uuid4, primary_key=True), define username field as str with Field(max_length=50, unique=True, index=True), define email field as str with Field(max_length=100, unique=True, index=True), define password_hash field as str with Field(max_length=255), define created_at field as datetime with Field(default_factory=datetime.utcnow), define updated_at field as datetime with Field(default_factory=datetime.utcnow), add tasks relationship as List["Task"] = Relationship(back_populates="user"), add Google-style docstring describing User model purpose and all attributes
- [ ] T018 [US1] Implement Task model class in backend/models.py: inherit from SQLModel with table=True, add __tablename__ = "tasks", define id field as UUID with Field(default_factory=uuid4, primary_key=True), define user_id field as UUID with Field(foreign_key="users.id", index=True), define title field as str with Field(max_length=200), define description field as Optional[str] with Field(default=None), define completed field as bool with Field(default=False, index=True), define priority field as str with Field(default="medium", max_length=20, index=True), define created_at field as datetime with Field(default_factory=datetime.utcnow), define updated_at field as datetime with Field(default_factory=datetime.utcnow), add user relationship as User = Relationship(back_populates="tasks"), add tags relationship as List["TaskTag"] = Relationship(back_populates="task"), add __table_args__ = (Index("idx_user_completed", "user_id", "completed"),) for composite index, add CHECK constraint validation for priority enum, add Google-style docstring
- [ ] T019 [US1] Implement TaskTag model class in backend/models.py: inherit from SQLModel with table=True, add __tablename__ = "task_tags", define id field as UUID with Field(default_factory=uuid4, primary_key=True), define task_id field as UUID with Field(foreign_key="tasks.id", index=True), define tag_name field as str with Field(max_length=50, index=True), define created_at field as datetime with Field(default_factory=datetime.utcnow), add task relationship as Task = Relationship(back_populates="tags"), add __table_args__ = (UniqueConstraint("task_id", "tag_name", name="uq_task_tag"),) for unique constraint on combination, add Google-style docstring
- [ ] T020 [US1] Add necessary imports to backend/models.py for Index and UniqueConstraint: from sqlalchemy import Index, UniqueConstraint
- [ ] T021 [US1] Verify all three models (User, Task, TaskTag) are exported from backend/models.py by adding __all__ = ["User", "Task", "TaskTag"]
- [ ] T022 [US1] Run mypy type checking on backend/models.py with strict mode: `cd backend && mypy models.py --strict` and verify zero errors with no Any types
- [ ] T023 [US1] Create backend/tests/test_models.py with test_user_model_fields: import User model, instantiate User with all required fields, assert all field values correct, verify type hints with get_type_hints()
- [ ] T024 [P] [US1] Add test_task_model_fields to backend/tests/test_models.py: import Task model, instantiate Task with all fields, verify foreign key field user_id exists, verify relationships defined
- [ ] T025 [P] [US1] Add test_tasktag_model_unique_constraint to backend/tests/test_models.py: import TaskTag model, verify __table_args__ contains UniqueConstraint, instantiate TaskTag and verify fields
- [ ] T026 [P] [US1] Add test_user_task_relationship to backend/tests/test_models.py: verify User.tasks relationship returns List[Task] type, verify Task.user relationship returns User type
- [ ] T027 [US1] Run pytest on backend/tests/test_models.py: `cd backend && pytest tests/test_models.py -v` and verify all model tests pass

**Checkpoint**: User Story 1 complete - All three models defined with complete type hints, relationships configured, tests passing

---

## Phase 4: User Story 2 - Backend Developer Establishes Database Connection (Priority: P2)

**Goal**: Establish secure connection to Neon PostgreSQL with session management via dependency injection

**Independent Test**: Run database connection with valid DATABASE_URL, verify connection succeeds, use get_session() with FastAPI Depends(), verify session auto-closes

### Implementation for User Story 2

- [ ] T028 [US2] Create backend/db.py with imports: from sqlmodel import Session, create_engine; from typing import Generator; import os; from dotenv import load_dotenv
- [ ] T029 [US2] Add environment variable loading in backend/db.py: call load_dotenv() to load .env file, get DATABASE_URL from environment with os.getenv("DATABASE_URL"), add validation to raise ValueError with helpful message if DATABASE_URL is None or empty
- [ ] T030 [US2] Create database engine in backend/db.py: call create_engine(DATABASE_URL, echo=True, pool_size=5, max_overflow=10, pool_timeout=30, pool_recycle=3600), store in module-level engine variable, add error handling for invalid connection string format with clear error message
- [ ] T031 [US2] Implement get_session() function in backend/db.py: define function with return type Generator[Session, None, None], use context manager pattern `with Session(engine) as session:`, yield session for FastAPI dependency injection, session automatically closed after yield, add Google-style docstring explaining dependency injection usage
- [ ] T032 [US2] Add type hints to all functions in backend/db.py ensuring no Any types, verify with mypy strict mode
- [ ] T033 [US2] Create backend/scripts/test_connection.py script: import engine from db module, import Session from sqlmodel, create test_connection() function that creates session and executes simple query `SELECT 1`, print success message with database host information from engine.url, add error handling with try/except printing clear failure message, add script entry point with if __name__ == "__main__": test_connection()
- [ ] T034 [US2] Create backend/tests/test_connection.py with test_database_connection_valid: mock DATABASE_URL environment variable with valid Neon format, import engine from db, verify engine created successfully, create session and execute simple query, assert query succeeds
- [ ] T035 [P] [US2] Add test_database_connection_invalid to backend/tests/test_connection.py: mock DATABASE_URL with invalid format, attempt to import db module or create engine, expect ValueError or connection error with clear message
- [ ] T036 [P] [US2] Add test_get_session_dependency to backend/tests/test_connection.py: import get_session from db, call it and verify it yields Session object, verify session is closed after generator exits
- [ ] T037 [US2] Run pytest on backend/tests/test_connection.py: `cd backend && pytest tests/test_connection.py -v` and verify all connection tests pass
- [ ] T038 [US2] Manually test connection script: create backend/.env with valid DATABASE_URL from Neon dashboard, run `cd backend && python scripts/test_connection.py` and verify success message appears

**Checkpoint**: User Story 2 complete - Database connection working, session management ready for FastAPI routes

---

## Phase 5: User Story 3 - Backend Developer Creates Database Tables (Priority: P3)

**Goal**: Run migration script to create all tables with indexes and constraints in Neon PostgreSQL database

**Independent Test**: Execute migration script, verify all three tables exist in database with correct columns, foreign keys, and indexes via metadata inspection

### Implementation for User Story 3

- [ ] T039 [US3] Create backend/migrations/create_tables.py with imports: from sqlmodel import SQLModel; from backend.db import engine; from backend.models import User, Task, TaskTag; import logging
- [ ] T040 [US3] Configure logging in backend/migrations/create_tables.py: set up logging with INFO level, format includes timestamp and message
- [ ] T041 [US3] Implement create_tables() function in backend/migrations/create_tables.py: log "Creating database tables...", call SQLModel.metadata.create_all(engine, checkfirst=True) to create all tables idempotently, log "Table creation complete", add error handling with try/except catching database connection errors and logging failure with details, add Google-style docstring
- [ ] T042 [US3] Add table verification step in create_tables() function: after table creation, query database metadata to verify users table exists with all columns (id, username, email, password_hash, created_at, updated_at), verify tasks table exists with all columns, verify task_tags table exists with all columns, log verification results
- [ ] T043 [US3] Add index verification step in create_tables() function: query pg_indexes system table to verify unique indexes on users.email and users.username, verify indexes on tasks.user_id/completed/priority, verify composite index idx_user_completed on tasks(user_id, completed), verify indexes on task_tags.task_id and task_tags.tag_name, log index verification results
- [ ] T044 [US3] Add foreign key verification step in create_tables() function: query pg_constraint system table to verify foreign key from tasks.user_id to users.id, verify foreign key from task_tags.task_id to tasks.id with CASCADE DELETE, log foreign key verification results
- [ ] T045 [US3] Add script entry point to backend/migrations/create_tables.py: if __name__ == "__main__": create_tables(), print final success or failure status
- [ ] T046 [US3] Create backend/tests/test_migration.py with test_migration_creates_all_tables: import create_tables function, use test database, run create_tables(), query information_schema.tables, assert users, tasks, task_tags tables exist
- [ ] T047 [P] [US3] Add test_migration_creates_indexes to backend/tests/test_migration.py: run create_tables(), query pg_indexes, assert all expected indexes exist (users email/username unique, tasks user_id/completed/priority, composite user_completed, task_tags task_id/tag_name)
- [ ] T048 [P] [US3] Add test_migration_creates_foreign_keys to backend/tests/test_migration.py: run create_tables(), query pg_constraint for foreign keys, assert tasks.user_id FK exists, assert task_tags.task_id FK exists with CASCADE DELETE
- [ ] T049 [P] [US3] Add test_migration_idempotent to backend/tests/test_migration.py: run create_tables() twice, assert no errors on second run, verify tables still exist correctly
- [ ] T050 [P] [US3] Add test_unique_constraints_enforced to backend/tests/test_migration.py: run create_tables(), attempt to insert two users with same email using session.exec(), expect IntegrityError for unique constraint violation
- [ ] T051 [P] [US3] Add test_foreign_key_constraints_enforced to backend/tests/test_migration.py: run create_tables(), attempt to insert task with non-existent user_id, expect IntegrityError for foreign key violation
- [ ] T052 [US3] Run pytest on backend/tests/test_migration.py: `cd backend && pytest tests/test_migration.py -v` and verify all migration tests pass
- [ ] T053 [US3] Manually execute migration script: ensure backend/.env has valid DATABASE_URL, run `cd backend && python migrations/create_tables.py`, verify success message and all verification steps pass, verify no errors
- [ ] T054 [US3] Verify tables in Neon database using psql: run `psql $DATABASE_URL -c "\dt"` and confirm users, tasks, task_tags tables listed
- [ ] T055 [P] [US3] Verify indexes in Neon database: run `psql $DATABASE_URL -c "\di"` and confirm all expected indexes exist
- [ ] T056 [P] [US3] Verify foreign keys in Neon database: run `psql $DATABASE_URL -c "SELECT conname, conrelid::regclass, confrelid::regclass FROM pg_constraint WHERE contype = 'f';"` and confirm FK constraints exist

**Checkpoint**: User Story 3 complete - All tables created in Neon PostgreSQL with indexes and constraints verified

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, documentation, and quality assurance across all user stories

- [ ] T057 Run complete test suite: `cd backend && pytest tests/ -v --cov=backend --cov-report=html` and verify all tests pass with 100% coverage for models.py and db.py
- [ ] T058 [P] Run mypy type checking on all backend files: `cd backend && mypy models.py db.py migrations/create_tables.py scripts/test_connection.py --strict` and verify zero type errors
- [ ] T059 [P] Verify models are importable from other modules: create temporary test script importing `from backend.models import User, Task, TaskTag`, run script, verify no import errors, delete test script
- [ ] T060 [P] Verify get_session() works with FastAPI Depends: create temporary FastAPI route using `session: Session = Depends(get_session)`, verify it type checks and would work in real route handler, delete test script
- [ ] T061 Update backend/README.md with database setup section: add link to quickstart.md, add instructions for running migration, add link to test_connection.py script, add troubleshooting section for common DATABASE_URL errors
- [ ] T062 Create backend/MODELS.md documentation: document all three models with field descriptions, relationship explanations, constraint details, usage examples from contracts/, link to contracts/ for detailed interfaces
- [ ] T063 [P] Add inline comments to backend/models.py explaining complex relationships and __table_args__ configurations for future developers
- [ ] T064 Verify all acceptance criteria from spec.md: review spec.md acceptance scenarios for user stories 1, 2, 3, manually verify each scenario can be tested with current implementation, document any gaps
- [ ] T065 Final verification checklist: models defined with complete type hints (FR-001 to FR-003), relationships configured (FR-004 to FR-005), database connection working (FR-006 to FR-007), migration script functional (FR-008), all indexes created (FR-009 to FR-012), foreign key constraints enforced (FR-013 to FR-014), type safety verified (FR-015), models exportable (FR-016), test connection script working (FR-017)

**Final Checkpoint**: All user stories complete, all acceptance criteria met, ready for integration with API features

---

## User Story Dependency Graph

```
┌─────────────┐
│   Setup     │  (Phase 1: T001-T012)
│  (Parallel) │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Foundational   │  (Phase 2: T013-T015)
│ (Prerequisites) │
└────────┬────────┘
         │
         ├─────────────────┐
         │                 │
         ▼                 ▼
┌──────────────┐    ┌─────────────────┐
│ User Story 1 │    │ User Story 2    │
│ (Models P1)  │───▶│ (Connection P2) │
│ T016-T027    │    │ T028-T038       │
└──────────────┘    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ User Story 3    │
                    │ (Migration P3)  │
                    │ T039-T056       │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     Polish      │
                    │   T057-T065     │
                    └─────────────────┘
```

**Dependency Explanation**:
- **Setup → Foundational**: Must install dependencies before configuration
- **Foundational → US1**: Must have test infrastructure before defining models
- **US1 → US2**: Connection module imports models, so models must be defined first
- **US2 → US3**: Migration script imports both models and connection, so both must be ready
- **US3 → Polish**: Final validation requires all components complete

**Independent Testing**:
- **US1 Standalone**: Can test model definitions by importing and instantiating (tests T023-T027)
- **US2 Standalone**: Can test connection independently of migration (tests T034-T036)
- **US3 Standalone**: Can test migration creates schema independently (tests T046-T051)

---

## Parallel Execution Opportunities

### Within Setup Phase (T002-T011)
All dependency installation tasks can run in parallel:
```bash
# Parallel execution example (run simultaneously)
uv add sqlmodel &
uv add psycopg2-binary &
uv add python-dotenv &
uv add --dev pytest &
uv add --dev pytest-cov &
uv add --dev mypy &
wait
```

### Within User Story 1 Tests (T023-T026)
All model test files can be written in parallel (different test functions):
- T023: test_user_model_fields [P]
- T024: test_task_model_fields [P]
- T025: test_tasktag_model_unique_constraint [P]
- T026: test_user_task_relationship [P]

### Within User Story 2 Tests (T034-T036)
All connection test functions can be written in parallel:
- T034: test_database_connection_valid [P]
- T035: test_database_connection_invalid [P]
- T036: test_get_session_dependency [P]

### Within User Story 3 Tests (T046-T051)
All migration test functions can be written in parallel:
- T046: test_migration_creates_all_tables [P]
- T047: test_migration_creates_indexes [P]
- T048: test_migration_creates_foreign_keys [P]
- T049: test_migration_idempotent [P]
- T050: test_unique_constraints_enforced [P]
- T051: test_foreign_key_constraints_enforced [P]

### Within Polish Phase (T057-T064)
Several validation tasks can run in parallel:
- T058: mypy type checking [P]
- T059: test model imports [P]
- T060: test session dependency [P]
- T063: add inline comments [P]

---

## Implementation Strategy

### MVP Scope (Minimal Viable Product)

**Recommended MVP**: User Story 1 ONLY (Tasks T001-T027)

Delivers:
- ✅ All three data models defined with type hints
- ✅ Models importable and instantiable
- ✅ Type safety verified with mypy
- ✅ Model tests passing

Enables:
- Other developers can start building on models
- API endpoints can reference models in type hints
- Clear data contracts established

Deferred to later increments:
- Database connection (US2)
- Table creation (US3)
- Full integration

### Incremental Delivery

**Increment 1**: User Story 1 (T001-T027)
- Delivers: Model definitions
- Value: Type-safe contracts for API development
- Testable: Model import and instantiation tests

**Increment 2**: User Story 1 + 2 (T001-T038)
- Delivers: Models + database connection
- Value: Can now persist data to database
- Testable: Connection tests + model tests

**Increment 3**: All User Stories (T001-T056)
- Delivers: Complete database foundation
- Value: Production-ready database layer with schema
- Testable: Full integration with real database

**Increment 4**: Polished Release (T001-T065)
- Delivers: Documented, validated, production-ready
- Value: Can be integrated with API features
- Testable: All acceptance criteria verified

### Execution Recommendations

**For Fast MVP**:
1. Execute Phase 1 (Setup): T001-T012
2. Execute Phase 2 (Foundational): T013-T015
3. Execute Phase 3 (US1): T016-T027
4. **STOP** - MVP complete, models available

**For Full Feature**:
1. Execute all phases in order: Phase 1 → 2 → 3 → 4 → 5 → 6
2. Leverage parallel tasks within each phase
3. Run checkpoints after each phase
4. Final validation in Phase 6

---

## Task Summary

**Total Tasks**: 65 tasks across 6 phases

| Phase | Tasks | Parallelizable | Description |
|-------|-------|----------------|-------------|
| Phase 1: Setup | 12 | 10 | Dependency installation, directory structure |
| Phase 2: Foundational | 3 | 1 | Configuration, test infrastructure |
| Phase 3: User Story 1 (P1) | 12 | 4 | Model definitions and tests |
| Phase 4: User Story 2 (P2) | 11 | 4 | Database connection and tests |
| Phase 5: User Story 3 (P3) | 18 | 12 | Migration script and tests |
| Phase 6: Polish | 9 | 4 | Final validation and documentation |

**Parallel Opportunities**: 35 tasks (54%) can run in parallel within their phase

**Sequential Dependencies**: 30 tasks (46%) must run in order

**User Story Breakdown**:
- US1 (Models): 12 tasks
- US2 (Connection): 11 tasks
- US3 (Migration): 18 tasks
- Infrastructure: 24 tasks

---

## Validation Checklist

Before marking feature complete, verify:

- [ ] All 65 tasks completed (checkboxes marked [X])
- [ ] All pytest tests passing (100% pass rate)
- [ ] Code coverage 100% for models.py and db.py
- [ ] Mypy type checking passes with zero errors (strict mode)
- [ ] All three tables exist in Neon PostgreSQL database
- [ ] All indexes created and verified via pg_indexes
- [ ] All foreign key constraints enforced via pg_constraint
- [ ] All unique constraints enforced (tested with duplicate attempts)
- [ ] Test connection script reports success
- [ ] Migration script runs successfully and is idempotent
- [ ] All 17 functional requirements from spec.md verified
- [ ] All 8 success criteria from spec.md met
- [ ] All acceptance scenarios from spec.md tested
- [ ] Documentation updated (README, MODELS.md)
- [ ] No Any types in codebase
- [ ] All functions have Google-style docstrings

---

## Next Command

Execute the task list:

```bash
/sp.implement
```

This will:
1. Execute each task in dependency order
2. Mark tasks complete as they finish
3. Run tests after each phase
4. Verify acceptance criteria
5. Report final status

**All planning complete! Ready for implementation.** 🎯
