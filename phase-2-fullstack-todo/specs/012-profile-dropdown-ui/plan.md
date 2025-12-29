# Implementation Plan: Profile Dropdown Menu and Auth Page UI Enhancement

**Branch**: `012-profile-dropdown-ui` | **Date**: 2025-12-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/012-profile-dropdown-ui/spec.md`

## Summary

Enhance the application's user interface by implementing a profile dropdown menu for logout functionality, fixing the username display issue in the navbar, adding navbar and footer to the authentication page, and improving the overall UI/UX polish with smooth transitions and proper alignment. This is a pure frontend enhancement requiring no backend API changes.

## Technical Context

**Language/Version**: TypeScript with React 18+, Next.js 16+
**Primary Dependencies**: React (hooks: useState, useRef, useEffect, useCallback), Lucide React (icons), Tailwind CSS (styling), Next.js (routing, Link component)
**Storage**: LocalStorage for user session data (existing)
**Testing**: Manual testing (visual verification), optional Jest/Vitest for component tests
**Target Platform**: Web browsers (Chrome, Firefox, Safari, Edge) on desktop and mobile
**Project Type**: Frontend-only enhancement to existing full-stack application
**Performance Goals**: Dropdown opens <100ms, transitions complete <200ms, zero cumulative layout shift
**Constraints**: Must maintain dark mode compatibility; must not break existing responsive design; must reuse existing components where possible
**Scale/Scope**: Single-user UI enhancement affecting navbar and auth page only; no database or API changes

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Spec-Driven Development (SDD) Check
- [X] Feature has complete specification (spec.md) → **PASS**
- [X] All agents/skills documented → **PASS**
- [X] No manual code writing → **PASS**

### ✅ Clean Code with SRP Check
- [X] Single responsibility per module → **PASS**
- [X] Comprehensive docstrings → **PASS**
- [X] Short, focused functions → **PASS**

### ✅ Type Safety Check
- [X] No 'any' types → **PASS**
- [X] Strict mode → **PASS**

### ✅ Accessibility Check
- [X] Semantic HTML → **PASS**
- [X] Keyboard navigation → **PASS**
- [X] Screen reader compatible → **PASS**

### ✅ Performance Check
- [X] O(1) operations → **PASS**
- [X] Fast rendering → **PASS**
- [X] Zero layout shift → **PASS**

### ✅ Modular Architecture Check
- [X] Clear separation → **PASS**
- [X] Reusable components → **PASS**

**Constitution Gate**: ✅ **PASS**

## Implementation Strategy

### Components

**ProfileDropdown.tsx**: Clickable dropdown with logout
**Footer.tsx**: Footer with terms/privacy links
**getUserDisplayName()**: Extract name from oauth_data

### Modifications

**Navbar.tsx**: Replace logout button with ProfileDropdown
**app/auth/page.tsx**: Add navbar, footer, fix Google button alignment

## Next Steps

Run `/sp.tasks` to generate implementation tasks

## Notes

- Pure frontend enhancement
- No backend changes
- Estimated time: 2-3 hours
- Can be deployed independently
