"""
Security tests for GET /api/users/{user_id}/tasks/{task_id} endpoint.

This module tests security-critical behaviors:
- Information disclosure prevention (404 for unauthorized access, not 403)
- Cross-user access prevention
- Authentication and authorization enforcement
- Response timing consistency (prevent enumeration via timing attacks)
"""

import time
from uuid import uuid4

from fastapi.testclient import TestClient

from models import Task

# ============================================================================
# Successful Retrieval Tests
# ============================================================================


def test_get_task_success_with_tags(
    client: TestClient,
    auth_headers_user_a: dict,
    test_user_a,
    test_task_with_tags: Task,
):
    """
    Test successful task retrieval with tags.

    GIVEN: User A is authenticated and task exists with tags
    WHEN: GET /api/users/{user_id}/tasks/{task_id}
    THEN: Returns 200 OK with task details including tags array
    """
    user, _, _ = test_user_a
    task_id = test_task_with_tags.id

    response = client.get(
        f"/users/{user.id}/tasks/{task_id}", headers=auth_headers_user_a
    )

    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}: {response.json()}"
    )

    data = response.json()
    assert data["id"] == str(task_id)
    assert data["title"] == test_task_with_tags.title
    assert isinstance(data["tags"], list)
    assert len(data["tags"]) == 3
    assert "urgent" in data["tags"]
    assert "work" in data["tags"]
    assert "important" in data["tags"]


def test_get_task_with_no_tags(
    client: TestClient, auth_headers_user_a: dict, test_user_a, test_task_no_tags: Task
):
    """
    Test retrieval of task with no tags.

    GIVEN: User A is authenticated and task exists with no tags
    WHEN: GET /api/users/{user_id}/tasks/{task_id}
    THEN: Returns 200 OK with empty tags array
    """
    user, _, _ = test_user_a
    task_id = test_task_no_tags.id

    response = client.get(
        f"/users/{user.id}/tasks/{task_id}", headers=auth_headers_user_a
    )

    assert response.status_code == 200
    data = response.json()
    assert data["tags"] == []


def test_get_task_response_schema(
    client: TestClient,
    auth_headers_user_a: dict,
    test_user_a,
    test_task_with_tags: Task,
):
    """
    Test that response matches TaskResponse schema exactly.

    GIVEN: User A is authenticated and task exists
    WHEN: GET /api/users/{user_id}/tasks/{task_id}
    THEN: Response contains all required fields with correct types
    """
    user, _, _ = test_user_a
    task_id = test_task_with_tags.id

    response = client.get(
        f"/users/{user.id}/tasks/{task_id}", headers=auth_headers_user_a
    )

    assert response.status_code == 200
    data = response.json()

    # Verify all required fields are present
    required_fields = [
        "id",
        "user_id",
        "title",
        "description",
        "completed",
        "priority",
        "tags",
        "created_at",
        "updated_at",
    ]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"

    # Verify data types
    assert isinstance(data["id"], str)
    assert isinstance(data["user_id"], str)
    assert isinstance(data["title"], str)
    assert isinstance(data["completed"], bool)
    assert isinstance(data["priority"], str)
    assert isinstance(data["tags"], list)
    assert isinstance(data["created_at"], str)
    assert isinstance(data["updated_at"], str)


# ============================================================================
# Information Disclosure Prevention Tests (CRITICAL SECURITY)
# ============================================================================


def test_get_task_non_existent_returns_404(
    client: TestClient, auth_headers_user_a: dict, test_user_a
):
    """
    Test non-existent task returns 404.

    GIVEN: User A is authenticated and task does not exist
    WHEN: GET /api/users/{user_id}/tasks/{non_existent_uuid}
    THEN: Returns 404 Not Found
    """
    user, _, _ = test_user_a
    non_existent_id = uuid4()

    response = client.get(
        f"/users/{user.id}/tasks/{non_existent_id}", headers=auth_headers_user_a
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_get_task_cross_user_access_returns_404_not_403(
    client: TestClient,
    auth_headers_user_a: dict,
    auth_headers_user_b: dict,
    test_user_a,
    test_user_b,
    test_task_user_b: Task,
):
    """
    CRITICAL SECURITY TEST: Cross-user access returns 404 (NOT 403).

    GIVEN: User A is authenticated, task belongs to User B
    WHEN: User A attempts GET /api/users/{user_a_id}/tasks/{user_b_task_id}
    THEN: Returns 404 Not Found (NOT 403 Forbidden)
    AND: No information is disclosed about task existence

    This test verifies the CRITICAL security requirement that prevents
    enumeration attacks by returning the same 404 response for both
    non-existent tasks and unauthorized access.
    """
    user_a, _, _ = test_user_a
    user_b, _, _ = test_user_b
    task_b_id = test_task_user_b.id

    # User A attempts to access User B's task
    response_a = client.get(
        f"/users/{user_a.id}/tasks/{task_b_id}", headers=auth_headers_user_a
    )

    # CRITICAL: Must be 404, not 403
    assert response_a.status_code == 404, (
        f"SECURITY VIOLATION: Cross-user access must return 404 (not 403) to prevent enumeration. "
        f"Got {response_a.status_code}: {response_a.json()}"
    )

    assert response_a.json()["detail"] == "Task not found", (
        "Error message should not distinguish between non-existent and unauthorized"
    )

    # Verify User B can still access their own task (sanity check)
    response_b = client.get(
        f"/users/{user_b.id}/tasks/{task_b_id}", headers=auth_headers_user_b
    )
    assert response_b.status_code == 200, (
        "User B should still be able to access their own task"
    )


def test_get_task_response_timing_consistent(
    client: TestClient, auth_headers_user_a: dict, test_user_a, test_task_user_b: Task
):
    """
    Test response timing consistency to prevent timing attacks.

    GIVEN: User A is authenticated
    WHEN: User A attempts to access non-existent task vs User B's task
    THEN: Response times should be similar (no timing attack surface)

    This test verifies that response times don't leak information about
    whether a task exists.
    """
    user_a, _, _ = test_user_a
    non_existent_id = uuid4()
    user_b_task_id = test_task_user_b.id

    latencies = []

    # Measure time for non-existent task (10 iterations)
    for _ in range(10):
        start = time.perf_counter()
        response1 = client.get(
            f"/users/{user_a.id}/tasks/{non_existent_id}", headers=auth_headers_user_a
        )
        latency1 = time.perf_counter() - start
        latencies.append(("non_existent", latency1))
        assert response1.status_code == 404

    # Measure time for other user's task (10 iterations)
    for _ in range(10):
        start = time.perf_counter()
        response2 = client.get(
            f"/users/{user_a.id}/tasks/{user_b_task_id}", headers=auth_headers_user_a
        )
        latency2 = time.perf_counter() - start
        latencies.append(("other_user", latency2))
        assert response2.status_code == 404

    # Calculate average latencies for each case
    non_existent_avg = sum(l for t, l in latencies if t == "non_existent") / 10
    other_user_avg = sum(l for t, l in latencies if t == "other_user") / 10

    # Times should be similar (within 50ms)
    time_diff = abs(non_existent_avg - other_user_avg)
    assert time_diff < 0.05, (
        f"Timing attack risk: Average response time difference {time_diff * 1000:.2f}ms exceeds 50ms threshold"
    )


# ============================================================================
# Authorization Tests
# ============================================================================


def test_get_task_path_user_mismatch_returns_403(
    client: TestClient, auth_headers_user_a: dict, test_user_a, test_user_b
):
    """
    Test path user_id mismatch returns 403 before DB query.

    GIVEN: User A is authenticated
    WHEN: User A attempts GET /api/users/{user_b_id}/tasks/{any_task_id}
    THEN: Returns 403 Forbidden BEFORE database query

    This test verifies the first layer of defense: path user_id must
    match JWT user_id. This check should happen before any database queries.
    """
    user_a, _, _ = test_user_a
    user_b, _, _ = test_user_b

    response = client.get(
        f"/users/{user_b.id}/tasks/{uuid4()}", headers=auth_headers_user_a
    )

    assert response.status_code == 403
    assert "Not authorized" in response.json()["detail"]


# ============================================================================
# Authentication Tests
# ============================================================================


def test_get_task_no_token_returns_401(
    client: TestClient, test_user_a, test_task_user_a: Task
):
    """
    Test missing JWT token returns 401.

    GIVEN: No JWT token provided
    WHEN: GET /api/users/{user_id}/tasks/{task_id}
    THEN: Returns 401 Unauthorized from middleware
    """
    user, _, _ = test_user_a
    task_id = test_task_user_a.id

    response = client.get(
        f"/users/{user.id}/tasks/{task_id}"
        # No Authorization header
    )

    assert response.status_code == 401
    assert (
        "Authorization" in response.json()["error"]
        or "MISSING_TOKEN" in response.json()["code"]
    )


def test_get_task_invalid_token_returns_401(
    client: TestClient, test_user_a, test_task_user_a: Task
):
    """
    Test invalid JWT token returns 401.

    GIVEN: Invalid JWT token provided
    WHEN: GET /api/users/{user_id}/tasks/{task_id}
    THEN: Returns 401 Unauthorized from middleware
    """
    user, _, _ = test_user_a
    task_id = test_task_user_a.id

    response = client.get(
        f"/users/{user.id}/tasks/{task_id}",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401
    json_response = response.json()
    assert "Invalid" in json_response.get(
        "error", ""
    ) or "INVALID" in json_response.get("code", "")


def test_get_task_expired_token_returns_401(
    client: TestClient, test_user_a, test_task_user_a: Task, generate_expired_jwt
):
    """
    Test expired JWT token returns 401.

    GIVEN: Expired JWT token provided
    WHEN: GET /api/users/{user_id}/tasks/{task_id}
    THEN: Returns 401 Unauthorized from middleware
    """
    user, _, _ = test_user_a
    task_id = test_task_user_a.id
    expired_token = generate_expired_jwt(user_id=str(user.id), email=user.email)

    response = client.get(
        f"/users/{user.id}/tasks/{task_id}",
        headers={"Authorization": f"Bearer {expired_token}"},
    )

    assert response.status_code == 401
    json_response = response.json()
    assert "expired" in json_response.get(
        "error", ""
    ).lower() or "EXPIRED" in json_response.get("code", "")


# ============================================================================
# Input Validation Tests
# ============================================================================


def test_get_task_invalid_uuid_format(
    client: TestClient, auth_headers_user_a: dict, test_user_a
):
    """
    Test invalid UUID format returns 422.

    GIVEN: User A is authenticated
    WHEN: GET /api/users/{user_id}/tasks/{invalid_uuid}
    THEN: Returns 422 Unprocessable Entity (FastAPI validation error)
    """
    user, _, _ = test_user_a

    response = client.get(
        f"/users/{user.id}/tasks/not-a-uuid", headers=auth_headers_user_a
    )

    assert response.status_code == 422
