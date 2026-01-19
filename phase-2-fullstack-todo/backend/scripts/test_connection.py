"""
Database connection test script.

Tests the database connection to Neon PostgreSQL and verifies it's working correctly.
Run this script manually to verify your DATABASE_URL configuration.

Usage:
    python scripts/test_connection.py
"""

import os
import sys

from sqlmodel import Session, text

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from db import engine
except ValueError as e:
    print(f"❌ Database configuration error: {e}")
    sys.exit(1)


def test_connection() -> None:
    """
    Test database connection by executing a simple query.

    Attempts to create a session and execute SELECT 1 to verify connectivity.
    Prints success message with database host information or error details.
    """
    try:
        # Create a session and execute a simple query
        with Session(engine) as session:
            result = session.exec(text("SELECT 1 as test")).first()

            if result and result[0] == 1:
                # Extract database host from engine URL
                db_host = engine.url.host
                db_database = engine.url.database
                db_driver = engine.url.drivername

                print("✅ Database connection successful!")
                print(f"   Driver: {db_driver}")
                print(f"   Host: {db_host}")
                print(f"   Database: {db_database}")
                print(f"   Query result: {result[0]}")
            else:
                print(
                    "⚠️  Database connection established but query returned unexpected result."
                )
                print(f"   Expected: 1, Got: {result}")

    except Exception as e:
        print("❌ Database connection failed!")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Verify DATABASE_URL is set in your .env file")
        print("2. Check your Neon PostgreSQL connection string is correct")
        print("3. Ensure your database is running and accessible")
        print("4. Verify your network connection allows PostgreSQL connections")
        sys.exit(1)


if __name__ == "__main__":
    print("🔍 Testing database connection...\n")
    test_connection()
    print("\n✨ Connection test complete!")
