# Feature Specification: TaskWave Dashboard

**Feature Branch**: `001-taskwave-dashboard`
**Created**: 2025-12-16
**Status**: Draft
**Input**: User description: "Create a detailed specification for the protected Todo (or Task) page in Phase 2, branded as 'TaskWave Dashboard' at /tasks route in Next.js App Router to add uniqueness (differentiate from generic todo apps by incorporating wave-themed elements like subtle wave animations on task cards, gamification: streak counter for completed tasks showing 'Wave Streak: X days' at top). It must be protected with Better Auth (redirect to /auth if no JWT). UI: Responsive layout with navbar (from components/Navbar.tsx), main content in grid/sections with unique 'Ride Your Task Waves' gradient heading (teal-cyan with subtle wave animation underline for distinctiveness, instead of plain 'My Tasks'). Include task list as interactive cards (not plain table for uniqueness: each card with wave border/animation on hover, showing title, desc, completed checkbox, priority badge (high/red with flame icon, med/yellow with clock, low/green with leaf), tags as colorful pills). Add form at top for new task (fields: title input required, desc textarea optional, priority select (high/med/low), tags multi-input with uniqueness: predefined readymade tags as clickable chips below input e.g., Fitness, Home, Work, Code, Planning, Design, UI/UX, Backend, Security – user clicks to auto-add to tags field, allow custom too). At the end of the task list, add a paid Pro feature section (teased with CSS blur filter on content for blurriness, 'Coming Soon' badge in teal-cyan gradient for attractiveness): Include 'Go Pro' button (cyan glow hover), small description 'Unlock AI magic: Auto-tags, smart priorities, sub-task breakdowns for ultimate productivity waves!', gated behind upgrade modal. Features: Search input (filter by title/tags), filter dropdowns (by status: All/Pending/Completed; by priority: All/High/Med/Low), sort buttons (by title/priority/created, with 'Smart Sort' as Pro tease button leading to upgrade). Use server components default, client for interactive (e.g., form submission, filters, tag clicks, Pro button). Integrate API calls via /lib/api.ts with JWT (GET/POST/PUT/DELETE/PATCH to /api/{user_id}/tasks endpoints, but focus on frontend UI for now – use mock data if needed). Handle loading states with suspense/spinner (wave-themed loader), errors with toasts. Match site theme: Teal-cyan gradients (#2dd4bf to #06b6d4), light mode bg #f0f9ff/text gray-800, dark mode bg #0f172a/text white; Inter font (extrabold headings, text-xl body); Animations: Hover scale-110/translate-y-1 on cards/buttons (duration-300), active scale-95, gradient text for headings, cursor glow (teal/cyan), backdrop-blur on filters bar, unique wave transition on task add/complete. Accessibility: ARIA labels, keyboard nav, contrast. Reference specs/features/task-crud.md, specs/ui/components.md, and constitution for modularity/type safety. just do this"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Access Protected Dashboard (Priority: P1)

As an authenticated user, I want to access my personalized TaskWave Dashboard at the /tasks route so that I can manage my tasks in a unique, wave-themed environment with visual feedback and gamification elements.

**Why this priority**: This is the foundational functionality that enables all other features. Without secure access to the dashboard, no other functionality is possible.

**Independent Test**: Can be fully tested by logging in and navigating to the /tasks route. The user should see the dashboard with their tasks and be prevented from accessing it when not authenticated.

**Acceptance Scenarios**:

1. **Given** I am an authenticated user, **When** I navigate to /tasks, **Then** I see the TaskWave Dashboard with my tasks and wave-themed UI elements
2. **Given** I am not authenticated, **When** I navigate to /tasks, **Then** I am redirected to the authentication page

---

### User Story 2 - View and Interact with Task Cards (Priority: P1)

As a user, I want to view my tasks as interactive cards with wave-themed animations and priority badges so that I can quickly identify and manage my tasks with visual feedback.

**Why this priority**: This is the core user interaction with tasks, providing the visual differentiation that makes TaskWave unique.

**Independent Test**: Can be fully tested by viewing existing tasks displayed as interactive cards with proper priority indicators, hover animations, and completion toggling.

**Acceptance Scenarios**:

1. **Given** I have tasks in my list, **When** I view the dashboard, **Then** I see each task as an interactive card with wave-themed border and animations
2. **Given** I hover over a task card, **When** I move my cursor over it, **Then** the card scales up and moves up with wave-themed border animation
3. **Given** I have tasks with different priorities, **When** I view the dashboard, **Then** I see appropriate priority badges (flame for high, clock for medium, leaf for low)

---

### User Story 3 - Create New Tasks with Enhanced Form (Priority: P2)

As a user, I want to create new tasks using a form with title, description, priority selection, and tag management with clickable predefined chips so that I can efficiently add tasks with all necessary details.

**Why this priority**: This enables the core functionality of adding new tasks with rich metadata, improving user productivity.

**Independent Test**: Can be fully tested by filling out the task creation form and successfully adding new tasks to the list.

**Acceptance Scenarios**:

1. **Given** I am on the dashboard, **When** I fill in the task form and submit, **Then** the new task appears in my task list
2. **Given** I want to add predefined tags, **When** I click on a tag chip, **Then** that tag is added to the tags field
3. **Given** I have entered a custom tag, **When** I submit the form, **Then** the custom tag is preserved with the task

---

### User Story 4 - Filter, Search and Sort Tasks (Priority: P2)

As a user, I want to filter my tasks by status and priority, search by title and tags, and sort by various criteria so that I can quickly find and organize my tasks.

**Why this priority**: This significantly improves task management efficiency and user productivity with large task lists.

**Independent Test**: Can be fully tested by applying different filters, search terms, and sorting options to see the task list update accordingly.

**Acceptance Scenarios**:

1. **Given** I have multiple tasks with different statuses, **When** I select a status filter, **Then** only tasks with that status are displayed
2. **Given** I have tasks with various tags, **When** I search for a specific term, **Then** only matching tasks are displayed
3. **Given** I want to organize my tasks, **When** I click a sort option, **Then** tasks are reordered according to the selected criteria

---

### User Story 5 - Experience Gamification Elements (Priority: P3)

As a user, I want to see my completion streak ("Wave Streak") and experience wave-themed animations so that I feel motivated to maintain my productivity habits.

**Why this priority**: This adds the unique gamification element that differentiates TaskWave from other todo apps and encourages continued use.

**Independent Test**: Can be fully tested by completing tasks and observing the streak counter update with visual feedback.

**Acceptance Scenarios**:

1. **Given** I have completed tasks in consecutive days, **When** I view the dashboard, **Then** I see my current "Wave Streak: X days" counter
2. **Given** I complete a task, **When** I click the checkbox, **Then** I see a wave-themed animation confirming the action

---

### User Story 6 - Access Pro Features Teaser (Priority: P3)

As a user, I want to see premium features teased at the bottom of the dashboard with a "Go Pro" button so that I understand the value of upgrading to premium.

**Why this priority**: This provides a monetization pathway and showcases advanced features to encourage premium adoption.

**Independent Test**: Can be fully tested by viewing the teaser section with blurred content and the "Go Pro" button.

**Acceptance Scenarios**:

1. **Given** I am on the dashboard, **When** I scroll to the bottom, **Then** I see the pro features teaser with blurred content and "Coming Soon" badge
2. **Given** I am interested in premium features, **When** I click the "Go Pro" button, **Then** I am prompted with upgrade options

---

### Edge Cases

- What happens when a user has more than 1000 tasks and the UI needs to handle performance?
- How does the system handle authentication token expiration during a session?
- What happens when the network is slow or unavailable for API calls?
- How does the system handle invalid or malicious input in task creation?
- What happens when a user tries to add a task with a very long title or description?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST authenticate users via Better Auth JWT tokens before allowing access to the /tasks route
- **FR-002**: System MUST redirect unauthenticated users to the /auth route when accessing the dashboard
- **FR-003**: Users MUST be able to view their tasks as interactive cards with wave-themed animations
- **FR-004**: System MUST display priority badges with appropriate icons (flame for high, clock for medium, leaf for low)
- **FR-005**: System MUST provide a form for creating new tasks with title, description, priority, and tags
- **FR-006**: System MUST allow users to click predefined tag chips to auto-add tags to the task
- **FR-007**: Users MUST be able to filter tasks by status (All/Pending/Completed) and priority (All/High/Med/Low)
- **FR-008**: Users MUST be able to search tasks by title and tags
- **FR-009**: Users MUST be able to sort tasks by title, priority, and creation date
- **FR-010**: System MUST display a "Wave Streak" counter showing consecutive days of completed tasks
- **FR-011**: System MUST provide wave-themed animations for task completion and addition
- **FR-012**: System MUST display a teaser section for pro features with blurred content and "Go Pro" button
- **FR-013**: System MUST handle loading states with wave-themed spinners during API calls
- **FR-014**: System MUST provide appropriate error handling with user-friendly messages
- **FR-015**: System MUST maintain accessibility standards with ARIA labels and keyboard navigation

### Key Entities *(include if feature involves data)*

- **Task**: Represents a user's to-do item with attributes: title, description, completion status, priority level, tags, creation date, and update date
- **User**: Represents an authenticated user with unique identifier and task ownership
- **Priority**: Represents the importance level of a task with values: high, medium, low
- **Tag**: Represents a categorical label that can be associated with tasks for organization and filtering

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can access their TaskWave Dashboard within 3 seconds of navigating to the /tasks route
- **SC-002**: 95% of users successfully complete task creation on their first attempt
- **SC-003**: Users can filter, search, and sort their tasks in under 1 second of applying the filter
- **SC-004**: 80% of users notice and interact with the wave-themed animations and visual elements
- **SC-005**: Users maintain a task completion streak for an average of 7 consecutive days after using the gamification features
- **SC-006**: 10% of free users click the "Go Pro" button within 30 days of using the dashboard
- **SC-007**: The dashboard is fully accessible with keyboard navigation and screen reader compatibility
- **SC-008**: The dashboard maintains responsive design across mobile, tablet, and desktop devices