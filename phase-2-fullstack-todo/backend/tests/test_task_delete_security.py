"""
Security tests for DELETE /api/users/{user_id}/tasks/{task_id} endpoint.

This module tests security-critical behaviors:
- Information disclosure prevention (404 for unauthorized access, not 403)
- Cross-user deletion prevention
- Cascade delete verification (tags are deleted)
- Authentication and authorization enforcement
- Idempotency and response timing consistency
"""

import time
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from models import Task, TaskTag

# ============================================================================
# Successful Deletion Tests
# ============================================================================


def test_delete_task_success_with_cascade(
    client: TestClient,
    auth_headers_user_a: dict,
    test_user_a,
    test_task_with_tags: Task,
    session: Session,
):
    """
    Test successful task deletion with cascade delete of tags.

    GIVEN: User A is authenticated and task exists with tags
    WHEN: DELETE /api/users/{user_id}/tasks/{task_id}
    THEN: Returns 200 OK, task and all tags are deleted from database
    """
    user, _, _ = test_user_a
    task_id = test_task_with_tags.id

    # Verify tags exist before deletion
    tags_before = session.exec(select(TaskTag).where(TaskTag.task_id == task_id)).all()
    assert len(tags_before) > 0, "Test setup: task should have tags"

    # Delete task
    response = client.delete(
        f"/users/{user.id}/tasks/{task_id}", headers=auth_headers_user_a
    )

    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}: {response.json()}"
    )
    assert response.json()["message"] == "Task deleted successfully"

    # Verify task deleted
    task_after = session.get(Task, task_id)
    assert task_after is None, "Task should be deleted from database"

    # Verify tags deleted (cascade)
    tags_after = session.exec(select(TaskTag).where(TaskTag.task_id == task_id)).all()
    assert len(tags_after) == 0, "All tags should be deleted (cascade)"


def test_delete_task_no_tags(
    client: TestClient,
    auth_headers_user_a: dict,
    test_user_a,
    test_task_no_tags: Task,
    session: Session,
):
    """
    Test deletion of task with no tags.

    GIVEN: Task with no tags
    WHEN: DELETE task
    THEN: Task deleted successfully (no cascade needed)
    """
    user, _, _ = test_user_a
    task_id = test_task_no_tags.id

    response = client.delete(
        f"/users/{user.id}/tasks/{task_id}", headers=auth_headers_user_a
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Task deleted successfully"

    # Verify task deleted
    task_after = session.get(Task, task_id)
    assert task_after is None


def test_delete_task_cascade_multiple_tags(
    client: TestClient, auth_headers_user_a: dict, test_user_a, session: Session
):
    """
    Test cascade delete with multiple tags (5 tags).

    GIVEN: Task with 5 tags
    WHEN: DELETE task
    THEN: All 5 tags are deleted from database
    """
    user, _, _ = test_user_a

    # Create task with 5 tags
    task = Task(title="Task with many tags", user_id=user.id, priority="medium")
    session.add(task)
    session.flush()

    tag_names = ["tag1", "tag2", "tag3", "tag4", "tag5"]
    for tag_name in tag_names:
        tag = TaskTag(task_id=task.id, tag_name=tag_name)
        session.add(tag)
    session.commit()
    session.refresh(task)

    # Verify 5 tags exist
    tags_before = session.exec(select(TaskTag).where(TaskTag.task_id == task.id)).all()
    assert len(tags_before) == 5

    # Delete task
    response = client.delete(
        f"/users/{user.id}/tasks/{task.id}", headers=auth_headers_user_a
    )

    assert response.status_code == 200

    # Verify all 5 tags deleted
    tags_after = session.exec(select(TaskTag).where(TaskTag.task_id == task.id)).all()
    assert len(tags_after) == 0, "All 5 tags should be deleted"


def test_delete_task_no_orphaned_tags(
    client: TestClient,
    auth_headers_user_a: dict,
    test_user_a,
    test_task_with_tags: Task,
    session: Session,
):
    """
    Verify no orphaned tags after deletion.

    GIVEN: Task with tags exists
    WHEN: DELETE task
    THEN: Database query confirms no orphaned TaskTag records exist
    """
    user, _, _ = test_user_a
    task_id = test_task_with_tags.id

    # Get tag IDs before deletion
    tags_before = session.exec(select(TaskTag).where(TaskTag.task_id == task_id)).all()
    tag_ids_before = [tag.id for tag in tags_before]
    assert len(tag_ids_before) > 0

    # Delete task
    response = client.delete(
        f"/users/{user.id}/tasks/{task_id}", headers=auth_headers_user_a
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


# ============================================================================
# Information Disclosure Prevention Tests (CRITICAL SECURITY)
# ============================================================================


def test_delete_task_non_existent_returns_404(
    client: TestClient, auth_headers_user_a: dict, test_user_a
):
    """
    Test non-existent task returns 404.

    GIVEN: User A is authenticated and task does not exist
    WHEN: DELETE /api/users/{user_id}/tasks/{non_existent_uuid}
    THEN: Returns 404 Not Found
    """
    user, _, _ = test_user_a
    non_existent_id = uuid4()

    response = client.delete(
        f"/users/{user.id}/tasks/{non_existent_id}", headers=auth_headers_user_a
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_delete_task_cross_user_access_returns_404_not_403(
    client: TestClient,
    auth_headers_user_a: dict,
    auth_headers_user_b: dict,
    test_user_a,
    test_user_b,
    test_task_user_b: Task,
    session: Session,
):
    """
    CRITICAL SECURITY TEST: Cross-user deletion returns 404 (NOT 403).

    GIVEN: User A is authenticated, task belongs to User B
    WHEN: User A attempts DELETE /api/users/{user_a_id}/tasks/{user_b_task_id}
    THEN: Returns 404 Not Found (NOT 403 Forbidden)
    AND: User B's task is NOT deleted
    AND: No information is disclosed about task existence
    """
    user_a, _, _ = test_user_a
    user_b, _, _ = test_user_b
    task_b_id = test_task_user_b.id

    # User A attempts to delete User B's task
    response_a = client.delete(
        f"/users/{user_a.id}/tasks/{task_b_id}", headers=auth_headers_user_a
    )

    # CRITICAL: Must be 404, not 403
    assert response_a.status_code == 404, (
        f"SECURITY VIOLATION: Cross-user deletion must return 404 (not 403) to prevent enumeration. "
        f"Got {response_a.status_code}: {response_a.json()}"
    )

    assert response_a.json()["detail"] == "Task not found", (
        "Error message should not distinguish between non-existent and unauthorized"
    )

    # Verify User B's task still exists
    task_still_exists = session.get(Task, task_b_id)
    assert task_still_exists is not None, (
        "SECURITY VIOLATION: User A should not be able to delete User B's task"
    )

    # Verify User B can still delete their own task (sanity check)
    response_b = client.delete(
        f"/users/{user_b.id}/tasks/{task_b_id}", headers=auth_headers_user_b
    )
    assert response_b.status_code == 200, (
        "User B should still be able to delete their own task"
    )


def test_delete_task_response_timing_consistent(
    client: TestClient, auth_headers_user_a: dict, test_user_a, test_task_user_b: Task
):
    """
    Test response timing consistency to prevent timing attacks.

    GIVEN: User A is authenticated
    WHEN: User A attempts to delete non-existent task vs User B's task
    THEN: Response times should be similar (no timing attack surface)
    """
    user_a, _, _ = test_user_a
    non_existent_id = uuid4()
    user_b_task_id = test_task_user_b.id

    latencies = []

    # Measure time for non-existent task (5 iterations)
    for _ in range(5):
        start = time.perf_counter()
        response1 = client.delete(
            f"/users/{user_a.id}/tasks/{non_existent_id}", headers=auth_headers_user_a
        )
        latency1 = time.perf_counter() - start
        latencies.append(("non_existent", latency1))
        assert response1.status_code == 404

    # Measure time for other user's task (5 iterations)
    for _ in range(5):
        start = time.perf_counter()
        response2 = client.delete(
            f"/users/{user_a.id}/tasks/{user_b_task_id}", headers=auth_headers_user_a
        )
        latency2 = time.perf_counter() - start
        latencies.append(("other_user", latency2))
        assert response2.status_code == 404

    # Calculate average latencies for each case
    non_existent_avg = sum(l for t, l in latencies if t == "non_existent") / 5
    other_user_avg = sum(l for t, l in latencies if t == "other_user") / 5

    # Times should be similar (within 50ms)
    time_diff = abs(non_existent_avg - other_user_avg)
    assert time_diff < 0.05, (
        f"Timing attack risk: Average response time difference {time_diff * 1000:.2f}ms exceeds 50ms threshold"
    )


# ============================================================================
# Authorization Tests
# ============================================================================


def test_delete_task_path_user_mismatch_returns_403(
    client: TestClient, auth_headers_user_a: dict, test_user_a, test_user_b
):
    """
    Test path user_id mismatch returns 403 before DB query.

    GIVEN: User A is authenticated
    WHEN: User A attempts DELETE /api/users/{user_b_id}/tasks/{any_task_id}
    THEN: Returns 403 Forbidden BEFORE database query
    """
    user_a, _, _ = test_user_a
    user_b, _, _ = test_user_b

    response = client.delete(
        f"/users/{user_b.id}/tasks/{uuid4()}", headers=auth_headers_user_a
    )

    assert response.status_code == 403
    assert "Not authorized" in response.json()["detail"]


# ============================================================================
# Authentication Tests
# ============================================================================


def test_delete_task_no_token_returns_401(
    client: TestClient, test_user_a, test_task_user_a: Task
):
    """
    Test missing JWT token returns 401.

    GIVEN: No JWT token provided
    WHEN: DELETE /api/users/{user_id}/tasks/{task_id}
    THEN: Returns 401 Unauthorized from middleware
    """
    user, _, _ = test_user_a
    task_id = test_task_user_a.id

    response = client.delete(
        f"/users/{user.id}/tasks/{task_id}"
        # No Authorization header
    )

    assert response.status_code == 401
    assert (
        "Authorization" in response.json()["error"]
        or "MISSING_TOKEN" in response.json()["code"]
    )


def test_delete_task_invalid_token_returns_401(
    client: TestClient, test_user_a, test_task_user_a: Task
):
    """
    Test invalid JWT token returns 401.

    GIVEN: Invalid JWT token provided
    WHEN: DELETE /api/users/{user_id}/tasks/{task_id}
    THEN: Returns 401 Unauthorized from middleware
    """
    user, _, _ = test_user_a
    task_id = test_task_user_a.id

    response = client.delete(
        f"/users/{user.id}/tasks/{task_id}",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401
    json_response = response.json()
    assert "Invalid" in json_response.get(
        "error", ""
    ) or "INVALID" in json_response.get("code", "")


# ============================================================================
# Idempotency Tests
# ============================================================================


def test_delete_task_idempotent(
    client: TestClient, auth_headers_user_a: dict, test_user_a, test_task_user_a: Task
):
    """
    Test DELETE is idempotent (second delete returns 404).

    GIVEN: User A is authenticated and task exists
    WHEN: DELETE task twice
    THEN: First returns 200 OK, second returns 404 Not Found
    AND: No errors occur (idempotent operation)
    """
    user, _, _ = test_user_a
    task_id = test_task_user_a.id

    # First deletion
    response1 = client.delete(
        f"/users/{user.id}/tasks/{task_id}", headers=auth_headers_user_a
    )
    assert response1.status_code == 200
    assert response1.json()["message"] == "Task deleted successfully"

    # Second deletion (idempotent)
    response2 = client.delete(
        f"/users/{user.id}/tasks/{task_id}", headers=auth_headers_user_a
    )
    assert response2.status_code == 404
    assert response2.json()["detail"] == "Task not found"


# ============================================================================
# Input Validation Tests
# ============================================================================


def test_delete_task_invalid_uuid_format(
    client: TestClient, auth_headers_user_a: dict, test_user_a
):
    """
    Test invalid UUID format returns 422.

    GIVEN: User A is authenticated
    WHEN: DELETE /api/users/{user_id}/tasks/{invalid_uuid}
    THEN: Returns 422 Unprocessable Entity (FastAPI validation error)
    """
    user, _, _ = test_user_a

    response = client.delete(
        f"/users/{user.id}/tasks/not-a-uuid", headers=auth_headers_user_a
    )

    assert response.status_code == 422


# ============================================================================
# Concurrent Deletion Tests
# ============================================================================


def test_delete_task_concurrent_attempts(
    client: TestClient, auth_headers_user_a: dict, test_user_a, session: Session
):
    """
    Test concurrent deletion attempts.

    GIVEN: Task exists
    WHEN: Two concurrent DELETE requests
    THEN: One succeeds (200), one returns 404
    AND: No database errors occur (transaction safety)
    """
    import concurrent.futures

    user, _, _ = test_user_a

    # Create a task to delete
    task = Task(
        title="Task for concurrent deletion", user_id=user.id, priority="medium"
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    task_id = task.id

    results = []

    def delete_task():
        response = client.delete(
            f"/users/{user.id}/tasks/{task_id}", headers=auth_headers_user_a
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
