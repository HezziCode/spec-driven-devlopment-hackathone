"""
User profile service layer.

Handles business logic for user profile operations including
retrieval and updates with duplicate checking.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func
from sqlmodel import Session, select

from models import User
from schemas.user import UpdateUserRequest


def get_user_profile(session: Session, user_id: UUID) -> Optional[User]:
    """
    Retrieve user profile by ID.

    Args:
        session: Database session
        user_id: User's unique identifier

    Returns:
        User model if found, None otherwise
    """
    return session.get(User, user_id)


def update_user_profile(
    session: Session, user_id: UUID, request: UpdateUserRequest
) -> Optional[User]:
    """
    Update user profile with duplicate checking.

    Validates that at least one field is provided and checks for
    duplicate usernames/emails before updating. Usernames are
    case-sensitive, emails are case-insensitive.

    Args:
        session: Database session
        user_id: User's unique identifier
        request: Update request with username and/or email

    Returns:
        Updated User model if successful, None if user not found

    Raises:
        HTTPException: 409 if username/email already taken
        HTTPException: 422 if validation fails (no fields provided)
    """
    # Get user
    user = session.get(User, user_id)
    if not user:
        return None

    # Validate at least one field provided
    if not request.username and not request.email:
        raise HTTPException(
            status_code=422,
            detail="At least one field (username or email) must be provided",
        )

    # Check username duplicate (case-sensitive)
    if request.username:
        existing = session.exec(
            select(User).where(User.username == request.username, User.id != user_id)
        ).first()
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Username '{request.username}' is already taken",
            )
        user.username = request.username

    # Check email duplicate (case-insensitive)
    if request.email:
        existing = session.exec(
            select(User).where(
                func.lower(User.email) == func.lower(request.email), User.id != user_id
            )
        ).first()
        if existing:
            raise HTTPException(
                status_code=409, detail=f"Email '{request.email}' is already taken"
            )
        user.email = request.email

    # Update timestamp and commit
    user.updated_at = datetime.utcnow()
    session.add(user)
    session.commit()
    session.refresh(user)

    return user
