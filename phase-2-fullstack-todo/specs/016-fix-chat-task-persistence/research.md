# Research Findings: Fix Chat Task Persistence

**Feature**: 016-fix-chat-task-persistence
**Date**: 2026-01-05
**Status**: Complete

## Overview

This document consolidates research findings for fixing chat task persistence issues. Research focused on understanding correct API usage patterns, best practices, and identifying root causes of the reported bugs.

---

## R1: OpenAI Agents SDK ThreadManager API

### Decision
Use ThreadManager with proper parameter structure including required `content` field for all message operations.

### Research Findings

**Correct ThreadManager.add_message() Usage**:
```python
from openai import OpenAI
from openai.agents import Agent, ThreadManager

# Initialize thread manager
thread_manager = ThreadManager()

# CORRECT: Add message with all required parameters
thread_manager.add_message(
    role="user",           # Required: "user" or "assistant"
    content="message text", # Required: The actual message content
    metadata={}            # Optional: Additional metadata
)

# INCORRECT: Missing content parameter
thread_manager.add_message(role="user")  # ❌ Will raise TypeError
```

**Key Requirements**:
- `role`: Must be either "user" or "assistant"
- `content`: Required string containing the message text
- `metadata`: Optional dict for additional context

**Common Mistakes**:
1. Forgetting to pass `content` parameter
2. Passing empty string as content
3. Not handling exceptions when adding messages

### Rationale
The OpenAI Agents SDK requires explicit content for message tracking and context building. Without content, the agent cannot process or respond to messages.

### Alternatives Considered
- Using raw OpenAI API calls instead of ThreadManager
- Building custom message management
- **Rejected**: ThreadManager provides better integration with Agents SDK

### Implementation Impact
- Fix all ThreadManager.add_message() calls in chatkit_service.py
- Add validation to ensure content is never empty
- Add error handling for message addition failures

---

## R2: FastAPI SSE Streaming Best Practices

### Decision
Use proper SSE format with `data:` prefix and double newline separators, sending JSON-encoded chunks.

### Research Findings

**Correct SSE Format**:
```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import json

async def generate_sse_stream():
    # Each data chunk must follow SSE format
    yield f"data: {json.dumps({'content': 'Hello'})}\n\n"
    yield f"data: {json.dumps({'content': ' there'})}\n\n"
    yield f"data: {json.dumps({'content': '!'})}\n\n"

    # Event markers for special messages
    yield f"event: done\n"
    yield f"data: {json.dumps({'thread_id': 'abc123'})}\n\n"

@app.post("/chat/stream")
async def stream_chat():
    return StreamingResponse(
        generate_sse_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )
```

**SSE Format Rules**:
1. Each message starts with `data: `
2. Message ends with double newline `\n\n`
3. Event types use `event: <type>\n`
4. Comments use `: <comment>\n`

**Frontend Parsing**:
```typescript
const parseSSEChunk = (chunk: string): string => {
  const lines = chunk.split('\n');
  let content = '';

  for (const line of lines) {
    if (line.startsWith('data: ')) {
      try {
        const jsonStr = line.slice(6); // Remove "data: " prefix
        const data = JSON.parse(jsonStr);
        if (data.content) {
          content += data.content;
        }
      } catch (e) {
        console.warn('Failed to parse SSE data:', line);
      }
    }
  }

  return content;
};
```

### Rationale
SSE is a standard protocol for server-to-client streaming. Following the specification ensures compatibility with all browsers and prevents parsing errors.

### Alternatives Considered
- WebSockets for bidirectional communication
- Long polling with chunked responses
- **Rejected**: SSE is simpler for one-way streaming and has better browser support

### Implementation Impact
- Fix backend SSE generation to use proper format
- Update frontend SSE parser to handle format correctly
- Remove technical artifacts from user-facing display
- Add error handling for malformed SSE data

---

## R3: SQLModel Cascade Delete Configuration

### Decision
Configure CASCADE DELETE on foreign key relationships to automatically remove child records when parent is deleted.

### Research Findings

**Correct SQLModel Relationship Configuration**:
```python
from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime

class ChatThread(SQLModel, table=True):
    __tablename__ = "chat_threads"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    name: Optional[str] = Field(default=None, max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship with cascade delete
    messages: List["ChatMessage"] = Relationship(
        back_populates="thread",
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan",
            "passive_deletes": True
        }
    )

class ChatMessage(SQLModel, table=True):
    __tablename__ = "chat_messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    thread_id: UUID = Field(
        foreign_key="chat_threads.id",
        nullable=False,
        index=True,
        ondelete="CASCADE"  # Database-level cascade
    )
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    role: str = Field(max_length=20)
    content: str = Field(sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Relationship
    thread: ChatThread = Relationship(back_populates="messages")
```

**Key Configuration Options**:
- `cascade="all, delete-orphan"`: SQLAlchemy-level cascade
- `ondelete="CASCADE"`: Database-level cascade (PostgreSQL)
- `passive_deletes=True`: Let database handle cascades

**Database Migration**:
```sql
-- Verify existing constraint
SELECT constraint_name, delete_rule
FROM information_schema.referential_constraints
WHERE constraint_name LIKE '%chat_messages%thread%';

-- Recreate with CASCADE if needed
ALTER TABLE chat_messages
DROP CONSTRAINT IF EXISTS chat_messages_thread_id_fkey;

ALTER TABLE chat_messages
ADD CONSTRAINT chat_messages_thread_id_fkey
FOREIGN KEY (thread_id)
REFERENCES chat_threads(id)
ON DELETE CASCADE;
```

### Rationale
Cascade delete ensures data consistency by automatically removing orphaned messages when a thread is deleted. This prevents database bloat and maintains referential integrity.

### Alternatives Considered
- Manual deletion of child records before parent
- Soft delete (marking as deleted instead of removing)
- **Rejected**: Cascade delete is cleaner and prevents orphaned data

### Implementation Impact
- Verify/update SQLModel relationship configurations
- Run database migration to add CASCADE constraint
- Test thread deletion to ensure messages are removed
- Add transaction management for deletion operations

---

## R4: Frontend SSE Parsing Patterns

### Decision
Implement robust SSE parsing that handles chunked data, reconnection, and error cases.

### Research Findings

**Robust SSE Parser Implementation**:
```typescript
interface SSEMessage {
  content?: string;
  thread_id?: string;
  error?: string;
}

class SSEParser {
  private buffer: string = '';

  parseChunk(chunk: string): SSEMessage[] {
    this.buffer += chunk;
    const messages: SSEMessage[] = [];

    // Split by double newline (message separator)
    const parts = this.buffer.split('\n\n');

    // Keep last incomplete part in buffer
    this.buffer = parts.pop() || '';

    for (const part of parts) {
      const message = this.parseMessage(part);
      if (message) {
        messages.push(message);
      }
    }

    return messages;
  }

  private parseMessage(raw: string): SSEMessage | null {
    const lines = raw.split('\n');
    let data: string | null = null;
    let event: string | null = null;

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        data = line.slice(6);
      } else if (line.startsWith('event: ')) {
        event = line.slice(7);
      }
    }

    if (data) {
      try {
        return JSON.parse(data);
      } catch (e) {
        console.warn('Failed to parse SSE data:', data);
        return null;
      }
    }

    return null;
  }

  reset() {
    this.buffer = '';
  }
}

// Usage in component
const parser = new SSEParser();

const handleStream = async (response: Response) => {
  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value, { stream: true });
    const messages = parser.parseChunk(chunk);

    for (const msg of messages) {
      if (msg.content) {
        appendToDisplay(msg.content);
      }
      if (msg.thread_id) {
        setThreadId(msg.thread_id);
      }
    }
  }

  parser.reset();
};
```

**Error Handling**:
```typescript
try {
  const response = await fetch(url, {
    headers: { 'Accept': 'text/event-stream' }
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  if (!response.body) {
    throw new Error('No response body');
  }

  await handleStream(response);
} catch (error) {
  console.error('Stream error:', error);
  showError('Failed to receive response');
}
```

### Rationale
Proper SSE parsing handles edge cases like chunked data, incomplete messages, and network errors. This ensures reliable message display even with slow connections.

### Alternatives Considered
- Using EventSource API (limited POST support)
- Simple string splitting (fails with chunked data)
- **Rejected**: Custom parser provides better control and error handling

### Implementation Impact
- Replace existing SSE parser with robust implementation
- Add buffer management for incomplete chunks
- Add error handling for malformed data
- Test with various network conditions

---

## R5: Database Transaction Management in FastAPI

### Decision
Use async context managers with proper commit/rollback handling for all database operations.

### Research Findings

**Correct Transaction Pattern**:
```python
from sqlmodel.ext.asyncio.session import AsyncSession
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_session():
    async with AsyncSession(engine) as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Usage in service
class ChatService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_message(
        self,
        thread_id: UUID,
        user_id: UUID,
        role: str,
        content: str
    ) -> ChatMessage:
        """Save message with proper transaction management"""
        try:
            message = ChatMessage(
                thread_id=thread_id,
                user_id=user_id,
                role=role,
                content=content
            )
            self.session.add(message)
            await self.session.commit()
            await self.session.refresh(message)
            return message
        except Exception as e:
            await self.session.rollback()
            raise DatabaseError(f"Failed to save message: {str(e)}")

# Usage in endpoint
@router.post("/chat/messages")
async def send_message(
    message: MessageCreate,
    session: AsyncSession = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    chat_service = ChatService(session)

    # Save user message
    user_msg = await chat_service.save_message(
        thread_id=message.thread_id,
        user_id=user_id,
        role="user",
        content=message.content
    )

    # Process with agent...

    # Save assistant response
    assistant_msg = await chat_service.save_message(
        thread_id=message.thread_id,
        user_id=user_id,
        role="assistant",
        content=response_text
    )

    return {"message_id": assistant_msg.id}
```

**Key Principles**:
1. Always use try-except-finally for transactions
2. Commit after successful operations
3. Rollback on any exception
4. Close session in finally block
5. Use dependency injection for session management

### Rationale
Proper transaction management ensures data consistency and prevents partial writes. Rollback on errors maintains database integrity.

### Alternatives Considered
- Manual commit/rollback in each function
- Auto-commit mode (dangerous)
- **Rejected**: Context managers provide cleaner and safer transaction handling

### Implementation Impact
- Verify all database operations use proper transaction management
- Add rollback handling to all service methods
- Ensure sessions are properly closed
- Add database error handling and logging

---

## Summary of Key Findings

### Critical Fixes Required
1. **ThreadManager**: Add `content` parameter to all add_message() calls
2. **SSE Format**: Use proper `data: {json}\n\n` format in backend
3. **SSE Parsing**: Implement robust parser with buffer management in frontend
4. **Cascade Delete**: Configure ON DELETE CASCADE for thread-message relationship
5. **Transactions**: Use proper commit/rollback patterns for all database operations

### Best Practices Identified
- Always validate required parameters before API calls
- Use context managers for database sessions
- Implement proper error handling at all layers
- Test with edge cases (network errors, malformed data, concurrent operations)
- Add comprehensive logging for debugging

### Risk Mitigation
- Test all database migrations on staging first
- Add rollback procedures for each change
- Implement feature flags for gradual rollout
- Monitor error rates after deployment
- Have rollback plan ready for production

---

**Research Status**: Complete
**Next Phase**: Phase 1 - Design & Contracts
