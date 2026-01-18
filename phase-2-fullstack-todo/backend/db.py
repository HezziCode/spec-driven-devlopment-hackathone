"""
Database connection and session management.

Provides database engine configuration and session management for FastAPI
dependency injection with Neon PostgreSQL, including connection retry logic.
"""

from sqlmodel import create_engine, Session
from typing import Generator
import os
import time
import logging
from dotenv import load_dotenv
from sqlalchemy.exc import OperationalError
from sqlalchemy import text

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Get DATABASE_URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Validate DATABASE_URL
if DATABASE_URL is None:
    raise ValueError(
        "DATABASE_URL environment variable is not set. "
        "Please configure DATABASE_URL in your .env file with a valid "
        "Neon PostgreSQL connection string. "
        "Example: postgresql://user:password@host/database?sslmode=require"
    )

if "sqlite" in DATABASE_URL.lower():
    raise ValueError(
        "SQLite database detected in DATABASE_URL. "
        "This application requires Neon PostgreSQL for production. "
        "Please update DATABASE_URL with a valid PostgreSQL connection string. "
        "Example: postgresql://user:password@host/database?sslmode=require"
    )

# Create the database engine with connection pooling
# Pool settings optimized for serverless PostgreSQL (Neon)
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Log all SQL statements for debugging
    pool_size=5,  # Number of connections to keep in the pool
    max_overflow=10,  # Maximum number of connections above pool_size
    pool_timeout=30,  # Seconds to wait before timing out connection request
    pool_recycle=3600,  # Recycle connections after 1 hour to prevent stale connections
    pool_pre_ping=True,  # Verify connections before using them
    connect_args={
        "connect_timeout": 10  # Connection timeout in seconds
    }
)


def get_session_with_retry(max_retries: int = 3, retry_delay: float = 1.0) -> Session:
    """
    Create a database session with retry logic for connection failures.

    Args:
        max_retries: Maximum number of retry attempts
        retry_delay: Initial delay between retries (exponential backoff)

    Returns:
        Session: SQLModel database session

    Raises:
        OperationalError: If all retry attempts fail
    """
    last_error = None

    for attempt in range(max_retries):
        try:
            session = Session(engine)
            # Test the connection
            session.execute(text("SELECT 1"))
            return session
        except OperationalError as e:
            last_error = e
            if attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                logger.warning(
                    f"Database connection failed (attempt {attempt + 1}/{max_retries}). "
                    f"Retrying in {wait_time}s... Error: {str(e)}"
                )
                time.sleep(wait_time)
            else:
                logger.error(
                    f"Database connection failed after {max_retries} attempts. "
                    f"Error: {str(e)}"
                )

    raise last_error


def get_session() -> Generator[Session, None, None]:
    """
    Get a database session for FastAPI dependency injection with retry logic.

    This function creates a new database session with automatic retry on
    connection failures and yields it for use in route handlers. The session
    is automatically closed after the request completes.

    Yields:
        Session: SQLModel database session for executing queries.

    Example:
        ```python
        from fastapi import Depends

        @app.get("/tasks")
        def get_tasks(session: Session = Depends(get_session)):
            tasks = session.exec(select(Task)).all()
            return tasks
        ```

    Note:
        - Automatically retries connection failures up to 3 times
        - Session is automatically committed on successful completion
        - Session is rolled back on exception
        - Session is always closed after use
    """
    session = None
    try:
        session = get_session_with_retry()
        yield session
        session.commit()
    except OperationalError as e:
        logger.error(f"Database operation failed: {str(e)}")
        if session:
            session.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error in database session: {str(e)}")
        if session:
            session.rollback()
        raise
    finally:
        if session:
            session.close()