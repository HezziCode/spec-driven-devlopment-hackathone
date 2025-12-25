# Theme Consistency Guidelines

## Overview
This document outlines the theme consistency patterns implemented to ensure consistent light/dark mode styling across the TaskWave application.

## Background Colors
- Use `bg-white/90 dark:bg-slate-800/80` for cards and containers to maintain consistent transparency
- Add `border border-slate-200 dark:border-slate-700/50` for consistent borders

## Text Colors
- Primary text: `text-slate-800 dark:text-slate-200`
- Secondary text: `text-slate-600 dark:text-slate-400`
- Muted text: `text-slate-500 dark:text-slate-500`

## Border Colors
- Use `border-slate-200 dark:border-slate-700/50` for consistent borders across components

## Priority Badge Colors
- Use the existing gradient patterns with consistent dark mode variants

## Form Elements
- Background: `bg-white/90 dark:bg-slate-700/30`
- Border: `border-slate-300 dark:border-slate-600`
- Text: `text-slate-800 dark:text-slate-300`

## Implementation Notes
- Avoid hardcoded color values in inline styles
- Use CSS variables defined in globals.css for consistency
- Maintain proper contrast ratios for accessibility