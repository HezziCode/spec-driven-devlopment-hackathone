---
id: 2
title: ChatKit UI Implementation Plan
stage: plan
date: 2025-12-31
surface: agent
model: claude-sonnet-4-5-20250929
feature: 015-chatkit-ui
branch: 015-chatkit-ui
user: developer
command: /sp.plan
labels: ["chatkit", "implementation-plan", "openai", "react", "phase3", "agents", "skills"]
links:
  spec: specs/015-chatkit-ui/spec.md
  plan: specs/015-chatkit-ui/plan.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/015-chatkit-ui/plan.md
  - specs/015-chatkit-ui/research.md
  - specs/015-chatkit-ui/data-model.md
  - specs/015-chatkit-ui/quickstart.md
  - specs/015-chatkit-ui/contracts/chatkit-api.yaml
  - history/prompts/015-chatkit-ui/2-chatkit-ui-implementation-plan.plan.prompt.md
tests:
  - null
---

## Prompt

User ran `/sp.plan` with instruction: "use related agent and skills too" and then continued with: "continue ur plan and use related agent and skills too"

**Context**: Building on completed specification (PHR #1) to create comprehensive implementation plan with Phase 0 research and Phase 1 design artifacts.

## Response snapshot

Created complete implementation plan for ChatKit UI with Phase 0 research and Phase 1 design:

### Phase 0: Research (Completed)

**File**: `specs/015-chatkit-ui/research.md`

**Key Decisions Made**:
1. **ChatKit Integration**: Use @openai/chatkit-react with useChatKit hook
   - Rationale: Official library, React 19 compatible, built-in WebSocket handling
2. **Session Management**: Exchange JWT for ChatKit client secret via backend endpoint
   - Rationale: Maintains existing auth model, secure token exchange
3. **Thread Persistence**: Hybrid localStorage (immediate) + PostgreSQL (long-term)
   - Rationale: Balances performance with reliability
4. **Composer Tools**: Use ChatKit native composer.tools configuration
   - Rationale: Visual discovery, native UI, consistent UX
5. **Event Handlers**: All ChatKit events (onReady, onError, onThreadChange, onResponseStart/End)
   - Rationale: Comprehensive state management, proper loading/error states
6. **Theme**: Tailwind CSS with TaskWave teal-cyan gradients
   - Rationale: Consistency with existing design

**Technology Stack Finalized**: @openai/chatkit-react, Next.js 16, TypeScript 5.3+, Tailwind CSS, FastAPI, SQLModel, Neon PostgreSQL

---

### Phase 1: Design (Completed)

#### 1. Data Models (`data-model.md`)

**Frontend Models (TypeScript)**:
- `ChatSession` - Active session with client secret and status
- `ChatThread` - Thread metadata for display and persistence
- `ChatMessage` - Message structure (ChatKit-managed)
- `ToolCall` - AI tool invocation tracking
- `ComposerTool` - Tool menu configuration
- `ChatUIState` - Global UI state

**Backend Models (SQLModel)**:
- `ChatKitSession` - Session tracking with expiry
- `ChatThread` - Thread metadata persistence

**Pydantic Schemas**:
- `SessionResponse`, `ThreadSyncRequest`, `ThreadItem`, `ThreadListResponse`

**Database Tables**:
```sql
chatkit_sessions (id, user_id, client_secret_hash, created_at, expires_at, status)
chat_threads (id, user_id, name, last_message_preview, message_count, created_at, updated_at)
```

#### 2. API Contracts (`contracts/chatkit-api.yaml`)

**OpenAPI 3.1 Specification Created**:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/chatkit/session` | POST | Create ChatKit session (JWT → client_secret) |
| `/api/users/{user_id}/chatkit/threads` | GET | List user's threads with pagination |
| `/api/users/{user_id}/chatkit/threads/{thread_id}/sync` | POST | Sync thread metadata to database |
| `/api/users/{user_id}/chatkit/threads/{thread_id}` | DELETE | Delete chat thread |

**Authentication**: All endpoints require JWT Bearer token
**Error Handling**: Standardized responses (400, 401, 403, 404, 500)

#### 3. Quickstart Guide (`quickstart.md`)

**5-Phase Implementation Guide**:
1. Setup & Dependencies (30 min)
2. Backend API Implementation (2-3 hours)
3. Frontend Components (3-4 hours)
4. Integration & Testing (2-3 hours)
5. Testing & Polish (1-2 hours)

**Total Estimated Time**: 8-12 hours

**Includes**: Code examples, test checklists, troubleshooting guide

---

### Implementation Plan (`plan.md`)

**Complete plan document with**:

#### Technical Context
- Languages: TypeScript 5.3+ (frontend), Python 3.11+ (backend)
- Dependencies: @openai/chatkit-react, Next.js 16, React 19, FastAPI, SQLModel
- Storage: localStorage (local), PostgreSQL (persistent), ChatKit (messages)
- Performance targets: 2s init, 500ms message, 1s thread switch, 60fps UI
- Scale: 100 threads/user, 500+ messages/thread, multi-device support

#### Constitution Check
- ✅ All 7 principles satisfied (modularity, type safety, accessibility, performance, security, maintainability, stateless architecture)
- ✅ Post-design validation confirms compliance
- ✅ No violations requiring justification

#### Project Structure
- **Documentation**: spec.md, plan.md, research.md, data-model.md, quickstart.md, contracts/
- **Frontend**: app/chat/page.tsx, components/ChatInterface.tsx, lib/chatkit-api.ts, types/chatkit.ts
- **Backend**: models.py (add), schemas/chatkit.py (new), routes/chatkit.py (new), services/chatkit_service.py (new)

#### Agents & Skills Integration (User Requested)

**Primary Agent**:
- **`chatkit-frontend-builder`** - For ChatInterface component, useChatKit hook, composer tools, event handlers

**Supporting Agents**:
- **`frontend-feature-builder`** - For Next.js page and routing
- **`backend-api-builder`** - For FastAPI endpoints and database ops

**Key Skills**:
- **Frontend**: `chatkit-react-components` (ChatKit patterns), `frontend-component` (React), `frontend-api-client` (API calls), `frontend-types` (TypeScript)
- **Backend**: `fastapi-crud-endpoints` (REST patterns), `jwt-middleware` (auth), `pytest-api-testing` (tests)

#### Risk Assessment
- **Technical Risks**: 6 identified with mitigation (ChatKit breaking changes, session expiry, localStorage clear, WebSocket failures, sync conflicts, rate limiting)
- **Performance Risks**: 4 identified with mitigation (large thread list, concurrent users, storage quota, slow AI responses)
- **Integration Risks**: 3 identified with mitigation (MCP tools timeout, JWT expiry, API changes)

#### Testing Strategy
- **Backend**: 100% coverage for ChatKit endpoints (7 test cases)
- **Frontend**: 90% coverage for critical UI flows (6 test cases)
- **E2E**: Manual checklist (10 items) + optional automated Playwright tests

#### Implementation Phases
- **Phase 2A**: Backend Implementation (backend-api-builder agent, fastapi-crud-endpoints skill)
- **Phase 2B**: Frontend Implementation (chatkit-frontend-builder agent, chatkit-react-components skill)
- **Phase 2C**: Integration & Polish (frontend-feature-builder agent, page-animation skill)

---

### Quality & Completeness

**Constitution Compliance**: ✅ All principles satisfied
- Modularity: Component-based architecture
- Type Safety: Strict TypeScript + Python type hints
- Accessibility: ChatKit native a11y + custom labels
- Performance: WebSocket optimization, caching, pagination
- Security: JWT auth, user isolation, client secret hashing
- Maintainability: Documentation, agents, skills
- Stateless: All state persisted to DB

**Documentation Artifacts Created**: 5 files
- research.md (6 decisions with rationale)
- data-model.md (11 models with validation rules)
- chatkit-api.yaml (OpenAPI 3.1 spec with 4 endpoints)
- quickstart.md (5-phase guide with code examples)
- plan.md (comprehensive plan with agents/skills integration)

**Agent/Skill Integration**: ✅ Explicit mapping
- 3 agents identified for implementation phases
- 7 skills mapped to specific tasks
- Clear responsibilities and usage patterns

---

## Outcome

- ✅ Impact: Complete implementation plan ready for task generation
- 🧪 Tests: Testing strategy defined (backend 100%, frontend 90%, E2E manual)
- 📁 Files: 5 planning artifacts created (research, data-model, contracts, quickstart, plan)
- 🔁 Next prompts: `/sp.tasks` to generate detailed task breakdown
- 🧠 Reflection: Plan integrates seamlessly with existing Phase 2/3 infrastructure; agents/skills explicitly mapped per user request; quickstart provides step-by-step guidance

## Evaluation notes (flywheel)

- Failure modes observed: None - all Phase 0 and Phase 1 deliverables completed successfully
- Graders run and results (PASS/FAIL): Constitution check PASS (all 7 principles satisfied)
- Prompt variant (if applicable): Standard /sp.plan workflow with explicit agent/skill integration per user request
- Next experiment (smallest change to try): Proceed to `/sp.tasks` for task breakdown

## Key Strengths

1. **Comprehensive Research**: 6 key technical decisions with rationale and alternatives considered
2. **Detailed Data Models**: 11 models with validation rules, state transitions, and relationships
3. **Clear API Contracts**: OpenAPI 3.1 spec with 4 endpoints, authentication, and error handling
4. **Practical Quickstart**: 5-phase guide with code examples, test checklists, and troubleshooting
5. **Agent/Skill Integration**: Explicit mapping of agents and skills to implementation phases per user request
6. **Risk Management**: 13 risks identified with mitigation strategies
7. **Testing Strategy**: Clear targets (100% backend, 90% frontend, E2E manual)
8. **Performance Targets**: Specific metrics (2s init, 500ms message, 1s thread switch, 60fps)

## Ready for Implementation

This plan can proceed directly to task generation (`/sp.tasks`) as all research and design work is complete, agents/skills are identified, and implementation phases are clearly defined.
