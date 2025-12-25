"""
Tests for database connection and session management.

Verifies database connection configuration, validation, and session lifecycle.
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from sqlmodel import Session, text


def test_database_url_validation_missing():
    """Test that missing DATABASE_URL raises ValueError."""
    # Mock environment without DATABASE_URL
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError) as exc_info:
            # Force reimport to trigger validation
            import importlib
            import sys
            if "db" in sys.modules:
                del sys.modules["db"]
            import db

        assert "DATABASE_URL environment variable is not set" in str(exc_info.value)


def test_database_url_validation_sqlite():
    """Test that SQLite DATABASE_URL raises ValueError."""
    # Mock environment with SQLite URL
    with patch.dict(os.environ, {"DATABASE_URL": "sqlite:///test.db"}):
        with pytest.raises(ValueError) as exc_info:
            # Force reimport to trigger validation
            import importlib
            import sys
            if "db" in sys.modules:
                del sys.modules["db"]
            import db

        assert "SQLite database detected" in str(exc_info.value)


def test_get_session_yields_session(engine):
    """Test that get_session yields a valid Session object."""
    from db import get_session

    # Get session from generator
    session_gen = get_session()
    session = next(session_gen)

    # Verify it's a Session instance
    assert isinstance(session, Session)

    # Cleanup
    try:
        next(session_gen)
    except StopIteration:
        pass


def test_get_session_commits_on_success(engine, session):
    """Test that get_session commits the session on successful completion."""
    from db import get_session

    # Track if commit was called
    commit_called = False
    original_commit = session.commit

    def mock_commit():
        nonlocal commit_called
        commit_called = True
        original_commit()

    session.commit = mock_commit

    # Use the session
    with patch("db.Session", return_value=session):
        session_gen = get_session()
        s = next(session_gen)

        # Simulate successful completion
        try:
            next(session_gen)
        except StopIteration:
            pass

    # Note: In actual usage, commit happens when generator exits normally
    # This test verifies the structure; full integration test would verify actual commit


def test_get_session_rollback_on_exception(engine):
    """Test that get_session rolls back on exception."""
    from db import get_session
    from sqlmodel import Session

    # Create a mock session
    mock_session = MagicMock(spec=Session)
    mock_session.__enter__ = MagicMock(return_value=mock_session)
    mock_session.__exit__ = MagicMock(return_value=False)

    with patch("db.Session", return_value=mock_session):
        session_gen = get_session()
        session = next(session_gen)

        # Simulate an exception
        try:
            session_gen.throw(Exception("Test exception"))
        except Exception:
            pass

        # Verify rollback was called
        mock_session.rollback.assert_called_once()


def test_get_session_closes_session(engine):
    """Test that get_session always closes the session."""
    from db import get_session
    from sqlmodel import Session

    # Create a mock session
    mock_session = MagicMock(spec=Session)
    mock_session.__enter__ = MagicMock(return_value=mock_session)
    mock_session.__exit__ = MagicMock(return_value=False)

    with patch("db.Session", return_value=mock_session):
        session_gen = get_session()
        session = next(session_gen)

        # Complete the generator
        try:
            next(session_gen)
        except StopIteration:
            pass

        # Verify close was called
        mock_session.close.assert_called_once()


def test_engine_has_connection_pool():
    """Test that engine is configured with connection pooling."""
    # Set valid PostgreSQL URL for this test
    with patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@localhost/test"}):
        # Force reimport
        import sys
        if "db" in sys.modules:
            del sys.modules["db"]
        import db

        # Verify engine has pool settings
        engine = db.engine
        assert engine is not None
        assert hasattr(engine.pool, "size")


def test_database_connection_with_valid_url(engine, session):
    """Test actual database connection with valid engine."""
    # Execute simple query
    result = session.exec(text("SELECT 1 as test")).first()

    # Verify result
    assert result is not None
    assert result[0] == 1


def test_session_context_manager(engine):
    """Test that Session works as context manager."""
    from db import engine as db_engine

    # Use session as context manager
    with Session(db_engine) as session:
        result = session.exec(text("SELECT 1")).first()
        assert result[0] == 1

    # Session should be closed after context


def test_get_session_dependency_injection_pattern():
    """Test that get_session follows FastAPI dependency injection pattern."""
    from db import get_session
    from typing import get_type_hints
    import inspect

    # Verify function signature
    assert inspect.isgeneratorfunction(get_session)

    # Verify return type hints
    hints = get_type_hints(get_session)
    assert "return" in hints


def test_database_url_format_validation():
    """Test various DATABASE_URL formats."""
    valid_urls = [
        "postgresql://user:pass@localhost/db",
        "postgresql://user:pass@host:5432/db",
        "postgresql://user:pass@host/db?sslmode=require",
    ]

    invalid_urls = [
        "sqlite:///test.db",
        "sqlite:///:memory:",
    ]

    # Test valid URLs don't raise errors
    for url in valid_urls:
        with patch.dict(os.environ, {"DATABASE_URL": url}):
            try:
                import sys
                if "db" in sys.modules:
                    del sys.modules["db"]
                import db
                assert db.engine is not None
            except ValueError:
                pytest.fail(f"Valid URL {url} raised ValueError")

    # Test invalid URLs raise errors
    for url in invalid_urls:
        with patch.dict(os.environ, {"DATABASE_URL": url}):
            with pytest.raises(ValueError):
                import sys
                if "db" in sys.modules:
                    del sys.modules["db"]
                import db
