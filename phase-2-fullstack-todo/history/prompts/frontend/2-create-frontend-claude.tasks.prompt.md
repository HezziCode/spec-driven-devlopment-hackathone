---
id: 2
title: Create Frontend CLAUDE
stage: tasks
date: 2025-12-12
surface: agent
model: Claude Sonnet 4.5
feature: frontend
branch: 001-console-todo-app
user: Claude
command: /sp.tasks "Generate /frontend/CLAUDE.md based on root CLAUDE.md. Focus on frontend guidelines: Stack (Next.js 16+ App Router, TS, Tailwind), patterns (server components default, client for interactivity, API calls via /lib/api.ts with JWT attach), component structure (/components, /app), styling (Tailwind only, no inline), auth (Better Auth config for JWT)."
labels: [frontend, documentation, guidelines]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - frontend/CLAUDE.md
tests:
 - none
---

## Prompt

Generate /frontend/CLAUDE.md based on root CLAUDE.md. Focus on frontend guidelines: Stack (Next.js 16+ App Router, TS, Tailwind), patterns (server components default, client for interactivity, API calls via /lib/api.ts with JWT attach), component structure (/components, /app), styling (Tailwind only, no inline), auth (Better Auth config for JWT)."

## Response snapshot

Created comprehensive frontend CLAUDE.md file with specific guidelines for Next.js frontend development:

1. Technology Stack: Next.js 16+, TypeScript, Tailwind CSS, Better Auth with JWT
2. Project Structure: Detailed directory structure with /app, /components, /lib organization
3. Component Patterns: Server components as default, client components for interactivity
4. API Integration: Centralized API client in /lib/api.ts with JWT handling
5. Styling Guidelines: Tailwind CSS only, no inline styles
6. Authentication: Better Auth configuration with JWT plugin
7. TypeScript Best Practices: Strict mode, shared types, proper typing
8. Component Architecture: Base UI, feature, and layout components
9. Development Workflow: Step-by-step development approach
10. Security and Accessibility: WCAG 2.1 AA compliance and security guidelines

## Outcome

- ✅ Impact: Created detailed frontend development guidelines
- 🧪 Tests: No tests needed for documentation file
- 📁 Files: Created frontend/CLAUDE.md
- 🔁 Next prompts: Continue with frontend implementation tasks
- 🧠 Reflection: Documentation provides clear frontend development standards

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A