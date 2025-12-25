#!/usr/bin/env python3
"""
Generate JWT test tokens for manual testing of authentication middleware.

This script generates valid JWT tokens that can be used with curl or other
HTTP clients to test protected API endpoints.

Usage:
    python scripts/generate_test_token.py
    python scripts/generate_test_token.py --user-id "custom-user-id" --email "user@example.com"
    python scripts/generate_test_token.py --expired  # Generate an expired token
"""

import os
import sys
from datetime import datetime, timedelta, UTC
from pathlib import Path

# Add parent directory to path so we can import from backend
sys.path.insert(0, str(Path(__file__).parent.parent))

from jose import jwt
from dotenv import load_dotenv
import argparse

# Load environment variables from parent directory
load_dotenv(Path(__file__).parent.parent / ".env")


def generate_token(
    user_id: str = "test-user-123",
    email: str = "test@example.com",
    expired: bool = False
) -> str:
    """
    Generate a JWT token for testing.

    Args:
        user_id: User ID to include in the token (default: "test-user-123").
        email: Email address to include in the token (default: "test@example.com").
        expired: Whether to generate an expired token (default: False).

    Returns:
        str: JWT token string.

    Raises:
        ValueError: If BETTER_AUTH_SECRET is not set in environment.
    """
    secret = os.getenv("BETTER_AUTH_SECRET")
    if not secret:
        raise ValueError(
            "BETTER_AUTH_SECRET environment variable is not set. "
            "Please set it in your .env file."
        )

    # Create payload
    now = datetime.now(UTC)
    if expired:
        exp_time = now - timedelta(hours=1)  # Expired 1 hour ago
        iat_time = now - timedelta(hours=2)
    else:
        exp_time = now + timedelta(hours=24)  # Valid for 24 hours
        iat_time = now

    payload = {
        "sub": user_id,
        "email": email,
        "exp": exp_time,
        "iat": iat_time
    }

    # Generate token
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Generate JWT tokens for testing authentication middleware"
    )
    parser.add_argument(
        "--user-id",
        default="test-user-123",
        help="User ID to include in the token (default: test-user-123)"
    )
    parser.add_argument(
        "--email",
        default="test@example.com",
        help="Email address to include in the token (default: test@example.com)"
    )
    parser.add_argument(
        "--expired",
        action="store_true",
        help="Generate an expired token for testing expiration handling"
    )

    args = parser.parse_args()

    try:
        token = generate_token(
            user_id=args.user_id,
            email=args.email,
            expired=args.expired
        )

        print("\n" + "=" * 80)
        print("JWT Token Generated Successfully")
        print("=" * 80)
        print(f"\nUser ID: {args.user_id}")
        print(f"Email: {args.email}")
        print(f"Status: {'EXPIRED' if args.expired else 'VALID (24 hours)'}")
        print("\nToken:")
        print(token)
        print("\n" + "=" * 80)
        print("Usage Example:")
        print("=" * 80)
        print(f'\ncurl -H "Authorization: Bearer {token}" \\')
        print('     http://localhost:8000/api/users/me')
        print("\n" + "=" * 80 + "\n")

    except ValueError as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
