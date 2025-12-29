import { RefObject, useEffect } from 'react';

/**
 * Custom hook to detect clicks outside a referenced element.
 *
 * Useful for closing dropdowns, modals, or popovers when user clicks outside.
 *
 * @param ref - React ref to the element to monitor
 * @param handler - Callback function to execute when click outside is detected
 *
 * @example
 * const dropdownRef = useRef<HTMLDivElement>(null);
 * useClickOutside(dropdownRef, () => setIsOpen(false));
 *
 * return (
 *   <div ref={dropdownRef}>
 *     Dropdown content
 *   </div>
 * );
 */
export function useClickOutside<T extends HTMLElement>(
  ref: RefObject<T | null>,
  handler: () => void
): void {
  useEffect(() => {
    const listener = (event: MouseEvent | TouchEvent) => {
      // Do nothing if clicking ref's element or descendent elements
      if (!ref.current || ref.current.contains(event.target as Node)) {
        return;
      }

      // Click outside - execute handler
      handler();
    };

    // Attach listeners for both mouse and touch events
    document.addEventListener('mousedown', listener);
    document.addEventListener('touchstart', listener);

    // Cleanup listeners on unmount or dependency change
    return () => {
      document.removeEventListener('mousedown', listener);
      document.removeEventListener('touchstart', listener);
    };
  }, [ref, handler]); // Re-run effect if ref or handler changes
}
