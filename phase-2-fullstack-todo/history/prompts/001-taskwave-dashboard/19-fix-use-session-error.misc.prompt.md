---
id: 19
title: fix-use-session-error
stage: misc
date: 2025-12-16
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-taskwave-dashboard
branch: 001-taskwave-dashboard
user: ""
command: "/sp.analyze"
labels: ["frontend", "auth", "bug-fix", "runtime-error"]
links:
  spec: specs/001-taskwave-dashboard/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - "frontend/lib/auth.ts"
  - "frontend/app/tasks/page.tsx"
tests:
  - "No tests specified"
---

## Prompt

but when i click on get started button to this err appera in task page ## Error Type
Runtime TypeError

## Error Message
useSession is not a function


    at useAuth (file://D:/Side Projects/giaic-hackathone/phase-2-fullstack-todo/frontend/.next/dev/static/chunks/_4f24ac78._.js:160:58)
    at TasksPage (file://D:/Side Projects/giaic-hackathone/phase-2-fullstack-todo/frontend/.next/dev/static/chunks/_4f24ac78._.js:2345:189)
    at Object.react_stack_bottom_frame (file://D:/Side Projects/giaic-hackathone/phase-2-fullstack-todo/frontend/.next/dev/static/chunks/node_modules_next_dist_compiled_react-dom_1e674e59._.js:14816:24)
    at renderWithHooks (file://D:/Side Projects/giaic-hackathone/phase-2-fullstack-todo/frontend/.next/dev/static/chunks/node_modules_next_dist_compiled_react-dom_1e674e59._.js:4645:24)
    at updateFunctionComponent (file://D:/Side Projects/giaic-hackathone/phase-2-fullstack-todo/frontend/.next/dev/static/chunks/node_modules_next_dist_compiled_react-dom_1e674e59._.js:6106:21)
    at beginWork (file://D:/Side Projects/giaic-hackathone/phase-2-fullstack-todo/frontend/.next/dev/static/chunks/node_modules_next_dist_compiled_react-dom_1e674e59._.js:6702:24)
    at runWithFiberInDEV (file://D:/Side Projects/giaic-hackathone/phase-2-fullstack-todo/frontend/.next/dev/static/chunks/node_modules_next_dist_compiled_react-dom_1e674e59._.js:959:74)
    at performUnitOfWork (file://D:/Side Projects/giaic-hackathone/phase-2-fullstack-todo/frontend/.next/dev/static/chunks/node_modules_next_dist_compiled_react-dom_1e674e59._.js:9556:97)
    at workLoopSync (file://D:/Side Projects/giaic-hackathone/phase-2-fullstack-todo/frontend/.next/dev/static/chunks/node_modules_next_dist_compiled_react-dom_1e674e59._.js:9450:40)
    at renderRootSync (file://D:/Side Projects/giaic-hackathone/phase-2-fullstack-todo/frontend/.next/dev/static/chunks/node_modules_next_dist_compiled_react-dom_1e674e59._.js:9434:13)
    at performWorkOnRoot (file://D:/Side Projects/giaic-hackathone/phase-2-fullstack-todo/frontend/.next/dev/static/chunks/node_modules_next_dist_compiled_react-dom_1e674e59._.js:9099:47)
    at performWorkOnRootViaSchedulerTask (file://D:/Side Projects/giaic-hackathone/phase-2-fullstack-todo/frontend/.next/dev/static/chunks/node_modules_next_dist_compiled_react-dom_1e674e59._.js:10224:9)
    at MessagePort.performWorkUntilDeadline (file://D:/Side Projects/giaic-hackathone/phase-2-fullstack-todo/frontend/.next/dev/static/chunks/node_modules_next_dist_compiled_a0e4c7b4._.js:2647:64)
    at ClientPageRoot (file://D:/Side Projects/giaic-hackathone/phase-2-fullstack-todo/frontend/.next/dev/static/chunks/node_modules_next_dist_094231d7._.js:2202:50)

Next.js version: 16.0.10 (Turbopack)

## Response snapshot

The /sp.analyze command has been initiated to identify inconsistencies, duplications, ambiguities, and underspecified items across the core artifacts. The user has reported a runtime error where 'useSession is not a function' occurs in the useAuth hook when accessing the tasks page after clicking the 'Get Started' button. This suggests an issue with the Better Auth integration in the auth.ts file where the useSession function is not properly defined or imported.

## Outcome

- ✅ Impact: Identified runtime error in authentication system
- 🧪 Tests: No tests specified
- 📁 Files: auth.ts and tasks page need inspection
- 🔁 Next prompts: Fix the Better Auth integration
- 🧠 Reflection: Runtime error indicates incorrect Better Auth API usage

## Evaluation notes (flywheel)

- Failure modes observed: Runtime TypeError with useSession
- Graders run and results (PASS/FAIL): Not applicable yet
- Prompt variant (if applicable): Bug analysis and fix
- Next experiment (smallest change to try): Fix useSession import in auth.ts