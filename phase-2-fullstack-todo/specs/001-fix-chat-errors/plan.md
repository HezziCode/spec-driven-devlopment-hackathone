# Implementation Plan: Fix Chat Thread and API Key Errors

**Branch**: `001-fix-chat-errors` | **Date**: 2026-01-13 | **Spec**: [link](spec.md)
**Input**: Feature specification from `/specs/001-fix-chat-errors/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Fix two critical errors in the chat functionality: 1) HTTP 404 errors when loading chat threads due to timing issues between thread creation and access, and 2) HTTP 401 API authentication errors when connecting to OpenAI services. The solution involves implementing proper thread synchronization, retry mechanisms, and correct OpenAI API key configuration.

## Technical Context

**Language/Version**: Python 3.13, TypeScript/JavaScript (Next.js 16.0.10)
**Primary Dependencies**: FastAPI, SQLModel, Next.js, OpenAI Agents SDK, uv (package manager)
**Storage**: PostgreSQL (Neon)
**Testing**: pytest (backend), Jest/Vitest (frontend)
**Target Platform**: Linux server (backend), Web browser (frontend)
**Project Type**: Web application (full-stack)
**Performance Goals**: Sub-2 second thread loading, sub-200ms API responses, stable SSE connections
**Constraints**: <200ms p95 response time, secure API key handling, thread access validation
**Scale/Scope**: Single user per session, multiple concurrent chat threads per user

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [X] **Clean Code with SRP**: Each function/module will have single responsibility
- [X] **Type Safety**: All code will use strict TypeScript/Python typing with no 'any' types
- [X] **Accessibility**: Existing UI patterns will maintain WCAG 2.1 AA compliance
- [X] **Performance**: Solutions will maintain O(1)/O(n) complexity goals
- [X] **Modular Architecture**: Changes will respect clear frontend/backend separation
- [X] **SDD Methodology**: All implementation will follow Spec-Driven Development using agents/skills

## Project Structure

### Documentation (this feature)

```text
specs/001-fix-chat-errors/
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
│   │   └── chatkit_service.py    # Thread synchronization fixes
│   ├── routes/
│   │   └── custom_chat.py        # Thread access endpoint fixes
│   └── chatkit/
│       ├── server.py             # SSE connection stability
│       ├── agent.py              # OpenAI API configuration
│       └── thread_manager.py     # Thread creation/access synchronization
└── tests/
    └── test_chat_endpoints.py

frontend/
├── src/
│   ├── components/
│   │   └── CustomChatInterface.tsx    # 404 error handling, retry logic
│   ├── lib/
│   │   └── sse-parser.ts              # SSE error handling
│   └── types/
│       └── sse.ts                     # SSE type definitions
└── tests/
    └── chat-interface.test.tsx
```

**Structure Decision**: Full-stack web application with separate backend (FastAPI) and frontend (Next.js) following established project architecture.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Cross-layer changes | Need to fix synchronization between frontend and backend | Single-layer fix wouldn't address race condition root cause |