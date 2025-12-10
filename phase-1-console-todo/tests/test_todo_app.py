import pytest
from src.todo_app import TodoApp
from src.models import Task


def test_add_task_success():
    """Test that adding a task works correctly."""
    app = TodoApp()
    task_id = app.add_task("Test task", "Test description")
    
    assert task_id == 1
    assert len(app.tasks) == 1
    assert app.tasks[0].id == 1
    assert app.tasks[0].title == "Test task"
    assert app.tasks[0].description == "Test description"
    assert app.tasks[0].completed is False


def test_add_task_without_description():
    """Test adding a task without a description."""
    app = TodoApp()
    task_id = app.add_task("Test task")
    
    assert task_id == 1
    assert app.tasks[0].description is None


def test_get_all_tasks():
    """Test getting all tasks."""
    app = TodoApp()
    app.add_task("Task 1")
    app.add_task("Task 2")
    
    tasks = app.get_all_tasks()
    assert len(tasks) == 2
    assert tasks[0].title == "Task 1"
    assert tasks[1].title == "Task 2"


def test_get_task_by_id():
    """Test getting a task by ID."""
    app = TodoApp()
    app.add_task("Test task")
    task_id = app.add_task("Another task")
    
    task = app.get_task_by_id(task_id)
    assert task is not None
    assert task.title == "Another task"
    
    nonexistent_task = app.get_task_by_id(999)
    assert nonexistent_task is None


def test_update_task():
    """Test updating a task."""
    app = TodoApp()
    task_id = app.add_task("Original task", "Original description")
    
    app.update_task(task_id, "Updated task", "Updated description")
    
    updated_task = app.get_task_by_id(task_id)
    assert updated_task.title == "Updated task"
    assert updated_task.description == "Updated description"
    assert updated_task.completed is False  # Should preserve completion status


def test_delete_task():
    """Test deleting a task."""
    app = TodoApp()
    task_id = app.add_task("Task to delete")
    
    result = app.delete_task(task_id)
    assert result is True
    assert len(app.tasks) == 0
    
    # Try to delete a non-existent task
    with pytest.raises(ValueError):
        app.delete_task(999)


def test_toggle_task_completion():
    """Test toggling task completion status."""
    app = TodoApp()
    task_id = app.add_task("Test task")
    
    task = app.get_task_by_id(task_id)
    assert task.completed is False
    
    app.toggle_task_completion(task_id)
    task = app.get_task_by_id(task_id)
    assert task.completed is True
    
    app.toggle_task_completion(task_id)
    task = app.get_task_by_id(task_id)
    assert task.completed is False
    
    # Try to toggle non-existent task
    with pytest.raises(ValueError):
        app.toggle_task_completion(999)


def test_get_completed_tasks():
    """Test getting completed tasks."""
    app = TodoApp()
    task1_id = app.add_task("Task 1")
    task2_id = app.add_task("Task 2")
    
    app.toggle_task_completion(task1_id)  # Mark first task as complete
    
    completed = app.get_completed_tasks()
    pending = app.get_pending_tasks()
    
    assert len(completed) == 1
    assert completed[0].id == task1_id
    assert len(pending) == 1
    assert pending[0].id == task2_id
