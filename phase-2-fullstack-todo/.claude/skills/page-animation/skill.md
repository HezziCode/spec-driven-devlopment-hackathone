# Page Transition Skill

**Purpose**: Add a lightweight, responsive, and accessible page transition animation for route changes (e.g., Home → Tasks). The animation must be subtle, mobile-safe, respect `prefers-reduced-motion`, and not cause layout shifts or block interactions.

---

## Overview

This skill implements a single, global page transition wrapper and integrates it into the Next.js App Router layout. Prefer a CSS+JS solution using `framer-motion` for clean enter/exit handling; provide a CSS-only fallback if `framer-motion` is not desired.

Key goals:
- Subtle fade + small Y translation on route change
- Fast durations (120–200ms)
- Respect `prefers-reduced-motion: reduce`
- Not blocking on mobile; must remain interactive during/after transition
- Minimal DOM changes; no rerender thrash

---

## Scope

### Included
- `frontend/app/layout.tsx` (wrap children in transition)
- New component: `frontend/components/ui/PageTransition.tsx`
- Optional CSS in `frontend/styles/transitions.css` or `globals.css`
- Add dependency instructions for `framer-motion` (if used)

### Excluded
- Visual redesigns
- Backend changes
- Per-page bespoke animations

---

## Inputs (skill parameters)

- `useFramerMotion` (boolean, default: true) — Use framer-motion `AnimatePresence` + `motion.div`.
- `animation` (string, default: "fade-y") — Options: `fade-y`, `fade`.
- `durationMs` (number, default: 160) — Transition duration in ms (120–200 recommended).
- `yOffset` (number, default: 6) — Vertical offset in px for translateY effect.
- `reducedMotionSafe` (boolean, default: true) — Respect `prefers-reduced-motion`.
- `filesToEdit` (array) — Suggested files to create/edit.

---

## Files to create / edit (suggested)

- `frontend/components/ui/PageTransition.tsx` (new)
- `frontend/app/layout.tsx` (edit — wrap children)
- `frontend/styles/transitions.css` (new or add to `globals.css`)
- Optional: update `package.json` (add `framer-motion`), or include CSS-only fallback

---

## Implementation Steps

1. **Read layout & conventions**  
   - Inspect `frontend/app/layout.tsx`, global CSS, and header components. Keep style tokens consistent.

2. **Create PageTransition component**  
   - If `useFramerMotion=true`, create a client component using `usePathname` from `next/navigation`, `AnimatePresence`, and `motion.div` keyed by pathname.
   - If `useFramerMotion=false`, implement a CSS-only approach keyed by a `data-route` attribute and `opacity/transform` transitions.

3. **Respect reduced motion**  
   - Detect `window.matchMedia('(prefers-reduced-motion: reduce)')` and short-circuit animations to instant apply (no transition).
   - Provide CSS `@media (prefers-reduced-motion: reduce)` rules to disable transitions.

4. **Wrap global layout**  
   - In `app/layout.tsx`, wrap `children` with `<PageTransition>{children}</PageTransition>` so every route change uses the animation.

5. **Ensure accessibility & mobile safety**  
   - Do not disable pointer events during transition.
   - Keep animation durations short (<=200ms).
   - Avoid animating layout dimensions; animate opacity & transform only.

6. **Add fallback CSS**  
   - Provide `.page-enter`, `.page-enter-active`, `.page-exit`, `.page-exit-active` CSS classes for the CSS-only fallback.

7. **Document & test**  
   - Add short comments in the files explaining reduced-motion handling and how to toggle framer-motion usage.
   - Manual test checklist included below.

---

## Example (Framer Motion) — PageTransition.tsx

```tsx
"use client";
import React from "react";
import { usePathname } from "next/navigation";
import { AnimatePresence, motion } from "framer-motion";

export default function PageTransition({
  children,
  duration = 0.16,
  y = 6,
}: {
  children: React.ReactNode;
  duration?: number; // seconds
  y?: number; // px
}) {
  const pathname = usePathname();
  const prefersReducedMotion =
    typeof window !== "undefined" &&
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (prefersReducedMotion) {
    return <>{children}</>;
  }

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={pathname}
        initial={{ opacity: 0, y }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -y }}
        transition={{ duration, ease: "easeOut" }}
        style={{ willChange: "opacity, transform" }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
}
