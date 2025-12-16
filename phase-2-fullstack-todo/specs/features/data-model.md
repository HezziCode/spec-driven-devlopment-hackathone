# Data Model: Add Task Feature

## Overview
This document defines the data model for the Add Task feature in the Phase 2 full-stack todo web application. The model includes entities, relationships, and validation rules required for task creation with priority and tagging functionality.

## Task Entity

### Fields
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, NOT NULL | Unique identifier for the task |
| user_id | UUID | FOREIGN KEY, NOT NULL | Reference to the user who owns the task |
| title | VARCHAR(200) | NOT NULL | Task title |
| description | TEXT | NULL | Detailed task description |
| completed | BOOLEAN | NOT NULL, DEFAULT FALSE | Completion status |
| priority | VARCHAR(20) | NOT NULL, DEFAULT 'medium' | Task priority (low, medium, high, critical) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Task creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

### Validation Rules
- Title: Required, length between 1-200 characters
- Description: Optional, maximum 1000 characters
- Priority: Must be one of: 'low', 'medium', 'high', 'critical'
- User_id: Must reference a valid user in the users table
- Completed: Boolean value (true/false)

### State Transitions
- New task: completed = false by default
- Task completion: completed can be updated to true
- Task reversion: completed can be updated back to false

## User Entity (Referenced)

### Fields
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, NOT NULL | Unique identifier for the user |
| username | VARCHAR(50) | UNIQUE, NOT NULL | User's chosen username |
| email | VARCHAR(100) | UNIQUE, NOT NULL | User's email address |
| password_hash | VARCHAR(255) | NOT NULL | Hashed password using secure algorithm |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Account creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

## Tag Entity (Many-to-Many with Task)

### Fields
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, NOT NULL | Unique identifier for the tag association |
| task_id | UUID | FOREIGN KEY, NOT NULL | Reference to the task |
| tag_name | VARCHAR(50) | NOT NULL | Name of the tag |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Association creation timestamp |

### Validation Rules
- Tag_name: Required, length between 1-50 characters
- Task_id: Must reference a valid task in the tasks table
- Unique constraint: (task_id, tag_name) combination must be unique

## Relationships

### Task to User
- **Relationship Type**: Many-to-One (Many tasks belong to one user)
- **Foreign Key**: `tasks.user_id` references `users.id`
- **Cardinality**: Each task belongs to exactly one user
- **User Isolation**: Tasks are filtered by user_id to ensure data isolation

### Task to Tags
- **Relationship Type**: Many-to-Many (Many tasks can have many tags)
- **Join Table**: `task_tags` table manages the relationship
- **Foreign Keys**:
  - `task_tags.task_id` references `tasks.id`
  - `task_tags.tag_name` references tag names
- **Cardinality**: Each task can have zero or more tags, each tag can be on zero or more tasks

## API Data Transfer Objects (DTOs)

### TaskCreate DTO
**Purpose**: Data transfer object for creating new tasks

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| title | string | Yes | 1-200 chars | Task title |
| description | string | No | 0-1000 chars | Task description |
| priority | string | No | enum: low, medium, high, critical | Task priority |
| tags | array of strings | No | max 10 tags, 1-50 chars each | Task tags |

### TaskResponse DTO
**Purpose**: Data transfer object for returning task data

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string (UUID) | Yes | Task identifier |
| title | string | Yes | Task title |
| description | string | Yes | Task description |
| completed | boolean | Yes | Completion status |
| priority | string | Yes | Task priority |
| tags | array of strings | Yes | Task tags |
| user_id | string (UUID) | Yes | Owner user identifier |
| created_at | string (ISO 8601) | Yes | Creation timestamp |
| updated_at | string (ISO 8601) | Yes | Update timestamp |

### TaskUpdate DTO
**Purpose**: Data transfer object for updating existing tasks

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| title | string | No | 1-200 chars | Task title |
| description | string | No | 0-1000 chars | Task description |
| completed | boolean | No | boolean | Completion status |
| priority | string | No | enum: low, medium, high, critical | Task priority |
| tags | array of strings | No | max 10 tags, 1-50 chars each | Task tags |

## Database Indexes

### Primary Indexes
- `tasks.id`: Primary key index (automatically created)
- `users.id`: Primary key index (automatically created)

### Secondary Indexes
- `tasks.user_id`: Index for efficient user-based queries
- `tasks.completed`: Index for filtering completed tasks
- `tasks.priority`: Index for priority-based queries
- `task_tags.task_id`: Index for task-based tag queries
- `task_tags.tag_name`: Index for tag-based queries

### Composite Indexes
- `tasks.user_id + tasks.completed`: For user completion queries
- `task_tags.task_id + tag_name`: For unique constraint and efficient lookups

## Business Rules

### User Isolation
- Users can only create, read, update, or delete tasks they own
- User_id from JWT token must match task's user_id
- Unauthorized access attempts return 403 Forbidden

### Task Uniqueness
- Task titles must be unique per user (to be implemented if required)
- Each task-tag combination must be unique

### Data Integrity
- Referential integrity enforced through foreign key constraints
- All required fields must be present for task creation
- Priority values restricted to defined enum values

## Performance Considerations

### Query Optimization
- Queries filtered by user_id will use the user_id index
- Priority and completion status queries will use their respective indexes
- Tag queries will use indexes on task_tags table

### Scalability
- UUID primary keys support distributed systems
- Proper indexing supports large datasets
- Timestamps enable efficient archival strategies

## Migration Requirements

### Initial Schema
- Create users table if not exists
- Create tasks table with all specified fields and constraints
- Create task_tags table for many-to-many relationship
- Create all required indexes
- Set up foreign key relationships with proper constraints

### Future Considerations
- Potential full-text search index on title/description
- Archive/completion date indexes if needed for historical queries
- Soft delete capability if required for data retention policies