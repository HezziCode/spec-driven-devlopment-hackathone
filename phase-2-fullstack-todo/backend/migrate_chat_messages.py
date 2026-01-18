"""Migration script to add user_id column to chat_messages table."""
import sys
from sqlalchemy import text
from db import engine

def migrate():
    """Add user_id column to chat_messages table if it doesn't exist."""
    try:
        with engine.connect() as conn:
            # Check if user_id column already exists
            result = conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'chat_messages'
                AND column_name = 'user_id'
            """))

            if result.fetchone():
                print("✓ user_id column already exists in chat_messages table")
                return

            # Step 1: Add user_id column as nullable first
            print("Step 1: Adding user_id column (nullable)...")
            conn.execute(text("""
                ALTER TABLE chat_messages
                ADD COLUMN user_id UUID
            """))

            # Step 2: Populate user_id from chat_threads (cast thread_id to text for comparison)
            print("Step 2: Populating user_id from chat_threads...")
            result = conn.execute(text("""
                UPDATE chat_messages cm
                SET user_id = ct.user_id
                FROM chat_threads ct
                WHERE cm.thread_id::text = ct.id
            """))
            print(f"  Updated {result.rowcount} rows")

            # Step 3: Delete orphaned messages (messages without valid thread)
            print("Step 3: Checking for orphaned messages...")
            result = conn.execute(text("""
                DELETE FROM chat_messages
                WHERE user_id IS NULL
            """))
            if result.rowcount > 0:
                print(f"  Deleted {result.rowcount} orphaned messages")
            else:
                print("  No orphaned messages found")

            # Step 4: Make user_id NOT NULL
            print("Step 4: Making user_id NOT NULL...")
            conn.execute(text("""
                ALTER TABLE chat_messages
                ALTER COLUMN user_id SET NOT NULL
            """))

            # Step 5: Add foreign key constraint
            print("Step 5: Adding foreign key constraint...")
            conn.execute(text("""
                ALTER TABLE chat_messages
                ADD CONSTRAINT fk_chat_messages_user_id
                FOREIGN KEY (user_id) REFERENCES users(id)
            """))

            # Step 6: Create index for user_id
            print("Step 6: Creating index on user_id...")
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_chatmessage_user
                ON chat_messages(user_id)
            """))

            conn.commit()
            print("✓ Successfully added user_id column to chat_messages table")

    except Exception as e:
        print(f"✗ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    migrate()
