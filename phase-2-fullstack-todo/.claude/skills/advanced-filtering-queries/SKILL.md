---
name: advanced-filtering-queries
description: Build complex database queries with multiple filters, search, sorting, and pagination using SQLModel. Use when implementing flexible query APIs, building task/item listing endpoints, or combining multiple filter conditions.
---

# Advanced Filtering Queries

## Purpose
Implement complex database queries with multiple filters, search, sorting, and pagination.

## Context
Used for building flexible query APIs with various filter combinations.

## Pattern

```python
from sqlmodel import select, func, or_, and_, case
from typing import Optional

def build_task_query(
    user_id: str,
    search: Optional[str] = None,
    priority: Optional[str] = None,
    tag: Optional[str] = None,
    status: Optional[str] = None,
    sort: str = "created"
):
    # Base query with user isolation
    query = select(Task).where(Task.user_id == user_id)

    # Search in title and description
    if search:
        search_filter = or_(
            Task.title.ilike(f"%{search}%"),
            Task.description.ilike(f"%{search}%")
        )
        query = query.where(search_filter)

    # Priority filter
    if priority:
        query = query.where(Task.priority == priority)

    # Status filter
    if status == "pending":
        query = query.where(Task.completed == False)
    elif status == "completed":
        query = query.where(Task.completed == True)

    # Tag filter (requires join)
    if tag:
        query = query.join(TaskTag).where(TaskTag.tag_name == tag)

    # Sorting
    if sort == "created":
        query = query.order_by(Task.created_at.desc())
    elif sort == "title":
        query = query.order_by(Task.title)
    elif sort == "priority":
        priority_order = case(
            (Task.priority == "critical", 1),
            (Task.priority == "high", 2),
            (Task.priority == "medium", 3),
            (Task.priority == "low", 4)
        )
        query = query.order_by(priority_order)

    return query
```