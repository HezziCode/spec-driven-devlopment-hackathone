# Tasks: Light Theme Boxes Fix

## Feature Overview
Fix theme consistency on the tasks page so that when light theme is enabled, all boxes and components have light background colors instead of dark ones, matching the home/landing page styling.

## Dependencies
- User Story: US-2 (View Tasks) - as this affects the task display components
- User Story: US-7 (Task Search and Filter) - as this affects the filter components

## Implementation Strategy
Address hardcoded dark colors on the tasks page to ensure proper light theme appearance when theme is switched to light mode.

## Phase 1: Setup Tasks
- [x] T001 Create feature directory for light theme boxes fix: specs/features/light-theme-boxes-fix/

## Phase 2: Foundational Tasks
- [x] T002 Review current theme implementation in globals.css
- [x] T003 [P] Identify all components with dark boxes in light theme
- [x] T004 [P] Document current theme variables and Tailwind classes

## Phase 3: [US-2] Fix Task Display Components
- [x] T005 [US-2] Update TaskCard background to be light in light theme
- [x] T006 [US-2] Fix TaskCard text colors for proper light theme contrast
- [x] T007 [US-2] Update TaskCard border colors for light theme consistency
- [x] T008 [US-2] Fix TaskCard priority badges for light theme
- [x] T009 [US-2] Update TaskCard tag styling for light theme

## Phase 4: [US-2/US-7] Fix Tasks Page Layout Components
- [x] T010 [US-2] [US-7] Update stats section cards to be light in light theme
- [x] T011 [US-2] [US-7] Fix task creation form background for light theme
- [x] T012 [US-2] [US-7] Update task filters section for light theme
- [x] T013 [US-2] [US-7] Fix task list container background for light theme
- [x] T014 [US-2] [US-7] Update empty state container for light theme

## Phase 5: [US-2] Fix Global Theme Elements
- [x] T015 [US-2] Remove any hardcoded dark styles that override theme
- [x] T016 [US-2] Ensure body background respects CSS variables properly
- [x] T017 [US-2] Fix any gradient text styling for theme consistency
- [x] T018 [US-2] Update any theme-dependent components to respect light theme

## Phase 6: Cross-cutting Theme Consistency
- [x] T019 Ensure all border colors are theme-consistent
- [x] T020 [P] Ensure all text colors are theme-consistent
- [x] T021 [P] Ensure all hover states respect theme colors
- [x] T022 Test theme switching functionality after all changes

## Phase 7: Polish & Cross-cutting Concerns
- [x] T023 Update documentation to reflect theme consistency patterns
- [x] T024 [P] Add theme consistency tests
- [x] T025 Review and validate all changes work properly in both themes