# Feature Specification: Fix Chat Task Creation and Implement Persistent Chat History

**Feature Branch**: `019-fix-chat-task-persistence`
**Created**: 2026-01-05
**Status**: Draft
**Input**: User description: "Fix chat task creation failures and implement persistent chat history with 20-message limit. Agent should successfully use MCP tools to create tasks, and chat conversations should persist across server restarts with a maximum of 20 chat histories."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Agent Successfully Creates Tasks via Natural Language (Priority: P1)

Users interact with the AI chat agent to create tasks using natural language commands like "I need to buy groceries tomorrow" or "Add a task to finish the project report". The agent understands the intent, calls the appropriate MCP tool, and successfully creates the task in the database.

**Why this priority**: This is the core functionality of the AI chat feature. Without reliable task creation, the chat interface provides no value to users. This is a critical bug fix that blocks all other chat functionality.

**Independent Test**: Can be fully tested by sending a natural language message to create a task, verifying the agent responds with success confirmation, and checking that the task appears in the Tasks page. Delivers immediate value by enabling the primary use case.

**Acceptance Scenarios**:

1. **Given** a user is authenticated and on the chat page, **When** they send "I need to buy groceries tomorrow", **Then** the agent responds with "Done! I've added 'Buy groceries' to your tasks" and the task appears in the task list
2. **Given** a user sends a task creation request, **When** the agent processes the message, **Then** the MCP tool is called successfully without 401 or 500 errors
3. **Given** a task is created via chat, **When** the user navigates to the Tasks page, **Then** the newly created task is visible with correct title and description
4. **Given** a user sends multiple task creation requests in sequence, **When** each request is processed, **Then** all tasks are created successfully without failures

---

### User Story 2 - Chat Messages Persist Across Sessions (Priority: P2)

Users expect their chat conversations to be saved and available when they return to the application. When a user refreshes the page or the server restarts, their previous chat messages and conversations should still be accessible.

**Why this priority**: Persistent chat history is essential for a good user experience. Users need to reference previous conversations and maintain context across sessions. Without persistence, users lose all conversation history on every page refresh, making the chat feature frustrating to use.

**Independent Test**: Can be tested by creating a chat conversation, refreshing the browser, and verifying all messages are still visible. Also test by restarting the backend server and confirming chat history loads correctly. Delivers value by maintaining conversation context.

**Acceptance Scenarios**:

1. **Given** a user has an active chat conversation with 5 messages, **When** they refresh the browser page, **Then** all 5 messages are still visible in the correct order
2. **Given** a user has multiple chat threads, **When** they switch between threads, **Then** each thread displays its own message history correctly
3. **Given** the backend server is restarted, **When** a user opens the chat page, **Then** their previous chat threads and messages are loaded from the database
4. **Given** a user sends a message, **When** the message is successfully sent, **Then** it is immediately saved to the database before the response is generated

---

### User Story 3 - Chat History Limit Prevents Database Bloat (Priority: P3)

The system enforces a maximum of 20 chat conversation threads per user. When a user reaches this limit and creates a new conversation, the system displays a warning message similar to "Chat history is full. Please delete some conversations to create new ones." The system prevents creating new threads beyond the limit.

**Why this priority**: This is an operational concern to prevent unlimited database growth and maintain system performance. While important for long-term sustainability, it's lower priority than fixing core functionality and basic persistence.

**Independent Test**: Can be tested by creating 20 chat threads, attempting to create a 21st thread, and verifying the warning message appears and no new thread is created. Delivers value by ensuring system scalability and preventing resource exhaustion.

**Acceptance Scenarios**:

1. **Given** a user has 20 existing chat threads, **When** they attempt to create a new chat, **Then** the system displays "Chat history is full. Delete some conversations to create new ones" and prevents thread creation
2. **Given** a user has 20 chat threads and deletes one, **When** they create a new chat, **Then** the new thread is created successfully
3. **Given** a user has fewer than 20 threads, **When** they create a new chat, **Then** the thread is created without any warnings
4. **Given** a user reaches the 20-thread limit, **When** they try to send a message without selecting a thread, **Then** the system prompts them to either select an existing thread or delete old threads

---

### Edge Cases

- What happens when a user sends a message while the backend is processing a previous message? (Should queue or show loading state)
- How does the system handle network failures during message sending? (Should retry or show error with retry option)
- What happens if the MCP server is unavailable when the agent tries to create a task? (Should return graceful error message to user)
- How does the system handle very long messages (>10,000 characters)? (Should validate and truncate or reject)
- What happens when a user deletes a task that was created via chat? (Chat history should remain, but task reference becomes invalid)
- How does the system handle concurrent message sending in the same thread? (Should process sequentially or handle race conditions)
- What happens if database save fails after agent generates a response? (Should retry save or notify user)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST successfully call MCP server tools from agent functions without authentication errors
- **FR-002**: System MUST persist all chat messages (user and agent) to the database immediately after they are sent/generated
- **FR-003**: System MUST persist chat thread metadata (name, last message preview, message count, timestamps) to the database
- **FR-004**: System MUST load chat thread list from database on page load, sorted by most recent activity
- **FR-005**: System MUST load all messages for a selected thread from the database
- **FR-006**: System MUST enforce a maximum of 20 chat threads per user
- **FR-007**: System MUST display a clear warning message when user reaches the 20-thread limit
- **FR-008**: System MUST prevent creating new threads when user has 20 existing threads
- **FR-009**: System MUST allow users to delete chat threads to free up space for new conversations
- **FR-010**: Agent MUST successfully parse natural language task creation requests and extract title and description
- **FR-011**: Agent MUST call the create_task MCP tool with correct user_id, title, and description parameters
- **FR-012**: System MUST return task creation success/failure status to the agent
- **FR-013**: Agent MUST provide clear success confirmation messages when tasks are created (e.g., "Done! I've added 'Task Title' to your tasks")
- **FR-014**: Agent MUST provide clear error messages when task creation fails, without exposing technical details
- **FR-015**: System MUST maintain thread_id consistency between frontend localStorage and backend database
- **FR-016**: System MUST handle server restarts gracefully, with all chat data persisting across restarts
- **FR-017**: System MUST sync thread metadata (message count, last message preview) after each message exchange
- **FR-018**: System MUST validate that MCP tool responses are properly formatted before returning to agent

### Key Entities

- **ChatThread**: Represents a conversation thread with attributes: id (UUID), user_id (UUID), name (string), last_message_preview (string), message_count (integer), created_at (timestamp), updated_at (timestamp)
- **ChatMessage**: Represents a single message in a conversation with attributes: id (UUID), thread_id (UUID), role (enum: 'user' or 'assistant'), content (text), created_at (timestamp)
- **Task**: Existing entity that is created via MCP tools, linked to user_id

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of natural language task creation requests result in successful task creation (no "It looks like there was an issue" errors)
- **SC-002**: Chat messages persist across browser refreshes with 100% accuracy (all messages visible after refresh)
- **SC-003**: Chat threads persist across server restarts with 100% accuracy (all threads and messages available after restart)
- **SC-004**: Users can create up to 20 chat threads without errors
- **SC-005**: System prevents creating a 21st thread and displays appropriate warning message
- **SC-006**: Agent response time for task creation remains under 5 seconds for 95% of requests
- **SC-007**: Chat message load time is under 2 seconds for threads with up to 50 messages
- **SC-008**: Zero MCP authentication errors (401) in backend logs during agent tool calls
- **SC-009**: Task creation success rate via chat matches direct API task creation success rate (both should be 100%)

## Assumptions

- The MCP server authentication fix (adding `/mcp/` to public paths) has been applied
- The database schema for chat_threads and chat_messages tables already exists (from previous ChatKit implementation)
- Users are authenticated via JWT tokens before accessing the chat interface
- The OpenAI Agents SDK and MCP server are properly configured and running
- Frontend uses localStorage for temporary thread state management
- Backend uses PostgreSQL (Neon) for persistent storage
- The 20-thread limit applies per user, not globally
- Deleted threads are permanently removed from the database (no soft delete)
- Message content is stored as plain text without encryption (unless specified in security requirements)

## Dependencies

- Backend: FastAPI, SQLModel, OpenAI Agents SDK, FastMCP, PostgreSQL (Neon)
- Frontend: Next.js, React, localStorage API
- External: OpenAI API for agent inference
- Database: Existing chat_threads and chat_messages tables must be properly indexed
- Authentication: JWT middleware must be functioning correctly

## Out of Scope

- Message editing or deletion (users cannot modify sent messages)
- Message search functionality within chat history
- Exporting chat history to external formats
- Real-time collaboration (multiple users in same chat)
- Message encryption or privacy features beyond user isolation
- Chat analytics or usage statistics
- Voice input/output for chat messages
- File attachments in chat messages
- Rich text formatting in messages (markdown, code blocks, etc.)
- Conversation branching or forking
- Message reactions or emoji responses

## Security Considerations

- All chat operations must verify user_id matches authenticated user (user isolation)
- Chat threads and messages must be filtered by user_id to prevent cross-user access
- MCP tool calls must include user_id to ensure tasks are created for the correct user
- Input validation must prevent SQL injection and XSS attacks in message content
- Rate limiting should be considered to prevent chat spam or abuse

## Performance Considerations

- Database queries for chat threads should use indexes on user_id and updated_at
- Message loading should be paginated for threads with many messages (though 50 messages is reasonable limit)
- Thread list should be cached in frontend to reduce database queries
- MCP tool calls should have appropriate timeouts to prevent hanging requests
