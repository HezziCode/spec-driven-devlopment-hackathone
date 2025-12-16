# Tasks: Remove Extra Background from Hero Section

**Feature**: Remove extra background from hero section in LandingPage
**Branch**: `007-hero-bg-removal` | **Date**: 2025-12-16 | **Spec**: [specs/features/hero-section-removal.md](../features/hero-section-removal.md)
**Input**: User request to remove extra background in hero section

## Summary

Implementation of UI modification to remove the extra background styling from the hero section in the LandingPage component, allowing the site's background to show through without the card-like background effect.

## Implementation Strategy

**MVP Scope**: Modify the hero section styling to remove the background color while maintaining proper spacing and readability.

**Phase 1**: Setup and research tasks
**Phase 2**: Foundational UI changes
**Phase 3**: User Story 1 - Update Landing Page Hero Section
**Final Phase**: Polish and testing

## Dependencies

- LandingPage component styling needs to be updated
- Global styles should remain consistent
- Text contrast must remain adequate for readability

## Parallel Execution Opportunities

- Multiple styling changes can be made in parallel across different sections of the LandingPage component

---

## Phase 1: Setup

- [ ] T001 Research current LandingPage component structure and hero section styling
- [ ] T002 Identify all styling that affects the hero section background

## Phase 2: Foundational Changes

- [X] T003 [P] Remove background styling from hero section container in LandingPage component
- [X] T004 [P] Update hero section container to use transparent background instead of card-style background
- [X] T005 [P] Ensure proper spacing and padding remain after background removal
- [X] T006 [P] Update any backdrop-blur effects that may be unnecessary after background removal

## Phase 3: [US1] Update Landing Page Hero Section

- [X] T007 [US1] Remove background color from hero section in `frontend/components/LandingPage.tsx`
- [X] T008 [US1] Adjust hero section styling to maintain readability without background card
- [X] T009 [US1] Ensure "Ride the TaskWave" heading remains visible and readable
- [X] T010 [US1] Test hero section appearance with both light and dark modes
- [X] T011 [US1] Verify that site background color shows through properly in hero section

## Phase 4: Polish & Cross-Cutting Concerns

- [X] T012 [P] Test hero section appearance across different screen sizes and devices
- [X] T013 [P] Ensure text contrast remains adequate without background card
- [X] T014 [P] Review and adjust any visual elements that may need adjustment after background removal
- [X] T015 [P] Verify that the global cursor glow effect does not interfere with hero section text
- [X] T016 Run visual regression tests to ensure no unintended UI changes

## Independent Test Criteria

Each user story has independently testable criteria:

**US1 Test Criteria:**
- Hero section displays with site background color instead of card background
- Text remains readable and properly positioned
- Both light and dark modes work correctly
- Global cursor glow does not interfere with text visibility

## Implementation Notes

- The main change will be in the hero section container in LandingPage.tsx
- Need to maintain proper spacing and ensure text remains readable
- Should preserve the gradient text effect for "TaskWave" heading
- Need to ensure the change works in both light and dark modes