---
id: 002
title: Profile Dropdown UI Implementation Planning
stage: plan
date: 2025-12-27
surface: agent
model: claude-sonnet-4-5
feature: 012-profile-dropdown-ui
branch: 012-profile-dropdown-ui
user: huzaifasys
command: /sp.plan
labels: ["ui-planning", "frontend-architecture", "component-design"]
links:
  spec: /mnt/d/Side Projects/giaic-hackathone/specs/012-profile-dropdown-ui/spec.md
  plan: /mnt/d/Side Projects/giaic-hackathone/specs/012-profile-dropdown-ui/plan.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/012-profile-dropdown-ui/plan.md
 - specs/012-profile-dropdown-ui/research.md
 - specs/012-profile-dropdown-ui/quickstart.md
tests:
 - Constitution check passed (all 6 principles satisfied)
 - Component design validated for accessibility and performance
---

## Prompt

User requested implementation planning for profile dropdown menu and auth page UI enhancement feature after successful specification creation.

## Response snapshot

### Implementation Plan Created

**Technical Approach**:
- Pure frontend enhancement (no backend changes)
- Reuse existing Navbar component with ProfileDropdown integration
- Create new Footer component for consistency
- Extract username display logic into utility function

**Key Components**:
1. **ProfileDropdown.tsx** (NEW):
   - Clickable profile picture/icon trigger
   - Dropdown menu with "Logout" option
   - Click-outside detection using custom hook
   - Keyboard navigation (Tab, Enter, Escape)
   - ARIA attributes for accessibility

2. **Footer.tsx** (NEW):
   - Terms of Service and Privacy Policy links (placeholders)
   - Copyright notice with current year
   - Responsive design for mobile

3. **getUserDisplayName()** (NEW):
   - Extract full name from oauth_data.name
   - Fallback to username
   - Tertiary fallback to email prefix

**Modified Components**:
1. **Navbar.tsx**:
   - Remove standalone logout button
   - Integrate ProfileDropdown
   - Fix username display to use getUserDisplayName()

2. **app/auth/page.tsx**:
   - Add Navbar at top
   - Add Footer at bottom
   - Center Google OAuth button
   - Fix button width alignment
   - Improve spacing and transitions

### Architecture Decisions

**Decision 1**: Dropdown implementation without library
- **Rationale**: Lightweight, full control, no dependencies
- **Tradeoff**: Slightly more code vs adding heavy UI library

**Decision 2**: Reuse existing Navbar for auth page
- **Rationale**: Design consistency, avoid duplication
- **Tradeoff**: Need conditional rendering logic vs separate component

**Decision 3**: CSS transitions only (no Framer Motion)
- **Rationale**: Faster, smaller bundle, sufficient for smooth animations
- **Tradeoff**: Less powerful animations vs bundle size

**Decision 4**: Custom click-outside hook
- **Rationale**: Reusable pattern, type-safe, standard React
- **Tradeoff**: 10-15 lines of code vs importing library

### Constitution Validation

✅ All 6 core principles satisfied:
1. SDD: Using agents/skills for implementation
2. Clean Code: SRP for each component
3. Type Safety: No 'any' types, strict TypeScript
4. Accessibility: ARIA, keyboard nav, WCAG 2.1 AA
5. Performance: O(1) operations, CSS transitions
6. Modular: Clear component boundaries, reusable

### Critical Files Identified

**P1 (Core)**:
- frontend/components/ProfileDropdown.tsx
- frontend/components/Navbar.tsx
- frontend/lib/utils/getUserDisplayName.ts

**P2 (Consistency)**:
- frontend/components/Footer.tsx
- frontend/app/auth/page.tsx

## Outcome

- ✅ Impact: Complete implementation plan ready for task generation
- 🧪 Tests: Constitution check passed (6/6 principles)
- 📁 Files: 3 files created (plan.md, research.md, quickstart.md)
- 🔁 Next steps: Run `/sp.tasks` to generate task breakdown
- 🧠 Reflection: Straightforward UI enhancement with clear component separation. No complex state management needed. All decisions made with standard React/Next.js patterns.

## Evaluation notes

- No architectural decisions requiring ADR (standard UI patterns)
- Implementation can proceed directly after task generation
- Estimated 10-12 tasks total across 3 phases (components, integration, polish)
