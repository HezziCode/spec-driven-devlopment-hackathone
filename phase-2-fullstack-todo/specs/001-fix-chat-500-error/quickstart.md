# Developer Quickstart: Fix Chat 500 Error

**Feature**: Fix Chat Message Loading Error (001-fix-chat-500-error)
**Date**: 2026-01-04
**Estimated Time**: 2-3 hours

## Problem Summary

Chat message sending fails with HTTP 500 error due to improper database session handling. The thread manager receives a generator object instead of a SQLAlchemy Session object.

**Error**: `AttributeError: 'generator' object has no attribute 'connect'`
**Location**: `backend/chatkit/thread_manager.py:55`

## Quick Fix Overview

1. Update session dependency injection in routes
2. Fix session passing in ChatKitService
3. Update ThreadManager to accept Session objects
4. Add proper error handling

## Prerequisites

- Backend server running (`uv run python -m uvicorn main:app --reload`)
- Database connection working
- Environment variables configured (`BETTER_AUTH_SECRET`, `DATABASE_URL`)

## Files to Modify

| File | Changes Required |
|------|------------------|
| `backend/routes/custom_chat.py` | Fix session injection in route handlers |
| `backend/services/chatkit_service.py` | Update to accept and pass Session objects |
| `backend/chatkit/thread_manager.py` | Update constructor to accept Session |
| `backend/chatkit/server.py` | Update to pass Session to thread manager |

## Step-by-Step Fix

### Step 1: Verify Session Dependency (5 min)

Check `backend/db.py` for session factory:

```python
# Should look like this:
async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

### Step 2: Fix Route Handler (10 min)

Update `backend/routes/custom_chat.py`:

```python
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from backend.db import get_session

@router.post("/api/users/{user_id}/chat/messages")
async def send_message(
    user_id: str,
    request: ChatRequest,
    session: AsyncSession = Depends(get_session)  # Inject session
):
    # Pass resolved session to service
    service = ChatKitService(session)
    result = await service.process_message(...)
    return result
```

### Step 3: Update ChatKitService (15 min)

Update `backend/services/chatkit_service.py`:

```python
from sqlalchemy.ext.asyncio import AsyncSession

class ChatKitService:
    def __init__(self, session: AsyncSession):
        self.session = session  # Store resolved session
        self.thread_manager = ThreadManager(session)  # Pass to manager

    async def process_message(self, user_id: str, thread_id: str, message: str):
        # Use self.session for database operations
        thread = await self.thread_manager.get_thread(user_id, thread_id)
        # ... rest of logic
```

### Step 4: Update ThreadManager (15 min)

Update `backend/chatkit/thread_manager.py`:

```python
from sqlalchemy.ext.asyncio import AsyncSession

class ThreadManager:
    def __init__(self, session: AsyncSession):
        self.session = session  # Store concrete session

    async def get_thread(self, user_id: str, thread_id: str) -> Thread:
        # Use self.session directly (no longer a generator)
        result = await self.session.execute(
            select(Thread)
            .where(Thread.id == thread_id)
            .where(Thread.user_id == user_id)
        )
        return result.scalar_one_or_none()
```

### Step 5: Update ChatKit Server (10 min)

Update `backend/chatkit/server.py`:

```python
class ChatKitServer:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.thread_manager = ThreadManager(session)  # Pass session

    async def respond(self, user_id: str, thread_id: str, message: str):
        # Use thread_manager with proper session
        thread = await self.thread_manager.get_thread(user_id, thread_id)
        # ... rest of logic
```

### Step 6: Add Error Handling (15 min)

Add try-except blocks in service and manager:

```python
async def get_thread(self, user_id: str, thread_id: str) -> Thread:
    try:
        result = await self.session.execute(...)
        thread = result.scalar_one_or_none()
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")
        return thread
    except SQLAlchemyError as e:
        logger.error(f"Database error getting thread: {e}")
        raise HTTPException(status_code=500, detail="Database error")
```

## Testing the Fix

### Manual Test (5 min)

1. Start backend server
2. Open frontend at `http://localhost:3000/chat`
3. Send a message
4. Verify no 500 error
5. Check backend logs for proper session initialization

### Expected Behavior

**Before Fix**:
```
ERROR - Unexpected chat error: 'generator' object has no attribute 'connect'
HTTP 500 Internal Server Error
```

**After Fix**:
```
INFO - ChatKitService initialized
INFO - Processing message for user {user_id}
INFO - Thread {thread_id} retrieved successfully
HTTP 200 OK
```

## Verification Checklist

- [ ] No more "generator object has no attribute connect" errors
- [ ] Messages send successfully without 500 errors
- [ ] Thread history loads correctly
- [ ] Backend logs show proper session initialization
- [ ] User isolation still enforced (users only see their threads)

## Common Issues

### Issue: Still getting generator error
**Solution**: Ensure you're passing the resolved session, not `get_session` function

### Issue: Session closed prematurely
**Solution**: Don't call `session.close()` manually - let FastAPI dependency handle it

### Issue: Async/await errors
**Solution**: Ensure all session operations use `await` keyword

## Rollback Plan

If fix causes issues:
1. Revert changes to affected files
2. Restart backend server
3. Check git diff to see what changed
4. Review error logs for new issues

## Performance Notes

- Session injection adds minimal overhead (~1ms)
- Proper session management improves connection pooling
- No performance degradation expected

## Next Steps After Fix

1. Run full test suite
2. Test concurrent message sending
3. Monitor error logs for 24 hours
4. Update documentation if needed

## Support

If issues persist:
- Check backend logs: `backend/logs/app.log`
- Verify database connection: `psql $DATABASE_URL`
- Test session factory: `python -c "from backend.db import get_session; print(get_session)"`

## Estimated Timeline

| Task | Time |
|------|------|
| Verify session dependency | 5 min |
| Fix route handler | 10 min |
| Update ChatKitService | 15 min |
| Update ThreadManager | 15 min |
| Update ChatKit Server | 10 min |
| Add error handling | 15 min |
| Testing | 15 min |
| **Total** | **85 min (~1.5 hours)** |

## Success Criteria

✅ Chat messages send without 500 errors
✅ Thread history loads correctly
✅ Backend logs show proper session usage
✅ No generator-related errors in logs
✅ User isolation maintained
