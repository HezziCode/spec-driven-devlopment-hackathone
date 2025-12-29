# Implementation Tasks: Task Deletion and Single Task Retrieval (Security-Focused)

**Feature ID**: 010-task-delete-get
**Status**: In Progress
**Created**: 2025-12-24
**Branch**: 010-task-delete-get

## Overview

This task list breaks down the implementation of secure single task retrieval and deletion endpoints with emphasis on comprehensive security testing. The implementation is already complete; these tasks focus on security review, testing, and verification.

## Task Breakdown

### Phase 1: Security Review and Analysis

#### Task 1.1: Review Existing Implementation for Security Issues
**Priority**: P0 (Critical)
**Estimated**: 30 minutes
**Status**: ✅ COMPLETE

**Description**: Analyze existing GET and DELETE endpoint implementations to identify security vulnerabilities, particularly information disclosure issues.

**Acceptance Criteria**:
- [x] Review `/backend/routes/tasks.py` lines 86-115 (GET endpoint)
- [x] Review `/backend/routes/tasks.py` lines 184-213 (DELETE endpoint)
- [x] Review `/backend/services/task_service.py` lines 101-116 (get_task_by_id)
- [x] Review `/backend/services/task_service.py` lines 178-199 (delete_task)
- [x] Identify any information disclosure vulnerabilities
- [x] Verify service layer queries include user_id filter
- [x] Verify cascade delete is implemented correctly

**Test Cases**: N/A (analysis task)

**Implementation Notes**:
```python
# Current implementation analysis:
# 1. Routes layer:
#    - Lines 28, 68, 97, 130, 163, 195: Path user_id check (403)
#    - This check happens BEFORE service call (GOOD)
#
# 2. Service layer:
#    - Line 105: task = session.get(Task, task_id)
#    - Line 108: if task and task.user_id == user_id:
#    - This checks ownership AFTER fetching (GOOD)
#    - Returns None for both non-existent and unauthorized (GOOD)
#
# 3. Cascade delete:
#    - Lines 188-193: Explicit tag deletion
#    - This is defense-in-depth (GOOD)
#
# FINDING: Implementation is mostly secure, but needs comprehensive testing
```

**Dependencies**: None

---

#### Task 1.2: Verify Database Cascade Delete Constraints
**Priority**: P1 (High)
**Estimated**: 15 minutes
**Status**: PENDING

**Description**: Verify that database-level CASCADE constraints are properly configured on task_tags.task_id foreign key.

**Acceptance Criteria**:
- [ ] Query database schema to verify ON DELETE CASCADE constraint
- [ ] Verify constraint exists on task_tags.task_id → tasks.id
- [ ] Document constraint status in test setup
- [ ] If missing: Create migration to add constraint (defense-in-depth)

**Test Cases**:
```python
def test_database_cascade_constraint_exists():
    """Verify database has ON DELETE CASCADE constraint."""
    # Query information_schema or equivalent
    # Check task_tags foreign key has CASCADE delete rule
    assert constraint_exists("task_tags", "task_id", "CASCADE")
```

**Implementation Notes**:
```sql
-- Expected constraint:
ALTER TABLE task_tags
ADD CONSTRAINT fk_task_tags_task_id
FOREIGN KEY (task_id) REFERENCES tasks(id)
ON DELETE CASCADE;
```

**Dependencies**: Database connection

---

### Phase 2: Security Test Suite Implementation

#### Task 2.1: Create Security Test Module for GET Endpoint
**Priority**: P0 (Critical)
**Estimated**: 2 hours
**Status**: PENDING

**Description**: Implement comprehensive security test suite for GET /api/users/{user_id}/tasks/{task_id} endpoint, focusing on information disclosure prevention.

**Acceptance Criteria**:
- [ ] Create `/backend/tests/test_task_get_security.py`
- [ ] Implement all 10 security test cases (listed below)
- [ ] All tests pass with 100% success rate
- [ ] Test coverage > 95% for GET endpoint code paths
- [ ] Tests verify 404 (not 403) for unauthorized access

**Test Cases**:

```python
# Test Case 1: Successful retrieval with tags
def test_get_task_success_with_tags(client, auth_headers, test_user, test_task_with_tags):
    """
    GIVEN: User is authenticated and task exists with tags
    WHEN: GET /api/users/{user_id}/tasks/{task_id}
    THEN: Returns 200 OK with task details including tags array
    """
    response = client.get(
        f"/api/users/{test_user.id}/tasks/{test_task_with_tags.id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_task_with_tags.id)
    assert data["title"] == test_task_with_tags.title
    assert isinstance(data["tags"], list)
    assert len(data["tags"]) > 0


# Test Case 2: Non-existent task returns 404
def test_get_task_non_existent_returns_404(client, auth_headers, test_user):
    """
    GIVEN: User is authenticated and task does not exist
    WHEN: GET /api/users/{user_id}/tasks/{non_existent_uuid}
    THEN: Returns 404 Not Found
    """
    non_existent_id = uuid4()
    response = client.get(
        f"/api/users/{test_user.id}/tasks/{non_existent_id}",
        headers=auth_headers
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


# Test Case 3: Cross-user access returns 404 (NOT 403) - CRITICAL SECURITY TEST
def test_get_task_cross_user_access_returns_404_not_403(
    client, auth_headers_user_a, auth_headers_user_b,
    test_user_a, test_user_b, test_task_user_b
):
    """
    GIVEN: User A is authenticated, task belongs to User B
    WHEN: User A attempts GET /api/users/{user_a_id}/tasks/{user_b_task_id}
    THEN: Returns 404 Not Found (NOT 403 Forbidden)
    AND: No information is disclosed about task existence

    This test verifies the CRITICAL security requirement that prevents
    enumeration attacks by returning the same 404 response for both
    non-existent tasks and unauthorized access.
    """
    # User A attempts to access User B's task
    response = client.get(
        f"/api/users/{test_user_a.id}/tasks/{test_task_user_b.id}",
        headers=auth_headers_user_a
    )

    # CRITICAL: Must be 404, not 403
    assert response.status_code == 404, \
        "SECURITY VIOLATION: Cross-user access must return 404 (not 403) to prevent enumeration"
    assert response.json()["detail"] == "Task not found"

    # Verify User B can still access their own task
    response_b = client.get(
        f"/api/users/{test_user_b.id}/tasks/{test_task_user_b.id}",
        headers=auth_headers_user_b
    )
    assert response_b.status_code == 200


# Test Case 4: Path user_id mismatch returns 403 (before DB query)
def test_get_task_path_user_mismatch_returns_403(
    client, auth_headers_user_a, test_user_a, test_user_b
):
    """
    GIVEN: User A is authenticated
    WHEN: User A attempts GET /api/users/{user_b_id}/tasks/{any_task_id}
    THEN: Returns 403 Forbidden BEFORE database query

    This test verifies the first layer of defense: path user_id must
    match JWT user_id. This check should happen before any database queries.
    """
    response = client.get(
        f"/api/users/{test_user_b.id}/tasks/{uuid4()}",
        headers=auth_headers_user_a
    )
    assert response.status_code == 403
    assert "Not authorized" in response.json()["detail"]


# Test Case 5: Missing JWT token returns 401
def test_get_task_no_token_returns_401(client, test_user, test_task):
    """
    GIVEN: No JWT token provided
    WHEN: GET /api/users/{user_id}/tasks/{task_id}
    THEN: Returns 401 Unauthorized from middleware
    """
    response = client.get(
        f"/api/users/{test_user.id}/tasks/{test_task.id}"
        # No Authorization header
    )
    assert response.status_code == 401
    assert "Authorization" in response.json()["error"]


# Test Case 6: Invalid JWT token returns 401
def test_get_task_invalid_token_returns_401(client, test_user, test_task):
    """
    GIVEN: Invalid JWT token provided
    WHEN: GET /api/users/{user_id}/tasks/{task_id}
    THEN: Returns 401 Unauthorized from middleware
    """
    response = client.get(
        f"/api/users/{test_user.id}/tasks/{test_task.id}",
        headers={"Authorization": "Bearer invalid-token"}
    )
    assert response.status_code == 401
    assert "Invalid token" in response.json()["error"]


# Test Case 7: Response timing consistency (prevent timing attacks)
def test_get_task_response_timing_consistent(
    client, auth_headers, test_user, test_task, test_user_b, test_task_user_b
):
    """
    GIVEN: User A is authenticated
    WHEN: User A attempts to access non-existent task vs User B's task
    THEN: Response times should be similar (no timing attack surface)

    This test verifies that response times don't leak information about
    whether a task exists.
    """
    import time

    # Measure time for non-existent task
    start = time.perf_counter()
    response1 = client.get(
        f"/api/users/{test_user.id}/tasks/{uuid4()}",
        headers=auth_headers
    )
    time1 = time.perf_counter() - start
    assert response1.status_code == 404

    # Measure time for other user's task
    start = time.perf_counter()
    response2 = client.get(
        f"/api/users/{test_user.id}/tasks/{test_task_user_b.id}",
        headers=auth_headers
    )
    time2 = time.perf_counter() - start
    assert response2.status_code == 404

    # Times should be similar (within 50ms)
    time_diff = abs(time1 - time2)
    assert time_diff < 0.05, \
        f"Timing attack risk: Response time difference {time_diff}s exceeds threshold"


# Test Case 8: Task with no tags
def test_get_task_with_no_tags(client, auth_headers, test_user, test_task_no_tags):
    """
    GIVEN: User is authenticated and task exists with no tags
    WHEN: GET /api/users/{user_id}/tasks/{task_id}
    THEN: Returns 200 OK with empty tags array
    """
    response = client.get(
        f"/api/users/{test_user.id}/tasks/{test_task_no_tags.id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["tags"] == []


# Test Case 9: Invalid UUID format
def test_get_task_invalid_uuid_format(client, auth_headers, test_user):
    """
    GIVEN: User is authenticated
    WHEN: GET /api/users/{user_id}/tasks/{invalid_uuid}
    THEN: Returns 422 Unprocessable Entity (FastAPI validation error)
    """
    response = client.get(
        f"/api/users/{test_user.id}/tasks/not-a-uuid",
        headers=auth_headers
    )
    assert response.status_code == 422


# Test Case 10: Response schema validation
def test_get_task_response_schema(client, auth_headers, test_user, test_task_with_tags):
    """
    GIVEN: User is authenticated and task exists
    WHEN: GET /api/users/{user_id}/tasks/{task_id}
    THEN: Response matches TaskResponse schema exactly
    """
    response = client.get(
        f"/api/users/{test_user.id}/tasks/{test_task_with_tags.id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()

    # Verify all required fields
    required_fields = ["id", "user_id", "title", "description", "completed",
                      "priority", "tags", "created_at", "updated_at"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"

    # Verify data types
    assert isinstance(data["id"], str)
    assert isinstance(data["completed"], bool)
    assert isinstance(data["priority"], str)
    assert isinstance(data["tags"], list)
```

**Dependencies**: Task 1.1, Test fixtures

---

#### Task 2.2: Create Security Test Module for DELETE Endpoint
**Priority**: P0 (Critical)
**Estimated**: 2 hours
**Status**: PENDING

**Description**: Implement comprehensive security test suite for DELETE /api/users/{user_id}/tasks/{task_id} endpoint, focusing on cascade delete verification and information disclosure prevention.

**Acceptance Criteria**:
- [ ] Create `/backend/tests/test_task_delete_security.py`
- [ ] Implement all 12 security test cases (listed below)
- [ ] All tests pass with 100% success rate
- [ ] Test coverage > 95% for DELETE endpoint code paths
- [ ] Tests verify cascade delete removes all tags

**Test Cases**:

```python
# Test Case 1: Successful deletion with cascade
def test_delete_task_success_with_cascade(
    client, auth_headers, test_user, test_task_with_tags, session
):
    """
    GIVEN: User is authenticated and task exists with tags
    WHEN: DELETE /api/users/{user_id}/tasks/{task_id}
    THEN: Returns 200 OK, task and all tags are deleted from database
    """
    task_id = test_task_with_tags.id

    # Verify tags exist before deletion
    tags_before = session.exec(
        select(TaskTag).where(TaskTag.task_id == task_id)
    ).all()
    assert len(tags_before) > 0, "Test setup: task should have tags"

    # Delete task
    response = client.delete(
        f"/api/users/{test_user.id}/tasks/{task_id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Task deleted successfully"

    # Verify task deleted
    task_after = session.get(Task, task_id)
    assert task_after is None, "Task should be deleted from database"

    # Verify tags deleted (cascade)
    tags_after = session.exec(
        select(TaskTag).where(TaskTag.task_id == task_id)
    ).all()
    assert len(tags_after) == 0, "All tags should be deleted (cascade)"


# Test Case 2: Non-existent task returns 404
def test_delete_task_non_existent_returns_404(client, auth_headers, test_user):
    """
    GIVEN: User is authenticated and task does not exist
    WHEN: DELETE /api/users/{user_id}/tasks/{non_existent_uuid}
    THEN: Returns 404 Not Found
    """
    non_existent_id = uuid4()
    response = client.delete(
        f"/api/users/{test_user.id}/tasks/{non_existent_id}",
        headers=auth_headers
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


# Test Case 3: Cross-user deletion returns 404 (NOT 403) - CRITICAL SECURITY TEST
def test_delete_task_cross_user_access_returns_404_not_403(
    client, auth_headers_user_a, auth_headers_user_b,
    test_user_a, test_user_b, test_task_user_b, session
):
    """
    GIVEN: User A is authenticated, task belongs to User B
    WHEN: User A attempts DELETE /api/users/{user_a_id}/tasks/{user_b_task_id}
    THEN: Returns 404 Not Found (NOT 403 Forbidden)
    AND: User B's task is NOT deleted
    AND: No information is disclosed about task existence

    This test verifies the CRITICAL security requirement that prevents
    enumeration attacks and ensures data isolation.
    """
    task_id = test_task_user_b.id

    # User A attempts to delete User B's task
    response = client.delete(
        f"/api/users/{test_user_a.id}/tasks/{task_id}",
        headers=auth_headers_user_a
    )

    # CRITICAL: Must be 404, not 403
    assert response.status_code == 404, \
        "SECURITY VIOLATION: Cross-user deletion must return 404 (not 403) to prevent enumeration"
    assert response.json()["detail"] == "Task not found"

    # Verify User B's task still exists
    task_still_exists = session.get(Task, task_id)
    assert task_still_exists is not None, \
        "SECURITY VIOLATION: User A should not be able to delete User B's task"

    # Verify User B can still delete their own task
    response_b = client.delete(
        f"/api/users/{test_user_b.id}/tasks/{task_id}",
        headers=auth_headers_user_b
    )
    assert response_b.status_code == 200


# Test Case 4: Path user_id mismatch returns 403 (before DB query)
def test_delete_task_path_user_mismatch_returns_403(
    client, auth_headers_user_a, test_user_a, test_user_b
):
    """
    GIVEN: User A is authenticated
    WHEN: User A attempts DELETE /api/users/{user_b_id}/tasks/{any_task_id}
    THEN: Returns 403 Forbidden BEFORE database query
    """
    response = client.delete(
        f"/api/users/{test_user_b.id}/tasks/{uuid4()}",
        headers=auth_headers_user_a
    )
    assert response.status_code == 403
    assert "Not authorized" in response.json()["detail"]


# Test Case 5: Missing JWT token returns 401
def test_delete_task_no_token_returns_401(client, test_user, test_task):
    """
    GIVEN: No JWT token provided
    WHEN: DELETE /api/users/{user_id}/tasks/{task_id}
    THEN: Returns 401 Unauthorized from middleware
    """
    response = client.delete(
        f"/api/users/{test_user.id}/tasks/{test_task.id}"
        # No Authorization header
    )
    assert response.status_code == 401
    assert "Authorization" in response.json()["error"]


# Test Case 6: Idempotent deletion (second delete returns 404)
def test_delete_task_idempotent(client, auth_headers, test_user, test_task):
    """
    GIVEN: User is authenticated and task exists
    WHEN: DELETE task twice
    THEN: First returns 200 OK, second returns 404 Not Found
    AND: No errors occur (idempotent operation)
    """
    task_id = test_task.id

    # First deletion
    response1 = client.delete(
        f"/api/users/{test_user.id}/tasks/{task_id}",
        headers=auth_headers
    )
    assert response1.status_code == 200

    # Second deletion (idempotent)
    response2 = client.delete(
        f"/api/users/{test_user.id}/tasks/{task_id}",
        headers=auth_headers
    )
    assert response2.status_code == 404
    assert response2.json()["detail"] == "Task not found"


# Test Case 7: Cascade delete with multiple tags
def test_delete_task_cascade_multiple_tags(
    client, auth_headers, test_user, session
):
    """
    GIVEN: Task with 5 tags
    WHEN: DELETE task
    THEN: All 5 tags are deleted from database
    """
    # Create task with 5 tags
    task = Task(
        title="Task with many tags",
        user_id=test_user.id,
        priority="medium"
    )
    session.add(task)
    session.flush()

    tag_names = ["tag1", "tag2", "tag3", "tag4", "tag5"]
    for tag_name in tag_names:
        tag = TaskTag(task_id=task.id, tag_name=tag_name)
        session.add(tag)
    session.commit()

    # Verify 5 tags exist
    tags_before = session.exec(
        select(TaskTag).where(TaskTag.task_id == task.id)
    ).all()
    assert len(tags_before) == 5

    # Delete task
    response = client.delete(
        f"/api/users/{test_user.id}/tasks/{task.id}",
        headers=auth_headers
    )
    assert response.status_code == 200

    # Verify all 5 tags deleted
    tags_after = session.exec(
        select(TaskTag).where(TaskTag.task_id == task.id)
    ).all()
    assert len(tags_after) == 0, "All 5 tags should be deleted"


# Test Case 8: Task with no tags (edge case)
def test_delete_task_no_tags(
    client, auth_headers, test_user, test_task_no_tags, session
):
    """
    GIVEN: Task with no tags
    WHEN: DELETE task
    THEN: Task deleted successfully (no cascade needed)
    """
    task_id = test_task_no_tags.id

    response = client.delete(
        f"/api/users/{test_user.id}/tasks/{task_id}",
        headers=auth_headers
    )
    assert response.status_code == 200

    # Verify task deleted
    task_after = session.get(Task, task_id)
    assert task_after is None


# Test Case 9: Concurrent deletion attempts
def test_delete_task_concurrent_attempts(
    client, auth_headers, test_user, test_task, session
):
    """
    GIVEN: Task exists
    WHEN: Two concurrent DELETE requests
    THEN: One succeeds (200), one returns 404
    AND: No database errors occur (transaction safety)
    """
    import concurrent.futures
    import threading

    task_id = test_task.id
    results = []

    def delete_task():
        response = client.delete(
            f"/api/users/{test_user.id}/tasks/{task_id}",
            headers=auth_headers
        )
        return response.status_code

    # Execute two deletions concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(delete_task) for _ in range(2)]
        results = [f.result() for f in futures]

    # One should be 200, one should be 404 (order doesn't matter)
    assert 200 in results, "One deletion should succeed"
    assert 404 in results, "One deletion should get 404"

    # Verify task is deleted
    task_after = session.get(Task, task_id)
    assert task_after is None


# Test Case 10: Response timing consistency
def test_delete_task_response_timing_consistent(
    client, auth_headers, test_user, test_task, test_user_b, test_task_user_b
):
    """
    GIVEN: User A is authenticated
    WHEN: User A attempts to delete non-existent task vs User B's task
    THEN: Response times should be similar (no timing attack surface)
    """
    import time

    # Measure time for non-existent task
    start = time.perf_counter()
    response1 = client.delete(
        f"/api/users/{test_user.id}/tasks/{uuid4()}",
        headers=auth_headers
    )
    time1 = time.perf_counter() - start
    assert response1.status_code == 404

    # Measure time for other user's task
    start = time.perf_counter()
    response2 = client.delete(
        f"/api/users/{test_user.id}/tasks/{test_task_user_b.id}",
        headers=auth_headers
    )
    time2 = time.perf_counter() - start
    assert response2.status_code == 404

    # Times should be similar (within 50ms)
    time_diff = abs(time1 - time2)
    assert time_diff < 0.05, \
        f"Timing attack risk: Response time difference {time_diff}s exceeds threshold"


# Test Case 11: Invalid UUID format
def test_delete_task_invalid_uuid_format(client, auth_headers, test_user):
    """
    GIVEN: User is authenticated
    WHEN: DELETE /api/users/{user_id}/tasks/{invalid_uuid}
    THEN: Returns 422 Unprocessable Entity (FastAPI validation error)
    """
    response = client.delete(
        f"/api/users/{test_user.id}/tasks/not-a-uuid",
        headers=auth_headers
    )
    assert response.status_code == 422


# Test Case 12: Verify no orphaned tags after deletion
def test_delete_task_no_orphaned_tags(
    client, auth_headers, test_user, test_task_with_tags, session
):
    """
    GIVEN: Task with tags exists
    WHEN: DELETE task
    THEN: Database query confirms no orphaned TaskTag records exist

    This test provides additional verification that cascade delete works.
    """
    task_id = test_task_with_tags.id

    # Get tag IDs before deletion
    tags_before = session.exec(
        select(TaskTag).where(TaskTag.task_id == task_id)
    ).all()
    tag_ids_before = [tag.id for tag in tags_before]
    assert len(tag_ids_before) > 0

    # Delete task
    response = client.delete(
        f"/api/users/{test_user.id}/tasks/{task_id}",
        headers=auth_headers
    )
    assert response.status_code == 200

    # Verify tags deleted by ID (not just task_id filter)
    for tag_id in tag_ids_before:
        orphaned_tag = session.get(TaskTag, tag_id)
        assert orphaned_tag is None, f"Orphaned tag found: {tag_id}"

    # Verify no tags with this task_id exist
    orphaned_tags = session.exec(
        select(TaskTag).where(TaskTag.task_id == task_id)
    ).all()
    assert len(orphaned_tags) == 0
```

**Dependencies**: Task 1.1, Test fixtures

---

#### Task 2.3: Create Test Fixtures for Security Tests
**Priority**: P1 (High)
**Estimated**: 1 hour
**Status**: PENDING

**Description**: Create pytest fixtures to support security testing, including multiple users, tasks with various states, and authentication headers.

**Acceptance Criteria**:
- [ ] Update `/backend/tests/conftest.py` with security test fixtures
- [ ] Create fixtures for multiple users (user_a, user_b)
- [ ] Create fixtures for tasks with different ownership
- [ ] Create fixtures for authentication headers (per user)
- [ ] Create fixtures for tasks with/without tags
- [ ] All fixtures are properly isolated (no test pollution)

**Test Cases**: N/A (fixture creation)

**Implementation Notes**:
```python
# Add to conftest.py

@pytest.fixture
def test_user_a(session):
    """Create test user A."""
    user = User(
        username="user_a",
        email="user_a@example.com",
        password_hash="hashed_password_a"
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def test_user_b(session):
    """Create test user B."""
    user = User(
        username="user_b",
        email="user_b@example.com",
        password_hash="hashed_password_b"
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def auth_headers_user_a(test_user_a):
    """Create auth headers for user A."""
    token = create_test_jwt_token(test_user_a.id, test_user_a.email)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_user_b(test_user_b):
    """Create auth headers for user B."""
    token = create_test_jwt_token(test_user_b.id, test_user_b.email)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_task_user_b(session, test_user_b):
    """Create test task owned by user B."""
    task = Task(
        title="User B's task",
        description="This task belongs to user B",
        user_id=test_user_b.id,
        priority="medium"
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@pytest.fixture
def test_task_with_tags(session, test_user):
    """Create test task with 3 tags."""
    task = Task(
        title="Task with tags",
        user_id=test_user.id,
        priority="high"
    )
    session.add(task)
    session.flush()

    for tag_name in ["urgent", "work", "important"]:
        tag = TaskTag(task_id=task.id, tag_name=tag_name)
        session.add(tag)

    session.commit()
    session.refresh(task)
    return task


@pytest.fixture
def test_task_no_tags(session, test_user):
    """Create test task with no tags."""
    task = Task(
        title="Task without tags",
        user_id=test_user.id,
        priority="low"
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def create_test_jwt_token(user_id: str, email: str) -> str:
    """Create JWT token for testing."""
    from jose import jwt
    import os

    secret = os.getenv("BETTER_AUTH_SECRET")
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, secret, algorithm="HS256")
```

**Dependencies**: None

---

### Phase 3: Implementation Verification

#### Task 3.1: Run Security Test Suite and Fix Issues
**Priority**: P0 (Critical)
**Estimated**: 2 hours
**Status**: PENDING

**Description**: Execute the complete security test suite and fix any identified issues in the implementation.

**Acceptance Criteria**:
- [ ] Run all GET endpoint security tests
- [ ] Run all DELETE endpoint security tests
- [ ] All tests pass (100% success rate)
- [ ] Fix any identified security vulnerabilities
- [ ] Document any changes made to implementation
- [ ] No 403 responses for cross-user access (must be 404)

**Test Cases**:
```bash
# Run GET security tests
pytest backend/tests/test_task_get_security.py -v

# Run DELETE security tests
pytest backend/tests/test_task_delete_security.py -v

# Run all security tests
pytest backend/tests/ -k "security" -v

# Run with coverage
pytest backend/tests/ -k "security" --cov=backend/routes --cov=backend/services --cov-report=html
```

**Implementation Notes**:
- If tests fail, review error messages carefully
- Check if 403 is returned instead of 404 (information disclosure)
- Verify cascade delete is working correctly
- Ensure timing consistency between responses

**Dependencies**: Task 2.1, Task 2.2, Task 2.3

---

#### Task 3.2: Verify Database Cascade Delete Works
**Priority**: P1 (High)
**Estimated**: 30 minutes
**Status**: PENDING

**Description**: Manually verify that cascade delete works correctly by inspecting database after deletions.

**Acceptance Criteria**:
- [ ] Create task with 10 tags via API
- [ ] Query database to confirm 10 TaskTag records exist
- [ ] Delete task via API
- [ ] Query database to confirm 0 TaskTag records remain
- [ ] No orphaned tags found in database
- [ ] Document verification process

**Test Cases**:
```sql
-- Before deletion
SELECT COUNT(*) FROM task_tags WHERE task_id = '<task_uuid>';
-- Expected: 10

-- After deletion
SELECT COUNT(*) FROM task_tags WHERE task_id = '<task_uuid>';
-- Expected: 0

-- Check for orphaned tags
SELECT tt.* FROM task_tags tt
LEFT JOIN tasks t ON tt.task_id = t.id
WHERE t.id IS NULL;
-- Expected: 0 rows
```

**Implementation Notes**:
```python
# Script to verify cascade delete
def verify_cascade_delete():
    # Create task with 10 tags
    response = client.post("/api/users/{user_id}/tasks", json={
        "title": "Test cascade",
        "tags": [f"tag{i}" for i in range(10)]
    })
    task_id = response.json()["id"]

    # Verify tags exist
    tags = session.exec(select(TaskTag).where(TaskTag.task_id == task_id)).all()
    assert len(tags) == 10

    # Delete task
    client.delete(f"/api/users/{user_id}/tasks/{task_id}")

    # Verify tags deleted
    tags_after = session.exec(select(TaskTag).where(TaskTag.task_id == task_id)).all()
    assert len(tags_after) == 0
```

**Dependencies**: Task 3.1

---

### Phase 4: Performance and Load Testing

#### Task 4.1: Performance Testing for GET Endpoint
**Priority**: P2 (Medium)
**Estimated**: 1 hour
**Status**: PENDING

**Description**: Verify GET endpoint meets performance requirements (p95 < 200ms).

**Acceptance Criteria**:
- [ ] Create performance test script
- [ ] Test with 100 concurrent requests
- [ ] Measure p50, p95, p99 latencies
- [ ] Verify p95 < 200ms
- [ ] Document results and any optimizations

**Test Cases**:
```python
def test_get_task_performance(client, auth_headers, test_user, test_task_with_tags):
    """
    GIVEN: Task exists with tags
    WHEN: 100 concurrent GET requests
    THEN: p95 latency < 200ms
    """
    import time
    import concurrent.futures

    latencies = []

    def get_task():
        start = time.perf_counter()
        response = client.get(
            f"/api/users/{test_user.id}/tasks/{test_task_with_tags.id}",
            headers=auth_headers
        )
        latency = (time.perf_counter() - start) * 1000  # Convert to ms
        return latency, response.status_code

    # 100 concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(get_task) for _ in range(100)]
        results = [f.result() for f in futures]

    latencies = [r[0] for r in results if r[1] == 200]

    # Calculate percentiles
    latencies.sort()
    p50 = latencies[len(latencies) // 2]
    p95 = latencies[int(len(latencies) * 0.95)]
    p99 = latencies[int(len(latencies) * 0.99)]

    print(f"Performance: p50={p50:.2f}ms, p95={p95:.2f}ms, p99={p99:.2f}ms")

    assert p95 < 200, f"p95 latency {p95:.2f}ms exceeds 200ms threshold"
```

**Dependencies**: Task 3.1

---

#### Task 4.2: Performance Testing for DELETE Endpoint
**Priority**: P2 (Medium)
**Estimated**: 1 hour
**Status**: PENDING

**Description**: Verify DELETE endpoint meets performance requirements (p95 < 200ms).

**Acceptance Criteria**:
- [ ] Create performance test script
- [ ] Test with 100 tasks (deleted sequentially to avoid conflicts)
- [ ] Measure p50, p95, p99 latencies
- [ ] Verify p95 < 200ms
- [ ] Document results and any optimizations

**Test Cases**:
```python
def test_delete_task_performance(client, auth_headers, test_user, session):
    """
    GIVEN: 100 tasks with tags
    WHEN: DELETE each task sequentially
    THEN: p95 latency < 200ms
    """
    import time

    # Create 100 tasks with tags
    task_ids = []
    for i in range(100):
        task = Task(
            title=f"Task {i}",
            user_id=test_user.id,
            priority="medium"
        )
        session.add(task)
        session.flush()

        for j in range(3):  # 3 tags each
            tag = TaskTag(task_id=task.id, tag_name=f"tag{j}")
            session.add(tag)

        task_ids.append(task.id)
    session.commit()

    # Delete all tasks and measure latency
    latencies = []
    for task_id in task_ids:
        start = time.perf_counter()
        response = client.delete(
            f"/api/users/{test_user.id}/tasks/{task_id}",
            headers=auth_headers
        )
        latency = (time.perf_counter() - start) * 1000  # Convert to ms
        if response.status_code == 200:
            latencies.append(latency)

    # Calculate percentiles
    latencies.sort()
    p50 = latencies[len(latencies) // 2]
    p95 = latencies[int(len(latencies) * 0.95)]
    p99 = latencies[int(len(latencies) * 0.99)]

    print(f"Performance: p50={p50:.2f}ms, p95={p95:.2f}ms, p99={p99:.2f}ms")

    assert p95 < 200, f"p95 latency {p95:.2f}ms exceeds 200ms threshold"
```

**Dependencies**: Task 3.1

---

### Phase 5: Documentation and Deployment

#### Task 5.1: Update API Documentation
**Priority**: P2 (Medium)
**Estimated**: 30 minutes
**Status**: PENDING

**Description**: Update API documentation to document security behavior (404 for unauthorized access).

**Acceptance Criteria**:
- [ ] Update OpenAPI/Swagger docs for GET endpoint
- [ ] Update OpenAPI/Swagger docs for DELETE endpoint
- [ ] Document security pattern (404 vs 403)
- [ ] Add examples of error responses
- [ ] Document cascade delete behavior

**Implementation Notes**:
```python
# Add to route docstrings

@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_user_task(...):
    """
    Get a specific task for the authenticated user.

    Security Note:
    - Returns 404 for both non-existent tasks AND unauthorized access
    - This prevents information disclosure about task existence
    - Path user_id must match JWT user_id (403 if mismatch)

    Args:
        user_id: User ID from path (must match JWT)
        task_id: Task ID to retrieve
        current_user_id: User ID from JWT token
        session: Database session

    Returns:
        Task details including tags array

    Raises:
        401: Missing or invalid JWT token
        403: Path user_id doesn't match JWT user_id
        404: Task not found OR unauthorized access (no distinction)
    """
```

**Dependencies**: Task 3.1

---

#### Task 5.2: Create Security Documentation
**Priority**: P2 (Medium)
**Estimated**: 1 hour
**Status**: PENDING

**Description**: Document security patterns and best practices for future features.

**Acceptance Criteria**:
- [ ] Create `/backend/docs/security-patterns.md`
- [ ] Document information disclosure prevention pattern
- [ ] Document cascade delete pattern
- [ ] Document two-layer authorization pattern
- [ ] Include code examples and test cases
- [ ] Add to project documentation index

**Implementation Notes**:
```markdown
# Security Patterns for Task API

## Information Disclosure Prevention

**Problem**: Returning different errors (403 vs 404) reveals whether a resource exists.

**Solution**: Return 404 for both non-existent and unauthorized resources.

**Implementation**:
1. Check path user_id matches JWT user_id (403 if not)
2. Query resource with user_id filter
3. Return 404 if query returns None (covers both cases)

**Example**: See test_task_get_security.py::test_get_task_cross_user_access_returns_404_not_403

## Cascade Delete Pattern

**Problem**: Deleting parent resource without cleaning up child resources creates orphaned data.

**Solution**: Defense-in-depth with application-level and database-level cascade delete.

**Implementation**:
1. Explicit child deletion in service layer
2. Database ON DELETE CASCADE as backup
3. Transaction ensures atomic operation

**Example**: See task_service.py::delete_task()
```

**Dependencies**: Task 3.1

---

#### Task 5.3: Run Full Test Suite
**Priority**: P1 (High)
**Estimated**: 30 minutes
**Status**: PENDING

**Description**: Run complete test suite (unit, integration, security) and verify 95%+ coverage.

**Acceptance Criteria**:
- [ ] Run all backend tests
- [ ] All tests pass (100% success rate)
- [ ] Test coverage > 95% for routes and services
- [ ] Generate coverage report
- [ ] Document any uncovered code paths

**Test Cases**:
```bash
# Run all tests
pytest backend/tests/ -v

# Run with coverage
pytest backend/tests/ --cov=backend/routes --cov=backend/services --cov=backend/middleware --cov-report=html --cov-report=term

# Check coverage percentage
coverage report --fail-under=95
```

**Implementation Notes**:
- Aim for 100% coverage of security-critical code paths
- Document any intentionally uncovered code (e.g., error handlers)
- Ensure all edge cases are tested

**Dependencies**: All previous tasks

---

#### Task 5.4: Deployment Preparation
**Priority**: P1 (High)
**Estimated**: 30 minutes
**Status**: PENDING

**Description**: Prepare for deployment by verifying environment configuration and creating deployment checklist.

**Acceptance Criteria**:
- [ ] Verify BETTER_AUTH_SECRET is configured
- [ ] Verify database connection works
- [ ] Create deployment checklist
- [ ] Document rollback procedure
- [ ] Create monitoring dashboard (if applicable)

**Implementation Notes**:
```markdown
# Deployment Checklist

## Pre-Deployment
- [ ] All tests pass (100%)
- [ ] Security tests pass (100%)
- [ ] Performance tests pass (p95 < 200ms)
- [ ] Code review approved (2 reviewers)
- [ ] BETTER_AUTH_SECRET configured in production
- [ ] Database migrations applied

## Deployment
- [ ] Deploy to staging
- [ ] Run smoke tests on staging
- [ ] Deploy to production (blue-green)
- [ ] Monitor error rates for 10 minutes
- [ ] Monitor latency metrics for 10 minutes

## Post-Deployment
- [ ] Verify endpoints return correct responses
- [ ] Verify security behavior (404 for unauthorized)
- [ ] Verify cascade delete works
- [ ] Update API documentation
- [ ] Notify team of deployment

## Rollback Procedure
If error rate > 5% or p95 latency > 500ms:
1. Switch traffic back to previous version
2. Investigate issues in logs
3. Fix and redeploy
```

**Dependencies**: Task 5.3

---

## Task Summary

| Phase | Tasks | Estimated Time | Priority |
|-------|-------|----------------|----------|
| Phase 1: Security Review | 2 tasks | 45 minutes | P0-P1 |
| Phase 2: Security Tests | 3 tasks | 5 hours | P0-P1 |
| Phase 3: Verification | 2 tasks | 2.5 hours | P0-P1 |
| Phase 4: Performance | 2 tasks | 2 hours | P2 |
| Phase 5: Documentation | 4 tasks | 3 hours | P1-P2 |
| **Total** | **13 tasks** | **13.25 hours** | |

## Critical Path
1. Task 1.1 (Security Review) → Task 2.3 (Fixtures) → Task 2.1 (GET Tests) → Task 2.2 (DELETE Tests) → Task 3.1 (Fix Issues) → Task 5.3 (Full Test Suite) → Task 5.4 (Deployment)

## Testing Checklist

### Security Tests (Must Pass)
- [ ] Cross-user GET access returns 404 (not 403)
- [ ] Cross-user DELETE access returns 404 (not 403)
- [ ] Path user_id mismatch returns 403 before DB query
- [ ] Missing JWT returns 401
- [ ] Invalid JWT returns 401
- [ ] Response timing is consistent (no timing attacks)
- [ ] Cascade delete removes all tags
- [ ] No orphaned tags after deletion
- [ ] DELETE is idempotent (second delete returns 404)

### Functional Tests (Must Pass)
- [ ] GET returns task with tags array
- [ ] DELETE returns success message
- [ ] Task with no tags works correctly
- [ ] Task with maximum tags (10) works correctly
- [ ] Invalid UUID format returns 422
- [ ] Response schemas match specification

### Performance Tests (Must Pass)
- [ ] GET p95 latency < 200ms
- [ ] DELETE p95 latency < 200ms
- [ ] Database queries are optimized

## Success Metrics
- **Security**: 100% of security tests pass, no information disclosure
- **Functionality**: 100% of functional tests pass
- **Performance**: p95 latency < 200ms for both endpoints
- **Coverage**: > 95% test coverage
- **Quality**: Code review approved, documentation complete

## Risks and Mitigation
- **Risk**: Security tests reveal information disclosure vulnerability
  - **Mitigation**: Fix immediately, verify with additional tests
- **Risk**: Cascade delete fails in edge cases
  - **Mitigation**: Comprehensive testing, database constraints as backup
- **Risk**: Performance degrades under load
  - **Mitigation**: Database indexing, connection pooling, load testing

## Next Steps
1. Execute Task 1.1 (Security Review) - COMPLETE
2. Execute Task 2.3 (Create Test Fixtures)
3. Execute Task 2.1 (GET Security Tests)
4. Execute Task 2.2 (DELETE Security Tests)
5. Execute Task 3.1 (Run Tests and Fix Issues)
6. Complete remaining tasks in sequence
