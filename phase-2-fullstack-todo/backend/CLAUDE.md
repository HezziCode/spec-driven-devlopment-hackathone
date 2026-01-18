# Backend CLAUDE.md: Guidelines for FastAPI Backend in Phase 2/3 Todo Web App

This file provides specific guidelines for developing the backend of the Phase 2/3 Full-Stack Todo Web App using FastAPI, SQLModel, Neon PostgreSQL, and MCP Server for AI agents.

## Technology Stack
- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLModel (for database operations)
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: Better Auth JWT verification
- **MCP Framework**: FastMCP 2.x (for AI agent tools)
- **Package Management**: UV for dependency management
- **Server**: Uvicorn for running the application

## Project Structure
```
/backend/
├── main.py                 # FastAPI application entry point (with MCP mount)
├── db.py                   # Database connection and session management
├── models.py               # SQLModel database models
├── /mcp_server/            # MCP Server for AI agents (Phase 3)
│   ├── __init__.py         # Package exports
│   ├── server.py           # FastMCP server instance and lifespan
│   ├── schemas.py          # Pydantic schemas for MCP tool I/O
│   └── tools.py            # MCP tool implementations (6 tools)
├── /routes/                # API route handlers
│   ├── __init__.py
│   ├── auth.py             # Authentication endpoints
│   ├── tasks.py            # Task management endpoints
│   └── users.py            # User management endpoints
├── /schemas/               # Pydantic schemas for request/response validation
│   ├── __init__.py
│   ├── task.py             # Task-related schemas
│   ├── user.py             # User-related schemas
│   └── auth.py             # Authentication schemas
├── /services/              # Business logic layer
│   ├── __init__.py
│   ├── task_service.py     # Task business logic
│   └── user_service.py     # User business logic
├── /middleware/            # Custom middleware
│   ├── __init__.py
│   └── auth_middleware.py  # JWT authentication middleware
├── /utils/                 # Utility functions
│   ├── __init__.py
│   ├── jwt_utils.py        # JWT token utilities
│   └── security.py         # Security utilities
├── /tests/                 # Backend tests
│   └── test_mcp_tools.py   # MCP tools tests
├── pyproject.toml          # Project dependencies and configuration
└── .env                    # Environment variables (not committed)
```

## API Conventions
### Request/Response Handling
- Use Pydantic models for all request and response validation
- Return JSON responses for all API endpoints
- Use HTTPException for error responses with appropriate status codes
- Follow RESTful API principles for endpoint design

### HTTP Status Codes
- 200: Success for GET, PUT, PATCH requests
- 201: Success for POST requests (resource created)
- 204: Success for DELETE requests (no content)
- 400: Bad Request (validation errors)
- 401: Unauthorized (authentication required)
- 403: Forbidden (insufficient permissions)
- 404: Not Found (resource not found)
- 422: Unprocessable Entity (validation errors)
- 500: Internal Server Error (unexpected errors)

### Error Handling
- Use FastAPI's built-in HTTPException for standardized error responses
- Create custom exceptions that inherit from HTTPException when needed
- Include meaningful error messages in responses
- Log errors appropriately for debugging

## Database Operations
### SQLModel Usage
- Use SQLModel for all database models combining SQLAlchemy and Pydantic
- Define relationships between models using SQLModel's relationship fields
- Use TypedDict for complex query results when needed
- Follow SQLModel's best practices for model definitions

### Environment Variables
- Use DATABASE_URL for database connection string
- Use BETTER_AUTH_SECRET for JWT secret key
- Use other environment variables as needed for configuration
- Store sensitive data in environment variables, never in code

### Database Connection Management
- Use SQLModel's create_engine for database connection
- Implement proper session management with context managers
- Handle database connection pooling appropriately
- Use transactions for operations that modify multiple records

## Authentication Implementation
### JWT Middleware
- Implement JWT middleware for authentication verification
- Verify JWT tokens against the shared secret (BETTER_AUTH_SECRET)
- Extract user information from JWT payloads
- Attach user context to request objects for use in route handlers

### User Isolation
- Ensure all API endpoints verify user_id matches JWT claims
- Implement proper authorization checks for resource access
- Prevent cross-user data access through proper user_id validation
- Return 403 Forbidden for unauthorized access attempts

## Development Guidelines
### Type Safety
- Use strict type hints for all functions and variables
- Leverage Pydantic for request/response validation
- Use mypy for static type checking
- Avoid using 'any' type - create proper type definitions

### Code Organization
- Separate concerns into different modules (models, routes, services, utils)
- Use dependency injection for service dependencies
- Implement repository pattern for database operations if needed
- Keep route handlers thin by delegating to service layer

### Testing
- Write comprehensive unit tests for business logic
- Write integration tests for API endpoints
- Test authentication and authorization flows
- Test error handling and edge cases
- Aim for high test coverage (90%+)

## Running the Application
### Development
- Use uvicorn for running the application: `uvicorn main:app --reload`
- Set environment variables in .env file for local development
- Use proper logging for debugging during development

### Production
- Deploy with uvicorn in production mode
- Use proper process managers (like systemd) for production deployments
- Implement proper monitoring and logging
- Set up health check endpoints

## Security Considerations
### Input Validation
- Use Pydantic models for all input validation
- Sanitize and validate all user inputs
- Implement rate limiting for API endpoints
- Use parameterized queries to prevent SQL injection

### Authentication Security
- Use HTTPS in production for all API communications
- Implement proper token expiration and refresh mechanisms
- Store JWT secrets securely in environment variables
- Implement proper token revocation if needed

### Database Security
- Use parameterized queries to prevent SQL injection
- Implement proper database access controls
- Encrypt sensitive data at rest when necessary
- Use connection pooling with proper security settings

## Performance Considerations
### Database Queries
- Optimize database queries with proper indexing
- Use eager loading to prevent N+1 query problems
- Implement pagination for large datasets
- Cache frequently accessed data when appropriate

### API Performance
- Implement proper request/response caching
- Use async/await for I/O operations
- Optimize JSON serialization/deserialization
- Monitor API response times and optimize bottlenecks

## Error Handling and Logging
### Logging Standards
- Use structured logging with appropriate log levels
- Include request IDs for tracing requests
- Log important business events and errors
- Avoid logging sensitive information

### Error Response Format
- Standardize error response format across all endpoints
- Include error codes for client-side error handling
- Provide meaningful error messages for debugging
- Log errors with full context for troubleshooting

## Environment Configuration
### Required Environment Variables
- DATABASE_URL: Database connection string for Neon PostgreSQL
- BETTER_AUTH_SECRET: Secret key for JWT token verification
- ENVIRONMENT: Development/Production/Staging flag
- LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR)

### Development Configuration
- Use .env file for local development environment variables
- Never commit .env files to version control
- Use different database URLs for different environments
- Implement configuration validation at startup

## Deployment Considerations
### Production Deployment
- Use Docker for containerization if needed
- Implement proper health check endpoints
- Set up proper monitoring and alerting
- Implement proper backup strategies for the database
- Use proper SSL certificates for HTTPS

## MCP Server (Phase 3)

### Overview
The MCP (Model Context Protocol) server exposes todo management functionality as tools for AI agents. It is mounted at the `/mcp` endpoint using FastMCP's SSE transport.

### Available Tools
| Tool | Description | Parameters |
|------|-------------|------------|
| `create_task` | Create a new task | user_id, title, description? |
| `list_tasks` | List user's tasks | user_id, status? (all/pending/completed) |
| `mark_complete` | Mark task as completed | user_id, task_id |
| `update_task` | Update task details | user_id, task_id, title?, description? |
| `delete_task` | Delete a task | user_id, task_id |
| `search_tasks` | Search tasks by keyword | user_id, query |

### Response Formats
**Success Response (single task operations):**
```json
{
  "task_id": "uuid",
  "status": "created|updated|deleted|completed",
  "title": "Task title"
}
```

**Success Response (list/search operations):**
```json
{
  "tasks": [{"id": "uuid", "title": "...", "completed": false, ...}],
  "total": 5
}
```

**Error Response:**
```json
{
  "error": "Error message",
  "code": "NOT_FOUND|VALIDATION_ERROR|DATABASE_ERROR",
  "task_id": "uuid (if applicable)"
}
```

### User Isolation
All MCP tools enforce user isolation by:
1. Requiring `user_id` parameter on all operations
2. Filtering database queries by `user_id`
3. Returning "not found" for resources belonging to other users

### Integration with AI Agents
The MCP server can be used with:
- OpenAI Agents SDK: Connect via `http://localhost:8000/mcp`
- FastMCP Client: Use `fastmcp.client.Client` for direct tool invocation
- Any MCP-compatible AI framework

### Testing MCP Tools
```bash
# Run unit tests (no database required)
uv run pytest tests/test_mcp_tools.py -v -k "not integration"

# Run integration tests (requires database)
uv run pytest tests/test_mcp_tools.py -v -m integration
```

### Adding New Tools
1. Define input schema in `mcp_server/schemas.py`
2. Implement tool function in `mcp_server/tools.py` with `@mcp.tool()` decorator
3. Add tests in `tests/test_mcp_tools.py`
4. Update this documentation

## OpenAI Agents SDK Integration (Phase 3)

### Overview
The OpenAI Agents SDK integration provides a TaskManagerAgent that enables natural language task management. The agent uses `@function_tool` decorators to expose task operations and calls the existing MCP server tools for all database operations.

### Project Structure
```
/backend/
├── /agents/                 # OpenAI Agents SDK integration
│   ├── __init__.py         # Package exports
│   ├── agent.py            # TaskManagerAgent definition with AGENT_INSTRUCTIONS
│   ├── tools.py            # @function_tool implementations (7 tools)
│   ├── context.py          # AgentContext dataclass for user isolation
│   └── schemas.py          # Agent-specific Pydantic models
├── /routes/
│   └── chat.py             # POST /api/users/{user_id}/chat endpoint
├── /services/
│   └── chat_service.py     # Chat orchestration (process_message, etc.)
├── /schemas/
│   └── chat.py             # ChatRequest, ChatResponse, ToolCall schemas
```

### Available Agent Tools
| Tool | Description | Parameters |
|------|-------------|------------|
| `create_task` | Create a new task from natural language | ctx, title, description? |
| `list_tasks` | List user's tasks with optional status filter | ctx, status? |
| `get_task` | Get a specific task by ID | ctx, task_id |
| `mark_complete` | Mark task as completed | ctx, task_id |
| `update_task` | Update task title/description | ctx, task_id, title?, description? |
| `delete_task` | Delete a task | ctx, task_id |
| `search_tasks` | Search tasks by keyword | ctx, query |

### Agent Context
```python
from agents.context import AgentContext

@dataclass
class AgentContext:
    """Context passed to all agent tool invocations."""
    user_id: str                    # UUID of authenticated user
    conversation_id: str = None     # Conversation ID for context
    mcp_base_url: str = "http://localhost:8000"  # MCP server URL
```

### Chat Endpoint
**POST** `/api/users/{user_id}/chat`

**Request:**
```json
{
  "conversation_id": "uuid (optional)",
  "message": "I need to buy groceries this weekend"
}
```

**Response:**
```json
{
  "conversation_id": "uuid",
  "response": "Done! I've added 'Buy groceries' to your tasks.",
  "tool_calls": [
    {
      "tool_name": "create_task",
      "arguments": {"title": "Buy groceries"},
      "result": {"task_id": "uuid", "status": "created", "title": "Buy groceries"}
    }
  ]
}
```

### Usage Example
```python
from agents import Runner
from agents.agent import task_manager_agent
from agents.context import AgentContext

async def chat_with_agent(user_id: str, message: str):
    context = AgentContext(
        user_id=user_id,
        conversation_id=None,  # Creates new conversation if not provided
        mcp_base_url="http://localhost:8000"
    )

    result = await Runner.run(
        task_manager_agent,
        input=message,
        context=context
    )

    return result.final_output
```

### User Isolation
All agent tools enforce user isolation by:
1. Extracting `user_id` from AgentContext
2. Passing `user_id` to all MCP server calls
3. MCP server filters queries by `user_id`

### Testing Agent Tools
```bash
# Run agent tool tests
uv run pytest tests/test_agent_tools.py -v

# Run chat endpoint tests
uv run pytest tests/test_chat_endpoint.py -v
```

### Configuration
Required environment variables:
- `OPENAI_API_KEY`: OpenAI API key for agent inference
- `DATABASE_URL`: PostgreSQL connection (existing)
- `BETTER_AUTH_SECRET`: JWT secret (existing)