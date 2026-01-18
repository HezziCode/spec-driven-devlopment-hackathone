---
id: 2
title: Fix Chat Task Persistence Planning
stage: plan
date: 2026-01-05
surface: agent
model: claude-sonnet-4-5
feature: 016-fix-chat-task-persistence
branch: 016-fix-chat-task-persistence
user: Claude Sonnet 4.5
command: /sp.plan
labels: ["planning", "chat", "persistence", "bug-fix", "architecture", "api-design"]
links:
  spec: specs/016-fix-chat-task-persistence/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/016-fix-chat-task-persistence/plan.md
  - specs/016-fix-chat-task-persistence/research.md
  - specs/016-fix-chat-task-persistence/data-model.md
  - specs/016-fix-chat-task-persistence/contracts/chat-api.md
tests:
  - None (planning phase)
---

## Prompt

/sp.plan

## Response snapshot

Created comprehensive implementation plan for fixing chat task persistence issues with detailed technical analysis and implementation strategy.

**Planning Artifacts Created**:

1. **Implementation Plan** (plan.md):
   - Executive summary of 7 critical issues to resolve
   - Technical context and current architecture analysis
   - Detailed root cause analysis for each issue
   - Constitution compliance verification (all 7 principles ✅)
   - Phase 0: Research tasks with 5 key areas
   - Phase 1: Design with data models and API contracts
   - Phase 2: Implementation strategy with priority-based ordering
   - Risk assessment (high/medium/low risk items)
   - Success metrics (technical and UX)
   - 6-day rollout plan with 4 phases

2. **Research Document** (research.md):
   - R1: OpenAI Agents SDK ThreadManager API - Correct usage patterns with required `content` parameter
   - R2: FastAPI SSE Streaming - Proper `data: {json}\n\n` format specification
   - R3: SQLModel Cascade Delete - Configuration for automatic child record deletion
   - R4: Frontend SSE Parsing - Robust parser with buffer management
   - R5: Database Transaction Management - Async context managers with commit/rollback
   - All research findings documented with code examples and rationale

3. **Data Model Documentation** (data-model.md):
   - ChatThread model with cascade delete relationships
   - ChatMessage model with proper foreign key constraints
   - Task model updates for source tracking (manual vs chat)
   - User model relationship updates
   - Complete database schema with indexes
   - Migration strategy with SQL scripts
   - Performance considerations and query optimization

4. **API Contracts** (contracts/chat-api.md):
   - GET /api/users/{user_id}/chat/threads - List threads with pagination
   - GET /api/users/{user_id}/chat/threads/{thread_id} - Get thread with messages
   - POST /api/users/{user_id}/chat/messages - Send message with SSE streaming
   - DELETE /api/users/{user_id}/chat/threads/{thread_id} - Delete thread
   - Complete request/response schemas with TypeScript interfaces
   - Error response format and codes
   - Rate limiting specifications
   - Security considerations

**Key Technical Decisions**:

1. **ThreadManager Fix**: Add required `content` parameter to all add_message() calls
2. **SSE Format**: Use proper `data: {json}\n\n` format with event markers
3. **Cascade Delete**: Configure ON DELETE CASCADE for thread-message relationships
4. **Transaction Management**: Use async context managers with proper commit/rollback
5. **Thread Limit**: Enforce 20-thread limit at application level with clear user feedback
6. **Task Source Tracking**: Add `source` and `created_by_thread_id` fields to tasks table

**Implementation Priority**:
- P1: Fix critical errors (ThreadManager, HTTP 500s, message persistence, task creation)
- P2: Fix UX issues (SSE format, thread limits, deletion)
- P3: Polish and edge cases (error handling, loading states, tests)

**Risk Assessment**:
- High: Database schema changes, SSE parsing changes, thread deletion cascade
- Medium: Thread limit enforcement, Agent SDK parameter changes
- Low: Error messages, loading states

**Estimated Effort**: 5-6 days across 4 rollout phases

## Outcome

- ✅ Impact: Complete implementation plan with detailed technical analysis, research findings, data models, and API contracts ready for task generation
- 🧪 Tests: Testing strategy defined with unit, integration, and E2E test requirements
- 📁 Files: Created plan.md, research.md, data-model.md, and contracts/chat-api.md
- 🔁 Next prompts: `/sp.tasks` to generate detailed task breakdown for implementation
- 🧠 Reflection: Successfully analyzed all 7 reported issues, identified root causes, researched correct solutions, and designed comprehensive fix strategy. Plan addresses both immediate bugs and long-term architecture improvements while maintaining constitution compliance.

## Evaluation notes (flywheel)

- Failure modes observed: None - planning completed successfully with all required artifacts
- Graders run and results (PASS/FAIL): All constitution principles verified PASS
- Prompt variant (if applicable): Standard /sp.plan workflow with Phase 0 research and Phase 1 design
- Next experiment (smallest change to try): Proceed to task generation to break plan into actionable implementation steps
