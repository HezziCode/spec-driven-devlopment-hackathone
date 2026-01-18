# Quickstart Guide: Fix Chat Thread and API Key Errors

**Feature**: Fix Chat Thread and API Key Errors
**Date**: 2026-01-13
**Author**: Claude Code

## Overview

This guide provides step-by-step instructions to implement fixes for two critical errors in the chat functionality:
1. HTTP 404 errors when loading chat threads due to timing issues
2. HTTP 401 API authentication errors when connecting to OpenAI services

## Prerequisites

- Python 3.13 with uv package manager
- Node.js 18+ with npm
- Valid OpenAI API key
- PostgreSQL database (Neon)
- Git for version control

## Environment Setup

### 1. Backend Setup
```bash
cd backend/
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync
```

### 2. Environment Variables
Create/update `.env` file in backend directory:
```env
DATABASE_URL=postgresql://user:password@host/database
BETTER_AUTH_SECRET=your-32-character-secret
OPENAI_API_KEY=your-valid-openai-api-key
FRONTEND_URL=http://localhost:3000
```

### 3. Frontend Setup
```bash
cd frontend/
npm install
```

## Implementation Steps

### Step 1: Fix Database Synchronization (Backend)

**File**: `backend/services/chatkit_service.py`

**Changes**:
1. Add proper database synchronization after thread creation
2. Implement `session.commit()` and `session.expire_all()` calls
3. Add small delay after thread creation for database visibility

```python
# In create_thread method:
def _create_thread(self, user_id: str) -> ChatThread:
    # ... existing code ...

    # Add proper synchronization
    self.session.add(thread)
    self.session.commit()  # Commit the transaction
    self.session.refresh(thread)  # Refresh to get the actual database record
    self.session.expire_all()  # Expire all objects to ensure visibility

    # Small delay to ensure database propagation
    import time
    time.sleep(0.1)  # 100ms delay

    return thread
```

### Step 2: Fix OpenAI API Key Configuration (Backend)

**File**: `backend/main.py`

**Changes**:
1. Update OpenAI configuration to use proper SDK functions
2. Ensure API key is available for both startup and runtime

```python
# In lifespan function:
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ... existing code ...

    # Configure OpenAI API key properly
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        # Set the API key for the OpenAI library
        openai.api_key = openai_api_key

        # Configure the agents package with the API key
        try:
            from agents import set_default_openai_api, set_default_openai_client
            from openai import OpenAI

            # Set default API key for agents
            set_default_openai_api(openai_api_key)

            # Set custom client for agents
            client = OpenAI(api_key=openai_api_key)
            set_default_openai_client(client)

            # Disable tracing to prevent 401 errors on tracing endpoints
            os.environ["OPENAI_AGENTS_DISABLE_TRACING"] = "1"

            logger.info("OpenAI API key configured successfully for agents package")
        except ImportError as e:
            logger.warning(f"Agents package functions not available: {e}")
            os.environ["OPENAI_API_KEY"] = openai_api_key
        except Exception as e:
            logger.error(f"Failed to configure agents package with API key: {e}")
            os.environ["OPENAI_API_KEY"] = openai_api_key
    else:
        logger.warning("OPENAI_API_KEY not found in environment variables")

    # ... rest of function ...
```

### Step 3: Enhance Frontend Error Handling (Frontend)

**File**: `frontend/components/CustomChatInterface.tsx`

**Changes**:
1. Improve retry logic for thread loading
2. Add proper handling for invalid thread IDs
3. Clear invalid thread IDs from local storage

```typescript
// Add retry function with exponential backoff
const loadWithRetry = async (threadId: string, maxRetries: number = 3) => {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/users/${userId}/chat/threads/${threadId}`);

      if (response.status === 404) {
        console.log(`Thread ${threadId} not found, retrying in ${attempt * 100}ms (attempt ${attempt}/${maxRetries})`);

        if (attempt === maxRetries) {
          // Clear invalid thread ID from local storage
          localStorage.removeItem('currentThreadId');
          setCurrentThreadId(null);
          setError('Thread not found. Please start a new conversation.');
          return;
        }

        // Wait before retrying
        await new Promise(resolve => setTimeout(resolve, attempt * 100));
        continue;
      }

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setThreadMessages(data.messages || []);
      setThreadInfo(data);
      break; // Success, exit retry loop
    } catch (err) {
      console.error('Error loading thread messages:', err);
      setError('Failed to load thread messages');
    }
  }
};
```

### Step 4: Update SSE Error Handling (Frontend)

**File**: `frontend/lib/sse-parser.ts`

**Changes**:
1. Add support for thread_created events
2. Properly parse threadId from metadata
3. Handle error events appropriately

```typescript
// Add thread_created event type
export type SSEEventType = 'text_delta' | 'error' | 'done' | 'thread_created';

// Update parseSSEEvents to handle thread_created
export async function* parseSSEEvents(reader: ReadableStreamDefaultReader<Uint8Array>) {
  // ... existing code ...

  if (eventLine.startsWith('event:')) {
    eventType = eventLine.substring(6).trim() as SSEEventType;
  }

  if (dataLine.startsWith('data:')) {
    const jsonData = dataLine.substring(5).trim();

    switch (eventType) {
      case 'thread_created':
        yield {
          content: '',
          isComplete: true,
          eventType: 'thread_created',
          metadata: JSON.parse(jsonData) as { threadId: string }
        };
        break;
      // ... other cases ...
    }
  }
}
```

### Step 5: Update SSE Type Definitions (Frontend)

**File**: `frontend/types/sse.ts`

**Changes**:
1. Add thread_created event type
2. Update SSEEvent interface to include metadata

```typescript
export type SSEEventType = 'text_delta' | 'error' | 'done' | 'thread_created';

export interface SSEEvent {
  content: string;
  isComplete: boolean;
  eventType: SSEEventType;
  metadata?: {
    threadId?: string;
  };
}
```

## Testing the Fixes

### 1. Test Thread Creation and Access
1. Start both servers:
   ```bash
   # Terminal 1 - Backend
   cd backend/
   uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload

   # Terminal 2 - Frontend
   cd frontend/
   npm run dev
   ```
2. Navigate to the chat interface
3. Create a new thread
4. Verify the thread is immediately accessible without 404 errors

### 2. Test OpenAI Integration
1. Send a message to the AI assistant
2. Verify that responses are received without 401 authentication errors
3. Check that the SSE connection remains stable

### 3. Test Error Scenarios
1. Try to access a non-existent thread ID
2. Verify that the frontend handles the 404 error gracefully
3. Verify that invalid thread IDs are cleared from local storage

## Verification Checklist

- [ ] HTTP 404 errors eliminated when accessing threads
- [ ] HTTP 401 API authentication errors resolved
- [ ] Thread creation followed by immediate access works consistently
- [ ] SSE connections remain stable during chat sessions
- [ ] Frontend properly handles thread not found scenarios
- [ ] OpenAI API key is properly configured for runtime usage
- [ ] Database synchronization prevents race conditions
- [ ] Retry logic works for temporary connection issues

## Troubleshooting

### Issue: 404 errors still occurring
**Solution**: Check that database synchronization is properly implemented with `session.commit()` and `session.expire_all()` calls.

### Issue: 401 API authentication errors persist
**Solution**: Verify that OpenAI API key is set in environment variables and that `set_default_openai_api()` is called during application startup.

### Issue: SSE connections unstable
**Solution**: Ensure proper headers are set in the SSE endpoint and error handling is implemented for all event types.

## Performance Considerations

- Keep synchronization delays minimal (under 200ms)
- Implement efficient database queries with proper indexing
- Use appropriate retry intervals to avoid overwhelming the server
- Monitor API response times to ensure performance goals are met

## Next Steps

1. Deploy the fixes to the staging environment
2. Perform load testing to verify performance under concurrent users
3. Monitor error rates in production to ensure issues are resolved
4. Implement additional monitoring for thread creation and access patterns