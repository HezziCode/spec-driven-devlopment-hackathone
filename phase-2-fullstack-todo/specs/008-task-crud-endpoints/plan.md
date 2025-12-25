# Implementation Plan: Task Creation and Retrieval Endpoints

**Feature ID**: 008-task-crud-endpoints
**Version**: 1.0.0
**Status**: Implementation
**Created**: 2025-12-24
**Last Updated**: 2025-12-24

## 1. Scope and Dependencies

### In Scope
- POST /api/users/{user_id}/tasks endpoint implementation
- GET /api/users/{user_id}/tasks endpoint implementation
- Pydantic schemas for request/response validation (TaskCreate, TaskResponse, TaskListResponse)
- Service layer business logic for task creation and retrieval
- Input validation (title length, description length, tag count, tag length)
- User isolation enforcement (user_id path validation against JWT)
- Filtering logic (status, priority, tag, search)
- Pagination logic (limit, offset, total count)
- Tag management (create TaskTag records, prevent duplicates)
- Comprehensive unit and integration tests
- Error handling with proper HTTP status codes (201, 200, 401, 403, 422)

### Out of Scope
- Task update endpoints (PUT/PATCH) - separate feature
- Task deletion endpoint (DELETE) - separate feature
- Single task retrieval (GET /tasks/{task_id}) - separate feature
- Task sorting by fields other than created_at
- Bulk operations on tasks
- Task sharing or collaboration features
- Frontend UI components
- Database migration scripts (models already exist)
- Better Auth integration (JWT middleware already complete)

### External Dependencies
| Dependency | Owner | Status | Notes |
|------------|-------|--------|-------|
| Database Models (Task, TaskTag, User) | Database Foundation | ✅ Complete | models.py exists with all required fields |
| JWT Middleware | Auth Middleware | ✅ Complete | request.state.user_id available |
| Auth Endpoints | Auth Endpoints | ✅ Complete | Users can signup/login to get JWT tokens |
| Database Connection | Database Foundation | ✅ Complete | db.py with get_session() dependency |
| Neon PostgreSQL Database | External Service | ✅ Configured | DATABASE_URL in .env |
| FastAPI Framework | External Package | ✅ Installed | Core web framework |
| SQLModel | External Package | ✅ Installed | ORM for database operations |
| Pydantic | External Package | ✅ Installed | Data validation library |

### Internal Dependencies
- Database session management (db.py)
- JWT middleware (middleware/auth_middleware.py)
- User model for foreign key relationship
- PriorityEnum for validation

## 2. Key Decisions and Rationale

### Decision 1: Service Layer Pattern
**Options Considered**:
1. Inline business logic in route handlers
2. Service layer with separate task_service.py module
3. Repository pattern with separate repository and service layers

**Trade-offs**:
- **Option 1**: Simple but violates SRP, hard to test
- **Option 2**: Clean separation, testable, maintainable (CHOSEN)
- **Option 3**: Over-engineered for current scope

**Rationale**: Service layer provides clean separation between HTTP concerns (routes) and business logic (services), making the code more testable and maintainable. Repository pattern adds unnecessary complexity for this straightforward CRUD operation.

**Principles**: SRP (Single Responsibility Principle), testability, smallest viable change

**Reversibility**: Easy to refactor to repository pattern later if needed

### Decision 2: Tag Storage Strategy
**Options Considered**:
1. Store tags as JSON array in tasks table
2. Separate task_tags junction table (many-to-many)
3. Separate tags table with junction table

**Trade-offs**:
- **Option 1**: Simple but not queryable, no referential integrity
- **Option 2**: Queryable, simple, allows duplicate tag names (CHOSEN)
- **Option 3**: Normalized, prevents duplicate tag definitions, more complex

**Rationale**: Junction table approach allows efficient tag filtering via JOIN queries while maintaining database normalization. Allowing duplicate tag names (e.g., "work" on multiple tasks) is acceptable for this use case and simplifies implementation.

**Principles**: Database normalization, query efficiency, smallest viable change

**Reversibility**: Can migrate to option 3 (normalized tags table) later if needed

### Decision 3: Pagination Default and Limits
**Options Considered**:
1. No pagination (return all tasks)
2. Default limit=20, max limit=100 (CHOSEN)
3. Default limit=50, max limit=500

**Trade-offs**:
- **Option 1**: Simple but performance issues with large task lists
- **Option 2**: Balances performance and usability (CHOSEN)
- **Option 3**: Higher limits may cause slow queries

**Rationale**: Default limit of 20 is reasonable for most users (fits on screen without scrolling). Max limit of 100 prevents abuse while allowing bulk operations. Follows REST API best practices.

**Principles**: Performance, user experience, API best practices

**Reversibility**: Can adjust limits via configuration if needed

### Decision 4: Search Implementation
**Options Considered**:
1. Exact match only
2. Case-insensitive partial match with ILIKE (CHOSEN)
3. Full-text search with PostgreSQL tsvector

**Trade-offs**:
- **Option 1**: Fast but poor user experience
- **Option 2**: Good UX, simple implementation, adequate performance (CHOSEN)
- **Option 3**: Best search quality but over-engineered for current needs

**Rationale**: ILIKE provides good enough search for typical task titles/descriptions. Full-text search adds complexity and may not be needed for short text fields. Can upgrade later if performance issues arise.

**Principles**: User experience, performance, smallest viable change

**Reversibility**: Can add full-text search indexes later without breaking API

### Decision 5: Filter Combination Logic
**Options Considered**:
1. Only one filter at a time
2. Multiple filters combined with AND logic (CHOSEN)
3. Multiple filters with configurable AND/OR logic

**Trade-offs**:
- **Option 1**: Simple but limited usability
- **Option 2**: Intuitive, covers most use cases (CHOSEN)
- **Option 3**: Flexible but complex API design

**Rationale**: AND logic is intuitive (e.g., "high priority completed tasks tagged with 'work'"). Users rarely need OR logic for task filtering. Keeps API simple and predictable.

**Principles**: API simplicity, user experience, smallest viable change

**Reversibility**: Can add OR logic or query DSL later if needed

### Decision 6: Error Response Format
**Options Considered**:
1. Plain string error messages
2. Structured error objects with code and timestamp (CHOSEN)
3. RFC 7807 Problem Details for HTTP APIs

**Trade-offs**:
- **Option 1**: Simple but not machine-readable
- **Option 2**: Structured, consistent, adequate for current needs (CHOSEN)
- **Option 3**: Industry standard but more complex to implement

**Rationale**: Structured error format with error code and timestamp provides consistency across all endpoints while being simple to implement. Follows constitution requirements for error response format.

**Principles**: Consistency, API usability, constitution compliance

**Reversibility**: Can migrate to RFC 7807 later if needed

## 3. Interfaces and API Contracts

### Public APIs

#### POST /api/users/{user_id}/tasks
**Purpose**: Create a new task for the authenticated user

**Inputs**:
- Path: `user_id` (UUID, required)
- Headers: `Authorization: Bearer <jwt_token>` (required)
- Body:
```python
{
    "title": str,           # 1-200 chars, required
    "description": str,     # max 1000 chars, optional
    "priority": str,        # enum: low|medium|high|critical, optional, default: medium
    "tags": List[str]       # max 10 tags, 50 chars each, optional
}
```

**Outputs**:
- Success (201):
```python
{
    "id": UUID,
    "title": str,
    "description": str | None,
    "completed": bool,      # Always false for new tasks
    "priority": str,
    "tags": List[str],
    "user_id": UUID,
    "created_at": datetime,
    "updated_at": datetime
}
```

**Errors**:
- 400: Malformed request body
- 401: Missing/invalid JWT token
- 403: user_id in path != JWT user_id
- 422: Validation errors (title too long, too many tags, etc.)
- 500: Unexpected server error

**Idempotency**: Not idempotent (creates new task on each call)

**Timeouts**: 5 seconds max

**Retries**: Client should not retry on success (would create duplicate tasks)

#### GET /api/users/{user_id}/tasks
**Purpose**: Retrieve task list with filtering and pagination

**Inputs**:
- Path: `user_id` (UUID, required)
- Headers: `Authorization: Bearer <jwt_token>` (required)
- Query Parameters:
```python
{
    "limit": int,          # 1-100, optional, default: 20
    "offset": int,         # >=0, optional, default: 0
    "status": str,         # "completed"|"pending", optional
    "priority": str,       # "low"|"medium"|"high"|"critical", optional
    "tag": str,            # tag name, optional
    "search": str          # search term, optional
}
```

**Outputs**:
- Success (200):
```python
{
    "tasks": [TaskResponse],  # Array of task objects
    "total": int              # Total count (filtered)
}
```

**Errors**:
- 400: Invalid query parameters
- 401: Missing/invalid JWT token
- 403: user_id in path != JWT user_id
- 500: Unexpected server error

**Idempotency**: Fully idempotent (safe to retry)

**Timeouts**: 5 seconds max

**Retries**: Client can safely retry on network errors

### Versioning Strategy
- Current version: v1 (implicit in /api/ prefix)
- Breaking changes require new version (e.g., /api/v2/)
- Non-breaking changes can be added to current version
- Deprecation period: 6 months for old versions

### Error Taxonomy
| Status Code | Error Code | Use Case | Example |
|-------------|------------|----------|---------|
| 400 | BAD_REQUEST | Malformed request body/params | Invalid JSON syntax |
| 401 | UNAUTHORIZED | Missing/invalid JWT token | Token expired |
| 403 | FORBIDDEN | Valid token but not authorized | user_id mismatch |
| 422 | VALIDATION_ERROR | Request validation failed | Title too long |
| 500 | INTERNAL_SERVER_ERROR | Unexpected server error | Database connection failed |

## 4. Non-Functional Requirements (NFRs) and Budgets

### Performance
| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| POST response time | p95 < 200ms | API monitoring/tests |
| GET response time | p95 < 200ms | API monitoring/tests |
| Database query time | p95 < 50ms | Query profiling |
| Concurrent requests | 100 req/s | Load testing |

**Resource Caps**:
- Max request body size: 10KB
- Max response size: 1MB (for 100 tasks)
- Database connection pool: 10 connections

**Performance Budgets**:
- Database: 1 INSERT for task + N INSERTs for tags (1 + tag_count)
- GET: 1 SELECT for tasks + 1 SELECT per task for tags (could be optimized to 1 query with JOIN)

### Reliability
**SLOs**:
- Availability: 99.9% uptime
- Error rate: < 0.1% of requests

**Error Budgets**:
- Downtime: 43 minutes per month
- Failed requests: 1 per 1000

**Degradation Strategy**:
- If database slow: Return 503 Service Unavailable
- If tag table unavailable: Return tasks without tags (graceful degradation)
- Circuit breaker pattern for database connections

### Security
**Authentication/Authorization**:
- JWT token required on all requests (enforced by middleware)
- user_id in path must match JWT user_id (enforced in route handler)
- Token expiration: 7 days (handled by Better Auth)

**Data Handling**:
- Input validation: All fields validated via Pydantic
- SQL injection prevention: Parameterized queries (SQLModel handles this)
- XSS prevention: JSON encoding (FastAPI handles this)

**Secrets Management**:
- DATABASE_URL: Environment variable (not in code)
- BETTER_AUTH_SECRET: Environment variable (shared with frontend)

**Auditing**:
- Log all task creation events with user_id and timestamp
- Log all failed authentication attempts
- Log all validation errors for monitoring

### Cost
**Unit Economics**:
- Database storage: ~1KB per task (title + description + metadata)
- Database operations: 2 writes per task creation (task + tags)
- API compute: ~10ms CPU time per request

**Cost Optimization**:
- Use database indexes to minimize query time
- Implement pagination to limit response size
- Consider caching for frequently accessed task lists (future optimization)

## 5. Data Management and Migration

### Source of Truth
- **Primary**: PostgreSQL database (tasks and task_tags tables)
- **Cache**: None (current implementation)
- **Backups**: Neon automated backups (managed by Neon)

### Schema Evolution
**Current Schema**:
```sql
-- tasks table (already exists)
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes (already exist)
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_user_completed ON tasks(user_id, completed);

-- task_tags table (already exists)
CREATE TABLE task_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    tag_name VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(task_id, tag_name)
);

-- Indexes (already exist)
CREATE INDEX idx_task_tags_task_id ON task_tags(task_id);
CREATE INDEX idx_task_tags_tag_name ON task_tags(tag_name);
```

**Future Schema Changes** (out of scope for this feature):
- Add `due_date` field to tasks
- Add `reminder_at` field to tasks
- Add `archived` field for soft deletes
- Add `tags` table with `id`, `name`, `user_id` for tag reuse

**Backward Compatibility**:
- All schema changes must be backward compatible
- New columns must have defaults or be nullable
- Column renames require dual-write period
- Column deletions require deprecation period

### Migration Strategy
**Current Feature**: No migration needed (schema already exists)

**Future Migrations**:
- Use Alembic for schema migrations
- Test migrations in development environment first
- Run migrations before deploying new code
- Always have rollback plan ready

**Rollback Plan**:
- If endpoint fails: Remove routes from main.py, redeploy previous version
- If schema change fails: Run rollback migration, redeploy previous code
- Data loss prevention: Always test migrations with production data copies

### Data Retention
- Tasks: Retained indefinitely until user deletes
- Deleted tasks: Hard delete (no soft delete in current scope)
- Task tags: Cascade delete when task deleted
- Audit logs: Retained for 90 days (if implemented)

## 6. Operational Readiness

### Observability

**Logs**:
```python
# INFO level
logger.info(f"Task created: task_id={task.id}, user_id={user_id}")
logger.info(f"Tasks retrieved: user_id={user_id}, count={len(tasks)}, total={total}")

# WARNING level
logger.warning(f"Validation error: user_id={user_id}, errors={errors}")
logger.warning(f"User ID mismatch: path_user_id={user_id}, jwt_user_id={current_user_id}")

# ERROR level
logger.error(f"Task creation failed: user_id={user_id}, error={str(e)}")
logger.error(f"Task retrieval failed: user_id={user_id}, error={str(e)}")
```

**Metrics** (to be collected):
- `task_create_requests_total` (counter): Total POST requests
- `task_create_success_total` (counter): Successful POST requests
- `task_create_errors_total` (counter): Failed POST requests by error type
- `task_create_duration_seconds` (histogram): POST request duration
- `task_list_requests_total` (counter): Total GET requests
- `task_list_success_total` (counter): Successful GET requests
- `task_list_errors_total` (counter): Failed GET requests by error type
- `task_list_duration_seconds` (histogram): GET request duration
- `task_list_result_count` (histogram): Number of tasks returned

**Traces** (future):
- Distributed tracing with request IDs
- Track request flow: API → Service → Database
- Identify slow database queries

### Alerting

| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| High error rate | Error rate > 5% for 5 min | Critical | Page on-call engineer |
| Slow requests | p95 > 500ms for 5 min | Warning | Investigate database performance |
| Database connection failures | > 10 failures in 1 min | Critical | Check database health |
| High validation error rate | Validation errors > 10% | Warning | Review input validation logic |

**On-Call Owners**: Backend team

### Runbooks

**Runbook 1: High Error Rate**
1. Check error logs for specific error types
2. If database errors: Check database connection pool and health
3. If validation errors: Review recent code changes
4. If authentication errors: Check JWT middleware and Better Auth
5. Escalate to database team if database issues persist

**Runbook 2: Slow Request Performance**
1. Check database query performance with EXPLAIN
2. Verify indexes exist on user_id, completed, priority, tag_name
3. Check for missing connection pool configuration
4. Consider adding database query caching
5. Review query patterns for N+1 issues

**Runbook 3: User ID Mismatch Errors**
1. Check JWT middleware logs for token validation issues
2. Verify BETTER_AUTH_SECRET matches frontend configuration
3. Check for client-side bugs sending wrong user_id
4. Review recent changes to authentication flow

### Deployment Strategy

**Deployment Steps**:
1. Run tests locally (`pytest backend/tests/`)
2. Deploy to staging environment
3. Run integration tests in staging
4. Smoke test endpoints manually
5. Deploy to production using rolling update
6. Monitor error rates and response times
7. If issues detected, rollback immediately

**Rollback Strategy**:
- Keep previous version running during deployment
- If errors > 5%: Rollback to previous version
- If p95 latency > 500ms: Rollback to previous version
- Rollback time: < 5 minutes

**Feature Flags**: Not needed for this feature (straightforward API endpoints)

**Compatibility**:
- Backward compatible: Yes (new endpoints, no changes to existing)
- Forward compatible: Yes (clients ignore unknown response fields)

## 7. Risk Analysis and Mitigation

### Risk 1: N+1 Query Problem with Tags
**Description**: Fetching tags for each task individually causes N+1 database queries (1 for tasks, N for tags)

**Impact**: High - Slow performance with large task lists, p95 latency > 200ms

**Probability**: High - Current service implementation loads tags in loop

**Mitigation**:
- **Immediate**: Limit max tasks per request to 100
- **Short-term**: Optimize to use JOIN query to load tasks and tags in single query
- **Long-term**: Add database query caching

**Blast Radius**: All users retrieving task lists

**Kill Switch**: Rate limiting on GET endpoint

### Risk 2: User ID Mismatch Not Caught
**Description**: Bug in user_id validation allows cross-user data access

**Impact**: Critical - Security breach, data privacy violation

**Probability**: Low - Comprehensive tests should catch this

**Mitigation**:
- **Prevention**: Comprehensive unit and integration tests for user isolation
- **Detection**: Log all user_id mismatch attempts, monitor for anomalies
- **Response**: Immediate incident response, audit all access logs

**Blast Radius**: Potentially all users if exploit discovered

**Kill Switch**: Disable endpoints immediately, deploy fix

### Risk 3: Database Connection Pool Exhaustion
**Description**: High traffic exhausts database connection pool, requests timeout

**Impact**: Medium - Service unavailable for new requests

**Probability**: Medium - Depends on traffic patterns

**Mitigation**:
- **Prevention**: Configure adequate connection pool size (10-20 connections)
- **Detection**: Monitor connection pool utilization
- **Response**: Return 503 Service Unavailable when pool exhausted
- **Recovery**: Scale connection pool or database

**Blast Radius**: All users during high traffic

**Guardrails**: Connection pool timeout (5s), circuit breaker pattern

## 8. Evaluation and Validation

### Definition of Done
- ✅ All Pydantic schemas implemented and tested
- ✅ All service layer functions implemented and tested
- ✅ POST /api/users/{user_id}/tasks endpoint functional
- ✅ GET /api/users/{user_id}/tasks endpoint functional
- ✅ User isolation enforced (403 on mismatch)
- ✅ Input validation working (422 on errors)
- ✅ Filtering logic working (status, priority, tag, search)
- ✅ Pagination logic working (limit, offset, total)
- ✅ Tag management working (create, retrieve, deduplicate)
- ✅ All unit tests passing (≥95% coverage)
- ✅ All integration tests passing
- ✅ Manual testing complete (Postman/curl)
- ✅ Code review complete
- ✅ Documentation complete (docstrings, README)
- ✅ Type hints complete (mypy passing)
- ✅ Linting complete (ruff/black passing)

### Output Validation

**Format Validation**:
- Response body matches OpenAPI schema
- All required fields present
- All field types correct
- Timestamps in ISO 8601 format
- UUIDs in standard format

**Requirements Validation**:
- ✅ FR-1: POST endpoint creates tasks with all fields
- ✅ FR-2: GET endpoint retrieves tasks with filtering
- ✅ US-1: User can create task with title, description, priority, tags
- ✅ US-2: User can retrieve tasks with filters and pagination
- ✅ US-3: User isolation enforced on all operations

**Safety Validation**:
- No SQL injection vulnerabilities (parameterized queries)
- No XSS vulnerabilities (JSON encoding)
- No sensitive data in error messages
- No cross-user data access (comprehensive tests)
- Proper error handling (no unhandled exceptions)

### Test Plan

**Unit Tests** (backend/tests/test_task_service.py):
```python
def test_create_task_valid_data()
def test_create_task_with_tags()
def test_create_task_empty_tags_stripped()
def test_create_task_duplicate_tags_deduplicated()
def test_get_user_tasks_no_filters()
def test_get_user_tasks_filter_by_status()
def test_get_user_tasks_filter_by_priority()
def test_get_user_tasks_filter_by_tag()
def test_get_user_tasks_search_title()
def test_get_user_tasks_search_description()
def test_get_user_tasks_combined_filters()
def test_get_user_tasks_pagination()
def test_get_user_tasks_empty_results()
```

**Integration Tests** (backend/tests/test_tasks_endpoints.py):
```python
def test_post_tasks_success(client, jwt_token)
def test_post_tasks_no_token(client)
def test_post_tasks_user_id_mismatch(client, jwt_token)
def test_post_tasks_invalid_data(client, jwt_token)
def test_post_tasks_title_too_long(client, jwt_token)
def test_post_tasks_too_many_tags(client, jwt_token)
def test_get_tasks_success(client, jwt_token)
def test_get_tasks_no_token(client)
def test_get_tasks_user_id_mismatch(client, jwt_token)
def test_get_tasks_with_filters(client, jwt_token)
def test_get_tasks_with_pagination(client, jwt_token)
def test_create_and_retrieve_task_flow(client, jwt_token)
```

**Manual Test Cases**:
1. Create task with all fields via Postman
2. Create task with only required fields via Postman
3. Retrieve empty task list via Postman
4. Retrieve task list with filters via Postman
5. Test pagination with curl (limit=5, offset=0, then offset=5)
6. Test search functionality via Postman
7. Test user isolation by changing user_id in path
8. Test without JWT token (expect 401)

### Performance Testing
- Load test with 100 concurrent users
- Verify p95 latency < 200ms
- Verify database query time < 50ms
- Profile slow queries with EXPLAIN

## 9. Implementation Order

### Phase 1: Foundation (30 min)
1. ✅ Create specs/008-task-crud-endpoints/ directory
2. ✅ Create spec.md (this document)
3. ✅ Create plan.md (this document)
4. Create tasks.md with TDD breakdown

### Phase 2: Schemas (15 min)
5. Verify schemas/task.py exists with all required schemas
6. Add any missing validation rules
7. Write unit tests for schema validation

### Phase 3: Service Layer (30 min)
8. Verify services/task_service.py exists with create_task()
9. Verify services/task_service.py exists with get_user_tasks()
10. Add any missing validation logic
11. Write comprehensive unit tests for service layer

### Phase 4: Routes (30 min)
12. Verify routes/tasks.py exists with POST endpoint
13. Verify routes/tasks.py exists with GET endpoint
14. Ensure user isolation checks in place
15. Write integration tests for both endpoints

### Phase 5: Testing (45 min)
16. Run all unit tests (pytest backend/tests/test_task_service.py)
17. Run all integration tests (pytest backend/tests/test_tasks_endpoints.py)
18. Run manual tests with Postman/curl
19. Verify test coverage ≥95%

### Phase 6: Validation (30 min)
20. Run type checker (mypy backend/)
21. Run linter (ruff backend/)
22. Review code for best practices
23. Update documentation if needed

### Phase 7: Deployment (15 min)
24. Commit changes with descriptive message
25. Push to feature branch (008-task-crud-endpoints)
26. Create pull request
27. Deploy to staging for final testing

**Total Estimated Time**: 3 hours

**Dependencies**: All prerequisites (database, JWT middleware, auth endpoints) already complete

**Parallelization**: Phases 2-4 could be done in parallel by multiple developers if needed

## 10. File Structure

```
backend/
├── main.py                          # ✅ Include tasks router (already done)
├── db.py                            # ✅ Database session (already exists)
├── models.py                        # ✅ Task, TaskTag models (already exist)
├── schemas/
│   ├── __init__.py
│   └── task.py                      # ✅ TaskCreate, TaskResponse, TaskListResponse schemas (verify)
├── services/
│   ├── __init__.py
│   └── task_service.py              # ✅ create_task(), get_user_tasks() (verify)
├── routes/
│   ├── __init__.py
│   └── tasks.py                     # ✅ POST and GET endpoints (verify)
├── middleware/
│   └── auth_middleware.py           # ✅ JWT verification (already exists)
└── tests/
    ├── __init__.py
    ├── conftest.py                  # Test fixtures
    ├── test_task_service.py         # Unit tests for service layer
    └── test_tasks_endpoints.py      # Integration tests for API endpoints

specs/
└── 008-task-crud-endpoints/
    ├── spec.md                      # ✅ Feature specification (this file)
    ├── plan.md                      # ✅ Implementation plan (current file)
    └── tasks.md                     # TDD task breakdown (next)
```

## 11. Success Metrics

### Functional Metrics
- ✅ Both endpoints return correct HTTP status codes
- ✅ POST endpoint creates tasks in database
- ✅ GET endpoint retrieves correct tasks with filters
- ✅ User isolation prevents cross-user access
- ✅ Validation catches all invalid inputs

### Technical Metrics
- ✅ Test coverage ≥95%
- ✅ All type hints present (mypy passes)
- ✅ All linting rules pass (ruff/black)
- ✅ Response time p95 < 200ms
- ✅ Database queries < 50ms

### Business Metrics
- Task creation success rate > 99%
- Task retrieval success rate > 99%
- User adoption (track POST requests per day)
- Task search usage (track search parameter usage)

## Summary

This implementation plan provides a comprehensive roadmap for building the POST and GET task endpoints. The key architectural decisions prioritize simplicity, testability, and security while maintaining performance and scalability. The service layer pattern separates concerns cleanly, the junction table strategy enables efficient tag filtering, and the pagination/filtering logic provides a great user experience.

The plan emphasizes test-driven development with comprehensive unit and integration tests to ensure correctness and prevent regressions. Error handling follows the constitution's standardized format, and user isolation is enforced at multiple layers for defense in depth.

With all prerequisites already in place (database models, JWT middleware, auth endpoints), implementation should be straightforward and can be completed in approximately 3 hours following the phased approach outlined above.
