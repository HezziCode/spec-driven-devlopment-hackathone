# Quickstart: User Profile Management

**Feature**: User Profile Management Endpoints
**Status**: Planning Complete - Ready for Implementation

---

## Overview

Implement two secure REST API endpoints for user profile management:
- **GET /users/{user_id}**: Retrieve user profile
- **PUT /users/{user_id}**: Update username and/or email

---

## Prerequisites

- ✅ Database Foundation (CHUNK 1): User model exists
- ✅ JWT Middleware (CHUNK 2): Authentication functional
- ✅ Auth Endpoints (CHUNK 3): User signup/login working

---

## Implementation Order

### 1. Schemas (30 min)
Create `backend/schemas/user.py`:
- `UserResponse`: Excludes password_hash
- `UpdateUserRequest`: Optional username/email fields

### 2. Services (1 hour)
Create `backend/services/user_service.py`:
- `get_user_profile()`: Simple SELECT by ID
- `update_user_profile()`: Duplicate checking + update

### 3. Routes (45 min)
Create `backend/routes/users.py`:
- GET endpoint with JWT verification
- PUT endpoint with user isolation
- Register router in `main.py`

### 4. Tests (2 hours)
Create `backend/tests/test_user_profile.py`:
- 24+ tests covering security, duplicates, validation

**Total**: ~4-5 hours

---

## Key Design Decisions

1. **Password Exclusion**: Pydantic `response_model` enforces security
2. **Duplicate Checking**: Explicit queries excluding current user
3. **Partial Updates**: Optional fields, at least one required
4. **User Isolation**: JWT user_id must match path user_id

---

## Testing Strategy

**Security Tests** (8):
- Password hash never in response
- Cross-user access blocked (403)
- JWT validation (401)

**Duplicate Tests** (6):
- Username/email uniqueness (409)
- Case-insensitive email duplicates
- Idempotent updates allowed

**Validation Tests** (4):
- Username length (3-50 chars)
- Email format
- At least one field required

**Integration Tests** (6):
- Full GET/PUT flows
- Transaction rollback on errors

---

## Files to Create

- [ ] `backend/schemas/user.py`
- [ ] `backend/services/user_service.py`
- [ ] `backend/routes/users.py`
- [ ] `backend/tests/test_user_profile.py`

## Files to Modify

- [ ] `backend/main.py` (register users router)

---

## Success Criteria

- ✅ All 17 functional requirements implemented
- ✅ All 24+ tests passing
- ✅ Password hash never exposed (100% test coverage)
- ✅ Cross-user access blocked (100% test coverage)
- ✅ Duplicate detection working (100% accuracy)
- ✅ GET <1s, PUT <2s (95th percentile)
- ✅ Code coverage ≥95%

---

## Next Steps

1. Review plan.md for detailed architecture
2. Run `/sp.tasks` to generate task list
3. Run `/sp.implement` with user-management-specialist agent
4. Verify all tests pass
5. Create PR for review

---

## Agent & Skills

**Agent**: `user-management-specialist`
**Location**: `backend/.claude/agents/user-management-specialist.md`

**Skills**:
- user-profile-management
- duplicate-checking
- secure-responses

---

## Reference Documents

- **spec.md**: Feature requirements and user stories
- **plan.md**: Detailed architecture and implementation strategy
- **data-model.md**: Database schema and field validation
- **contracts/**: API request/response specifications
