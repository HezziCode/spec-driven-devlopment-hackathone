# Research: Database Session Management in FastAPI with SQLAlchemy

**Feature**: Fix Chat Message Loading Error (001-fix-chat-500-error)
**Date**: 2026-01-04
**Purpose**: Research proper database session management patterns for async FastAPI applications

## Problem Statement

The chat feature is failing with `AttributeError: 'generator' object has no attribute 'connect'` when attempting to query the database. The thread manager is receiving a generator object instead of a SQLAlchemy Session object, indicating improper session handling in async contexts.

## Research Questions

1. How should database sessions be managed in async FastAPI applications?
2. What is the proper pattern for dependency injection of database sessions?
3. How should sessions be passed to service layers and managers?
4. What are the best practices for session lifecycle management?

## Findings

### 1. FastAPI Database Session Dependency Pattern

**Decision**: Use FastAPI's dependency injection with async context managers

**Rationale**:
- FastAPI provides built-in dependency injection system via `Depends()`
- Async context managers ensure proper session lifecycle (creation, usage, cleanup)
- Dependencies are automatically resolved and injected into route handlers
- Sessions are automatically closed after request completion

**Pattern**:
```python
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

@app.post("/api/users/{user_id}/chat/messages")
async def send_message(
    user_id: str,
    session: AsyncSession = Depends(get_session)
):
    # session is properly injected and managed
    pass
```

**Alternatives Considered**:
- Manual session creation in each route (rejected: error-prone, no automatic cleanup)
- Global session object (rejected: not thread-safe, causes connection issues)
- Passing session factory instead of session (rejected: causes the generator error we're seeing)

### 2. Session Passing to Service Layers

**Decision**: Pass resolved Session objects (not factories or generators) to services

**Rationale**:
- Services should receive concrete Session objects, not generators
- The dependency injection system resolves the generator at the route level
- Services and managers should not be responsible for session lifecycle
- Clear separation of concerns: routes handle DI, services handle business logic

**Pattern**:
```python
# Route handler (receives session via DI)
async def send_message(
    session: AsyncSession = Depends(get_session)
):
    service = ChatKitService(session)  # Pass resolved session
    result = await service.process_message(...)
    return result

# Service (receives concrete session)
class ChatKitService:
    def __init__(self, session: AsyncSession):
        self.session = session  # Store concrete session

    async def process_message(self, ...):
        # Use self.session directly
        thread = await self.session.get(Thread, thread_id)
```

**Alternatives Considered**:
- Passing session factory to services (rejected: causes generator error)
- Creating new sessions in services (rejected: breaks transaction boundaries)
- Using global session (rejected: not async-safe)

### 3. Thread Manager Session Handling

**Decision**: Thread manager should receive Session objects via constructor or method parameters

**Rationale**:
- Thread manager is a utility class that performs database operations
- It should not manage session lifecycle (single responsibility principle)
- Sessions should be passed from the service layer
- This allows for proper transaction management at the service level

**Current Problem**:
```python
# WRONG: Passing generator/factory
thread_manager = ThreadManager(get_session)  # Returns generator
thread = thread_manager.get_thread(user_id, thread_id)  # Fails!

# CORRECT: Passing resolved session
session = await get_session()  # Resolve generator
thread_manager = ThreadManager(session)  # Pass concrete session
thread = thread_manager.get_thread(user_id, thread_id)  # Works!
```

**Pattern**:
```python
class ThreadManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    def get_thread(self, user_id: str, thread_id: str) -> Thread:
        # Use self.session directly (already resolved)
        thread = self.session.get(Thread, thread_id)
        return thread
```

### 4. Async vs Sync Session Operations

**Decision**: Use async session operations consistently throughout the stack

**Rationale**:
- FastAPI is async by default
- Mixing sync and async operations can cause blocking
- SQLAlchemy supports both sync and async sessions
- Async operations provide better performance under load

**Pattern**:
```python
# Async session operations
async def get_thread(self, user_id: str, thread_id: str) -> Thread:
    result = await self.session.execute(
        select(Thread).where(Thread.id == thread_id)
    )
    thread = result.scalar_one_or_none()
    return thread
```

**Note**: If using sync operations, ensure they're wrapped properly:
```python
# Sync operations in async context (if needed)
def get_thread_sync(self, user_id: str, thread_id: str) -> Thread:
    # session.get() is sync in SQLAlchemy
    thread = self.session.get(Thread, thread_id)
    return thread
```

### 5. Error Handling and Session Rollback

**Decision**: Implement proper error handling with automatic rollback

**Rationale**:
- Database errors should trigger session rollback
- FastAPI dependency system handles cleanup automatically
- Services should catch and log errors appropriately
- Failed operations should not leave database in inconsistent state

**Pattern**:
```python
async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()  # Commit on success
        except Exception:
            await session.rollback()  # Rollback on error
            raise
        finally:
            await session.close()  # Always close
```

## Implementation Recommendations

### 1. Fix Session Dependency Injection
- Ensure `get_session()` is an async generator that yields Session objects
- Use `Depends(get_session)` in all route handlers
- Never pass `get_session` directly to services (pass the resolved session)

### 2. Update Service Layer
- Modify `ChatKitService` to accept `AsyncSession` in constructor
- Store session as instance variable
- Pass session to thread manager and other utilities

### 3. Update Thread Manager
- Modify `ThreadManager` to accept `AsyncSession` in constructor
- Remove any session factory/generator handling
- Use `self.session` directly for all database operations

### 4. Update Route Handlers
- Inject session via `Depends(get_session)`
- Pass resolved session to service constructors
- Let FastAPI handle session lifecycle

### 5. Add Error Handling
- Wrap database operations in try-except blocks
- Log errors with sufficient context
- Return appropriate HTTP status codes (not 500 for expected errors)

## Testing Strategy

1. **Unit Tests**: Test thread manager with mock sessions
2. **Integration Tests**: Test full request flow with real database
3. **Error Tests**: Verify proper error handling and rollback
4. **Concurrency Tests**: Test multiple simultaneous requests

## References

- FastAPI Dependencies: https://fastapi.tiangolo.com/tutorial/dependencies/
- SQLAlchemy Async: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- FastAPI Database: https://fastapi.tiangolo.com/tutorial/sql-databases/

## Conclusion

The root cause is passing a session generator/factory to the thread manager instead of a resolved Session object. The fix requires:
1. Proper dependency injection at route level
2. Passing resolved sessions to services
3. Services passing sessions to utilities
4. Consistent async session usage throughout

This follows FastAPI best practices and ensures proper session lifecycle management.
