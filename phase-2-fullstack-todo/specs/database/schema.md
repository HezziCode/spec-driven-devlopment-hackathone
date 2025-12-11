# Database Schema Specification

## Overview
This document defines the database schema for the Phase 2 full-stack todo web application. The database uses Neon PostgreSQL and follows a user-isolation model where each user's data is separated by user_id.

## Technology Stack
- **Database**: Neon Serverless PostgreSQL
- **ORM**: SQLModel (combines SQLAlchemy and Pydantic)
- **Connection**: Connection pooling with proper security settings

## Database Tables

### users Table
Stores user account information.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, NOT NULL | Unique identifier for the user |
| username | VARCHAR(50) | UNIQUE, NOT NULL | User's chosen username |
| email | VARCHAR(100) | UNIQUE, NOT NULL | User's email address |
| password_hash | VARCHAR(255) | NOT NULL | Hashed password using secure algorithm |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Account creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes:**
- Primary key on `id`
- Unique index on `email`
- Unique index on `username`

**Constraints:**
- Email format validation
- Username length between 3-50 characters
- Password must meet complexity requirements

### tasks Table
Stores todo tasks with user association and metadata.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, NOT NULL | Unique identifier for the task |
| user_id | UUID | FOREIGN KEY, NOT NULL | Reference to the user who owns the task |
| title | VARCHAR(200) | NOT NULL | Task title |
| description | TEXT | NULL | Detailed task description |
| completed | BOOLEAN | NOT NULL, DEFAULT FALSE | Completion status |
| priority | VARCHAR(20) | NOT NULL, DEFAULT 'medium' | Task priority (low, medium, high, critical) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Task creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes:**
- Primary key on `id`
- Index on `user_id` for efficient user-based queries
- Index on `completed` for filtering completed tasks
- Index on `priority` for priority-based queries
- Composite index on `user_id` and `completed` for user completion queries

**Constraints:**
- Foreign key constraint linking `user_id` to `users.id`
- Title length between 1-200 characters
- Priority must be one of: 'low', 'medium', 'high', 'critical'

### task_tags Table
Stores tags that can be associated with tasks (many-to-many relationship).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, NOT NULL | Unique identifier for the tag association |
| task_id | UUID | FOREIGN KEY, NOT NULL | Reference to the task |
| tag_name | VARCHAR(50) | NOT NULL | Name of the tag |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Association creation timestamp |

**Indexes:**
- Primary key on `id`
- Index on `task_id` for task-based queries
- Index on `tag_name` for tag-based queries
- Composite index on `task_id` and `tag_name` for unique constraint

**Constraints:**
- Foreign key constraint linking `task_id` to `tasks.id`
- Tag name length between 1-50 characters
- Unique constraint on `task_id` and `tag_name` combination

## Relationships

### User to Tasks
- **Relationship**: One-to-Many (One user has many tasks)
- **Foreign Key**: `tasks.user_id` references `users.id`
- **Cascade**: No cascade on user deletion (tasks remain but user_id becomes invalid)

### Task to Tags
- **Relationship**: Many-to-Many (One task can have multiple tags, one tag can be on multiple tasks)
- **Through Table**: `task_tags`
- **Foreign Keys**:
  - `task_tags.task_id` references `tasks.id`
  - `task_tags.tag_name` references tag names

## Security Considerations
- All user data is isolated by `user_id`
- No cross-user access is possible without proper authentication
- Passwords are stored as secure hashes (not plain text)
- Database connections use SSL encryption
- Connection pooling with proper security settings

## Performance Considerations
- Proper indexing on frequently queried columns
- Efficient foreign key relationships
- UUID primary keys for distributed systems compatibility
- Timestamp columns for audit trails and caching

## Migration Strategy
- Database schema changes will be handled through migration scripts
- Backward compatibility maintained during schema evolution
- Proper backup procedures before any schema changes
- Rollback plans for each migration

## Data Integrity
- Foreign key constraints to maintain referential integrity
- NOT NULL constraints on required fields
- Unique constraints where appropriate
- Check constraints for value validation (e.g., priority values)

## Assumptions
- Database is hosted on Neon Serverless PostgreSQL
- Connection pooling is properly configured
- Database credentials are stored securely in environment variables
- Database access is properly secured and monitored