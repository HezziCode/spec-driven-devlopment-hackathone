---
id: 4
title: Create API Endpoint Skill
stage: tasks
date: 2025-12-12
surface: agent
model: Claude Sonnet 4.5
feature: backend
branch: 001-console-todo-app
user: Claude
command: /sp.tasks "Generate .skills/api-endpoint/skill.md. Purpose: Create secure FastAPI routes with SQLModel CRUD. Patterns: @app.post('/tasks'), async def with Session=Depends(get_db), JWT verify, Pydantic models, error handling. Examples: Create task with user_id filter, integrate MCP tools for agent comms if needed."
labels: [backend, skill, api, fastapi]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .claude/.skills/api-endpoint/skill.md
tests:
 - none
---

## Prompt

"Generate .skills/api-endpoint/skill.md. Purpose: Create secure FastAPI routes with SQLModel CRUD. Patterns: @app.post('/tasks'), async def with Session=Depends(get_db), JWT verify, Pydantic models, error handling. Examples: Create task with user_id filter, integrate MCP tools for agent comms if needed."

## Response snapshot

Created comprehensive API endpoint skill with guidelines for creating secure FastAPI routes:

1. Purpose: Secure FastAPI routes with SQLModel CRUD operations
2. Pattern: Complete example with JWT verification, database session management
3. Key Components: Authentication, database session, Pydantic models, error handling
4. Security Considerations: JWT verification, user isolation, input validation
5. MCP Integration: Guidelines for multi-agent communication
6. Common Variations: Different endpoint types (GET, PUT, PATCH, DELETE)
7. Validation Checklist: Complete verification steps

The skill includes proper JWT token verification, SQLModel session management, Pydantic validation, user isolation by user_id, and error handling patterns.

## Outcome

- ✅ Impact: Created reusable skill for API endpoint development
- 🧪 Tests: No tests needed for documentation file
- 📁 Files: Created .claude/.skills/api-endpoint/skill.md
- 🔁 Next prompts: Continue with other backend skills
- 🧠 Reflection: Skill provides clear pattern for secure API development

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A