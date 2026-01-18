# Research: ChatKit UI Implementation

**Feature**: 015-chatkit-ui
**Date**: 2025-12-31
**Research Phase**: Phase 0

## Research Objectives

This research phase resolves all technical unknowns identified in the Technical Context before proceeding to design. Key areas:

1. @openai/chatkit-react library integration patterns
2. Session management with JWT authentication
3. Thread persistence strategies
4. Composer tool menu configuration
5. Event handler implementation patterns
6. TaskWave theme integration approaches

## Research Findings

### 1. @openai/chatkit-react Integration

**Decision**: Use @openai/chatkit-react npm package with useChatKit hook pattern

**Rationale**:
- Official OpenAI library with React 19 compatibility
- Built-in support for session management, thread switching, and composer configuration
- Provides pre-built accessible UI components
- Handles WebSocket connections and reconnection logic automatically
- Integrates seamlessly with Next.js 16 App Router as Client Component

**Alternatives Considered**:
- **Custom WebSocket implementation**: Rejected due to complexity and need to rebuild features like threading, UI, and accessibility
- **OpenAI Chat API + custom UI**: Rejected because ChatKit provides optimized UI and handles state management

**Integration Pattern**:
```tsx
// Client Component for chat interface
'use client';
import { ChatKit, useChatKit } from '@openai/chatkit-react';

export function ChatInterface() {
  const { control } = useChatKit({
    api: { getClientSecret },
    onReady: handleReady,
    onError: handleError,
  });
  return <ChatKit control={control} />;
}
```

**Key Requirements**:
- Must be used as Client Component ('use client' directive)
- Requires Next.js 16+ with App Router
- TypeScript 5.3+ with strict mode enabled
- React 19+ for concurrent features

---

### 2. Session Management with JWT Authentication

**Decision**: Implement getClientSecret function that exchanges JWT for ChatKit session credentials

**Rationale**:
- ChatKit requires client secrets for secure session establishment
- Better Auth already provides JWT tokens for authenticated users
- Backend can validate JWT and issue ChatKit-compatible session tokens
- Maintains existing security model without introducing new auth system

**Architecture**:
```
Frontend (Next.js)        Backend (FastAPI)           ChatKit Backend
     |                           |                           |
     | 1. Has JWT token          |                           |
     |-------------------------->|                           |
     |  POST /api/chatkit/session|                           |
     |    { jwt: "Bearer ..." }  |                           |
     |                           |                           |
     |                           | 2. Validates JWT          |
     |                           | 3. Generates client_secret|
     |                           |-------------------------->|
     |                           |  (with OpenAI API)        |
     |                           |                           |
     | 4. Returns client_secret  |<--------------------------|
     |<--------------------------|                           |
     |                           |                           |
     | 5. Establishes chat session                           |
     |-------------------------------------------------------->|
```

**Implementation Pattern**:
```tsx
const getClientSecret = async () => {
  const token = await getAuthToken(); // From Better Auth
  const res = await fetch('/api/chatkit/session', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });
  const { client_secret } = await res.json();
  return client_secret;
};
```

**Security Considerations**:
- Client secrets are short-lived (configurable TTL)
- Backend validates JWT before issuing client secret
- User ID extracted from JWT ensures proper isolation
- Session refresh handled automatically by ChatKit

**Alternatives Considered**:
- **Public API keys**: Rejected due to security risks (exposes OpenAI API key)
- **Cookie-based sessions**: Rejected because ChatKit requires client secrets, not cookies

---

### 3. Thread Persistence Strategies

**Decision**: Hybrid approach using localStorage for immediate access and backend API for long-term persistence

**Rationale**:
- localStorage provides instant thread switching without network latency
- Backend persistence enables cross-device access and prevents data loss
- Hybrid approach balances performance with reliability
- Aligns with existing TaskWave architecture

**Persistence Flow**:
```
1. User switches thread → Update localStorage immediately
2. Background sync → POST /api/chatkit/threads/{threadId}/sync
3. On app load → Fetch threads from backend, populate localStorage
4. On thread list change → Sync to backend for persistence
```

**Data Structure (localStorage)**:
```typescript
interface ThreadMetadata {
  id: string;
  lastMessagePreview: string;
  lastUpdated: string;
  messageCount: number;
}

localStorage.setItem('chatkit_threads', JSON.stringify(threads));
localStorage.setItem('chatkit_last_thread', threadId);
```

**Backend API Endpoints**:
- `GET /api/users/{user_id}/chatkit/threads` - List user's threads
- `POST /api/users/{user_id}/chatkit/threads/{thread_id}/sync` - Sync thread metadata
- `DELETE /api/users/{user_id}/chatkit/threads/{thread_id}` - Delete thread

**Alternatives Considered**:
- **Backend-only persistence**: Rejected due to network latency on thread switching
- **localStorage-only**: Rejected because data lost on browser clear or device change
- **IndexedDB**: Rejected as overkill for simple thread metadata storage

---

### 4. Composer Tool Menu Configuration

**Decision**: Use ChatKit's built-in composer.tools configuration with predefined task operations

**Rationale**:
- ChatKit provides native tool menu UI in the composer
- Tools can trigger specific AI behaviors without typing commands
- Users see available actions visually in the composer toolbar
- Each tool can customize placeholder text for context

**Tool Configuration Pattern**:
```tsx
composer: {
  tools: [
    {
      id: "create_task",
      icon: "plus",
      label: "Create Task",
      shortLabel: "Create",
      placeholderOverride: "What would you like to add?",
    },
    {
      id: "search_tasks",
      icon: "search",
      label: "Search Tasks",
      shortLabel: "Search",
      placeholderOverride: "Search by title or tag...",
    },
    {
      id: "view_tasks",
      icon: "list",
      label: "View All Tasks",
      shortLabel: "View",
    },
  ],
}
```

**Backend Integration**:
- Tool IDs are sent with messages to backend
- Backend ChatKit endpoint routes to appropriate AI agent tools
- Agent uses MCP tools to perform actual operations
- Response includes task data for UI updates

**UX Benefits**:
- Reduces cognitive load (no need to remember commands)
- Visual discovery of capabilities
- Contextual placeholder text guides input
- Icons provide quick recognition

**Alternatives Considered**:
- **Custom button UI**: Rejected because reinvents ChatKit's native tool menu
- **Slash commands only**: Rejected as less discoverable than visual tool menu
- **Separate toolbar**: Rejected to avoid UI duplication

---

### 5. Event Handler Implementation Patterns

**Decision**: Use all ChatKit event handlers for comprehensive state management

**Rationale**:
- Events provide hooks into ChatKit's internal lifecycle
- Enable proper loading states and error handling
- Allow UI updates in response to chat events
- Support thread management and persistence

**Event Handlers Required**:

1. **onReady**: Chat session initialized
   ```tsx
   onReady: () => {
     setSessionReady(true);
     loadThreadList();
   }
   ```

2. **onError**: Handle connection/API errors
   ```tsx
   onError: ({ error }) => {
     console.error('ChatKit error:', error);
     showErrorToast(error.message);
   }
   ```

3. **onThreadChange**: Thread switched
   ```tsx
   onThreadChange: ({ threadId }) => {
     setCurrentThread(threadId);
     localStorage.setItem('lastThread', threadId);
     syncThreadToBackend(threadId);
   }
   ```

4. **onResponseStart**: AI begins responding
   ```tsx
   onResponseStart: () => {
     setIsResponding(true);
     setLoadingIndicator('AI is thinking...');
   }
   ```

5. **onResponseEnd**: AI completes response
   ```tsx
   onResponseEnd: () => {
     setIsResponding(false);
     clearLoadingIndicator();
   }
   ```

6. **onClientTool** (Optional): Handle client-side tool calls
   ```tsx
   onClientTool: async ({ name, params }) => {
     if (name === 'refresh_task_list') {
       await refetchTasks();
       return { success: true };
     }
   }
   ```

**State Management Pattern**:
```tsx
const [sessionReady, setSessionReady] = useState(false);
const [isResponding, setIsResponding] = useState(false);
const [currentThread, setCurrentThread] = useState<string | null>(null);
const [error, setError] = useState<string | null>(null);
```

**Alternatives Considered**:
- **Minimal event handling**: Rejected because lacks proper loading/error states
- **External state library (Redux/Zustand)**: Rejected as React hooks sufficient for this scope

---

### 6. TaskWave Theme Integration

**Decision**: Apply Tailwind CSS classes matching existing TaskWave design system

**Rationale**:
- ChatKit components accept className props for styling
- Tailwind provides utility classes for consistent theming
- TaskWave already uses teal-cyan gradients and wave animations
- Custom CSS can extend ChatKit's default styles

**Theme Variables (From Existing TaskWave)**:
```css
/* Existing TaskWave colors */
--primary: #06b6d4; /* cyan-500 */
--primary-dark: #0891b2; /* cyan-600 */
--primary-light: #22d3ee; /* cyan-400 */
--accent: #2dd4bf; /* teal-400 */
--background-light: #f0f9ff; /* sky-50 */
--background-dark: #0f172a; /* slate-900 */
--text-light: #1f2937; /* gray-800 */
--text-dark: #ffffff;
```

**ChatKit Component Styling**:
```tsx
<ChatKit
  control={control}
  className="h-[600px] w-full rounded-lg border border-cyan-500/20 shadow-lg shadow-cyan-500/10"
  composerClassName="bg-slate-900 border-t border-cyan-500/30"
  messageClassName="prose prose-slate dark:prose-invert"
/>
```

**Custom CSS for Wave Animation**:
```css
@keyframes wave {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}

.wave-animation {
  animation: wave 2s ease-in-out infinite;
}
```

**Dark Mode Support**:
- Use Tailwind's `dark:` variant for dark mode styles
- ChatKit respects system theme preferences
- TaskWave already has theme toggle implementation
- Apply theme-aware classes to ChatKit container

**Alternatives Considered**:
- **CSS modules**: Rejected for consistency with Tailwind-first approach
- **Styled-components**: Rejected to avoid runtime CSS-in-JS overhead
- **Custom design system**: Rejected because TaskWave theme already established

---

## Technology Stack Summary

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Chat UI Library | @openai/chatkit-react | Latest | Pre-built chat interface components |
| Framework | Next.js | 16+ | App Router for routing and SSR |
| Language | TypeScript | 5.3+ | Type safety and developer experience |
| Styling | Tailwind CSS | Latest | Utility-first styling matching TaskWave |
| State Management | React Hooks | 19+ | Local state for chat UI |
| Authentication | Better Auth (JWT) | Latest | User authentication and sessions |
| Backend Integration | FastAPI | Python 3.11+ | ChatKit session endpoint |
| AI Backend | OpenAI Agents SDK | Latest | Conversational AI logic |
| Tools | MCP Server | Latest | Task operation tools for AI agent |
| Storage (Local) | localStorage | Browser API | Thread metadata caching |
| Storage (Persistent) | PostgreSQL | Neon Serverless | Long-term thread persistence |

---

## Integration Points

### Frontend → Backend
- **POST /api/chatkit/session**: Exchange JWT for client secret
- **GET /api/users/{user_id}/chatkit/threads**: Fetch user's thread list
- **POST /api/users/{user_id}/chatkit/threads/{thread_id}/sync**: Sync thread metadata
- **DELETE /api/users/{user_id}/chatkit/threads/{thread_id}**: Delete thread

### ChatKit → OpenAI Backend
- Managed automatically by ChatKit library
- Uses client secret for authentication
- WebSocket connection for real-time messaging

### Backend → MCP Server
- Backend ChatKit endpoint calls MCP tools
- MCP tools perform task operations via existing FastAPI routes
- Response includes task data for AI to format

---

## Risk Assessment

### Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| ChatKit library breaking changes | High | Low | Pin version, monitor release notes |
| Session expiry during conversation | Medium | Medium | Implement auto-refresh in getClientSecret |
| localStorage cleared by user | Low | Medium | Sync to backend periodically |
| WebSocket connection failures | High | Low | ChatKit handles reconnection automatically |
| Thread sync conflicts | Medium | Low | Use optimistic updates with conflict resolution |

### Performance Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Large thread history slow loading | Medium | Medium | Implement pagination in thread list |
| Many concurrent users strain backend | High | Low | Implement rate limiting on ChatKit endpoint |
| localStorage quota exceeded | Low | Low | Limit threads cached, implement cleanup |

---

## Performance Targets

Based on specification success criteria:

- **Session Initialization**: < 2 seconds on 3G connection
- **Message Send**: < 500ms to show in UI
- **Thread Switch**: < 1 second including history load
- **AI Response Start**: < 1 second after message sent
- **Composer Interaction**: < 100ms for tool menu open
- **Thread List Load**: < 500ms for up to 100 threads

---

## Dependencies and Prerequisites

### External Dependencies (npm)
```json
{
  "@openai/chatkit-react": "^latest",
  "react": "^19.0.0",
  "react-dom": "^19.0.0",
  "next": "^16.0.0",
  "tailwindcss": "^latest"
}
```

### Backend Dependencies (Python/pip)
```toml
[dependencies]
openai = "^latest"      # For ChatKit session creation
fastapi = "^0.100.0"    # Existing
sqlmodel = "^latest"    # Existing
```

### Environment Variables Required
```bash
# Frontend (.env.local)
NEXT_PUBLIC_CHATKIT_ENABLED=true
BETTER_AUTH_SECRET=<shared-secret>

# Backend (.env)
OPENAI_API_KEY=<openai-api-key>
BETTER_AUTH_SECRET=<shared-secret>
DATABASE_URL=<neon-db-url>
```

### Prerequisite Features
- Better Auth JWT authentication (already implemented)
- Backend API endpoints for tasks (already implemented)
- MCP Server with task tools (already implemented in Phase 3)
- OpenAI Agents SDK integration (already implemented in Phase 3)

---

## Next Steps

Phase 0 research complete. All technical unknowns resolved. Proceed to:

1. **Phase 1**: Design data models and API contracts
2. **Phase 1**: Create quickstart implementation guide
3. **Phase 2**: Generate tasks.md with /sp.tasks command

---

**Research Completed**: 2025-12-31
**Reviewed By**: AI Architect
**Approved for Phase 1**: ✅
