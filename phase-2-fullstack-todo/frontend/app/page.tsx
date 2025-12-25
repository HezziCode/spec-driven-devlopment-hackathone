'use client';

import React, { useState, useEffect, useCallback } from 'react';
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
  const [userId, setUserId] = useState<string | null>(null);
  const [isAuthReady, setIsAuthReady] = useState(false);
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


  // Initialize authentication state
  useEffect(() => {
    // Simulate authentication initialization
    setTimeout(() => {
      setIsAuthReady(true);
    }, 500);
  }, []);

  // --- Auth Action Handler ---
  const handleAuthAction = useCallback(async (action: string) => {
    if (action === 'signin') {
      // Simulate sign in by creating a demo JWT token
      // Create a simple JWT payload with demo user data
      const demoUser = {
        userId: 'demo-user',
        email: 'demo@example.com',
        username: 'Demo User',
        exp: Math.floor(Date.now() / 1000) + (24 * 60 * 60), // 24 hours from now
        iat: Math.floor(Date.now() / 1000)
      };

      // Create a fake JWT token (header.payload.signature format)
      // Note: This is for demo purposes only - real JWTs should be signed by the server
      const header = btoa(JSON.stringify({ alg: 'none', typ: 'JWT' }));
      const payload = btoa(JSON.stringify(demoUser));
      const fakeSignature = btoa('fake-signature');
      const demoToken = `${header}.${payload}.${fakeSignature}`;

      // Store the demo token in localStorage
      if (typeof window !== 'undefined') {
        localStorage.setItem('better-auth-session-token', demoToken);
      }

      // Set the userId state
      setUserId('demo-user');

      // Redirect to the tasks dashboard after sign in
      if (typeof window !== 'undefined') {
        window.location.href = '/tasks';
      }
    } else if (action === 'signout') {
      // Clear the demo token from localStorage
      if (typeof window !== 'undefined') {
        localStorage.removeItem('better-auth-session-token');
      }
      setUserId(null);
      setView('landing');
    }
  }, []);


  // --- Loading State ---
  if (!isAuthReady) {
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
          <Navbar
            userId={userId}
            handleAuthAction={handleAuthAction}
            setView={setView}
          />

          <LandingPage
            handleAuthAction={handleAuthAction}
          />
          <Footer setView={setView} />
        </div>
      </div>
    </PageRouteTransitionProvider>
  );
}