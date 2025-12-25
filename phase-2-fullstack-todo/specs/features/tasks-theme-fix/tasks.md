# Tasks: Theme Consistency Fix for Tasks Page

## Feature Overview
Fix theme consistency on the tasks page so that when light theme is enabled, all boxes and components match the light theme styling used on the home/landing page.

## Dependencies
- User Story: US-2 (View Tasks) - as this affects the task display components
- User Story: US-7 (Task Search and Filter) - as this affects the filter components

## Implementation Strategy
Address hardcoded colors and inconsistent theme usage on the tasks page to ensure proper light/dark mode switching.

## Phase 1: Setup Tasks
- [x] T001 Create feature directory for theme fix tasks: specs/features/tasks-theme-fix/

## Phase 2: Foundational Tasks
- [x] T002 Review current theme implementation across the application
- [x] T003 [P] Document all theme-related CSS variables and Tailwind classes used in globals.css
- [x] T004 [P] Identify all components that need theme consistency fixes

## Phase 3: [US-2] Fix Task Display Components Theme
- [x] T005 [US-2] Update TaskCard component to use consistent theme variables instead of hardcoded colors
- [x] T006 [US-2] Fix TaskCard background colors to properly switch between light/dark modes
- [x] T007 [US-2] Update TaskCard priority badges to use consistent theme colors
- [x] T008 [US-2] Fix TaskCard tag styling for theme consistency
- [x] T009 [US-2] Update TaskCard completion button styling for theme consistency

## Phase 4: [US-2/US-7] Fix Tasks Page Layout Theme
- [x] T010 [US-2] [US-7] Update stats section cards to use consistent theme variables
- [x] T011 [US-2] [US-7] Fix task creation form background and input styling for theme consistency
- [x] T012 [US-2] [US-7] Update task filters section to use consistent theme variables
- [x] T013 [US-2] [US-7] Fix task list container background for theme consistency
- [x] T014 [US-2] [US-7] Update empty state container to use consistent theme variables

## Phase 5: [US-2] Fix Global Theme Elements on Tasks Page
- [x] T015 [US-2] Remove hardcoded inline styles in GlobalStyles component that override theme
- [x] T016 [US-2] Update body background color to use CSS variables instead of hardcoded values
- [x] T017 [US-2] Fix gradient text styling to be consistent with landing page implementation
- [x] T018 [US-2] Update CursorGlow component to respect theme colors properly

## Phase 6: Cross-cutting Theme Consistency
- [x] T019 Ensure all border colors use theme variables consistently
- [x] T020 [P] Ensure all text colors use theme variables consistently
- [x] T021 [P] Ensure all shadow and hover states respect theme colors
- [x] T022 Test theme switching functionality on tasks page after all changes

## Phase 7: Polish & Cross-cutting Concerns
- [x] T023 Update documentation to reflect theme consistency patterns
- [x] T024 [P] Add theme consistency tests to ensure future changes maintain consistency
- [x] T025 Review and validate all changes work properly in both light and dark modes