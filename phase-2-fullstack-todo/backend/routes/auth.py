"""
Authentication route handlers for signup, login, and logout endpoints.

Implements user registration with password hashing, authentication with JWT token
generation, and stateless logout functionality following FastAPI Auth Endpoints skill.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlmodel import Session, select, func
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone
from uuid import UUID
import os
from dotenv import load_dotenv

from db import get_session
from models import User
from schemas.auth import (
    SignupRequest,
    LoginRequest,
    UserResponse,
    AuthResponse,
    GoogleOAuthCallback,
    AccountLinkingRequired,
    GoogleLinkConfirm
)
from services.oauth_service import (
    verify_google_token,
    find_user_by_google_id,
    find_user_by_email,
    create_user_from_google_profile,
    link_google_account,
    generate_linking_token,
    verify_linking_token
)

# Load environment variables
load_dotenv()

# Password hashing context with bcrypt 12 rounds
pwd_context = CryptContext(schemes=["bcrypt"], bcrypt__rounds=12, deprecated="auto")

# JWT configuration
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")
if not BETTER_AUTH_SECRET:
    raise ValueError(
        "BETTER_AUTH_SECRET environment variable is not set. "
        "Please configure BETTER_AUTH_SECRET in your .env file."
    )

JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DAYS = 7

# Create router
router = APIRouter(prefix="/auth", tags=["authentication"])


def create_jwt_token(user_id: UUID, email: str) -> str:
    """
    Create a JWT token for authenticated user.

    Args:
        user_id: User's unique identifier (UUID).
        email: User's email address.

    Returns:
        str: Encoded JWT token string with 7-day expiration.

    Example:
        >>> token = create_jwt_token(user.id, user.email)
        >>> # Token contains: sub, email, exp, iat claims
    """
    now = datetime.now(timezone.utc)
    expiration = now + timedelta(days=JWT_EXPIRATION_DAYS)

    payload = {
        "sub": str(user_id),  # Subject (user ID)
        "email": email,
        "exp": expiration,  # Expiration time
        "iat": now  # Issued at time
    }

    token = jwt.encode(payload, BETTER_AUTH_SECRET, algorithm=JWT_ALGORITHM)
    return token


def create_user_response(user: User) -> UserResponse:
    """
    Create UserResponse from User model with profile picture extraction.

    Extracts profile picture URL from oauth_data JSON if available.

    Args:
        user: User model instance.

    Returns:
        UserResponse with profile picture extracted from oauth_data.
    """
    import json

    profile_picture = None
    if user.oauth_data:
        try:
            # Parse oauth_data if it's a string
            oauth_dict = json.loads(user.oauth_data) if isinstance(user.oauth_data, str) else user.oauth_data
            profile_picture = oauth_dict.get('picture')
        except (json.JSONDecodeError, AttributeError, TypeError):
            pass

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        created_at=user.created_at,
        profile_picture=profile_picture,
        auth_provider=user.auth_provider
    )


def error_response(status_code: int, message: str, code: str) -> JSONResponse:
    """
    Create standardized error response.

    Args:
        status_code: HTTP status code for the error.
        message: Human-readable error message.
        code: Machine-readable error code.

    Returns:
        JSONResponse: Standardized error response with timestamp.

    Example:
        >>> return error_response(409, "Username already exists", "DUPLICATE_USERNAME")
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "error": message,
            "code": code,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account with username, email, and password. Returns user data and JWT token."
)
async def signup_user(
    request: SignupRequest,
    session: Session = Depends(get_session)
) -> AuthResponse:
    """
    Register a new user with password hashing and JWT token generation.

    Validates username and email uniqueness (case-insensitive for email),
    hashes password with bcrypt 12 rounds, and generates JWT token with 7-day expiration.

    Args:
        request: Signup request containing username, email, and password.
        session: Database session for user creation.

    Returns:
        AuthResponse: User data (excluding password_hash) and JWT token.

    Raises:
        HTTPException 409: Username or email already exists.
        HTTPException 422: Validation errors (handled by Pydantic).
        HTTPException 500: Database or server errors.
    """
    try:
        # Check username uniqueness
        existing_username = session.exec(
            select(User).where(User.username == request.username)
        ).first()

        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"error": "Username already exists", "code": "DUPLICATE_USERNAME"}
            )

        # Check email uniqueness (case-insensitive)
        existing_email = session.exec(
            select(User).where(func.lower(User.email) == request.email.lower())
        ).first()

        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"error": "Email already exists", "code": "DUPLICATE_EMAIL"}
            )

        # Hash password with bcrypt 12 rounds
        password_hash = pwd_context.hash(request.password)

        # Create new user with normalized email (lowercase)
        new_user = User(
            username=request.username,
            email=request.email.lower(),
            password_hash=password_hash
        )

        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        # Generate JWT token
        token = create_jwt_token(new_user.id, new_user.email)

        # Create response with user data (excluding password_hash)
        user_response = create_user_response(new_user)
        return AuthResponse(user=user_response, token=token)

    except HTTPException:
        # Re-raise HTTP exceptions (validation errors, duplicates)
        raise
    except Exception as e:
        # Log unexpected errors and return 500
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error during signup", "code": "SERVER_ERROR"}
        )


@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate user",
    description="Authenticate user with email and password. Returns user data and JWT token."
)
async def login_user(
    request: LoginRequest,
    session: Session = Depends(get_session)
) -> AuthResponse:
    """
    Authenticate user and generate JWT token.

    Performs case-insensitive email lookup, verifies password using constant-time
    comparison, and generates JWT token with 7-day expiration on success.

    Args:
        request: Login request containing email and password.
        session: Database session for user lookup.

    Returns:
        AuthResponse: User data (excluding password_hash) and JWT token.

    Raises:
        HTTPException 401: Invalid credentials (wrong password or user not found).
        HTTPException 422: Validation errors (handled by Pydantic).
        HTTPException 500: Database or server errors.

    Security Notes:
        - Returns same error message for wrong password and nonexistent user
        - Uses constant-time password comparison to prevent timing attacks
        - Email lookup is case-insensitive
    """
    try:
        # Query user by email (case-insensitive)
        user = session.exec(
            select(User).where(func.lower(User.email) == request.email.lower())
        ).first()

        # Return 401 if user not found (same message as wrong password for security)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": "Invalid credentials", "code": "INVALID_CREDENTIALS"}
            )

        # Verify password using constant-time comparison
        is_valid_password = pwd_context.verify(request.password, user.password_hash)

        if not is_valid_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": "Invalid credentials", "code": "INVALID_CREDENTIALS"}
            )

        # Generate JWT token
        token = create_jwt_token(user.id, user.email)

        # Create response with user data (excluding password_hash)
        user_response = create_user_response(user)
        return AuthResponse(user=user_response, token=token)

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log unexpected errors and return 500
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal server error during login", "code": "SERVER_ERROR"}
        )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout user",
    description="Logout endpoint for stateless JWT authentication. Client should discard token."
)
async def logout_user() -> dict:
    """
    Logout user (stateless operation).

    Since JWT tokens are stateless, logout is handled client-side by discarding
    the token. This endpoint always returns success to confirm the operation.

    Returns:
        dict: Success message confirming logout.

    Notes:
        - No authentication required (stateless JWT)
        - No database operations performed
        - Client is responsible for discarding the JWT token
        - Token will remain valid until expiration (7 days)
        - For immediate revocation, implement token blacklist (future enhancement)
    """
    return {"message": "Successfully logged out"}


@router.post(
    "/google/callback",
    response_model=AuthResponse | AccountLinkingRequired,
    status_code=status.HTTP_200_OK,
    summary="Google OAuth callback",
    description="Handle Google OAuth callback with ID token verification and user creation or authentication."
)
async def google_oauth_callback(
    request: GoogleOAuthCallback,
    session: Session = Depends(get_session)
) -> AuthResponse | AccountLinkingRequired:
    """
    Handle Google OAuth callback and create or authenticate user.

    Flow:
    1. Verify Google ID token
    2. Check if user exists by google_id → authenticate existing Google user
    3. Check if user exists by email → require account linking confirmation
    4. Create new user from Google profile

    Args:
        request: Google OAuth callback containing ID token.
        session: Database session.

    Returns:
        AuthResponse: JWT token and user data for new/existing Google user.
        AccountLinkingRequired: Linking token and confirmation required for email match.

    Raises:
        HTTPException 400: Invalid Google token.
        HTTPException 500: Server errors.
    """
    try:
        # Verify Google ID token
        try:
            google_claims = verify_google_token(request.id_token)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": f"Invalid Google token: {str(e)}", "code": "INVALID_GOOGLE_TOKEN"}
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": f"Token verification failed: {str(e)}", "code": "TOKEN_VERIFICATION_FAILED"}
            )

        google_id = google_claims.get('sub')
        email = google_claims.get('email')

        if not google_id or not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "Missing required Google claims (sub, email)", "code": "MISSING_CLAIMS"}
            )

        # Check if user exists with this google_id (returning Google user)
        existing_google_user = find_user_by_google_id(session, google_id)
        if existing_google_user:
            # Existing Google user - authenticate
            token = create_jwt_token(existing_google_user.id, existing_google_user.email)
            user_response = create_user_response(existing_google_user)
            return AuthResponse(user=user_response, token=token)

        # Check if user exists with this email (email/password user)
        existing_email_user = find_user_by_email(session, email)
        if existing_email_user and existing_email_user.auth_provider == "local":
            # Email/password user exists - require account linking confirmation
            linking_token = generate_linking_token(
                str(existing_email_user.id),
                existing_email_user.email,
                google_id
            )
            return AccountLinkingRequired(
                requires_confirmation=True,
                email=email,
                linking_token=linking_token,
                message=f"An account with email {email} already exists. Do you want to link your Google account to this existing account?"
            )

        # New Google user - create account
        try:
            new_user = create_user_from_google_profile(session, google_claims)
            token = create_jwt_token(new_user.id, new_user.email)
            user_response = create_user_response(new_user)
            return AuthResponse(user=user_response, token=token)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": str(e), "code": "USER_CREATION_FAILED"}
            )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log unexpected errors and return 500
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": f"Internal server error during OAuth callback: {str(e)}", "code": "SERVER_ERROR"}
        )


@router.post(
    "/google/link-confirm",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Confirm Google account linking",
    description="Confirm linking Google account to existing email/password account after user confirmation."
)
async def google_link_confirm(
    request: GoogleLinkConfirm,
    session: Session = Depends(get_session)
) -> AuthResponse:
    """
    Confirm Google account linking to existing user account.

    Args:
        request: Linking confirmation containing linking_token and confirm flag.
        session: Database session.

    Returns:
        AuthResponse: JWT token and user data with linked Google account.

    Raises:
        HTTPException 400: Invalid linking token or user not found.
        HTTPException 403: User rejected linking (confirm=False).
        HTTPException 500: Server errors.
    """
    try:
        # Verify linking token
        try:
            claims = verify_linking_token(request.linking_token)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": f"Invalid linking token: {str(e)}", "code": "INVALID_LINKING_TOKEN"}
            )

        # Check if user rejected linking
        if not request.confirm:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"error": "Account linking cancelled by user", "code": "LINKING_CANCELLED"}
            )

        user_id = claims['sub']
        google_id = claims['google_id']

        # Find user
        user = session.get(User, UUID(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "User not found", "code": "USER_NOT_FOUND"}
            )

        # Verify Google token to get fresh claims
        # (In production, you'd store google_claims in the linking token or re-verify)
        # For now, create minimal oauth_data
        oauth_data_minimal = {"google_id": google_id, "linked_at": datetime.now(timezone.utc).isoformat()}

        # Link Google account
        try:
            updated_user = link_google_account(
                session,
                user,
                google_id,
                oauth_data_minimal  # Store minimal data for now
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": str(e), "code": "LINKING_FAILED"}
            )

        # Generate new JWT token
        token = create_jwt_token(updated_user.id, updated_user.email)
        user_response = create_user_response(updated_user)
        return AuthResponse(user=user_response, token=token)

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log unexpected errors and return 500
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": f"Internal server error during linking confirmation: {str(e)}", "code": "SERVER_ERROR"}
        )
