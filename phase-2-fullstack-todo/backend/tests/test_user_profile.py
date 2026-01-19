"""
Test suite for user profile management endpoints.

This module tests the GET and PUT user profile endpoints
with comprehensive coverage of security, validation, and
duplicate checking requirements.
"""

from uuid import uuid4

from models import User


def test_get_profile_success(client, test_user, auth_headers):
    """Test successful profile retrieval."""
    user, _, _ = test_user

    response = client.get(f"/users/{user.id}", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == str(user.id)
    assert data["username"] == user.username
    assert data["email"] == user.email
    assert "password_hash" not in data  # CRITICAL SECURITY CHECK

    # Verify timestamps are present and valid
    assert "created_at" in data
    assert "updated_at" in data


def test_get_profile_excludes_password_hash(client, test_user, auth_headers):
    """Test GET profile response never includes password_hash."""
    user, _, _ = test_user

    response = client.get(f"/users/{user.id}", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert "password_hash" not in data


def test_get_profile_cross_user_blocked(client, test_user, auth_headers, session):
    """Test cross-user access blocked (403 Forbidden)."""
    user, _, token = test_user

    # Create another user
    import bcrypt

    other_password_hash = bcrypt.hashpw(
        "OtherPass123".encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")
    other_user = User(
        username="otheruser",
        email="other@example.com",
        password_hash=other_password_hash,
    )
    session.add(other_user)
    session.commit()
    session.refresh(other_user)

    # Try to access other user's profile with own token
    response = client.get(f"/users/{other_user.id}", headers=auth_headers)
    assert response.status_code == 403
    assert "authorized" in response.json()["detail"].lower()


def test_get_profile_unauthenticated(client, test_user):
    """Test GET profile without authentication returns 401."""
    user, _, _ = test_user

    response = client.get(f"/users/{user.id}")
    assert response.status_code == 401


def test_get_profile_nonexistent_user(client, test_user, auth_headers):
    """Test GET profile for non-existent user returns 404."""
    # Create a fake UUID
    fake_user_id = uuid4()

    response = client.get(f"/users/{fake_user_id}", headers=auth_headers)
    assert response.status_code == 404


def test_get_profile_invalid_uuid_format(client, test_user, auth_headers):
    """Test GET profile with invalid UUID format returns 422."""
    response = client.get("/users/invalid-uuid", headers=auth_headers)
    assert response.status_code == 422


def test_put_update_username_success(client, test_user, auth_headers):
    """Test successful username update."""
    user, _, _ = test_user

    response = client.put(
        f"/users/{user.id}", json={"username": "newusername"}, headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["username"] == "newusername"
    assert data["email"] == user.email  # Email unchanged
    assert data["id"] == str(user.id)

    # Verify password_hash not in response
    assert "password_hash" not in data


def test_put_update_email_success(client, test_user, auth_headers):
    """Test successful email update."""
    user, _, _ = test_user

    response = client.put(
        f"/users/{user.id}",
        json={"email": "newemail@example.com"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert data["email"] == "newemail@example.com"
    assert data["username"] == user.username  # Username unchanged
    assert data["id"] == str(user.id)

    # Verify password_hash not in response
    assert "password_hash" not in data


def test_put_update_both_success(client, test_user, auth_headers):
    """Test successful update of both username and email."""
    user, _, _ = test_user

    response = client.put(
        f"/users/{user.id}",
        json={"username": "newusername", "email": "newemail@example.com"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert data["username"] == "newusername"
    assert data["email"] == "newemail@example.com"
    assert data["id"] == str(user.id)

    # Verify password_hash not in response
    assert "password_hash" not in data


def test_put_update_username_duplicate(client, test_user, auth_headers, session):
    """Test updating username to duplicate value returns 409."""
    user, _, _ = test_user

    # Create another user with a username we'll try to duplicate
    import bcrypt

    other_password_hash = bcrypt.hashpw(
        "OtherPass123".encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")
    other_user = User(
        username="existinguser",
        email="other@example.com",
        password_hash=other_password_hash,
    )
    session.add(other_user)
    session.commit()

    # Try to update to the other user's username
    response = client.put(
        f"/users/{user.id}", json={"username": "existinguser"}, headers=auth_headers
    )

    assert response.status_code == 409
    assert "already taken" in response.json()["detail"]
    assert "existinguser" in response.json()["detail"]


def test_put_update_email_duplicate(client, test_user, auth_headers, session):
    """Test updating email to duplicate value returns 409."""
    user, _, _ = test_user

    # Create another user with an email we'll try to duplicate
    import bcrypt

    other_password_hash = bcrypt.hashpw(
        "OtherPass123".encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")
    other_user = User(
        username="otheruser",
        email="existing@example.com",
        password_hash=other_password_hash,
    )
    session.add(other_user)
    session.commit()

    # Try to update to the other user's email
    response = client.put(
        f"/users/{user.id}",
        json={"email": "existing@example.com"},
        headers=auth_headers,
    )

    assert response.status_code == 409
    assert "already taken" in response.json()["detail"]
    assert "existing@example.com" in response.json()["detail"]


def test_put_update_email_case_insensitive_duplicate(
    client, test_user, auth_headers, session
):
    """Test updating email to case-insensitive duplicate value returns 409."""
    user, _, _ = test_user

    # Create another user with an email we'll try to duplicate (different case)
    import bcrypt

    other_password_hash = bcrypt.hashpw(
        "OtherPass123".encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")
    other_user = User(
        username="otheruser",
        email="existing@example.com",  # lowercase
        password_hash=other_password_hash,
    )
    session.add(other_user)
    session.commit()

    # Try to update to the same email but different case
    response = client.put(
        f"/users/{user.id}",
        json={"email": "EXISTING@EXAMPLE.COM"},  # uppercase
        headers=auth_headers,
    )

    assert response.status_code == 409
    assert "already taken" in response.json()["detail"]
    assert "EXISTING@EXAMPLE.COM" in response.json()["detail"]


def test_put_update_username_length_validation(client, test_user, auth_headers):
    """Test username length validation (3-50 chars)."""
    user, _, _ = test_user

    # Test too short (2 chars)
    response = client.put(
        f"/users/{user.id}", json={"username": "ab"}, headers=auth_headers
    )
    assert response.status_code == 422

    # Test too long (51 chars)
    long_username = "a" * 51
    response = client.put(
        f"/users/{user.id}", json={"username": long_username}, headers=auth_headers
    )
    assert response.status_code == 422


def test_put_update_email_format_validation(client, test_user, auth_headers):
    """Test email format validation."""
    user, _, _ = test_user

    # Test invalid email format
    response = client.put(
        f"/users/{user.id}", json={"email": "invalid-email"}, headers=auth_headers
    )
    assert response.status_code == 422


def test_put_update_cross_user_blocked(client, test_user, auth_headers, session):
    """Test PUT cross-user access blocked (403 Forbidden)."""
    user, _, token = test_user

    # Create another user
    import bcrypt

    other_password_hash = bcrypt.hashpw(
        "OtherPass123".encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")
    other_user = User(
        username="otheruser",
        email="other@example.com",
        password_hash=other_password_hash,
    )
    session.add(other_user)
    session.commit()
    session.refresh(other_user)

    # Try to update other user's profile with own token
    response = client.put(
        f"/users/{other_user.id}",
        json={"username": "hacker_username"},
        headers=auth_headers,
    )
    assert response.status_code == 403
    assert "authorized" in response.json()["detail"].lower()


def test_put_update_neither_field_provided(client, test_user, auth_headers):
    """Test PUT with neither username nor email returns 422."""
    user, _, _ = test_user

    response = client.put(f"/users/{user.id}", json={}, headers=auth_headers)
    assert response.status_code == 422
    assert "at least one field" in response.json()["detail"].lower()


def test_put_update_username_idempotent(client, test_user, auth_headers):
    """Test updating username to same value succeeds (idempotent)."""
    user, _, _ = test_user

    response = client.put(
        f"/users/{user.id}",
        json={"username": user.username},  # Same username
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == user.username


def test_put_update_email_idempotent(client, test_user, auth_headers):
    """Test updating email to same value succeeds (idempotent)."""
    user, _, _ = test_user

    response = client.put(
        f"/users/{user.id}",
        json={"email": user.email},  # Same email
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user.email


def test_put_update_username_duplicate_with_valid_email(
    client, test_user, auth_headers, session
):
    """Test updating username to duplicate with valid email returns 409 (neither field updated)."""
    user, _, _ = test_user

    # Create another user with a username we'll try to duplicate
    import bcrypt

    other_password_hash = bcrypt.hashpw(
        "OtherPass123".encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")
    other_user = User(
        username="existinguser",
        email="existing@example.com",
        password_hash=other_password_hash,
    )
    session.add(other_user)
    session.commit()

    # Get current username before attempt
    original_username = user.username
    original_email = user.email

    # Try to update username to duplicate with a valid new email
    response = client.put(
        f"/users/{user.id}",
        json={"username": "existinguser", "email": "newemail@example.com"},
        headers=auth_headers,
    )

    assert response.status_code == 409
    assert "username" in response.json()["detail"].lower()
    assert "already taken" in response.json()["detail"]

    # Verify NEITHER field was updated (transaction rollback)
    session.refresh(user)
    assert user.username == original_username
    assert user.email == original_email


def test_put_update_email_duplicate_with_valid_username(
    client, test_user, auth_headers, session
):
    """Test updating email to duplicate with valid username returns 409 (neither field updated)."""
    user, _, _ = test_user

    # Create another user with an email we'll try to duplicate
    import bcrypt

    other_password_hash = bcrypt.hashpw(
        "OtherPass123".encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")
    other_user = User(
        username="otheruser",
        email="existing@example.com",
        password_hash=other_password_hash,
    )
    session.add(other_user)
    session.commit()

    # Get current values before attempt
    original_username = user.username
    original_email = user.email

    # Try to update email to duplicate with a valid new username
    response = client.put(
        f"/users/{user.id}",
        json={"username": "newusername", "email": "existing@example.com"},
        headers=auth_headers,
    )

    assert response.status_code == 409
    assert "email" in response.json()["detail"].lower()
    assert "already taken" in response.json()["detail"]

    # Verify NEITHER field was updated (transaction rollback)
    session.refresh(user)
    assert user.username == original_username
    assert user.email == original_email
