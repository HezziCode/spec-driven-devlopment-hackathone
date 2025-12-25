"""
Tests for JWT utility functions.

Tests verify token decoding, verification, and user extraction utilities.
"""

import pytest
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError
from datetime import datetime, timedelta


class TestJWTUtils:
    """Test suite for JWT utility functions."""

    def test_decode_valid_token(self, generate_valid_jwt, test_secret):
        """
        Test decode_token with a valid JWT token.

        Verifies:
        - Token decodes successfully
        - Payload contains expected claims
        - Returns dict with sub and email
        """
        from utils.jwt_utils import decode_token

        # Arrange
        user_id = "decode-test-user"
        email = "decode@example.com"
        token = generate_valid_jwt(user_id=user_id, email=email)

        # Act
        payload = decode_token(token)

        # Assert
        assert payload["sub"] == user_id
        assert payload["email"] == email
        assert "exp" in payload
        assert "iat" in payload

    def test_decode_invalid_signature(self, generate_invalid_jwt):
        """
        Test decode_token with invalid signature raises JWTError.

        Verifies:
        - Invalid signature is detected
        - JWTError exception is raised
        """
        from utils.jwt_utils import decode_token

        # Arrange
        token = generate_invalid_jwt()

        # Act & Assert
        with pytest.raises(JWTError):
            decode_token(token)

    def test_decode_expired_token(self, generate_expired_jwt):
        """
        Test decode_token with expired token raises ExpiredSignatureError.

        Verifies:
        - Expired tokens are detected
        - ExpiredSignatureError exception is raised
        """
        from utils.jwt_utils import decode_token

        # Arrange
        token = generate_expired_jwt()

        # Act & Assert
        with pytest.raises(ExpiredSignatureError):
            decode_token(token)

    def test_verify_valid_token(self, generate_valid_jwt):
        """
        Test verify_token returns True for valid tokens.

        Verifies:
        - Valid token returns True
        - No exceptions raised
        """
        from utils.jwt_utils import verify_token

        # Arrange
        token = generate_valid_jwt()

        # Act
        result = verify_token(token)

        # Assert
        assert result is True

    def test_verify_expired_token(self, generate_expired_jwt):
        """
        Test verify_token returns False for expired tokens.

        Verifies:
        - Expired token returns False
        - No exceptions raised
        """
        from utils.jwt_utils import verify_token

        # Arrange
        token = generate_expired_jwt()

        # Act
        result = verify_token(token)

        # Assert
        assert result is False

    def test_verify_invalid_signature(self, generate_invalid_jwt):
        """
        Test verify_token returns False for invalid signatures.

        Verifies:
        - Invalid signature returns False
        - No exceptions raised
        """
        from utils.jwt_utils import verify_token

        # Arrange
        token = generate_invalid_jwt()

        # Act
        result = verify_token(token)

        # Assert
        assert result is False

    def test_extract_existing_user(self, engine, session, generate_valid_jwt):
        """
        Test extract_user_from_token returns User for existing user.

        Verifies:
        - User is found in database
        - User object is returned
        - User ID matches token claim
        """
        from utils.jwt_utils import extract_user_from_token
        from models import User
        from sqlmodel import SQLModel

        # Create tables
        SQLModel.metadata.create_all(engine)

        # Arrange
        # Create test user in database
        user = User(
            username="testuser",
            email="extract@example.com",
            password_hash="hashed_password"
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        token = generate_valid_jwt(user_id=str(user.id), email=user.email)

        # Act
        result = extract_user_from_token(token, session)

        # Assert
        assert result is not None
        assert result.id == user.id
        assert result.email == user.email

        # Cleanup
        SQLModel.metadata.drop_all(engine)

    def test_extract_nonexistent_user(self, session, generate_valid_jwt):
        """
        Test extract_user_from_token returns None for nonexistent user.

        Verifies:
        - User not found in database
        - Returns None
        - No exceptions raised
        """
        from utils.jwt_utils import extract_user_from_token
        from uuid import uuid4

        # Arrange
        token = generate_valid_jwt(user_id=str(uuid4()))

        # Act
        result = extract_user_from_token(token, session)

        # Assert
        assert result is None
