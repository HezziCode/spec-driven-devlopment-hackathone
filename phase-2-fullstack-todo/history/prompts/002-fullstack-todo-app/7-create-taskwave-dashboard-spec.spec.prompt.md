---
id: 7
title: create-taskwave-dashboard-spec
stage: spec
date: 2025-12-16
surface: agent
model: claude-sonnet-4-5-20250929
feature: 002-fullstack-todo-app
branch: 002-fullstack-todo-app
user: ""
command: "/sp.specify"
labels: ["frontend", "dashboard", "taskwave", "authentication"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - "specs/003-taskwave-dashboard/spec.md"
  - "specs/003-taskwave-dashboard/checklists/requirements.md"
tests:
  - "No tests specified"
---

## Prompt

Create a detailed specification for the protected Todo (or Task) page in Phase 2, branded as 'TaskWave Dashboard' at /tasks route in Next.js App Router to add uniqueness (differentiate from generic todo apps by incorporating wave-themed elements like subtle wave animations on task cards, gamification: streak counter for completed tasks showing 'Wave Streak: X days' at top). It must be protected with Better Auth (redirect to /auth if no JWT). UI: Responsive layout with navbar (from components/Navbar.tsx), main content in grid/sections with unique 'Ride Your Task Waves' gradient heading (teal-cyan with subtle wave animation underline for distinctiveness, instead of plain 'My Tasks'). Include task list as interactive cards (not plain table for uniqueness: each card with wave border/animation on hover, showing title, desc, completed checkbox, priority badge (high/red with flame icon, med/yellow with clock, low/green with leaf), tags as colorful pills). Add form at top for new task (fields: title input required, desc textarea optional, priority select (high/med/low), tags multi-input with uniqueness: predefined readymade tags as clickable chips below input e.g., Fitness, Home, Work, Code, Planning, Design, UI/UX, Backend, Security – user clicks to auto-add to tags field, allow custom too). At the end of the task list, add a paid Pro feature section (teased with CSS blur filter on content for blurriness, 'Coming Soon' badge in teal-cyan gradient for attractiveness): Include 'Go Pro' button (cyan glow hover), small description 'Unlock AI magic: Auto-tags, smart priorities, sub-task breakdowns for ultimate productivity waves!', gated behind upgrade modal. Features: Search input (filter by title/tags), filter dropdowns (by status: All/Pending/Completed; by priority: All/High/Med/Low), sort buttons (by title/priority/created, with 'Smart Sort' as Pro tease button leading to upgrade). Use server components default, client for interactive (e.g., form submission, filters, tag clicks, Pro button). Integrate API calls via /lib/api.ts with JWT (GET/POST/PUT/DELETE/PATCH to /api/{user_id}/tasks endpoints, but focus on frontend UI for now – use mock data if needed). Handle loading states with suspense/spinner (wave-themed loader), errors with toasts. Match site theme: Teal-cyan gradients (#2dd4bf to #06b6d4), light mode bg #f0f9ff/text gray-800, dark mode bg #0f172a/text white; Inter font (extrabold headings, text-xl body); Animations: Hover scale-110/translate-y-1 on cards/buttons (duration-300), active scale-95, gradient text for headings, cursor glow (teal/cyan), backdrop-blur on filters bar, unique wave transition on task add/complete. Accessibility: ARIA labels, keyboard nav, contrast. Reference specs/features/task-crud.md, specs/ui/components.md, and constitution for modularity/type safety.

## Response snapshot

The /sp.specify command has been initiated to create a detailed specification for the TaskWave Dashboard. This will generate a comprehensive feature specification for the protected Todo page at /tasks route with wave-themed elements, authentication protection, and interactive UI components. The specification will cover user scenarios, functional requirements, success criteria, and key entities for the TaskWave dashboard implementation.

## Outcome

- ✅ Impact: Will generate comprehensive spec for TaskWave dashboard
- 🧪 Tests: No tests specified
- 📁 Files: Will create spec.md and requirements checklist
- 🔁 Next prompts: Planning and task generation for implementation
- 🧠 Reflection: This establishes the foundation for the wave-themed dashboard feature

## Evaluation notes (flywheel)

- Failure modes observed: None yet
- Graders run and results (PASS/FAIL): Not applicable yet
- Prompt variant (if applicable): Standard spec generation
- Next experiment (smallest change to try): Complete spec generation and review