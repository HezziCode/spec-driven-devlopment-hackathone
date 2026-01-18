# Implementation Plan: ChatKit UI

**Branch**: `015-chatkit-ui` | **Date**: 2025-12-31 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/015-chatkit-ui/spec.md`

**Note**: This implementation plan follows the `/sp.plan` command workflow with Phase 0 research and Phase 1 design completed.

## Summary

Implementation of an AI-powered chat interface using @openai/chatkit-react for natural language task management. The feature enables users to interact with their TaskWave tasks through conversational AI, with support for multi-thread conversations, tool-based actions (create, search, view tasks), and persistent thread storage. Integration with existing Better Auth (JWT), OpenAI Agents SDK, and MCP Server infrastructure from Phase 3.

**Key Deliverables**:
- ChatKit React component with session management
- Backend API for ChatKit sessions and thread persistence
- Multi-thread chat with localStorage + database persistence
- Composer tool menu for task operations
- Event-driven loading states and error handling
- TaskWave-themed UI with Tailwind CSS

---

## Technical Context

**Language/Version**: TypeScript 5.3+ (frontend), Python 3.11+ (backend)

**Primary Dependencies**:
- **Frontend**: @openai/chatkit-react (latest), Next.js 16+ (App Router), React 19+, Tailwind CSS
- **Backend**: OpenAI Python SDK (latest), FastAPI, SQLModel, Better Auth JWT

**Storage**:
- **Local**: Browser localStorage for immediate thread access
- **Persistent**: Neon PostgreSQL for long-term thread metadata storage
- **Chat History**: Managed by OpenAI ChatKit backend (not stored in our database)

**Testing**: Jest/Vitest (frontend), Pytest (backend)

**Target Platform**: Web application (responsive design for mobile, tablet, desktop)

**Project Type**: Full-stack web (frontend + backend integration)

**Performance Goals**:
- Session initialization: < 2 seconds on 3G
- Message send/receive: < 500ms
- Thread switching: < 1 second with history load
- AI response start: < 1 second after message sent
- Composer interaction: < 100ms
- Smooth 60fps UI during response streaming

**Constraints**:
- Must use Better Auth JWT for session authentication
- Chat messages stored by ChatKit, NOT in our database
- Thread metadata only stored in our database for persistence
- Must integrate with existing MCP Server task tools
- Must match TaskWave theme (teal-cyan gradients, wave animations)
- Accessibility (WCAG 2.1 AA) required

**Scale/Scope**:
- Multi-user support via JWT user isolation
- Support up to 100 threads per user
- Handle conversations with 500+ messages per thread
- Concurrent chat sessions across multiple devices

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Initial Check (Pre-Research)
- ✅ **Modularity**: Component-based architecture with clear separation (UI, API client, backend services)
- ✅ **Type Safety**: Strict TypeScript (no `any`), Python type hints throughout
- ✅ **Accessibility**: ChatKit provides built-in a11y, additional ARIA labels for custom UI
- ✅ **Performance**: ChatKit handles WebSocket optimization, thread list pagination, localStorage caching
- ✅ **Security**: JWT authentication, user isolation on all endpoints, client secret hashing
- ✅ **Maintainability**: Clear documentation, reusable patterns, agent/skill integration
- ✅ **Stateless Architecture (Phase III Principle)**: Backend holds NO state; all thread data persisted to database

### Post-Design Check (After Phase 1)
- ✅ **Modularity**: Confirmed via data models (ChatInterface, API client, backend routes separate)
- ✅ **Type Safety**: All TypeScript interfaces defined, Pydantic schemas for backend
- ✅ **Accessibility**: ChatKit native accessibility + custom loading states with screen reader support
- ✅ **Performance**: Event handlers prevent unnecessary re-renders, thread sync debounced
- ✅ **Security**: Client secret generation with expiry, JWT validation middleware reused
- ✅ **Maintainability**: Quickstart guide created, API contracts documented (OpenAPI spec)
- ✅ **Stateless**: Thread metadata synced to DB, session state in DB, no in-memory state

**GATE PASSED**: All constitution principles satisfied. No violations requiring justification.

---

## Project Structure

### Documentation (this feature)

```text
specs/015-chatkit-ui/
├── spec.md                  # Feature specification (/sp.specify output)
├── plan.md                  # This file (/sp.plan output)
├── research.md              # Phase 0 research findings (/sp.plan Phase 0)
├── data-model.md            # Phase 1 data models (/sp.plan Phase 1)
├── quickstart.md            # Phase 1 implementation guide (/sp.plan Phase 1)
├── contracts/               # Phase 1 API contracts (/sp.plan Phase 1)
│   └── chatkit-api.yaml     # OpenAPI 3.1 specification
├── checklists/              # Quality validation
│   └── requirements.md      # Spec quality checklist (from /sp.specify)
└── tasks.md                 # Implementation tasks (NOT YET CREATED - use /sp.tasks)
```

### Source Code (repository root)

#### Frontend Structure

```text
frontend/
├── app/
│   └── chat/
│       └── page.tsx         # Chat page route
├── components/
│   ├── ChatInterface.tsx    # Main ChatKit component (Client Component)
│   ├── ThreadSidebar.tsx    # Thread list sidebar (optional enhancement)
│   └── ChatLoadingState.tsx # Loading skeleton for chat
├── lib/
│   ├── chatkit-api.ts       # ChatKit API client functions
│   └── auth.ts              # Existing auth utilities (reuse getAuthToken)
├── types/
│   └── chatkit.ts           # TypeScript interfaces for ChatKit
└── styles/
    └── globals.css          # TaskWave theme (already configured)
```

#### Backend Structure

```text
backend/
├── models.py                # Add: ChatKitSession, ChatThread models
├── schemas/
│   └── chatkit.py           # NEW: Pydantic schemas for ChatKit endpoints
├── routes/
│   └── chatkit.py           # NEW: ChatKit session and thread endpoints
├── services/
│   └── chatkit_service.py   # NEW: Business logic for session/thread management
├── middleware/
│   └── auth_middleware.py   # EXISTING: Reuse get_user_id_from_token
└── tests/
    ├── test_chatkit.py      # NEW: Unit tests for ChatKit endpoints
    └── fixtures/            # Shared test fixtures (reuse existing)
```

**Structure Decision**: Selected full-stack structure with frontend Client Components for ChatKit (requires 'use client' due to WebSocket usage) and backend FastAPI routes following existing pattern. Data models extend existing User model with ChatKitSession and ChatThread for persistence. Integration leverages existing JWT middleware and MCP Server tools.

---

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| - | - | - |

**No violations identified.** All requirements align with constitution principles.

---

## Phase 0: Research Summary

**Status**: ✅ Completed

**Key Decisions**:

1. **ChatKit Library Integration**: Use @openai/chatkit-react npm package with useChatKit hook
   - **Rationale**: Official library, React 19 compatible, built-in WebSocket handling
   - **Alternative Rejected**: Custom WebSocket implementation (too complex, reinvents wheel)

2. **Session Management**: Implement getClientSecret that exchanges JWT for ChatKit session token
   - **Rationale**: Maintains existing auth model, secure token exchange
   - **Alternative Rejected**: Public API keys (security risk), cookie-based (incompatible with ChatKit)

3. **Thread Persistence**: Hybrid localStorage (immediate) + backend DB (long-term)
   - **Rationale**: Balances performance (instant switching) with reliability (cross-device)
   - **Alternative Rejected**: Backend-only (latency), localStorage-only (data loss risk)

4. **Composer Tools**: Use ChatKit's native composer.tools configuration
   - **Rationale**: Visual discovery, native UI, consistent UX
   - **Alternative Rejected**: Custom button toolbar (duplicates UI), slash commands only (less discoverable)

5. **Event Handlers**: Implement all ChatKit events (onReady, onError, onThreadChange, onResponseStart/End)
   - **Rationale**: Comprehensive state management, proper loading/error states
   - **Alternative Rejected**: Minimal events (lacks feedback), external state library (overkill)

6. **Theme Integration**: Apply Tailwind CSS with TaskWave teal-cyan gradients
   - **Rationale**: Consistency with existing design, utility-first approach
   - **Alternative Rejected**: CSS modules (inconsistent), styled-components (runtime overhead)

**Research Document**: [research.md](research.md)

---

## Phase 1: Design Artifacts

**Status**: ✅ Completed

### Data Models Created

**Frontend (TypeScript)**:
- `ChatSession` - Active session state with client secret and status
- `ChatThread` - Thread metadata for display and persistence
- `ChatMessage` - Individual message structure (managed by ChatKit, type only)
- `ToolCall` - AI tool invocation tracking
- `ComposerTool` - Tool menu configuration
- `ChatUIState` - Global UI state for chat interface

**Backend (SQLModel/Pydantic)**:
- `ChatKitSession` (DB table) - Session tracking with expiry
- `ChatThread` (DB table) - Thread metadata persistence
- `SessionResponse` (Pydantic) - Session creation response
- `ThreadSyncRequest` (Pydantic) - Thread sync request
- `ThreadItem` (Pydantic) - Thread list item
- `ThreadListResponse` (Pydantic) - Thread list response

**Data Model Document**: [data-model.md](data-model.md)

### API Contracts Created

**OpenAPI 3.1 Specification**: [contracts/chatkit-api.yaml](contracts/chatkit-api.yaml)

**Endpoints**:
1. `POST /api/chatkit/session` - Create ChatKit session (returns client_secret)
2. `GET /api/users/{user_id}/chatkit/threads` - List user's threads (with pagination)
3. `POST /api/users/{user_id}/chatkit/threads/{thread_id}/sync` - Sync thread metadata
4. `DELETE /api/users/{user_id}/chatkit/threads/{thread_id}` - Delete thread

**Authentication**: All endpoints require JWT Bearer token (except session creation uses JWT to issue client_secret)

**Error Handling**: Standardized error responses (400, 401, 403, 404, 500) with consistent format

### Quickstart Guide Created

**Implementation Guide**: [quickstart.md](quickstart.md)

**Phases**:
1. Setup & Dependencies (30 min) - Install packages, configure env
2. Backend API Implementation (2-3 hours) - Models, schemas, services, routes
3. Frontend Components (3-4 hours) - Types, API client, ChatInterface, page
4. Integration & Testing (2-3 hours) - Database migrations, manual testing
5. Testing & Polish (1-2 hours) - Unit tests, refinements

**Estimated Total Time**: 8-12 hours for full implementation

---

## Implementation Strategy

### Agents & Skills to Leverage

Based on user request to "use related agent and skills":

#### Primary Agent
- **`chatkit-frontend-builder`** - Autonomous agent for building ChatKit React frontends
  - **Use for**: Creating ChatInterface component, implementing useChatKit hook, configuring composer tools, handling events
  - **Responsibilities**: Frontend component structure, session management, thread UI, event handlers

#### Supporting Agents
- **`frontend-feature-builder`** - For Next.js page and routing setup
- **`backend-api-builder`** - For FastAPI endpoints and database operations

#### Key Skills to Apply

**Frontend Skills**:
1. **`chatkit-react-components`** - ChatKit React patterns
   - Use for: useChatKit hook configuration, composer tools, event handlers, thread management
2. **`frontend-component`** - React component patterns
   - Use for: Component structure, props, TypeScript types
3. **`frontend-api-client`** - API client setup
   - Use for: getClientSecret implementation, thread sync calls
4. **`frontend-types`** - TypeScript type definitions
   - Use for: ChatSession, ChatThread, ChatMessage interfaces

**Backend Skills**:
1. **`fastapi-crud-endpoints`** - RESTful endpoint patterns
   - Use for: ChatKit session and thread CRUD endpoints
2. **`jwt-middleware`** - Authentication middleware
   - Use for: Reusing get_user_id_from_token for JWT validation
3. **`pytest-api-testing`** - API testing patterns
   - Use for: Test suite for ChatKit endpoints

---

## Dependencies and Prerequisites

### External Dependencies

**Frontend (npm)**:
```json
{
  "@openai/chatkit-react": "^latest",
  "react": "^19.0.0",
  "react-dom": "^19.0.0",
  "next": "^16.0.0",
  "tailwindcss": "^latest"
}
```

**Backend (Python/uv)**:
```toml
[dependencies]
openai = "^latest"      # For ChatKit session generation
fastapi = "^0.100.0"    # Already installed
sqlmodel = "^latest"    # Already installed
pydantic = "^2.0.0"     # Already installed
```

### Internal Prerequisites

**Must be completed before implementation**:
- ✅ Better Auth JWT authentication (Phase 2)
- ✅ Backend task CRUD endpoints (Phase 2)
- ✅ OpenAI Agents SDK integration (Phase 3)
- ✅ MCP Server with task tools (Phase 3)
- ✅ TaskWave theme and Tailwind config (Phase 2)

**Environment Variables Required**:
```bash
# Frontend (.env.local)
NEXT_PUBLIC_CHATKIT_ENABLED=true
BETTER_AUTH_SECRET=<shared-secret>

# Backend (.env)
OPENAI_API_KEY=<openai-api-key>
BETTER_AUTH_SECRET=<shared-secret>
DATABASE_URL=<neon-db-url>
```

---

## Risk Assessment and Mitigation

### Technical Risks

| Risk | Impact | Probability | Mitigation Strategy |
|------|--------|-------------|---------------------|
| ChatKit library breaking changes | High | Low | Pin version in package.json, monitor release notes |
| Session expiry during conversation | Medium | Medium | Implement auto-refresh in getClientSecret with token check |
| localStorage cleared by user | Low | Medium | Periodic sync to backend, fetch threads on app load |
| WebSocket connection failures | High | Low | ChatKit handles reconnection automatically, show error UI |
| Thread sync conflicts (race conditions) | Medium | Low | Optimistic updates, debounce sync calls (500ms) |
| OpenAI API rate limiting | Medium | Low | Implement backend rate limiting, show user feedback |

### Performance Risks

| Risk | Impact | Probability | Mitigation Strategy |
|------|--------|-------------|---------------------|
| Large thread list slow rendering | Medium | Medium | Implement pagination (50 threads per page), virtualization |
| Many concurrent users strain backend | High | Low | Rate limit ChatKit endpoints (10 req/min per user) |
| localStorage quota exceeded | Low | Low | Limit cached threads to 100, cleanup old threads |
| Slow AI response times | Medium | Medium | Show loading state immediately, stream responses |

### Integration Risks

| Risk | Impact | Probability | Mitigation Strategy |
|------|--------|-------------|---------------------|
| MCP tools not responding | High | Low | Timeout after 10s, show error to user, allow retry |
| JWT token invalid/expired | High | Medium | Refresh token automatically, redirect to login if refresh fails |
| Backend API changes break frontend | Medium | Low | Use TypeScript for compile-time type checking, E2E tests |

---

## Testing Strategy

### Unit Tests (Pytest - Backend)

**File**: `backend/tests/test_chatkit.py`

**Test Coverage**:
- ✅ Session creation endpoint (valid JWT → client_secret)
- ✅ Session creation with invalid JWT (401 error)
- ✅ Thread list endpoint (returns user's threads only)
- ✅ Thread sync endpoint (creates new thread)
- ✅ Thread sync endpoint (updates existing thread)
- ✅ Thread delete endpoint (deletes thread)
- ✅ User isolation (user A cannot access user B's threads)

**Target Coverage**: 100% for ChatKit endpoints

### Integration Tests (Frontend)

**File**: `frontend/__tests__/ChatInterface.test.tsx`

**Test Coverage**:
- ✅ ChatInterface renders loading state initially
- ✅ ChatInterface renders chat UI after session ready
- ✅ Error state shown on session failure
- ✅ Composer tools menu appears with correct tools
- ✅ Thread switching updates currentThread state
- ✅ localStorage updates on thread change

**Target Coverage**: 90% for critical UI flows

### End-to-End Tests

**Manual Testing Checklist** (from quickstart.md):
- [ ] Navigate to /chat page
- [ ] Verify chat interface loads without errors
- [ ] Send test message: "Hello"
- [ ] Verify AI responds
- [ ] Use "Create Task" tool from composer
- [ ] Send message: "Add a task to buy groceries"
- [ ] Verify task created (check /tasks page)
- [ ] Create new thread
- [ ] Switch between threads
- [ ] Reload page, verify last thread restored

**Automated E2E** (Optional, future enhancement):
- Playwright tests for full user flow
- Test task creation via chat → verify in task list
- Test thread persistence across page reloads

---

## Implementation Phases

### Phase 2A: Backend Implementation (First)

**Tasks**:
1. Add ChatKitSession and ChatThread models to `backend/models.py`
2. Create Pydantic schemas in `backend/schemas/chatkit.py`
3. Implement chatkit_service.py business logic
4. Create API routes in `backend/routes/chatkit.py`
5. Register routes in `backend/main.py`
6. Run database migrations (Alembic)
7. Write unit tests in `backend/tests/test_chatkit.py`

**Agent to Use**: `backend-api-builder`
**Skills to Apply**: `fastapi-crud-endpoints`, `jwt-middleware`, `pytest-api-testing`

**Validation**: All backend tests pass, OpenAPI docs show new endpoints

---

### Phase 2B: Frontend Implementation (Second)

**Tasks**:
1. Install @openai/chatkit-react package
2. Create TypeScript types in `frontend/types/chatkit.ts`
3. Implement API client functions in `frontend/lib/chatkit-api.ts`
4. Build ChatInterface component in `frontend/components/ChatInterface.tsx`
5. Create /chat page in `frontend/app/chat/page.tsx`
6. Add navigation link to chat page in navbar

**Agent to Use**: `chatkit-frontend-builder` (PRIMARY)
**Skills to Apply**: `chatkit-react-components`, `frontend-component`, `frontend-api-client`, `frontend-types`

**Validation**: Chat interface renders, session establishes, message sending works

---

### Phase 2C: Integration & Polish (Third)

**Tasks**:
1. Test end-to-end flow (login → chat → create task)
2. Verify thread persistence (create thread → reload → thread restored)
3. Test error scenarios (invalid JWT, network failure)
4. Apply TaskWave theme styling (teal-cyan gradients)
5. Add loading states and error boundaries
6. Write frontend integration tests
7. Update README with ChatKit feature documentation

**Agent to Use**: `frontend-feature-builder`
**Skills to Apply**: `page-animation` (for loading states), `frontend-component` (for error boundaries)

**Validation**: All manual tests pass, theme consistent with TaskWave

---

## Success Criteria Validation

Based on specification success criteria (SC-001 to SC-010):

| Success Criterion | Validation Method | Target |
|-------------------|-------------------|--------|
| SC-001: Session initialization | Manual test + performance monitoring | < 2 seconds |
| SC-002: Message success rate | Integration test + analytics | 95% success |
| SC-003: Thread switching | Manual test + timer | < 1 second |
| SC-004: Thread persistence | E2E test (reload page) | 100% retention |
| SC-005: Loading states | Manual test | < 200ms to show |
| SC-006: UI performance | Chrome DevTools FPS monitor | 60fps during streaming |
| SC-007: Tool menu usage | Manual test + analytics | 90% find tools |
| SC-008: Theme consistency | Visual review | 95% brand match |
| SC-009: Error recovery | Manual test (disconnect network) | No context loss |
| SC-010: Responsive design | Manual test (mobile/tablet/desktop) | Works on all devices |

---

## Post-Implementation Tasks

**After core implementation complete**:

1. **Documentation**:
   - [ ] Update main README with ChatKit feature section
   - [ ] Create video demo of chat interface
   - [ ] Document environment variable setup

2. **Monitoring**:
   - [ ] Add logging for ChatKit session creation
   - [ ] Track thread creation/deletion metrics
   - [ ] Monitor ChatKit API usage and costs

3. **Enhancements** (Future):
   - [ ] Thread search and filtering in sidebar
   - [ ] Thread renaming functionality
   - [ ] Export conversation history
   - [ ] Voice input integration (Phase 3 bonus)
   - [ ] Mobile app support (React Native)

---

## Next Steps

**Implementation Ready**: Phase 0 research and Phase 1 design complete.

**To Begin Implementation**:
1. Run `/sp.tasks` to generate detailed task breakdown from this plan
2. Use `/sp.implement` to execute tasks with agents (backend-api-builder, chatkit-frontend-builder)
3. Follow quickstart.md for step-by-step implementation guidance

**Estimated Implementation Time**: 8-12 hours total
- Backend: 2-3 hours
- Frontend: 3-4 hours
- Integration & Testing: 3-5 hours

---

## Related Documentation

- **Specification**: [spec.md](spec.md) - Feature requirements and user stories
- **Research**: [research.md](research.md) - Technical decisions and rationale
- **Data Models**: [data-model.md](data-model.md) - Database and TypeScript models
- **API Contracts**: [contracts/chatkit-api.yaml](contracts/chatkit-api.yaml) - OpenAPI specification
- **Quickstart**: [quickstart.md](quickstart.md) - Implementation guide
- **Constitution**: [.specify/memory/constitution.md](../../.specify/memory/constitution.md) - Project principles

**Agents**:
- [chatkit-frontend-builder](.claude/agents/chatkit-frontend-builder.md) - PRIMARY agent for frontend
- [backend-api-builder](.claude/agents/backend-api-builder.md) - For backend endpoints

**Skills**:
- [chatkit-react-components](.claude/skills/chatkit-react-components/SKILL.md) - ChatKit patterns
- [fastapi-crud-endpoints](.claude/skills/fastapi-crud-endpoints/SKILL.md) - Backend patterns
- [frontend-component](.claude/skills/frontend-component/SKILL.md) - React patterns

---

**Plan Version**: 1.0.0
**Plan Created**: 2025-12-31
**Last Updated**: 2025-12-31
**Plan Status**: ✅ Complete - Ready for /sp.tasks
**Reviewed By**: AI Architect
**Approved for Implementation**: ✅
