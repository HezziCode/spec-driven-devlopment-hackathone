# Specification: Console Todo App

## Feature Description

Build a command-line todo application using Python 3.13 standard library only, with in-memory storage (list of Task dataclasses) and no persistence. Implement basic features: Add Task (prompt for title required and description optional, auto-ID), Delete Task (by ID), Update Task (by ID, update title/description), View Task List (formatted display with status), Mark as Complete (toggle by ID). Include main loop for user menu choices. Handle errors with ValueError and user messages.

## In Scope

- Command-line interface for todo management
- Add Task functionality (title required, description optional, auto-generated ID)
- Delete Task functionality (by ID)
- Update Task functionality (by ID, update title/description)
- View Task List functionality (formatted display with status indicators)
- Mark as Complete functionality (toggle by ID)
- Main menu loop with user-friendly prompts
- Error handling with user-friendly messages
- In-memory storage using Task dataclass
- Pytest unit tests with 100% coverage

## Out of Scope

- Persistence (file/database storage)
- Web or GUI interface
- User authentication or multiple users
- Advanced features like priorities, due dates, or categories
- External API integrations

## User Scenarios & Testing

### Scenario 1: Adding a new task
- User selects "Add Task" from menu
- User enters a title (required) and description (optional)
- System creates task with auto-generated ID
- System confirms task creation

### Scenario 2: Viewing task list
- User selects "View Tasks" from menu
- System displays all tasks with ID, title, description, and completion status
- System shows appropriate message if no tasks exist

### Scenario 3: Updating a task
- User selects "Update Task" from menu
- User enters task ID and new title/description
- System updates the task
- System confirms update or shows error for invalid ID

### Scenario 4: Marking task as complete
- User selects "Mark Complete" from menu
- User enters task ID
- System toggles completion status
- System confirms status change

### Scenario 5: Deleting a task
- User selects "Delete Task" from menu
- User enters task ID
- System removes task from list
- System confirms deletion or shows error for invalid ID

## Functional Requirements

### FR-1: Add Task
- The system shall allow users to add a new task with a required title
- The system shall allow users to optionally add a description to the task
- The system shall auto-generate a unique ID for each task
- The system shall store the task in memory with completed status as false by default
- The system shall validate that the title is not empty

### FR-2: View Task List
- The system shall display all tasks in a formatted list
- The system shall show task ID, title, description, and completion status
- The system shall use visual indicators for completion status (e.g., [✓] for complete, [ ] for incomplete)
- The system shall show an appropriate message when no tasks exist

### FR-3: Update Task
- The system shall allow users to update an existing task by ID
- The system shall allow updating the title and/or description
- The system shall validate that the task ID exists
- The system shall preserve the completion status during updates

### FR-4: Delete Task
- The system shall allow users to delete a task by ID
- The system shall validate that the task ID exists
- The system shall remove the task from the in-memory list
- The system shall handle attempts to delete non-existent tasks gracefully

### FR-5: Mark Task Complete
- The system shall allow users to toggle the completion status of a task by ID
- The system shall validate that the task ID exists
- The system shall update the completion status of the task
- The system shall handle attempts to update non-existent tasks gracefully

### FR-6: Main Menu Loop
- The system shall present a main menu with numbered options
- The system shall handle user input for menu selection
- The system shall continue running until the user chooses to exit
- The system shall handle invalid menu selections gracefully

### FR-7: Error Handling
- The system shall provide user-friendly error messages
- The system shall handle invalid input (non-numeric IDs, empty titles, etc.)
- The system shall not crash on invalid operations
- The system shall return to the main menu after error handling

## Non-Functional Requirements

### NFR-1: Performance
- The system shall respond to user input within 1 second
- The system shall handle up to 1000 tasks without performance degradation

### NFR-2: Usability
- The system shall provide clear, intuitive menu options
- The system shall provide helpful error messages
- The system shall follow consistent formatting for task display

### NFR-3: Reliability
- The system shall handle all error conditions gracefully
- The system shall not crash due to invalid user input
- The system shall maintain data integrity during operations

## Success Criteria

- Users can successfully add, view, update, delete, and mark tasks as complete
- All functionality is accessible through the command-line interface
- The application runs without crashes under normal usage conditions
- Test coverage is 100% for all core functionality
- The application adheres to PEP8 style guidelines
- The application uses type hints throughout
- The application follows clean code principles as defined in the constitution

## Key Entities

### Task
- ID: Unique identifier (integer)
- Title: Task title (string, required)
- Description: Task description (string, optional)
- Completed: Completion status (boolean)

## Dependencies

- Python 3.13+ standard library only
- Pytest for testing (development dependency)

## Assumptions

- Users will interact with the application through a terminal interface
- Tasks exist only in memory and will be lost when the application exits
- Task IDs are sequential and auto-incrementing
- The application runs on a system with Python 3.13+ installed

## Constraints

- Must use Python 3.13+ standard library only (no external dependencies except pytest)
- No persistence - data exists only in memory
- Must follow PEP8 style guidelines
- Must use type hints throughout
- Must adhere to the project constitution for clean code principles
