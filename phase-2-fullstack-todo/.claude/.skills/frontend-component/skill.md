# Frontend Component Skill

## Purpose
Create Next.js server/client components following best practices for data fetching, interactivity, authentication, styling, and accessibility.

## Pattern
### Server Component (Default)
```tsx
// app/tasks/page.tsx
import { getTasks } from '@/lib/api';
import { TaskList } from '@/components/task/task-list';

interface TasksPageProps {
  searchParams: {
    filter?: string;
    sort?: string;
  };
}

export default async function TasksPage({ searchParams }: TasksPageProps) {
  const { filter, sort } = searchParams;
  const tasks = await getTasks(filter, sort);

  return (
    <div className="container mx-auto py-8">
      <TaskList tasks={tasks} />
    </div>
  );
}
```

### Client Component (For Interactivity)
```tsx
// components/task/task-form.tsx
'use client';

import { useState } from 'react';
import { createTask } from '@/lib/api';
import { TaskSchema } from '@/lib/types';

export function TaskForm() {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      await createTask({ title, description });
      setTitle('');
      setDescription('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create task');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="title" className="block text-sm font-medium mb-1">
          Title
        </label>
        <input
          id="title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          aria-required="true"
          disabled={isLoading}
        />
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium mb-1">
          Description
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          aria-required="false"
          disabled={isLoading}
        />
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        aria-busy={isLoading}
      >
        {isLoading ? 'Creating...' : 'Create Task'}
      </button>

      {error && (
        <div
          className="p-3 bg-red-100 text-red-700 rounded-md"
          role="alert"
          aria-live="polite"
        >
          {error}
        </div>
      )}
    </form>
  );
}
```

### Protected Route Component
```tsx
// components/auth/protected-route.tsx
'use client';

import { useAuth } from 'use-better-auth/react';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ReactNode } from 'react';

interface ProtectedRouteProps {
  children: ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { session } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!session?.data?.user && !session.isLoading) {
      router.push('/auth/login');
    }
  }, [session, router]);

  if (!session?.data?.user && !session.isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p className="text-lg">Redirecting to login...</p>
      </div>
    );
  }

  return <>{children}</>;
}
```

## Key Components
1. **Server Components**: Default for data fetching and initial rendering
2. **Client Components**: Use 'use client' directive for interactivity
3. **Protected Routes**: Authentication wrapper for protected content
4. **Tailwind Styling**: Utility-first CSS approach with consistent classes
5. **Suspense Loading**: For async data fetching with loading states
6. **Accessibility**: ARIA attributes, keyboard navigation, semantic HTML
7. **Error Handling**: Proper error boundaries and user feedback

## API Integration
- All API calls must go through centralized API client in `/lib/api.ts`
- API client automatically attaches JWT tokens from auth context
- Proper error handling with loading and error states
- Type-safe API calls with TypeScript

## Security Considerations
- Never expose sensitive data in client-side code
- Validate JWT tokens on the client side for UX (server validation remains primary)
- Sanitize user inputs before sending to API
- Implement proper error masking to avoid information disclosure

## Performance Considerations
- Use React.Suspense for code splitting
- Implement proper loading and error states
- Optimize bundle size with proper imports
- Use React.memo for components that render frequently
- Implement proper caching strategies

## Accessibility Requirements (WCAG 2.1 AA)
- Proper semantic HTML structure
- ARIA labels for interactive elements
- Keyboard navigation support
- Sufficient color contrast ratios
- Screen reader compatibility
- Focus management for dynamic content
- Proper labeling of form elements

## MCP Integration
If the specification mentions multi-agent communication or cloud-native tools, this skill should be extended to:
- Include WebSocket integration for real-time updates
- Add event tracking for user interactions
- Implement feature flag components for A/B testing
- Include configuration for multi-cloud deployment scenarios

## Common Variations
- Data tables with sorting and pagination
- Form components with validation
- Modal dialogs with proper focus management
- Navigation components with active state tracking
- Loading skeletons for better UX
- Infinite scroll components for large datasets

## Validation Checklist
- [ ] Server components used by default for data fetching
- [ ] 'use client' directive added when interactivity is needed
- [ ] Protected routes implemented for authentication
- [ ] Tailwind classes used exclusively for styling
- [ ] Proper ARIA attributes and accessibility features
- [ ] Suspense boundaries for async operations
- [ ] Error boundaries for graceful error handling
- [ ] TypeScript type safety maintained
- [ ] Keyboard navigation support implemented
- [ ] Proper loading and error states