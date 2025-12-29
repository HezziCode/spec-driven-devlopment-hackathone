'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import {
  ListTodo,
  LogOut,
  ArrowRight,
  Zap,
  Layers,
  Home,
  Users
} from 'lucide-react';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import LandingPage from '@/components/LandingPage';
import NeuralBackground from '@/components/NeuralBackground';
import PageRouteTransitionProvider from '@/components/providers/PageRouteTransitionProvider';
import { useAuth } from '@/lib/auth';

// --- Custom Styles for Theme & Typography ---
const GlobalStyles = () => (
  <style>{`
    body {
      transition: background-color 0.3s ease-in-out;
      background-color: #0f172a; /* Dark background */
    }

    /* Gradient Text for Landing Page Headline */
    .gradient-text-teal {
      background-clip: text;
      -webkit-background-clip: text;
      color: transparent;
      background-image: linear-gradient(to right, #2dd4bf, #06b6d4, #0e7490); /* Teal-Cyan blend */
      transition: all 0.3s ease-in-out;
    }
  `}</style>
);

// --- Global Cursor Follow Glow Component ---
// This component displays the subtle glow animation that follows the mouse position globally.
const CursorGlow = ({ mousePosition }: { mousePosition: { x: number; y: number } }) => (
    <div
        className="fixed inset-0 z-0 pointer-events-none transition-opacity duration-300"
        style={{
            // Dynamic background with radial gradient following the mouse position relative to the viewport
            background: `radial-gradient(450px at ${mousePosition.x}px ${mousePosition.y}px, rgba(6, 182, 212, 0.1), transparent 80%)`,
            transition: 'background 0.05s ease-out',
        }}
    />
);


// --- Main Application Component ---
export default function App() {
  const router = useRouter();
  const { session, status } = useAuth();
  const [view, setView] = useState('landing');

  // Always in dark mode now
  const isDarkMode = true;

  // Global Mouse Position State and Handler
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  const handleMouseMove = useCallback((e: MouseEvent) => {
    // Track mouse position relative to the viewport for global glow
    setMousePosition({
      x: e.clientX,
      y: e.clientY,
    });
  }, []);


  // Set up global mouse tracking
  useEffect(() => {
    window.addEventListener('mousemove', handleMouseMove);
    return () => {
        window.removeEventListener('mousemove', handleMouseMove);
    };
  }, [handleMouseMove]);

  // --- Auth Action Handler ---
  const handleAuthAction = useCallback(async (action: string) => {
    if (action === 'signin') {
      // Check if user is already authenticated
      if (session && status === 'authenticated') {
        // User is logged in, go directly to tasks
        router.push('/tasks');
      } else {
        // User not logged in, redirect to auth page
        router.push('/auth');
      }
    } else if (action === 'signout') {
      // This shouldn't be called from landing page, but handle it anyway
      router.push('/auth');
    }
  }, [session, status, router]);


  // --- Loading State ---
  if (status === 'loading') {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center transition-colors duration-300">
        <div className="w-16 h-16 border-4 border-cyan-200 border-t-cyan-600 rounded-full animate-spin"></div>
      </div>
    );
  }

  // --- Main Render (Only Landing Page is available) ---
  return (
    <PageRouteTransitionProvider>
      <div className="min-h-screen bg-slate-900/90 transition-colors duration-300 relative">
        <GlobalStyles />

        {/* Neural Background - positioned just behind content but above base background */}
        <NeuralBackground />

        {/* Global Cursor Glow rendered as a fixed element */}
        <CursorGlow mousePosition={mousePosition} />

        <div className="relative z-10">
          <Navbar />

          <LandingPage
            handleAuthAction={handleAuthAction}
          />
          <Footer />
        </div>
      </div>
    </PageRouteTransitionProvider>
  );
}