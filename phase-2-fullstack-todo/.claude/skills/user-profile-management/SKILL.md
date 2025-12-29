---
name: user-profile-management
description: Implement secure user profile retrieval and update with duplicate checking and password exclusion. Use when building user account endpoints, profile management, or any user self-service operations in FastAPI.
---

# User Profile Management Skill

## Purpose
Implement secure user profile retrieval and update with duplicate checking and password exclusion.

## Context
Used for managing user account information with proper security and validation.

## Pydantic Schemas (schemas/user.py)
```python
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Excludes password_hash automatically

class UpdateUserRequest(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None