# Frontend CLAUDE.md: Guidelines for Next.js Frontend in Phase 2 Todo Web App

This file provides specific guidelines for developing the frontend of the Phase 2 Full-Stack Todo Web App using Next.js 16+, TypeScript, and Tailwind CSS.

## Technology Stack
- **Framework**: Next.js 16+ with App Router
- **Language**: TypeScript (strict mode enabled)
- **Styling**: Tailwind CSS (no inline styles)
- **Authentication**: Better Auth with JWT plugin
- **API Client**: Custom API client in `/lib/api.ts` with JWT token attachment

## Project Structure
```
/frontend/
├── /app/                 # Next.js App Router pages
│   ├── /api/             # Client-side API routes (if needed)
│   ├── /auth/            # Authentication pages (login, register)
│   ├── /dashboard/       # Main dashboard page
│   ├── /tasks/           # Task management pages
│   └── layout.tsx        # Root layout
│   └── page.tsx          # Home page
├── /components/          # Reusable UI components
│   ├── /ui/              # Base UI components (buttons, inputs, etc.)
│   ├── /forms/           # Form components
│   └── /layout/          # Layout components
├── /lib/                 # Utility functions and API client
│   ├── api.ts            # API client with JWT handling
│   └── types.ts          # Shared TypeScript types
├── /hooks/               # Custom React hooks
├── /styles/              # Global styles (if any beyond Tailwind)
├── /public/              # Static assets
└── next.config.js        # Next.js configuration
```

## Component Patterns
### Server Components (Default)
- Use server components as the default for data fetching and initial rendering
- Server components should fetch data directly from API routes or services
- Server components are better for SEO and initial page load performance
- Example: `async function TaskList({ userId }: { userId: string })`

### Client Components (For Interactivity)
- Use client components only when interactivity is required (events, state, effects)
- Add `'use client'` directive at the top of client components
- Example: `use client` for components with useState, useEffect, event handlers

### API Integration
- All API calls must go through the centralized API client in `/lib/api.ts`
- API client must automatically attach JWT tokens from auth context
- API client should handle common error scenarios and token refresh

## Styling Guidelines
- Use Tailwind CSS classes exclusively (no inline styles)
- Follow consistent design system with Tailwind configuration
- Use utility-first approach for styling
- Create reusable component classes in the `/components/ui/` directory
- No custom CSS files unless absolutely necessary

## Authentication Implementation
- Configure Better Auth with JWT plugin for frontend authentication
- Implement JWT token storage and retrieval (preferably in httpOnly cookies)
- Create auth context/provider to manage authentication state
- Protect routes that require authentication
- Implement token refresh mechanism

## File Naming Conventions
- Use PascalCase for React components: `TaskItem.tsx`, `TaskForm.tsx`
- Use camelCase for utility functions: `apiClient.ts`, `utils.ts`
- Use kebab-case for folder names: `task-list`, `auth-pages`
- Component files should match component names: `Button.tsx` contains `Button` component

## TypeScript Best Practices
- Use strict TypeScript mode with no implicit any
- Create shared types in `/lib/types.ts`
- Use TypeScript interfaces for component props
- Implement proper error handling with TypeScript error types
- Avoid using `any` type - create proper type definitions

## Component Architecture
### Base UI Components (`/components/ui/`)
- Create base components for common UI elements (Button, Input, Card, etc.)
- These should be highly reusable and customizable via props
- Follow accessibility best practices (ARIA attributes, keyboard navigation)

### Feature Components (`/components/`)
- Create feature-specific components that compose base UI components
- These components implement specific functionality (TaskList, TaskForm, etc.)

### Layout Components (`/components/layout/`)
- Create layout components for consistent page structure
- Include header, navigation, sidebar, footer components

## API Client Implementation
- Centralized API client in `/lib/api.ts`
- Automatic JWT token attachment to requests
- Error handling and retry logic
- Type-safe API calls with proper response typing
- Support for GET, POST, PUT, DELETE operations

## Development Workflow
1. Create shared types in `/lib/types.ts`
2. Implement base UI components in `/components/ui/`
3. Create API client in `/lib/api.ts`
4. Build feature components using base components and API client
5. Create pages in `/app/` using feature components
6. Add authentication layer with Better Auth
7. Test with comprehensive component and integration tests

## Testing Guidelines
- Component testing with Jest and React Testing Library
- Integration tests for API client functionality
- End-to-end tests for critical user flows
- Accessibility testing for WCAG 2.1 AA compliance

## Performance Considerations
- Use Next.js Image component for optimized images
- Implement proper loading and error states
- Use React.Suspense for code splitting
- Optimize bundle size with proper imports
- Implement proper caching strategies

## Security Guidelines
- Sanitize user inputs before sending to API
- Validate JWT tokens on the client side (for UX, server validation remains primary)
- Never expose sensitive data in client-side code
- Use HTTPS for all API communications
- Implement proper error masking to avoid information disclosure

## Accessibility Requirements (WCAG 2.1 AA)
- Proper semantic HTML structure
- ARIA labels for interactive elements
- Keyboard navigation support
- Sufficient color contrast ratios
- Screen reader compatibility
- Focus management for dynamic content

## Error Handling
- Implement global error boundary for unexpected errors
- Create specific error components for different error types
- Provide user-friendly error messages
- Implement graceful degradation for API failures
- Log errors appropriately without exposing sensitive information

## Environment Variables
- Use `.env.local` for local development
- Store API endpoints and other configuration
- Never commit environment files to version control
- Use proper validation for required environment variables

## Deployment Considerations
- Optimize for production builds with Next.js
- Implement proper caching headers
- Ensure all assets are properly optimized
- Set up proper error monitoring in production
- Implement proper logging and monitoring