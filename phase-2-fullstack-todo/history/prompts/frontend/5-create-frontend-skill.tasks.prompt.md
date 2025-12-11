---
id: 5
title: Create Frontend Component Skill
stage: tasks
date: 2025-12-12
surface: agent
model: Claude Sonnet 4.5
feature: frontend
branch: 001-console-todo-app
user: Claude
command: /sp.tasks "Generate .skills/frontend-component/skill.md. Purpose: Create Next.js server/client components. Patterns: Server by default, 'use client' for interactive, ProtectedRoute for auth, Tailwind classes, suspense loading. Examples: Task form with JWT API post, accessible ARIA/keyboard nav."
labels: [frontend, skill, component, nextjs]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .claude/.skills/frontend-component/skill.md
tests:
 - none
---

## Prompt

"Generate .skills/frontend-component/skill.md. Purpose: Create Next.js server/client components. Patterns: Server by default, 'use client' for interactive, ProtectedRoute for auth, Tailwind classes, suspense loading. Examples: Task form with JWT API post, accessible ARIA/keyboard nav."

## Response snapshot

Created comprehensive frontend component skill with guidelines for creating Next.js components:

1. Purpose: Next.js server/client components with best practices
2. Pattern: Complete examples for server components, client components, and protected routes
3. Key Components: Server/client patterns, protected routes, Tailwind styling, accessibility
4. API Integration: Centralized API client with JWT handling
5. Security Considerations: Client-side validation, input sanitization
6. Performance: React.Suspense, code splitting, optimization strategies
7. Accessibility: WCAG 2.1 AA compliance with ARIA attributes
8. MCP Integration: Guidelines for multi-agent communication
9. Common Variations: Different component types and patterns
10. Validation Checklist: Complete verification steps

The skill includes proper server/client component patterns, authentication protection, Tailwind styling, and accessibility features.

## Outcome

- ✅ Impact: Created reusable skill for frontend component development
- 🧪 Tests: No tests needed for documentation file
- 📁 Files: Created .claude/.skills/frontend-component/skill.md
- 🔁 Next prompts: Continue with other frontend skills
- 🧠 Reflection: Skill provides clear pattern for component development

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A