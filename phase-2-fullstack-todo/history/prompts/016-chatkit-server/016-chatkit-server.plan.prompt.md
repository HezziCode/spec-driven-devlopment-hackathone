---
id: "016-chatkit-server-plan-001"
title: "ChatKit AI server plan"
stage: "plan"
date: "2025-12-30"
surface: "agent"
model: "sonnet-4-5-20250929"
feature: "016-chatkit-server"
branch: "016-chatkit-server"
user: "human"
command: "sp.plan"
labels: ["feature", "chat", "ai", "planning"]
links:
  spec: "specs/016-chatkit-server/spec.md"
  ticket: null
  adr: null
  pr: null
files:
  - "specs/016-chatkit-server/plan.md"
  - "specs/016-chatkit-server/data-model.md"
  - "specs/016-chatkit-server/contracts/chatkit-endpoint.yaml"
  - "specs/016-chatkit-server/quickstart.md"
  - "specs/016-chatkit-server/research.md"
tests: []
---

## Prompt

Run /sp.plan for feature 016-chatkit-server to create implementation plan.

## Response snapshot

Created comprehensive implementation plan for ChatKit AI Chat Server:

**Research (Phase 0)**:
- Streaming: `Runner.run_streamed()` with `stream_events()` filtering for `ResponseTextDeltaEvent`
- SSE format: Standard `data: <text>\n\n` format with event types
- AgentContext: dataclass with user_id, thread_id passed via Runner context

**Design (Phase 1)**:
- Data model: Thread and ChatMessage entities with indexes
- API contracts: OpenAPI spec for /chatkit endpoint with streaming
- Quickstart: Testing examples with curl and frontend integration

**Key Architecture Decisions**:
- Thread storage: SQLModel with 20-message context limit
- Response format: Server-Sent Events (text/event-stream)
- Tool integration: Reuse MCP tools from 014-mcp-todo-server

**Constitution Check**: All 7 principles pass ✅

## Outcome

- ✅ Impact: Complete implementation plan for AI chat server
- 🧪 Tests: None - planning phase
- 📁 Files: plan.md, data-model.md, contracts/, quickstart.md, research.md
- 🔁 Next prompts: /sp.tasks to generate implementation tasks
- 🧠 Reflection: Streaming pattern well-documented via Context7 research

## Evaluation notes (flywheel)

- Failure modes observed: Agent context script had Windows line endings (skipped)
- Graders run and results (PASS/FAIL): N/A (planning phase)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
