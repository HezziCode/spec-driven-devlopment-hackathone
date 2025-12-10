# Tasks: Console Todo App

## Feature Overview
Build a command-line todo application using Python 3.13 standard library only, with in-memory storage (list of Task dataclasses) and no persistence. Implement basic features: Add Task, Delete Task, Update Task, View Task List, Mark as Complete with a main menu loop.

## Phase 1: Setup
Initialize project structure and foundational components.

- [x] T001 Create src directory structure
- [x] T002 Create tests directory structure
- [x] T003 [P] Create basic __init__.py files in src and tests directories

## Phase 2: Foundational
Core components required by all user stories.

- [x] T004 Create Task dataclass in src/models.py with id, title, description, completed fields
- [x] T005 Create in-memory task storage in src/todo_app.py (tasks: List[Task])
- [x] T006 [P] Create utility functions for ID generation in src/utils.py
- [x] T007 [P] Create validation functions for input validation in src/utils.py

## Phase 3: [US1] Add Task Functionality
Enable users to add new tasks with required title and optional description.

### Story Goal
Users can add a new task with a required title and optional description. The system auto-generates a unique ID and sets completion status to false by default.

### Independent Test Criteria
- Can add a task with title only
- Can add a task with title and description
- Auto-generated ID is unique and sequential
- Task completion status defaults to false
- Title validation prevents empty titles

### Implementation Tasks
- [x] T008 [US1] Implement add_task function in src/todo_app.py
- [x] T009 [US1] Create input validation for add_task in src/utils.py
- [x] T010 [US1] Create user interface for adding tasks in src/main.py
- [x] T011 [US1] Write unit tests for add_task functionality in tests/test_todo_app.py
- [x] T012 [US1] Write integration tests for add_task UI flow in tests/test_main.py

## Phase 4: [US2] View Task List Functionality
Display all tasks with ID, title, description, and completion status.

### Story Goal
Users can view all tasks in a formatted list with visual indicators for completion status.

### Independent Test Criteria
- Can display all tasks with proper formatting
- Shows appropriate message when no tasks exist
- Uses visual indicators for completion status ([✓] for complete, [ ] for incomplete)
- Displays ID, title, description for each task

### Implementation Tasks
- [x] T013 [US2] Implement get_all_tasks function in src/todo_app.py
- [x] T014 [US2] Implement formatted display function in src/utils.py
- [x] T015 [US2] Create user interface for viewing tasks in src/main.py
- [x] T016 [US2] Write unit tests for get_all_tasks functionality in tests/test_todo_app.py
- [x] T017 [US2] Write integration tests for view tasks UI flow in tests/test_main.py

## Phase 5: [US3] Delete Task Functionality
Enable users to delete tasks by ID.

### Story Goal
Users can delete a task by its ID. The system validates the ID exists and removes the task from memory.

### Independent Test Criteria
- Can delete an existing task by ID
- Shows error for non-existent task ID
- Properly removes task from in-memory list
- Handles invalid input gracefully

### Implementation Tasks
- [x] T018 [US3] Implement delete_task function in src/todo_app.py
- [x] T019 [US3] Create input validation for delete_task in src/utils.py
- [x] T020 [US3] Create user interface for deleting tasks in src/main.py
- [x] T021 [US3] Write unit tests for delete_task functionality in tests/test_todo_app.py
- [x] T022 [US3] Write integration tests for delete_task UI flow in tests/test_main.py

## Phase 6: [US4] Update Task Functionality
Enable users to update existing tasks by ID.

### Story Goal
Users can update the title and/or description of an existing task by its ID while preserving completion status.

### Independent Test Criteria
- Can update task title only
- Can update task description only
- Can update both title and description
- Preserves completion status during updates
- Shows error for non-existent task ID

### Implementation Tasks
- [x] T023 [US4] Implement update_task function in src/todo_app.py
- [x] T024 [US4] Create input validation for update_task in src/utils.py
- [x] T025 [US4] Create user interface for updating tasks in src/main.py
- [x] T026 [US4] Write unit tests for update_task functionality in tests/test_todo_app.py
- [x] T027 [US4] Write integration tests for update_task UI flow in tests/test_main.py

## Phase 7: [US5] Mark Task Complete Functionality
Enable users to toggle the completion status of tasks by ID.

### Story Goal
Users can toggle the completion status of a task by its ID (completed ↔ incomplete).

### Independent Test Criteria
- Can toggle completion status from incomplete to complete
- Can toggle completion status from complete to incomplete
- Shows error for non-existent task ID
- Properly updates completion status in memory

### Implementation Tasks
- [x] T028 [US5] Implement toggle_task_completion function in src/todo_app.py
- [x] T029 [US5] Create input validation for toggle_task_completion in src/utils.py
- [x] T030 [US5] Create user interface for marking tasks complete in src/main.py
- [x] T031 [US5] Write unit tests for toggle_task_completion functionality in tests/test_todo_app.py
- [x] T032 [US5] Write integration tests for mark complete UI flow in tests/test_main.py

## Phase 8: [US6] Main Menu Loop
Create the main application loop with user-friendly menu options.

### Story Goal
Provide a main menu with numbered options that allows users to access all functionality and gracefully handle invalid selections.

### Independent Test Criteria
- Shows menu with all required options (Add, View, Update, Delete, Mark Complete, Exit)
- Handles user input for menu selection
- Continues running until user chooses to exit
- Handles invalid menu selections gracefully
- Returns to main menu after each operation

### Implementation Tasks
- [x] T033 [US6] Implement main menu loop in src/main.py
- [x] T034 [US6] Create menu display function in src/main.py
- [x] T035 [US6] Implement menu option handling in src/main.py
- [x] T036 [US6] Add error handling for invalid menu selections in src/main.py
- [x] T037 [US6] Write integration tests for main menu functionality in tests/test_main.py

## Phase 9: [US7] Error Handling
Implement comprehensive error handling with user-friendly messages.

### Story Goal
Handle all error conditions gracefully with user-friendly messages that don't crash the application.

### Independent Test Criteria
- Provides user-friendly error messages
- Handles invalid input (non-numeric IDs, empty titles, etc.)
- Does not crash on invalid operations
- Returns to main menu after error handling
- Maintains data integrity during error conditions

### Implementation Tasks
- [x] T038 [US7] Implement exception handling for input validation in src/utils.py
- [x] T039 [US7] Create error message formatting functions in src/utils.py
- [x] T040 [US7] Add error handling to all core functions in src/todo_app.py
- [x] T041 [US7] Add error handling to user interface functions in src/main.py
- [x] T042 [US7] Write error handling tests in tests/test_utils.py

## Phase 10: Polish & Cross-Cutting Concerns
Final touches, integration, and quality assurance.

- [x] T043 Add type hints to all functions across src/ files
- [x] T044 [P] Add docstrings to all functions following Google style
- [x] T045 [P] Ensure all code follows PEP8 style guidelines
- [x] T046 Run full test suite and achieve 100% coverage
- [x] T047 Create README.md with usage instructions
- [x] T048 [P] Perform final integration testing of complete application
- [x] T049 Document any architectural decisions in ADR if needed

## Dependencies
- US3 (Delete Task) depends on US1 (Add Task) - need tasks to exist before deleting
- US4 (Update Task) depends on US1 (Add Task) - need tasks to exist before updating
- US5 (Mark Complete) depends on US1 (Add Task) - need tasks to exist before marking complete
- US6 (Main Menu) depends on US1-US5 (all features) - menu needs to access all functionality
- US7 (Error Handling) applies to all other user stories

## Parallel Execution Examples
- T006 and T007 can run in parallel (different utility functions)
- T011 and T012 can run in parallel (different test files)
- T016 and T017 can run in parallel (different test files)
- T021 and T022 can run in parallel (different test files)
- T026 and T027 can run in parallel (different test files)
- T031 and T032 can run in parallel (different test files)
- T036 and T037 can run in parallel (test and implementation)

## Implementation Strategy
- MVP Scope: Complete Phase 1 (Setup) + Phase 2 (Foundational) + Phase 3 (Add Task) to have a minimal working feature
- Incremental Delivery: Each user story phase delivers a complete, testable increment of functionality
- Test-First Approach: Each functionality includes corresponding unit and integration tests
