# Data Model: TaskWave Dashboard

## Task Entity

**Description**: Represents a user's to-do item with metadata for organization and prioritization

**Fields**:
- `id`: string (UUID) - Unique identifier for the task
- `title`: string - Required title of the task (max 200 characters)
- `description`: string - Optional detailed description of the task (max 1000 characters)
- `completed`: boolean - Status indicating if the task is completed
- `priority`: string - Priority level ("high", "medium", "low")
- `tags`: string[] - Array of tags for categorization
- `createdAt`: string (ISO 8601) - Timestamp when the task was created
- `updatedAt`: string (ISO 8601) - Timestamp when the task was last updated
- `userId`: string - Foreign key to the user who owns the task

**Validation Rules**:
- Title must be 1-200 characters
- Description, if provided, must be 0-1000 characters
- Priority must be one of "high", "medium", "low"
- Tags array must have 0-10 items
- Each tag must be 1-30 characters
- userId must match authenticated user

**State Transitions**:
- `pending` → `completed` (when checkbox is clicked)
- `completed` → `pending` (when checkbox is unclicked)

## User Entity

**Description**: Represents an authenticated user with task ownership

**Fields**:
- `id`: string (UUID) - Unique identifier for the user
- `username`: string - User's display name
- `email`: string - User's email address
- `createdAt`: string (ISO 8601) - Timestamp when the user was created
- `updatedAt`: string (ISO 8601) - Timestamp when the user was last updated

## Priority Entity

**Description**: Represents the importance level of a task

**Values**:
- `high`: Critical tasks requiring immediate attention (red with flame icon)
- `medium`: Important tasks to be completed soon (yellow with clock icon)
- `low`: Tasks that can be completed when convenient (green with leaf icon)

## Tag Entity

**Description**: Represents categorical labels for organizing tasks

**Constraints**:
- Each tag is a string of 1-30 characters
- Predefined tags: "Fitness", "Home", "Work", "Code", "Planning", "Design", "UI/UX", "Backend", "Security"
- Custom tags allowed in addition to predefined ones
- Maximum of 10 tags per task

## Streak Entity

**Description**: Represents the consecutive days of completed tasks for gamification

**Fields**:
- `currentStreak`: number - Current number of consecutive days with completed tasks
- `longestStreak`: number - Longest streak achieved by the user
- `lastCompletedDate`: string (ISO 8601 date) - Date of last completed task
- `userId`: string - Foreign key to the user