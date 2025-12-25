# Theme Consistency Guidelines

This document outlines the theme consistency patterns implemented in the TaskFlow Dashboard to ensure proper light and dark mode behavior.

## Background Color Standards

### Primary Containers
- **Light Theme**: `bg-white`
- **Dark Theme**: `dark:bg-slate-800`
- **Example**: `bg-white dark:bg-slate-800 rounded-xl`

### Secondary Containers
- **Light Theme**: `bg-gray-50` or `bg-slate-100`
- **Dark Theme**: `dark:bg-slate-700`
- **Example**: `bg-slate-100 dark:bg-slate-700`

## Input Elements
- **Text inputs**: `bg-white dark:bg-slate-700 border border-slate-300 dark:border-slate-600`
- **Select dropdowns**: `bg-white dark:bg-slate-700 border border-slate-300 dark:border-slate-600`

## Important Notes
- Always use full opacity backgrounds (avoid `/80`, `/90` opacity modifiers)
- Pair light and dark classes together: `bg-white dark:bg-slate-800`
- Test components in both light and dark modes to ensure proper contrast
- Avoid hard-coding colors without theme alternatives

## Common Patterns
- Cards: `bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6 border border-slate-200 dark:border-slate-700/50`
- Buttons: `bg-gradient-to-r from-cyan-600 to-blue-600 text-white` or `bg-white dark:bg-slate-700 border border-slate-300 dark:border-slate-600`
- Tags: `bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-600/50`