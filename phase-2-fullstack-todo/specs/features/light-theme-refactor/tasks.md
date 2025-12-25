# Tasks: Light Theme Refactor

## Feature Overview
Comprehensive refactor of the Task page to eliminate all hard-coded dark backgrounds and implement proper theme-aware styling. Every background color must be conditional to ensure light theme is 100% light with no dark elements.

## Dependencies
- User Story: US-2 (View Tasks) - as this affects the task display components
- User Story: US-7 (Task Search and Filter) - as this affects the filter components

## Implementation Strategy
Replace all fixed dark background classes (bg-slate-800, bg-slate-900, bg-slate-700) with conditional theme-aware classes (bg-white dark:bg-slate-800). Audit all components on the Task page to ensure 100% light theme compliance.

## Phase 1: Setup Tasks
- [x] T001 Create feature directory for light theme refactor: specs/features/light-theme-refactor/

## Phase 2: Foundational Tasks
- [ ] T002 Audit all components on Task page for hard-coded dark backgrounds
- [ ] T003 [P] Document all fixed dark classes that need replacement
- [ ] T004 [P] Create theme consistency guidelines for future development

## Phase 3: [US-2] Refactor Task Display Components
- [ ] T005 [US-2] Replace hard-coded dark backgrounds in TaskCard component
- [ ] T006 [US-2] Update TaskCard text colors to be theme-aware
- [ ] T007 [US-2] Fix TaskCard border colors for proper theme consistency
- [ ] T008 [US-2] Update TaskCard priority badges to use conditional classes
- [ ] T009 [US-2] Refactor TaskCard tag styling to be theme-aware

## Phase 4: [US-2/US-7] Refactor Tasks Page Layout Components
- [ ] T010 [US-2] [US-7] Replace hard-coded dark backgrounds in stats cards
- [ ] T011 [US-2] [US-7] Refactor task creation form to use conditional backgrounds
- [ ] T012 [US-2] [US-7] Update task filters section to be theme-aware
- [ ] T013 [US-2] [US-7] Fix task list container backgrounds for theme consistency
- [ ] T014 [US-2] [US-7] Update empty state container to use conditional classes

## Phase 5: [US-2] Refactor Global Theme Elements
- [ ] T015 [US-2] Remove any remaining hardcoded dark styles that override theme
- [ ] T016 [US-2] Ensure all input fields use proper conditional backgrounds
- [ ] T017 [US-2] Update all dropdowns and selects to be theme-aware
- [ ] T018 [US-2] Refactor any theme-dependent components to use conditional classes

## Phase 6: Cross-cutting Theme Consistency
- [ ] T019 Replace all fixed bg-slate-800 classes with bg-white dark:bg-slate-800
- [ ] T020 [P] Replace all fixed bg-slate-900 classes with bg-white dark:bg-slate-900
- [ ] T021 [P] Replace all fixed bg-slate-700 classes with bg-gray-100 dark:bg-slate-700
- [ ] T022 Test theme switching functionality after all changes

## Phase 7: Polish & Cross-cutting Concerns
- [ ] T023 Update documentation to reflect new theme consistency patterns
- [ ] T024 [P] Add theme consistency tests to prevent future regressions
- [ ] T025 Review and validate all changes work properly in both themes