# Implementation Plan: ChatKit Frontend-Backend Integration

**Branch**: `017-chatkit-integration` | **Date**: 2026-01-01 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/017-chatkit-integration/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Integrate the existing ChatKit React frontend with the AI backend to enable actual intelligent conversations. This involves connecting the ChatKit frontend components to the backend AI services, implementing proper session management with JWT authentication, and establishing client effect handlers for real-time UI synchronization when tasks are modified through chat operations.

## Technical Context

**Language/Version**: TypeScript/JavaScript for frontend, Python 3.11 for backend
**Primary Dependencies**: @openai/chatkit-react, Next.js 16+, FastAPI, SQLModel, Neon PostgreSQL, Better Auth
**Storage**: Neon PostgreSQL database for thread persistence and task operations
**Testing**: Pytest for backend, Jest/Vitest for frontend
**Target Platform**: Web application (frontend + backend)
**Performance Goals**: AI responses within 5 seconds (95% of messages), UI updates within 1 second
**Constraints**: <200ms loading state feedback, JWT authentication, secure API communication
**Scale/Scope**: Multi-user task management system with AI integration

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Clean code (SRP, docstrings) - ✅
- Type safety (no 'any') - ✅
- Accessibility (WCAG 2.1 AA) - ✅
- Performance (O(1)/O(n)) - ✅
- Modular architecture - ✅
- NFRs (reliable, secure, maintainable) - ✅

## Project Structure

### Documentation (this feature)

```text
specs/017-chatkit-integration/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/
```

**Structure Decision**: Web application with separate frontend and backend directories following the existing project architecture. The ChatKit integration spans both frontend components and backend API endpoints.

## Phase 0: Research & Analysis

### Research Findings

**Decision**: Use existing ChatKit React components with backend integration
**Rationale**: Leverages existing UI investment while connecting to actual AI backend services
**Alternatives considered**: Complete rewrite of chat interface, using different chat SDK

**Decision**: Implement session management via JWT authentication
**Rationale**: Consistent with existing authentication system, secure token passing
**Alternatives considered**: Session cookies, OAuth tokens

**Decision**: Use Server-Sent Events (SSE) for streaming AI responses
**Rationale**: Efficient for one-way streaming from server to client, low latency
**Alternatives considered**: WebSockets, long polling

## Phase 1: Data Model Design

### Key Entities

1. **ChatSession** - Represents authenticated chat session with client secret
   - id (UUID, primary key)
   - user_id (UUID, foreign key to users)
   - client_secret_hash (string, hashed for security)
   - expires_at (datetime)
   - created_at (datetime)

2. **ChatThread** - Represents conversation thread metadata
   - id (string, primary key from ChatKit)
   - user_id (UUID, foreign key to users)
   - name (string, display name)
   - last_message_preview (string, nullable)
   - message_count (int)
   - created_at (datetime)
   - updated_at (datetime)

3. **ChatMessage** - Represents individual chat messages
   - id (UUID, primary key)
   - thread_id (string, foreign key to chat_threads)
   - role (string, 'user' or 'assistant')
   - content (text)
   - created_at (datetime)

4. **ClientEffectEvent** - Represents events for UI synchronization
   - id (UUID, primary key)
   - thread_id (string, foreign key to chat_threads)
   - event_type (string, task_created, task_updated, etc.)
   - event_data (JSON, nullable)
   - created_at (datetime)

## Phase 1: API Contracts

### Backend Endpoints

1. **POST /api/chatkit/session** - Create authenticated chat session
   - Input: JWT token in Authorization header
   - Output: {client_secret: string, expires_at: string}
   - Auth: JWT required

2. **GET /api/users/{user_id}/chatkit/threads** - List user's chat threads
   - Input: user_id (UUID), JWT token
   - Output: {threads: Thread[], total: number}
   - Auth: JWT required, user isolation

3. **POST /api/users/{user_id}/chatkit/threads/{thread_id}/sync** - Sync thread metadata
   - Input: thread metadata in request body
   - Output: Thread metadata
   - Auth: JWT required, user isolation

4. **POST /api/chatkit** - Send message and receive streaming response
   - Input: {thread_id: string, message: string}
   - Output: Server-sent events stream
   - Auth: JWT required

### Frontend Components

1. **ChatInterface** - Main chat component using @openai/chatkit-react
   - Session management via getClientSecret
   - Message handling and streaming
   - Composer tools configuration
   - Loading states and animations

2. **Chat Page** - Full chat interface with sidebar
   - Thread history management
   - Navigation with Navbar and Footer
   - Responsive layout

## Phase 1: Quickstart Guide

### Prerequisites
- Node.js 18+ for frontend
- Python 3.11+ for backend
- Neon PostgreSQL database
- OpenAI API key

### Setup Commands
```bash
# Backend setup
cd backend
uv venv
source .venv/bin/activate  # or appropriate activation command
uv pip install -r requirements.txt
cp .env.example .env
# Set OPENAI_API_KEY in .env

# Frontend setup
cd frontend
npm install
cp .env.example .env
# Set NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Running Locally
```bash
# Terminal 1: Backend
cd backend
uv run python -m uvicorn main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

### Key Integration Points
1. Frontend calls `/api/chatkit/session` for authentication
2. ChatKit uses streaming responses from `/api/chatkit`
3. Thread metadata syncs via `/api/users/{user_id}/chatkit/threads`
4. Client effect events trigger UI updates

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| | | |

## Architecture Decision Record (ADR)

### ADR-001: ChatKit React SDK Integration
**Context**: Need to integrate AI chat functionality with existing task management system
**Decision**: Use @openai/chatkit-react for frontend with custom backend integration
**Status**: Accepted
**Consequences**: Leverages existing UI components while requiring custom backend integration

### ADR-002: Server-Sent Events for Streaming
**Context**: Need to stream AI responses from backend to frontend
**Decision**: Use Server-Sent Events instead of WebSockets
**Status**: Accepted
**Consequences**: Simpler implementation, HTTP-based, good for one-way streaming

### ADR-003: JWT Authentication Integration
**Context**: Need to authenticate ChatKit sessions with existing auth system
**Decision**: Use existing JWT tokens to create ChatKit session secrets
**Status**: Accepted
**Consequences**: Consistent auth flow, secure token passing, user isolation

## Risk Analysis

### High-Risk Areas
1. **Authentication Integration** - JWT token handling between systems
2. **AI Response Latency** - Performance with external AI services
3. **Data Consistency** - Thread persistence and task synchronization

### Mitigation Strategies
1. Comprehensive error handling and fallback mechanisms
2. Loading indicators and optimistic UI updates
3. Thorough testing of user isolation and security

## Dependencies

### External Dependencies
- @openai/chatkit-react: Frontend chat component library
- OpenAI API: AI response generation
- Neon PostgreSQL: Database storage
- Better Auth: User authentication

### Internal Dependencies
- Existing task management API
- User authentication system
- Database models and schemas

## Success Criteria

- 95% of AI responses delivered within 5 seconds
- 100% of task operations synchronized automatically
- 90% user success rate with contextual tools
- Zero authentication bypass vulnerabilities
- Responsive UI with <200ms feedback