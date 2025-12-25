---
id: "003"
title: "Responsive UI Specification"
stage: "general"
date_iso: "2025-12-22"
model: "sonnet-4-5-20250929"
feature: "none"
branch: "003-responsive-ui-spec"
user: "user"
command: "sp.specify"
labels: ["responsive", "ui-ux", "mobile", "frontend"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml: |
  - specs/003-responsive-ui-spec/spec.md
  - specs/003-responsive-ui-spec/checklists/requirements.md
tests_yaml: |
  - Mobile responsiveness testing
  - Tablet responsiveness testing
  - Desktop compatibility verification
---

# Responsive UI Specification

## Overview
This prompt documents the specification for making the TaskFlow dashboard responsive, with a focus on mobile and short-height screens while preserving the desktop experience.

## Feature Description
The feature aims to audit, refactor, and validate frontend code with a strict focus on full responsiveness, prioritizing mobile and short-height screens over desktop aesthetics. The implementation should ensure the UI is clear, usable, touch-friendly, and visually stable across:
- Mobile (320px–480px)
- Small tablets (600px–768px)
- Short-height screens (≤700px height)
- Desktop

## Specification Requirements
The implementation must follow these non-negotiable rules:
1. Mobile-first approach with base styles optimized for mobile
2. Support for short screens (≤700px height) without forced centering
3. No horizontal overflow on any device
4. Touch-friendly interactions with minimum 44px tap targets
5. Layout simplification to ensure stability across devices

## Allowed Changes
- Adjust layout structure
- Modify spacing, padding, margins
- Change flex/grid behavior across breakpoints
- Scale typography responsibly
- Remove fixed heights and widths
- Add responsive utility classes
- Clamp text and normalize containers

## Forbidden Changes
- Adding new features
- Changing API behavior
- Introducing new UI concepts
- Redesigning visuals beyond responsiveness fixes
- Preserving broken layouts for "desktop beauty"

## Container Standard
All pages must use the consistent max-width container pattern:
```tsx
w-full px-4 sm:px-6 lg:px-8 max-w-6xl mx-auto
```

## Outcome
The specification provides clear guidelines for making the TaskFlow dashboard responsive while maintaining the existing desktop experience. The focus is on mobile-first design principles while ensuring compatibility across all device sizes and screen heights.