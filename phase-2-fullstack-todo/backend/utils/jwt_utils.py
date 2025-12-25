"""
JWT utility functions for token validation and user extraction.

Provides comprehensive JWT token operations including decoding, verification,
and user extraction from database based on token claims.
"""

import os
from typing import Optional, Any, Dict
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError
from sqlmodel import Session, select
from dotenv import load_dotenv
from models import User

# Load environment variables
load_dotenv()

# Get BETTER_AUTH_SECRET from environment
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")

# Validate secret exists
if not BETTER_AUTH_SECRET:
    raise ValueError(
        "BETTER_AUTH_SECRET environment variable is not set. "
        "Please configure BETTER_AUTH_SECRET in your .env file."
    )


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode a JWT token and return the payload.

    This function verifies the token signature and returns the decoded payload.
    Raises exceptions for invalid or expired tokens.

    Args:
        token: JWT token string to decode.

    Returns:
        dict[str, Any]: Decoded JWT payload containing claims.

    Raises:
        ExpiredSignatureError: If the token has expired.
        JWTError: If the token signature is invalid or token is malformed.

    Example:
        >>> token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        >>> payload = decode_token(token)
        >>> print(payload["sub"])  # User ID
        'user-123'
        >>> print(payload["email"])
        'user@example.com'

    Note:
        This function raises exceptions instead of returning None to allow
        callers to handle different error cases appropriately.
    """
    # Decode and verify token using BETTER_AUTH_SECRET
    payload = jwt.decode(
        token,
        BETTER_AUTH_SECRET,
        algorithms=["HS256"]
    )
    return payload


def verify_token(token: str) -> bool:
    """
    Verify if a JWT token is valid without raising exceptions.

    This function attempts to decode the token and returns a boolean
    indicating validity. Useful for conditional checks where you don't
    want to handle exceptions.

    Args:
        token: JWT token string to verify.

    Returns:
        bool: True if token is valid, False if expired or invalid.

    Example:
        >>> token = generate_jwt_token()
        >>> if verify_token(token):
        ...     print("Token is valid")
        ... else:
        ...     print("Token is invalid or expired")

    Note:
        This function catches all JWT-related errors and returns False.
        For detailed error information, use decode_token() instead.
    """
    try:
        decode_token(token)
        return True
    except (JWTError, ExpiredSignatureError):
        return False
    except Exception:
        # Catch any unexpected errors
        return False


def extract_user_from_token(token: str, session: Session) -> Optional[User]:
    """
    Extract user information from JWT token and fetch User from database.

    This function decodes the JWT token, extracts the user ID from the 'sub'
    claim, and queries the database to retrieve the corresponding User object.

    Args:
        token: JWT token string containing user identity.
        session: SQLModel database session for querying.

    Returns:
        Optional[User]: User object if found in database, None otherwise.

    Raises:
        No exceptions raised - returns None for all error cases.

    Example:
        >>> from db import get_session
        >>> with Session(engine) as session:
        ...     user = extract_user_from_token(token, session)
        ...     if user:
        ...         print(f"Found user: {user.email}")
        ...     else:
        ...         print("User not found")

    Note:
        - Returns None if token is invalid or expired
        - Returns None if user_id is missing from token
        - Returns None if user is not found in database
        - Safe to use without try/except blocks
    """
    try:
        # Decode token to get payload
        payload = decode_token(token)

        # Extract user ID from 'sub' claim
        user_id_str = payload.get("sub")
        if not user_id_str:
            return None

        # Convert string UUID to UUID type for database query
        from uuid import UUID
        try:
            user_id = UUID(user_id_str)
        except (ValueError, TypeError):
            # Invalid UUID format
            return None

        # Query database for user using session.get() which is more efficient
        user = session.get(User, user_id)

        return user

    except (JWTError, ExpiredSignatureError):
        # Token is invalid or expired
        return None
    except Exception:
        # Database error or other unexpected error
        return None
