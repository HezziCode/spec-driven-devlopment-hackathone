# Quickstart Guide: Console Todo App

## Getting Started

This guide provides quick setup and usage instructions for the Console Todo App.

### Prerequisites

- Python 3.13+
- Git (for cloning the repository)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd phase-1-console-todo
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies (only for testing):
   ```bash
   pip install pytest
   ```

### Running the Application

1. Execute the main application:
   ```bash
   python -m src.main
   ```

2. The application will start with a welcome message and present a menu:
   ```
   --- Todo App ---
   1. Add Task
   2. View Tasks
   3. Update Task
   4. Delete Task
   5. Mark Complete
   6. Exit
   ```

### Basic Usage

#### Adding a Task
1. Select option 1 from the menu
2. Enter a task title (required)
3. Optionally enter a task description
4. The system will assign an auto-generated ID

#### Viewing Tasks
1. Select option 2 from the menu
2. All tasks will be displayed with ID, title, description, and completion status
3. Completed tasks show [✓], pending tasks show [ ]

#### Updating a Task
1. Select option 3 from the menu
2. Enter the task ID you want to update
3. Enter new title or description (or press Enter to keep current)

#### Deleting a Task
1. Select option 4 from the menu
2. Enter the task ID you want to delete
3. Confirm the deletion

#### Marking Complete
1. Select option 5 from the menu
2. Enter the task ID you want to toggle
3. The completion status will switch (complete ↔ incomplete)

### Running Tests

To run the full test suite:

```bash
python -m pytest tests/ -v
```

This will run all tests and show detailed results. All tests should pass.

### Development Workflow

1. Make changes to the code
2. Run tests to ensure functionality still works:
   ```bash
   python -m pytest tests/
   ```
3. Add new tests for new functionality
4. Verify all tests pass before committing changes

### Troubleshooting

- If you get import errors, ensure you're running as a module: `python -m src.main`
- If you encounter issues with virtual environment, recreate it with `python -m venv venv`
- For any runtime errors, check that you're using Python 3.13+

This quickstart guide provides the essential information to get up and running with the Console Todo App quickly.