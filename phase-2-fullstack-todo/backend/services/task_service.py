import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import asc, case, desc, func
from sqlmodel import Session, select

from models import Task, TaskTag
from schemas.task import PriorityEnum, TaskCreate, TaskUpdate

_logger = logging.getLogger(__name__)


def _generate_tags_from_keywords(title: str) -> List[str]:
    """
    CONTRACT-ENFORCED: Generate EXACTLY 2+ tags from task title.
    This function GUARANTEES at least 2 tags are returned.

    Uses keyword detection for relevant categorization.
    """
    title_lower = title.lower() if title else ""
    tags = []

    # Category keywords - detect what TYPE of task this is
    category_map = {
        "shopping": ["buy", "purchase", "shop", "order", "groceries", "store", "amazon", "ps5", "ps4", "xbox"],
        "work": ["report", "meeting", "email", "project", "deadline", "presentation", "office", "boss", "client"],
        "personal": ["call", "visit", "meet", "friend", "family", "mom", "dad", "birthday", "party"],
        "health": ["doctor", "gym", "exercise", "workout", "medicine", "appointment", "dentist", "checkup"],
        "finance": ["pay", "bill", "bank", "transfer", "budget", "invoice", "tax", "rent", "electricity"],
        "study": ["exam", "study", "learn", "course", "homework", "assignment", "research", "prepare", "test"],
        "home": ["clean", "fix", "repair", "organize", "laundry", "cook", "dishes", "vacuum"],
        "travel": ["book", "flight", "hotel", "trip", "vacation", "pack", "ticket"],
        "communication": ["call", "text", "message", "email", "contact", "reply", "respond"],
    }

    # Find matching categories
    for category, keywords in category_map.items():
        if any(kw in title_lower for kw in keywords):
            if category not in tags:
                tags.append(category)

    # Action type keywords - detect the ACTION being taken
    action_map = {
        "errands": ["buy", "pick", "get", "drop", "return"],
        "planning": ["plan", "schedule", "organize", "prepare", "arrange"],
        "completion": ["finish", "complete", "submit", "deliver", "send"],
        "creation": ["create", "make", "write", "build", "design"],
    }

    for action, keywords in action_map.items():
        if any(kw in title_lower for kw in keywords):
            if action not in tags:
                tags.append(action)
                break  # Only one action tag

    # GUARANTEE: Always return at least 2 tags
    if len(tags) == 0:
        tags = ["general", "todo"]
    elif len(tags) == 1:
        tags.append("task")

    return tags[:3]  # Max 3 tags


def _generate_description_from_title(title: str) -> str:
    """
    CONTRACT-ENFORCED: Generate a non-empty description.
    This function GUARANTEES a description is returned.
    """
    if not title or not title.strip():
        return "Task to be completed."

    # Capitalize and format
    clean_title = title.strip()
    if clean_title[0].islower():
        clean_title = clean_title[0].upper() + clean_title[1:]

    return f"Task: {clean_title}"


def create_task(
    session: Session,
    task_data: TaskCreate,
    user_id: UUID,
    source: str = "manual",
    thread_id: Optional[str] = None,
    use_dapr: bool = False,
) -> Task:
    """Create a new task for a user.

    CONTRACT-ENFORCED GUARANTEES:
    1. Task WILL have at least 2 tags (enforced, not requested)
    2. Task WILL have a non-empty description (enforced, not requested)
    3. These guarantees are SYSTEM-LEVEL, not dependent on AI compliance

    Args:
        session: Database session
        task_data: Task creation data
        user_id: User UUID
        source: Task creation source ('manual' or 'chat')
        thread_id: Optional chat thread ID if created from chat
        use_dapr: Whether to sync with Dapr state store

    Returns:
        Task: Created task with GUARANTEED tags and description
    """
    # ========== CONTRACT ENFORCEMENT: TAGS ==========
    # Step 1: Check if valid tags were provided
    provided_tags = task_data.tags if task_data.tags else []
    valid_tags = [t.strip() for t in provided_tags if t and t.strip()]

    # Step 2: ENFORCE minimum 2 tags - generate if missing
    if len(valid_tags) < 2:
        _logger.info(
            f"ENFORCING TAGS: Provided {len(valid_tags)} tags, generating fallback for '{task_data.title}'"
        )
        final_tags = _generate_tags_from_keywords(task_data.title)
    else:
        final_tags = valid_tags[:3]  # Max 3 tags

    # Step 3: VERIFY contract (defensive - should never fail)
    assert len(final_tags) >= 2, f"CONTRACT VIOLATION: Tags must be >= 2, got {len(final_tags)}"

    # ========== CONTRACT ENFORCEMENT: DESCRIPTION ==========
    # Step 1: Check if valid description was provided
    provided_desc = task_data.description.strip() if task_data.description else ""

    # Step 2: ENFORCE non-empty description - generate if missing
    if not provided_desc:
        _logger.info(
            f"ENFORCING DESCRIPTION: Empty description provided, generating for '{task_data.title}'"
        )
        final_description = _generate_description_from_title(task_data.title)
    else:
        final_description = provided_desc

    # Step 3: VERIFY contract (defensive - should never fail)
    assert final_description, "CONTRACT VIOLATION: Description must not be empty"

    _logger.info(
        f"Creating task: title='{task_data.title}', tags={final_tags}, description='{final_description[:50]}...'"
    )

    # ========== CREATE TASK WITH GUARANTEED METADATA ==========
    task = Task(
        title=task_data.title,
        description=final_description,
        completed=False,
        priority=task_data.priority or PriorityEnum.medium,
        user_id=user_id,
        source=source,
        created_by_thread_id=thread_id if source == "chat" else None,
    )

    session.add(task)
    session.flush()  # Get the task ID

    # Add GUARANTEED tags to database
    for tag_name in final_tags:
        tag = TaskTag(task_id=task.id, tag_name=tag_name)
        session.add(tag)

    session.commit()
    session.refresh(task)

    _logger.info(f"Task created: id={task.id}, tags_count={len(final_tags)}")

    return task


def get_user_tasks(
    session: Session,
    user_id: UUID,
    completed: Optional[bool] = None,
    priority: Optional[PriorityEnum] = None,
    tag: Optional[str] = None,
    search: Optional[str] = None,
    sort: str = "created",
    limit: int = 20,
    offset: int = 0,
) -> tuple[List[Task], int]:
    """
    Get tasks for a specific user with optional filters.
    Returns a tuple of (tasks, total_count).
    """
    # Start with the base query
    query = select(Task).where(Task.user_id == user_id)

    # Apply filters
    if completed is not None:
        query = query.where(Task.completed == completed)

    if priority is not None:
        query = query.where(Task.priority == priority)

    if search is not None:
        search_pattern = f"%{search}%"
        query = query.where(
            (Task.title.ilike(search_pattern))
            | (Task.description.ilike(search_pattern))
        )

    # Apply tag filter if needed
    if tag is not None:
        # Join with TaskTag to filter by tag
        query = query.join(TaskTag).where(TaskTag.tag_name == tag)

    # Get total count
    total_query = select(func.count()).select_from(query.subquery())
    total_count = session.exec(total_query).one()

    # Apply sorting
    if sort == "created":
        query = query.order_by(desc(Task.created_at))
    elif sort == "title":
        query = query.order_by(asc(Task.title))
    elif sort == "priority":
        # Custom order: critical > high > medium > low
        query = query.order_by(
            case(
                (Task.priority == "critical", 1),
                (Task.priority == "high", 2),
                (Task.priority == "medium", 3),
                (Task.priority == "low", 4),
                else_=5,
            )
        )
    elif sort == "updated":
        query = query.order_by(desc(Task.updated_at))
    else:  # Default to created descending
        query = query.order_by(desc(Task.created_at))

    # Apply pagination
    query = query.offset(offset).limit(limit)

    tasks = session.exec(query).all()

    # Load tags for each task (tags are TaskTag objects loaded via relationship)
    # No need to manually query - SQLModel relationships handle this automatically
    # The tags will be converted to strings in the route handler

    return tasks, total_count


def get_task_by_id(session: Session, task_id: UUID, user_id: UUID, use_dapr: bool = False) -> Optional[Task]:
    """Get task with optional Dapr state fallback."""
    """
    Get a specific task by ID for a user.

    Returns the task with its tags loaded if it exists and belongs to the user.
    Returns None if task doesn't exist or belongs to a different user.
    """
    task = session.get(Task, task_id)

    # Verify that the task belongs to the user
    task = session.get(Task, task_id)

    if task and task.user_id == user_id:
        return task

    if use_dapr:
        from .dapr_state import dapr_manager
        state_task = dapr_manager.get_task(str(user_id), str(task_id))
        if state_task:
            # Rehydrate from state if DB miss
            # For simplicity, return DB task or None
            pass

    return None


def update_task(
    session: Session, task_id: UUID, task_data: TaskUpdate, user_id: UUID, use_dapr: bool = False
) -> Optional[Task]:
    """Update task with optional Dapr sync."""
    """
    Update an existing task.
    """
    task = session.get(Task, task_id)

    # Verify that the task belongs to the user
    if not task or task.user_id != user_id:
        return None

    # Update fields that are provided
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.completed is not None:
        task.completed = task_data.completed
    if task_data.priority is not None:
        task.priority = task_data.priority

    # Update the timestamp
    task.updated_at = datetime.utcnow()

    # Handle tags if provided
    if task_data.tags is not None:
        # Delete all existing tags for this task first
        from sqlalchemy import delete as sql_delete

        delete_stmt = sql_delete(TaskTag).where(TaskTag.task_id == task.id)
        session.exec(delete_stmt)

        # Flush to ensure delete completes before inserts
        session.flush()

        # Add new tags
        for tag_name in task_data.tags:
            if tag_name.strip():  # Only add non-empty tags
                tag = TaskTag(task_id=task.id, tag_name=tag_name.strip())
                session.add(tag)

    session.add(task)
    session.commit()
    session.refresh(task)

    if use_dapr:
        from .dapr_state import dapr_manager
        dapr_manager.save_task(str(user_id), task)

    # Force load the tags relationship to ensure they're TaskTag objects
    # This prevents lazy loading issues when the task is accessed outside the session
    _ = task.tags  # Access tags to trigger loading if not already loaded

    return task


def delete_task(session: Session, task_id: UUID, user_id: UUID, use_dapr: bool = False) -> bool:
    """
    Delete a task by ID for a user.
    """
    task = session.get(Task, task_id)

    # Verify that the task belongs to the user
    if not task or task.user_id != user_id:
        return False

    # Delete associated tags first
    task_tags = session.exec(select(TaskTag).where(TaskTag.task_id == task.id)).all()
    for tag in task_tags:
        session.delete(tag)

    # Delete the task
    session.delete(task)
    session.commit()

    if use_dapr:
        from .dapr_state import dapr_manager
        dapr_manager.delete_task(str(user_id), str(task_id))

    return True


def validate_task_data(task_data: TaskCreate) -> List[str]:
    """
    Validate task data and return a list of error messages.
    """
    errors = []

    # Validate title length
    if task_data.title and len(task_data.title) > 200:
        errors.append("Title must be 200 characters or less")

    # Validate description length
    if task_data.description and len(task_data.description) > 1000:
        errors.append("Description must be 1000 characters or less")

    # Validate tags
    if task_data.tags:
        if len(task_data.tags) > 10:
            errors.append("A task can have at most 10 tags")

        for tag in task_data.tags:
            if len(tag) > 50:
                errors.append("Each tag must be 50 characters or less")
            if not tag.strip():
                errors.append("Tags cannot be empty")

    return errors
