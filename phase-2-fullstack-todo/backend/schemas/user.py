"""
Pydantic schemas for user profile operations.

This module defines request and response models for user profile endpoints.
UserResponse explicitly excludes the password_hash field for security.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserResponse(BaseModel):
    """
    User profile response schema.

    Returns user information without exposing sensitive fields like password_hash.
    Used as the response model for GET and PUT user profile endpoints.

    Attributes:
        id: User's unique identifier (UUID)
        username: User's display name (3-50 characters)
        email: User's email address
        created_at: Account creation timestamp (UTC)
        updated_at: Last profile modification timestamp (UTC)
    """

    id: UUID
    username: str
    email: str
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic configuration."""

        from_attributes = True  # Allows SQLModel → Pydantic conversion


class UpdateUserRequest(BaseModel):
    """
    User profile update request schema.

    Accepts partial updates with optional username and/or email fields.
    At least one field must be provided (validated in service layer).

    Attributes:
        username: Optional new username (3-50 characters)
        email: Optional new email address (valid email format)
    """

    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
