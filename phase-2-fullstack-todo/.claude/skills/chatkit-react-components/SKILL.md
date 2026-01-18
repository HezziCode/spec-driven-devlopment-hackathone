---
name: chatkit-react-components
description: Build chat interfaces using @openai/chatkit-react. Use when implementing chat UI, handling sessions, managing threads, configuring composer tools, or integrating with ChatKit backend.
---

# ChatKit React Components Skill

## Purpose
Build chat user interfaces using ChatKit React with proper session management, event handling, and multi-thread support.

## Pattern

### Basic ChatKit Component
```tsx
import { ChatKit, useChatKit } from '@openai/chatkit-react';

export function ChatInterface() {
  const { control } = useChatKit({
    api: {
      async getClientSecret(existing) {
        const res = await fetch('/api/chatkit/session', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        });
        const { client_secret } = await res.json();
        return client_secret;
      },
    },
    onReady: () => console.log('ChatKit ready'),
    onError: ({ error }) => console.error('ChatKit error:', error),
    onResponseStart: () => setIsLoading(true),
    onResponseEnd: () => setIsLoading(false),
    onThreadChange: ({ threadId }) => {
      setCurrentThread(threadId);
      localStorage.setItem('lastThread', threadId);
    },
  });

  return <ChatKit control={control} className="h-[600px] w-full" />;
}
```

### Composer with Tool Menu
```tsx
const { control } = useChatKit({
  api: { getClientSecret },
  composer: {
    tools: [
      {
        id: "create_task",
        icon: "plus",
        label: "Create Task",
        placeholderOverride: "Describe your task...",
      },
      {
        id: "search_tasks",
        icon: "search",
        label: "Search Tasks",
        shortLabel: "Search",
      },
      {
        id: "view_tasks",
        icon: "list",
        label: "View Tasks",
      },
    ],
  },
});
```

### Multi-Thread Management
```tsx
const {
  control,
  setThreadId,
  focusComposer,
} = useChatKit({
  api: { getClientSecret },
  initialThread: localStorage.getItem('lastThread'),
  onThreadChange: ({ threadId }) => {
    setCurrentThread(threadId);
    updateThreadList(threadId);
  },
});

const createNewThread = async () => {
  await setThreadId(null);
  await focusComposer();
};

const switchThread = async (threadId: string) => {
  await setThreadId(threadId);
};
```

### Client Tool Handler
```tsx
const { control } = useChatKit({
  api: { getClientSecret },
  onClientTool: async ({ name, params }) => {
    if (name === "refresh_task_list") {
      await refetchTasks();
      return { success: true };
    }
    if (name === "highlight_task") {
      highlightTaskInUI(params.taskId);
      return { highlighted: true };
    }
  },
});
```

## Key Principles
1. Session Management: Always implement getClientSecret for auth
2. Event Handlers: Use onResponseStart/End for loading states
3. Thread Persistence: Save thread ID to localStorage
4. Client Tools: Handle UI updates from backend events
5. Accessibility: ChatKit handles a11y, add custom labels as needed
```
