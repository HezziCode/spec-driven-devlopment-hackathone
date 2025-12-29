"""
OAuth service for Google authentication token verification and user management.

Provides functions for verifying Google ID tokens, creating users from Google profiles,
and managing account linking for OAuth authentication.
"""

from typing import Optional, Dict, Any
from google.oauth2 import id_token
from google.auth.transport import requests
from sqlmodel import Session, select, func
from uuid import uuid4
from datetime import datetime, timedelta, timezone
import os
import json
from dotenv import load_dotenv
from jose import jwt

from models import User

# Load environment variables
load_dotenv()

# Google OAuth configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
if not GOOGLE_CLIENT_ID:
    raise ValueError(
        "GOOGLE_OAUTH_CLIENT_ID environment variable is not set. "
        "Please configure Google OAuth credentials in your .env file."
    )

# Better Auth secret for linking tokens
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")
if not BETTER_AUTH_SECRET:
    raise ValueError("BETTER_AUTH_SECRET environment variable is not set.")


def verify_google_token(token: str) -> Dict[str, Any]:
    """
    Verify Google ID token and extract user claims.

    Args:
        token: Google ID token from OAuth callback.

    Returns:
        Dict containing verified Google user claims (sub, email, name, picture, etc.).

    Raises:
        ValueError: If token is invalid, expired, or audience mismatch.
        Exception: For other token verification failures.

    Example:
        >>> claims = verify_google_token(id_token_string)
        >>> print(claims['email'])  # user@gmail.com
        >>> print(claims['sub'])    # Google user ID
    """
    try:
        # Verify the token using Google's public keys
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )

        # Verify issuer
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Invalid token issuer')

        # Return verified claims
        return idinfo

    except ValueError as e:
        # Invalid token (expired, wrong audience, etc.)
        raise ValueError(f"Invalid Google token: {str(e)}")
    except Exception as e:
        # Other verification errors
        raise Exception(f"Google token verification failed: {str(e)}")


def find_user_by_google_id(session: Session, google_id: str) -> Optional[User]:
    """
    Find user by Google ID.

    Args:
        session: Database session.
        google_id: Google user ID from OAuth.

    Returns:
        User object if found, None otherwise.

    Example:
        >>> user = find_user_by_google_id(session, "123456789")
        >>> if user:
        >>>     print(f"Found user: {user.email}")
    """
    statement = select(User).where(User.google_id == google_id)
    result = session.exec(statement)
    return result.first()


def find_user_by_email(session: Session, email: str) -> Optional[User]:
    """
    Find user by email address.

    Args:
        session: Database session.
        email: User's email address.

    Returns:
        User object if found, None otherwise.

    Example:
        >>> user = find_user_by_email(session, "user@example.com")
        >>> if user:
        >>>     print(f"User auth provider: {user.auth_provider}")
    """
    statement = select(User).where(func.lower(User.email) == email.lower())
    result = session.exec(statement)
    return result.first()


def create_user_from_google_profile(
    session: Session,
    google_claims: Dict[str, Any]
) -> User:
    """
    Create new user from Google OAuth profile.

    Args:
        session: Database session.
        google_claims: Verified Google ID token claims.

    Returns:
        Newly created User object.

    Raises:
        ValueError: If required claims are missing or user already exists.

    Example:
        >>> claims = verify_google_token(token)
        >>> user = create_user_from_google_profile(session, claims)
        >>> print(f"Created user: {user.email}")
    """
    # Extract required claims
    google_id = google_claims.get('sub')
    email = google_claims.get('email')
    name = google_claims.get('name', email.split('@')[0])

    if not google_id or not email:
        raise ValueError("Missing required Google claims (sub, email)")

    # Check if Google ID already exists
    existing_user = find_user_by_google_id(session, google_id)
    if existing_user:
        raise ValueError(f"User with Google ID {google_id} already exists")

    # Create username from Google name or email
    base_username = name.replace(' ', '_').lower()
    username = base_username
    counter = 1

    # Ensure username uniqueness
    while True:
        stmt = select(User).where(User.username == username)
        if not session.exec(stmt).first():
            break
        username = f"{base_username}{counter}"
        counter += 1

    # Create new user
    oauth_profile_data = {
        "name": google_claims.get('name'),
        "picture": google_claims.get('picture'),
        "given_name": google_claims.get('given_name'),
        "family_name": google_claims.get('family_name'),
        "locale": google_claims.get('locale'),
    }

    new_user = User(
        id=uuid4(),
        username=username,
        email=email,
        password_hash=None,  # OAuth users don't have passwords
        auth_provider="google",
        google_id=google_id,
        oauth_data=json.dumps(oauth_profile_data),  # Store as JSON string
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user


def link_google_account(
    session: Session,
    user: User,
    google_id: str,
    google_claims: Dict[str, Any]
) -> User:
    """
    Link Google account to existing user.

    Args:
        session: Database session.
        user: Existing user to link Google account to.
        google_id: Google user ID to link.
        google_claims: Google profile claims for oauth_data.

    Returns:
        Updated User object with linked Google account.

    Raises:
        ValueError: If Google ID is already linked to different user.

    Example:
        >>> user = find_user_by_email(session, "user@example.com")
        >>> updated_user = link_google_account(session, user, google_id, claims)
        >>> print(f"Linked Google account to {updated_user.email}")
    """
    # Check if Google ID is already linked to different user
    existing_google_user = find_user_by_google_id(session, google_id)
    if existing_google_user and existing_google_user.id != user.id:
        raise ValueError(
            f"Google account is already linked to a different user (ID: {existing_google_user.id})"
        )

    # Update user with Google account link
    oauth_profile_data = {
        "name": google_claims.get('name'),
        "picture": google_claims.get('picture'),
        "given_name": google_claims.get('given_name'),
        "family_name": google_claims.get('family_name'),
        "locale": google_claims.get('locale'),
    }

    user.google_id = google_id
    user.oauth_data = json.dumps(oauth_profile_data)  # Store as JSON string
    user.updated_at = datetime.utcnow()

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


def generate_linking_token(user_id: str, email: str, google_id: str) -> str:
    """
    Generate temporary JWT token for account linking confirmation.

    Args:
        user_id: User's UUID.
        email: User's email address.
        google_id: Google user ID to link.

    Returns:
        JWT token valid for 5 minutes.

    Example:
        >>> token = generate_linking_token(str(user.id), user.email, google_id)
        >>> # Token can be used to confirm account linking
    """
    now = datetime.now(timezone.utc)
    expiration = now + timedelta(minutes=5)

    payload = {
        "sub": user_id,
        "email": email,
        "google_id": google_id,
        "action": "link_google_account",
        "exp": expiration,
        "iat": now
    }

    token = jwt.encode(payload, BETTER_AUTH_SECRET, algorithm="HS256")
    return token


def verify_linking_token(token: str) -> Dict[str, Any]:
    """
    Verify account linking token.

    Args:
        token: JWT linking token.

    Returns:
        Dict containing token claims (sub, email, google_id).

    Raises:
        Exception: If token is invalid or expired.

    Example:
        >>> claims = verify_linking_token(linking_token)
        >>> user_id = claims['sub']
        >>> google_id = claims['google_id']
    """
    try:
        claims = jwt.decode(token, BETTER_AUTH_SECRET, algorithms=["HS256"])

        # Verify action
        if claims.get('action') != 'link_google_account':
            raise ValueError("Invalid token action")

        return claims
    except Exception as e:
        raise Exception(f"Invalid linking token: {str(e)}")


# Export public API
__all__ = [
    "verify_google_token",
    "find_user_by_google_id",
    "find_user_by_email",
    "create_user_from_google_profile",
    "link_google_account",
    "generate_linking_token",
    "verify_linking_token"
]
