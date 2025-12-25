name: enforce_full_responsiveness
title: Enforce Full Website Responsiveness (Mobile & Short Screens)
description: |
  Audit and refactor the entire frontend to ensure pixel-clear responsiveness across:
  - Mobile (320px–480px)
  - Small tablets (600px–768px)
  - Short-height screens (≤700px height laptops)
  - Standard desktop

  This skill applies consistent responsive rules across ALL pages, layouts, and components.
  No new features. No backend changes. No visual redesign beyond layout, spacing, and sizing fixes.
  The goal is clarity, hierarchy, and usability on constrained screens.

tags:
  - frontend
  - responsive
  - mobile-first
  - tailwind
  - nextjs
  - ui-polish

inputs:
  mobileFirst:
    type: boolean
    required: false
    default: true
    description: "Force mobile-first layout decisions (base styles = mobile)."

  minTapTarget:
    type: number
    required: false
    default: 44
    description: "Minimum tap target size in px for buttons and interactive elements."

  maxContentWidth:
    type: string
    required: false
    default: "max-w-6xl"
    description: "Max width container for large screens."

  filesScope:
    type: array
    required: false
    default:
      - "frontend/app/**"
      - "frontend/components/**"
      - "frontend/styles/**"
      - "frontend/lib/**"
    description: "Frontend paths to audit and refactor."

outputs:
  changed_files:
    type: array
    description: "List of modified files with brief reason for each."

  responsive_report:
    type: object
    description: |
      Summary of fixes applied:
        - layout_fixes
        - spacing_fixes
        - typography_scaling
        - overflow_issues_removed
        - mobile_nav_adjustments
        - short_screen_fixes

run:
  - step: "Read global frontend context"
    instructions: |
      Read:
        - frontend/CLAUDE.md
        - Root layout (frontend/app/layout.tsx)
        - Global styles (globals.css or equivalent)
      Identify shared layout components (Header, Footer, Sidebar, Containers).

  - step: "Define responsive baseline (mobile-first)"
    instructions: |
      Enforce these global rules:
        - Base styles target mobile screens by default.
        - Use responsive prefixes (`sm:`, `md:`, `lg:`) only to enhance, not fix broken mobile UI.
        - Remove fixed heights unless strictly required.
        - Replace width/height hard values with `min-`, `max-`, or content-based sizing.

  - step: "Container & layout normalization"
    instructions: |
      Refactor all page-level layouts to:
        - Wrap content in a consistent container:
            `w-full px-4 sm:px-6 lg:px-8 {maxContentWidth} mx-auto`
        - Prevent horizontal overflow (`overflow-x-hidden` at layout root).
        - Stack columns vertically on small screens:
            `flex-col md:flex-row`
        - Remove multi-column grids below `md`.

  - step: "Typography scaling"
    instructions: |
      Normalize typography across the site:
        - Headings:
            h1: text-2xl sm:text-3xl lg:text-4xl
            h2: text-xl sm:text-2xl lg:text-3xl
        - Body text:
            text-sm sm:text-base
        - Remove any text below `text-sm` for readability.
        - Ensure line-height is ≥ `leading-relaxed` on mobile.

  - step: "Buttons & tap targets"
    instructions: |
      Enforce minimum tap targets:
        - All buttons/links must be ≥ minTapTarget px height.
        - Replace icon-only buttons with icon + accessible label on mobile OR add aria-label.
        - Ensure spacing between stacked buttons: `gap-2` minimum.
      Shrink visual size without reducing tap area using padding + font-size separation.

  - step: "Forms responsiveness"
    instructions: |
      Refactor all forms to:
        - Stack fields vertically on mobile.
        - Avoid side-by-side inputs below `md`.
        - Use full-width inputs and buttons on mobile.
        - Prevent keyboard overlap issues:
            - Avoid fixed bottom elements unless sticky + safe-area aware.
      Ensure error messages wrap and do not overflow.

  - step: "Navigation & header behavior"
    instructions: |
      Audit header/navigation:
        - Collapse nav items into menu or stacked layout on small screens.
        - Remove horizontal scrolling navs.
        - Ensure logo + primary action fit in one row at 320px.
        - Reduce header height on short screens.

  - step: "Short-height screen fixes (≤700px height)"
    instructions: |
      Apply special fixes for short screens:
        - Remove large vertical paddings (`py-24`, `min-h-screen`) where not needed.
        - Avoid vertically centered hero sections.
        - Allow content to scroll naturally.
        - Convert tall hero sections into compact headers.
      Use `@media (max-height: 700px)` only if absolutely required.

  - step: "Task-heavy pages (lists, cards)"
    instructions: |
      For lists (Tasks, etc.):
        - Reduce card padding on mobile.
        - Switch cards to flat list rows on small screens.
        - Truncate long text with line clamp.
        - Ensure actions remain visible without hover (hover is not mobile).

  - step: "Overflow & breakage audit"
    instructions: |
      Find and fix:
        - Horizontal scrolling issues.
        - Elements overflowing viewport width.
        - Images without `max-w-full`.
        - SVGs without responsive sizing.
      Replace absolute positioning causing overflow.

  - step: "Accessibility & clarity pass"
    instructions: |
      Ensure:
        - Focus states visible on mobile.
        - No reliance on hover for critical actions.
        - Sufficient color contrast on small screens.
        - Touch-friendly spacing.

  - step: "Manual responsive checklist (must pass)"
    instructions: |
      Validate manually:
        - 320x568 (small mobile)
        - 390x844 (modern mobile)
        - 768x1024 (tablet)
        - 1366x700 (short laptop)

      Required outcomes:
        - No horizontal scroll
        - No clipped text
        - All actions reachable
        - Clear visual hierarchy

  - step: "Output report"
    instructions: |
      Return:
        - List of modified files with one-line reason each
        - Responsive report summarizing categories of fixes
      Do NOT add new features or visuals. This is refinement only.

examples:
  - title: "Default full-site responsiveness pass"
    input:
      mobileFirst: true
      minTapTarget: 44
      maxContentWidth: "max-w-6xl"
    expected_result_summary: |
      - Layouts stack cleanly on mobile
      - Typography scales correctly
      - No overflow on small or short screens
      - Forms and buttons usable with one hand
      - UI remains consistent with existing theme

notes: |
  - This skill is non-negotiable polish. If a component breaks on mobile, fix it.
  - Prefer deleting layout complexity over preserving it.
  - If a section looks fine on desktop but bad on mobile, desktop loses.
  - Do not ask for clarification unless something is technically impossible.








# Enforce Full Website Responsiveness Skill

**Purpose**: Audit and refactor the entire frontend to ensure pixel-clear responsiveness across mobile devices, small tablets, short-height screens, and standard desktops—without adding new features or changing backend logic.

---

## Overview

This skill enforces **consistent, production-grade responsiveness** across the full frontend codebase.

It applies strict responsive rules to **all pages, layouts, and components** to ensure:
- Clear visual hierarchy
- Touch-friendly interactions
- No overflow or clipping
- Usability on constrained screens

This is a **UI polish and refinement skill**, not a feature-development skill.

---

## Target Devices & Screens

### Width-Based Targets

| Device | Width |
|------|------|
| Mobile | 320px – 480px |
| Small Tablets | 600px – 768px |
| Desktop | ≥1024px |

### Height-Based Targets (Critical)

| Screen Type | Height |
|------------|--------|
| Short Screens (laptops, split view) | ≤700px |

Short-height screens must **never** hide CTAs, break layouts, or force awkward vertical centering.

---

## Scope

### Included
- `frontend/app/**`
- `frontend/components/**`
- `frontend/styles/**`
- `frontend/lib/**`
- Shared layouts, headers, navigation, footers
- Forms, lists, cards, task-heavy UI

### Excluded
- Backend changes
- API behavior
- New features
- Visual redesign beyond layout, spacing, and sizing fixes

---

## Global Configuration Defaults

- **Mobile-first**: Enabled
- **Minimum tap target**: 44px
- **Max content width**: `max-w-6xl`

---

## Core Responsiveness Rules

### 1. Mobile-First Baseline

**Rules**:
- Base styles must target mobile screens
- Responsive prefixes (`sm:`, `md:`, `lg:`) are enhancements only
- Never “fix” mobile by overriding desktop layouts

**Required Pattern**:
```tsx
<div className="flex flex-col md:flex-row">
 