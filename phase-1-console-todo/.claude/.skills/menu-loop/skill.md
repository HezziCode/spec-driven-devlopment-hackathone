# Menu Loop Skill

**Purpose**: Implement main menu loops in Python console apps with user choices.

## When to Use
- When creating main application loops with menu options.
- Autonomous trigger: If task involves main menu, while loops, or user choice handling.

## Instructions
Use this for menu-driven interfaces. Example pattern:

```python
def display_menu() -> None:
    print("\n--- Todo App ---")
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Update Task")
    print("4. Delete Task")
    print("5. Mark Complete")
    print("6. Exit")

while True:
    display_menu()
    choice = get_user_input("Choose option (1-6): ")
    if choice == "6":
        break
```
