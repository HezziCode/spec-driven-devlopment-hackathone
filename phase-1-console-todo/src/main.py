from typing import Optional
from .todo_app import TodoApp
from .models import Task


def print_task(task: Task) -> None:
    """
    Print a single task with proper formatting.

    Args:
        task: The task to print
    """
    status = "[✓]" if task.completed else "[ ]"
    print(f"{status} {task.id}. {task.title}")
    if task.description:
        print(f"   {task.description}")


def print_tasks(tasks: list[Task]) -> None:
    """
    Print all tasks in a formatted list.

    Args:
        tasks: List of tasks to print
    """
    if not tasks:
        print("No tasks found.")
        return

    for task in tasks:
        print_task(task)


def print_error(message: str) -> None:
    """
    Print an error message in a consistent format.

    Args:
        message: The error message to print
    """
    print(f"Error: {message}")


def get_user_input(prompt: str) -> str:
    """
    Get input from the user with proper error handling.

    Args:
        prompt: The prompt to display to the user

    Returns:
        str: The user's input (stripped of leading/trailing whitespace)
    """
    return input(prompt).strip()


def get_int_input(prompt: str) -> int:
    """
    Get an integer input from the user with validation.

    Args:
        prompt: The prompt to display to the user

    Returns:
        int: The user's integer input

    Raises:
        ValueError: If the input is not a valid integer
    """
    user_input = input(prompt).strip()
    try:
        return int(user_input)
    except ValueError:
        raise ValueError("Invalid input. Please enter a number.")


def display_menu() -> None:
    """
    Display the main menu options to the user.
    """
    print("\n--- Todo App ---")
    print("1. Add Task")
    print("2. View Tasks")
    print("3. Update Task")
    print("4. Delete Task")
    print("5. Mark Complete")
    print("6. Exit")


def handle_add_task(app: TodoApp) -> None:
    """
    Handle the add task functionality.

    Args:
        app: The TodoApp instance
    """
    try:
        title = get_user_input("Enter task title: ")
        if not title:
            print_error("Title cannot be empty.")
            return

        description = get_user_input("Enter task description (optional, press Enter to skip): ")
        if not description:  # If user pressed Enter without typing
            description = None

        task_id = app.add_task(title, description)
        print(f"Task added successfully with ID: {task_id}")
    except ValueError as e:
        print_error(str(e))


def handle_view_tasks(app: TodoApp) -> None:
    """
    Handle the view tasks functionality.

    Args:
        app: The TodoApp instance
    """
    tasks = app.get_all_tasks()
    print("\n--- All Tasks ---")
    print_tasks(tasks)


def handle_update_task(app: TodoApp) -> None:
    """
    Handle the update task functionality.

    Args:
        app: The TodoApp instance
    """
    try:
        task_id = get_int_input("Enter task ID to update: ")

        # Check if task exists
        task = app.get_task_by_id(task_id)
        if not task:
            print_error(f"Task with ID {task_id} does not exist.")
            return

        print(f"Current task: {task.title}")
        if task.description:
            print(f"Current description: {task.description}")

        new_title = get_user_input("Enter new title (or press Enter to keep current): ")
        new_title = new_title if new_title else None  # Use None if empty

        new_description = get_user_input("Enter new description (or press Enter to keep current): ")
        new_description = new_description if new_description else None  # Use None if empty

        # If both are None, nothing to update
        if new_title is None and new_description is None:
            print("No changes made.")
            return

        app.update_task(task_id, new_title, new_description)
        print("Task updated successfully.")
    except ValueError as e:
        print_error(str(e))


def handle_delete_task(app: TodoApp) -> None:
    """
    Handle the delete task functionality.

    Args:
        app: The TodoApp instance
    """
    try:
        task_id = get_int_input("Enter task ID to delete: ")
        app.delete_task(task_id)
        print("Task deleted successfully.")
    except ValueError as e:
        print_error(str(e))


def handle_mark_complete(app: TodoApp) -> None:
    """
    Handle the mark task as complete functionality.

    Args:
        app: The TodoApp instance
    """
    try:
        task_id = get_int_input("Enter task ID to toggle completion: ")
        app.toggle_task_completion(task_id)
        task = app.get_task_by_id(task_id)
        status = "completed" if task.completed else "pending"
        print(f"Task marked as {status}.")
    except ValueError as e:
        print_error(str(e))


def main() -> None:
    """
    Main function to run the todo application.
    """
    app = TodoApp()

    print("Welcome to the Todo App!")

    while True:
        try:
            display_menu()
            choice = get_user_input("Choose an option (1-6): ")

            if choice == "1":
                handle_add_task(app)
            elif choice == "2":
                handle_view_tasks(app)
            elif choice == "3":
                handle_update_task(app)
            elif choice == "4":
                handle_delete_task(app)
            elif choice == "5":
                handle_mark_complete(app)
            elif choice == "6":
                print("Goodbye!")
                break
            else:
                print_error("Invalid option. Please choose a number between 1 and 6.")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print_error(f"An unexpected error occurred: {str(e)}")


if __name__ == "__main__":
    main()
