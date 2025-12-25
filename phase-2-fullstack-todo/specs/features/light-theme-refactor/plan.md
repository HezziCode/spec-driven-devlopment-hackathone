# Implementation Plan: Light Theme Refactor

## Summary
Complete refactor of the Task page to eliminate all hard-coded dark backgrounds and implement proper theme-aware styling. Every background color must be conditional to ensure light theme is 100% light with no dark elements. This addresses the fundamental issue where light mode still displays dark UI elements.

## Technical Context
**Language/Version**: TypeScript, Next.js 16+
**Primary Dependencies**: Tailwind CSS, React
**Target Platform**: Web application (browser-based)
**Performance Goals**: Minimal impact on rendering performance
**Constraints**: Maintain accessibility standards, preserve existing functionality

## Project Structure
### Documentation
```text
specs/features/light-theme-refactor/
├── spec.md              # Feature requirements
├── plan.md              # This file
└── tasks.md             # Implementation tasks
```

### Source Code (existing)
```text
frontend/
├── app/tasks/page.tsx           # Main tasks page with hard-coded dark backgrounds
├── components/TaskCard.tsx      # Task card component with hard-coded dark backgrounds
├── components/TaskForm.tsx      # Task form component with hard-coded dark backgrounds
├── app/globals.css              # Theme variables and CSS
└── tailwind.config.js           # Tailwind configuration
```

## Implementation Sequence

### Phase 0: Research and Setup
- Audit all components on Task page for hard-coded dark backgrounds
- Identify all instances of bg-slate-800, bg-slate-900, bg-slate-700 classes
- Document all fixed dark classes that need replacement

### Phase 1: Component Refactors
- Update TaskCard component to use conditional theme classes
- Refactor TaskForm component to use conditional backgrounds
- Update stats section cards to use conditional classes
- Update form and filter components to use theme-aware styling

### Phase 2: Global Refactors
- Replace all fixed dark background classes with conditional ones
- Ensure all components properly respect theme variables
- Test theme switching functionality

### Phase 3: Validation
- Verify all components display correctly in both themes
- Ensure accessibility standards are maintained
- Test cross-browser compatibility

## Agent and Skill Usage
- **frontend-feature-builder agent**: For implementing the component refactors
- **frontend-component skill**: For updating Next.js components with proper theme handling

## Complexity Tracking
| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Multiple component changes | Task page has multiple components with hard-coded dark backgrounds | Would leave some elements with incorrect theme behavior |