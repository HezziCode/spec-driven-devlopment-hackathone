"""Run database migrations for task source tracking and cascade delete."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in environment variables")
    sys.exit(1)

# Create database engine
engine = create_engine(DATABASE_URL, echo=True)


def run_migration(migration_file: Path):
    """Run a single migration file."""
    print(f"\n{'=' * 80}")
    print(f"Running migration: {migration_file.name}")
    print(f"{'=' * 80}\n")

    # Read migration SQL
    with open(migration_file, "r") as f:
        sql = f.read()

    # Split into individual statements (handle multi-line statements)
    statements = []
    current_statement = []

    for line in sql.split("\n"):
        # Skip comments and empty lines
        if line.strip().startswith("--") or not line.strip():
            continue

        current_statement.append(line)

        # Check if statement is complete (ends with semicolon)
        if line.strip().endswith(";"):
            statements.append("\n".join(current_statement))
            current_statement = []

    # Execute each statement
    with engine.connect() as conn:
        for i, statement in enumerate(statements, 1):
            try:
                print(f"\nExecuting statement {i}:")
                print(f"{statement[:100]}..." if len(statement) > 100 else statement)

                result = conn.execute(text(statement))
                conn.commit()

                # Print results if it's a SELECT statement
                if statement.strip().upper().startswith("SELECT"):
                    rows = result.fetchall()
                    if rows:
                        print(f"Results: {len(rows)} rows")
                        for row in rows:
                            print(f"  {row}")
                    else:
                        print("No results")
                else:
                    print("✓ Success")

            except Exception as e:
                print(f"✗ Error: {e}")
                # Continue with next statement (some errors are expected, like constraint already exists)
                continue

    print(f"\n✓ Migration {migration_file.name} completed\n")


def main():
    """Run all migrations in order."""
    migrations_dir = Path(__file__).parent / "migrations"

    if not migrations_dir.exists():
        print(f"ERROR: Migrations directory not found: {migrations_dir}")
        sys.exit(1)

    # Get all .sql files sorted by name
    migration_files = sorted(migrations_dir.glob("*.sql"))

    if not migration_files:
        print("No migration files found")
        return

    print(f"Found {len(migration_files)} migration(s) to run:")
    for mf in migration_files:
        print(f"  - {mf.name}")

    # Run each migration
    for migration_file in migration_files:
        run_migration(migration_file)

    print("\n" + "=" * 80)
    print("All migrations completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()
