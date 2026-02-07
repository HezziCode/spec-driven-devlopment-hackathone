"""
Simple Rate Limiting using FastAPI dependencies (without SlowAPI).

Uses in-memory storage with timestamps. For production, consider Redis.
"""

import time
from typing import Dict, Tuple
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


# In-memory storage: {identifier: [(timestamp, count)]}
_rate_limit_storage: Dict[str, list] = {}


def get_identifier(request: Request) -> str:
    """Get unique identifier for rate limiting (IP or user)."""
    # Try to get Authorization header for logged-in users
    auth = request.headers.get("authorization", "")
    if auth:
        return f"user:{hash(auth)}"

    # Fall back to IP
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0]
    return request.client.host if request.client else "unknown"


def check_rate_limit(
    request: Request,
    max_requests: int,
    window_seconds: int,
    error_message_en: str = "Too many requests. Please try again later.",
    error_message_ur: str = "Bohat zyada requests. Thodi der baad try karein."
):
    """
    Check if request exceeds rate limit.

    Args:
        request: FastAPI request object
        max_requests: Maximum requests allowed in window
        window_seconds: Time window in seconds
        error_message_en: English error message
        error_message_ur: Urdu error message

    Raises:
        HTTPException 429 if rate limit exceeded
    """
    identifier = get_identifier(request)
    current_time = time.time()

    # Clean old entries
    if identifier in _rate_limit_storage:
        _rate_limit_storage[identifier] = [
            ts for ts in _rate_limit_storage[identifier]
            if current_time - ts < window_seconds
        ]
    else:
        _rate_limit_storage[identifier] = []

    # Check limit
    request_count = len(_rate_limit_storage[identifier])

    if request_count >= max_requests:
        raise HTTPException(
            status_code=429,
            detail={
                "error": error_message_en,
                "message": error_message_en,
                "message_ur": error_message_ur,
                "retry_after_seconds": window_seconds,
                "code": "RATE_LIMIT_EXCEEDED"
            }
        )

    # Add current request
    _rate_limit_storage[identifier].append(current_time)


# Pre-configured rate limiters as dependencies
def rate_limit_login(request: Request):
    """Rate limit for login: 5 requests per minute"""
    check_rate_limit(
        request,
        max_requests=5,
        window_seconds=60,
        error_message_en="Too many login attempts. Please wait before trying again.",
        error_message_ur="Bohat zyada login attempts. Thodi der baad try karein."
    )


def rate_limit_signup(request: Request):
    """Rate limit for signup: 3 requests per minute"""
    check_rate_limit(
        request,
        max_requests=3,
        window_seconds=60,
        error_message_en="Too many signup attempts. Please wait before trying again.",
        error_message_ur="Bohat zyada signup attempts. Thodi der baad try karein."
    )


def rate_limit_auth_general(request: Request):
    """Rate limit for general auth: 20 requests per minute"""
    check_rate_limit(
        request,
        max_requests=20,
        window_seconds=60,
        error_message_en="Too many authentication requests. Please wait.",
        error_message_ur="Bohat zyada authentication requests. Intezaar karein."
    )


def rate_limit_task_write(request: Request):
    """Rate limit for task creation/updates: 30 per minute"""
    check_rate_limit(
        request,
        max_requests=30,
        window_seconds=60,
        error_message_en="You're creating tasks too quickly. Please slow down.",
        error_message_ur="Aap bohat jaldi tasks bana rahe hain. Thoda slow karein."
    )


def rate_limit_task_delete(request: Request):
    """Rate limit for task deletion: 20 per minute"""
    check_rate_limit(
        request,
        max_requests=20,
        window_seconds=60,
        error_message_en="You're deleting tasks too quickly. Please slow down.",
        error_message_ur="Aap bohat jaldi tasks delete kar rahe hain. Thoda slow karein."
    )


def rate_limit_chat(request: Request):
    """Rate limit for chat: 10 messages per minute"""
    check_rate_limit(
        request,
        max_requests=10,
        window_seconds=60,
        error_message_en="You're sending messages too quickly. Please wait a moment.",
        error_message_ur="Aap bohat jaldi messages bhej rahe hain. Thoda intezaar karein."
    )
