---
id: 1
title: Create Constitution
stage: constitution
date: 2025-12-12
surface: agent
model: Claude Sonnet 4.5
feature: none
branch: 001-console-todo-app
user: Claude
command: /sp.constitution "Create a detailed constitution.md for Phase 2 Full-Stack Todo Web App. Base it on the provided Phase 2 description: Evolve Phase 1 console app to web with Neon DB persistence, adding priorities/tags/search/filter/sort. Tech: Next.js (App Router, TS, Tailwind), FastAPI, SQLModel, Better Auth (JWT for auth). Principles: SDD with agents/skills, clean code (SRP, docstrings), type safety, accessibility (WCAG 2.1 AA), performance, modular arch. Scope: Basic + intermediate features, user isolation via JWT. Constraints: No manual code, atomic commits 'Co-authored-by: Claude'. Include project overview, stack/constraints, code quality, arch principles, dev guidelines, NFRs. Make immutable unless ADR. Integrate MCP tools prep if needed for future phases."
labels: [constitution, spec, governance]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - none
---

## Prompt

Create a detailed constitution.md for Phase 2 Full-Stack Todo Web App. Base it on the provided Phase 2 description: Evolve Phase 1 console app to web with Neon DB persistence, adding priorities/tags/search/filter/sort. Tech: Next.js (App Router, TS, Tailwind), FastAPI, SQLModel, Better Auth (JWT for auth). Principles: SDD with agents/skills, clean code (SRP, docstrings), type safety, accessibility (WCAG 2.1 AA), performance, modular arch. Scope: Basic + intermediate features, user isolation via JWT. Constraints: No manual code, atomic commits 'Co-authored-by: Claude'. Include project overview, stack/constraints, code quality, arch principles, dev guidelines, NFRs. Make immutable unless ADR. Integrate MCP tools prep if needed for future phases.

## Response snapshot

Created a comprehensive constitution.md file for the Phase 2 Full-Stack Todo Web App with the following sections:

1. Core Principles:
   - I. Spec-Driven Development (SDD) with Agents/Skills
   - II. Clean Code with Single Responsibility Principle
   - III. Type Safety and Strict TypeScript/Python Typing (NON-NEGOTIABLE)
   - IV. Accessibility Compliance (WCAG 2.1 AA)
   - V. Performance-First Architecture
   - VI. Modular Architecture with Clear Boundaries

2. Technology Stack and Constraints:
   - Defined the required technology stack (Next.js, FastAPI, SQLModel, Neon, Better Auth)
   - Package management requirements (UV, npm)

3. Development Workflow and Quality Standards:
   - SDD workflow process
   - Commit standards with Claude attribution
   - No manual code editing requirement

4. Non-Functional Requirements:
   - Security requirements with JWT and user isolation
   - Reliability and scalability standards

5. Governance:
   - Immutable constitution with ADR process for changes

## Outcome

- ✅ Impact: Created initial project constitution with comprehensive principles and guidelines
- 🧪 Tests: No tests needed for documentation file
- 📁 Files: Modified .specify/memory/constitution.md
- 🔁 Next prompts: Continue with spec and plan generation
- 🧠 Reflection: Constitution provides clear governance framework for the project

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A