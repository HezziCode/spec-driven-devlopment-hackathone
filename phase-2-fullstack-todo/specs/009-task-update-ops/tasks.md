# Implementation Tasks: Task Update Operations

## Feature ID
009-task-update-ops

## Task Breakdown

### Task 1: Review and Verify Existing Implementation
**Priority:** P0 (Critical)
**Estimated Time:** 30 minutes

**Description:**
Review the existing PUT and PATCH endpoints to understand current implementation state and identify what needs enhancement or testing.

**Steps:**
1. Review `backend/schemas/task.py` - TaskUpdate schema
2. Review `backend/services/task_service.py` - update_task function
3. Review `backend/routes/tasks.py` - PUT and PATCH handlers
4. Review existing tests in `backend/tests/test_tasks.py`
5. Identify gaps in implementation or testing

**Acceptance Criteria:**
- [ ] Existing schemas reviewed and documented
- [ ] Service layer logic reviewed and documented
- [ ] Route handlers reviewed and documented
- [ ] Test coverage assessed
- [ ] Gap analysis completed

**Test Cases:**
- N/A (review task)

---

### Task 2: Unit Test - Service Layer Full Update
**Priority:** P0 (Critical)
**Estimated Time:** 45 minutes
**TDD Phase:** RED

**Description:**
Write unit tests for full task update functionality in the service layer before verifying/implementing the logic.

**Test Cases:**
```python
def test_update_task_all_fields(db_session, test_user, test_task):
    """Test updating all task fields successfully."""
    # Arrange
    update_data = TaskUpdate(
        title="Updated Title",
        description="Updated Description",
        completed=True,
        priority=PriorityEnum.high,
        tags=["work", "urgent"]
    )

    # Act
    updated_task = update_task(db_session, test_task.id, update_data, test_user.id)

    # Assert
    assert updated_task is not None
    assert updated_task.title == "Updated Title"
    assert updated_task.description == "Updated Description"
    assert updated_task.completed is True
    assert updated_task.priority == PriorityEnum.high
    assert set(updated_task.tags) == {"work", "urgent"}
    assert updated_task.updated_at > test_task.created_at


def test_update_task_replaces_tags(db_session, test_user, test_task_with_tags):
    """Test that updating tags replaces all existing tags."""
    # Arrange
    original_tags = test_task_with_tags.tags  # ["tag1", "tag2"]
    update_data = TaskUpdate(
        title="Updated",
        tags=["new1", "new2", "new3"]
    )

    # Act
    updated_task = update_task(
        db_session, test_task_with_tags.id, update_data, test_user.id
    )

    # Assert
    assert set(updated_task.tags) == {"new1", "new2", "new3"}
    assert "tag1" not in updated_task.tags
    assert "tag2" not in updated_task.tags


def test_update_task_removes_all_tags(db_session, test_user, test_task_with_tags):
    """Test updating with empty tags array removes all tags."""
    # Arrange
    update_data = TaskUpdate(title="Updated", tags=[])

    # Act
    updated_task = update_task(
        db_session, test_task_with_tags.id, update_data, test_user.id
    )

    # Assert
    assert updated_task.tags == []


def test_update_task_not_found(db_session, test_user):
    """Test updating non-existent task returns None."""
    # Arrange
    fake_task_id = uuid4()
    update_data = TaskUpdate(title="Updated")

    # Act
    result = update_task(db_session, fake_task_id, update_data, test_user.id)

    # Assert
    assert result is None


def test_update_task_wrong_user(db_session, test_user, other_user, test_task):
    """Test updating task owned by another user returns None."""
    # Arrange
    update_data = TaskUpdate(title="Hacked")

    # Act
    result = update_task(db_session, test_task.id, update_data, other_user.id)

    # Assert
    assert result is None
    # Verify original task unchanged
    original_task = db_session.get(Task, test_task.id)
    assert original_task.title == test_task.title


def test_update_task_timestamp_changes(db_session, test_user, test_task):
    """Test that updated_at timestamp changes on update."""
    # Arrange
    import time
    original_updated_at = test_task.updated_at
    time.sleep(0.1)  # Ensure time difference
    update_data = TaskUpdate(title="Updated")

    # Act
    updated_task = update_task(db_session, test_task.id, update_data, test_user.id)

    # Assert
    assert updated_task.updated_at > original_updated_at
```

**Acceptance Criteria:**
- [ ] All test cases written and pass (or fail appropriately for TDD)
- [ ] Tests cover full update scenarios
- [ ] Tests verify tag replacement logic
- [ ] Tests verify user isolation
- [ ] Tests verify timestamp updates

---

### Task 3: Unit Test - Service Layer Partial Update
**Priority:** P0 (Critical)
**Estimated Time:** 45 minutes
**TDD Phase:** RED

**Description:**
Write unit tests for partial task update functionality (PATCH behavior).

**Test Cases:**
```python
def test_update_task_only_title(db_session, test_user, test_task):
    """Test updating only title field preserves others."""
    # Arrange
    original_description = test_task.description
    original_completed = test_task.completed
    original_priority = test_task.priority
    update_data = TaskUpdate(title="New Title Only")

    # Act
    updated_task = update_task(db_session, test_task.id, update_data, test_user.id)

    # Assert
    assert updated_task.title == "New Title Only"
    assert updated_task.description == original_description
    assert updated_task.completed == original_completed
    assert updated_task.priority == original_priority


def test_update_task_only_completed(db_session, test_user, test_task):
    """Test updating only completed status (toggle)."""
    # Arrange
    original_title = test_task.title
    original_completed = test_task.completed
    update_data = TaskUpdate(completed=not original_completed)

    # Act
    updated_task = update_task(db_session, test_task.id, update_data, test_user.id)

    # Assert
    assert updated_task.completed == (not original_completed)
    assert updated_task.title == original_title


def test_update_task_only_priority(db_session, test_user, test_task):
    """Test updating only priority field."""
    # Arrange
    original_title = test_task.title
    update_data = TaskUpdate(priority=PriorityEnum.critical)

    # Act
    updated_task = update_task(db_session, test_task.id, update_data, test_user.id)

    # Assert
    assert updated_task.priority == PriorityEnum.critical
    assert updated_task.title == original_title


def test_update_task_without_tags_preserves_existing(
    db_session, test_user, test_task_with_tags
):
    """Test updating without tags field preserves existing tags."""
    # Arrange
    original_tags = set(test_task_with_tags.tags)
    update_data = TaskUpdate(title="Updated Title")
    # Note: tags not included in update_data

    # Act
    updated_task = update_task(
        db_session, test_task_with_tags.id, update_data, test_user.id
    )

    # Assert
    assert updated_task.title == "Updated Title"
    assert set(updated_task.tags) == original_tags


def test_update_task_partial_with_new_tags(
    db_session, test_user, test_task_with_tags
):
    """Test partial update with tags replaces tags but preserves other fields."""
    # Arrange
    original_description = test_task_with_tags.description
    update_data = TaskUpdate(tags=["new-tag"])

    # Act
    updated_task = update_task(
        db_session, test_task_with_tags.id, update_data, test_user.id
    )

    # Assert
    assert updated_task.tags == ["new-tag"]
    assert updated_task.description == original_description
```

**Acceptance Criteria:**
- [ ] All test cases written and pass
- [ ] Tests verify only provided fields updated
- [ ] Tests verify tags preserved when not provided
- [ ] Tests verify tags replaced when provided
- [ ] Tests cover various partial update combinations

---

### Task 4: Verify/Enhance Service Layer Implementation
**Priority:** P0 (Critical)
**Estimated Time:** 1 hour
**TDD Phase:** GREEN

**Description:**
Verify the existing service layer implementation passes all tests, enhance if needed.

**Steps:**
1. Run unit tests from Tasks 2 and 3
2. Verify `update_task` function handles all test cases
3. Ensure `exclude_unset=True` is used for partial updates
4. Verify tag replacement logic (delete existing + insert new)
5. Verify timestamp update logic
6. Fix any failing tests

**Implementation Checklist:**
```python
def update_task(
    session: Session,
    task_id: UUID,
    task_data: TaskUpdate,
    user_id: UUID
) -> Optional[Task]:
    """Update a task with full or partial data."""
    # [ ] Fetch task by ID
    # [ ] Verify task exists
    # [ ] Verify user owns task (return None if not)
    # [ ] Extract only provided fields (exclude_unset=True)
    # [ ] Update task fields (excluding tags)
    # [ ] Update updated_at timestamp
    # [ ] Handle tags if provided:
    #     [ ] Delete all existing tags
    #     [ ] Insert new tags
    #     [ ] Skip if tags field not in update_data
    # [ ] Commit transaction
    # [ ] Refresh task
    # [ ] Load tags for response
    # [ ] Return updated task
```

**Acceptance Criteria:**
- [ ] All unit tests from Tasks 2 and 3 pass
- [ ] Service function uses exclude_unset for partial updates
- [ ] Tag replacement logic works correctly
- [ ] Timestamp updated on every change
- [ ] User isolation enforced
- [ ] Code follows type hints and docstring standards

---

### Task 5: Integration Test - PUT Endpoint
**Priority:** P0 (Critical)
**Estimated Time:** 1 hour
**TDD Phase:** RED

**Description:**
Write integration tests for PUT endpoint with full request/response cycle.

**Test Cases:**
```python
def test_put_task_success(client, auth_headers, test_user, test_task):
    """Test PUT successfully updates all task fields."""
    # Arrange
    url = f"/users/{test_user.id}/tasks/{test_task.id}"
    payload = {
        "title": "Fully Updated Task",
        "description": "Completely new description",
        "completed": True,
        "priority": "high",
        "tags": ["updated", "tags"]
    }

    # Act
    response = client.put(url, json=payload, headers=auth_headers)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Fully Updated Task"
    assert data["description"] == "Completely new description"
    assert data["completed"] is True
    assert data["priority"] == "high"
    assert set(data["tags"]) == {"updated", "tags"}
    assert "updated_at" in data


def test_put_task_replaces_tags(client, auth_headers, test_user, test_task_with_tags):
    """Test PUT replaces all existing tags."""
    # Arrange
    url = f"/users/{test_user.id}/tasks/{test_task_with_tags.id}"
    payload = {
        "title": "Updated",
        "completed": False,
        "priority": "medium",
        "tags": ["brand", "new", "tags"]
    }

    # Act
    response = client.put(url, json=payload, headers=auth_headers)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert set(data["tags"]) == {"brand", "new", "tags"}


def test_put_task_removes_tags(client, auth_headers, test_user, test_task_with_tags):
    """Test PUT with empty tags removes all tags."""
    # Arrange
    url = f"/users/{test_user.id}/tasks/{test_task_with_tags.id}"
    payload = {
        "title": "No Tags",
        "completed": False,
        "priority": "low",
        "tags": []
    }

    # Act
    response = client.put(url, json=payload, headers=auth_headers)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["tags"] == []


def test_put_task_unauthorized_user(
    client, auth_headers, test_user, other_user, test_task
):
    """Test PUT returns 403 when user doesn't own task."""
    # Arrange
    url = f"/users/{other_user.id}/tasks/{test_task.id}"
    payload = {"title": "Hacked", "completed": True, "priority": "high"}

    # Act
    response = client.put(url, json=payload, headers=auth_headers)

    # Assert
    assert response.status_code == 403


def test_put_task_not_found(client, auth_headers, test_user):
    """Test PUT returns 404 for non-existent task."""
    # Arrange
    fake_task_id = uuid4()
    url = f"/users/{test_user.id}/tasks/{fake_task_id}"
    payload = {"title": "Ghost", "completed": False, "priority": "medium"}

    # Act
    response = client.put(url, json=payload, headers=auth_headers)

    # Assert
    assert response.status_code == 404


def test_put_task_validation_error(client, auth_headers, test_user, test_task):
    """Test PUT returns 422 for invalid data."""
    # Arrange
    url = f"/users/{test_user.id}/tasks/{test_task.id}"
    payload = {
        "title": "",  # Empty title invalid
        "completed": False,
        "priority": "invalid-priority"  # Invalid enum
    }

    # Act
    response = client.put(url, json=payload, headers=auth_headers)

    # Assert
    assert response.status_code == 422


def test_put_task_no_auth(client, test_user, test_task):
    """Test PUT returns 401 without authentication."""
    # Arrange
    url = f"/users/{test_user.id}/tasks/{test_task.id}"
    payload = {"title": "Unauthorized", "completed": False, "priority": "medium"}

    # Act
    response = client.put(url, json=payload)

    # Assert
    assert response.status_code == 401
```

**Acceptance Criteria:**
- [ ] All PUT endpoint test cases written
- [ ] Tests cover success scenarios
- [ ] Tests cover error scenarios (403, 404, 422, 401)
- [ ] Tests verify tag replacement
- [ ] Tests verify user isolation

---

### Task 6: Integration Test - PATCH Endpoint
**Priority:** P0 (Critical)
**Estimated Time:** 1 hour
**TDD Phase:** RED

**Description:**
Write integration tests for PATCH endpoint with partial update scenarios.

**Test Cases:**
```python
def test_patch_task_only_title(client, auth_headers, test_user, test_task):
    """Test PATCH updates only title field."""
    # Arrange
    url = f"/users/{test_user.id}/tasks/{test_task.id}"
    original = client.get(url, headers=auth_headers).json()
    payload = {"title": "Partially Updated"}

    # Act
    response = client.patch(url, json=payload, headers=auth_headers)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Partially Updated"
    assert data["description"] == original["description"]
    assert data["completed"] == original["completed"]
    assert data["priority"] == original["priority"]


def test_patch_task_toggle_completed(client, auth_headers, test_user, test_task):
    """Test PATCH toggles completion status."""
    # Arrange
    url = f"/users/{test_user.id}/tasks/{test_task.id}"
    original = client.get(url, headers=auth_headers).json()
    payload = {"completed": not original["completed"]}

    # Act
    response = client.patch(url, json=payload, headers=auth_headers)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["completed"] != original["completed"]
    assert data["title"] == original["title"]


def test_patch_task_only_priority(client, auth_headers, test_user, test_task):
    """Test PATCH updates only priority."""
    # Arrange
    url = f"/users/{test_user.id}/tasks/{test_task.id}"
    original = client.get(url, headers=auth_headers).json()
    payload = {"priority": "critical"}

    # Act
    response = client.patch(url, json=payload, headers=auth_headers)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["priority"] == "critical"
    assert data["title"] == original["title"]


def test_patch_task_preserves_tags_when_not_provided(
    client, auth_headers, test_user, test_task_with_tags
):
    """Test PATCH without tags preserves existing tags."""
    # Arrange
    url = f"/users/{test_user.id}/tasks/{test_task_with_tags.id}"
    original = client.get(url, headers=auth_headers).json()
    original_tags = set(original["tags"])
    payload = {"title": "Updated Title"}

    # Act
    response = client.patch(url, json=payload, headers=auth_headers)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert set(data["tags"]) == original_tags


def test_patch_task_replaces_tags_when_provided(
    client, auth_headers, test_user, test_task_with_tags
):
    """Test PATCH with tags replaces existing tags."""
    # Arrange
    url = f"/users/{test_user.id}/tasks/{test_task_with_tags.id}"
    original = client.get(url, headers=auth_headers).json()
    payload = {"tags": ["new-tag-1", "new-tag-2"]}

    # Act
    response = client.patch(url, json=payload, headers=auth_headers)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert set(data["tags"]) == {"new-tag-1", "new-tag-2"}
    assert data["title"] == original["title"]  # Other fields preserved


def test_patch_task_multiple_fields(client, auth_headers, test_user, test_task):
    """Test PATCH updates multiple fields at once."""
    # Arrange
    url = f"/users/{test_user.id}/tasks/{test_task.id}"
    payload = {
        "title": "Multi-Update",
        "completed": True,
        "priority": "high"
    }

    # Act
    response = client.patch(url, json=payload, headers=auth_headers)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Multi-Update"
    assert data["completed"] is True
    assert data["priority"] == "high"


def test_patch_task_unauthorized(client, auth_headers, test_user, other_user, test_task):
    """Test PATCH returns 403 for unauthorized user."""
    # Arrange
    url = f"/users/{other_user.id}/tasks/{test_task.id}"
    payload = {"title": "Hacked"}

    # Act
    response = client.patch(url, json=payload, headers=auth_headers)

    # Assert
    assert response.status_code == 403


def test_patch_task_not_found(client, auth_headers, test_user):
    """Test PATCH returns 404 for non-existent task."""
    # Arrange
    fake_task_id = uuid4()
    url = f"/users/{test_user.id}/tasks/{fake_task_id}"
    payload = {"title": "Ghost"}

    # Act
    response = client.patch(url, json=payload, headers=auth_headers)

    # Assert
    assert response.status_code == 404


def test_patch_task_validation_error(client, auth_headers, test_user, test_task):
    """Test PATCH returns 422 for invalid data."""
    # Arrange
    url = f"/users/{test_user.id}/tasks/{test_task.id}"
    payload = {"priority": "super-duper-urgent"}  # Invalid enum

    # Act
    response = client.patch(url, json=payload, headers=auth_headers)

    # Assert
    assert response.status_code == 422
```

**Acceptance Criteria:**
- [ ] All PATCH endpoint test cases written
- [ ] Tests verify partial update behavior
- [ ] Tests verify tags preserved when not provided
- [ ] Tests verify tags replaced when provided
- [ ] Tests cover error scenarios (403, 404, 422, 401)

---

### Task 7: Verify/Enhance Route Handlers
**Priority:** P0 (Critical)
**Estimated Time:** 30 minutes
**TDD Phase:** GREEN

**Description:**
Verify existing PUT and PATCH route handlers pass all integration tests.

**Steps:**
1. Run integration tests from Tasks 5 and 6
2. Verify route handlers properly call service layer
3. Verify user isolation checks at route level
4. Verify error handling (403, 404, 422)
5. Verify JWT middleware integration
6. Fix any failing tests

**Implementation Checklist (PUT Handler):**
```python
@router.put("/users/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_user_task(...):
    # [ ] Extract user_id from path
    # [ ] Get current_user_id from JWT middleware
    # [ ] Verify user_id match (403 if not)
    # [ ] Call update_task service function
    # [ ] Handle None return (404)
    # [ ] Return updated task (200)
    # [ ] Proper error handling
```

**Implementation Checklist (PATCH Handler):**
```python
@router.patch("/users/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def partial_update_user_task(...):
    # [ ] Extract user_id from path
    # [ ] Get current_user_id from JWT middleware
    # [ ] Verify user_id match (403 if not)
    # [ ] Call update_task service function
    # [ ] Handle None return (404)
    # [ ] Return updated task (200)
    # [ ] Proper error handling
```

**Acceptance Criteria:**
- [ ] All integration tests from Tasks 5 and 6 pass
- [ ] Route handlers implement user isolation
- [ ] Error responses correct (403, 404, 422, 401)
- [ ] JWT middleware integrated correctly
- [ ] Code follows FastAPI best practices

---

### Task 8: Edge Case Testing
**Priority:** P1 (High)
**Estimated Time:** 1 hour
**TDD Phase:** RED + GREEN

**Description:**
Write and verify tests for edge cases and boundary conditions.

**Test Cases:**
```python
def test_update_task_max_title_length(client, auth_headers, test_user, test_task):
    """Test updating with maximum title length (200 chars)."""
    # Arrange
    url = f"/users/{test_user.id}/tasks/{test_task.id}"
    max_title = "a" * 200
    payload = {"title": max_title}

    # Act
    response = client.patch(url, json=payload, headers=auth_headers)

    # Assert
    assert response.status_code == 200
    assert response.json()["title"] == max_title


def test_update_task_title_too_long(client, auth_headers, test_user, test_task):
    """Test updating with title exceeding max length returns 422."""
    # Arrange
    url = f"/users/{test_user.id}/tasks/{test_task.id}"
    too_long_title = "a" * 201
    payload = {"title": too_long_title}

    # Act
    response = client.patch(url, json=payload, headers=auth_headers)

    # Assert
    assert response.status_code == 422


def test_update_task_max_description_length(client, auth_headers, test_user, test_task):
    """Test updating with maximum description length (1000 chars)."""
    # Arrange
    url = f"/users/{test_user.id}/tasks/{test_task.id}"
    max_desc = "a" * 1000
    payload = {"description": max_desc}

    # Act
    response = client.patch(url, json=payload, headers=auth_headers)

    # Assert
    assert response.status_code == 200
    assert response.json()["description"] == max_desc


def test_update_task_description_too_long(client, auth_headers, test_user, test_task):
    """Test updating with description exceeding max length returns 422."""
    # Arrange
    url = f"/users/{test_user.id}/tasks/{test_task.id}"
    too_long_desc = "a" * 1001
    payload = {"description": too_long_desc}

    # Act
    response = client.patch(url, json=payload, headers=auth_headers)

    # Assert
    assert response.status_code == 422


def test_update_task_max_tags(client, auth_headers, test_user, test_task):
    """Test updating with maximum tags (10)."""
    # Arrange
    url = f"/users/{test_user.id}/tasks/{test_task.id}"
    max_tags = [f"tag{i}" for i in range(10)]
    payload = {"tags": max_tags}

    # Act
    response = client.patch(url, json=payload, headers=auth_headers)

    # Assert
    assert response.status_code == 200
    assert len(response.json()["tags"]) == 10


def test_update_task_too_many_tags(client, auth_headers, test_user, test_task):
    """Test updating with more than 10 tags returns 422."""
    # Arrange
    url = f"/users/{test_user.id}/tasks/{test_task.id}"
    too_many_tags = [f"tag{i}" for i in range(11)]
    payload = {"tags": too_many_tags}

    # Act
    response = client.patch(url, json=payload, headers=auth_headers)

    # Assert
    assert response.status_code == 422


def test_update_task_tag_max_length(client, auth_headers, test_user, test_task):
    """Test updating with tag at maximum length (50 chars)."""
    # Arrange
    url = f"/users/{test_user.id}/tasks/{test_task.id}"
    max_tag = "a" * 50
    payload = {"tags": [max_tag]}

    # Act
    response = client.patch(url, json=payload, headers=auth_headers)

    # Assert
    assert response.status_code == 200
    assert response.json()["tags"][0] == max_tag


def test_update_task_tag_too_long(client, auth_headers, test_user, test_task):
    """Test updating with tag exceeding max length returns 422."""
    # Arrange
    url = f"/users/{test_user.id}/tasks/{test_task.id}"
    too_long_tag = "a" * 51
    payload = {"tags": [too_long_tag]}

    # Act
    response = client.patch(url, json=payload, headers=auth_headers)

    # Assert
    assert response.status_code == 422


def test_update_task_empty_title(client, auth_headers, test_user, test_task):
    """Test updating with empty title returns 422."""
    # Arrange
    url = f"/users/{test_user.id}/tasks/{test_task.id}"
    payload = {"title": ""}

    # Act
    response = client.patch(url, json=payload, headers=auth_headers)

    # Assert
    assert response.status_code == 422


def test_update_task_whitespace_title(client, auth_headers, test_user, test_task):
    """Test updating with whitespace-only title returns 422."""
    # Arrange
    url = f"/users/{test_user.id}/tasks/{test_task.id}"
    payload = {"title": "   "}

    # Act
    response = client.patch(url, json=payload, headers=auth_headers)

    # Assert
    assert response.status_code == 422


def test_update_task_special_characters(client, auth_headers, test_user, test_task):
    """Test updating with special characters in fields."""
    # Arrange
    url = f"/users/{test_user.id}/tasks/{test_task.id}"
    payload = {
        "title": "Task with émojis 🚀 and spëcial chars!",
        "description": "Description with <html> & symbols",
        "tags": ["tag-with-dash", "tag_with_underscore", "tag.with.dot"]
    }

    # Act
    response = client.patch(url, json=payload, headers=auth_headers)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "🚀" in data["title"]
    assert "spëcial" in data["title"]


def test_update_task_duplicate_tags_in_request(client, auth_headers, test_user, test_task):
    """Test updating with duplicate tags in same request."""
    # Arrange
    url = f"/users/{test_user.id}/tasks/{test_task.id}"
    payload = {"tags": ["duplicate", "duplicate", "unique"]}

    # Act
    response = client.patch(url, json=payload, headers=auth_headers)

    # Assert
    # Note: Behavior depends on implementation
    # Either accept all (including duplicates) or deduplicate
    assert response.status_code in [200, 422]


def test_update_task_null_description(client, auth_headers, test_user, test_task):
    """Test updating description to null/None."""
    # Arrange
    url = f"/users/{test_user.id}/tasks/{test_task.id}"
    payload = {"description": None}

    # Act
    response = client.patch(url, json=payload, headers=auth_headers)

    # Assert
    assert response.status_code == 200
    assert response.json()["description"] is None
```

**Acceptance Criteria:**
- [ ] All edge case tests written
- [ ] Tests for maximum field lengths
- [ ] Tests for validation errors
- [ ] Tests for special characters
- [ ] Tests for null/empty values
- [ ] All tests pass

---

### Task 9: Test Coverage Verification
**Priority:** P1 (High)
**Estimated Time:** 30 minutes
**TDD Phase:** REFACTOR

**Description:**
Verify test coverage meets requirements (> 95%).

**Steps:**
1. Run pytest with coverage: `pytest --cov=backend/services/task_service --cov=backend/routes/tasks --cov-report=html`
2. Review coverage report
3. Identify uncovered lines
4. Add tests for uncovered code paths
5. Verify final coverage > 95%

**Acceptance Criteria:**
- [ ] Test coverage > 95% for task_service.py
- [ ] Test coverage > 95% for routes/tasks.py
- [ ] All code paths tested
- [ ] Coverage report generated

---

### Task 10: Documentation and Code Review
**Priority:** P1 (High)
**Estimated Time:** 30 minutes

**Description:**
Ensure code is well-documented and ready for review.

**Steps:**
1. Verify all functions have docstrings
2. Verify all functions have type hints
3. Add inline comments for complex logic
4. Update OpenAPI/Swagger docs if needed
5. Review code for style consistency
6. Run linters (black, flake8, mypy)

**Documentation Checklist:**
- [ ] Service functions have docstrings
- [ ] Route handlers have docstrings
- [ ] Type hints on all functions
- [ ] Complex logic has inline comments
- [ ] OpenAPI docs reflect PUT/PATCH endpoints

**Acceptance Criteria:**
- [ ] All code documented
- [ ] Linters pass (no errors)
- [ ] Type checking passes (mypy)
- [ ] Code style consistent
- [ ] Ready for review

---

### Task 11: Performance Testing
**Priority:** P2 (Medium)
**Estimated Time:** 45 minutes

**Description:**
Verify update operations meet performance requirements (< 200ms p95).

**Steps:**
1. Create performance test script
2. Test PUT endpoint with concurrent requests
3. Test PATCH endpoint with concurrent requests
4. Measure latency (p50, p95, p99)
5. Identify bottlenecks if any
6. Optimize if needed

**Performance Test Script:**
```python
import asyncio
import time
from statistics import quantiles

async def benchmark_update_endpoint(num_requests=100):
    """Benchmark task update endpoint."""
    latencies = []

    for _ in range(num_requests):
        start = time.time()
        # Make PATCH request
        response = await client.patch(url, json=payload, headers=headers)
        end = time.time()

        latencies.append((end - start) * 1000)  # Convert to ms

    p50, p95, p99 = quantiles(latencies, n=100)[49], quantiles(latencies, n=100)[94], quantiles(latencies, n=100)[98]

    print(f"Latency p50: {p50:.2f}ms")
    print(f"Latency p95: {p95:.2f}ms")
    print(f"Latency p99: {p99:.2f}ms")

    assert p95 < 200, f"p95 latency {p95:.2f}ms exceeds 200ms target"
```

**Acceptance Criteria:**
- [ ] Performance test script created
- [ ] p95 latency < 200ms for PUT
- [ ] p95 latency < 200ms for PATCH
- [ ] No performance bottlenecks identified
- [ ] Performance results documented

---

### Task 12: Security Review
**Priority:** P1 (High)
**Estimated Time:** 30 minutes

**Description:**
Verify security requirements are met.

**Security Checklist:**
- [ ] JWT authentication required for all endpoints
- [ ] User isolation enforced at route level
- [ ] User isolation enforced at service level
- [ ] 404 returned for both non-existent and unauthorized (no info leakage)
- [ ] Input validation via Pydantic
- [ ] No SQL injection vulnerabilities (SQLModel parameterized queries)
- [ ] No sensitive data in error messages
- [ ] No sensitive data in logs
- [ ] HTTPS required in production (environment config)

**Security Tests:**
```python
def test_update_task_no_jwt_token(client, test_user, test_task):
    """Test update fails without JWT token."""
    url = f"/users/{test_user.id}/tasks/{test_task.id}"
    payload = {"title": "Unauthorized"}

    response = client.patch(url, json=payload)

    assert response.status_code == 401


def test_update_task_invalid_jwt_token(client, test_user, test_task):
    """Test update fails with invalid JWT token."""
    url = f"/users/{test_user.id}/tasks/{test_task.id}"
    payload = {"title": "Hacked"}
    headers = {"Authorization": "Bearer invalid-token"}

    response = client.patch(url, json=payload, headers=headers)

    assert response.status_code == 401


def test_update_task_cross_user_access_blocked(
    client, auth_headers_user1, test_user1, test_user2, test_task_user2
):
    """Test user1 cannot update user2's task."""
    url = f"/users/{test_user2.id}/tasks/{test_task_user2.id}"
    payload = {"title": "Hacked"}

    response = client.patch(url, json=payload, headers=auth_headers_user1)

    assert response.status_code == 403

    # Verify task unchanged
    response_check = client.get(url, headers=auth_headers_user2)
    assert response_check.json()["title"] != "Hacked"
```

**Acceptance Criteria:**
- [ ] All security checks pass
- [ ] Security tests written and passing
- [ ] No vulnerabilities identified
- [ ] Security review documented

---

## Task Summary

### Critical Path (P0)
1. Task 1: Review existing implementation (30 min)
2. Task 2: Unit tests - full update (45 min)
3. Task 3: Unit tests - partial update (45 min)
4. Task 4: Verify/enhance service layer (1 hour)
5. Task 5: Integration tests - PUT (1 hour)
6. Task 6: Integration tests - PATCH (1 hour)
7. Task 7: Verify/enhance route handlers (30 min)

**Total Critical Path Time:** ~5.5 hours

### High Priority (P1)
8. Task 8: Edge case testing (1 hour)
9. Task 9: Test coverage verification (30 min)
10. Task 10: Documentation and review (30 min)
12. Task 12: Security review (30 min)

**Total High Priority Time:** ~2.5 hours

### Medium Priority (P2)
11. Task 11: Performance testing (45 min)

**Total Estimated Time:** ~8.75 hours

---

## Test Fixtures Needed

```python
# backend/tests/conftest.py

@pytest.fixture
def test_task(db_session, test_user):
    """Create a test task."""
    task = Task(
        title="Test Task",
        description="Test Description",
        completed=False,
        priority="medium",
        user_id=test_user.id
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    return task


@pytest.fixture
def test_task_with_tags(db_session, test_user):
    """Create a test task with tags."""
    task = Task(
        title="Task With Tags",
        description="Description",
        completed=False,
        priority="medium",
        user_id=test_user.id
    )
    db_session.add(task)
    db_session.flush()

    # Add tags
    tag1 = TaskTag(task_id=task.id, tag_name="tag1")
    tag2 = TaskTag(task_id=task.id, tag_name="tag2")
    db_session.add(tag1)
    db_session.add(tag2)
    db_session.commit()
    db_session.refresh(task)

    return task


@pytest.fixture
def other_user(db_session):
    """Create another user for testing user isolation."""
    user = User(
        username="otheruser",
        email="other@example.com",
        password_hash="hashed_password"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers with JWT token."""
    token = create_jwt_token(user_id=str(test_user.id))
    return {"Authorization": f"Bearer {token}"}
```

---

## Success Criteria

### Functionality
- ✅ PUT endpoint updates all fields correctly
- ✅ PATCH endpoint updates only provided fields
- ✅ Tags replaced when provided in update
- ✅ Tags preserved when not provided in PATCH
- ✅ User isolation enforced (403 on mismatch)
- ✅ Proper error responses (403, 404, 422, 401)

### Quality
- ✅ Test coverage > 95%
- ✅ All tests passing
- ✅ No linting errors
- ✅ Type hints on all functions
- ✅ Comprehensive docstrings

### Performance
- ✅ p95 latency < 200ms
- ✅ No N+1 query problems
- ✅ Database indexes utilized

### Security
- ✅ User isolation verified
- ✅ No SQL injection vulnerabilities
- ✅ No information leakage
- ✅ JWT authentication enforced

---

## Dependencies

### Completed Features
- ✅ 005-database-foundation: Database models (Task, TaskTag)
- ✅ 006-jwt-auth-middleware: JWT authentication
- ✅ 007-auth-endpoints: User signup/login
- ✅ 008-task-crud-endpoints: Task create, get, delete

### Environment
- ✅ DATABASE_URL configured
- ✅ BETTER_AUTH_SECRET configured
- ✅ Python 3.11+ with UV
- ✅ FastAPI, SQLModel, Pytest installed

---

## Notes

- The implementation already exists in routes/tasks.py and services/task_service.py
- Focus is on verifying implementation and adding comprehensive tests
- If implementation gaps found, enhance as needed during GREEN phase
- Follow TDD cycle: RED (write tests) → GREEN (verify/fix code) → REFACTOR (improve)
- Prioritize user isolation and security throughout
- Tag management uses full replacement strategy (simpler than delta approach)
- PATCH without tags preserves existing tags (uses exclude_unset=True)
