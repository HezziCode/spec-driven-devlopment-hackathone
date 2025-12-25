"""
Database connection and session management.

Provides database engine configuration and session management for FastAPI
dependency injection with Neon PostgreSQL.
"""

from sqlmodel import create_engine, Session
from typing import Generator
import os
from dotenv import load_dotenv

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
)


def get_session() -> Generator[Session, None, None]:
    """
    Get a database session for FastAPI dependency injection.

    This function creates a new database session and yields it for use in
    route handlers. The session is automatically closed after the request
    completes, ensuring proper resource cleanup.

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
        - Session is automatically committed on successful completion.
        - Session is rolled back on exception.
        - Session is always closed after use.
    """
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()