# Research: Profile Dropdown and Auth Page UI Patterns

**Feature**: 012-profile-dropdown-ui
**Date**: 2025-12-27

## Dropdown Menu Best Practices

### Accessibility (WCAG 2.1 AA)
- Use `role="button"` for trigger element
- Use `aria-expanded` to indicate dropdown state
- Use `aria-haspopup="menu"` on trigger
- Use `role="menu"` on dropdown container
- Use `role="menuitem"` on each menu item
- Support keyboard navigation: Tab, Enter, Escape, Arrow keys

### Click-Outside Detection
**Pattern**: Custom React hook using useRef and useEffect
```typescript
function useClickOutside(ref, handler) {
  useEffect(() => {
    const listener = (event) => {
      if (!ref.current || ref.current.contains(event.target)) return;
      handler();
    };
    document.addEventListener('mousedown', listener);
    document.addEventListener('touchstart', listener);
    return () => {
      document.removeEventListener('mousedown', listener);
      document.removeEventListener('touchstart', listener);
    };
  }, [ref, handler]);
}
```

### Positioning Strategy
- Use `relative` on parent container
- Use `absolute top-full right-0` on dropdown
- Add `mt-2` for spacing from trigger
- Consider viewport boundaries (adjust if near edge)

## Username Display Priority

### Extraction Logic
1. **First priority**: Google OAuth name from `oauth_data.name`
2. **Second priority**: Local username
3. **Fallback**: Email prefix (email.split('@')[0])

### Character Limits
- Truncate display names longer than 20 characters
- Use CSS `truncate` utility (text-overflow: ellipsis)
- Add `title` attribute with full name for hover tooltip

## Auth Page Layout Patterns

### Common Patterns
- Centered form container with max-width (400-500px)
- Navbar at top (can be minimal or full)
- Footer at bottom with legal links
- Gradient or solid background
- Card/panel for form with shadow
- Consistent spacing (p-8 for container, space-y-6 for form fields)

### OAuth Button Integration
- Place after form fields, before mode toggle
- Add visual separator ("or" divider with horizontal lines)
- Match button width to form inputs (w-full)
- Consistent padding and styling with other buttons

## Animation and Transitions

### Best Practices
- Use Tailwind transition utilities: `transition duration-200`
- Focus states: `focus:ring-2 focus:ring-indigo-500`
- Hover states: `hover:shadow-lg hover:-translate-y-0.5`
- Fade in: `transition opacity-0 → opacity-100`
- Keep transitions under 300ms for responsiveness
- Use CSS transitions (GPU-accelerated) not JavaScript

### Dropdown Animation
- Entry: `transition-opacity duration-150 ease-out`
- Exit: `transition-opacity duration-100 ease-in`
- Scale: Start at `scale-95`, animate to `scale-100`

## Mobile Considerations

### Touch Support
- Ensure dropdown trigger has adequate touch target (min 44x44px)
- Add touchstart listener in addition to click
- Prevent scroll when dropdown open (optional)
- Adjust dropdown position if near screen edge

### Responsive Design
- Dropdown should stack vertically on mobile
- Footer links might wrap on narrow screens
- Navbar might need simplified layout (existing responsive already handled)

## Design Tokens (Existing Tailwind Config)

### Colors
- Primary: indigo-600, cyan-600
- Background: slate-900, slate-800
- Text: slate-200, gray-400
- Success: green-500
- Error: red-500

### Spacing
- Container padding: p-8
- Form field spacing: space-y-6
- Button padding: px-4 py-2, px-6 py-3
- Dropdown padding: p-2

### Shadows
- Card: shadow-2xl
- Hover: hover:shadow-lg
- Dropdown: shadow-lg

## Decisions Summary

1. **Dropdown**: Custom React component (no library)
2. **Click-outside**: Custom useClickOutside hook
3. **Username**: oauth_data.name → username → email fallback
4. **Navbar reuse**: Same component with conditional rendering
5. **Animations**: CSS transitions via Tailwind utilities
6. **Mobile**: Existing responsive design + position adjustment
