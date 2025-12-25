---
id: 6
title: create-frontend-skills
stage: tasks
date: 2025-12-16
surface: agent
model: claude-sonnet-4-5-20250929
feature: 002-fullstack-todo-app
branch: 002-fullstack-todo-app
user: ""
command: "/sp.tasks"
labels: ["frontend", "skills", "taskwave", "dashboard"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - ".skills/task-card/skill.md"
  - ".skills/new-task-form/skill.md"
  - ".skills/pro-feature-tease/skill.md"
  - ".skills/wave-animations/skill.md"
tests:
  - "No tests specified"
---

## Prompt

Generate reusable skills in .skills/ for TaskWave Dashboard frontend implementation: 1. .skills/task-card/skill.md – Patterns for interactive wave-themed cards (wave border SVG/animation on hover, priority badges with icons, tags pills, completed checkbox, hover scale-110/translate-y-1 duration-300). 2. .skills/new-task-form/skill.md – Patterns for form with title/desc/priority select, tags multi-input + clickable predefined chips (e.g., Fitness/Home/Work auto-add on click). 3. .skills/pro-feature-tease/skill.md – Patterns for end-section with blur filter, 'Coming Soon' gradient badge, 'Go Pro' button (cyan glow), small desc, upgrade modal trigger. 4. .skills/wave-animations/skill.md – Reusable wave-themed animations/transitions (e.g., on add/complete, cursor glow teal/cyan, backdrop-blur). Include theme integration (teal-cyan gradients, Inter font, light/dark modes), accessibility (ARIA/keyboard), and client-side interactivity. Reference constitution for type safety/modularity, use Tailwind classes.

## Response snapshot

The /sp.tasks command has been initiated to generate tasks for creating reusable skills in .skills/ for TaskWave Dashboard frontend implementation. The command will analyze the feature specifications and generate a tasks.md file with detailed implementation steps for:
1. Task card skill with wave-themed design
2. New task form skill with multi-input functionality
3. Pro feature tease skill with upgrade modal
4. Wave animations skill with theme integration

The generated tasks will follow the constitution guidelines for type safety, modularity, and accessibility while using Tailwind CSS classes.

## Outcome

- ✅ Impact: Will generate structured tasks for implementing frontend skills
- 🧪 Tests: No tests specified
- 📁 Files: Will create 4 skill files in .skills/ directory
- 🔁 Next prompts: Implementation of the generated tasks
- 🧠 Reflection: This will establish reusable frontend patterns for the TaskWave dashboard

## Evaluation notes (flywheel)

- Failure modes observed: None yet
- Graders run and results (PASS/FAIL): Not applicable yet
- Prompt variant (if applicable): Standard tasks generation
- Next experiment (smallest change to try): Execute the generated tasks