"""
Middleware for JWT authentication and request processing.

This module provides middleware for automatic JWT token verification
on protected endpoints.
"""

from middleware.auth_middleware import verify_jwt_middleware

__all__ = ["verify_jwt_middleware"]
