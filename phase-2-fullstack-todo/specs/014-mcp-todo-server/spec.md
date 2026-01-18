# Feature Specification: MCP Server for Todo Management

**Feature Branch**: `014-mcp-todo-server`
**Created**: 2025-12-30
**Status**: Draft
**Input**: User description: "Set up MCP Server for Todo Management using FastMCP. Create a Python MCP server that exposes todo CRUD operations as MCP tools. Include tools for: create_task, update_task, delete_task, list_tasks, search_tasks, mark_complete. Use FastMCP decorators (@mcp.tool()) with proper inputSchema/outputSchema validation. Server should connect to existing Neon PostgreSQL database via SQLModel. Include lifespan management for database connections."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - AI Agent Creates Task via MCP Tool (Priority: P1)

An AI agent (powered by OpenAI Agents SDK or similar) needs to create a new task for a user through natural language conversation. The agent invokes the MCP server's create_task tool, passing user identification and task details. The MCP server validates the input, creates the task in the database, and returns confirmation to the agent.

**Why this priority**: Task creation is the most fundamental operation. Without the ability to create tasks, no other task management functionality has value. This establishes the core integration pattern between AI agents and the task database.

**Independent Test**: Can be fully tested by invoking the create_task tool with valid user credentials and task data, verifying the task appears in the database with correct attributes.

**Acceptance Scenarios**:

1. **Given** a valid user ID and task title, **When** the create_task tool is invoked, **Then** a new task is created and the tool returns the task ID and confirmation status.
2. **Given** a valid user ID, task title, and optional description, **When** the create_task tool is invoked, **Then** the task is created with all provided attributes stored correctly.
3. **Given** an invalid or missing user ID, **When** the create_task tool is invoked, **Then** the tool returns an error indicating the user was not found.
4. **Given** an empty task title, **When** the create_task tool is invoked, **Then** the tool returns a validation error specifying that title is required.

---

### User Story 2 - AI Agent Lists User Tasks (Priority: P1)

An AI agent needs to retrieve a user's tasks to answer questions like "What are my tasks?" or "Show me my pending items." The agent invokes the list_tasks tool with optional filters (status: all/pending/completed) and receives a list of tasks belonging to that user.

**Why this priority**: Listing tasks is essential for the AI to provide meaningful responses about the user's task state. It's used in almost every conversational flow after initial task creation.

**Independent Test**: Can be fully tested by creating test tasks for a user, then invoking list_tasks with various filter combinations and verifying the returned list matches expected tasks.

**Acceptance Scenarios**:

1. **Given** a user with existing tasks, **When** list_tasks is invoked with status "all", **Then** all tasks for that user are returned.
2. **Given** a user with both completed and pending tasks, **When** list_tasks is invoked with status "pending", **Then** only incomplete tasks are returned.
3. **Given** a user with both completed and pending tasks, **When** list_tasks is invoked with status "completed", **Then** only completed tasks are returned.
4. **Given** a user with no tasks, **When** list_tasks is invoked, **Then** an empty list is returned (not an error).
5. **Given** an invalid user ID, **When** list_tasks is invoked, **Then** an error indicating user not found is returned.

---

### User Story 3 - AI Agent Marks Task Complete (Priority: P2)

When a user says "I finished buying groceries" or "Mark task 3 as done", the AI agent needs to update the task's completion status. The agent invokes mark_complete with the task ID, and the server updates the task and confirms the action.

**Why this priority**: Completing tasks is the primary goal of a todo system. Users frequently indicate task completion through natural language.

**Independent Test**: Can be fully tested by creating a pending task, invoking mark_complete, and verifying the task's completed status changes to true in the database.

**Acceptance Scenarios**:

1. **Given** an existing pending task, **When** mark_complete is invoked with the task ID, **Then** the task's completed status becomes true and confirmation is returned.
2. **Given** an already completed task, **When** mark_complete is invoked, **Then** the task remains completed and a success response is returned (idempotent operation).
3. **Given** a non-existent task ID, **When** mark_complete is invoked, **Then** a "task not found" error is returned.
4. **Given** a task belonging to a different user, **When** mark_complete is invoked, **Then** a "task not found" or "access denied" error is returned (user isolation enforced).

---

### User Story 4 - AI Agent Updates Task Details (Priority: P2)

When a user says "Change task 1 to 'Call mom tonight'" or "Update the description of my grocery task", the AI agent needs to modify task attributes. The update_task tool allows changing title and/or description.

**Why this priority**: Users frequently need to refine or correct task details after initial creation.

**Independent Test**: Can be fully tested by creating a task, invoking update_task with new values, and verifying the changes persist in the database.

**Acceptance Scenarios**:

1. **Given** an existing task, **When** update_task is invoked with a new title, **Then** the task title is updated and confirmation is returned.
2. **Given** an existing task, **When** update_task is invoked with a new description, **Then** the task description is updated.
3. **Given** an existing task, **When** update_task is invoked with both new title and description, **Then** both fields are updated.
4. **Given** a non-existent task ID, **When** update_task is invoked, **Then** a "task not found" error is returned.
5. **Given** an empty title in the update request, **When** update_task is invoked, **Then** a validation error is returned (title cannot be cleared).

---

### User Story 5 - AI Agent Deletes Task (Priority: P2)

When a user says "Delete task 2" or "Remove the meeting task", the AI agent needs to permanently remove a task. The delete_task tool removes the task from the database.

**Why this priority**: Users need the ability to remove tasks that are no longer relevant.

**Independent Test**: Can be fully tested by creating a task, invoking delete_task, and verifying the task no longer exists in the database.

**Acceptance Scenarios**:

1. **Given** an existing task, **When** delete_task is invoked with the task ID, **Then** the task is permanently removed and confirmation is returned.
2. **Given** a non-existent task ID, **When** delete_task is invoked, **Then** a "task not found" error is returned.
3. **Given** a task belonging to a different user, **When** delete_task is invoked, **Then** a "task not found" or "access denied" error is returned.

---

### User Story 6 - AI Agent Searches Tasks (Priority: P3)

When a user asks "Find my tasks about shopping" or "Search for anything related to work", the AI agent needs to search through task titles and descriptions. The search_tasks tool performs text-based search across the user's tasks.

**Why this priority**: Search is valuable for users with many tasks but is an enhancement over basic listing functionality.

**Independent Test**: Can be fully tested by creating tasks with specific keywords, invoking search_tasks, and verifying matching tasks are returned.

**Acceptance Scenarios**:

1. **Given** tasks containing the word "groceries", **When** search_tasks is invoked with query "groceries", **Then** all tasks with "groceries" in title or description are returned.
2. **Given** a search query with no matches, **When** search_tasks is invoked, **Then** an empty list is returned (not an error).
3. **Given** a case-insensitive search query, **When** search_tasks is invoked with "GROCERIES", **Then** tasks containing "groceries" (any case) are returned.
4. **Given** a partial word search, **When** search_tasks is invoked with "groc", **Then** tasks containing words starting with "groc" are returned.

---

### Edge Cases

- What happens when the database connection is unavailable at server startup?
  - Server should fail to start with a clear error message indicating database connectivity issue.
- What happens when the database connection drops during a tool invocation?
  - Tool should return an error indicating temporary unavailability, not crash the server.
- What happens when a user provides extremely long task titles (e.g., 10,000 characters)?
  - Validation should reject input exceeding reasonable limits (200 characters for title).
- What happens when multiple tools are invoked simultaneously for the same user?
  - Each operation should complete independently without race conditions.
- What happens when the server receives malformed input that doesn't match the expected schema?
  - Server should return a validation error with details about what was expected.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST expose a `create_task` tool that accepts user ID, title (required), and description (optional), creating a new task and returning the created task's ID and status.
- **FR-002**: System MUST expose a `list_tasks` tool that accepts user ID and optional status filter (all/pending/completed), returning all matching tasks for that user.
- **FR-003**: System MUST expose a `mark_complete` tool that accepts user ID and task ID, marking the specified task as completed.
- **FR-004**: System MUST expose an `update_task` tool that accepts user ID, task ID, and optional new title/description, updating the specified fields.
- **FR-005**: System MUST expose a `delete_task` tool that accepts user ID and task ID, permanently removing the task.
- **FR-006**: System MUST expose a `search_tasks` tool that accepts user ID and search query, returning tasks where title or description contains the query text.
- **FR-007**: System MUST enforce user isolation - each tool MUST only access/modify tasks belonging to the specified user ID.
- **FR-008**: System MUST validate all inputs against defined schemas before processing, returning descriptive errors for invalid input.
- **FR-009**: System MUST manage database connections with proper lifecycle management - opening connections at startup and closing them gracefully at shutdown.
- **FR-010**: System MUST return structured responses with consistent format including status, data, and error information.
- **FR-011**: System MUST handle database errors gracefully, returning appropriate error responses without crashing.
- **FR-012**: System MUST validate that task titles are between 1 and 200 characters.
- **FR-013**: System MUST validate that task descriptions do not exceed 2000 characters.

### Key Entities

- **Task**: Represents a todo item belonging to a user. Key attributes: unique identifier, user ownership, title, description, completion status, creation timestamp, last update timestamp.
- **User**: The owner of tasks. Referenced by user ID to enforce data isolation. (Note: User entity already exists in the system from Phase II)
- **Tool Response**: Standardized structure for all MCP tool responses containing: task_id (when applicable), status (created/updated/deleted/completed/found), title (for confirmation), and error details (when failed).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: AI agents can successfully create, read, update, and delete tasks through MCP tools with 99.9% reliability during normal database operation.
- **SC-002**: All 6 MCP tools respond within 500 milliseconds under normal load (single user operations).
- **SC-003**: System correctly enforces user isolation - 100% of cross-user access attempts are blocked.
- **SC-004**: Input validation catches 100% of malformed requests before database operations are attempted.
- **SC-005**: Server gracefully handles database disconnection, returning appropriate errors without crashing.
- **SC-006**: Search functionality returns relevant results for 95% of keyword-based queries.
- **SC-007**: System maintains stable database connections across server lifecycle without connection leaks.

## Assumptions

- The existing Neon PostgreSQL database and SQLModel models from Phase II are available and operational.
- The existing Task model includes: id, user_id, title, description, completed, created_at, updated_at fields.
- User authentication and authorization are handled externally - the MCP server receives already-validated user IDs.
- The MCP server will be invoked by AI agents (OpenAI Agents SDK) as part of the Phase III chatbot architecture.
- Connection pooling configuration will use sensible defaults (min 1, max 10 connections).
- The server will run as a single instance initially (horizontal scaling is a future consideration).

## Dependencies

- Phase II database infrastructure (Neon PostgreSQL with existing Task and User tables)
- Phase II SQLModel models (Task, User, TaskTag if applicable)
- MCP SDK for Python (FastMCP or official implementation)
- Environment configuration for database connection string

## Implementation Resources

### Available Agents
- **mcp-server-builder**: Autonomous agent for building MCP servers with FastMCP. Use for creating MCP tool servers, implementing database-connected tools, setting up MCP transport, and integrating with AI agents. Location: `.claude/agents/mcp-server-builder.md`

### Available Skills
- **mcp-server-tools**: Skill for creating MCP servers with FastMCP that expose tools to AI agents. Provides patterns for:
  - Basic MCP server with tools using `@mcp.tool()` decorator
  - Database lifespan management with async context managers
  - Input/output schema validation with Pydantic models
  - Location: `.claude/skills/mcp-server-tools/SKILL.md`

### Related Skills (Supporting)
- **sqlmodel-database-modeling**: Database modeling patterns
- **python-type-safety**: Type hints and Pydantic validation
- **pytest-api-testing**: Testing patterns for the MCP tools
