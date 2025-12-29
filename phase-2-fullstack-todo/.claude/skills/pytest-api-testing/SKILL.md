---
name: pytest-api-testing
description: Write comprehensive test suites for FastAPI applications using Pytest. Use when testing API endpoints, authentication, authorization, user isolation, or business logic.
---

# Pytest API Testing

## Purpose

Write comprehensive test suites for FastAPI applications using Pytest.

## Context

Used for testing API endpoints, authentication, authorization, and business logic.

## Pattern

```python
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from app.main import app
from app.models import User, Task
from app.db import get_session

# Test database
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})

@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture(name="test_user")
def test_user_fixture(client: TestClient):
    response = client.post("/auth/signup", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    })
    data = response.json()
    return {"user": data["user"], "token": data["token"]}

def test_create_task(client: TestClient, test_user: dict):
    headers = {"Authorization": f"Bearer {test_user['token']}"}
    response = client.post(
        f"/api/users/{test_user['user']['id']}/tasks",
        headers=headers,
        json={"title": "Test Task", "priority": "high", "tags": ["work"]}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["priority"] == "high"
    assert "work" in data["tags"]

def test_cross_user_access_blocked(client: TestClient, test_user: dict):
    # Create second user
    response2 = client.post("/auth/signup", json={
        "username": "user2",
        "email": "user2@example.com",
        "password": "pass123"
    })
    user2 = response2.json()

    # User 1 creates task
    headers1 = {"Authorization": f"Bearer {test_user['token']}"}
    response = client.post(
        f"/api/users/{test_user['user']['id']}/tasks",
        headers=headers1,
        json={"title": "User 1 Task"}
    )
    task_id = response.json()["id"]

    # User 2 tries to access User 1's task
    headers2 = {"Authorization": f"Bearer {user2['token']}"}
    response = client.get(
        f"/api/users/{user2['user']['id']}/tasks/{task_id}",
        headers=headers2
    )
    assert response.status_code == 404  # Not 403, to prevent info disclosure