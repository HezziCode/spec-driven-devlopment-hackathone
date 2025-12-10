# Error Handling Skill

**Purpose**: Handle errors gracefully in Python console apps with user-friendly messages.

## When to Use
- When implementing try/catch blocks or error validation.
- Autonomous trigger: If task involves ValueError, exceptions, or error messages.

## Instructions
Use this for consistent error handling. Example patterns:

```python
def print_error(message: str) -> None:
    print(f"Error: {message}")

# In main functions:
try:
    # operation
except ValueError as e:
    print_error(str(e))
```
