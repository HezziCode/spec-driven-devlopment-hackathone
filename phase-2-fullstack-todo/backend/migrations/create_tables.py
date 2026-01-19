"""
Database migration script to create all tables.

Creates User, Task, and TaskTag tables with proper indexes, foreign keys,
and constraints in the Neon PostgreSQL database.

Usage:
    python migrations/create_tables.py
"""

import logging
import os
import sys

from sqlmodel import SQLModel, text

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from db import engine
except ValueError as e:
    print(f"❌ Configuration error: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def verify_tables() -> bool:
    """
    Verify that all required tables exist in the database.

    Returns:
        bool: True if all tables exist, False otherwise.
    """
    logger.info("Verifying table existence...")

    expected_tables = {"users", "tasks", "task_tags"}

    try:
        from sqlmodel import Session

        with Session(engine) as session:
            # Query information_schema to get list of tables
            result = session.exec(
                text(
                    """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
            """
                )
            )

            existing_tables = {row[0] for row in result}

            missing_tables = expected_tables - existing_tables

            if missing_tables:
                logger.error(f"Missing tables: {missing_tables}")
                return False

            logger.info(f"✅ All required tables exist: {expected_tables}")

            # Verify column counts for each table
            for table in expected_tables:
                result = session.exec(
                    text(
                        f"""
                    SELECT COUNT(*)
                    FROM information_schema.columns
                    WHERE table_name = '{table}'
                    AND table_schema = 'public'
                """
                    )
                )
                column_count = result.first()[0]
                logger.info(f"   Table '{table}' has {column_count} columns")

            return True

    except Exception as e:
        logger.error(f"❌ Table verification failed: {e}")
        return False


def verify_indexes() -> bool:
    """
    Verify that all required indexes exist in the database.

    Returns:
        bool: True if all indexes exist, False otherwise.
    """
    logger.info("Verifying indexes...")

    expected_indexes = {
        # User table indexes
        "ix_users_username",
        "ix_users_email",
        # Task table indexes
        "ix_tasks_user_id",
        "ix_tasks_completed",
        "ix_tasks_priority",
        "idx_user_completed",  # Composite index
        # TaskTag table indexes
        "ix_task_tags_task_id",
        "ix_task_tags_tag_name",
    }

    try:
        from sqlmodel import Session

        with Session(engine) as session:
            # Query pg_indexes to get list of indexes
            result = session.exec(
                text(
                    """
                SELECT indexname
                FROM pg_indexes
                WHERE schemaname = 'public'
                AND tablename IN ('users', 'tasks', 'task_tags')
            """
                )
            )

            existing_indexes = {row[0] for row in result}

            # Check for expected indexes (some might have different names)
            found_count = 0
            for expected_idx in expected_indexes:
                if expected_idx in existing_indexes:
                    logger.info(f"   ✅ Index '{expected_idx}' exists")
                    found_count += 1

            # Also log all indexes found
            logger.info(f"\nAll indexes found ({len(existing_indexes)}):")
            for idx in sorted(existing_indexes):
                logger.info(f"   - {idx}")

            if found_count < len(expected_indexes):
                logger.warning(
                    f"⚠️  Some expected indexes not found ({found_count}/{len(expected_indexes)})"
                )

            return True

    except Exception as e:
        logger.error(f"❌ Index verification failed: {e}")
        return False


def verify_foreign_keys() -> bool:
    """
    Verify that all required foreign key constraints exist.

    Returns:
        bool: True if all foreign keys exist, False otherwise.
    """
    logger.info("Verifying foreign key constraints...")

    try:
        from sqlmodel import Session

        with Session(engine) as session:
            # Query pg_constraint for foreign keys
            result = session.exec(
                text(
                    """
                SELECT
                    tc.constraint_name,
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                    AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_schema = 'public'
                AND tc.table_name IN ('tasks', 'task_tags')
            """
                )
            )

            foreign_keys = list(result)

            if not foreign_keys:
                logger.warning("⚠️  No foreign key constraints found")
                return False

            logger.info(f"✅ Found {len(foreign_keys)} foreign key constraint(s):")
            for fk in foreign_keys:
                logger.info(f"   - {fk[1]}.{fk[2]} -> {fk[3]}.{fk[4]} ({fk[0]})")

            # Verify specific foreign keys
            expected_fks = [
                ("tasks", "user_id", "users", "id"),
                ("task_tags", "task_id", "tasks", "id"),
            ]

            for expected_fk in expected_fks:
                found = any(
                    fk[1] == expected_fk[0]
                    and fk[2] == expected_fk[1]
                    and fk[3] == expected_fk[2]
                    and fk[4] == expected_fk[3]
                    for fk in foreign_keys
                )
                if found:
                    logger.info(
                        f"   ✅ FK {expected_fk[0]}.{expected_fk[1]} -> {expected_fk[2]}.{expected_fk[3]}"
                    )
                else:
                    logger.warning(
                        f"   ⚠️  FK {expected_fk[0]}.{expected_fk[1]} -> {expected_fk[2]}.{expected_fk[3]} not found"
                    )

            return True

    except Exception as e:
        logger.error(f"❌ Foreign key verification failed: {e}")
        return False


def verify_unique_constraints() -> bool:
    """
    Verify that unique constraints exist on the database tables.

    Returns:
        bool: True if unique constraints exist, False otherwise.
    """
    logger.info("Verifying unique constraints...")

    try:
        from sqlmodel import Session

        with Session(engine) as session:
            # Query for unique constraints
            result = session.exec(
                text(
                    """
                SELECT
                    tc.constraint_name,
                    tc.table_name,
                    kcu.column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                WHERE tc.constraint_type = 'UNIQUE'
                AND tc.table_schema = 'public'
                AND tc.table_name IN ('users', 'tasks', 'task_tags')
                ORDER BY tc.table_name, tc.constraint_name
            """
                )
            )

            constraints = list(result)

            if not constraints:
                logger.warning("⚠️  No unique constraints found")
                return False

            logger.info(f"✅ Found {len(constraints)} unique constraint(s):")
            for constraint in constraints:
                logger.info(f"   - {constraint[1]}.{constraint[2]} ({constraint[0]})")

            return True

    except Exception as e:
        logger.error(f"❌ Unique constraint verification failed: {e}")
        return False


def create_tables() -> bool:
    """
    Create all database tables with indexes and constraints.

    Creates User, Task, and TaskTag tables idempotently (won't fail if
    tables already exist). Also verifies table creation and constraints.

    Returns:
        bool: True if tables created/verified successfully, False otherwise.
    """
    try:
        logger.info("Creating database tables...")

        # Create all tables defined in SQLModel metadata
        # checkfirst=True makes this idempotent
        SQLModel.metadata.create_all(engine, checkfirst=True)

        logger.info("✅ Table creation complete")

        # Run verification steps
        verification_passed = True

        if not verify_tables():
            verification_passed = False

        if not verify_indexes():
            logger.warning("⚠️  Some indexes may be missing (this might be okay)")

        if not verify_foreign_keys():
            verification_passed = False

        if not verify_unique_constraints():
            logger.warning("⚠️  Some unique constraints may be missing")

        if verification_passed:
            logger.info("\n✅ Migration completed successfully!")
            logger.info("All tables, foreign keys verified.")
            return True
        else:
            logger.error("\n❌ Migration completed with warnings/errors")
            logger.error(
                "Some verification checks failed. Please review the logs above."
            )
            return False

    except Exception as e:
        logger.error(f"❌ Table creation failed: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error("\nTroubleshooting:")
        logger.error("1. Verify DATABASE_URL is correctly configured in .env")
        logger.error("2. Check database server is running and accessible")
        logger.error("3. Ensure database user has CREATE TABLE permissions")
        logger.error("4. Verify network connectivity to database")
        return False


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Database Migration: Create Tables")
    logger.info("=" * 60)

    success = create_tables()

    if success:
        logger.info("\n" + "=" * 60)
        logger.info("✨ Migration successful! Database is ready.")
        logger.info("=" * 60)
        sys.exit(0)
    else:
        logger.error("\n" + "=" * 60)
        logger.error("❌ Migration failed. Please fix errors and try again.")
        logger.error("=" * 60)
        sys.exit(1)
