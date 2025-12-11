---
id: 3
title: Create Backend CLAUDE
stage: tasks
date: 2025-12-12
surface: agent
model: Claude Sonnet 4.5
feature: backend
branch: 001-console-todo-app
user: Claude
command: /sp.tasks "Generate /backend/CLAUDE.md based on root CLAUDE.md. Focus on backend guidelines: Stack (FastAPI, SQLModel, Neon PG), structure (main.py, models.py, routes/, db.py), API conventions (JSON, Pydantic, HTTPException), DB ops (SQLModel, env DATABASE_URL/BETTER_AUTH_SECRET), JWT middleware for auth verification, running (uvicorn)."
labels: [backend, documentation, guidelines]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - backend/CLAUDE.md
tests:
 - none
---

## Prompt

Generate /backend/CLAUDE.md based on root CLAUDE.md. Focus on backend guidelines: Stack (FastAPI, SQLModel, Neon PG), structure (main.py, models.py, routes/, db.py), API conventions (JSON, Pydantic, HTTPException), DB ops (SQLModel, env DATABASE_URL/BETTER_AUTH_SECRET), JWT middleware for auth verification, running (uvicorn)."

## Response snapshot

Created comprehensive backend CLAUDE.md file with specific guidelines for FastAPI backend development:

1. Technology Stack: FastAPI, SQLModel, Neon PostgreSQL, UV, Uvicorn
2. Project Structure: Detailed directory structure with main.py, models.py, routes/, db.py organization
3. API Conventions: JSON responses, Pydantic schemas, HTTPException for errors
4. Database Operations: SQLModel usage, environment variables (DATABASE_URL/BETTER_AUTH_SECRET)
5. Authentication: JWT middleware implementation, user isolation via user_id validation
6. Development Guidelines: Type safety, code organization, testing requirements
7. Running the Application: Development and production deployment guidance
8. Security Considerations: Input validation, authentication security, database security
9. Performance: Query optimization, API performance, caching strategies
10. Error Handling and Logging: Structured logging, standardized error responses
11. Environment Configuration: Required environment variables, development setup
12. Deployment: Production deployment considerations

## Outcome

- ✅ Impact: Created detailed backend development guidelines
- 🧪 Tests: No tests needed for documentation file
- 📁 Files: Created backend/CLAUDE.md
- 🔁 Next prompts: Continue with backend implementation tasks
- 🧠 Reflection: Documentation provides clear backend development standards

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A