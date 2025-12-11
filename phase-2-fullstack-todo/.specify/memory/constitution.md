<!--
Sync Impact Report:
Version change: 1.0.0 → 1.0.0 (initial constitution for this project)
Modified principles: None (new constitution)
Added sections: All sections (new constitution)
Removed sections: None
Templates requiring updates:
- .specify/templates/plan-template.md ✅ updated
- .specify/templates/spec-template.md ✅ updated
- .specify/templates/tasks-template.md ✅ updated
- .specify/templates/commands/*.md ⚠ pending
Follow-up TODOs: None
-->
# Phase 2 Full-Stack Todo Web App Constitution

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

## Technology Stack and Constraints

The project must use the following technology stack:
- Frontend: Next.js 16+ with App Router, TypeScript, Tailwind CSS
- Backend: FastAPI with Python 3.11+, SQLModel ORM
- Database: Neon Serverless PostgreSQL
- Authentication: Better Auth with JWT for backend verification
- Package Management: UV for Python dependencies, npm for frontend
- Testing: Pytest for backend, Jest/Vitest for frontend
- All features must support user isolation via JWT token verification

## Development Workflow and Quality Standards

Development follows a strict workflow: Specification → Planning → Task Generation → Agent/Skill Implementation → Testing → Commit. All commits must be atomic and include "Co-authored-by: Claude" attribution. No manual code editing by humans - all code must be generated via agents/skills. Every pull request must include comprehensive tests with 100% coverage for the changed functionality.

## Non-Functional Requirements (NFRs)

### Security Requirements
- All API endpoints must be secured with JWT token verification
- User data must be isolated by user_id to prevent cross-user access
- Authentication tokens must be properly validated and refreshed
- Input validation and sanitization required for all user inputs
- Environment variables for secrets (BETTER_AUTH_SECRET, DB_URL) must be properly configured

### Reliability Standards
- 99.9% uptime for core functionality
- Proper error handling and graceful degradation
- Comprehensive logging for debugging and monitoring
- Automated backup and recovery procedures for database

### Scalability Considerations
- Architecture must support multiple concurrent users
- Database queries optimized for performance
- Caching strategies where appropriate
- Efficient resource utilization

## Governance

This constitution is immutable and supersedes all other development practices for this project. Any changes to these principles require an Architectural Decision Record (ADR) with proper justification and approval. All pull requests and code reviews must verify compliance with these principles. Development teams must follow Spec-Kit-Plus guidance for runtime development and maintain consistency with these core principles.

**Version**: 1.0.0 | **Ratified**: 2025-12-12 | **Last Amended**: 2025-12-12
