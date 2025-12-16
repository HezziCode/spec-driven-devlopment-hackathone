'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Sun,
  Moon,
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

// --- Custom Styles for Theme & Typography ---
const GlobalStyles = ({ isDarkMode }) => (
  <style>{`
    body {
      transition: background-color 0.3s ease-in-out;
      background-color: ${isDarkMode ? '#0f172a' : '#f0f9ff'}; /* Slate 900 / Sky 50 */
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
const CursorGlow = ({ isDarkMode, mousePosition }) => (
    <div
        className="fixed inset-0 z-0 pointer-events-none transition-opacity duration-300"
        style={{
            // Dynamic background with radial gradient following the mouse position relative to the viewport
            background: `radial-gradient(450px at ${mousePosition.x}px ${mousePosition.y}px, ${isDarkMode ? 'rgba(45, 212, 191, 0.15)' : 'rgba(6, 182, 212, 0.3)'}, transparent 80%)`,
            transition: 'background 0.05s ease-out',
        }}
    />
);






// --- Main Application Component ---
export default function App() {
  const [userId, setUserId] = useState(null);
  const [isAuthReady, setIsAuthReady] = useState(false);
  const [view, setView] = useState('landing');

  // Initialize Dark Mode based on system preference
  const [isDarkMode, setIsDarkMode] = useState(() => {
    if (typeof window !== 'undefined' && window.matchMedia) {
      return window.matchMedia('(prefers-color-scheme: dark)').matches;
    }
    return false;
  });

  // Global Mouse Position State and Handler
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  const handleMouseMove = useCallback((e) => {
    // Track mouse position relative to the viewport for global glow
    setMousePosition({
      x: e.clientX,
      y: e.clientY,
    });
  }, []);

  // Theme Toggle Effect (Apply to HTML root element)
  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  // Set up global mouse tracking
  useEffect(() => {
    window.addEventListener('mousemove', handleMouseMove);
    return () => {
        window.removeEventListener('mousemove', handleMouseMove);
    };
  }, [handleMouseMove]);


  // Initialize authentication state
  useEffect(() => {
    // Simulate authentication initialization
    setTimeout(() => {
      setIsAuthReady(true);
    }, 500);
  }, []);

  // --- Auth Action Handler ---
  const handleAuthAction = useCallback(async (action) => {
    if (action === 'signin') {
      // Simulate sign in
      setUserId('demo-user');
    } else if (action === 'signout') {
      setUserId(null);
      setView('landing');
    }
  }, []);


  // --- Loading State ---
  if (!isAuthReady) {
    return (
      <div className="min-h-screen bg-sky-50 dark:bg-slate-900 flex items-center justify-center transition-colors duration-300">
        <div className="w-16 h-16 border-4 border-cyan-200 border-t-cyan-600 rounded-full animate-spin"></div>
      </div>
    );
  }

  // --- Main Render (Only Landing Page is available) ---
  return (
    <div className={`min-h-screen transition-colors duration-300 ${isDarkMode ? 'dark' : ''} relative`}>
      <GlobalStyles isDarkMode={isDarkMode} />

      {/* Global Cursor Glow rendered as a fixed element */}
      <CursorGlow isDarkMode={isDarkMode} mousePosition={mousePosition} />

      <Navbar
        userId={userId}
        handleAuthAction={handleAuthAction}
        isDarkMode={isDarkMode}
        setIsDarkMode={setIsDarkMode}
        setView={setView}
      />

      <LandingPage
        handleAuthAction={handleAuthAction}
        isDarkMode={isDarkMode}
      />
      <Footer isDarkMode={isDarkMode} setView={setView} />

    </div>
  );
}