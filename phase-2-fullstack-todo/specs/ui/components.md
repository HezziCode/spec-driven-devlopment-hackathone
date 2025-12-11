# UI Components Specification

## Overview
This document defines the UI components for the Phase 2 full-stack todo web application. The components are built with Next.js using the App Router, TypeScript, and Tailwind CSS. Components follow accessibility standards (WCAG 2.1 AA) and are organized for reusability and maintainability.

## Technology Stack
- **Framework**: Next.js 16+ with App Router
- **Language**: TypeScript with strict mode
- **Styling**: Tailwind CSS (utility-first approach)
- **Authentication**: Better Auth integration
- **API Client**: Centralized API client in `/lib/api.ts`

## Component Structure

### Base UI Components (`/components/ui/`)

#### Button Component
- **Purpose**: Reusable button with different variants
- **Props**:
  - `variant`: primary, secondary, danger, success
  - `size`: sm, md, lg
  - `disabled`: boolean
  - `loading`: boolean
  - `children`: ReactNode
- **Features**: Loading states, accessibility attributes, responsive sizing
- **Accessibility**: Proper ARIA attributes, keyboard navigation, focus states

#### Input Component
- **Purpose**: Reusable text input with validation
- **Props**:
  - `label`: string (optional)
  - `id`: string
  - `type`: text, email, password, etc.
  - `value`: string
  - `onChange`: function
  - `error`: string (optional)
  - `required`: boolean
- **Features**: Label integration, error display, proper input types
- **Accessibility**: Proper labeling, error association, focus management

#### Card Component
- **Purpose**: Container for grouping related content
- **Props**:
  - `title`: string (optional)
  - `children`: ReactNode
  - `className`: string (optional)
- **Features**: Optional header, flexible content area, responsive design
- **Accessibility**: Semantic structure, proper heading hierarchy

#### Modal Component
- **Purpose**: Overlay for important interactions
- **Props**:
  - `isOpen`: boolean
  - `onClose`: function
  - `title`: string
  - `children`: ReactNode
- **Features**: Overlay backdrop, close functionality, focus trapping
- **Accessibility**: Focus management, keyboard navigation (ESC to close), screen reader support

### Task-Specific Components (`/components/task/`)

#### TaskItem Component
- **Purpose**: Display individual task with interactive elements
- **Props**:
  - `task`: Task object with id, title, description, completed, priority, tags
  - `onToggleComplete`: function (optional)
  - `onEdit`: function (optional)
  - `onDelete`: function (optional)
- **Features**:
  - Visual indication of completion status
  - Priority level visualization
  - Tag display
  - Action buttons (edit, delete, complete)
- **Accessibility**: Proper labeling, keyboard navigation, ARIA states for completion status

#### TaskList Component
- **Purpose**: Display multiple tasks with filtering and sorting
- **Props**:
  - `tasks`: Array of Task objects
  - `onTaskAction`: function for handling task interactions
  - `filter`: string (optional) - filter criteria
  - `sort`: string (optional) - sort criteria
- **Features**:
  - Responsive grid/list layout
  - Filtering by status, priority, tags
  - Sorting options (date, priority, title)
  - Empty state handling
- **Accessibility**: Proper list semantics, keyboard navigation, screen reader announcements

#### TaskForm Component
- **Purpose**: Create or edit tasks with validation
- **Props**:
  - `initialData`: Task object (optional) for editing
  - `onSubmit`: function
  - `onCancel`: function (optional)
- **Features**:
  - Title and description fields
  - Priority selection dropdown
  - Tag input with suggestions
  - Form validation and error display
  - Loading states
- **Accessibility**: Proper form labeling, error association, focus management

#### TaskFilter Component
- **Purpose**: Filter and sort tasks
- **Props**:
  - `onFilterChange`: function
  - `onSortChange`: function
- **Features**:
  - Status filter (all, completed, pending)
  - Priority filter
  - Tag filter
  - Sort options (date, priority, title)
  - Clear filters functionality
- **Accessibility**: Proper form controls, keyboard navigation, ARIA attributes

### Layout Components (`/components/layout/`)

#### Header Component
- **Purpose**: Top navigation with user authentication
- **Props**:
  - `user`: User object (optional)
  - `onLogout`: function
- **Features**:
  - Logo/title display
  - Navigation links
  - User profile dropdown
  - Authentication status indicator
- **Accessibility**: Proper navigation landmarks, keyboard navigation

#### Sidebar Component
- **Purpose**: Secondary navigation and quick actions
- **Props**:
  - `navigationItems`: Array of navigation objects
  - `activeItem`: string
- **Features**:
  - Navigation links
  - Quick action buttons
  - Collapsible sections
- **Accessibility**: Proper navigation semantics, keyboard navigation

#### ProtectedRoute Component
- **Purpose**: Wrapper to protect routes requiring authentication
- **Props**:
  - `children`: ReactNode
  - `fallback`: ReactNode (optional)
- **Features**:
  - Authentication check
  - Redirect to login if not authenticated
  - Loading state during authentication check
- **Accessibility**: Proper loading announcements, smooth transitions

### Authentication Components (`/components/auth/`)

#### LoginForm Component
- **Purpose**: User login form with validation
- **Props**:
  - `onLogin`: function
  - `onNavigateToSignup`: function
- **Features**:
  - Email and password fields
  - Form validation
  - Loading states
  - Error handling
- **Accessibility**: Proper form labeling, error association

#### SignupForm Component
- **Purpose**: User registration form with validation
- **Props**:
  - `onSignup`: function
  - `onNavigateToLogin`: function
- **Features**:
  - Username, email, password fields
  - Password strength validation
  - Form validation
  - Loading states
- **Accessibility**: Proper form labeling, error association, password visibility toggle

## Page Components (`/app/`)

### Dashboard Page (`/app/page.tsx`)
- **Purpose**: Main dashboard showing user tasks
- **Features**:
  - Welcome message
  - Task summary statistics
  - Recent tasks list
  - Quick add task form
- **Data Fetching**: Server component fetching user data and tasks

### Tasks Page (`/app/tasks/page.tsx`)
- **Purpose**: Full task management interface
- **Features**:
  - Task list with filtering
  - Task creation form
  - Bulk actions
  - Pagination
- **Data Fetching**: Server component fetching tasks with filters

### Auth Pages (`/app/auth/`)
- **Login Page** (`/app/auth/login/page.tsx`): Login form component
- **Signup Page** (`/app/auth/signup/page.tsx`): Signup form component
- **Data Fetching**: Server components with authentication redirects

## Styling Guidelines

### Tailwind CSS Usage
- Use utility classes exclusively (no custom CSS files)
- Follow consistent color palette defined in Tailwind config
- Use responsive prefixes for mobile-first design
- Implement consistent spacing using Tailwind's spacing scale

### Responsive Design
- Mobile-first approach with progressive enhancement
- Consistent breakpoints across all components
- Touch-friendly interactions for mobile devices
- Appropriate touch target sizes (minimum 44px)

### Accessibility Standards (WCAG 2.1 AA)
- Proper semantic HTML structure
- Sufficient color contrast ratios (4.5:1 minimum)
- Keyboard navigation support for all interactive elements
- ARIA attributes where necessary
- Screen reader compatibility
- Focus management and focus traps
- Proper labeling of form elements

## API Integration
- All API calls go through centralized API client in `/lib/api.ts`
- API client automatically attaches JWT tokens from auth context
- Components handle loading and error states appropriately
- Type-safe API calls with TypeScript interfaces

## Performance Considerations
- Server components used by default for data fetching
- Client components only when interactivity is required
- Proper suspense boundaries for async operations
- Image optimization using Next.js Image component
- Code splitting and lazy loading where appropriate

## Security Considerations
- No sensitive data exposed in client-side components
- Proper authentication state management
- Input sanitization before API calls
- Error messages that don't expose system details

## Component Reusability
- Generic components in `/components/ui/`
- Feature-specific components in `/components/task/`, `/components/auth/`, etc.
- Clear separation of concerns between presentation and logic
- Consistent prop interfaces across similar components