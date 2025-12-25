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
from datetime import datetime, timedelta, UTC
from uuid import UUID
import os
from dotenv import load_dotenv

from db import get_session
from models import User
from schemas.auth import SignupRequest, LoginRequest, UserResponse, AuthResponse

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
    now = datetime.now(UTC)
    expiration = now + timedelta(days=JWT_EXPIRATION_DAYS)

    payload = {
        "sub": str(user_id),  # Subject (user ID)
        "email": email,
        "exp": expiration,  # Expiration time
        "iat": now  # Issued at time
    }

    token = jwt.encode(payload, BETTER_AUTH_SECRET, algorithm=JWT_ALGORITHM)
    return token


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
            "timestamp": datetime.now(UTC).isoformat()
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
        user_response = UserResponse.model_validate(new_user)
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
        user_response = UserResponse.model_validate(user)
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
