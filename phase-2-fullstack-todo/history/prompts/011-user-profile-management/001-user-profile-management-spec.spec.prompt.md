---
id: 001
title: user-profile-management-spec
stage: spec
date: 2025-12-25
surface: agent
model: claude-sonnet-4-5
feature: 011-user-profile-management
branch: 011-user-profile-management
user: system
command: /sp.specify
labels: ["user-profile", "crud", "security", "validation"]
links:
  spec: specs/011-user-profile-management/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/011-user-profile-management/spec.md
  - specs/011-user-profile-management/checklists/requirements.md
tests:
  - Specification quality validation (all checks passed)
---

## Prompt

User Profile Management Endpoints: Implement two user management endpoints - GET /api/users/{user_id} verifies path user_id matches authenticated user from JWT returns 403 Forbidden if mismatch, queries User table by user_id, excludes password_hash field from response for security, returns 200 OK with {id: UUID, username: string, email: string, created_at: timestamp, updated_at: timestamp}. PUT /api/users/{user_id} verifies user_id matches JWT returns 403, accepts {username: string optional 3-50 chars, email: string optional valid format}, validates at least one field provided returns 422 if both omitted, checks if new username already taken by another user returns 409 Conflict if duplicate, checks if new email already taken by another user returns 409 Conflict if duplicate, updates user record in database with provided fields, returns 200 OK with updated user object without password_hash. Create Pydantic schemas UserResponse (excludes password_hash), UpdateUserRequest (both fields optional) in schemas/user.py. Create service functions get_user_profile(user_id), update_user_profile(user_id, request) in services/user_service.py with duplicate checking logic. Acceptance criteria: GET returns user profile without password, PUT updates username and/or email, duplicate username returns 409, duplicate email returns 409, user isolation enforced returns 403, password_hash never exposed in any response, validation working returns 422, all tests passing including duplicate checks, cross-user access blocked, updating own profile succeeds. use related agents and skills too

## Response snapshot

Created comprehensive specification for User Profile Management Endpoints (CHUNK 7) with:

**Branch**: `011-user-profile-management`
**Spec File**: `specs/011-user-profile-management/spec.md`

**Key Features**:
- GET /users/{user_id} - View own profile with password exclusion
- PUT /users/{user_id} - Update username and/or email with duplicate checking

**Specification Details**:
- 4 prioritized user stories (P1-P3) with independent test scenarios
- 17 functional requirements (FR-001 to FR-017) covering:
  - User isolation (JWT verification, 403 for mismatched user_id)
  - Security (password_hash exclusion from all responses)
  - Validation (username 3-50 chars, email format, at least one field required)
  - Duplicate checking (409 Conflict for username/email taken by others)
  - Status codes (200, 401, 403, 404, 409, 422)
- 8 measurable success criteria (response times, error prevention, concurrency)
- 7 edge cases identified
- 8 assumptions documented
- 4 dependencies listed
- 9 out-of-scope items clearly defined

**Quality Validation**: All checklist items passed (zero [NEEDS CLARIFICATION] markers)

## Outcome

- ✅ Impact: Specification complete for CHUNK 7 (User Profile Management) - 6th of 12 backend chunks before frontend integration
- 🧪 Tests: Specification quality checklist - all 14 items passed
- 📁 Files: Created spec.md, checklists/requirements.md in correct location (specs/011-user-profile-management/)
- 🔁 Next prompts: `/sp.clarify` (optional - zero clarifications needed) or `/sp.plan` (ready for architecture planning)
- 🧠 Reflection: Comprehensive spec with clear security requirements, validation rules, and duplicate checking logic. All edge cases covered. Ready for planning phase with user-management-specialist agent.

## Evaluation notes (flywheel)

- Failure modes observed: Script created spec outside phase-2-fullstack-todo directory initially - manually corrected to maintain proper folder structure
- Graders run and results (PASS/FAIL): PASS - All 14 quality checklist items passed on first validation
- Prompt variant (if applicable): Standard /sp.specify workflow with detailed acceptance criteria
- Next experiment (smallest change to try): Proceed with /sp.plan using user-management-specialist agent
