"""
Tag Migration Script
Updates old tag names to new generic names in the database
Run this script once to migrate all existing task tags
"""

import os
import sys

from sqlmodel import Session, select

# Add parent directory to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import engine
from models import TaskTag

# Tag mapping: old_name -> new_name
TAG_MAPPING = {
    "Design": "home",
    "design": "home",
    "Dev": "dev",
    "Development": "dev",
    "development": "dev",
    "Marketing": "fitness",
    "marketing": "fitness",
    "Meeting": "meeting",
    "meeting": "meeting",
    "Strategy": "enjoyment",
    "strategy": "enjoyment",
    "Urgent": "cricket",
    "urgent": "cricket",
    "Critical": "cricket",
    "critical": "cricket",
}


def migrate_tags():
    """Update all task tags in the database according to mapping"""

    with Session(engine) as session:
        # Get all task tags
        statement = select(TaskTag)
        results = session.exec(statement)
        tags = results.all()

        updated_count = 0
        print(f"Found {len(tags)} total tag records")

        for tag in tags:
            old_name = tag.tag_name

            # Check if this tag needs to be migrated
            if old_name in TAG_MAPPING:
                new_name = TAG_MAPPING[old_name]
                print(f"Updating: {old_name} → {new_name} (Task ID: {tag.task_id})")

                tag.tag_name = new_name
                session.add(tag)
                updated_count += 1

        # Commit all changes
        session.commit()

        print("\n✅ Migration complete!")
        print(f"Total tags migrated: {updated_count}")
        print(f"Tags unchanged: {len(tags) - updated_count}")


if __name__ == "__main__":
    print("Starting tag migration...")
    print("This will update the following tags:")
    for old, new in TAG_MAPPING.items():
        print(f"  {old} → {new}")

    response = input("\nProceed with migration? (yes/no): ")

    if response.lower() in ["yes", "y"]:
        migrate_tags()
    else:
        print("Migration cancelled")
