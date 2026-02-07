# Phase 1: Console Todo App

> **Part of ChatTask Evolution** - The foundation of a journey from console to cloud

A command-line todo application built with Python 3.13 using standard library only. This is Phase 1 of the GIAIC Hackathon project, demonstrating core todo functionality before evolving into a full-stack web application.

**🔗 See the full project:** [ChatTask - All Phases](../README.md)

**🌐 Live Production App:** [chat-task.site](https://chat-task.site)

## 🎯 Phase 1 Overview

This console app serves as the foundation for the ChatTask project. It implements core CRUD operations and task management logic that will later be evolved into a cloud-native web application.

### What This Phase Demonstrates
- ✅ Core todo functionality (CRUD operations)
- ✅ Clean code architecture with separation of concerns
- ✅ In-memory data storage
- ✅ Input validation and error handling
- ✅ Test-driven development

### Evolution Path
**Phase 1 (You are here)** → Phase 2 (Web App + DB) → Phase 3 (AI Chatbot) → Phase 4 (Docker + K8s) → Phase 5 (Cloud Production)

## Features

- Add tasks with required title and optional description
- View all tasks with formatted display and status indicators
- Update existing tasks (title and/or description)
- Delete tasks by ID
- Mark tasks as complete/incomplete (toggle)
- Menu-driven interface with user-friendly prompts
- Comprehensive error handling

## Requirements

- Python 3.13+
- No external dependencies (except pytest for testing)

## Installation

1. Clone or download the repository
2. Navigate to the project directory
3. Create a virtual environment:
   ```bash
   uv venv
   source .venv/bin/activate
   ```
4. Install dependencies:
   ```bash
   uv pip install -r requirements.txt  # if you have a requirements file
   # or just run the app directly with Python 3.13+
   ```

## Usage

Run the application:
```bash
python src/main.py
```

The application will present a menu with the following options:
1. Add Task - Create a new task with title and optional description
2. View Tasks - Display all tasks with their status
3. Update Task - Modify an existing task's title or description
4. Delete Task - Remove a task by its ID
5. Mark Complete - Toggle the completion status of a task
6. Exit - Quit the application

## Project Structure

```
src/
├── main.py              # Main application loop and menu
├── models.py            # Task dataclass and related models
├── todo_app.py          # Core todo functionality (add, delete, update, etc.)
└── utils.py             # Utility functions and helpers

tests/
├── test_todo_app.py     # Unit tests for core functionality
├── test_models.py       # Unit tests for data models
└── test_utils.py        # Unit tests for utility functions
```

## Testing

To run the test suite:
```bash
python -m pytest tests/ -v
```

All tests should pass with 100% coverage.

## Architecture

- **Task Model**: Dataclass with id, title, description, and completed fields
- **TodoApp Class**: Core business logic with in-memory storage
- **Utility Functions**: Validation and helper functions
- **Main Interface**: Menu-driven console interface

## Design Decisions

- Used dataclasses for clean, readable model definition
- In-memory storage for simplicity (Phase 1 requirement)
- Modular code organization with separation of concerns
- Comprehensive validation and error handling
- User-friendly console interface with clear prompts and messages

## Limitations

- Data is not persisted (lost when application exits)
- Single-user application
- No advanced features like priorities, due dates, or categories
