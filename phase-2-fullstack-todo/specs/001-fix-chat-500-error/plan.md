# Implementation Plan: Fix Chat Message Loading Error

**Feature**: 001-fix-chat-500-error
**Branch**: `001-fix-chat-500-error`
**Created**: 2026-01-04
**Status**: Ready for Implementation

## Executive Summary

Fix critical bug in chat functionality where sending messages results in HTTP 500 errors due to improper database session management. The thread manager receives a generator object instead of a SQLAlchemy Session object, causing `AttributeError: 'generator' object has no attribute 'connect'`.

**Impact**: Chat feature is completely non-functional - users cannot send messages or interact with AI assistant.

**Solution**: Implement proper FastAPI dependency injection pattern for database sessions, ensuring resolved Session objects are passed to service layers and utilities.

**Estimated Effort**: 2-3 hours
**Risk Level**: Low (isolated fix, well-understood problem)

## Technical Context

### Current Architecture

```
Route Handler (custom_chat.py)
    ↓
ChatKitService (chatkit_service.py)
    ↓
ChatKitServer (chatkit/server.py)
    ↓
ThreadManager (chatkit/thread_manager.py)
    ↓
Database (via SQLAlchemy Session)
```

### Root Cause

The session is being passed as a generator function or factory instead of a resolved Session object. When ThreadManager attempts to use it:

```python
# Current (BROKEN):
thread_manager = ThreadManager(get_session)  # Passes generator
thread = thread_manager.get_thread(...)      # Fails: generator has no 'connect'

# Required (FIXED):
session = await get_session()                # Resolve generator
thread_manager = ThreadManager(session)      # Pass concrete session
thread = thread_manager.get_thread(...)      # Works!
```

### Error Details

**Error**: `AttributeError: 'generator' object has no attribute 'connect'`
**Location**: `backend/chatkit/thread_manager.py:55` in `get_thread()`
**Trigger**: `session.get(Thread, thread_id)`
**Frequency**: 100% of message send attempts

### Affected Components

| Component | File | Issue |
|-----------|------|-------|
| Route Handler | `backend/routes/custom_chat.py` | Not injecting session via Depends() |
| ChatKit Service | `backend/services/chatkit_service.py` | Passing generator instead of session |
| ChatKit Server | `backend/chatkit/server.py` | Receiving and passing generator |
| Thread Manager | `backend/chatkit/thread_manager.py` | Attempting to use generator as session |

## Constitution Check

### Principle Compliance

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Development | ✅ PASS | Following SDD workflow: spec → plan → tasks → implement |
| II. Clean Code & SRP | ✅ PASS | Each component has single responsibility; fix maintains separation |
| III. Type Safety | ✅ PASS | Using AsyncSession type hints throughout |
| IV. Accessibility | N/A | Backend-only fix, no UI changes |
| V. Performance-First | ✅ PASS | Proper session management improves connection pooling |
| VI. Modular Architecture | ✅ PASS | Clear boundaries maintained between layers |
| VII. Stateless Server | ✅ PASS | No state held between requests; sessions managed per-request |

### Technology Stack Compliance

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| FastAPI | ✅ PASS | Using FastAPI dependency injection (Depends) |
| SQLAlchemy/SQLModel | ✅ PASS | Using AsyncSession from SQLAlchemy |
| Python 3.11+ | ✅ PASS | Async/await syntax, type hints |
| Type Safety | ✅ PASS | Full type hints for all session parameters |

### NFR Compliance

| NFR | Status | Implementation |
|-----|--------|----------------|
| Security | ✅ PASS | User isolation maintained via JWT and user_id filtering |
| Reliability | ✅ PASS | Proper error handling and session rollback |
| Performance | ✅ PASS | Session lifecycle optimized, no performance degradation |
| Maintainability | ✅ PASS | Following FastAPI best practices, clear code structure |

## Implementation Strategy

### Phase 0: Research & Design ✅ COMPLETED

**Artifacts Created**:
- `research.md` - Session management patterns and best practices
- `data-model.md` - Existing Thread and Message models documentation
- `quickstart.md` - Developer guide for implementing the fix

**Key Decisions**:
1. Use FastAPI dependency injection with `Depends(get_session)`
2. Pass resolved AsyncSession objects to services
3. Services pass sessions to utilities (thread manager)
4. Maintain async operations throughout stack

### Phase 1: Core Session Management Fix

**Objective**: Fix session passing from routes to thread manager

**Files to Modify**:

1. **`backend/routes/custom_chat.py`**
   - Add session injection via `Depends(get_session)`
   - Pass resolved session to ChatKitService
   - Update all route handlers that use chat functionality

2. **`backend/services/chatkit_service.py`**
   - Update constructor to accept `AsyncSession`
   - Store session as instance variable
   - Pass session to ChatKitServer and ThreadManager

3. **`backend/chatkit/server.py`**
   - Update constructor to accept `AsyncSession`
   - Pass session to ThreadManager
   - Use session for any direct database operations

4. **`backend/chatkit/thread_manager.py`**
   - Update constructor to accept `AsyncSession` (not generator)
   - Store session as instance variable
   - Use `self.session` for all database operations
   - Update all methods to use async session operations

**Implementation Order**:
1. ThreadManager (bottom-up approach)
2. ChatKitServer
3. ChatKitService
4. Route handlers

**Rationale**: Fix from bottom up to ensure each layer receives correct session type.

### Phase 2: Error Handling & Logging

**Objective**: Add proper error handling for database operations

**Changes**:

1. **ThreadManager error handling**:
   ```python
   async def get_thread(self, user_id: str, thread_id: str) -> Thread:
       try:
           result = await self.session.execute(...)
           thread = result.scalar_one_or_none()
           if not thread:
               raise HTTPException(404, "Thread not found")
           return thread
       except SQLAlchemyError as e:
           logger.error(f"Database error: {e}", exc_info=True)
           raise HTTPException(500, "Database error")
   ```

2. **Service layer error handling**:
   - Catch and log exceptions from thread manager
   - Return appropriate HTTP status codes
   - Provide user-friendly error messages

3. **Enhanced logging**:
   - Log session initialization
   - Log successful database operations
   - Log errors with full context

### Phase 3: Testing & Validation

**Test Strategy**:

1. **Unit Tests** (backend/tests/test_thread_manager.py):
   - Test ThreadManager with mock AsyncSession
   - Test get_thread with valid/invalid thread_id
   - Test user isolation (wrong user_id)
   - Test error handling

2. **Integration Tests** (backend/tests/test_chat_integration.py):
   - Test full message send flow
   - Test thread creation and retrieval
   - Test concurrent message sending
   - Test session lifecycle

3. **Manual Testing**:
   - Send message via frontend
   - Verify no 500 errors
   - Check backend logs for proper session usage
   - Test multiple concurrent users

**Success Criteria**:
- ✅ All unit tests pass
- ✅ All integration tests pass
- ✅ Manual testing shows no 500 errors
- ✅ Backend logs show proper session initialization
- ✅ No "generator object" errors in logs

## File Changes Summary

| File | Type | Lines Changed | Complexity |
|------|------|---------------|------------|
| `backend/routes/custom_chat.py` | Modify | ~10-15 | Low |
| `backend/services/chatkit_service.py` | Modify | ~15-20 | Low |
| `backend/chatkit/server.py` | Modify | ~10-15 | Low |
| `backend/chatkit/thread_manager.py` | Modify | ~20-30 | Medium |
| `backend/tests/test_thread_manager.py` | Create | ~100-150 | Medium |
| `backend/tests/test_chat_integration.py` | Create | ~150-200 | Medium |

**Total Estimated Changes**: ~300-400 lines

## Dependencies & Prerequisites

### External Dependencies
- ✅ SQLAlchemy (already installed)
- ✅ FastAPI (already installed)
- ✅ SQLModel (already installed)
- ✅ Pytest (already installed)

### Internal Dependencies
- ✅ Database connection working
- ✅ User authentication working
- ✅ Thread and Message models defined
- ✅ Session factory (`get_session`) exists

### Environment Requirements
- ✅ `DATABASE_URL` configured
- ✅ `BETTER_AUTH_SECRET` configured
- ✅ Backend server can connect to database

## Risk Assessment

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Breaking existing functionality | Low | High | Comprehensive testing, gradual rollout |
| Session lifecycle issues | Low | Medium | Follow FastAPI best practices, proper cleanup |
| Performance degradation | Very Low | Medium | Session pooling already configured |
| Concurrent access issues | Low | Medium | Test with multiple simultaneous requests |

### Rollback Plan

If issues arise after deployment:
1. Revert changes to affected files
2. Restart backend server
3. Monitor error logs
4. Re-test with previous version

**Rollback Time**: < 5 minutes

## Testing Strategy

### Test Coverage Goals
- Unit tests: 100% coverage for modified code
- Integration tests: All critical paths covered
- Manual tests: All user scenarios verified

### Test Environments
1. **Local Development**: Initial testing
2. **Staging**: Full integration testing
3. **Production**: Gradual rollout with monitoring

### Performance Testing
- Baseline: Current error rate (100%)
- Target: 0% error rate for valid requests
- Load test: 100 concurrent message sends

## Deployment Strategy

### Pre-Deployment Checklist
- [ ] All tests passing
- [ ] Code review completed
- [ ] Type checking passing (mypy)
- [ ] Linting passing
- [ ] Documentation updated

### Deployment Steps
1. Merge feature branch to main
2. Deploy to staging environment
3. Run smoke tests
4. Monitor error logs for 1 hour
5. Deploy to production
6. Monitor for 24 hours

### Monitoring
- Error rate (should drop to 0%)
- Response times (should remain stable)
- Database connection pool usage
- Session lifecycle metrics

## Success Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Message send success rate | 0% | 100% | HTTP status codes |
| 500 errors per hour | ~50 | 0 | Error logs |
| Average response time | N/A | < 200ms | API monitoring |
| Database session errors | 100% | 0% | Error logs |

## Timeline

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 0: Research | ✅ Complete | None |
| Phase 1: Core Fix | 1-1.5 hours | Phase 0 |
| Phase 2: Error Handling | 30 minutes | Phase 1 |
| Phase 3: Testing | 1 hour | Phase 2 |
| Code Review | 30 minutes | Phase 3 |
| Deployment | 30 minutes | Code Review |
| **Total** | **3.5-4 hours** | |

## Next Steps

1. Run `/sp.tasks` to generate detailed task breakdown
2. Implement tasks using agents/skills
3. Run test suite
4. Create pull request
5. Deploy to staging
6. Deploy to production

## References

- [FastAPI Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Feature Specification](./spec.md)
- [Research Document](./research.md)
- [Data Model](./data-model.md)
- [Quickstart Guide](./quickstart.md)

## Appendix: Code Examples

### Before (Broken)
```python
# Route handler
@router.post("/api/users/{user_id}/chat/messages")
async def send_message(user_id: str, request: ChatRequest):
    service = ChatKitService(get_session)  # WRONG: passing generator
    return await service.process_message(...)

# Service
class ChatKitService:
    def __init__(self, session_factory):
        self.session_factory = session_factory  # Generator
        self.thread_manager = ThreadManager(session_factory)  # WRONG

# Thread Manager
class ThreadManager:
    def __init__(self, session):
        self.session = session  # Actually a generator!

    def get_thread(self, user_id, thread_id):
        thread = self.session.get(Thread, thread_id)  # ERROR!
```

### After (Fixed)
```python
# Route handler
@router.post("/api/users/{user_id}/chat/messages")
async def send_message(
    user_id: str,
    request: ChatRequest,
    session: AsyncSession = Depends(get_session)  # CORRECT: inject session
):
    service = ChatKitService(session)  # CORRECT: pass resolved session
    return await service.process_message(...)

# Service
class ChatKitService:
    def __init__(self, session: AsyncSession):
        self.session = session  # Concrete session
        self.thread_manager = ThreadManager(session)  # CORRECT

# Thread Manager
class ThreadManager:
    def __init__(self, session: AsyncSession):
        self.session = session  # Concrete session

    async def get_thread(self, user_id, thread_id):
        result = await self.session.execute(...)  # CORRECT: works!
        return result.scalar_one_or_none()
```

---

**Plan Status**: ✅ Ready for Task Generation (`/sp.tasks`)
**Reviewed By**: Claude Sonnet 4.5
**Approved**: 2026-01-04
