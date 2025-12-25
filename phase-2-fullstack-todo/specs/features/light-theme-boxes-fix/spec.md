# Light Theme Boxes Fix Specification

## Overview
This feature addresses the issue where boxes and components on the tasks page remain dark even when the light theme is enabled. The goal is to ensure all UI elements properly switch to light theme colors when the theme is set to light mode.

## User Stories

### US-1: Light Theme Consistency
**As a** user
**I want** the tasks page to properly display light theme colors when light theme is selected
**So that** the UI is consistent with the home/landing page and easier on the eyes in light mode

**Acceptance Criteria:**
- When light theme is enabled, all boxes on the tasks page appear with light backgrounds
- Text colors maintain proper contrast in light theme
- Border colors are consistent with light theme
- No elements remain dark when light theme is active

### US-2: Theme Switching Consistency
**As a** user
**I want** to switch between light and dark themes seamlessly on the tasks page
**So that** I can choose the theme that works best for my environment

**Acceptance Criteria:**
- Theme switching works consistently across all components
- No hardcoded colors override the theme system
- All components respect the theme setting properly

## Constraints
- Must maintain accessibility standards (proper contrast ratios)
- Should not affect dark theme functionality
- Changes should be consistent with existing theme implementation patterns

## Success Metrics
- All boxes and containers use appropriate light colors in light theme
- Text remains readable with proper contrast in both themes
- Theme switching works smoothly without visual glitches