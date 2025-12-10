# Console Output Skill

**Purpose**: Format console outputs in Python apps with consistent styling.

## When to Use
- When displaying data to users (e.g., task lists, status messages).
- Autonomous trigger: If task involves print statements or display formatting.

## Instructions
Use this for consistent output formatting. Example patterns:

```python
def print_task(task: Task) -> None:
    status = "[✓]" if task.completed else "[ ]"
    print(f"{status} {task.id}. {task.title}")
    if task.description:
        print(f"   {task.description}")

def print_tasks(tasks: list[Task]) -> None:
    if not tasks:
        print("No tasks found.")
        return
    for task in tasks:
        print_task(task)
```
