---
id: 1
title: Chatkit Frontend Backend Integration
stage: spec
date: 2026-01-01
surface: agent
model: claude-sonnet-4-5-20250929
feature: 017-chatkit-integration
branch: 017-chatkit-integration
user: claude
command: sp.specify
labels: [chatkit, integration, ai, frontend, backend]
links:
  spec: ../spec.md
  ticket: null
  adr: null
  pr: null
files:
- specs/017-chatkit-integration/spec.md
- specs/017-chatkit-integration/checklists/requirements.md
tests:
- null
---

## Prompt

sp.specify "Integrate the existing ChatKit React frontend with the new AI backend to enable actual intelligent conversations.

CURRENT STATE:
- ChatInterface component exists using @openai/chatkit-react
- Session management and authentication working
- Thread switching and persistence working
- BUT: No actual AI responses (backend wasn't connected properly)

WHAT TO FIX/ADD:

1. UPDATE CHATKIT CONFIGURATION:
In ChatInterface component, update useChatKit hook:
- api.getClientSecret: Should call POST /api/chatkit/session
- Endpoint should return JWT token for authentication
- Update base URL to point to new ChatKit endpoint

2. IMPLEMENT onClientEffect HANDLER:
Add handler to respond to backend events:
```typescript
onClientEffect: async ({ name, data }) => {
  if (name === 'task_created') {
    // Refresh task list in TaskList component
    await refetchTasks();
    // Show success toast
    showToast('Task created successfully');
  }
  if (name === 'task_updated') {
    // Update specific task in UI
    updateTaskInList(data.task);
  }
  if (name === 'task_deleted') {
    // Remove from task list
    removeTaskFromList(data.taskId);
  }
  if (name === 'task_completed') {
    // Toggle completion in UI
    toggleTaskCompletion(data.taskId);
  }
}
```

3. ADD TASK LIST SYNCHRONIZATION:
- Import TaskList context or state management
- Connect chat events to task list updates
- Implement optimistic updates with rollback on error
- Show loading states during operations

4. ENHANCE COMPOSER:
Update composer configuration with contextual tools:
```typescript
composer: {
  tools: [
    { id: 'create_task', icon: 'plus', label: 'Create Task' },
    { id: 'search_tasks', icon: 'search', label: 'Search Tasks' },
    { id: 'list_tasks', icon: 'list', label: 'View All Tasks' },
    { id: 'analytics', icon: 'bar-chart', label: 'Statistics' }
  ],
  placeholder: 'Ask me to create, search, or manage your tasks...'
}
```

5. ADD EXAMPLE PROMPTS:
Show example prompts when chat is empty:
- 'Create a task for my meeting tomorrow'
- 'Show me all urgent tasks'
- 'What tasks do I have this week?'
- 'Mark my report task as complete'

6. IMPROVE ERROR HANDLING:
```typescript
onError: ({ error }) => {
  console.error('Chat error:', error);
  if (error.code === 'AUTHENTICATION_FAILED') {
    // Redirect to login
    router.push('/login');
  } else if (error.code === 'RATE_LIMIT') {
    showToast('Too many requests. Please wait a moment.');
  } else {
    showToast('Something went wrong. Please try again.');
  }
}
```

7. ADD LOADING INDICATORS:
- Show 'AI is thinking...' during agent processing
- Show tool-specific loading ('Creating task...', 'Searching...')
- Animate message appearance
- Add typing indicators

8. IMPLEMENT SESSION ENDPOINT:
Create /api/chatkit/session endpoint in backend:
```python
@app.post('/api/chatkit/session')
async def create_chat_session(current_user: User = Depends(get_current_user)):
    # Generate session token (JWT)
    token = create_access_token(data={'sub': current_user.id})
    return {'client_secret': token}
```

9. ADD CHAT BUTTON IMPROVEMENTS:
For the floating chat button on landing page:
- Add unread message indicator
- Add animation when AI is processing
- Show last message preview on hover
- Add keyboard shortcut (Ctrl+K)

10. INTEGRATE WITH TASK PAGE:
When on /tasks page:
- Show chat button that opens chat sidebar
- Sync task list automatically with chat operations
- Highlight tasks mentioned in chat
- Enable quick actions from chat

FILE LOCATIONS TO UPDATE:
- frontend/components/chat/ChatInterface.tsx
- frontend/components/chat/ChatButton.tsx (floating button)
- frontend/app/chat/page.tsx (full chat page)
- frontend/lib/api/chatkit.ts (API client)
- backend/routes/chatkit.py (session endpoint)

ENVIRONMENT VARIABLES:
Frontend (.env.local):
- NEXT_PUBLIC_CHATKIT_URL=http://localhost:8000/api/chatkit

Backend (.env):
- Already configured in Phase 2

TESTING CHECKLIST:
- [ ] Can send message and get AI response
- [ ] Task creation from chat works
- [ ] Task list updates automatically
- [ ] Thread persistence works
- [ ] Authentication errors handled
- [ ] Loading states show correctly
- [ ] Client effects trigger UI updates
- [ ] Error messages are user-friendly
- [ ] Works on both landing page and /chat page
- [ ] Mobile responsive

OUTPUT:
- Fully working AI chat integrated with task management
- Real-time task list synchronization
- Proper error handling and loading states
- Enhanced UX with examples and indicators"

--- if this work is already implementeed then just update code as per requriment

## Response snapshot

Created a comprehensive specification for integrating the existing ChatKit React frontend with the AI backend to enable actual intelligent conversations. The specification includes:

- 5 user stories with acceptance scenarios covering core functionality
- 15 functional requirements defining the integration points
- 4 key entities describing the main concepts
- 10 measurable success criteria with specific metrics
- 7 edge cases for robustness
- Quality checklist confirming the specification is ready for planning

The specification addresses the core issue that while the ChatKit UI components exist, they're not properly connected to the AI backend for actual intelligent responses. The spec defines how to establish proper session authentication, implement client effect handlers for UI synchronization, enhance the composer with contextual tools, and provide proper loading states and error handling.

## Outcome

- ✅ Impact: Complete specification for ChatKit frontend-backend integration
- 🧪 Tests: N/A - this is a specification phase
- 📁 Files: Created spec.md and requirements.md checklists
- 🔁 Next prompts: Ready for /sp.clarify or /sp.plan
- 🧠 Reflection: Specification addresses the gap between existing UI and backend AI functionality

## Evaluation notes (flywheel)

- Failure modes observed: None - specification is complete and well-structured
- Graders run and results (PASS/FAIL): All checklist items pass validation
- Prompt variant (if applicable): Standard feature specification workflow
- Next experiment (smallest change to try): Proceed to planning phase to design implementation