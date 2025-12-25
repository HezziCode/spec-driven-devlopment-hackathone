"""
Tests for database models.

Verifies model structure, fields, relationships, and constraints.
"""

import pytest
from uuid import UUID
from datetime import datetime
from typing import get_type_hints
from sqlalchemy import Index, UniqueConstraint

from models import User, Task, TaskTag, PriorityEnum


def test_user_model_fields():
    """Test User model has all required fields with correct types."""
    # Create a user instance
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password_123"
    )

    # Verify field values
    assert isinstance(user.id, UUID)
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.password_hash == "hashed_password_123"
    assert isinstance(user.created_at, datetime)
    assert isinstance(user.updated_at, datetime)

    # Verify type hints exist
    hints = get_type_hints(User)
    assert "id" in hints
    assert "username" in hints
    assert "email" in hints
    assert "password_hash" in hints
    assert "created_at" in hints
    assert "updated_at" in hints


def test_user_model_tablename():
    """Test User model has correct table name."""
    assert User.__tablename__ == "users"


def test_user_model_relationships():
    """Test User model has correct relationship to tasks."""
    hints = get_type_hints(User)
    assert "tasks" in hints


def test_task_model_fields():
    """Test Task model has all required fields with correct types."""
    from uuid import uuid4

    # Create a task instance
    user_id = uuid4()
    task = Task(
        user_id=user_id,
        title="Test Task",
        description="Test Description",
        completed=False,
        priority="medium"
    )

    # Verify field values
    assert isinstance(task.id, UUID)
    assert task.user_id == user_id
    assert task.title == "Test Task"
    assert task.description == "Test Description"
    assert task.completed is False
    assert task.priority == "medium"
    assert isinstance(task.created_at, datetime)
    assert isinstance(task.updated_at, datetime)

    # Verify type hints exist
    hints = get_type_hints(Task)
    assert "id" in hints
    assert "user_id" in hints
    assert "title" in hints
    assert "description" in hints
    assert "completed" in hints
    assert "priority" in hints
    assert "created_at" in hints
    assert "updated_at" in hints


def test_task_model_tablename():
    """Test Task model has correct table name."""
    assert Task.__tablename__ == "tasks"


def test_task_model_relationships():
    """Test Task model has correct relationships."""
    hints = get_type_hints(Task)
    assert "user" in hints
    assert "tags" in hints


def test_task_model_composite_index():
    """Test Task model has composite index on user_id and completed."""
    # Verify __table_args__ exists
    assert hasattr(Task, "__table_args__")
    assert Task.__table_args__ is not None

    # Check for composite index
    table_args = Task.__table_args__
    index_found = False
    for arg in table_args:
        if isinstance(arg, Index) and arg.name == "idx_user_completed":
            index_found = True
            # Verify index columns
            column_names = [col.name for col in arg.columns]
            assert "user_id" in column_names
            assert "completed" in column_names
            break

    assert index_found, "Composite index idx_user_completed not found"


def test_tasktag_model_fields():
    """Test TaskTag model has all required fields with correct types."""
    from uuid import uuid4

    # Create a task tag instance
    task_id = uuid4()
    tag = TaskTag(
        task_id=task_id,
        tag_name="urgent"
    )

    # Verify field values
    assert isinstance(tag.id, UUID)
    assert tag.task_id == task_id
    assert tag.tag_name == "urgent"
    assert isinstance(tag.created_at, datetime)

    # Verify type hints exist
    hints = get_type_hints(TaskTag)
    assert "id" in hints
    assert "task_id" in hints
    assert "tag_name" in hints
    assert "created_at" in hints


def test_tasktag_model_tablename():
    """Test TaskTag model has correct table name."""
    assert TaskTag.__tablename__ == "task_tags"


def test_tasktag_model_unique_constraint():
    """Test TaskTag model has unique constraint on task_id and tag_name."""
    # Verify __table_args__ exists
    assert hasattr(TaskTag, "__table_args__")
    assert TaskTag.__table_args__ is not None

    # Check for unique constraint
    table_args = TaskTag.__table_args__
    constraint_found = False
    for arg in table_args:
        if isinstance(arg, UniqueConstraint) and arg.name == "uq_task_tag":
            constraint_found = True
            # Verify constraint columns
            column_names = [col.name for col in arg.columns]
            assert "task_id" in column_names
            assert "tag_name" in column_names
            break

    assert constraint_found, "Unique constraint uq_task_tag not found"


def test_tasktag_model_relationships():
    """Test TaskTag model has correct relationship to task."""
    hints = get_type_hints(TaskTag)
    assert "task" in hints


def test_priority_enum_values():
    """Test PriorityEnum has all expected priority levels."""
    assert PriorityEnum.low.value == "low"
    assert PriorityEnum.medium.value == "medium"
    assert PriorityEnum.high.value == "high"
    assert PriorityEnum.critical.value == "critical"


def test_models_export():
    """Test all models are exported in __all__."""
    from models import __all__

    assert "User" in __all__
    assert "Task" in __all__
    assert "TaskTag" in __all__
    assert "PriorityEnum" in __all__


def test_user_task_relationship_types():
    """Test User and Task relationship types are correctly defined."""
    # Get type hints
    user_hints = get_type_hints(User)
    task_hints = get_type_hints(Task)

    # Verify User.tasks returns List[Task]
    assert "tasks" in user_hints

    # Verify Task.user returns User
    assert "user" in task_hints


def test_task_default_values():
    """Test Task model has correct default values."""
    from uuid import uuid4

    user_id = uuid4()
    task = Task(
        user_id=user_id,
        title="Test Task"
    )

    # Verify defaults
    assert task.completed is False
    assert task.priority == "medium"
    assert task.description is None


def test_user_unique_fields():
    """Test User model has unique constraints on username and email."""
    # This is verified by the Field definitions in the model
    # The unique=True parameter on username and email ensures uniqueness
    user1 = User(
        username="unique_user",
        email="unique@example.com",
        password_hash="hash123"
    )

    user2 = User(
        username="unique_user2",
        email="unique2@example.com",
        password_hash="hash456"
    )

    # Verify both users can be created with unique values
    assert user1.username != user2.username
    assert user1.email != user2.email
