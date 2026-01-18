# Implementation Plan: Responsive Chat Interface

**Branch**: `020-responsive-chat-ui` | **Date**: 2026-01-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/020-responsive-chat-ui/spec.md`

## Summary

Transform the chat interface into a fully responsive experience across mobile, tablet, and desktop devices while preserving the existing desktop layout. Add consistent navigation icons (chatbot icon on task page, task page icon in navbar) and implement a ChatGPT-like mobile interface with a collapsible history panel accessible via a top icon.

**Technical Approach**: Mobile-first responsive design using Tailwind CSS breakpoints (sm:, md:, lg:), CSS transforms for smooth panel animations, and conditional rendering based on screen size. Preserve desktop layout (1024px+) exactly as-is while progressively enhancing mobile experience.

## Technical Context

**Language/Version**: TypeScript 5.x with Next.js 15+ (App Router)
**Primary Dependencies**:
- Next.js 15+ (App Router, Client Components)
- React 18+
- Tailwind CSS 3.x (responsive utilities)
- lucide-react (icon library)
- Better Auth (authentication context)

**Storage**: N/A (UI-only changes, existing localStorage for thread state)
**Testing**: Jest/React Testing Library for component tests, manual testing across devices
**Target Platform**: Web browsers (Chrome 90+, Safari 14+, Firefox 90+, mobile browsers)
**Project Type**: Web application (frontend-only changes)
**Performance Goals**:
- Panel animations complete within 300ms
- Layout reflow on orientation change within 300ms
- 60fps scroll performance on mobile
- No Cumulative Layout Shift (CLS) when keyboard appears

**Constraints**:
- Must preserve existing desktop layout pixel-perfect (1024px+)
- Minimum touch target size 44x44px (WCAG 2.1 AA)
- Must handle iOS safe area insets (notch)
- Must work with Android system navigation gestures

**Scale/Scope**:
- 4 component files to modify (CustomChatInterface, Navbar, chat page, task page)
- 3 responsive breakpoints (mobile: <768px, tablet: 768-1023px, desktop: 1024px+)
- 2 new icon components (chatbot icon, task page icon)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✅ **Clean Code Principles**:
- Single Responsibility: Each component handles one concern (chat interface, navigation, icons)
- Type Safety: All components use TypeScript with proper interfaces
- Accessibility: WCAG 2.1 AA compliance (touch targets, keyboard navigation, screen readers)

✅ **Performance**:
- CSS transforms for animations (GPU-accelerated)
- Conditional rendering to avoid unnecessary DOM nodes
- Lazy loading not needed (small component changes)

✅ **Modularity**:
- Icon components can be reused across pages
- Responsive utilities encapsulated in Tailwind classes
- No tight coupling between components

✅ **Testing**:
- Component tests for responsive behavior
- Manual testing across devices and screen sizes
- Accessibility testing with screen readers

## Project Structure

### Documentation (this feature)

```text
specs/020-responsive-chat-ui/
├── spec.md              # Feature specification
├── plan.md              # This file (implementation plan)
├── checklists/
│   └── requirements.md  # Requirements validation checklist
└── tasks.md             # Will be created by /sp.tasks command
```

### Source Code (repository root)

```text
frontend/
├── app/
│   ├── chat/
│   │   └── page.tsx                    # [MODIFY] Add mobile history icon
│   └── tasks/
│       └── page.tsx                    # [MODIFY] Add chatbot icon
├── components/
│   ├── CustomChatInterface.tsx         # [MODIFY] Add responsive layout
│   ├── Navbar.tsx                      # [MODIFY] Add task page icon
│   ├── ChatbotIcon.tsx                 # [NEW] Reusable chatbot icon component
│   └── TaskPageIcon.tsx                # [NEW] Task page navigation icon
└── styles/
    └── globals.css                     # [VERIFY] Tailwind config for breakpoints
```

**Structure Decision**: Web application structure with frontend-only changes. All modifications are in the `frontend/` directory. No backend changes required.

## Complexity Tracking

> **No violations** - This implementation follows constitution principles without requiring exceptions.

## Phase 0: Research & Discovery

### Current Implementation Analysis

**Existing Chat Interface** (`frontend/components/CustomChatInterface.tsx`):
- Lines 84: `const [isSidebarOpen, setIsSidebarOpen] = useState(true);`
- Sidebar is always visible on desktop
- No responsive breakpoints currently implemented
- Uses Tailwind classes but not responsive utilities

**Existing Navbar** (`frontend/components/Navbar.tsx`):
- Lines 40-76: Simple navbar with logo (left) and profile dropdown (right)
- No task page icon currently
- No responsive considerations beyond basic Tailwind classes

**Landing Page Chatbot Icon** (`frontend/components/LandingPage.tsx`):
- Lines 81-89: Floating chat button with `MessageCircle` icon from lucide-react
- Styling: `p-4 rounded-full bg-cyan-600 hover:bg-cyan-700 text-white shadow-lg`
- Position: `fixed bottom-6 right-6 z-50`

**Chat Page Layout** (`frontend/app/chat/page.tsx`):
- Lines 27-39: Simple wrapper with Navbar, CustomChatInterface, Footer
- Uses flexbox for layout
- No responsive considerations

### Responsive Breakpoints Strategy

**Tailwind CSS Breakpoints** (standard):
- `sm:` - 640px and up (small tablets, landscape phones)
- `md:` - 768px and up (tablets)
- `lg:` - 1024px and up (laptops, desktops)
- `xl:` - 1280px and up (large desktops)

**Our Breakpoints**:
- **Mobile**: Default (< 768px) - Collapsible sidebar, history icon at top
- **Tablet**: `md:` (768px - 1023px) - Hybrid layout, sidebar can toggle
- **Desktop**: `lg:` (1024px+) - Preserve existing layout, sidebar always visible

### Icon Strategy

**Chatbot Icon** (for task page):
- Copy styling from landing page floating button
- Use `MessageCircle` icon from lucide-react
- Position: Fixed bottom-right corner (matching landing page)
- Behavior: Navigate to `/chat` on click

**Task Page Icon** (for navbar):
- Use `ListTodo` icon from lucide-react (matches logo)
- Position: In navbar, left of profile dropdown
- Styling: Match profile dropdown button style
- Behavior: Navigate to `/tasks` on click

### Mobile History Panel Design

**Approach**: Overlay panel that slides in from left on mobile
- **Trigger**: History icon at top-left of chat interface (mobile only)
- **Animation**: CSS transform `translateX(-100%)` to `translateX(0)`
- **Backdrop**: Semi-transparent overlay to close panel
- **Z-index**: Higher than chat content, lower than navbar

## Phase 1: Design & Architecture

### Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Navbar (Modified)                                           │
│ ┌─────────┐                           ┌──────┬───────────┐ │
│ │  Logo   │                           │ Task │  Profile  │ │
│ └─────────┘                           │ Icon │  Dropdown │ │
│                                       └──────┴───────────┘ │
└─────────────────────────────────────────────────────────────┘
│
│ Desktop (lg:1024px+) - Preserve Existing Layout
├─────────────────────────────────────────────────────────────┤
│ ┌──────────────┬────────────────────────────────────────┐  │
│ │   Sidebar    │         Chat Messages                  │  │
│ │   (Visible)  │                                        │  │
│ │              │                                        │  │
│ │  Thread 1    │  User: Hello                          │  │
│ │  Thread 2    │  Bot: Hi there!                       │  │
│ │  Thread 3    │                                        │  │
│ │              │                                        │  │
│ │  [+ New]     │         [Input Field]                 │  │
│ └──────────────┴────────────────────────────────────────┘  │
│
│ Mobile (<768px) - New Responsive Layout
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ [☰ History]              Chat              [Profile]    │ │
│ ├─────────────────────────────────────────────────────────┤ │
│ │                                                         │ │
│ │  User: Hello                                           │ │
│ │  Bot: Hi there!                                        │ │
│ │                                                         │ │
│ │                                                         │ │
│ │                                                         │ │
│ │                     [Input Field]                      │ │
│ └─────────────────────────────────────────────────────────┘ │
│
│ Mobile with History Panel Open
├─────────────────────────────────────────────────────────────┤
│ ┌──────────────┬──────────────────────────────────────────┐ │
│ │   Sidebar    │ [Backdrop - Click to Close]             │ │
│ │   (Overlay)  │                                         │ │
│ │              │                                         │ │
│ │  Thread 1    │                                         │ │
│ │  Thread 2    │                                         │ │
│ │  Thread 3    │                                         │ │
│ │              │                                         │ │
│ │  [+ New]     │                                         │ │
│ │  [X Close]   │                                         │ │
│ └──────────────┴──────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Responsive Layout Strategy

**Desktop (lg:1024px+)**: Preserve existing layout
```tsx
<div className="flex h-full">
  {/* Sidebar - Always visible on desktop */}
  <div className="w-64 border-r border-slate-700">
    {/* Thread list */}
  </div>

  {/* Chat area */}
  <div className="flex-1">
    {/* Messages and input */}
  </div>
</div>
```

**Mobile (<768px)**: Collapsible sidebar with overlay
```tsx
<div className="relative h-full">
  {/* Mobile header with history icon */}
  <div className="lg:hidden flex items-center p-4 border-b">
    <button onClick={() => setIsSidebarOpen(true)}>
      <Menu className="w-6 h-6" />
    </button>
    <span className="ml-4 font-semibold">Chat</span>
  </div>

  {/* Sidebar - Overlay on mobile */}
  {isSidebarOpen && (
    <>
      {/* Backdrop */}
      <div
        className="lg:hidden fixed inset-0 bg-black/50 z-40"
        onClick={() => setIsSidebarOpen(false)}
      />

      {/* Sidebar panel */}
      <div className="lg:hidden fixed left-0 top-0 bottom-0 w-64 bg-slate-800 z-50 transform transition-transform duration-300">
        {/* Thread list */}
      </div>
    </>
  )}

  {/* Chat area - Full width on mobile */}
  <div className="flex-1">
    {/* Messages and input */}
  </div>
</div>
```

### Icon Component Design

**ChatbotIcon.tsx** (New component):
```tsx
'use client';

import { MessageCircle } from 'lucide-react';
import { useRouter } from 'next/navigation';

export function ChatbotIcon() {
  const router = useRouter();

  return (
    <button
      onClick={() => router.push('/chat')}
      className="fixed bottom-6 right-6 z-50 p-4 rounded-full bg-cyan-600 hover:bg-cyan-700 text-white shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-110"
      aria-label="Open chat"
    >
      <MessageCircle className="w-6 h-6" />
    </button>
  );
}
```

**TaskPageIcon** (Navbar modification):
```tsx
// In Navbar.tsx, add before profile dropdown
{session && (
  <button
    onClick={() => router.push('/tasks')}
    className="p-2 rounded-lg hover:bg-slate-700 transition-colors"
    aria-label="Go to tasks"
  >
    <ListTodo className="w-5 h-5 text-cyan-400" />
  </button>
)}
```

### Animation Strategy

**Sidebar Slide Animation**:
```css
/* Tailwind classes */
.sidebar-enter {
  transform: translateX(-100%);
}

.sidebar-enter-active {
  transform: translateX(0);
  transition: transform 300ms ease-out;
}

.sidebar-exit {
  transform: translateX(0);
}

.sidebar-exit-active {
  transform: translateX(-100%);
  transition: transform 300ms ease-in;
}
```

**Implementation**: Use Tailwind's `transition-transform duration-300` class

### Mobile Keyboard Handling

**Problem**: Mobile keyboard covers input field when typing

**Solution**: Use CSS viewport units and proper positioning
```tsx
<div className="flex flex-col h-[100dvh]"> {/* dvh = dynamic viewport height */}
  <div className="flex-1 overflow-y-auto">
    {/* Messages */}
  </div>

  <div className="sticky bottom-0 bg-slate-800 border-t border-slate-700 p-4">
    {/* Input field */}
  </div>
</div>
```

### Touch Target Optimization

**Minimum Size**: 44x44px for all interactive elements on mobile

**Implementation**:
```tsx
// Mobile buttons
<button className="min-h-[44px] min-w-[44px] p-3 ...">
  <Icon className="w-6 h-6" />
</button>

// Thread list items on mobile
<button className="w-full min-h-[44px] px-4 py-3 text-left ...">
  {threadName}
</button>
```

## Phase 2: Implementation Tasks

### Task Breakdown (High-Level)

**Phase 2A: Responsive Chat Interface** (P1)
1. Add responsive breakpoints to CustomChatInterface.tsx
2. Implement mobile header with history icon
3. Convert sidebar to overlay panel on mobile
4. Add backdrop for closing panel
5. Test keyboard handling on mobile devices
6. Test orientation changes (portrait/landscape)

**Phase 2B: Navigation Icons** (P2)
7. Create ChatbotIcon component
8. Add ChatbotIcon to task page
9. Add task page icon to Navbar
10. Test navigation between pages
11. Verify icon consistency across pages

**Phase 2C: Mobile History Panel** (P3)
12. Implement slide-in animation for sidebar
13. Add close button to mobile sidebar
14. Handle outside click to close panel
15. Test thread selection from mobile panel
16. Verify panel behavior on different mobile devices

**Phase 2D: Testing & Refinement**
17. Cross-browser testing (Chrome, Safari, Firefox mobile)
18. Accessibility testing (screen readers, keyboard navigation)
19. Performance testing (animation smoothness, scroll performance)
20. Visual regression testing (desktop layout preservation)

### Detailed Implementation Steps

**Step 1: Add Responsive Breakpoints to CustomChatInterface**

File: `frontend/components/CustomChatInterface.tsx`

Changes:
- Add mobile header with history icon (lines 200-210, new)
- Modify sidebar container to use responsive classes (line 250)
- Add backdrop for mobile overlay (lines 260-265, new)
- Update sidebar visibility logic for mobile vs desktop

```tsx
// Add state for mobile detection
const [isMobile, setIsMobile] = useState(false);

useEffect(() => {
  const checkMobile = () => {
    setIsMobile(window.innerWidth < 1024);
  };

  checkMobile();
  window.addEventListener('resize', checkMobile);
  return () => window.removeEventListener('resize', checkMobile);
}, []);

// Mobile header (show only on mobile)
{isMobile && (
  <div className="flex items-center justify-between p-4 border-b border-slate-700">
    <button
      onClick={() => setIsSidebarOpen(true)}
      className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
      aria-label="Open chat history"
    >
      <Menu className="w-6 h-6 text-cyan-400" />
    </button>
    <span className="text-lg font-semibold text-white">Chat</span>
    <div className="w-10" /> {/* Spacer for centering */}
  </div>
)}

// Backdrop (mobile only)
{isMobile && isSidebarOpen && (
  <div
    className="fixed inset-0 bg-black/50 z-40"
    onClick={() => setIsSidebarOpen(false)}
    aria-label="Close sidebar"
  />
)}

// Sidebar with responsive classes
<div
  className={`
    ${isMobile ? 'fixed left-0 top-0 bottom-0 z-50' : 'relative'}
    ${isMobile && !isSidebarOpen ? '-translate-x-full' : 'translate-x-0'}
    w-64 bg-slate-800 border-r border-slate-700
    transition-transform duration-300 ease-out
  `}
>
  {/* Sidebar content */}
</div>
```

**Step 2: Create ChatbotIcon Component**

File: `frontend/components/ChatbotIcon.tsx` (new)

```tsx
'use client';

import { MessageCircle } from 'lucide-react';
import { useRouter } from 'next/navigation';

/**
 * Floating chatbot icon for navigating to chat page
 * Matches the style from landing page
 */
export function ChatbotIcon() {
  const router = useRouter();

  const handleClick = () => {
    router.push('/chat');
  };

  return (
    <button
      onClick={handleClick}
      className="fixed bottom-6 right-6 z-50 p-4 rounded-full bg-cyan-600 hover:bg-cyan-700 text-white shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-110 min-h-[56px] min-w-[56px]"
      aria-label="Open chat assistant"
      title="Chat with AI Assistant"
    >
      <MessageCircle className="w-6 h-6" />
    </button>
  );
}
```

**Step 3: Add Task Page Icon to Navbar**

File: `frontend/components/Navbar.tsx`

Changes: Add task page icon before profile dropdown (line 57)

```tsx
{/* Right side - Task icon and Profile dropdown */}
<div className="flex items-center space-x-3">
  {session && (
    <>
      {/* Task Page Icon */}
      <button
        onClick={() => router.push('/tasks')}
        className="p-2 rounded-lg hover:bg-slate-700 transition-colors min-h-[44px] min-w-[44px]"
        aria-label="Go to tasks page"
        title="Tasks"
      >
        <ListTodo className="w-5 h-5 text-cyan-400" />
      </button>

      {/* Profile Dropdown */}
      <ProfileDropdown
        user={session.user}
        displayName={getUserDisplayName(session.user)}
        onLogout={handleLogout}
      />
    </>
  )}

  {!session && (
    /* Sign Up Button */
    <button
      onClick={navigateToAuth}
      className="px-6 py-2 flex items-center bg-cyan-600 hover:bg-cyan-700 text-white font-semibold rounded-lg shadow-md hover:shadow-lg transition-all duration-200 transform hover:-translate-y-0.5"
    >
      Sign Up
    </button>
  )}
</div>
```

**Step 4: Add ChatbotIcon to Task Page**

File: `frontend/app/tasks/page.tsx`

Changes: Import and render ChatbotIcon component

```tsx
import { ChatbotIcon } from '@/components/ChatbotIcon';

export default function TasksPage() {
  return (
    <ProtectedRoute authMode="signup">
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        <Navbar />

        {/* Main content */}
        <main className="container mx-auto px-4 py-8">
          {/* Task list and form */}
        </main>

        {/* Floating chatbot icon */}
        <ChatbotIcon />

        <Footer />
      </div>
    </ProtectedRoute>
  );
}
```

## Phase 3: Testing Strategy

### Unit Tests

**Component Tests** (Jest + React Testing Library):

```tsx
// CustomChatInterface.test.tsx
describe('CustomChatInterface Responsive', () => {
  it('shows sidebar by default on desktop', () => {
    window.innerWidth = 1024;
    render(<CustomChatInterface />);
    expect(screen.getByRole('complementary')).toBeVisible();
  });

  it('hides sidebar by default on mobile', () => {
    window.innerWidth = 375;
    render(<CustomChatInterface />);
    expect(screen.queryByRole('complementary')).not.toBeVisible();
  });

  it('shows history icon on mobile', () => {
    window.innerWidth = 375;
    render(<CustomChatInterface />);
    expect(screen.getByLabelText('Open chat history')).toBeInTheDocument();
  });

  it('opens sidebar when history icon clicked on mobile', async () => {
    window.innerWidth = 375;
    render(<CustomChatInterface />);

    const historyButton = screen.getByLabelText('Open chat history');
    await userEvent.click(historyButton);

    expect(screen.getByRole('complementary')).toBeVisible();
  });

  it('closes sidebar when backdrop clicked on mobile', async () => {
    window.innerWidth = 375;
    render(<CustomChatInterface />);

    // Open sidebar
    await userEvent.click(screen.getByLabelText('Open chat history'));

    // Click backdrop
    await userEvent.click(screen.getByLabelText('Close sidebar'));

    expect(screen.queryByRole('complementary')).not.toBeVisible();
  });
});

// ChatbotIcon.test.tsx
describe('ChatbotIcon', () => {
  it('renders floating button', () => {
    render(<ChatbotIcon />);
    expect(screen.getByLabelText('Open chat assistant')).toBeInTheDocument();
  });

  it('navigates to chat page when clicked', async () => {
    const mockPush = jest.fn();
    jest.spyOn(require('next/navigation'), 'useRouter').mockReturnValue({
      push: mockPush
    });

    render(<ChatbotIcon />);
    await userEvent.click(screen.getByLabelText('Open chat assistant'));

    expect(mockPush).toHaveBeenCalledWith('/chat');
  });

  it('has minimum touch target size', () => {
    render(<ChatbotIcon />);
    const button = screen.getByLabelText('Open chat assistant');

    const styles = window.getComputedStyle(button);
    expect(parseInt(styles.minHeight)).toBeGreaterThanOrEqual(44);
    expect(parseInt(styles.minWidth)).toBeGreaterThanOrEqual(44);
  });
});
```

### Manual Testing Checklist

**Desktop Testing (1024px+)**:
- [ ] Sidebar is visible by default
- [ ] No history icon in header
- [ ] Layout matches existing design exactly
- [ ] Task page icon visible in navbar
- [ ] Chatbot icon visible on task page
- [ ] All icons navigate correctly

**Tablet Testing (768px-1023px)**:
- [ ] Sidebar behavior is appropriate
- [ ] Touch targets are adequate size
- [ ] Layout adapts smoothly

**Mobile Testing (320px-767px)**:
- [ ] Sidebar hidden by default
- [ ] History icon visible at top
- [ ] Clicking history icon opens sidebar overlay
- [ ] Backdrop closes sidebar when clicked
- [ ] Sidebar slides in smoothly (300ms)
- [ ] Keyboard doesn't cover input field
- [ ] Orientation change works smoothly
- [ ] All touch targets are 44x44px minimum

**Cross-Browser Testing**:
- [ ] Chrome Mobile (Android)
- [ ] Safari (iOS)
- [ ] Firefox Mobile
- [ ] Chrome Desktop
- [ ] Safari Desktop
- [ ] Firefox Desktop

**Accessibility Testing**:
- [ ] Screen reader announces sidebar state
- [ ] Keyboard navigation works (Tab, Enter, Escape)
- [ ] Focus management when opening/closing sidebar
- [ ] Color contrast meets WCAG 2.1 AA (4.5:1)
- [ ] Touch targets meet WCAG 2.1 AA (44x44px)

**Performance Testing**:
- [ ] Sidebar animation completes in <300ms
- [ ] Orientation change completes in <300ms
- [ ] Scroll performance is 60fps on mobile
- [ ] No layout shift when keyboard appears (CLS = 0)

## Phase 4: Deployment & Rollout

### Pre-Deployment Checklist

- [ ] All unit tests passing
- [ ] Manual testing completed on all devices
- [ ] Accessibility audit passed
- [ ] Performance metrics met
- [ ] Code review completed
- [ ] Documentation updated

### Deployment Strategy

**Approach**: Single deployment with feature flag (optional)

1. Merge feature branch to main
2. Deploy to staging environment
3. Smoke test on staging (all devices)
4. Deploy to production
5. Monitor for issues (error tracking, user feedback)

### Rollback Plan

If issues are detected:
1. Revert deployment to previous version
2. Investigate issue in staging
3. Fix and re-test
4. Re-deploy when ready

### Success Metrics

**Quantitative**:
- Mobile bounce rate decreases by 20%
- Mobile session duration increases by 30%
- Zero layout shift (CLS = 0)
- Animation performance: 60fps on 95% of devices

**Qualitative**:
- User feedback: "Mobile experience is much better"
- No complaints about broken desktop layout
- Positive feedback on navigation improvements

## Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Breaking desktop layout | High | Medium | Extensive testing on desktop before deployment; use `lg:` prefix for all desktop-specific styles |
| Mobile keyboard covering input | High | High | Use `dvh` viewport units; test on iOS and Android; add padding when keyboard is visible |
| Performance issues on low-end devices | Medium | Medium | Use CSS transforms (GPU-accelerated); avoid JavaScript animations; test on low-end devices |
| Sidebar animation janky | Medium | Low | Use `will-change: transform`; optimize animation timing; test on various devices |
| Icons not matching style | Low | Low | Use shared icon components; create style guide; review with designer |

## Open Questions & Decisions

### Q1: Should sidebar slide from left or right on mobile?
**Decision**: Slide from left (matches ChatGPT pattern, feels natural for LTR languages)
**Rationale**: Industry standard, user familiarity, better UX

### Q2: Should we add swipe gestures to open/close sidebar?
**Decision**: Not in this phase (out of scope)
**Rationale**: Can be added as enhancement later; focus on core functionality first

### Q3: What should be minimum supported mobile width?
**Decision**: 320px (iPhone SE, smallest common device)
**Rationale**: Covers 99%+ of mobile devices; industry standard

### Q4: Should desktop layout change at all?
**Decision**: No changes to desktop layout (1024px+)
**Rationale**: User explicitly requested "layout kharab nhi karna laptop screen pr" (don't break laptop layout)

### Q5: How to handle very long thread titles on mobile?
**Decision**: Truncate with ellipsis after 30 characters
**Rationale**: Prevents layout breaks; full title visible on hover/long-press

## Next Steps

1. **Get user approval** on this implementation plan
2. **Run `/sp.tasks`** to break down into actionable tasks with test cases
3. **Begin implementation** starting with Phase 2A (responsive chat interface)
4. **Iterate and test** throughout implementation
5. **Deploy** when all tests pass and manual testing is complete

## References

- Specification: [spec.md](./spec.md)
- Requirements Checklist: [checklists/requirements.md](./checklists/requirements.md)
- Tailwind CSS Responsive Design: https://tailwindcss.com/docs/responsive-design
- WCAG 2.1 Touch Target Size: https://www.w3.org/WAI/WCAG21/Understanding/target-size.html
- Next.js App Router: https://nextjs.org/docs/app
