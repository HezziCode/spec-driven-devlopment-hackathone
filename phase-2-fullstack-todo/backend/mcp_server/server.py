"""
FastMCP server setup and configuration.

This module initializes the FastMCP server instance with database
lifespan management for the Todo MCP Server.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastmcp import FastMCP
from sqlmodel import Session

from db import engine

# Configure logging for MCP server
logger = logging.getLogger(__name__)

# Initialize FastMCP server instance
mcp = FastMCP(
    "TodoManager",
    instructions="""
    MCP Server for Todo Management.

    This server provides tools for AI agents to manage user tasks:
    - create_task: Create a new task
    - list_tasks: List user's tasks with optional filtering
    - mark_complete: Mark a task as completed
    - update_task: Update task details
    - delete_task: Delete a task
    - search_tasks: Search tasks by keyword

    All tools require a user_id parameter to ensure user isolation.
    Tasks are stored in a PostgreSQL database.
    """,
)


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[Session, None]:
    """
    Async context manager for database sessions.

    Provides a database session with automatic commit on success
    and rollback on failure. Ensures proper resource cleanup.

    Yields:
        Session: SQLModel database session for executing queries.

    Example:
        async with get_db_session() as session:
            task = session.exec(select(Task)).first()
    """
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {str(e)}")
            raise
        finally:
            session.close()


def get_sync_session() -> Session:
    """
    Get a synchronous database session.

    Returns a new session that must be manually managed
    (commit/rollback/close). Used by MCP tools.

    Returns:
        Session: SQLModel database session.
    """
    return Session(engine)


# Export the mcp instance for use in tools and main.py
__all__ = ["mcp", "get_db_session", "get_sync_session"]
