/**
 * Chat Page - TaskWave AI Assistant
 *
 * This page provides a natural language interface for task management
 * using a custom chat interface. Users can create, search, update, and manage
 * tasks through conversational AI.
 *
 * Features:
 * - Natural language task management
 * - Real-time AI responses with streaming
 * - Multi-thread conversation support
 * - TaskWave-themed UI with gradients and animations
 * - ChatGPT-like layout with sidebar history
 * - Navbar and Footer navigation
 */

'use client';

import { CustomChatInterface } from '@/components/CustomChatInterface';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import ProtectedRoute from '@/components/ProtectedRoute';

export default function ChatPage() {
  return (
    <ProtectedRoute authMode="signup">
      <div className="min-h-screen w-full max-w-full bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex flex-col overflow-x-hidden">
        {/* Navbar */}
        <Navbar />

        {/* Main Content */}
        <div className="flex flex-1 overflow-hidden w-full max-w-full">
          {/* Custom Chat Interface with integrated sidebar */}
          <div className="flex-1 flex flex-col overflow-hidden">
            <div className="flex-1 overflow-hidden">
              <CustomChatInterface />
            </div>
          </div>
        </div>

        {/* Footer */}
        <Footer />
      </div>
    </ProtectedRoute>
  );
}
