---
name: secure-resource-access
description: Implement secure resource retrieval and deletion with user isolation and proper error handling. Use when building GET/DELETE endpoints, fetching single resources, or implementing secure deletion with ownership verification in FastAPI.
---

# Secure Resource Access Skill

## Purpose
Implement secure resource retrieval and deletion with user isolation and proper error handling.

## Context
Used for GET and DELETE operations that must verify user ownership before allowing access.

## Pattern
```python
from fastapi import APIRouter, HTTPException, Depends, Request
from sqlmodel import select

router = APIRouter(prefix="/api/users/{user_id}/tasks", tags=["Tasks"])

@router.get("/{task_id}")
async def get_task(
    user_id: str,
    task_id: str,
    req: Request,
    session: Session = Depends(get_session)
):
    # User isolation check
    if str(req.state.user_id) != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    # Query with user ownership check (prevents cross-user access)
    task = session.exec(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    ).first()
    
    if not task:
        # Returns 404 even if task exists but belongs to different user
        # This prevents information disclosure
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Fetch related entities
    tags = session.exec(select(TaskTag).where(TaskTag.task_id == task_id)).all()
    task.tags = [tag.tag_name for tag in tags]
    
    return task

@router.delete("/{task_id}", status_code=200)
async def delete_task(
    user_id: str,
    task_id: str,
    req: Request,
    session: Session = Depends(get_session)
):
    # User isolation check
    if str(req.state.user_id) != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    # Query with user ownership check
    task = session.exec(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Delete task (cascade will remove related tags)
    session.delete(task)
    session.commit()
    
    return {"message": "Task deleted successfully"}