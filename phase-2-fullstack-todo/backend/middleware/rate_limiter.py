"""
Rate Limiting Middleware using SlowAPI

Protects API endpoints from abuse with user-friendly error messages.
Different limits for different endpoint types:
- AI/Chat endpoints: Strict (expensive API calls)
- Auth endpoints: Medium (prevent brute force)
- Task endpoints: Normal (regular usage)
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse
import os


def get_user_identifier(request: Request) -> str:
    """
    Get unique identifier for rate limiting.
    Uses user ID if authenticated, otherwise falls back to IP address.
    """
    # Try to get user from JWT token in header
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        # Use token hash as identifier (more accurate than IP for logged-in users)
        token = auth_header[7:]
        return f"user:{hash(token)}"

    # Fall back to IP address for unauthenticated requests
    return get_remote_address(request)


# Initialize limiter with user identifier
limiter = Limiter(key_func=get_user_identifier)


# Rate limit configurations (can be overridden via env vars)
RATE_LIMITS = {
    # AI/Chat - Very strict (OpenAI API is expensive!)
    "chat": os.getenv("RATE_LIMIT_CHAT", "10/minute"),  # 10 messages per minute
    "ai_agent": os.getenv("RATE_LIMIT_AI", "5/minute"),  # 5 AI agent calls per minute

    # Auth - Medium strict (prevent brute force attacks)
    "login": os.getenv("RATE_LIMIT_LOGIN", "5/minute"),  # 5 login attempts per minute
    "signup": os.getenv("RATE_LIMIT_SIGNUP", "3/minute"),  # 3 signups per minute
    "auth_general": os.getenv("RATE_LIMIT_AUTH", "20/minute"),  # General auth endpoints

    # Tasks - Normal usage
    "task_read": os.getenv("RATE_LIMIT_TASK_READ", "60/minute"),  # 60 reads per minute
    "task_write": os.getenv("RATE_LIMIT_TASK_WRITE", "30/minute"),  # 30 creates/updates per minute
    "task_delete": os.getenv("RATE_LIMIT_TASK_DELETE", "20/minute"),  # 20 deletes per minute

    # General API
    "default": os.getenv("RATE_LIMIT_DEFAULT", "100/minute"),  # Default for other endpoints
}


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """
    Custom handler for rate limit exceeded errors.
    Returns user-friendly message in both English and Urdu.
    """
    # Parse the limit info
    limit_info = str(exc.detail)

    # Determine which type of endpoint was hit
    path = request.url.path.lower()

    if "chat" in path or "message" in path:
        message_en = "You're sending messages too quickly. Please wait a moment before sending another message."
        message_ur = "Aap bohat jaldi messages bhej rahe hain. Thoda intezaar karein."
        retry_after = 60
    elif "auth" in path or "login" in path or "signup" in path:
        message_en = "Too many login attempts. Please wait before trying again."
        message_ur = "Bohat zyada login attempts. Thodi der baad try karein."
        retry_after = 60
    elif "task" in path:
        message_en = "You're performing actions too quickly. Please slow down."
        message_ur = "Aap bohat jaldi actions kar rahe hain. Thoda slow karein."
        retry_after = 30
    else:
        message_en = "Too many requests. Please wait before trying again."
        message_ur = "Bohat zyada requests. Thodi der baad try karein."
        retry_after = 60

    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "message": message_en,
            "message_ur": message_ur,
            "retry_after_seconds": retry_after,
            "detail": limit_info,
            "code": "RATE_LIMIT_EXCEEDED"
        },
        headers={
            "Retry-After": str(retry_after),
            "X-RateLimit-Limit": limit_info,
        }
    )


# Decorator shortcuts for common limits
def limit_chat(func):
    """Rate limit for chat/AI endpoints - Very strict"""
    return limiter.limit(RATE_LIMITS["chat"])(func)


def limit_ai_agent(func):
    """Rate limit for AI agent endpoints - Very strict"""
    return limiter.limit(RATE_LIMITS["ai_agent"])(func)


def limit_login(func):
    """Rate limit for login endpoint"""
    return limiter.limit(RATE_LIMITS["login"])(func)


def limit_signup(func):
    """Rate limit for signup endpoint"""
    return limiter.limit(RATE_LIMITS["signup"])(func)


def limit_auth(func):
    """Rate limit for general auth endpoints"""
    return limiter.limit(RATE_LIMITS["auth_general"])(func)


def limit_task_read(func):
    """Rate limit for reading tasks"""
    return limiter.limit(RATE_LIMITS["task_read"])(func)


def limit_task_write(func):
    """Rate limit for creating/updating tasks"""
    return limiter.limit(RATE_LIMITS["task_write"])(func)


def limit_task_delete(func):
    """Rate limit for deleting tasks"""
    return limiter.limit(RATE_LIMITS["task_delete"])(func)


def limit_default(func):
    """Default rate limit"""
    return limiter.limit(RATE_LIMITS["default"])(func)
