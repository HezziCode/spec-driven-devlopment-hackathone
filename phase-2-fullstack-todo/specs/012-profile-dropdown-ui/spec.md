# Feature Specification: Profile Dropdown Menu and Auth Page UI Enhancement

**Feature Branch**: `012-profile-dropdown-ui`
**Created**: 2025-12-27
**Status**: Draft
**Input**: User description: "Profile dropdown menu with logout, remove standalone logout button, fix email display issue, improve auth page UI/UX with navbar and footer"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Profile Dropdown for Logout (Priority: P1)

After signing in, users see only their profile picture/icon in the navbar. When clicked, a dropdown menu appears with the logout option. This provides a cleaner, more professional UI and follows common web application patterns.

**Why this priority**: Core usability improvement - current standalone logout button clutters the navbar and doesn't follow standard UI patterns. This is the primary user interaction after authentication.

**Independent Test**: Sign in to the application → Click profile picture/icon in navbar → Dropdown menu appears with "Logout" option → Click "Logout" → User is logged out and redirected to home page.

**Acceptance Scenarios**:

1. **Given** user is signed in with profile picture, **When** user clicks profile picture in navbar, **Then** dropdown menu opens showing "Logout" option
2. **Given** user is signed in without profile picture, **When** user clicks default profile icon, **Then** dropdown menu opens showing "Logout" option
3. **Given** dropdown menu is open, **When** user clicks "Logout", **Then** user is logged out and redirected to landing page
4. **Given** dropdown menu is open, **When** user clicks outside the dropdown, **Then** dropdown closes without action
5. **Given** user is signed in, **When** user views navbar, **Then** no standalone "Logout" button is visible (only profile picture/icon)

---

### User Story 2 - Fix Email Display in Navbar (Priority: P1)

Currently, the user's email prefix (mk26408527) is showing in the navbar instead of the full username or profile information. Users should see their username or full name (from Google profile) next to their profile picture.

**Why this priority**: Critical bug fix - displaying partial email creates poor user experience and looks unprofessional. This affects all authenticated users immediately.

**Independent Test**: Sign in with Google account → Check navbar → Verify full username (from Google: "M. Huzaifa") or local username is displayed, not email prefix.

**Acceptance Scenarios**:

1. **Given** user signs in with Google OAuth, **When** navbar loads, **Then** display Google profile name (e.g., "M. Huzaifa") next to profile picture
2. **Given** user signs in with email/password, **When** navbar loads, **Then** display username (not email) next to profile icon
3. **Given** Google profile has no name, **When** navbar loads, **Then** display username derived from email (fallback behavior)

---

### User Story 3 - Enhanced Auth Page UI with Navbar and Footer (Priority: P2)

The authentication page should have a consistent design with the rest of the application, including a navbar (for branding/navigation) and footer (for terms/privacy links). The "Sign in with Google" button should be properly aligned and visually balanced with the email/password form.

**Why this priority**: Important for professional appearance and brand consistency, but not blocking core functionality. Improves first-time user experience and trust.

**Independent Test**: Visit /auth page → Verify navbar with TaskWave logo visible → Verify footer with terms/privacy links → Verify "Sign in with Google" button is centered and properly styled.

**Acceptance Scenarios**:

1. **Given** user visits /auth page, **When** page loads, **Then** navbar with TaskWave branding is displayed at top
2. **Given** user is on /auth page, **When** user views the page, **Then** footer with Terms of Service and Privacy Policy links is visible at bottom
3. **Given** user views auth form, **When** user sees "Sign in with Google" button, **Then** button is centered, properly sized, and visually balanced with the form
4. **Given** user switches between sign-in and sign-up modes, **When** mode changes, **Then** "Sign in with Google" button text updates appropriately ("Sign in with Google" vs "Sign up with Google")
5. **Given** user is on auth page, **When** user clicks TaskWave logo in navbar, **Then** user is redirected to landing page

---

### User Story 4 - Interactive and Polished Auth Page UX (Priority: P3)

The authentication page should have smooth animations, better visual hierarchy, improved spacing, and interactive feedback to create a modern, polished user experience.

**Why this priority**: Nice-to-have enhancements that improve user satisfaction and perceived quality, but don't affect core functionality.

**Independent Test**: Visit /auth page → Interact with form elements (focus inputs, hover buttons, click Google button) → Verify smooth transitions, clear visual feedback, and professional polish.

**Acceptance Scenarios**:

1. **Given** user focuses on input field, **When** field receives focus, **Then** smooth transition animation occurs (border color, shadow)
2. **Given** user hovers over buttons, **When** mouse enters button area, **Then** button shows interactive hover state with smooth transition
3. **Given** user submits form, **When** form is processing, **Then** loading indicator shows with smooth animation
4. **Given** user views error messages, **When** error appears, **Then** error message fades in smoothly with appropriate icon
5. **Given** user toggles between sign-in and sign-up, **When** mode changes, **Then** form transitions smoothly without jarring layout shifts

---

### Edge Cases

- What happens when user has profile picture but image fails to load? → Fallback to default profile icon
- What happens when user clicks profile dropdown while another dropdown is open? → Close previous dropdown, open new one
- What happens when user is on auth page but already authenticated? → Redirect to /tasks dashboard
- What happens when Google OAuth button is clicked but Google service is unavailable? → Show user-friendly error message
- What happens when navbar is viewed on mobile devices? → Responsive layout, dropdown adjusts position if needed
- What happens when user presses Escape key while dropdown is open? → Dropdown closes
- What happens when very long username is displayed in navbar? → Truncate with ellipsis (...) after reasonable length

## Requirements *(mandatory)*

### Functional Requirements

#### Profile Dropdown Menu (P1)
- **FR-001**: System MUST display only profile picture or default icon in navbar after user signs in (no standalone logout button)
- **FR-002**: System MUST show dropdown menu when user clicks profile picture/icon
- **FR-003**: Dropdown menu MUST contain "Logout" option
- **FR-004**: System MUST log user out and redirect to home page when "Logout" is clicked in dropdown
- **FR-005**: System MUST close dropdown when user clicks outside the dropdown area
- **FR-006**: Dropdown MUST be accessible via keyboard navigation (Tab to profile, Enter to open, Escape to close)

#### Username Display Fix (P1)
- **FR-007**: System MUST display user's full name from Google profile when available (e.g., "M. Huzaifa")
- **FR-008**: System MUST display username for email/password users (not email address)
- **FR-009**: System MUST provide fallback to username if Google profile has no name field
- **FR-010**: System MUST NOT display email addresses or email prefixes in the navbar

#### Auth Page Navbar and Footer (P2)
- **FR-011**: Auth page MUST include navbar with TaskWave logo identical to other pages
- **FR-012**: Navbar logo MUST link to landing page (/)
- **FR-013**: Auth page MUST include footer with "Terms of Service" and "Privacy Policy" placeholder links
- **FR-014**: Navbar MUST NOT show sign-up button when user is on auth page (avoid duplicate actions)
- **FR-015**: Footer MUST include copyright notice with current year

#### Google OAuth Button Alignment (P2)
- **FR-016**: "Sign in with Google" button MUST be horizontally centered
- **FR-017**: "Sign in with Google" button width MUST match form input field widths
- **FR-018**: Spacing above "Sign in with Google" button MUST equal spacing below the form submit button (consistent visual rhythm)
- **FR-019**: "or" divider MUST be centered with equal spacing on both sides

#### Auth Page UX Polish (P3)
- **FR-020**: Input focus states MUST show transition animations (200ms duration)
- **FR-021**: Button hover states MUST show elevation change (shadow increase, slight scale)
- **FR-022**: Loading states MUST show spinner animation with "Signing in..." or "Creating account..." text
- **FR-023**: Error messages MUST fade in with 150ms transition
- **FR-024**: Success messages MUST show with green background and checkmark icon
- **FR-025**: Form container MUST have subtle hover shadow effect

### Key Entities

- **Profile Dropdown**: Contains logout action, positioned relative to profile icon, auto-closes on outside click or Escape key
- **User Display Name**: Derived from Google profile name OR username (never from email), truncated if longer than 20 characters
- **Auth Page Layout**: Navbar at top, centered auth form container, footer at bottom, consistent spacing
- **Profile Picture**: Google profile picture URL or default User icon, circular shape, 32x32px in navbar, 28x28px in dropdown trigger

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Logout action requires exactly 2 clicks (profile icon → logout button)
- **SC-002**: Profile dropdown opens in <100ms after click
- **SC-003**: 100% of Google OAuth users see their Google profile picture in navbar
- **SC-004**: 100% of users see correct display name (full name or username, never email)
- **SC-005**: Auth page loads with navbar and footer in <2 seconds
- **SC-006**: "Sign in with Google" button is perfectly centered (0px horizontal misalignment)
- **SC-007**: All hover transitions complete within 200ms
- **SC-008**: Profile dropdown is keyboard accessible (Tab, Enter, Escape work correctly)
- **SC-009**: Zero cumulative layout shift (CLS = 0) during auth page interactions

### User Experience Goals

- **SC-010**: Auth page feels modern and professional (polished appearance)
- **SC-011**: Profile dropdown follows familiar patterns (similar to Gmail, GitHub)
- **SC-012**: Navbar and footer create visual consistency with landing page and tasks page
- **SC-013**: Interactive elements provide clear visual feedback on user actions

## Scope *(mandatory)*

### In Scope

- Remove standalone "Logout" button from navbar
- Implement clickable profile dropdown menu with logout option
- Fix username display to show Google name or local username (not email)
- Add navbar to auth page with TaskWave branding
- Add footer to auth page with terms/privacy placeholder links
- Center and align "Sign in with Google" button properly
- Add smooth transitions and hover states to auth page elements
- Implement click-outside and Escape key handlers for dropdown
- Ensure keyboard accessibility (Tab, Enter, Escape)
- Mobile-responsive profile dropdown

### Out of Scope

- Additional dropdown menu items (Settings, Profile, Notifications - future enhancement)
- Actual Terms of Service and Privacy Policy page content
- Complete auth page redesign (only alignment and polish improvements)
- Profile picture editing/upload for email/password users
- User profile management functionality
- Advanced animation libraries (Framer Motion) - use CSS transitions only
- Multi-language support for dropdown menu
- Dark mode toggle in navbar (already handled globally)

## Assumptions

- Profile dropdown pattern is familiar to users (common in modern web apps)
- Tailwind CSS configuration includes all required utility classes
- Lucide React icon library provides suitable default profile icon (User or UserCircle)
- Current navbar component can be modified without breaking other pages
- Auth page can share the same navbar component with conditional rendering
- Users prefer minimal UI (just profile icon) over cluttered navbar with multiple buttons
- Dropdown menu can be implemented with simple React state (no complex state management needed)
- Terms and Privacy links can point to placeholder routes (#terms, #privacy) for now

## Dependencies

- Existing Navbar component
- Current authentication system (useAuth hook)
- Google OAuth profile data (oauth_data JSON field with profile picture URL)
- Tailwind CSS for styling
- Lucide React for icons
- React hooks (useState, useRef, useEffect, useCallback) for dropdown logic
- Click-outside detection utility or custom implementation

## Constraints

- Must not break existing authentication flows
- Must work on mobile and desktop viewports
- Must maintain dark mode compatibility
- Must follow existing design system (colors, spacing, typography)
- Frontend-only changes (no backend API modifications)
- Must load quickly (no heavy JavaScript libraries)
- Must be accessible (WCAG 2.1 AA compliance)

## Risks

- **Risk**: Dropdown position might overflow screen on small viewports
  - **Mitigation**: Auto-adjust dropdown position (show above icon if near bottom of screen)

- **Risk**: Click-outside detection might interfere with other interactive elements
  - **Mitigation**: Use proper event propagation and stopPropagation where needed

- **Risk**: Auth page navbar might look different from other pages if not careful
  - **Mitigation**: Reuse existing Navbar component with minimal conditional logic

- **Risk**: Profile picture might not load (slow network, invalid URL)
  - **Mitigation**: Implement proper onError handler with immediate fallback to icon

- **Risk**: Username truncation might cut off important information
  - **Mitigation**: Use title attribute to show full name on hover

## Acceptance Criteria Summary

**P1 - Critical**:
1. ✓ Standalone logout button removed
2. ✓ Profile dropdown menu functional
3. ✓ Correct username/full name displayed (no email prefix)
4. ✓ Profile picture shown for Google users
5. ✓ Default icon for email/password users
6. ✓ Logout works from dropdown

**P2 - Important**:
7. ✓ Auth page has navbar
8. ✓ Auth page has footer
9. ✓ "Sign in with Google" button aligned
10. ✓ Dropdown closes on outside click

**P3 - Nice-to-have**:
11. ✓ Smooth transitions on interactive elements
12. ✓ Hover states on buttons
13. ✓ Keyboard accessibility

## Notes

- Pure frontend feature - no backend changes
- Reuses existing Navbar component with conditional rendering
- Profile dropdown should be position-aware (adjust if near screen edge)
- Consider extracting dropdown into reusable component for future use
- This sets the foundation for additional dropdown menu items in future (Profile Settings, Preferences, etc.)
