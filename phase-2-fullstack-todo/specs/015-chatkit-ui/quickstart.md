# Quickstart Guide: ChatKit UI Implementation

**Feature**: 015-chatkit-ui
**Date**: 2025-12-31
**Target Audience**: Developers implementing the ChatKit UI feature

## Prerequisites

Before starting implementation, ensure you have:

- ✅ **Phase 0**: Research document reviewed and approved
- ✅ **Phase 1**: Data models and API contracts defined
- ✅ **Backend**: OpenAI Agents SDK and MCP Server implemented (Phase 3)
- ✅ **Authentication**: Better Auth with JWT configured
- ✅ **Environment**: Next.js 16+, TypeScript 5.3+, Tailwind CSS, FastAPI backend

## Implementation Overview

This guide provides a step-by-step approach to implementing the ChatKit UI feature. The implementation is divided into 5 main phases:

1. **Setup & Dependencies** - Install packages and configure environment
2. **Backend API** - Implement ChatKit session and thread endpoints
3. **Frontend Components** - Build chat interface with ChatKit React
4. **Integration** - Connect frontend to backend and test end-to-end
5. **Testing & Polish** - Write tests and refine UX

**Estimated Time**: 8-12 hours for full implementation

---

## Phase 1: Setup & Dependencies (30 min)

### 1.1 Install Frontend Dependencies

```bash
cd frontend
npm install @openai/chatkit-react@latest
```

**Verify Installation**:
```bash
npm list @openai/chatkit-react
# Expected output: @openai/chatkit-react@1.x.x
```

### 1.2 Install Backend Dependencies

```bash
cd backend
uv add openai  # For ChatKit session generation
```

**Verify Installation**:
```bash
uv pip list | grep openai
# Expected output: openai 1.x.x
```

### 1.3 Configure Environment Variables

**Frontend (.env.local)**:
```bash
# Add to existing .env.local
NEXT_PUBLIC_CHATKIT_ENABLED=true
```

**Backend (.env)**:
```bash
# Add to existing .env
OPENAI_API_KEY=your-openai-api-key-here
```

**Verify Environment**:
```bash
# Backend
cd backend && python -c "import os; print('OPENAI_API_KEY:', 'SET' if os.getenv('OPENAI_API_KEY') else 'MISSING')"

# Frontend
cd frontend && node -e "console.log('NEXT_PUBLIC_CHATKIT_ENABLED:', process.env.NEXT_PUBLIC_CHATKIT_ENABLED)"
```

---

## Phase 2: Backend API Implementation (2-3 hours)

### 2.1 Create Database Models

**File**: `backend/models.py` (add to existing file)

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4

class ChatKitSession(SQLModel, table=True):
    """ChatKit session tracking"""
    __tablename__ = "chatkit_sessions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False)
    client_secret_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    status: str = Field(default="active", max_length=20)

class ChatThread(SQLModel, table=True):
    """Chat thread metadata"""
    __tablename__ = "chat_threads"

    id: str = Field(primary_key=True, max_length=100)
    user_id: UUID = Field(foreign_key="users.id", nullable=False)
    name: str = Field(default="New Chat", max_length=100)
    last_message_preview: str | None = Field(default=None, max_length=200)
    message_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### 2.2 Create Pydantic Schemas

**File**: `backend/schemas/chatkit.py` (new file)

```python
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class SessionResponse(BaseModel):
    """ChatKit session response"""
    client_secret: str
    expires_at: datetime

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "client_secret": "cs_1234567890abcdef",
            "expires_at": "2025-12-31T23:59:59Z"
        }
    })

class ThreadSyncRequest(BaseModel):
    """Thread metadata sync request"""
    thread_id: str = Field(max_length=100)
    name: str = Field(max_length=100)
    last_message_preview: str | None = Field(default=None, max_length=200)
    message_count: int = Field(ge=0)

class ThreadItem(BaseModel):
    """Thread list item"""
    id: str
    name: str
    last_message_preview: str | None
    message_count: int
    created_at: datetime
    updated_at: datetime

class ThreadListResponse(BaseModel):
    """Thread list response"""
    threads: list[ThreadItem]
    total: int
```

### 2.3 Implement ChatKit Service

**File**: `backend/services/chatkit_service.py` (new file)

```python
from openai import OpenAI
from datetime import datetime, timedelta
from sqlmodel import Session
from models import ChatKitSession, ChatThread
from uuid import UUID
import hashlib

client = OpenAI()  # Uses OPENAI_API_KEY from environment

async def create_chatkit_session(user_id: UUID, session: Session) -> dict:
    """Generate ChatKit client secret for user"""
    # Generate client secret from OpenAI
    # Note: Implementation depends on OpenAI's ChatKit API
    # This is a placeholder - actual implementation will vary
    client_secret = f"cs_{user_id}_{datetime.utcnow().timestamp()}"

    expires_at = datetime.utcnow() + timedelta(hours=24)

    # Store session in database
    db_session = ChatKitSession(
        user_id=user_id,
        client_secret_hash=hashlib.sha256(client_secret.encode()).hexdigest(),
        expires_at=expires_at,
        status="active"
    )
    session.add(db_session)
    session.commit()

    return {
        "client_secret": client_secret,
        "expires_at": expires_at
    }

async def sync_thread(user_id: UUID, thread_data: dict, session: Session) -> ChatThread:
    """Sync thread metadata to database"""
    thread = session.get(ChatThread, thread_data["thread_id"])

    if thread:
        # Update existing thread
        thread.name = thread_data["name"]
        thread.last_message_preview = thread_data.get("last_message_preview")
        thread.message_count = thread_data["message_count"]
        thread.updated_at = datetime.utcnow()
    else:
        # Create new thread
        thread = ChatThread(
            id=thread_data["thread_id"],
            user_id=user_id,
            name=thread_data["name"],
            last_message_preview=thread_data.get("last_message_preview"),
            message_count=thread_data["message_count"]
        )
        session.add(thread)

    session.commit()
    session.refresh(thread)
    return thread
```

### 2.4 Create API Routes

**File**: `backend/routes/chatkit.py` (new file)

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from db import get_session
from middleware.auth_middleware import get_user_id_from_token
from schemas.chatkit import *
from services.chatkit_service import create_chatkit_session, sync_thread
from models import ChatThread
from uuid import UUID

router = APIRouter(prefix="/api", tags=["ChatKit"])

@router.post("/chatkit/session", response_model=SessionResponse)
async def create_session(
    current_user_id: str = Depends(get_user_id_from_token),
    session: Session = Depends(get_session)
):
    """Create ChatKit session and return client secret"""
    try:
        result = await create_chatkit_session(UUID(current_user_id), session)
        return SessionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@router.get("/users/{user_id}/chatkit/threads", response_model=ThreadListResponse)
async def list_threads(
    user_id: UUID,
    limit: int = 50,
    offset: int = 0,
    current_user_id: str = Depends(get_user_id_from_token),
    session: Session = Depends(get_session)
):
    """List user's chat threads"""
    if str(user_id) != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    query = select(ChatThread).where(ChatThread.user_id == user_id).offset(offset).limit(limit)
    threads = session.exec(query).all()

    total_query = select(ChatThread).where(ChatThread.user_id == user_id)
    total = len(session.exec(total_query).all())

    return ThreadListResponse(
        threads=[ThreadItem.model_validate(t) for t in threads],
        total=total
    )

@router.post("/users/{user_id}/chatkit/threads/{thread_id}/sync", response_model=ThreadItem)
async def sync_thread_endpoint(
    user_id: UUID,
    thread_id: str,
    thread_data: ThreadSyncRequest,
    current_user_id: str = Depends(get_user_id_from_token),
    session: Session = Depends(get_session)
):
    """Sync thread metadata"""
    if str(user_id) != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    thread = await sync_thread(user_id, thread_data.model_dump(), session)
    return ThreadItem.model_validate(thread)

@router.delete("/users/{user_id}/chatkit/threads/{thread_id}")
async def delete_thread(
    user_id: UUID,
    thread_id: str,
    current_user_id: str = Depends(get_user_id_from_token),
    session: Session = Depends(get_session)
):
    """Delete chat thread"""
    if str(user_id) != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    thread = session.get(ChatThread, thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    session.delete(thread)
    session.commit()

    return {"message": "Thread deleted successfully", "thread_id": thread_id}
```

### 2.5 Register Routes

**File**: `backend/main.py` (update existing file)

```python
# Add to existing imports
from routes import chatkit

# Add to existing app setup
app.include_router(chatkit.router)
```

**Test Backend Setup**:
```bash
cd backend
uv run uvicorn main:app --reload --port 8000
# Visit http://localhost:8000/docs to see new ChatKit endpoints
```

---

## Phase 3: Frontend Components (3-4 hours)

### 3.1 Create TypeScript Types

**File**: `frontend/types/chatkit.ts` (new file)

```typescript
export interface ChatSession {
  clientSecret: string;
  createdAt: Date;
  expiresAt: Date;
  status: 'initializing' | 'ready' | 'error' | 'expired';
  userId: string;
  error?: string;
}

export interface ChatThread {
  id: string;
  name: string;
  lastMessagePreview: string | null;
  lastUpdated: Date;
  messageCount: number;
  isActive: boolean;
  createdAt: Date;
  userId: string;
}

export interface ComposerTool {
  id: string;
  icon: string;
  label: string;
  shortLabel?: string;
  placeholderOverride?: string;
  enabled: boolean;
}

export const COMPOSER_TOOLS: ComposerTool[] = [
  {
    id: 'create_task',
    icon: 'plus',
    label: 'Create Task',
    shortLabel: 'Create',
    placeholderOverride: 'What would you like to add?',
    enabled: true,
  },
  {
    id: 'search_tasks',
    icon: 'search',
    label: 'Search Tasks',
    shortLabel: 'Search',
    placeholderOverride: 'Search by title or tag...',
    enabled: true,
  },
  {
    id: 'view_tasks',
    icon: 'list',
    label: 'View All Tasks',
    shortLabel: 'View',
    enabled: true,
  },
];
```

### 3.2 Create API Client Functions

**File**: `frontend/lib/chatkit-api.ts` (new file)

```typescript
import { getAuthToken } from './auth';

export async function getClientSecret(): Promise<string> {
  const token = await getAuthToken();

  const res = await fetch('/api/chatkit/session', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!res.ok) {
    throw new Error('Failed to get ChatKit client secret');
  }

  const { client_secret } = await res.json();
  return client_secret;
}

export async function fetchThreads(userId: string): Promise<any[]> {
  const token = await getAuthToken();

  const res = await fetch(`/api/users/${userId}/chatkit/threads`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    throw new Error('Failed to fetch threads');
  }

  const { threads } = await res.json();
  return threads;
}

export async function syncThread(userId: string, threadData: any): Promise<void> {
  const token = await getAuthToken();

  await fetch(`/api/users/${userId}/chatkit/threads/${threadData.thread_id}/sync`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(threadData),
  });
}
```

### 3.3 Create ChatInterface Component

**File**: `frontend/components/ChatInterface.tsx` (new file)

```tsx
'use client';

import { ChatKit, useChatKit } from '@openai/chatkit-react';
import { useState, useEffect } from 'react';
import { getClientSecret } from '@/lib/chatkit-api';
import { COMPOSER_TOOLS } from '@/types/chatkit';

export function ChatInterface() {
  const [isReady, setIsReady] = useState(false);
  const [isResponding, setIsResponding] = useState(false);
  const [currentThread, setCurrentThread] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const { control, setThreadId, focusComposer } = useChatKit({
    api: {
      getClientSecret: async () => {
        try {
          return await getClientSecret();
        } catch (err) {
          setError('Failed to initialize chat session');
          throw err;
        }
      },
    },
    composer: {
      tools: COMPOSER_TOOLS,
    },
    onReady: () => {
      setIsReady(true);
      const lastThread = localStorage.getItem('chatkit_last_thread');
      if (lastThread) {
        setThreadId(lastThread);
      }
    },
    onError: ({ error }) => {
      console.error('ChatKit error:', error);
      setError(error.message);
    },
    onThreadChange: ({ threadId }) => {
      setCurrentThread(threadId);
      localStorage.setItem('chatkit_last_thread', threadId);
    },
    onResponseStart: () => {
      setIsResponding(true);
    },
    onResponseEnd: () => {
      setIsResponding(false);
    },
  });

  if (error) {
    return (
      <div className="flex items-center justify-center h-[600px] bg-slate-900/50 rounded-lg border border-red-500/30">
        <div className="text-center">
          <p className="text-red-400 mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!isReady) {
    return (
      <div className="flex items-center justify-center h-[600px] bg-slate-900/50 rounded-lg border border-cyan-500/20">
        <div className="text-center">
          <div className="animate-spin w-8 h-8 border-4 border-cyan-500 border-t-transparent rounded-full mx-auto mb-4" />
          <p className="text-slate-400">Initializing chat...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative">
      {isResponding && (
        <div className="absolute top-4 left-1/2 -translate-x-1/2 z-10 px-4 py-2 bg-cyan-500/20 border border-cyan-500/30 rounded-full text-cyan-300 text-sm backdrop-blur-sm">
          AI is thinking...
        </div>
      )}

      <ChatKit
        control={control}
        className="h-[600px] w-full rounded-lg border border-cyan-500/20 shadow-lg shadow-cyan-500/10 bg-slate-900/80 backdrop-blur-sm"
        composerClassName="bg-slate-800/80 border-t border-cyan-500/30"
        messageClassName="prose prose-slate dark:prose-invert max-w-none"
      />
    </div>
  );
}
```

### 3.4 Create Chat Page

**File**: `frontend/app/chat/page.tsx` (new file)

```tsx
import { ChatInterface } from '@/components/ChatInterface';

export default function ChatPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-teal-400 mb-8">
          TaskWave AI Assistant
        </h1>

        <ChatInterface />
      </div>
    </div>
  );
}
```

---

## Phase 4: Integration & Testing (2-3 hours)

### 4.1 Run Database Migrations

```bash
cd backend
# Create migration for new tables
alembic revision --autogenerate -m "Add ChatKit tables"
alembic upgrade head
```

### 4.2 Start Development Servers

```bash
# Terminal 1: Backend
cd backend && uv run uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend && npm run dev
```

### 4.3 Manual Testing Checklist

- [ ] Navigate to http://localhost:3000/chat
- [ ] Verify chat interface loads without errors
- [ ] Send a test message: "Hello"
- [ ] Verify AI responds
- [ ] Click "Create Task" tool in composer
- [ ] Send message: "Add a task to buy groceries"
- [ ] Verify task is created (check /tasks page)
- [ ] Switch to new thread
- [ ] Verify previous thread persists in sidebar
- [ ] Reload page and verify last thread is restored

---

## Phase 5: Testing & Polish (1-2 hours)

### 5.1 Write Unit Tests

**File**: `backend/tests/test_chatkit.py` (new file)

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_session(auth_token):
    """Test ChatKit session creation"""
    response = client.post(
        "/api/chatkit/session",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 201
    assert "client_secret" in response.json()
    assert "expires_at" in response.json()

def test_list_threads(auth_token, user_id):
    """Test thread list retrieval"""
    response = client.get(
        f"/api/users/{user_id}/chatkit/threads",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert "threads" in response.json()
    assert "total" in response.json()
```

### 5.2 Refinements

- Add error boundaries for ChatKit component
- Implement thread search/filter in sidebar
- Add keyboard shortcuts (Ctrl+K for new thread)
- Optimize thread list rendering for 100+ threads
- Add loading skeleton for messages

---

## Troubleshooting

### Issue: "Failed to get ChatKit client secret"
- **Check**: OPENAI_API_KEY is set in backend .env
- **Check**: Better Auth JWT token is valid
- **Check**: Backend server is running on port 8000

### Issue: Chat interface doesn't load
- **Check**: @openai/chatkit-react is installed
- **Check**: Component has 'use client' directive
- **Check**: Browser console for JavaScript errors

### Issue: Thread not persisting
- **Check**: localStorage is enabled in browser
- **Check**: Backend /chatkit/threads endpoint is working
- **Check**: Thread sync is being called (check network tab)

---

## Next Steps

After completing this quickstart:

1. **Review**: Have another developer review the implementation
2. **Document**: Update README with ChatKit feature documentation
3. **Deploy**: Test in staging environment before production
4. **Monitor**: Set up logging and monitoring for ChatKit endpoints

---

## Related Files Reference

### Backend Files
- `backend/models.py` - ChatKitSession, ChatThread models
- `backend/schemas/chatkit.py` - Request/response schemas
- `backend/services/chatkit_service.py` - Business logic
- `backend/routes/chatkit.py` - API endpoints
- `backend/tests/test_chatkit.py` - Unit tests

### Frontend Files
- `frontend/types/chatkit.ts` - TypeScript types
- `frontend/lib/chatkit-api.ts` - API client functions
- `frontend/components/ChatInterface.tsx` - Main chat component
- `frontend/app/chat/page.tsx` - Chat page

### Agents & Skills to Use
- **Agent**: `chatkit-frontend-builder` - For building chat UI components
- **Skill**: `chatkit-react-components` - For ChatKit React patterns
- **Skill**: `frontend-api-client` - For API integration
- **Skill**: `fastapi-crud-endpoints` - For backend endpoints

---

**Quickstart Guide Version**: 1.0.0
**Last Updated**: 2025-12-31
**Maintained By**: TaskWave Development Team
