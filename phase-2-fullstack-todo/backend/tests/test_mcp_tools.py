"""
Comprehensive tests for MCP Server tools.

Tests all 6 MCP tools with success, error, and edge case scenarios.
Ensures user isolation and proper validation.
"""

import pytest
from uuid import uuid4
from datetime import datetime

from sqlmodel import Session, select

# Skip database connection for schema-only tests
import sys
sys.path.insert(0, '.')

from models import Task, User
from mcp_server.schemas import TaskStatus


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def test_user_id():
    """Generate a test user UUID."""
    return str(uuid4())


@pytest.fixture
def other_user_id():
    """Generate another user UUID for isolation tests."""
    return str(uuid4())


@pytest.fixture
def test_task_id():
    """Generate a test task UUID."""
    return str(uuid4())


# =============================================================================
# Helper Functions for Testing
# =============================================================================

def create_test_user(session: Session, user_id: str = None) -> User:
    """Create a test user in the database."""
    user = User(
        id=user_id or uuid4(),
        username=f"testuser_{uuid4().hex[:8]}",
        email=f"test_{uuid4().hex[:8]}@example.com",
        password_hash="test_hash",
        auth_provider="local"
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def create_test_task(
    session: Session,
    user_id: str,
    title: str = "Test Task",
    description: str = None,
    completed: bool = False
) -> Task:
    """Create a test task in the database."""
    task = Task(
        user_id=user_id,
        title=title,
        description=description,
        completed=completed,
        priority="medium"
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


# =============================================================================
# Schema Tests
# =============================================================================

class TestSchemas:
    """Tests for Pydantic schemas."""

    def test_task_status_enum(self):
        """Test TaskStatus enum values."""
        assert TaskStatus.all.value == "all"
        assert TaskStatus.pending.value == "pending"
        assert TaskStatus.completed.value == "completed"

    def test_create_task_input_valid(self):
        """Test CreateTaskInput with valid data."""
        from mcp_server.schemas import CreateTaskInput

        input_data = CreateTaskInput(
            user_id=str(uuid4()),
            title="Test Task",
            description="Test description"
        )
        assert input_data.title == "Test Task"
        assert input_data.description == "Test description"

    def test_create_task_input_no_description(self):
        """Test CreateTaskInput without description."""
        from mcp_server.schemas import CreateTaskInput

        input_data = CreateTaskInput(
            user_id=str(uuid4()),
            title="Test Task"
        )
        assert input_data.description == ""

    def test_create_task_input_title_too_long(self):
        """Test CreateTaskInput rejects title > 200 chars."""
        from mcp_server.schemas import CreateTaskInput
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            CreateTaskInput(
                user_id=str(uuid4()),
                title="x" * 201
            )

    def test_update_task_input_requires_at_least_one_field(self):
        """Test UpdateTaskInput requires title or description."""
        from mcp_server.schemas import UpdateTaskInput
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            UpdateTaskInput(
                user_id=str(uuid4()),
                task_id=str(uuid4())
            )

    def test_update_task_input_with_title_only(self):
        """Test UpdateTaskInput with title only."""
        from mcp_server.schemas import UpdateTaskInput

        input_data = UpdateTaskInput(
            user_id=str(uuid4()),
            task_id=str(uuid4()),
            title="New Title"
        )
        assert input_data.title == "New Title"
        assert input_data.description is None

    def test_search_tasks_input_query_too_long(self):
        """Test SearchTasksInput rejects query > 100 chars."""
        from mcp_server.schemas import SearchTasksInput
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            SearchTasksInput(
                user_id=str(uuid4()),
                query="x" * 101
            )


# =============================================================================
# Tool Unit Tests (Mocked)
# =============================================================================

class TestCreateTaskTool:
    """Tests for create_task tool."""

    def test_create_task_invalid_user_id(self):
        """Test create_task with invalid user_id format."""
        from mcp_server.tools import create_task

        result = create_task(
            user_id="invalid-uuid",
            title="Test Task"
        )
        assert "error" in result
        assert result["code"] == "VALIDATION_ERROR"

    def test_create_task_empty_title(self):
        """Test create_task with empty title."""
        from mcp_server.tools import create_task

        result = create_task(
            user_id=str(uuid4()),
            title=""
        )
        assert "error" in result
        assert result["code"] == "VALIDATION_ERROR"

    def test_create_task_title_too_long(self):
        """Test create_task with title > 200 chars."""
        from mcp_server.tools import create_task

        result = create_task(
            user_id=str(uuid4()),
            title="x" * 201
        )
        assert "error" in result
        assert result["code"] == "VALIDATION_ERROR"

    def test_create_task_description_too_long(self):
        """Test create_task with description > 2000 chars."""
        from mcp_server.tools import create_task

        result = create_task(
            user_id=str(uuid4()),
            title="Test Task",
            description="x" * 2001
        )
        assert "error" in result
        assert result["code"] == "VALIDATION_ERROR"


class TestListTasksTool:
    """Tests for list_tasks tool."""

    def test_list_tasks_invalid_user_id(self):
        """Test list_tasks with invalid user_id format."""
        from mcp_server.tools import list_tasks

        result = list_tasks(
            user_id="invalid-uuid",
            status="all"
        )
        assert "error" in result
        assert result["code"] == "VALIDATION_ERROR"

    def test_list_tasks_invalid_status(self):
        """Test list_tasks with invalid status filter."""
        from mcp_server.tools import list_tasks

        result = list_tasks(
            user_id=str(uuid4()),
            status="invalid"
        )
        assert "error" in result
        assert result["code"] == "VALIDATION_ERROR"


class TestMarkCompleteTool:
    """Tests for mark_complete tool."""

    def test_mark_complete_invalid_user_id(self):
        """Test mark_complete with invalid user_id format."""
        from mcp_server.tools import mark_complete

        result = mark_complete(
            user_id="invalid-uuid",
            task_id=str(uuid4())
        )
        assert "error" in result
        assert result["code"] == "VALIDATION_ERROR"

    def test_mark_complete_invalid_task_id(self):
        """Test mark_complete with invalid task_id format."""
        from mcp_server.tools import mark_complete

        result = mark_complete(
            user_id=str(uuid4()),
            task_id="invalid-uuid"
        )
        assert "error" in result
        assert result["code"] == "VALIDATION_ERROR"


class TestUpdateTaskTool:
    """Tests for update_task tool."""

    def test_update_task_no_fields_provided(self):
        """Test update_task with neither title nor description."""
        from mcp_server.tools import update_task

        result = update_task(
            user_id=str(uuid4()),
            task_id=str(uuid4())
        )
        assert "error" in result
        assert result["code"] == "VALIDATION_ERROR"

    def test_update_task_empty_title(self):
        """Test update_task with empty title."""
        from mcp_server.tools import update_task

        result = update_task(
            user_id=str(uuid4()),
            task_id=str(uuid4()),
            title="   "  # Whitespace only
        )
        assert "error" in result
        assert result["code"] == "VALIDATION_ERROR"

    def test_update_task_title_too_long(self):
        """Test update_task with title > 200 chars."""
        from mcp_server.tools import update_task

        result = update_task(
            user_id=str(uuid4()),
            task_id=str(uuid4()),
            title="x" * 201
        )
        assert "error" in result
        assert result["code"] == "VALIDATION_ERROR"

    def test_update_task_description_too_long(self):
        """Test update_task with description > 2000 chars."""
        from mcp_server.tools import update_task

        result = update_task(
            user_id=str(uuid4()),
            task_id=str(uuid4()),
            description="x" * 2001
        )
        assert "error" in result
        assert result["code"] == "VALIDATION_ERROR"


class TestDeleteTaskTool:
    """Tests for delete_task tool."""

    def test_delete_task_invalid_user_id(self):
        """Test delete_task with invalid user_id format."""
        from mcp_server.tools import delete_task

        result = delete_task(
            user_id="invalid-uuid",
            task_id=str(uuid4())
        )
        assert "error" in result
        assert result["code"] == "VALIDATION_ERROR"

    def test_delete_task_invalid_task_id(self):
        """Test delete_task with invalid task_id format."""
        from mcp_server.tools import delete_task

        result = delete_task(
            user_id=str(uuid4()),
            task_id="invalid-uuid"
        )
        assert "error" in result
        assert result["code"] == "VALIDATION_ERROR"


class TestSearchTasksTool:
    """Tests for search_tasks tool."""

    def test_search_tasks_invalid_user_id(self):
        """Test search_tasks with invalid user_id format."""
        from mcp_server.tools import search_tasks

        result = search_tasks(
            user_id="invalid-uuid",
            query="test"
        )
        assert "error" in result
        assert result["code"] == "VALIDATION_ERROR"

    def test_search_tasks_empty_query(self):
        """Test search_tasks with empty query."""
        from mcp_server.tools import search_tasks

        result = search_tasks(
            user_id=str(uuid4()),
            query=""
        )
        assert "error" in result
        assert result["code"] == "VALIDATION_ERROR"

    def test_search_tasks_query_too_long(self):
        """Test search_tasks with query > 100 chars."""
        from mcp_server.tools import search_tasks

        result = search_tasks(
            user_id=str(uuid4()),
            query="x" * 101
        )
        assert "error" in result
        assert result["code"] == "VALIDATION_ERROR"


# =============================================================================
# Integration Tests (Require Database)
# =============================================================================

@pytest.mark.integration
class TestCreateTaskIntegration:
    """Integration tests for create_task with database."""

    def test_create_task_success(self, db_session, test_user):
        """Test successful task creation."""
        from mcp_server.tools import create_task

        result = create_task(
            user_id=str(test_user.id),
            title="Integration Test Task",
            description="Test description"
        )

        assert "task_id" in result
        assert result["status"] == "created"
        assert result["title"] == "Integration Test Task"

    def test_create_task_with_title_only(self, db_session, test_user):
        """Test task creation with title only."""
        from mcp_server.tools import create_task

        result = create_task(
            user_id=str(test_user.id),
            title="Title Only Task"
        )

        assert result["status"] == "created"


@pytest.mark.integration
class TestListTasksIntegration:
    """Integration tests for list_tasks with database."""

    def test_list_tasks_all(self, db_session, test_user, test_tasks):
        """Test listing all tasks."""
        from mcp_server.tools import list_tasks

        result = list_tasks(
            user_id=str(test_user.id),
            status="all"
        )

        assert "tasks" in result
        assert result["total"] >= 0

    def test_list_tasks_pending(self, db_session, test_user, test_tasks):
        """Test listing pending tasks only."""
        from mcp_server.tools import list_tasks

        result = list_tasks(
            user_id=str(test_user.id),
            status="pending"
        )

        for task in result["tasks"]:
            assert task["completed"] == False

    def test_list_tasks_completed(self, db_session, test_user, test_tasks):
        """Test listing completed tasks only."""
        from mcp_server.tools import list_tasks

        result = list_tasks(
            user_id=str(test_user.id),
            status="completed"
        )

        for task in result["tasks"]:
            assert task["completed"] == True


@pytest.mark.integration
class TestMarkCompleteIntegration:
    """Integration tests for mark_complete with database."""

    def test_mark_complete_success(self, db_session, test_user, pending_task):
        """Test marking a task as complete."""
        from mcp_server.tools import mark_complete

        result = mark_complete(
            user_id=str(test_user.id),
            task_id=str(pending_task.id)
        )

        assert result["status"] == "completed"

    def test_mark_complete_idempotent(self, db_session, test_user, completed_task):
        """Test that marking already-completed task succeeds."""
        from mcp_server.tools import mark_complete

        result = mark_complete(
            user_id=str(test_user.id),
            task_id=str(completed_task.id)
        )

        assert result["status"] == "completed"

    def test_mark_complete_not_found(self, db_session, test_user):
        """Test mark_complete with non-existent task."""
        from mcp_server.tools import mark_complete

        result = mark_complete(
            user_id=str(test_user.id),
            task_id=str(uuid4())
        )

        assert "error" in result
        assert result["code"] == "NOT_FOUND"

    def test_mark_complete_wrong_user(self, db_session, test_user, other_user, other_user_task):
        """Test mark_complete enforces user isolation."""
        from mcp_server.tools import mark_complete

        result = mark_complete(
            user_id=str(test_user.id),  # Wrong user
            task_id=str(other_user_task.id)
        )

        assert "error" in result
        assert result["code"] == "NOT_FOUND"


@pytest.mark.integration
class TestUpdateTaskIntegration:
    """Integration tests for update_task with database."""

    def test_update_task_title_only(self, db_session, test_user, pending_task):
        """Test updating task title only."""
        from mcp_server.tools import update_task

        result = update_task(
            user_id=str(test_user.id),
            task_id=str(pending_task.id),
            title="Updated Title"
        )

        assert result["status"] == "updated"
        assert result["title"] == "Updated Title"

    def test_update_task_description_only(self, db_session, test_user, pending_task):
        """Test updating task description only."""
        from mcp_server.tools import update_task

        result = update_task(
            user_id=str(test_user.id),
            task_id=str(pending_task.id),
            description="Updated description"
        )

        assert result["status"] == "updated"

    def test_update_task_both_fields(self, db_session, test_user, pending_task):
        """Test updating both title and description."""
        from mcp_server.tools import update_task

        result = update_task(
            user_id=str(test_user.id),
            task_id=str(pending_task.id),
            title="New Title",
            description="New Description"
        )

        assert result["status"] == "updated"
        assert result["title"] == "New Title"


@pytest.mark.integration
class TestDeleteTaskIntegration:
    """Integration tests for delete_task with database."""

    def test_delete_task_success(self, db_session, test_user, pending_task):
        """Test successful task deletion."""
        from mcp_server.tools import delete_task

        task_id = str(pending_task.id)
        result = delete_task(
            user_id=str(test_user.id),
            task_id=task_id
        )

        assert result["status"] == "deleted"
        assert result["task_id"] == task_id

    def test_delete_task_not_found(self, db_session, test_user):
        """Test delete_task with non-existent task."""
        from mcp_server.tools import delete_task

        result = delete_task(
            user_id=str(test_user.id),
            task_id=str(uuid4())
        )

        assert "error" in result
        assert result["code"] == "NOT_FOUND"

    def test_delete_task_wrong_user(self, db_session, test_user, other_user, other_user_task):
        """Test delete_task enforces user isolation."""
        from mcp_server.tools import delete_task

        result = delete_task(
            user_id=str(test_user.id),  # Wrong user
            task_id=str(other_user_task.id)
        )

        assert "error" in result
        assert result["code"] == "NOT_FOUND"


@pytest.mark.integration
class TestSearchTasksIntegration:
    """Integration tests for search_tasks with database."""

    def test_search_tasks_finds_in_title(self, db_session, test_user, searchable_tasks):
        """Test search finds matches in title."""
        from mcp_server.tools import search_tasks

        result = search_tasks(
            user_id=str(test_user.id),
            query="groceries"
        )

        assert result["total"] >= 1

    def test_search_tasks_finds_in_description(self, db_session, test_user, searchable_tasks):
        """Test search finds matches in description."""
        from mcp_server.tools import search_tasks

        result = search_tasks(
            user_id=str(test_user.id),
            query="milk"
        )

        assert result["total"] >= 1

    def test_search_tasks_case_insensitive(self, db_session, test_user, searchable_tasks):
        """Test search is case-insensitive."""
        from mcp_server.tools import search_tasks

        result_lower = search_tasks(
            user_id=str(test_user.id),
            query="groceries"
        )
        result_upper = search_tasks(
            user_id=str(test_user.id),
            query="GROCERIES"
        )

        assert result_lower["total"] == result_upper["total"]

    def test_search_tasks_no_matches(self, db_session, test_user):
        """Test search returns empty list when no matches."""
        from mcp_server.tools import search_tasks

        result = search_tasks(
            user_id=str(test_user.id),
            query="nonexistentxyz123"
        )

        assert result["tasks"] == []
        assert result["total"] == 0
