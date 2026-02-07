'use client';

import { MessageCircle } from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

/**
 * StickyChatbotButton - Simple button that appears across all pages
 * Fixed position: bottom-right corner
 * Always visible (no scroll behavior - fixed position)
 * Simple Link component for instant navigation
 *
 * NOTE: This button is HIDDEN when on the /chat page to avoid duplication
 * with the chat interface component.
 */

export function StickyChatbotButton() {
  const pathname = usePathname();

  // Hide the sticky button when on the chat page
  if (pathname === '/chat') {
    return null;
  }

  return (
    <div
      className={`
        fixed z-50
        bottom-6 right-6
        md:bottom-8 md:right-8
      `}
      style={{
        position: 'fixed',
        zIndex: 50,
      }}
    >
      <Link
        href="/chat"
        className={`
          flex items-center justify-center
          w-14 h-14 md:w-16 md:h-16
          rounded-full
          bg-cyan-500 hover:bg-cyan-600
          text-white
          shadow-lg shadow-cyan-500/50 hover:shadow-xl hover:shadow-cyan-400/70
          transition-all duration-300 transform hover:scale-110
          focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:ring-offset-2
        `}
        aria-label="Open chat assistant"
        title="Chat with AI Assistant"
      >
        <MessageCircle className="w-6 h-6 md:w-7 md:h-7" />
      </Link>
    </div>
  );
}

export default StickyChatbotButton;
