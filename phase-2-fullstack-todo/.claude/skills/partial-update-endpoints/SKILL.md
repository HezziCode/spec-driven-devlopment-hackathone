---
name: fastapi-partial-update-endpoints
description: Implement PUT (full update) and PATCH (partial update) endpoints with validation and user isolation. Use when building update operations for resources, modifying existing records, or implementing RESTful update patterns in FastAPI.
---

# Partial Update Endpoints Skill

## Purpose
Implement PUT (full update) and PATCH (partial update) endpoints with proper validation and user isolation.

## Context
Used for updating resources with full replacement or partial modification.

## Pydantic Schemas (schemas/task.py)
```python
from pydantic import BaseModel, Field
from typing import Optional, List

class TaskUpdateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str
    completed: bool
    tags: List[str] = []

class TaskPatchRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    completed: Optional[bool] = None
    tags: Optional[List[str]] = None