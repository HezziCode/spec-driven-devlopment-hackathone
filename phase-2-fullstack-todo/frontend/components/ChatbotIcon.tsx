'use client';

import { MessageCircle } from 'lucide-react';
import { useRouter } from 'next/navigation';

/**
 * Floating chatbot icon for navigating to chat page
 * Matches the style from landing page
 */
export function ChatbotIcon() {
  const router = useRouter();

  const handleClick = () => {
    router.push('/chat');
  };

  return (
    <button
      onClick={handleClick}
      className="fixed bottom-6 right-6 z-50 p-4 rounded-full bg-cyan-600 hover:bg-cyan-700 text-white shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-110 min-h-[56px] min-w-[56px]"
      aria-label="Open chat assistant"
      title="Chat with AI Assistant"
    >
      <MessageCircle className="w-6 h-6" />
    </button>
  );
}
