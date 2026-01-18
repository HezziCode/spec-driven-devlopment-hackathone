<!--
Sync Impact Report:
Version change: 3.0.0 → 3.1.0 (minor update: add Phase IV local Kubernetes deployment guidance)
Modified principles:
  - None
Added sections:
  - Phase IV: Local Kubernetes Deployment (Minikube + Helm + kubectl-ai/kagent + Docker Desktop/Gordon)
Enhanced sections:
  - Phase Evolution (Phase IV clarified)
  - Technology Stack table (Phase IV deployment/tooling rows)
Removed sections: None (all Phase II/III content preserved)
Templates requiring updates:
- .specify/templates/plan-template.md ✅ compatible (no changes needed)
- .specify/templates/spec-template.md ✅ compatible (no changes needed)
- .specify/templates/tasks-template.md ✅ compatible (no changes needed)
- .specify/templates/commands/*.md ⚠ pending review for Phase IV deployment commands
Follow-up TODOs:
- Create Phase IV deployment spec using /sp.specify when ready
-->
# TaskWave Todo Application Constitution

## Project Overview

This constitution governs the multi-phase evolution of the TaskWave Todo application from a simple console app to a cloud-native AI chatbot. The project follows Spec-Driven Development (SDD) methodology using Claude Code CLI and Spec-Kit Plus.

### Phase Evolution
- **Phase I**: In-memory Python console todo app (completed)
- **Phase II**: Full-stack web app with persistence (deployed)
- **Phase III**: AI-powered chatbot interface with MCP server (current)
- **Phase IV**: Local Kubernetes deployment (Minikube + Helm + kubectl-ai/kagent + Docker Desktop/Gordon)

## Core Principles

### I. Spec-Driven Development (SDD) with Agents/Skills
All development follows Spec-Driven Development methodology using agents and skills for automated code generation. No manual code writing from scratch; all implementation must be generated via Spec-Kit-Plus tools and Claude Code CLI. Agents and skills must be reusable and documented for future feature development.

### II. Clean Code with Single Responsibility Principle
Every function, class, and module must have a single, well-defined responsibility. All code must include comprehensive docstrings following Google or NumPy style. Code should be self-documenting with meaningful variable and function names. Functions should be short and focused on one task.

### III. Type Safety and Strict TypeScript/Python Typing (NON-NEGOTIABLE)
All code must be fully typed with no use of 'any' or 'object' types in TypeScript. Python code must use type hints for all function signatures and class attributes. Type checking must pass before any code is committed. Use strict mode in TypeScript and enable mypy checking for Python.

### IV. Accessibility Compliance (WCAG 2.1 AA)
All UI components and pages must meet WCAG 2.1 AA standards. This includes proper semantic HTML, ARIA labels, keyboard navigation, color contrast ratios, and screen reader compatibility. All interactive elements must be accessible via keyboard only.

### V. Performance-First Architecture
All code must follow O(1) or O(n) complexity where possible; avoid O(n²) or worse without explicit justification. Frontend components should be optimized for fast loading and rendering. Backend endpoints should respond within 200ms for 95th percentile requests. Database queries must be optimized with proper indexing.

### VI. Modular Architecture with Clear Boundaries
Frontend and backend must be clearly separated with well-defined API contracts. Each feature should be encapsulated in its own module with clear interfaces. Frontend components should follow a consistent architecture pattern (server components for data fetching, client components for interactivity). Backend routes should be organized by domain functionality.

### VII. Stateless Server Architecture (Phase III)
Server components MUST hold NO state between requests. All conversation state, message history, and session data MUST be persisted to the database. This ensures horizontal scalability, resilience to server restarts, and testability where each request is independent and reproducible.

## Technology Stack and Constraints

### Required Technology Stack
The project must use the following technology stack exactly as specified:

| Layer | Technology | Version | Purpose | Phase |
|-------|-----------|---------|---------|-------|
| Frontend | Next.js | 16+ with App Router | Web application framework | II, III |
| Frontend Language | TypeScript | Latest | Type-safe development | II, III |
| Frontend Styling | Tailwind CSS | Latest | Utility-first CSS framework | II, III |
| Chatbot UI | OpenAI ChatKit | Latest | Conversational interface | III |
| Backend | Python FastAPI | Python 3.11+ | RESTful API server | II, III |
| AI Framework | OpenAI Agents SDK | Latest | AI agent logic and orchestration | III |
| MCP Server | Official MCP SDK | Latest | Tool exposure for AI agents | III |
| ORM | SQLModel | Latest | Database operations and models | II, III |
| Database | Neon Serverless PostgreSQL | Latest | Persistent storage | II, III |
| Authentication | Better Auth | Latest with JWT plugin | User authentication and session management | II, III |
| Spec-Driven | Claude Code + Spec-Kit Plus | Latest | Automated development workflow | II, III |
| Package Management | UV (Python), npm (Frontend) | Latest | Dependency management | II, III |
| Testing | Pytest (Backend), Jest/Vitest (Frontend) | Latest | Test automation and coverage | II, III |
| Containerization | Docker (Docker Desktop) | Latest | Containerize frontend/backend (use Gordon if available) | IV |
| Docker AI Agent | Gordon (Docker AI) | Latest | AI-assisted Docker operations | IV |
| Kubernetes | Minikube | Latest | Local Kubernetes cluster for deployment | IV |
| Kubernetes Packaging | Helm Charts | Latest | Package and deploy app on Kubernetes | IV |
| AI DevOps | kubectl-ai, kagent | Latest | AI-assisted Kubernetes operations | IV |

### Project Structure (Monorepo)
```
phase-2-fullstack-todo/
├── .spec-kit/                    # Spec-Kit configuration
│   ├── config.yaml               # Spec-Kit settings
│   └── memory/
│       └── constitution.md       # This file
├── specs/                        # Spec-Kit managed specifications
│   ├── overview.md               # Project overview and status
│   ├── architecture.md           # System architecture (optional)
│   ├── features/                 # Feature specifications
│   │   ├── task-crud.md          # Task CRUD operations
│   │   ├── authentication.md     # User authentication
│   │   ├── search-filter.md      # Search and filter features
│   │   └── ai-chatbot.md         # Phase III chatbot features
│   ├── api/                      # API specifications
│   │   ├── rest-endpoints.md     # RESTful API endpoints
│   │   ├── chat-endpoints.md     # Chat API endpoints (Phase III)
│   │   └── mcp-tools.md          # MCP server tools specification
│   ├── database/                 # Database specifications
│   │   └── schema.md             # Database schema and models
│   └── ui/                       # UI specifications
│       ├── components.md         # Reusable UI components
│       ├── pages.md              # Application pages
│       └── chatbot-ui.md         # ChatKit interface (Phase III)
├── CLAUDE.md                     # Root Claude Code instructions
├── frontend/
│   ├── CLAUDE.md                 # Frontend-specific guidelines
│   ├── app/                      # Next.js App Router pages
│   ├── components/               # React components
│   ├── lib/                      # Utility libraries
│   ├── public/                   # Static assets
│   ├── package.json              # Frontend dependencies
│   └── tsconfig.json             # TypeScript configuration
├── backend/
│   ├── CLAUDE.md                 # Backend-specific guidelines
│   ├── main.py                   # FastAPI application entry point
│   ├── db.py                     # Database connection and session
│   ├── models.py                 # SQLModel database models
│   ├── routes/                   # API route handlers
│   │   ├── auth.py               # Authentication endpoints
│   │   ├── tasks.py              # Task CRUD endpoints
│   │   ├── users.py              # User management endpoints
│   │   └── chat.py               # Chat endpoints (Phase III)
│   ├── schemas/                  # Pydantic request/response schemas
│   │   ├── task.py               # Task schemas
│   │   ├── user.py               # User schemas
│   │   ├── auth.py               # Auth schemas
│   │   └── chat.py               # Chat schemas (Phase III)
│   ├── services/                 # Business logic layer
│   │   ├── task_service.py       # Task business logic
│   │   ├── user_service.py       # User business logic
│   │   └── chat_service.py       # Chat orchestration (Phase III)
│   ├── mcp_server/               # MCP Server (Phase III)
│   │   ├── __init__.py           # MCP server initialization
│   │   ├── server.py             # MCP server implementation
│   │   └── tools/                # MCP tool implementations
│   │       ├── add_task.py       # Add task tool
│   │       ├── list_tasks.py     # List tasks tool
│   │       ├── complete_task.py  # Complete task tool
│   │       ├── delete_task.py    # Delete task tool
│   │       └── update_task.py    # Update task tool
│   ├── agents/                   # OpenAI Agents (Phase III)
│   │   ├── __init__.py           # Agent initialization
│   │   └── todo_agent.py         # Todo management agent
│   ├── middleware/               # Custom middleware
│   │   └── auth_middleware.py    # JWT verification middleware
│   ├── utils/                    # Utility functions
│   │   ├── jwt_utils.py          # JWT token utilities
│   │   └── security.py           # Security utilities
│   ├── tests/                    # Pytest tests
│   ├── pyproject.toml            # Python dependencies (UV)
│   └── .env                      # Environment variables (not committed)
├── docker-compose.yml            # Container orchestration (optional)
└── README.md                     # Project documentation

Key constraints:
- All features must support user isolation via JWT token verification
- Frontend must use Next.js App Router (not Pages Router)
- Backend must use UV for package management (not pip)
- Database must be Neon Serverless PostgreSQL (not local PostgreSQL)
- All API endpoints must follow RESTful conventions
- Monorepo structure required for unified development context
- Phase III: Server MUST be stateless - all state persisted to database
- Phase III: MCP tools MUST be stateless and store state in database
```

## Development Workflow and Quality Standards

Development follows a strict workflow: Specification → Planning → Task Generation → Agent/Skill Implementation → Testing → Commit. All commits must be atomic and include "Co-authored-by: Claude" attribution. No manual code editing by humans - all code must be generated via agents/skills. Every pull request must include comprehensive tests with 100% coverage for the changed functionality.

---

## Phase II: Required Features and API Endpoints

### Basic Level Features (All Required)
1. **Add Task** - Create new todo items with title, description, priority, and tags
2. **Delete Task** - Remove completed or unwanted tasks
3. **Update Task** - Modify task details, priority, or tags
4. **View Tasks** - Display all user's tasks with filtering and sorting
5. **Mark Complete/Incomplete** - Toggle task completion status

### Intermediate Features (Required)
6. **Task Prioritization** - Assign priority levels (Low, Medium, High, Critical)
7. **Task Categorization/Tagging** - Add multiple tags to organize tasks
8. **Search and Filter** - Search by title/description, filter by status/priority/tags
9. **Sort Tasks** - Sort by creation date, priority, or title

### Required API Endpoints

#### Authentication Endpoints (No JWT Required)
```
POST /auth/signup
  Request:  { "username": "string", "email": "string", "password": "string" }
  Response: { "user": { "id": "uuid", "username": "string", "email": "string" }, "token": "jwt_string" }
  Status:   201 Created | 400 Bad Request | 409 Conflict

POST /auth/login
  Request:  { "email": "string", "password": "string" }
  Response: { "user": { "id": "uuid", "username": "string", "email": "string" }, "token": "jwt_string" }
  Status:   200 OK | 400 Bad Request | 401 Unauthorized

POST /auth/logout
  Request:  (Empty body)
  Response: { "message": "Successfully logged out" }
  Status:   200 OK | 401 Unauthorized
```

#### Task Endpoints (JWT Required)
```
GET /api/users/{user_id}/tasks
  Query:    ?limit=20&offset=0&status=pending&priority=high&tag=work&search=meeting
  Response: { "tasks": [TaskObject], "total": number }
  Status:   200 OK | 401 Unauthorized | 403 Forbidden | 404 Not Found

POST /api/users/{user_id}/tasks
  Request:  { "title": "string", "description": "string", "priority": "medium", "tags": ["work", "urgent"] }
  Response: { "id": "uuid", "title": "string", "description": "string", "completed": false, "priority": "medium", "tags": ["work", "urgent"], "user_id": "uuid", "created_at": "ISO8601", "updated_at": "ISO8601" }
  Status:   201 Created | 400 Bad Request | 401 Unauthorized | 403 Forbidden | 422 Unprocessable Entity

GET /api/users/{user_id}/tasks/{task_id}
  Response: TaskObject
  Status:   200 OK | 401 Unauthorized | 403 Forbidden | 404 Not Found

PUT /api/users/{user_id}/tasks/{task_id}
  Request:  { "title": "string", "description": "string", "completed": boolean, "priority": "string", "tags": ["string"] }
  Response: TaskObject
  Status:   200 OK | 400 Bad Request | 401 Unauthorized | 403 Forbidden | 404 Not Found | 422 Unprocessable Entity

PATCH /api/users/{user_id}/tasks/{task_id}
  Request:  Any subset of task fields
  Response: TaskObject
  Status:   200 OK | 400 Bad Request | 401 Unauthorized | 403 Forbidden | 404 Not Found | 422 Unprocessable Entity

DELETE /api/users/{user_id}/tasks/{task_id}
  Response: { "message": "Task deleted successfully" }
  Status:   200 OK | 401 Unauthorized | 403 Forbidden | 404 Not Found
```

#### User Endpoints (JWT Required)
```
GET /api/users/{user_id}
  Response: { "id": "uuid", "username": "string", "email": "string", "created_at": "ISO8601", "updated_at": "ISO8601" }
  Status:   200 OK | 401 Unauthorized | 403 Forbidden | 404 Not Found

PUT /api/users/{user_id}
  Request:  { "username": "string", "email": "string" }
  Response: { "id": "uuid", "username": "string", "email": "string", "updated_at": "ISO8601" }
  Status:   200 OK | 400 Bad Request | 401 Unauthorized | 403 Forbidden | 404 Not Found | 422 Unprocessable Entity
```

### Database Schema Requirements

#### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE UNIQUE INDEX idx_users_username ON users(username);
```

#### Tasks Table
```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    priority VARCHAR(20) NOT NULL DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_user_completed ON tasks(user_id, completed);
```

#### Task Tags Table (Many-to-Many)
```sql
CREATE TABLE task_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    tag_name VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(task_id, tag_name)
);
CREATE INDEX idx_task_tags_task_id ON task_tags(task_id);
CREATE INDEX idx_task_tags_tag_name ON task_tags(tag_name);
```

### Authentication Flow: Better Auth + FastAPI JWT Integration

#### The Challenge
Better Auth is a JavaScript/TypeScript authentication library that runs on the Next.js frontend. However, FastAPI backend is a separate Python service that needs to verify which user is making API requests.

#### The Solution: JWT Tokens
Better Auth is configured to issue JWT (JSON Web Token) tokens when users log in. These tokens are self-contained credentials that include user information and can be verified by any service that knows the secret key.

#### How It Works
1. **User logs in on Frontend** → Better Auth creates a session and issues a JWT token
2. **Frontend makes API call** → Includes the JWT token in the `Authorization: Bearer <token>` header
3. **Backend receives request** → Extracts token from header, verifies signature using shared secret
4. **Backend identifies user** → Decodes token to get user ID, email, etc. and matches it with the user ID in the URL
5. **Backend filters data** → Returns only tasks belonging to that authenticated user

#### Required Changes

| Component | Changes Required |
|-----------|------------------|
| Better Auth Config | Enable JWT plugin to issue tokens |
| Frontend API Client | Attach JWT token to every API request header |
| FastAPI Backend | Add middleware to verify JWT and extract user |
| API Routes | Filter all queries by the authenticated user's ID |

#### The Shared Secret
Both frontend (Better Auth) and backend (FastAPI) must use the same secret key for JWT signing and verification. This is set via environment variable `BETTER_AUTH_SECRET` in both services.

#### Security Benefits
- **User Isolation**: Each user only sees their own tasks
- **Stateless Auth**: Backend doesn't need to call frontend to verify users
- **Token Expiry**: JWTs expire automatically (e.g., after 7 days)
- **No Shared DB Session**: Frontend and backend can verify auth independently

#### API Behavior After Authentication
- All endpoints (except `/auth/*`) require valid JWT token
- Requests without token receive `401 Unauthorized`
- Each user only sees/modifies their own tasks
- Task ownership is enforced on every operation

### Environment Variables Required

#### Backend `.env`
```bash
# Database
DATABASE_URL=postgresql://user:password@hostname/database?sslmode=require

# Authentication (shared with frontend)
BETTER_AUTH_SECRET=your-secret-key-here-minimum-32-characters

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO

# CORS (for frontend communication)
FRONTEND_URL=http://localhost:3000
ALLOWED_ORIGINS=http://localhost:3000,https://your-production-domain.com
```

#### Frontend `.env.local`
```bash
# Better Auth
BETTER_AUTH_SECRET=your-secret-key-here-minimum-32-characters  # Same as backend
BETTER_AUTH_URL=http://localhost:3000

# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Non-Functional Requirements (NFRs)

### Security Requirements
- All API endpoints (except `/auth/*`) must be secured with JWT token verification
- User data must be isolated by `user_id` to prevent cross-user access
- Path parameter `user_id` must match authenticated user's ID from JWT token
- Authentication tokens must be properly validated and refreshed
- Input validation and sanitization required for all user inputs
- Environment variables for secrets (`BETTER_AUTH_SECRET`, `DATABASE_URL`) must be properly configured
- Passwords must be hashed using bcrypt or argon2
- HTTPS required in production
- CORS properly configured to allow only trusted origins

### Reliability Standards
- 99.9% uptime for core functionality
- Proper error handling and graceful degradation
- Comprehensive logging for debugging and monitoring
- Automated backup and recovery procedures for database
- All API errors must follow standardized error response format

#### Error Response Format
All error responses must follow this consistent format:
```json
{
  "error": "Descriptive error message for developers",
  "code": "ERROR_CODE_IN_CAPS",
  "timestamp": "2025-12-23T20:00:00Z"
}
```

Example error responses:
```json
// 401 Unauthorized
{
  "error": "Missing or invalid JWT token",
  "code": "UNAUTHORIZED",
  "timestamp": "2025-12-23T20:00:00Z"
}

// 403 Forbidden
{
  "error": "User ID in path does not match authenticated user",
  "code": "FORBIDDEN",
  "timestamp": "2025-12-23T20:00:00Z"
}

// 404 Not Found
{
  "error": "Task with ID '123e4567-e89b-12d3-a456-426614174000' not found",
  "code": "NOT_FOUND",
  "timestamp": "2025-12-23T20:00:00Z"
}

// 422 Validation Error
{
  "error": "Title must be between 1 and 200 characters",
  "code": "VALIDATION_ERROR",
  "timestamp": "2025-12-23T20:00:00Z"
}
```

#### HTTP Status Codes
All API endpoints must use appropriate HTTP status codes:

| Code | Use Case | When to Use |
|------|----------|-------------|
| 200 | OK | Successful GET, PUT, PATCH requests |
| 201 | Created | Successful POST request (resource created) |
| 204 | No Content | Successful DELETE request (optional) |
| 400 | Bad Request | Malformed request, invalid JSON syntax |
| 401 | Unauthorized | Missing, invalid, or expired JWT token |
| 403 | Forbidden | Valid token but user not allowed to access resource |
| 404 | Not Found | Resource (task, user) doesn't exist |
| 409 | Conflict | Duplicate username or email on signup |
| 422 | Unprocessable Entity | Validation error (title too long, invalid priority) |
| 500 | Internal Server Error | Unexpected server errors (should be logged and monitored) |

### Scalability Considerations
- Architecture must support multiple concurrent users
- Database queries optimized for performance
- Caching strategies where appropriate
- Efficient resource utilization
- Connection pooling configured for database
- Rate limiting implemented to prevent abuse

## Spec-Kit Plus Workflow

### Required Workflow for All Features
All feature development must follow this exact workflow sequence:

#### Step 1: Specification (`/sp.specify`)
Create detailed feature specification with:
- User stories and acceptance criteria
- Functional requirements
- Data models and relationships
- API contracts and endpoints
- UI components and pages
- Non-functional requirements
- Edge cases and error handling

Output: `specs/<feature-id>-<feature-name>/spec.md`

#### Step 2: Planning (`/sp.plan`)
Generate implementation plan based on specification:
- Tech stack decisions and architecture
- File structure and organization
- Dependencies and integrations
- Database migrations
- API endpoint implementation order
- Testing strategy
- Risk assessment and mitigation

Output: `specs/<feature-id>-<feature-name>/plan.md`

#### Step 3: Task Generation (`/sp.tasks`)
Break plan into actionable tasks:
- Setup tasks (dependencies, config, env)
- Test tasks (TDD approach, write tests first)
- Core implementation tasks
- Integration tasks (database, auth, middleware)
- Polish tasks (documentation, optimization)
- Task dependencies and execution order
- Parallel vs sequential task markers

Output: `specs/<feature-id>-<feature-name>/tasks.md`

#### Step 4: Implementation (`/sp.implement`)
Execute task list using agents and skills:
- Follow task order and dependencies
- Use TDD: write tests before implementation
- Generate code via agents (no manual coding)
- Mark tasks complete as they're done
- Validate each phase before proceeding

Output: Working code with tests

#### Step 5: Validation and Commit
- Run all tests (must pass with 100% coverage)
- Verify type checking (mypy for Python, TypeScript strict)
- Lint code (follow style guides)
- Create atomic commit with "Co-authored-by: Claude" attribution
- Update documentation if needed

### Referencing Specs in Claude Code
```bash
# Implement a specific feature
@specs/features/task-crud.md implement the create task feature

# Implement specific API endpoint
@specs/api/rest-endpoints.md implement the GET /api/users/{user_id}/tasks endpoint

# Update database schema
@specs/database/schema.md add due_date field to tasks table

# Full feature across stack
@specs/features/authentication.md implement Better Auth login with JWT
```

### Workflow Rules
- **Never skip steps** - Each step builds on the previous
- **No manual coding** - All code generated via agents/skills
- **Tests first** - Follow TDD approach
- **Atomic commits** - One feature/fix per commit
- **100% coverage** - All new code must have tests
- **Type safety** - No `any` types, complete type hints
- **Documentation** - Update docs with code changes

## Phase IV: Local Kubernetes Deployment (Minikube, Helm Charts, kubectl-ai, Kagent, Docker Desktop, Gordon)

### Objective
Deploy the Phase III Todo Chatbot on a local Kubernetes cluster using Minikube and Helm Charts.

### Development Approach (Phase IV)
Use the Agentic Dev Stack workflow: Write spec → Generate plan → Break into tasks → Implement via Claude Code.
No manual coding allowed.

### Phase IV Requirements
- Containerize frontend and backend applications (prefer Docker Desktop)
- Use Docker AI Agent (Gordon) for AI-assisted Docker operations when available
- Create Helm charts for deployment (kubectl-ai and/or kagent can help generate)
- Use kubectl-ai and kagent for AI-assisted Kubernetes operations
- Deploy on Minikube locally

### AIOps Commands (examples)
**Docker AI (Gordon):**
- `docker ai "What can you do?"`

**kubectl-ai examples:**
- `kubectl-ai "deploy the todo frontend with 2 replicas"`
- `kubectl-ai "scale the backend to handle more load"`
- `kubectl-ai "check why the pods are failing"`

**kagent examples:**
- `kagent "analyze the cluster health"`
- `kagent "optimize resource allocation"`

### Notes
- If Docker AI (Gordon) is unavailable in your region/tier, use standard Docker CLI commands.
- Phase IV is deployment-focused; application functionality is the Phase III Todo Chatbot.

## Governance

This constitution is immutable and supersedes all other development practices for this project. Any changes to these principles require an Architectural Decision Record (ADR) with proper justification and approval. All pull requests and code reviews must verify compliance with these principles. Development teams must follow Spec-Kit-Plus guidance for runtime development and maintain consistency with these core principles.

### Success Criteria for Phase II Completion
Phase II is complete when ALL of the following are verified:

✅ **Features**
- All 5 basic level features implemented and tested
- All 4 intermediate features implemented and tested
- Responsive frontend interface works on mobile, tablet, desktop

✅ **API Endpoints**
- All 3 authentication endpoints functional
- All 6 task CRUD endpoints functional
- All 2 user management endpoints functional
- JWT authentication enforced on all protected endpoints

✅ **Database**
- Neon PostgreSQL connected and operational
- All tables created with proper indexes
- User isolation verified (no cross-user access)
- Data persistence confirmed

✅ **Authentication**
- Better Auth configured with JWT plugin
- Signup/login working on frontend
- JWT tokens issued and verified
- User sessions managed properly

✅ **Testing**
- Backend: 100% code coverage with Pytest
- Frontend: 100% coverage for critical components with Jest/Vitest
- Integration tests for all API endpoints
- User isolation tests passing

✅ **Type Safety**
- TypeScript strict mode enabled and passing
- Python mypy checks passing
- No `any` types in codebase

✅ **Performance**
- API responses < 200ms (95th percentile)
- Database queries optimized with indexes
- Frontend loads fast with optimized bundles

✅ **Documentation**
- All agents and skills documented
- README updated with setup instructions
- API documentation complete
- Environment variable guide provided

---

## Phase III: AI Chatbot with MCP Server

### Objective
Create an AI-powered chatbot interface for managing todos through natural language using MCP (Model Context Protocol) server architecture. The chatbot enables users to interact with their tasks using conversational commands instead of traditional UI.

**Development Approach**: Use the Agentic Dev Stack workflow: Write spec → Generate plan → Break into tasks → Implement via Claude Code. No manual coding allowed.

### Phase III Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Frontend | OpenAI ChatKit | Conversational UI interface |
| Backend | Python FastAPI | API server and orchestration |
| AI Framework | OpenAI Agents SDK | AI logic and reasoning |
| MCP Server | Official MCP SDK | Exposes task operations as tools |
| ORM | SQLModel | Database operations |
| Database | Neon Serverless PostgreSQL | Persistent storage |
| Authentication | Better Auth | User authentication (JWT) |

### Architecture Overview
```
┌─────────────────┐     ┌──────────────────────────────────────────────┐     ┌─────────────────┐
│                 │     │              FastAPI Server                   │     │                 │
│                 │     │  ┌────────────────────────────────────────┐  │     │                 │
│  ChatKit UI     │────▶│  │         Chat Endpoint                  │  │     │    Neon DB      │
│  (Frontend)     │     │  │  POST /api/{user_id}/chat              │  │     │  (PostgreSQL)   │
│                 │     │  └───────────────┬────────────────────────┘  │     │                 │
│                 │     │                  │                           │     │  - tasks        │
│                 │     │                  ▼                           │     │  - users        │
│                 │     │  ┌────────────────────────────────────────┐  │     │  - conversations│
│                 │◀────│  │      OpenAI Agents SDK                 │  │     │  - messages     │
│                 │     │  │      (Agent + Runner)                  │  │     │                 │
│                 │     │  └───────────────┬────────────────────────┘  │     │                 │
│                 │     │                  │                           │     │                 │
│                 │     │                  ▼                           │     │                 │
│                 │     │  ┌────────────────────────────────────────┐  │────▶│                 │
│                 │     │  │         MCP Server                     │  │     │                 │
│                 │     │  │  (MCP Tools for Task Operations)       │  │◀────│                 │
│                 │     │  └────────────────────────────────────────┘  │     │                 │
└─────────────────┘     └──────────────────────────────────────────────┘     └─────────────────┘
```

### Database Models (Phase III Additions)

#### Conversations Table
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
```

#### Messages Table
```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_user_id ON messages(user_id);
```

### Chat API Endpoint

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/{user_id}/chat | Send message & get AI response |

#### Request
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| conversation_id | integer | No | Existing conversation ID (creates new if not provided) |
| message | string | Yes | User's natural language message |

#### Response
| Field | Type | Description |
|-------|------|-------------|
| conversation_id | integer | The conversation ID |
| response | string | AI assistant's response |
| tool_calls | array | List of MCP tools invoked |

### MCP Tools Specification

The MCP server must expose the following tools for the AI agent:

#### Tool: add_task
| Attribute | Value |
|-----------|-------|
| Purpose | Create a new task |
| Parameters | `user_id` (string, required), `title` (string, required), `description` (string, optional) |
| Returns | `task_id`, `status`, `title` |
| Example Input | `{"user_id": "ziakhan", "title": "Buy groceries", "description": "Milk, eggs, bread"}` |
| Example Output | `{"task_id": 5, "status": "created", "title": "Buy groceries"}` |

#### Tool: list_tasks
| Attribute | Value |
|-----------|-------|
| Purpose | Retrieve tasks from the list |
| Parameters | `user_id` (string, required), `status` (string, optional: "all", "pending", "completed") |
| Returns | Array of task objects |
| Example Input | `{"user_id": "ziakhan", "status": "pending"}` |
| Example Output | `[{"id": 1, "title": "Buy groceries", "completed": false}, ...]` |

#### Tool: complete_task
| Attribute | Value |
|-----------|-------|
| Purpose | Mark a task as complete |
| Parameters | `user_id` (string, required), `task_id` (integer, required) |
| Returns | `task_id`, `status`, `title` |
| Example Input | `{"user_id": "ziakhan", "task_id": 3}` |
| Example Output | `{"task_id": 3, "status": "completed", "title": "Call mom"}` |

#### Tool: delete_task
| Attribute | Value |
|-----------|-------|
| Purpose | Remove a task from the list |
| Parameters | `user_id` (string, required), `task_id` (integer, required) |
| Returns | `task_id`, `status`, `title` |
| Example Input | `{"user_id": "ziakhan", "task_id": 2}` |
| Example Output | `{"task_id": 2, "status": "deleted", "title": "Old task"}` |

#### Tool: update_task
| Attribute | Value |
|-----------|-------|
| Purpose | Modify task title or description |
| Parameters | `user_id` (string, required), `task_id` (integer, required), `title` (string, optional), `description` (string, optional) |
| Returns | `task_id`, `status`, `title` |
| Example Input | `{"user_id": "ziakhan", "task_id": 1, "title": "Buy groceries and fruits"}` |
| Example Output | `{"task_id": 1, "status": "updated", "title": "Buy groceries and fruits"}` |

### Agent Behavior Specification

| Behavior | Description |
|----------|-------------|
| Task Creation | When user mentions adding/creating/remembering something, use `add_task` |
| Task Listing | When user asks to see/show/list tasks, use `list_tasks` with appropriate filter |
| Task Completion | When user says done/complete/finished, use `complete_task` |
| Task Deletion | When user says delete/remove/cancel, use `delete_task` |
| Task Update | When user says change/update/rename, use `update_task` |
| Confirmation | Always confirm actions with friendly response |
| Error Handling | Gracefully handle task not found and other errors |

### Conversation Flow (Stateless Request Cycle)

The server MUST follow this stateless flow for each request:

1. **Receive** user message via POST /api/{user_id}/chat
2. **Fetch** conversation history from database (if conversation_id provided)
3. **Build** message array for agent (history + new message)
4. **Store** user message in database
5. **Run** agent with MCP tools
6. **Agent invokes** appropriate MCP tool(s)
7. **Store** assistant response in database
8. **Return** response to client
9. **Server holds NO state** (ready for next request)

### Natural Language Commands

The chatbot should understand and respond to:

| User Says | Agent Should |
|-----------|--------------|
| "Add a task to buy groceries" | Call `add_task` with title "Buy groceries" |
| "Show me all my tasks" | Call `list_tasks` with status "all" |
| "What's pending?" | Call `list_tasks` with status "pending" |
| "Mark task 3 as complete" | Call `complete_task` with task_id 3 |
| "Delete the meeting task" | Call `list_tasks` first, then `delete_task` |
| "Change task 1 to 'Call mom tonight'" | Call `update_task` with new title |
| "I need to remember to pay bills" | Call `add_task` with title "Pay bills" |
| "What have I completed?" | Call `list_tasks` with status "completed" |

### OpenAI ChatKit Setup & Deployment

#### Domain Allowlist Configuration (Required for Hosted ChatKit)

Before deploying your chatbot frontend, you must configure OpenAI's domain allowlist for security:

1. **Deploy your frontend first** to get a production URL:
   - Vercel: `https://your-app.vercel.app`
   - GitHub Pages: `https://username.github.io/repo-name`
   - Custom domain: `https://yourdomain.com`

2. **Add your domain to OpenAI's allowlist**:
   - Navigate to: https://platform.openai.com/settings/organization/security/domain-allowlist
   - Click "Add domain"
   - Enter your frontend URL (without trailing slash)
   - Save changes

3. **Get your ChatKit domain key**:
   - After adding the domain, OpenAI will provide a domain key
   - Pass this key to your ChatKit configuration

#### Phase III Environment Variables (Additional)
```bash
# OpenAI (Phase III)
OPENAI_API_KEY=your-openai-api-key
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key-here

# MCP Server
MCP_SERVER_URL=http://localhost:8000/mcp
```

**Note**: The hosted ChatKit option only works after adding the correct domains under Security → Domain Allowlist. Local development (`localhost`) typically works without this configuration.

### Key Architecture Benefits

| Aspect | Benefit |
|--------|---------|
| MCP Tools | Standardized interface for AI to interact with your app |
| Single Endpoint | Simpler API — AI handles routing to tools |
| Stateless Server | Scalable, resilient, horizontally scalable |
| Tool Composition | Agent can chain multiple tools in one turn |

### Key Stateless Architecture Benefits

| Benefit | Description |
|---------|-------------|
| Scalability | Any server instance can handle any request |
| Resilience | Server restarts don't lose conversation state |
| Horizontal scaling | Load balancer can route to any backend |
| Testability | Each request is independent and reproducible |

### Phase III Deliverables

GitHub repository with:
- `/frontend` – ChatKit-based UI
- `/backend` – FastAPI + Agents SDK + MCP
- `/specs` – Specification files for agent and MCP tools
- Database migration scripts
- README with setup instructions

Working chatbot that can:
- Manage tasks through natural language via MCP tools
- Maintain conversation context via database (stateless server)
- Provide helpful responses with action confirmations
- Handle errors gracefully
- Resume conversations after server restart

### Success Criteria for Phase III Completion

Phase III is complete when ALL of the following are verified:

✅ **AI Chatbot**
- Conversational interface implemented with OpenAI ChatKit
- Natural language understanding for all task operations
- Friendly confirmations and error messages
- Context maintained across conversation turns

✅ **MCP Server**
- All 5 MCP tools implemented (`add_task`, `list_tasks`, `complete_task`, `delete_task`, `update_task`)
- Tools are stateless and store state in database
- Proper error handling for all edge cases
- User isolation enforced on all tool operations

✅ **OpenAI Agents SDK Integration**
- Agent correctly interprets user intent
- Agent selects appropriate tool(s) for each request
- Tool chaining works (e.g., list then delete)
- Graceful handling of ambiguous requests

✅ **Database**
- Conversations table created and operational
- Messages table created and operational
- Conversation history persisted and retrievable
- All indexes created for performance

✅ **Stateless Architecture**
- Server holds no state between requests
- Conversation can resume after server restart
- Multiple server instances can handle same conversation
- Request/response cycle is independent and reproducible

✅ **Testing**
- Unit tests for all MCP tools
- Integration tests for chat endpoint
- End-to-end tests for conversation flows
- User isolation tests for chatbot operations

✅ **Deployment**
- ChatKit domain allowlist configured
- OpenAI API key securely stored
- Production environment variables set
- Frontend and backend deployed and communicating

---

**Version**: 3.1.0 | **Ratified**: 2025-12-12 | **Last Amended**: 2026-01-06
