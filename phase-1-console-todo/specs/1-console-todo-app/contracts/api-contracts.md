# API Contracts: Console Todo App

## Public Interface Contracts

This document defines the API contracts for the Console Todo App's public interfaces. These contracts specify the inputs, outputs, and error behaviors for all public methods.

### TodoApp Class Interface

#### add_task(title: str, description: Optional[str] = None) -> int

**Purpose**: Add a new task to the todo list

**Inputs**: 
- `title`: Required task title (string, 1-200 characters)
- `description`: Optional task description (string, max 1000 characters)

**Output**: 
- `int`: Auto-generated unique task ID

**Errors**: 
- `ValueError`: If title is empty, contains only whitespace, or exceeds 200 characters

**Post-conditions**: 
- Task is added to in-memory storage
- Task ID is unique and sequential
- Task completion status defaults to False

#### get_all_tasks() -> List[Task]

**Purpose**: Retrieve all tasks in the todo list

**Inputs**: None

**Output**: 
- `List[Task]`: Copy of all tasks in the list

**Errors**: None

**Post-conditions**: 
- Returns a copy of the internal task list
- Original list remains unchanged

#### get_task_by_id(task_id: int) -> Optional[Task]

**Purpose**: Retrieve a specific task by its ID

**Inputs**: 
- `task_id`: Task identifier (positive integer)

**Output**: 
- `Optional[Task]`: Task if found, None if not found

**Errors**: 
- `ValueError`: If task_id is not a positive integer

**Post-conditions**: 
- Returns the task with matching ID or None
- Internal state unchanged

#### update_task(task_id: int, title: Optional[str] = None, description: Optional[str] = None) -> bool

**Purpose**: Update an existing task's title and/or description

**Inputs**: 
- `task_id`: Task identifier (positive integer)
- `title`: New title (optional)
- `description`: New description (optional)

**Output**: 
- `bool`: True if task was updated, False otherwise

**Errors**: 
- `ValueError`: If task_id is invalid or task doesn't exist

**Post-conditions**: 
- Task properties updated if provided
- Completion status preserved
- Returns True on successful update

#### delete_task(task_id: int) -> bool

**Purpose**: Delete a task by its ID

**Inputs**: 
- `task_id`: Task identifier (positive integer)

**Output**: 
- `bool`: True if task was deleted, False otherwise

**Errors**: 
- `ValueError`: If task_id is invalid or task doesn't exist

**Post-conditions**: 
- Task removed from internal storage
- Returns True on successful deletion

#### toggle_task_completion(task_id: int) -> bool

**Purpose**: Toggle the completion status of a task

**Inputs**: 
- `task_id`: Task identifier (positive integer)

**Output**: 
- `bool`: True if status was toggled, False otherwise

**Errors**: 
- `ValueError`: If task_id is invalid or task doesn't exist

**Post-conditions**: 
- Task completion status inverted
- Returns True on successful toggle

### Utility Functions Contracts

#### generate_next_id(tasks: List[Task]) -> int

**Purpose**: Generate the next available ID for a new task

**Inputs**: 
- `tasks`: List of existing tasks

**Output**: 
- `int`: Next available ID (1 if list is empty, max_id + 1 otherwise)

**Errors**: None

#### validate_task_title(title: str) -> str

**Purpose**: Validate a task title

**Inputs**: 
- `title`: Title to validate

**Output**: 
- `str`: Validated and stripped title

**Errors**: 
- `ValueError`: If title is empty, contains only whitespace, or exceeds 200 characters

#### validate_task_description(description: Optional[str]) -> Optional[str]

**Purpose**: Validate a task description

**Inputs**: 
- `description`: Description to validate (optional)

**Output**: 
- `Optional[str]`: Validated description or None

**Errors**: 
- `ValueError`: If description exceeds 1000 characters

#### validate_task_id(task_id: int) -> None

**Purpose**: Validate a task ID

**Inputs**: 
- `task_id`: ID to validate

**Output**: None

**Errors**: 
- `ValueError`: If task_id is not a positive integer

#### find_task_by_id(tasks: List[Task], task_id: int) -> Optional[Task]

**Purpose**: Find a task by its ID

**Inputs**: 
- `tasks`: List of tasks to search
- `task_id`: ID to search for

**Output**: 
- `Optional[Task]`: Task if found, None otherwise

**Errors**: None

## Error Taxonomy

### ValueError
- **Purpose**: Input validation failures
- **Examples**: Invalid titles, IDs, descriptions
- **Recovery**: User should provide valid input

### Behavior Guarantees

- All public methods maintain data integrity
- No method modifies inputs (except intended updates)
- Internal state remains consistent even during errors
- All operations are thread-safe (though not designed for concurrent access)

These contracts ensure predictable behavior and provide clear interfaces for the Console Todo App functionality.