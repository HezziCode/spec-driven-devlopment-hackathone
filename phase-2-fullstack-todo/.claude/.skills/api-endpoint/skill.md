# API Endpoint Skill

## Purpose
Create secure FastAPI routes with SQLModel CRUD operations following best practices for authentication, validation, and error handling.

## Pattern
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
import jwt

from backend.models import Task, TaskCreate, TaskUpdate
from backend.db import get_db
from backend.utils.jwt_utils import verify_jwt_token

router = APIRouter()

@router.post("/tasks", response_model=Task)
async def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(verify_jwt_token)
):
    try:
        # Create task with user_id from JWT
        task = Task(
            **task_data.dict(),
            user_id=current_user_id
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create task")

@router.get("/tasks", response_model=List[Task])
async def get_tasks(
    db: Session = Depends(get_db),
    current_user_id: str = Depends(verify_jwt_token)
):
    try:
        # Filter tasks by user_id to ensure user isolation
        statement = select(Task).where(Task.user_id == current_user_id)
        tasks = db.exec(statement).all()
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch tasks")
```

## Key Components
1. **Authentication**: JWT token verification using dependency injection
2. **Database Session**: SQLModel session management with dependency injection
3. **Pydantic Models**: Request/response validation with Pydantic schemas
4. **Error Handling**: Proper HTTPException usage with appropriate status codes
5. **User Isolation**: Filter data by user_id from JWT token to prevent cross-user access
6. **Async Functions**: Use async/await for non-blocking operations
7. **Transaction Management**: Proper commit/rollback handling

## Security Considerations
- All endpoints must verify JWT tokens
- User data must be isolated by user_id
- Input validation through Pydantic models
- Proper error messages that don't expose system details
- SQL injection prevention through parameterized queries

## MCP Integration
If the specification mentions multi-agent communication or cloud-native tools, this skill should be extended to:
- Include message queue integration for async operations
- Add distributed tracing capabilities
- Implement circuit breaker patterns for external service calls
- Include configuration for multi-cloud deployment scenarios

## Common Variations
- GET endpoints with pagination and filtering
- PUT/PATCH endpoints with proper update validation
- DELETE endpoints with soft delete options
- Search endpoints with full-text search capabilities
- Bulk operation endpoints for performance

## Validation Checklist
- [ ] JWT token verification on all endpoints
- [ ] Proper database session management
- [ ] Pydantic model validation
- [ ] User isolation by user_id
- [ ] Appropriate HTTP status codes
- [ ] Error handling with rollback
- [ ] Async function implementation
- [ ] SQL injection prevention