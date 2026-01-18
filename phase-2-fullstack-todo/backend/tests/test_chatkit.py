"""
Comprehensive tests for ChatKit session management and thread persistence endpoints.

Tests T024-T029 from specs/015-chatkit-ui/tasks.md Phase 2.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from uuid import UUID
from models import ChatKitSession, ChatThread


# ==================== Test Session Creation (T024) ====================

def test_create_session(client: TestClient, auth_headers_user_a):
    """Test ChatKit session creation endpoint returns client_secret."""
    response = client.post("/api/chatkit/session", headers=auth_headers_user_a)

    assert response.status_code == 201
    data = response.json()
    assert "client_secret" in data
    assert data["client_secret"].startswith("cs_")
    assert "expires_at" in data
    assert data["expires_at"].endswith("Z")  # ISO 8601 format


def test_create_session_unauthorized(client: TestClient):
    """Test session creation fails without JWT token."""
    response = client.post("/api/chatkit/session")

    assert response.status_code == 401
    assert "error" in response.json()


def test_create_session_stores_in_db(client: TestClient, auth_headers_user_a, test_user_a, session: Session):
    """Test session creation stores record in database."""
    user, _, _ = test_user_a

    response = client.post("/api/chatkit/session", headers=auth_headers_user_a)
    assert response.status_code == 201

    # Verify session stored in database
    from sqlmodel import select
    query = select(ChatKitSession).where(ChatKitSession.user_id == user.id)
    db_session = session.exec(query).first()

    assert db_session is not None
    assert db_session.user_id == user.id
    assert db_session.status == "active"
    assert db_session.client_secret_hash is not None


# ==================== Test List Threads (T025) ====================

def test_list_threads_empty(client: TestClient, auth_headers_user_a, test_user_a):
    """Test listing threads returns empty list for new user."""
    user, _, _ = test_user_a

    response = client.get(f"/api/users/{user.id}/chatkit/threads", headers=auth_headers_user_a)

    assert response.status_code == 200
    data = response.json()
    assert "threads" in data
    assert "total" in data
    assert data["total"] == 0
    assert len(data["threads"]) == 0


def test_list_threads_with_data(client: TestClient, auth_headers_user_a, test_user_a, session: Session):
    """Test listing threads returns user's threads."""
    user, _, _ = test_user_a

    # Create 3 threads for user
    for i in range(3):
        thread = ChatThread(
            id=f"thread_{i}",
            user_id=user.id,
            name=f"Test Thread {i}",
            message_count=i + 1
        )
        session.add(thread)
    session.commit()

    response = client.get(f"/api/users/{user.id}/chatkit/threads", headers=auth_headers_user_a)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["threads"]) == 3

    # Verify thread structure
    thread = data["threads"][0]
    assert "id" in thread
    assert "name" in thread
    assert "message_count" in thread
    assert "created_at" in thread
    assert "updated_at" in thread


def test_list_threads_pagination(client: TestClient, auth_headers_user_a, test_user_a, session: Session):
    """Test thread list pagination works correctly."""
    user, _, _ = test_user_a

    # Create 10 threads
    for i in range(10):
        thread = ChatThread(
            id=f"thread_{i}",
            user_id=user.id,
            name=f"Thread {i}",
            message_count=1
        )
        session.add(thread)
    session.commit()

    # Test limit
    response = client.get(
        f"/api/users/{user.id}/chatkit/threads?limit=5",
        headers=auth_headers_user_a
    )
    assert response.status_code == 200
    assert len(response.json()["threads"]) == 5

    # Test offset
    response = client.get(
        f"/api/users/{user.id}/chatkit/threads?limit=5&offset=5",
        headers=auth_headers_user_a
    )
    assert response.status_code == 200
    assert len(response.json()["threads"]) == 5


def test_list_threads_unauthorized(client: TestClient, test_user_a, auth_headers_user_b):
    """Test user B cannot list user A's threads."""
    user_a, _, _ = test_user_a

    response = client.get(
        f"/api/users/{user_a.id}/chatkit/threads",
        headers=auth_headers_user_b
    )

    assert response.status_code == 403
    assert "not authorized" in response.json()["detail"].lower()


# ==================== Test Sync Thread (T026) ====================

def test_sync_thread_create_new(client: TestClient, auth_headers_user_a, test_user_a):
    """Test syncing new thread creates it in database."""
    user, _, _ = test_user_a

    thread_data = {
        "thread_id": "thread_new_123",
        "name": "New Thread",
        "last_message_preview": "Hello, this is a test",
        "message_count": 5
    }

    response = client.post(
        f"/api/users/{user.id}/chatkit/threads/thread_new_123/sync",
        json=thread_data,
        headers=auth_headers_user_a
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "thread_new_123"
    assert data["name"] == "New Thread"
    assert data["message_count"] == 5
    assert data["last_message_preview"] == "Hello, this is a test"


def test_sync_thread_update_existing(client: TestClient, auth_headers_user_a, test_user_a, session: Session):
    """Test syncing existing thread updates it."""
    user, _, _ = test_user_a

    # Create initial thread
    thread = ChatThread(
        id="thread_update_test",
        user_id=user.id,
        name="Old Name",
        message_count=1
    )
    session.add(thread)
    session.commit()

    # Update thread
    thread_data = {
        "thread_id": "thread_update_test",
        "name": "Updated Name",
        "last_message_preview": "New message",
        "message_count": 10
    }

    response = client.post(
        f"/api/users/{user.id}/chatkit/threads/thread_update_test/sync",
        json=thread_data,
        headers=auth_headers_user_a
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["message_count"] == 10
    assert data["last_message_preview"] == "New message"


def test_sync_thread_unauthorized(client: TestClient, test_user_a, auth_headers_user_b):
    """Test user B cannot sync threads for user A."""
    user_a, _, _ = test_user_a

    thread_data = {
        "thread_id": "thread_unauthorized",
        "name": "Unauthorized Thread",
        "message_count": 1
    }

    response = client.post(
        f"/api/users/{user_a.id}/chatkit/threads/thread_unauthorized/sync",
        json=thread_data,
        headers=auth_headers_user_b
    )

    assert response.status_code == 403


# ==================== Test Delete Thread (T027) ====================

def test_delete_thread_success(client: TestClient, auth_headers_user_a, test_user_a, session: Session):
    """Test deleting thread removes it from database."""
    user, _, _ = test_user_a

    # Create thread
    thread = ChatThread(
        id="thread_to_delete",
        user_id=user.id,
        name="Delete Me",
        message_count=1
    )
    session.add(thread)
    session.commit()

    response = client.delete(
        f"/api/users/{user.id}/chatkit/threads/thread_to_delete",
        headers=auth_headers_user_a
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Thread deleted successfully"

    # Verify thread deleted from database
    from sqlmodel import select
    query = select(ChatThread).where(ChatThread.id == "thread_to_delete")
    deleted_thread = session.exec(query).first()
    assert deleted_thread is None


def test_delete_thread_not_found(client: TestClient, auth_headers_user_a, test_user_a):
    """Test deleting non-existent thread returns 404."""
    user, _, _ = test_user_a

    response = client.delete(
        f"/api/users/{user.id}/chatkit/threads/nonexistent_thread",
        headers=auth_headers_user_a
    )

    assert response.status_code == 404


def test_delete_thread_unauthorized(client: TestClient, test_user_a, test_user_b, auth_headers_user_b, session: Session):
    """Test user B cannot delete user A's thread."""
    user_a, _, _ = test_user_a

    # Create thread for user A
    thread = ChatThread(
        id="thread_user_a",
        user_id=user_a.id,
        name="User A Thread",
        message_count=1
    )
    session.add(thread)
    session.commit()

    # Try to delete with user B's token
    response = client.delete(
        f"/api/users/{user_a.id}/chatkit/threads/thread_user_a",
        headers=auth_headers_user_b
    )

    assert response.status_code == 403


# ==================== Test User Isolation (T028) ====================

def test_user_isolation_threads(client: TestClient, test_user_a, test_user_b, auth_headers_user_a, auth_headers_user_b, session: Session):
    """Test user A cannot access user B's threads and vice versa."""
    user_a, _, _ = test_user_a
    user_b, _, _ = test_user_b

    # Create threads for both users
    thread_a = ChatThread(
        id="thread_user_a_isolation",
        user_id=user_a.id,
        name="User A Thread",
        message_count=1
    )
    thread_b = ChatThread(
        id="thread_user_b_isolation",
        user_id=user_b.id,
        name="User B Thread",
        message_count=1
    )
    session.add(thread_a)
    session.add(thread_b)
    session.commit()

    # User A should only see their threads
    response = client.get(
        f"/api/users/{user_a.id}/chatkit/threads",
        headers=auth_headers_user_a
    )
    assert response.status_code == 200
    threads_a = response.json()["threads"]
    assert len(threads_a) == 1
    assert threads_a[0]["id"] == "thread_user_a_isolation"

    # User B should only see their threads
    response = client.get(
        f"/api/users/{user_b.id}/chatkit/threads",
        headers=auth_headers_user_b
    )
    assert response.status_code == 200
    threads_b = response.json()["threads"]
    assert len(threads_b) == 1
    assert threads_b[0]["id"] == "thread_user_b_isolation"

    # User A cannot access user B's threads endpoint
    response = client.get(
        f"/api/users/{user_b.id}/chatkit/threads",
        headers=auth_headers_user_a
    )
    assert response.status_code == 403


# ==================== Integration Tests ====================

def test_full_thread_lifecycle(client: TestClient, auth_headers_user_a, test_user_a):
    """Test complete thread lifecycle: create session → sync thread → list → delete."""
    user, _, _ = test_user_a

    # 1. Create session
    session_response = client.post("/api/chatkit/session", headers=auth_headers_user_a)
    assert session_response.status_code == 201
    assert "client_secret" in session_response.json()

    # 2. Sync new thread
    thread_data = {
        "thread_id": "lifecycle_thread",
        "name": "Lifecycle Test",
        "last_message_preview": "Test message",
        "message_count": 1
    }
    sync_response = client.post(
        f"/api/users/{user.id}/chatkit/threads/lifecycle_thread/sync",
        json=thread_data,
        headers=auth_headers_user_a
    )
    assert sync_response.status_code == 200

    # 3. List threads and verify it exists
    list_response = client.get(
        f"/api/users/{user.id}/chatkit/threads",
        headers=auth_headers_user_a
    )
    assert list_response.status_code == 200
    assert list_response.json()["total"] == 1

    # 4. Delete thread
    delete_response = client.delete(
        f"/api/users/{user.id}/chatkit/threads/lifecycle_thread",
        headers=auth_headers_user_a
    )
    assert delete_response.status_code == 200

    # 5. Verify thread is deleted
    final_list_response = client.get(
        f"/api/users/{user.id}/chatkit/threads",
        headers=auth_headers_user_a
    )
    assert final_list_response.json()["total"] == 0


def test_multiple_sessions_same_user(client: TestClient, auth_headers_user_a):
    """Test user can create multiple sessions (multi-device support)."""
    # Create first session
    response1 = client.post("/api/chatkit/session", headers=auth_headers_user_a)
    assert response1.status_code == 201
    secret1 = response1.json()["client_secret"]

    # Create second session
    response2 = client.post("/api/chatkit/session", headers=auth_headers_user_a)
    assert response2.status_code == 201
    secret2 = response2.json()["client_secret"]

    # Secrets should be different
    assert secret1 != secret2
