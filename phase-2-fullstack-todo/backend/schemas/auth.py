"""
Authentication Pydantic schemas for request and response validation.

Provides schemas for signup, login, and authentication responses.
All schemas enforce validation rules and exclude sensitive data from responses.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SignupRequest(BaseModel):
    """
    Schema for user signup request.

    Validates username (3-50 chars), email format, and password (8+ chars).
    """

    username: str = Field(
        ..., min_length=3, max_length=50, description="Username must be 3-50 characters"
    )
    email: EmailStr = Field(..., description="Valid email address required")
    password: str = Field(
        ..., min_length=8, description="Password must be at least 8 characters"
    )


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
    Contains only safe user information including OAuth profile data.
    """

    model_config = ConfigDict(from_attributes=True)  # Allow creating from ORM models

    id: UUID = Field(..., description="Unique user identifier")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    created_at: datetime = Field(..., description="Account creation timestamp")
    profile_picture: Optional[str] = Field(
        None, description="URL to user's profile picture (from OAuth)"
    )
    auth_provider: Optional[str] = Field(
        None, description="Authentication provider (local or google)"
    )


class AuthResponse(BaseModel):
    """
    Schema for authentication response containing user data and JWT token.

    Returned after successful signup or login.
    """

    user: UserResponse = Field(..., description="Authenticated user information")
    token: str = Field(..., description="JWT authentication token")


class GoogleOAuthCallback(BaseModel):
    """
    Schema for Google OAuth callback request.

    Contains the Google ID token received from OAuth flow.
    """

    id_token: str = Field(..., description="Google ID token from OAuth callback")
    state: Optional[str] = Field(None, description="CSRF protection state parameter")


class GoogleLinkConfirm(BaseModel):
    """
    Schema for confirming Google account linking.

    Used when user confirms linking their Google account to existing email/password account.
    """

    linking_token: str = Field(
        ..., description="Temporary JWT token for account linking confirmation"
    )
    confirm: bool = Field(
        ..., description="User confirmation (true to link, false to cancel)"
    )


class AccountLinkingRequired(BaseModel):
    """
    Schema for account linking confirmation response.

    Returned when Google email matches existing email/password account.
    """

    requires_confirmation: bool = Field(
        default=True, description="Indicates account linking requires confirmation"
    )
    email: str = Field(
        ..., description="Email address that requires linking confirmation"
    )
    linking_token: str = Field(
        ..., description="Temporary token to complete account linking"
    )
    message: str = Field(
        ..., description="User-friendly message explaining the situation"
    )
