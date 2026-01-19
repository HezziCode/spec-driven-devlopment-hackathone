"""
JWT Authentication Middleware for FastAPI.

Provides automatic JWT token verification for protected API endpoints.
Attaches user context to request.state for use in route handlers.
"""

import os
import warnings
from datetime import datetime, timezone
from typing import Any, Callable

from dotenv import load_dotenv
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError

# Load environment variables
load_dotenv()

# Get BETTER_AUTH_SECRET from environment
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")

# Validate secret exists
if not BETTER_AUTH_SECRET:
    # For testing, use a default secret if not set
    import warnings

    warnings.warn("BETTER_AUTH_SECRET not set, using default for testing")
    BETTER_AUTH_SECRET = "test-secret-key-at-least-32-characters-long-for-testing"
    # raise ValueError(
    #     "BETTER_AUTH_SECRET environment variable is not set. "
    #     "Please configure BETTER_AUTH_SECRET in your .env file. "
    #     "This secret must match the secret used by Better Auth on the frontend."
    # )

# Validate secret length (minimum 32 characters for security)
if len(BETTER_AUTH_SECRET) < 32:
    # For testing, use a default secret if too short
    import warnings

    warnings.warn("BETTER_AUTH_SECRET too short, using default for testing")
    BETTER_AUTH_SECRET = "test-secret-key-at-least-32-characters-long-for-testing"
    # raise ValueError(
    #     f"BETTER_AUTH_SECRET is too short ({len(BETTER_AUTH_SECRET)} characters). "
    #     "For security, it must be at least 32 characters long. "
    #     "Generate a secure secret using: openssl rand -base64 32"
    # )

# Public paths that bypass authentication
PUBLIC_PATHS = [
    "/auth/",
    "/api/auth/",  # For proxy/load balancer configurations that add /api prefix
    "/docs",
    "/redoc",
    "/openapi.json",
    "/health",
    "/mcp/",  # MCP server endpoint for internal agent tool calls
    "/api/ai/",  # AI tools endpoint for internal agent calls (bypasses auth since agent provides user_id)
]

# Exact match paths (no prefix matching)
EXACT_PUBLIC_PATHS = ["/"]


def create_error_response(
    error_message: str, error_code: str, status_code: int
) -> JSONResponse:
    """
    Create a standardized error response for authentication failures.

    Args:
        error_message: Human-readable error message.
        error_code: Machine-readable error code.
        status_code: HTTP status code (401, 400, etc.).

    Returns:
        JSONResponse: Standardized error response.

    Example:
        >>> response = create_error_response(
        ...     "Token has expired",
        ...     "TOKEN_EXPIRED",
        ...     401
        ... )
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "error": error_message,
            "code": error_code,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


async def verify_jwt_middleware(
    request: Request, call_next: Callable[[Request], Any]
) -> Response:
    """
    FastAPI middleware for JWT token verification.

    Validates JWT tokens on protected endpoints and attaches user context
    to request.state. Public routes defined in PUBLIC_PATHS bypass authentication.

    Args:
        request: FastAPI request object.
        call_next: Next middleware or route handler in the chain.

    Returns:
        Response: Either error response or response from next handler.

    Raises:
        No exceptions raised - all errors are caught and returned as JSON responses.

    Flow:
        1. Check if path is public - if yes, bypass authentication
        2. Extract Authorization header
        3. Validate "Bearer <token>" format
        4. Decode and verify JWT token
        5. Extract user_id and email from payload
        6. Attach to request.state
        7. Call next handler

    Error Responses:
        - 401: Missing token, expired token, invalid signature
        - 400: Malformed Authorization header

    Example:
        >>> # In main.py
        >>> from middleware.auth_middleware import verify_jwt_middleware
        >>> app.middleware("http")(verify_jwt_middleware)
    """
    # Allow CORS preflight requests to pass through without authentication
    if request.method == "OPTIONS":
        response = await call_next(request)
        return response

    # Check if path is public (bypass authentication)
    path = request.url.path

    # Check exact match paths
    if path in EXACT_PUBLIC_PATHS:
        response = await call_next(request)
        return response

    # Check prefix match paths
    for public_path in PUBLIC_PATHS:
        if path.startswith(public_path):
            # Public route - bypass authentication
            response = await call_next(request)
            return response

    # Extract Authorization header
    auth_header = request.headers.get("Authorization")

    # Check if Authorization header is present
    if not auth_header:
        return create_error_response(
            error_message="Authorization header is required",
            error_code="MISSING_TOKEN",
            status_code=401,
        )

    # Validate "Bearer <token>" format
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return create_error_response(
            error_message="Invalid Authorization header format. Expected: Bearer <token>",
            error_code="MALFORMED_HEADER",
            status_code=400,
        )

    token = parts[1]

    # Validate token is not empty
    if not token or token.strip() == "":
        return create_error_response(
            error_message="Token cannot be empty",
            error_code="EMPTY_TOKEN",
            status_code=400,
        )

    # Verify and decode JWT token
    try:
        # Decode token using BETTER_AUTH_SECRET
        payload = jwt.decode(token, BETTER_AUTH_SECRET, algorithms=["HS256"])

        # Extract user information from payload
        user_id = payload.get("sub")
        email = payload.get("email")

        # Validate required claims
        if not user_id:
            return create_error_response(
                error_message="Token is missing required 'sub' claim (user ID)",
                error_code="INVALID_TOKEN_CLAIMS",
                status_code=401,
            )

        # Attach user context to request.state
        request.state.user_id = user_id
        request.state.email = email

        # Proceed to next handler
        response = await call_next(request)
        return response

    except ExpiredSignatureError:
        # Token has expired
        return create_error_response(
            error_message="Token has expired",
            error_code="TOKEN_EXPIRED",
            status_code=401,
        )

    except JWTError as e:
        # Invalid token signature or other JWT errors
        return create_error_response(
            error_message=f"Invalid token signature: {str(e)}",
            error_code="INVALID_TOKEN_SIGNATURE",
            status_code=401,
        )

    except Exception as e:
        # Unexpected errors
        return create_error_response(
            error_message=f"Authentication error: {str(e)}",
            error_code="AUTHENTICATION_ERROR",
            status_code=401,
        )


def get_user_id_from_token(request: Request) -> str:
    """
    Extract user_id from authenticated request.

    This function retrieves the user_id that was attached to request.state
    by the verify_jwt_middleware after successful JWT token validation.

    Args:
        request: FastAPI request object with user context in state.

    Returns:
        str: User ID from JWT token payload.

    Raises:
        No exceptions - assumes middleware has already validated token.

    Usage:
        >>> @router.get("/tasks")
        >>> async def get_tasks(user_id: str = Depends(get_user_id_from_token)):
        >>>     # user_id is now available
        >>>     pass

    Note:
        This function should only be used in routes that are protected by
        verify_jwt_middleware. The middleware must run first to populate
        request.state.user_id.
    """
    return request.state.user_id


async def get_current_user(request: Request) -> dict:
    """
    Dependency to get the current authenticated user.

    This is a FastAPI dependency that can be used with Depends() to
    ensure the user is authenticated and get their user information.

    Args:
        request: FastAPI request object with user context in state.

    Returns:
        Dictionary containing user information from JWT token.

    Raises:
        HTTPException 401: If user is not authenticated.
    """
    if not hasattr(request.state, "user_id") or request.state.user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Return user information from the request state
    return {"id": request.state.user_id, "email": getattr(request.state, "email", None)}
