# Architecture Plan: Task Deletion and Single Task Retrieval (Security-Focused)

**Feature ID**: 010-task-delete-get
**Status**: Planning
**Created**: 2025-12-24
**Architect**: Claude Sonnet 4.5

## Executive Summary

This plan details the security architecture for single task retrieval and deletion endpoints, with emphasis on preventing information disclosure through enumeration attacks. The primary architectural challenge is balancing security (no information leakage) with usability (clear error messages). The solution implements defense-in-depth with three layers: JWT authentication, path authorization, and query-level user isolation.

**Key Architectural Decision**: Return 404 (not 403) when a task is not found OR not authorized, preventing attackers from enumerating which tasks exist.

## 1. Scope and Dependencies

### In Scope
- Security review and hardening of existing GET /api/users/{user_id}/tasks/{task_id}
- Security review and hardening of existing DELETE /api/users/{user_id}/tasks/{task_id}
- Comprehensive security test suite for cross-user access attempts
- Information disclosure prevention tests
- Cascade delete verification tests
- Documentation of security patterns

### Out of Scope
- Soft delete functionality (hard delete only)
- Audit logging of deletion events (future feature)
- Batch deletion operations
- Task recovery/undo functionality
- Rate limiting (implemented at API gateway level)

### External Dependencies

| Dependency | Owner | Status | Risk |
|------------|-------|--------|------|
| JWT Middleware | 006-jwt-auth-middleware | Implemented | Low |
| SQLModel Models (Task, TaskTag) | 005-database-foundation | Implemented | Low |
| Database Session Management | 005-database-foundation | Implemented | Low |
| Better Auth JWT Secret | Frontend/DevOps | Configured | Low |
| Neon PostgreSQL Database | DevOps/Cloud | Running | Low |

**Dependency Notes**:
- All dependencies are already implemented and tested
- No blocking dependencies
- JWT middleware provides authentication layer (401 responses)
- Database models include cascade delete relationships

## 2. Key Decisions and Rationale

### Decision 1: Information Disclosure Prevention Strategy

**Context**: When a user attempts to access a task that either doesn't exist or belongs to another user, we must decide what error to return. The naive approach would be:
- 404 if task doesn't exist
- 403 if task exists but belongs to another user

However, this reveals whether a task exists, enabling enumeration attacks.

**Options Considered**:

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **Option A: Return 403 for unauthorized, 404 for non-existent** | Clear error messages, RESTful | Information disclosure, enumeration attacks | REJECTED |
| **Option B: Return 404 for both cases** | No information disclosure, prevents enumeration | Less precise error messages | SELECTED |
| **Option C: Return 403 for both cases** | No information disclosure | Confusing (404 is standard for "not found") | REJECTED |
| **Option D: Random delay + 404** | Prevents timing attacks | Adds latency, complex | REJECTED (over-engineering) |

**Decision**: Option B - Return 404 for both non-existent and unauthorized tasks

**Rationale**:
1. **Security First**: Preventing information disclosure is more important than precise error messages
2. **OWASP Compliance**: Aligns with OWASP guidance on error handling
3. **Simplicity**: Clean implementation without timing attack complexity
4. **User Experience**: From user's perspective, "task not found" is accurate (they can't find it)

**Implementation**:
```python
# Service layer queries with user_id filter
task = session.get(Task, task_id)
if task and task.user_id == user_id:
    return task
return None  # Both cases: non-existent OR unauthorized

# Route layer returns 404
if not task:
    raise HTTPException(status_code=404, detail="Task not found")
```

**Tradeoffs**:
- **Pro**: No information leakage about task existence
- **Pro**: Simple implementation, no timing concerns
- **Con**: Developers might expect 403 for authorization failures
- **Con**: Debugging is slightly harder (can't distinguish causes in logs)

**Mitigation**: Document this pattern clearly, add detailed server-side logging (not exposed to client).

### Decision 2: Cascade Delete Implementation Strategy

**Context**: When deleting a task, associated TaskTag records must also be deleted. We can rely on database cascade delete, explicit application-level delete, or both.

**Options Considered**:

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **Option A: Database CASCADE only** | Simple, atomic, no app code | Relies on DB, less control | REJECTED |
| **Option B: Application-level only** | Full control, framework-agnostic | More code, risk of bugs | REJECTED |
| **Option C: Both (defense-in-depth)** | Redundancy, fail-safe, clear intent | Slightly more code | SELECTED |

**Decision**: Option C - Explicit application cascade + database CASCADE constraint

**Rationale**:
1. **Defense in Depth**: Two layers of protection against orphaned data
2. **Clarity**: Explicit code makes intent clear for maintainers
3. **Control**: Application can log, validate, or extend cascade logic
4. **Safety**: Database CASCADE as backup if application logic fails

**Implementation**:
```python
# Explicit cascade in service layer
task_tags = session.exec(select(TaskTag).where(TaskTag.task_id == task.id)).all()
for tag in task_tags:
    session.delete(tag)
session.delete(task)
session.commit()

# Database-level CASCADE as backup
# ON DELETE CASCADE in foreign key constraint
```

**Tradeoffs**:
- **Pro**: Multiple safety layers prevent orphaned data
- **Pro**: Explicit code is self-documenting
- **Con**: Slight performance overhead (extra DELETE statements)
- **Con**: More code to maintain

**Performance Impact**: Minimal - tags are already loaded for verification, DELETE operations are fast on indexed columns.

### Decision 3: Authorization Check Timing

**Context**: We have two checks: path user_id vs JWT user_id, and task ownership. When should each happen?

**Options Considered**:

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **Option A: All checks in service layer** | Centralized logic | Route layer becomes pass-through | REJECTED |
| **Option B: All checks in route layer** | Security visible at API boundary | Service layer loses context | REJECTED |
| **Option C: Path check in route, ownership in service** | Clear separation of concerns | Two authorization checks | SELECTED |

**Decision**: Option C - Path user_id check in route layer (403), ownership check in service layer (404)

**Rationale**:
1. **Separation of Concerns**: Route handles API-level auth, service handles data-level auth
2. **Performance**: Reject mismatched path user_id before database query
3. **Reusability**: Service layer can be called from different contexts (CLI, background jobs)
4. **Clarity**: Two distinct error codes for two distinct failures

**Implementation Flow**:
```
Request: DELETE /api/users/user-B/tasks/task-X
JWT Token: user-A

1. JWT Middleware: Verify token, extract user-A → request.state.user_id = "user-A"
2. Route Layer: Check path user_id (user-B) != JWT user_id (user-A) → 403 Forbidden
3. [Not reached] Service Layer: Would check task ownership → 404 Not Found

Request: DELETE /api/users/user-A/tasks/task-X (task belongs to user-B)
JWT Token: user-A

1. JWT Middleware: Verify token, extract user-A → request.state.user_id = "user-A"
2. Route Layer: Check path user_id (user-A) == JWT user_id (user-A) → PASS
3. Service Layer: Query task where id=task-X AND user_id=user-A → None → 404 Not Found
```

**Tradeoffs**:
- **Pro**: Early rejection of invalid requests (403 before DB query)
- **Pro**: Service layer remains pure (no HTTP concerns)
- **Con**: Two places to check authorization (complexity)
- **Con**: Must ensure consistent behavior

**Validation**: Comprehensive tests verify both checks work correctly.

### Decision 4: Testing Strategy - Security First

**Context**: These endpoints are security-critical. Traditional testing focuses on happy paths, but we need extensive negative testing.

**Decision**: Implement security test suite with 3 categories:
1. **Authentication Tests** (401): Missing/invalid/expired tokens
2. **Authorization Tests** (403): Path user_id mismatches
3. **Information Disclosure Tests** (404): Cross-user access, non-existent tasks

**Rationale**:
1. **Risk-Based**: Highest risk is security vulnerabilities
2. **OWASP Guidance**: Test for information exposure
3. **Compliance**: Security tests are audit requirements
4. **Confidence**: Comprehensive tests enable safe refactoring

**Test Coverage Target**: 100% for security paths, 95%+ overall

**Implementation**:
```python
# Security Test Suite Structure
tests/
  test_task_get_security.py
    - test_get_task_cross_user_access_returns_404()
    - test_get_task_non_existent_returns_404()
    - test_get_task_response_timing_consistent()
    - test_get_task_path_user_mismatch_returns_403()
    - test_get_task_no_token_returns_401()
  test_task_delete_security.py
    - test_delete_task_cross_user_access_returns_404()
    - test_delete_task_cascade_removes_tags()
    - test_delete_task_idempotent()
```

## 3. Interfaces and API Contracts

### GET /api/users/{user_id}/tasks/{task_id}

**Input Contract**:
```typescript
interface GetTaskRequest {
  path: {
    user_id: UUID;  // Must match JWT sub claim
    task_id: UUID;  // Task identifier
  };
  headers: {
    Authorization: string;  // "Bearer <jwt_token>"
  };
}
```

**Output Contract**:
```typescript
interface GetTaskResponse {
  id: UUID;
  user_id: UUID;
  title: string;           // max 200 chars
  description: string | null;  // max 1000 chars
  completed: boolean;
  priority: "low" | "medium" | "high" | "critical";
  tags: string[];          // Array of tag names
  created_at: string;      // ISO 8601
  updated_at: string;      // ISO 8601
}
```

**Error Taxonomy**:

| Status Code | Error Code | Message | Cause | Client Action |
|-------------|------------|---------|-------|---------------|
| 401 | MISSING_TOKEN | "Authorization header is required" | No JWT token | Redirect to login |
| 401 | TOKEN_EXPIRED | "Token has expired" | Expired JWT | Refresh token |
| 401 | INVALID_TOKEN_SIGNATURE | "Invalid token signature" | Tampered JWT | Redirect to login |
| 403 | FORBIDDEN | "Not authorized to view tasks for this user" | Path user_id != JWT user_id | Show error message |
| 404 | NOT_FOUND | "Task not found" | Non-existent OR unauthorized | Show "task not found" |
| 500 | INTERNAL_ERROR | "Error retrieving task: {detail}" | Server error | Retry, contact support |

**Idempotency**: GET is naturally idempotent (safe, no side effects)

**Caching**: Response can be cached with user-specific cache key

### DELETE /api/users/{user_id}/tasks/{task_id}

**Input Contract**:
```typescript
interface DeleteTaskRequest {
  path: {
    user_id: UUID;  // Must match JWT sub claim
    task_id: UUID;  // Task identifier
  };
  headers: {
    Authorization: string;  // "Bearer <jwt_token>"
  };
}
```

**Output Contract**:
```typescript
interface DeleteTaskResponse {
  message: "Task deleted successfully";
}
```

**Error Taxonomy**:

| Status Code | Error Code | Message | Cause | Client Action |
|-------------|------------|---------|-------|---------------|
| 401 | MISSING_TOKEN | "Authorization header is required" | No JWT token | Redirect to login |
| 401 | TOKEN_EXPIRED | "Token has expired" | Expired JWT | Refresh token |
| 401 | INVALID_TOKEN_SIGNATURE | "Invalid token signature" | Tampered JWT | Redirect to login |
| 403 | FORBIDDEN | "Not authorized to delete tasks for this user" | Path user_id != JWT user_id | Show error message |
| 404 | NOT_FOUND | "Task not found" | Non-existent OR unauthorized | Show "task not found" |
| 500 | INTERNAL_ERROR | "Error deleting task: {detail}" | Server error | Retry, contact support |

**Idempotency**: DELETE is idempotent (second delete returns 404, but no additional side effects)

**Side Effects**:
1. Task record deleted from `tasks` table
2. All TaskTag records deleted from `task_tags` table
3. Database transaction committed atomically

## 4. Non-Functional Requirements (NFRs) and Budgets

### Performance Requirements

| Metric | Target | Measurement | Action if Exceeded |
|--------|--------|-------------|-------------------|
| GET p50 latency | < 50ms | Application metrics | Optimize query |
| GET p95 latency | < 200ms | Application metrics | Add caching |
| GET p99 latency | < 500ms | Application metrics | Investigate outliers |
| DELETE p50 latency | < 100ms | Application metrics | Optimize transaction |
| DELETE p95 latency | < 200ms | Application metrics | Add async processing |
| DELETE p99 latency | < 500ms | Application metrics | Investigate outliers |
| Database query count (GET) | 1 query | SQL logs | Optimize joins |
| Database query count (DELETE) | 2 queries | SQL logs | Acceptable |

**Performance Budget**:
- GET: 200ms total (50ms DB, 50ms serialization, 100ms network/overhead)
- DELETE: 200ms total (100ms DB transaction, 50ms network, 50ms overhead)

**Optimization Strategy**:
1. **Indexing**: Ensure `tasks.id` and `tasks.user_id` are indexed
2. **Query Optimization**: Single query for GET with tag join
3. **Connection Pooling**: Reuse database connections
4. **No N+1 Queries**: Load tags in single query

### Reliability Requirements

| Requirement | Target | Measurement | Strategy |
|-------------|--------|-------------|----------|
| Success Rate (GET) | > 99.9% | Error logs | Retry on transient errors |
| Success Rate (DELETE) | > 99.9% | Error logs | Transaction rollback on failure |
| Database Availability | > 99.95% | Neon metrics | Connection retry logic |
| Data Integrity (CASCADE) | 100% | Verification tests | Explicit + DB cascade |

**Error Budget**: 0.1% error rate = 43 minutes downtime per month

**Degradation Strategy**:
- Database timeout: Return 503 Service Unavailable
- Connection pool exhausted: Queue requests, return 429 if queue full
- Cascade delete failure: Rollback transaction, retry once, then alert

### Security Requirements

| Requirement | Implementation | Verification |
|-------------|---------------|--------------|
| Authentication Required | JWT middleware | Security tests |
| Authorization Verified | Path user_id check + query filter | Security tests |
| No Information Disclosure | 404 for all unauthorized access | Enumeration tests |
| Input Validation | UUID validation on path parameters | Fuzz testing |
| SQL Injection Prevention | Parameterized queries (SQLModel) | SAST scanning |
| Timing Attack Prevention | Consistent query patterns | Timing analysis tests |

**Security Principles**:
1. **Fail Secure**: Deny access by default, explicit allow only
2. **Defense in Depth**: Multiple layers of authorization checks
3. **Least Privilege**: Users can only access their own tasks
4. **Secure Defaults**: 404 for ambiguous cases (not 403)

### Maintainability Requirements

| Requirement | Implementation | Verification |
|-------------|---------------|--------------|
| Code Coverage | > 95% | pytest coverage report |
| Docstring Coverage | 100% for public APIs | Documentation review |
| Type Hints | 100% | mypy static analysis |
| Security Documentation | Detailed comments on security patterns | Architecture review |
| Test Documentation | Security test rationale documented | Test review |

**Code Quality Standards**:
- PEP 8 compliant (enforced by linter)
- Maximum function complexity: 10 (cyclomatic)
- Maximum function length: 50 lines
- Clear variable names (no single letters except loop counters)

## 5. Data Management and Migration

### Source of Truth
- **Primary**: PostgreSQL `tasks` and `task_tags` tables
- **No Cache**: No caching layer for these operations (write-heavy, must be consistent)

### Schema Evolution
Current schema is stable. Future migrations:
- Add `deleted_at` column for soft delete (future feature)
- Add `deletion_reason` column for audit (future feature)

**Migration Strategy**: Alembic migrations managed in `/backend/migrations/`

### Data Retention
- **Hard Delete**: Tasks are permanently deleted (current implementation)
- **Future**: Implement soft delete with 30-day retention before permanent deletion
- **Audit Logs**: (Future) Retain deletion logs for 1 year

### Rollback Strategy
- Database transaction ensures atomic delete (rollback on error)
- No application-level undo (permanent deletion)
- Future: Soft delete enables 30-day recovery window

## 6. Operational Readiness

### Observability

**Logs** (Structured JSON):
```python
logger.info("Task retrieved", extra={
    "user_id": user_id,
    "task_id": task_id,
    "latency_ms": latency,
    "tags_count": len(tags)
})

logger.warning("Unauthorized task access attempt", extra={
    "user_id": user_id,
    "task_id": task_id,
    "requested_user_id": path_user_id
})

logger.info("Task deleted", extra={
    "user_id": user_id,
    "task_id": task_id,
    "tags_deleted": tags_count,
    "latency_ms": latency
})
```

**Metrics** (Prometheus format):
- `task_get_requests_total{status="success|error"}`
- `task_get_latency_seconds{quantile="0.5|0.95|0.99"}`
- `task_delete_requests_total{status="success|error"}`
- `task_delete_latency_seconds{quantile="0.5|0.95|0.99"}`
- `task_delete_cascade_count` (number of tags deleted per task)
- `unauthorized_access_attempts_total` (security monitoring)

**Traces** (OpenTelemetry):
- Span: `GET /api/users/{user_id}/tasks/{task_id}`
  - Child span: Database query
  - Child span: Response serialization
- Span: `DELETE /api/users/{user_id}/tasks/{task_id}`
  - Child span: Tag deletion
  - Child span: Task deletion
  - Child span: Transaction commit

### Alerting

| Alert | Condition | Severity | On-Call Action |
|-------|-----------|----------|----------------|
| High Error Rate | Error rate > 5% for 5 minutes | P2 | Check database health |
| Latency Spike | p95 > 1s for 5 minutes | P3 | Check database performance |
| Security Alert | Unauthorized attempts > 100/min | P2 | Investigate for attack |
| Cascade Delete Failure | Failed deletes > 0 | P1 | Check database constraints |
| Database Timeout | Timeout rate > 1% | P2 | Check connection pool |

**Escalation Path**: On-call engineer → Backend lead → DevOps → Database admin

### Runbooks

**Runbook: High Error Rate on DELETE Endpoint**
1. Check application logs for error patterns
2. Query database for long-running transactions
3. Check database connection pool utilization
4. Verify database CASCADE constraints are intact
5. If database issue: Failover to replica
6. If application issue: Rollback to previous version

**Runbook: Suspected Enumeration Attack**
1. Check metrics for unauthorized_access_attempts spike
2. Identify source IP addresses from logs
3. Verify endpoints return 404 (not 403) for unauthorized access
4. If attack confirmed: Block IP at API gateway
5. Investigate if any information was disclosed

### Deployment Strategy

**Blue-Green Deployment**:
1. Deploy new version to green environment
2. Run smoke tests (including security tests)
3. Switch 10% traffic to green
4. Monitor metrics for 10 minutes
5. If metrics good: Switch 100% traffic
6. If metrics bad: Rollback to blue

**Rollback Criteria**:
- Error rate > 5%
- Latency p95 > 500ms
- Any security test failures

**Feature Flags**: Not needed (no conditional logic)

**Compatibility**: Backward compatible (no schema changes)

## 7. Risk Analysis and Mitigation

### Risk 1: Information Disclosure Through Error Messages
**Likelihood**: Medium (common mistake in implementations)
**Impact**: High (enables enumeration attacks)
**Blast Radius**: All users (attacker can discover all task IDs)
**Mitigation**:
- Return 404 for both non-existent and unauthorized tasks
- Comprehensive security tests verify this behavior
- Code review checklist includes information disclosure check
**Kill Switch**: None needed (no feature flag)

### Risk 2: Orphaned Tags After Failed Deletion
**Likelihood**: Low (database CASCADE + explicit delete)
**Impact**: Medium (data integrity issue, storage waste)
**Blast Radius**: Single task's tags
**Mitigation**:
- Database CASCADE constraint as backup
- Explicit application-level cascade delete
- Transaction rollback on failure
- Daily database integrity check (verify no orphaned tags)
**Kill Switch**: None needed (permanent delete is not optional)

### Risk 3: Performance Degradation on High Load
**Likelihood**: Medium (depends on user growth)
**Impact**: Medium (slow responses, timeouts)
**Blast Radius**: All users during peak load
**Mitigation**:
- Database indexing on id and user_id
- Connection pooling with appropriate limits
- Load testing before production deployment
- Database read replicas for GET operations (future)
**Kill Switch**: Rate limiting at API gateway

### Risk 4: Concurrent Deletion Attempts
**Likelihood**: Low (rare user behavior)
**Impact**: Low (second delete returns 404, no data corruption)
**Blast Radius**: Single user
**Mitigation**:
- DELETE is idempotent by design
- Database transaction isolation prevents race conditions
- Test concurrent deletion scenarios
**Kill Switch**: None needed (handled gracefully)

## 8. Evaluation and Validation

### Definition of Done
- [ ] Security review completed
- [ ] Security test suite passes (100% of security tests)
- [ ] Functional test suite passes (95%+ coverage)
- [ ] Performance tests pass (p95 < 200ms)
- [ ] Code review approved (2 reviewers)
- [ ] Documentation complete (API docs, security notes)
- [ ] Penetration testing complete (no critical findings)
- [ ] Production deployment successful (no rollbacks)

### Output Validation

**Format Validation**:
- GET response matches TaskResponse schema
- DELETE response matches {"message": "..."} schema
- Error responses match standard error format

**Requirements Validation**:
- All acceptance criteria in spec.md verified
- All security test cases pass
- No information disclosure in error messages
- Cascade delete removes all tags

**Safety Validation**:
- No SQL injection vulnerabilities (SAST scan)
- No timing attack vulnerabilities (timing analysis)
- No information leakage (security tests)
- No data integrity issues (cascade delete tests)

### Test Strategy

**Test Pyramid**:
1. **Unit Tests** (60%): Service layer functions
   - test_get_task_by_id_success
   - test_get_task_by_id_not_found
   - test_get_task_by_id_wrong_user
   - test_delete_task_success
   - test_delete_task_not_found
   - test_delete_task_cascade

2. **Integration Tests** (30%): Route + Service + Database
   - test_get_task_endpoint_success
   - test_get_task_endpoint_unauthorized
   - test_delete_task_endpoint_success
   - test_delete_task_endpoint_unauthorized

3. **Security Tests** (10%): Attack scenarios
   - test_get_task_enumeration_prevention
   - test_get_task_timing_consistent
   - test_delete_task_cross_user_prevention
   - test_delete_task_idempotency

**Manual Testing Checklist**:
- [ ] Create task with tags, retrieve via GET, verify tags present
- [ ] Attempt cross-user GET, verify 404 (not 403)
- [ ] Delete task, verify tags deleted from database
- [ ] Attempt to delete same task twice, verify 404 on second attempt
- [ ] Test with invalid UUIDs, verify proper validation errors
- [ ] Test with expired JWT, verify 401 from middleware

## 9. Architectural Decision Records (ADRs)

### ADR-010-001: Information Disclosure Prevention via Consistent 404 Responses

**Status**: Accepted
**Date**: 2025-12-24
**Decision**: Return 404 "Task not found" for both non-existent tasks and unauthorized access attempts
**Context**: Need to prevent enumeration attacks while maintaining usable API
**Consequences**:
- **Positive**: No information leakage about task existence
- **Positive**: Simple implementation, no timing attack surface
- **Negative**: Less precise error messages for developers
- **Mitigation**: Detailed server-side logging for debugging

**Alternatives Considered**:
1. Different errors (403 vs 404): Rejected due to information disclosure
2. Random delays: Rejected as over-engineering
3. Always 403: Rejected as misleading (404 is standard for "not found")

### ADR-010-002: Defense-in-Depth Cascade Delete

**Status**: Accepted
**Date**: 2025-12-24
**Decision**: Implement both application-level explicit cascade delete AND database ON DELETE CASCADE constraint
**Context**: Need to prevent orphaned tags after task deletion
**Consequences**:
- **Positive**: Multiple safety layers, fail-safe design
- **Positive**: Clear intent in application code
- **Negative**: Slight performance overhead (extra DELETE statements)
- **Mitigation**: Tags are already loaded for verification, overhead is minimal

**Alternatives Considered**:
1. Database CASCADE only: Rejected due to lack of control
2. Application-level only: Rejected due to lack of backup safety
3. Both: Accepted for defense-in-depth

### ADR-010-003: Two-Layer Authorization Checks

**Status**: Accepted
**Date**: 2025-12-24
**Decision**: Check path user_id match in route layer (403), check task ownership in service layer (404)
**Context**: Need to balance early rejection with clear separation of concerns
**Consequences**:
- **Positive**: Early rejection saves database queries
- **Positive**: Service layer remains pure, reusable
- **Negative**: Two authorization checks to maintain
- **Mitigation**: Comprehensive tests verify both checks work correctly

**Alternatives Considered**:
1. All checks in service: Rejected, route layer becomes pass-through
2. All checks in route: Rejected, service layer loses context
3. Two layers: Accepted for separation of concerns

## 10. Follow-Up Actions and Risks

### Immediate Actions (This Feature)
1. Review existing implementation for security issues
2. Create comprehensive security test suite
3. Run tests and verify all security requirements met
4. Document security patterns for future features
5. Update API documentation with security notes

### Follow-Up Features
1. Implement soft delete with 30-day recovery window
2. Add audit logging for deletion events
3. Implement batch deletion with transaction safety
4. Add rate limiting for deletion operations
5. Implement undo/restore functionality

### Technical Debt
1. Consider adding database query optimization (caching, read replicas)
2. Consider adding more detailed metrics for cascade delete operations
3. Consider adding automated security scanning in CI/CD pipeline

### Risks After Implementation
- **Risk**: User discovers 404 pattern, still can enumerate (timing attacks)
- **Mitigation**: Ensure consistent query patterns, no timing differences
- **Risk**: Database CASCADE constraint gets dropped during migration
- **Mitigation**: Add migration tests, verify constraints after deploy
- **Risk**: Performance degrades as task count grows
- **Mitigation**: Monitor metrics, add indexing/caching as needed

## Summary

This architecture implements security-focused task retrieval and deletion with emphasis on preventing information disclosure. The key insight is that returning 404 for both non-existent and unauthorized tasks prevents enumeration attacks while maintaining usability.

The defense-in-depth approach (JWT auth → path check → ownership check → cascade delete) ensures multiple layers of protection. Comprehensive security testing verifies these protections work correctly.

The implementation is already mostly complete; this plan focuses on security review, comprehensive testing, and documentation of security patterns for future features.

**Next Steps**: Proceed to tasks.md to break down implementation into testable tasks.
