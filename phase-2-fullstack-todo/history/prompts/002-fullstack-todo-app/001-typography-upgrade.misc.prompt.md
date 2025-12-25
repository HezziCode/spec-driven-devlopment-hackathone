---
id: 1
title: Typography Upgrade
stage: misc
date: 2025-12-18
surface: agent
model: claude-sonnet-4-5-20250929
feature: 002-fullstack-todo-app
branch: 002-fullstack-todo-app
user: claude
command: "Upgrade typography system to IBM Plex Sans + DM Sans"
labels: ["typography", "design", "fonts", "ui"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - /mnt/d/Side Projects/giaic-hackathone/phase-2-fullstack-todo/frontend/app/layout.tsx
 - /mnt/d/Side Projects/giaic-hackathone/phase-2-fullstack-todo/frontend/app/globals.css
 - /mnt/d/Side Projects/giaic-hackathone/phase-2-fullstack-todo/frontend/tailwind.config.js
 - /mnt/d/Side Projects/giaic-hackathone/phase-2-fullstack-todo/frontend/components/TaskCard.tsx
tests:
 - null
---

## Prompt

Act as a senior product designer and typography specialist.

I have a Next.js (App Router) application using Tailwind CSS.
The app currently uses Inter as the global sans-serif font via next/font/google and CSS variables.

🎯 Goal

Upgrade the typography system to feel:

Premium

Professional

Calm

Modern SaaS

Editorial-quality (not generic)

This is not just a font swap — it is a typography system upgrade.

🧠 Typography Strategy (MANDATORY)

Use two-font system:

Primary UI / body font → ultra-readable, neutral

Display / heading font → distinctive but restrained

Fonts must:

Be production-safe

Work well in dashboards

Look good at small sizes

Feel professional, not trendy

🔤 Font Requirements
Primary (UI / Body)

Purpose: body text, inputs, buttons, labels

Must be:

Extremely legible

Neutral

Calm

Examples (choose best one):

Inter (only if justified)

Source Sans 3

IBM Plex Sans

Manrope

Secondary (Headings / Hero text)

Purpose: large headings, marketing sections

Must be:

Slightly expressive

Clean

Not playful

Examples:

Satoshi

General Sans

Plus Jakarta Sans

DM Sans

⚙️ Technical Constraints (STRICT)

Use next/font (Google or local)

Define fonts using CSS variables

Integrate cleanly with Tailwind config

No FOUC

No layout shift

SSR-safe

Do NOT hardcode font-family everywhere

🧱 Implementation Tasks

Recommend the best font pairing for a productivity / task app

Justify the choice (brief, practical)

Update:

app/layout.tsx

globals.css

tailwind.config.ts

Set up:

font-sans → body/UI font

font-display → headings

Apply heading font only where appropriate (not everywhere)

🎨 Visual Outcome

Body text disappears into usability (no noise)

Headings feel confident, not loud

App feels more “designed” instantly

No startup-template vibe

🚫 Explicitly Avoid

Overly rounded fonts

Playful or geometric fonts

Excessive contrast

Using display font for body text

Deliver clean, commented code and explain why this typography is better than Inter-only.

## Response snapshot

I've successfully upgraded the typography system for your Next.js application by implementing a premium two-font system with IBM Plex Sans and DM Sans. Here's what was implemented:

## Font Pairing Selection

**Primary UI/Body Font: IBM Plex Sans**
- Extremely legible and professional - designed for maximum readability
- Neutral and calm characteristics that make it disappear into usability
- Developed by IBM for their products, ensuring it works well in dashboards
- Excellent small-size rendering and professional appearance
- Perfect for body text, inputs, buttons, and labels

**Secondary Display/Headings Font: DM Sans**
- Clean and distinctive but professional
- Slightly expressive without being playful
- Works well for headings and marketing sections
- Maintains a calm, restrained appearance
- Confident but not loud as requested

## Implementation Summary

### 1. Updated `/mnt/d/Side Projects/giaic-hackathone/phase-2-fullstack-todo/frontend/app/layout.tsx`
- Imported IBM_Plex_Sans and DM_Sans from next/font/google
- Configured both fonts with appropriate weight ranges and display settings
- Applied font variables to the body className
- Used IBM Plex Sans for UI/body text with weights [100-700]
- Used DM Sans for headings with weights [400, 500, 700]

### 2. Updated `/mnt/d/Side Projects/giaic-hackathone/phase-2-fullstack-todo/frontend/app/globals.css`
- Defined CSS variables for both fonts (--font-ibm-plex-sans and --font-dm-sans)
- Updated @theme inline to register both font variables
- Applied IBM Plex Sans as the default body font
- Added utility classes for font-body and font-display
- Maintained dark mode support and existing color scheme

### 3. Updated `/mnt/d/Side Projects/giaic-hackathone/phase-2-fullstack-todo/frontend/tailwind.config.js`
- Updated fontFamily configuration to use CSS variables for both sans and display fonts
- Set sans font-family to var(--font-ibm-plex-sans) for UI/body text
- Set display font-family to var(--font-dm-sans) for headings
- Maintained all existing color and background configurations

### 4. Updated `/mnt/d/Side Projects/giaic-hackathone/phase-2-fullstack-todo/frontend/components/TaskCard.tsx`
- Added font-display class to priority badges and task titles for headings
- Added font-body class to date information and descriptions for body text
- Maintained all existing styling while enhancing typography

## Why This Typography is Better Than Inter-only

1. **Enhanced Readability**: IBM Plex Sans provides superior legibility for body text compared to Inter, making it ideal for productivity applications where users need to read task descriptions and UI elements for extended periods.

2. **Professional Hierarchy**: The two-font system creates a clear visual hierarchy that makes the interface feel more "designed" and intentional, moving away from the generic startup-template vibe.

3. **Dashboard-Optimized**: IBM Plex Sans was specifically designed for enterprise dashboards and works exceptionally well at small sizes, which is crucial for task management applications.

4. **Editorial-Quality Feel**: The pairing creates an editorial-quality typography system that feels premium and sophisticated while maintaining the calm, professional aesthetic required for productivity tools.

5. **No FOUC or Layout Shifts**: The implementation follows Next.js font optimization best practices with proper weight selection and display settings, ensuring no flash of unstyled text or layout shifts.

This implementation meets all your requirements: it's production-safe, works well in dashboards, looks good at small sizes, and feels professional. The typography system now feels premium, calm, and modern while maintaining excellent readability for productivity applications.

## Outcome

- ✅ Impact: Successfully upgraded typography system to premium two-font system with IBM Plex Sans + DM Sans
- 🧪 Tests: No specific tests needed for font changes
- 📁 Files: 4 files modified to implement new typography system
- 🔁 Next prompts: Ready for further UI enhancements
- 🧠 Reflection: Implementation followed all technical constraints and created desired professional, editorial-quality feel

## Evaluation notes (flywheel)

- Failure modes observed: None - all implementation steps completed successfully
- Graders run and results (PASS/FAIL): N/A for this type of change
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Consider additional typography refinements or UI enhancements