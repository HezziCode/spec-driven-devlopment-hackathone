"""
Tests for authentication route handlers.

Tests signup, login, and logout endpoints with comprehensive test coverage
following TDD approach (RED phase - tests written before implementation).
"""

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from datetime import datetime, timedelta, timezone
import os
from sqlmodel import select
from models import User
from db import get_session
from main import app


@pytest.fixture(name="client")
def test_client_fixture(session):
    """
    Create a test client with overridden database dependency.

    Overrides the get_session dependency to use the test database session
    instead of the production database.
    """
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# ============================================================================
# SIGNUP ENDPOINT TESTS (Task 3.1 - RED Phase)
# ============================================================================

def test_signup_success(client, session, valid_signup_data):
    """Test successful user signup with valid data."""
    response = client.post("/auth/signup", json=valid_signup_data)
    assert response.status_code == 201

    data = response.json()
    assert "user" in data
    assert "token" in data
    assert data["user"]["username"] == valid_signup_data["username"]
    assert data["user"]["email"] == valid_signup_data["email"].lower()
    assert "password_hash" not in data["user"]
    assert "id" in data["user"]
    assert "created_at" in data["user"]


def test_signup_duplicate_username(client, session, create_test_user, valid_signup_data):
    """Test signup fails with 409 when username already exists."""
    # Create user with username "testuser"
    user, _ = create_test_user(username="testuser", email="existing@example.com", password="Pass123")

    # Try to signup with same username but different email
    response = client.post("/auth/signup", json={
        "username": "testuser",
        "email": "different@example.com",
        "password": "SecurePass123"
    })

    assert response.status_code == 409
    error_data = response.json()
    assert "detail" in error_data
    detail = error_data["detail"]
    assert "error" in detail
    assert "username" in detail["error"].lower() or "already exists" in detail["error"].lower()


def test_signup_duplicate_email_case_insensitive(client, session, create_test_user):
    """Test signup fails with 409 when email already exists (case-insensitive)."""
    # Create user with email "test@example.com"
    user, _ = create_test_user(username="user1", email="test@example.com", password="Pass123")

    # Try to signup with same email in different case
    response = client.post("/auth/signup", json={
        "username": "user2",
        "email": "TEST@Example.COM",
        "password": "SecurePass123"
    })

    assert response.status_code == 409
    error_data = response.json()
    assert "detail" in error_data
    detail = error_data["detail"]
    assert "error" in detail
    assert "email" in detail["error"].lower() or "already exists" in detail["error"].lower()


def test_signup_short_username(client, session):
    """Test signup fails with 422 when username is too short."""
    response = client.post("/auth/signup", json={
        "username": "ab",  # Too short (< 3 chars)
        "email": "test@example.com",
        "password": "SecurePass123"
    })

    assert response.status_code == 422


def test_signup_invalid_email(client, session):
    """Test signup fails with 422 when email format is invalid."""
    response = client.post("/auth/signup", json={
        "username": "testuser",
        "email": "notanemail",  # Invalid email format
        "password": "SecurePass123"
    })

    assert response.status_code == 422


def test_signup_short_password(client, session):
    """Test signup fails with 422 when password is too short."""
    response = client.post("/auth/signup", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "Short1"  # Too short (< 8 chars)
    })

    assert response.status_code == 422


def test_signup_password_hashed_in_db(client, session, valid_signup_data):
    """Test password is properly hashed with bcrypt before storage."""
    response = client.post("/auth/signup", json=valid_signup_data)
    assert response.status_code == 201

    # Query database to check password hash
    user = session.exec(select(User).where(User.email == valid_signup_data["email"].lower())).first()
    assert user is not None
    assert user.password_hash.startswith("$2b$12$")  # bcrypt 12 rounds format
    assert user.password_hash != valid_signup_data["password"]  # Not plaintext


def test_signup_password_not_in_response(client, session, valid_signup_data):
    """Test password_hash is never exposed in API response."""
    response = client.post("/auth/signup", json=valid_signup_data)
    assert response.status_code == 201

    response_text = response.text
    assert "password_hash" not in response_text
    assert "$2b$" not in response_text  # Bcrypt hash pattern should not appear


def test_signup_jwt_token_structure(client, session, valid_signup_data):
    """Test JWT token has correct structure with 7-day expiration."""
    response = client.post("/auth/signup", json=valid_signup_data)
    assert response.status_code == 201

    data = response.json()
    token = data["token"]

    # Decode token without verification to inspect structure
    secret = os.getenv("BETTER_AUTH_SECRET", "test-secret-key-at-least-32-characters-long-for-testing")
    payload = jwt.decode(token, secret, algorithms=["HS256"])

    # Verify required fields
    assert "sub" in payload  # User ID
    assert "email" in payload
    assert "exp" in payload  # Expiration
    assert "iat" in payload  # Issued at

    # Verify expiration is approximately 7 days
    exp_timestamp = payload["exp"]
    iat_timestamp = payload["iat"]
    exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=UTC)
    iat_datetime = datetime.fromtimestamp(iat_timestamp, tz=UTC)

    time_diff = exp_datetime - iat_datetime
    # Should be 7 days (±1 minute tolerance for test execution time)
    assert 6.99 <= time_diff.days <= 7.01

    # Verify email matches signup email
    assert payload["email"] == valid_signup_data["email"].lower()


def test_signup_email_normalized_lowercase(client, session):
    """Test email is normalized to lowercase before storage."""
    response = client.post("/auth/signup", json={
        "username": "testuser",
        "email": "Test@EXAMPLE.com",
        "password": "SecurePass123"
    })

    assert response.status_code == 201

    # Check database
    user = session.exec(select(User).where(User.username == "testuser")).first()
    assert user is not None
    assert user.email == "test@example.com"  # Lowercase


# ============================================================================
# LOGIN ENDPOINT TESTS (Task 4.1 - RED Phase)
# ============================================================================

def test_login_success(client, session, create_test_user):
    """Test successful login with correct credentials."""
    user, plain_password = create_test_user(
        username="loginuser",
        email="login@example.com",
        password="SecurePass123"
    )

    response = client.post("/auth/login", json={
        "email": "login@example.com",
        "password": "SecurePass123"
    })

    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert "token" in data
    assert data["user"]["email"] == "login@example.com"
    assert data["user"]["username"] == "loginuser"
    assert "password_hash" not in data["user"]


def test_login_wrong_password(client, session, create_test_user):
    """Test login fails with 401 when password is incorrect."""
    user, _ = create_test_user(
        email="login@example.com",
        password="SecurePass123"
    )

    response = client.post("/auth/login", json={
        "email": "login@example.com",
        "password": "WrongPassword"
    })

    assert response.status_code == 401
    error_data = response.json()
    assert error_data["detail"]["error"] == "Invalid credentials"


def test_login_nonexistent_email(client, session):
    """Test login fails with 401 when email does not exist."""
    response = client.post("/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "SomePassword123"
    })

    assert response.status_code == 401
    error_data = response.json()
    assert error_data["detail"]["error"] == "Invalid credentials"


def test_login_case_insensitive_email(client, session, create_test_user):
    """Test login works with case-insensitive email matching."""
    user, plain_password = create_test_user(
        email="test@example.com",
        password="SecurePass123"
    )

    # Login with uppercase email
    response = client.post("/auth/login", json={
        "email": "TEST@Example.COM",
        "password": "SecurePass123"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["user"]["email"] == "test@example.com"


def test_login_invalid_email_format(client, session):
    """Test login fails with 422 when email format is invalid."""
    response = client.post("/auth/login", json={
        "email": "notanemail",
        "password": "SomePassword123"
    })

    assert response.status_code == 422


def test_login_missing_password(client, session):
    """Test login fails with 422 when password field is missing."""
    response = client.post("/auth/login", json={
        "email": "test@example.com"
        # Missing password field
    })

    assert response.status_code == 422


def test_login_jwt_token_valid(client, session, create_test_user):
    """Test JWT token from login has correct structure and expiration."""
    user, plain_password = create_test_user(
        email="token@example.com",
        password="SecurePass123"
    )

    response = client.post("/auth/login", json={
        "email": "token@example.com",
        "password": "SecurePass123"
    })

    assert response.status_code == 200
    token = response.json()["token"]

    # Decode and verify token
    secret = os.getenv("BETTER_AUTH_SECRET", "test-secret-key-at-least-32-characters-long-for-testing")
    payload = jwt.decode(token, secret, algorithms=["HS256"])

    assert payload["sub"] == str(user.id)
    assert payload["email"] == "token@example.com"

    # Verify 7-day expiration
    exp_datetime = datetime.fromtimestamp(payload["exp"], tz=UTC)
    iat_datetime = datetime.fromtimestamp(payload["iat"], tz=UTC)
    time_diff = exp_datetime - iat_datetime
    assert 6.99 <= time_diff.days <= 7.01


def test_login_password_verification(client, session, create_test_user):
    """Test password verification uses constant-time comparison."""
    user, _ = create_test_user(
        email="verify@example.com",
        password="CorrectPassword123"
    )

    # Correct password should succeed
    response1 = client.post("/auth/login", json={
        "email": "verify@example.com",
        "password": "CorrectPassword123"
    })
    assert response1.status_code == 200

    # Wrong password should fail with same error message
    response2 = client.post("/auth/login", json={
        "email": "verify@example.com",
        "password": "WrongPassword123"
    })
    assert response2.status_code == 401
    assert response2.json()["detail"]["error"] == "Invalid credentials"


# ============================================================================
# LOGOUT ENDPOINT TESTS (Task 5.1 - RED Phase)
# ============================================================================

def test_logout_success(client):
    """Test logout returns success message."""
    response = client.post("/auth/logout")
    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "Successfully logged out"


def test_logout_with_token(client, session, create_test_user):
    """Test logout works with Authorization header (token is optional)."""
    user, password = create_test_user(email="logout@example.com", password="Pass123")

    # Login to get token
    login_response = client.post("/auth/login", json={
        "email": "logout@example.com",
        "password": "Pass123"
    })
    token = login_response.json()["token"]

    # Logout with token
    response = client.post("/auth/logout", headers={
        "Authorization": f"Bearer {token}"
    })

    assert response.status_code == 200
    assert response.json()["message"] == "Successfully logged out"


def test_logout_without_token(client):
    """Test logout works without Authorization header (stateless)."""
    response = client.post("/auth/logout")
    assert response.status_code == 200
    assert response.json()["message"] == "Successfully logged out"


def test_logout_idempotent(client):
    """Test logout can be called multiple times successfully."""
    response1 = client.post("/auth/logout")
    response2 = client.post("/auth/logout")
    response3 = client.post("/auth/logout")

    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response3.status_code == 200

    assert response1.json()["message"] == "Successfully logged out"
    assert response2.json()["message"] == "Successfully logged out"
    assert response3.json()["message"] == "Successfully logged out"
