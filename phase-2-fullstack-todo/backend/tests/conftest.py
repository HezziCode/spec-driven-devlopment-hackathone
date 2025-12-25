"""
Test configuration and fixtures for pytest.

Provides fixtures for test database setup, session management, and cleanup.
"""

import pytest
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool
from typing import Generator, Tuple
from datetime import datetime, timedelta, UTC
import os
from jose import jwt
from passlib.context import CryptContext
from models import User


@pytest.fixture(name="engine")
def create_test_engine():
    """
    Create an in-memory SQLite database engine for testing.

    Returns:
        Engine: SQLModel engine configured for testing with in-memory SQLite.

    Note:
        Uses StaticPool to maintain single connection across test session.
        All tables are created fresh for each test session.
    """
    # Create in-memory SQLite database for testing
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create all tables
    SQLModel.metadata.create_all(engine)

    yield engine

    # Cleanup: drop all tables after tests
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(name="session")
def create_test_session(engine) -> Generator[Session, None, None]:
    """
    Create a test database session with automatic cleanup.

    Args:
        engine: Test database engine from create_test_engine fixture.

    Yields:
        Session: SQLModel session for database operations in tests.

    Note:
        Session is automatically rolled back after each test.
        Use for all database operations in tests.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    # Rollback transaction and close connection
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(name="test_tables")
def create_test_tables(engine):
    """
    Ensure all database tables are created for testing.

    Args:
        engine: Test database engine from create_test_engine fixture.

    Note:
        This fixture ensures tables exist before running tests.
        Use when tests require pre-existing table structure.
    """
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="test_secret")
def get_test_secret() -> str:
    """
    Get the test secret for JWT operations.

    Returns:
        str: Test secret key for JWT signing/verification.

    Note:
        Uses BETTER_AUTH_SECRET from environment or a default test secret.
    """
    return os.getenv("BETTER_AUTH_SECRET", "test-secret-key-at-least-32-characters-long-for-testing")


@pytest.fixture(name="generate_valid_jwt")
def create_valid_jwt_generator(test_secret: str):
    """
    Create a fixture that generates valid JWT tokens for testing.

    Args:
        test_secret: Test secret key from get_test_secret fixture.

    Returns:
        Callable that generates valid JWT tokens with 1 hour expiration.

    Example:
        def test_something(generate_valid_jwt):
            token = generate_valid_jwt(user_id="123", email="test@example.com")
            # Use token in test
    """
    def _generate(user_id: str = "test-user-id", email: str = "test@example.com") -> str:
        """
        Generate a valid JWT token for testing.

        Args:
            user_id: User ID to include in token (default: "test-user-id").
            email: Email to include in token (default: "test@example.com").

        Returns:
            str: Valid JWT token string.
        """
        payload = {
            "sub": user_id,
            "email": email,
            "exp": datetime.now(UTC) + timedelta(hours=1),
            "iat": datetime.now(UTC)
        }
        return jwt.encode(payload, test_secret, algorithm="HS256")

    return _generate


@pytest.fixture(name="generate_expired_jwt")
def create_expired_jwt_generator(test_secret: str):
    """
    Create a fixture that generates expired JWT tokens for testing.

    Args:
        test_secret: Test secret key from get_test_secret fixture.

    Returns:
        Callable that generates expired JWT tokens.

    Example:
        def test_expired_token(generate_expired_jwt):
            token = generate_expired_jwt()
            # Test should reject this token
    """
    def _generate(user_id: str = "test-user-id", email: str = "test@example.com") -> str:
        """
        Generate an expired JWT token for testing.

        Args:
            user_id: User ID to include in token (default: "test-user-id").
            email: Email to include in token (default: "test@example.com").

        Returns:
            str: Expired JWT token string.
        """
        payload = {
            "sub": user_id,
            "email": email,
            "exp": datetime.now(UTC) - timedelta(hours=1),  # Expired 1 hour ago
            "iat": datetime.now(UTC) - timedelta(hours=2)
        }
        return jwt.encode(payload, test_secret, algorithm="HS256")

    return _generate


@pytest.fixture(name="generate_invalid_jwt")
def create_invalid_jwt_generator():
    """
    Create a fixture that generates JWT tokens with invalid signatures.

    Returns:
        Callable that generates JWT tokens with wrong signature.

    Example:
        def test_invalid_signature(generate_invalid_jwt):
            token = generate_invalid_jwt()
            # Test should reject this token
    """
    def _generate(user_id: str = "test-user-id", email: str = "test@example.com") -> str:
        """
        Generate a JWT token with invalid signature for testing.

        Args:
            user_id: User ID to include in token (default: "test-user-id").
            email: Email to include in token (default: "test@example.com").

        Returns:
            str: JWT token with invalid signature.
        """
        payload = {
            "sub": user_id,
            "email": email,
            "exp": datetime.now(UTC) + timedelta(hours=1),
            "iat": datetime.now(UTC)
        }
        # Use wrong secret to create invalid signature
        return jwt.encode(payload, "wrong-secret-key-different-from-test-secret", algorithm="HS256")

    return _generate


# Password context for authentication testing
pwd_context = CryptContext(schemes=["bcrypt"], bcrypt__rounds=12, deprecated="auto")


@pytest.fixture(name="create_test_user")
def create_test_user_fixture(session):
    """
    Create a test user with hashed password.

    Returns a factory function that creates users with hashed passwords.
    Returns tuple: (user, plaintext_password) for testing login.

    Example:
        def test_something(create_test_user):
            user, password = create_test_user(username="testuser", email="test@example.com", password="TestPass123")
            # Use user and password in test
    """
    def _create_user(username: str = "testuser", email: str = "test@example.com", password: str = "TestPass123") -> Tuple[User, str]:
        """
        Create a test user with hashed password. Returns (user, plaintext_password).

        Args:
            username: Username for the user (default: "testuser").
            email: Email address for the user (default: "test@example.com").
            password: Plaintext password to be hashed (default: "TestPass123").

        Returns:
            Tuple[User, str]: Created user object and plaintext password.
        """
        password_hash = pwd_context.hash(password)
        user = User(
            username=username,
            email=email.lower(),  # Normalize email to lowercase
            password_hash=password_hash
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user, password

    return _create_user


@pytest.fixture(name="valid_signup_data")
def valid_signup_data_fixture():
    """
    Valid signup request data for testing.

    Returns:
        dict: Valid signup data with username, email, and password.

    Example:
        def test_signup(valid_signup_data):
            response = client.post("/auth/signup", json=valid_signup_data)
    """
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass123"
    }


@pytest.fixture(name="valid_login_data")
def valid_login_data_fixture():
    """
    Valid login request data for testing.

    Returns:
        dict: Valid login data with email and password.

    Example:
        def test_login(valid_login_data):
            response = client.post("/auth/login", json=valid_login_data)
    """
    return {
        "email": "test@example.com",
        "password": "SecurePass123"
    }
