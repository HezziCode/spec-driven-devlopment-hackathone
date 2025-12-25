"""
Authentication Pydantic schemas for request and response validation.

Provides schemas for signup, login, and authentication responses.
All schemas enforce validation rules and exclude sensitive data from responses.
"""

from pydantic import BaseModel, Field, EmailStr, ConfigDict
from uuid import UUID
from datetime import datetime


class SignupRequest(BaseModel):
    """
    Schema for user signup request.

    Validates username (3-50 chars), email format, and password (8+ chars).
    """
    username: str = Field(..., min_length=3, max_length=50, description="Username must be 3-50 characters")
    email: EmailStr = Field(..., description="Valid email address required")
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")


class LoginRequest(BaseModel):
    """
    Schema for user login request.

    Validates email format and requires password.
    No minimum password length for login (only validated during signup).
    """
    email: EmailStr = Field(..., description="Valid email address required")
    password: str = Field(..., description="Password required for authentication")


class UserResponse(BaseModel):
    """
    Schema for user data in API responses.

    Excludes password_hash for security.
    Contains only safe user information.
    """
    model_config = ConfigDict(from_attributes=True)  # Allow creating from ORM models

    id: UUID = Field(..., description="Unique user identifier")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    created_at: datetime = Field(..., description="Account creation timestamp")


class AuthResponse(BaseModel):
    """
    Schema for authentication response containing user data and JWT token.

    Returned after successful signup or login.
    """
    user: UserResponse = Field(..., description="Authenticated user information")
    token: str = Field(..., description="JWT authentication token")
