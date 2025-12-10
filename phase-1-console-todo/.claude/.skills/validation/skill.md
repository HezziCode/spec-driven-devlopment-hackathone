# Validation Skill

**Purpose**: Validate inputs and data in Python console apps with consistent rules.

## When to Use
- When implementing input validation or data verification.
- Autonomous trigger: If task involves validation, sanitization, or data checks.

## Instructions
Use this for consistent validation. Example patterns:

```python
def validate_task_title(title: str) -> str:
    if not title or not title.strip():
        raise ValueError("Title cannot be empty")
    if len(title) > 200:
        raise ValueError("Title too long")
    return title.strip()

# Use in functions:
title = validate_task_title(user_input)
```
