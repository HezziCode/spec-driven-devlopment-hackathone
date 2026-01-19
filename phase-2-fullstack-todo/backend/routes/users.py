"""
User profile API routes.

Provides endpoints for authenticated users to view and update their profiles.
All endpoints require JWT authentication and enforce user isolation.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from db import get_session
from middleware.auth_middleware import get_user_id_from_token
from schemas.user import UpdateUserRequest, UserResponse
from services.user_service import get_user_profile, update_user_profile

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    current_user_id: str = Depends(get_user_id_from_token),
    session: Session = Depends(get_session),
):
    """
    Get user profile (must be own profile).

    Retrieves authenticated user's profile information.
    Password hash is automatically excluded by response_model.

    Args:
        user_id: User ID from URL path (must match JWT user ID)
        current_user_id: Authenticated user ID from JWT token
        session: Database session

    Returns:
        UserResponse: User profile without password_hash

    Raises:
        HTTPException: 403 if user_id doesn't match authenticated user
        HTTPException: 404 if user not found
    """
    # Verify user_id matches JWT
    if str(user_id) != current_user_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to view this profile"
        )

    # Get profile
    user = get_user_profile(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    request: UpdateUserRequest,
    current_user_id: str = Depends(get_user_id_from_token),
    session: Session = Depends(get_session),
):
    """
    Update user profile (must be own profile).

    Updates authenticated user's username and/or email with duplicate checking.
    At least one field must be provided.

    Args:
        user_id: User ID from URL path (must match JWT user ID)
        request: Update request with username and/or email
        current_user_id: Authenticated user ID from JWT token
        session: Database session

    Returns:
        UserResponse: Updated user profile without password_hash

    Raises:
        HTTPException: 403 if user_id doesn't match authenticated user
        HTTPException: 404 if user not found
        HTTPException: 409 if username/email already taken
        HTTPException: 422 if validation fails
    """
    # Verify user_id matches JWT
    if str(user_id) != current_user_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this profile"
        )

    # Update profile (service handles duplicates and validation)
    try:
        user = update_user_profile(session, user_id, request)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise  # Re-raise 409/422 from service layer
