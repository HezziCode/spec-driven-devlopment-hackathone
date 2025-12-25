# Light Theme Refactor Specification

## Overview
This feature addresses the fundamental issue where the light theme is broken on the Task page. Multiple UI elements remain dark even when light mode is active because dark background colors are hard-coded into components. This refactor will ensure every background color is theme-aware, with light theme showing white/light gray and dark theme showing dark slate.

## User Stories

### US-1: Complete Theme Awareness
**As a** user
**I want** all UI elements on the Task page to properly respect the selected theme
**So that** when I select light theme, everything appears light, and when I select dark theme, everything appears dark

**Acceptance Criteria:**
- All cards use bg-white in light theme and dark:bg-slate-800 in dark theme
- All forms use bg-white in light theme and dark:bg-slate-800 in dark theme
- All containers use bg-white in light theme and dark:bg-slate-800 in dark theme
- No fixed dark classes like bg-slate-800 exist without light theme counterpart
- Theme switching works seamlessly without mixed UI states

### US-2: Consistent Light Theme Experience
**As a** user
**I want** the Task page to have consistent light theme appearance like the homepage
**So that** I have a uniform experience across the application

**Acceptance Criteria:**
- Stats cards appear with light backgrounds in light theme
- "Add New Task" form appears with light background in light theme
- Task filters appear with light background in light theme
- Task cards appear with light backgrounds in light theme
- All elements are 100% light when light theme is active

## Constraints
- Must maintain accessibility standards (proper contrast ratios)
- Should not affect dark theme functionality
- Changes should follow Tailwind's dark mode convention (bg-white dark:bg-slate-800)

## Success Metrics
- Zero hard-coded dark backgrounds remain on Task page in light theme
- All components properly switch between light and dark themes
- Consistent appearance with homepage theme behavior
- Proper contrast ratios maintained in both themes