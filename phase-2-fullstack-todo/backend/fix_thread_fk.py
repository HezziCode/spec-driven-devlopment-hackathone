"""Fix foreign key constraint on chat_messages.thread_id to point to chat_threads."""
import sys
from sqlalchemy import text
from db import engine

def fix_foreign_key():
    """Update foreign key constraint to point to chat_threads instead of threads."""
    try:
        with engine.connect() as conn:
            # Step 1: Check current foreign key constraints
            print("Step 1: Checking current foreign key constraints...")
            result = conn.execute(text("""
                SELECT constraint_name, table_name, column_name
                FROM information_schema.key_column_usage
                WHERE table_name = 'chat_messages'
                AND column_name = 'thread_id'
            """))
            constraints = result.fetchall()
            print(f"  Found {len(constraints)} constraints on thread_id")
            for c in constraints:
                print(f"    - {c[0]}")

            # Step 2: Drop old foreign key constraint pointing to threads table
            print("\nStep 2: Dropping old foreign key constraint...")
            conn.execute(text("""
                ALTER TABLE chat_messages
                DROP CONSTRAINT IF EXISTS chat_messages_thread_id_fkey
            """))
            print("  ✓ Dropped chat_messages_thread_id_fkey")

            # Step 3: Change thread_id column type from UUID to VARCHAR
            print("\nStep 3: Changing thread_id column type from UUID to VARCHAR...")
            conn.execute(text("""
                ALTER TABLE chat_messages
                ALTER COLUMN thread_id TYPE VARCHAR(100)
            """))
            print("  ✓ Changed thread_id to VARCHAR(100)")

            # Step 4: Add new foreign key constraint pointing to chat_threads
            print("\nStep 4: Adding new foreign key constraint to chat_threads...")
            conn.execute(text("""
                ALTER TABLE chat_messages
                ADD CONSTRAINT fk_chat_messages_thread_id
                FOREIGN KEY (thread_id) REFERENCES chat_threads(id)
            """))
            print("  ✓ Added foreign key constraint to chat_threads")

            conn.commit()
            print("\n✓ Successfully fixed foreign key constraint")

    except Exception as e:
        print(f"\n✗ Fix failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    fix_foreign_key()
