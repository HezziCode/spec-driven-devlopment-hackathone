# Tasks: Remove Hero Section Background Color

**Feature**: Remove background color from hero section to use site background color
**Branch**: `004-hero-bg-removal` | **Date**: 2025-12-16 | **Spec**: [specs/features/hero-section.md](../features/hero-section.md)
**Input**: User request to remove hero section background color and use site background instead

## Summary

Implementation of UI modification to remove the background color of the hero section in the LandingPage component, allowing the site's background color to show through instead of the current card-style background. This will create a more seamless visual experience with the rest of the page.

## Implementation Strategy

**MVP Scope**: Modify the hero section styling to remove the background color while maintaining readability and proper spacing.

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

- [ ] T001 Create feature branch `004-hero-bg-removal` and setup development environment
- [ ] T002 Research current LandingPage component structure and styling implementation
- [ ] T003 Identify all styling that affects the hero section background
- [ ] T004 Analyze the "Ride the TaskWave" heading and its gradient styling

## Phase 2: Foundational Changes

- [ ] T005 [P] Remove background styling from hero section container in LandingPage component
- [ ] T006 [P] Update hero section container to use transparent background instead of card-style background
- [ ] T007 [P] Ensure proper spacing and padding remain after background removal
- [ ] T008 [P] Update any backdrop-blur effects that may be unnecessary after background removal
- [ ] T009 [P] Verify text contrast remains adequate without background card

## Phase 3: [US1] Update Landing Page Hero Section

- [ ] T010 [US1] Remove background color from hero section in `frontend/components/LandingPage.tsx`
- [ ] T011 [US1] Adjust hero section styling to maintain readability without background card
- [ ] T012 [US1] Ensure "Ride the TaskWave" heading remains visible and readable
- [ ] T013 [US1] Test hero section appearance with both light and dark modes
- [ ] T014 [US1] Verify that site background color shows through properly in hero section
- [ ] T015 [US1] Update the hero section container classes to remove card-like styling

## Phase 4: Polish & Cross-Cutting Concerns

- [ ] T016 [P] Test hero section appearance across different screen sizes and devices
- [ ] T017 [P] Ensure text contrast remains adequate without background card in all conditions
- [ ] T018 [P] Review and adjust any visual elements that may need adjustment after background removal
- [ ] T019 [P] Verify that the global cursor glow effect does not interfere with hero section text
- [ ] T020 [P] Check that the gradient text effect for "TaskWave" still works properly
- [ ] T021 Update documentation if any component interfaces change
- [ ] T022 Run visual regression tests to ensure no unintended UI changes

## Independent Test Criteria

Each user story has independently testable criteria:

**US1 Test Criteria:**
- Hero section displays with site background color instead of card background
- Text remains readable and properly positioned
- Both light and dark modes work correctly
- Global cursor glow does not interfere with text visibility
- The "Ride the TaskWave" heading is clearly visible with its gradient effect

## Implementation Notes

- The main change will be in the hero section container (around line 71-75 in LandingPage.tsx)
- Need to maintain proper spacing and ensure text remains readable
- Should preserve the gradient text effect for "TaskWave" heading
- Need to ensure the change works in both light and dark modes
- Verify that the global cursor glow effect doesn't interfere with text readability