# Hero Section Background Modification Feature Specification

## Overview
This feature implements a UI modification to remove the background color of the hero section in the LandingPage component. Currently, the hero section has a card-style background that creates visual separation from the site's background. This change will make the hero section transparent so that the site's background color shows through, creating a more seamless visual experience.

## User Stories

### US-1: Remove Hero Section Background
**As a** website visitor
**I want to** see the hero section blend with the site's background color
**So that** the page has a more cohesive and modern design

**Acceptance Criteria:**
- Hero section background is removed, showing site background color
- "Ride the TaskWave" heading remains clearly visible and readable
- Text contrast remains adequate in both light and dark modes
- The gradient text effect for "TaskWave" continues to work properly
- Global cursor glow effect does not interfere with text visibility
- Spacing and layout remain consistent with the rest of the page

## Constraints
- Text must remain readable and accessible (WCAG 2.1 AA compliance)
- Both light and dark modes must work correctly
- The "Ride the TaskWave" heading gradient effect must be preserved
- Global cursor glow effect should not interfere with text

## Assumptions
- The hero section is in the LandingPage component
- The site background is handled by global styles
- The "Ride the TaskWave" text uses gradient styling
- The current implementation uses a card-style container with background color