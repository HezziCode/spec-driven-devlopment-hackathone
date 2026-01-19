"""
Tests for authentication Pydantic schemas.

Tests validation rules for SignupRequest, LoginRequest, UserResponse, and AuthResponse.
Follows TDD RED phase - these tests will fail until schemas are implemented.
"""

from datetime import datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError


def test_signup_request_valid():
    """Test creating SignupRequest with valid data."""
    from schemas.auth import SignupRequest

    request = SignupRequest(
        username="testuser", email="test@example.com", password="SecurePass123"
    )
    assert request.username == "testuser"
    assert request.email == "test@example.com"
    assert request.password == "SecurePass123"


def test_signup_request_short_username():
    """Test SignupRequest rejects username shorter than 3 characters."""
    from schemas.auth import SignupRequest

    with pytest.raises(ValidationError) as exc_info:
        SignupRequest(username="ab", email="test@example.com", password="SecurePass123")

    errors = exc_info.value.errors()
    assert any(
        "min_length" in str(error).lower() or "at least 3" in str(error).lower()
        for error in errors
    )


def test_signup_request_long_username():
    """Test SignupRequest rejects username longer than 50 characters."""
    from schemas.auth import SignupRequest

    long_username = "a" * 51
    with pytest.raises(ValidationError) as exc_info:
        SignupRequest(
            username=long_username, email="test@example.com", password="SecurePass123"
        )

    errors = exc_info.value.errors()
    assert any(
        "max_length" in str(error).lower() or "at most 50" in str(error).lower()
        for error in errors
    )


def test_signup_request_invalid_email():
    """Test SignupRequest rejects invalid email format."""
    from schemas.auth import SignupRequest

    with pytest.raises(ValidationError) as exc_info:
        SignupRequest(username="testuser", email="notanemail", password="SecurePass123")

    errors = exc_info.value.errors()
    assert any("email" in str(error).lower() for error in errors)


def test_signup_request_short_password():
    """Test SignupRequest rejects password shorter than 8 characters."""
    from schemas.auth import SignupRequest

    with pytest.raises(ValidationError) as exc_info:
        SignupRequest(username="testuser", email="test@example.com", password="Short1")

    errors = exc_info.value.errors()
    assert any(
        "min_length" in str(error).lower() or "at least 8" in str(error).lower()
        for error in errors
    )


def test_login_request_valid():
    """Test creating LoginRequest with valid email and password."""
    from schemas.auth import LoginRequest

    request = LoginRequest(email="test@example.com", password="SecurePass123")
    assert request.email == "test@example.com"
    assert request.password == "SecurePass123"


def test_login_request_invalid_email():
    """Test LoginRequest rejects invalid email format."""
    from schemas.auth import LoginRequest

    with pytest.raises(ValidationError) as exc_info:
        LoginRequest(email="notanemail", password="SecurePass123")

    errors = exc_info.value.errors()
    assert any("email" in str(error).lower() for error in errors)


def test_user_response_excludes_password_hash():
    """Test UserResponse does not include password_hash field."""
    from schemas.auth import UserResponse

    user_id = uuid4()
    user_response = UserResponse(
        id=user_id,
        username="testuser",
        email="test@example.com",
        created_at=datetime.utcnow(),
    )

    # Verify password_hash is not in model dump
    user_dict = user_response.model_dump()
    assert "password_hash" not in user_dict
    assert user_dict["username"] == "testuser"
    assert user_dict["email"] == "test@example.com"


def test_auth_response_structure():
    """Test AuthResponse has correct structure with user and token fields."""
    from schemas.auth import AuthResponse, UserResponse

    user_id = uuid4()
    user = UserResponse(
        id=user_id,
        username="testuser",
        email="test@example.com",
        created_at=datetime.utcnow(),
    )

    auth_response = AuthResponse(
        user=user, token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.token"
    )

    assert auth_response.user.username == "testuser"
    assert auth_response.token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.token"

    # Verify response can be serialized to dict
    auth_dict = auth_response.model_dump()
    assert "user" in auth_dict
    assert "token" in auth_dict
    assert auth_dict["user"]["username"] == "testuser"
