/**
 * ChatInterface Component
 *
 * Simple chat interface that redirects to the full chat page.
 * This component is used in other parts of the application
 * to provide access to the chat functionality.
 */

'use client';

import { useEffect } from 'react';

export function ChatInterface() {
  useEffect(() => {
    // Redirect to the full chat page after a short delay
    const timer = setTimeout(() => {
      window.location.href = '/chat';
    }, 100);

    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="flex items-center justify-center h-[600px] bg-slate-900/50 rounded-lg border border-cyan-500/20 backdrop-blur-sm">
      <div className="text-center">
        <div className="relative w-16 h-16 mx-auto mb-6">
          {/* Animated spinner with wave effect */}
          <div className="absolute inset-0 rounded-full border-4 border-cyan-500/20"></div>
          <div className="absolute inset-0 rounded-full border-4 border-cyan-500 border-t-transparent animate-spin"></div>
          <div className="absolute inset-2 rounded-full border-4 border-teal-400/30 border-b-transparent animate-spin animation-delay-150"></div>
        </div>
        <p className="text-slate-400 text-sm animate-pulse">Redirecting to chat...</p>
        <p className="text-slate-500 text-xs mt-2">Loading TaskFlow AI Assistant</p>
      </div>
    </div>
  );
}
