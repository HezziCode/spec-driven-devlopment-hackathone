'use client';

import React, { useState, useCallback } from 'react';
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

interface LandingPageProps {
  handleAuthAction: (action: string) => void;
}

const LandingPage: React.FC<LandingPageProps> = ({ handleAuthAction }) => {
  const isDarkMode = true; // Always use dark mode
  // State to track mouse position relative to the container for the spotlight effect
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  // Handler to update mouse position on movement
  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    // Calculate coordinates relative to the bounding box of the target element (e.currentTarget)
    const bounds = e.currentTarget.getBoundingClientRect();
    setMousePosition({
      x: e.clientX - bounds.left,
      y: e.clientY - bounds.top,
    });
  }, []);

  // Dark theme classes only
  const backgroundClasses = 'bg-slate-800/80 text-white'; // Removed transparency for cleaner dark theme appearance

  const featureItemClasses = 'bg-slate-800 border-slate-700 hover:border-cyan-500';

  const features = [
    {
      icon: Home,
      title: "Minimalist Design",
      description: "Focus on what matters with a clean, distraction-free interface."
    },
    {
      icon: Zap,
      title: "Instant Access",
      description: "Start managing tasks instantly with anonymous sign-in."
    },
    {
      icon: Layers,
      title: "Cross-Device Support",
      description: "Works perfectly across mobile, tablet, or desktop."
    },
    {
      icon: Users,
      title: "Wave of the Future",
      description: "Ready for future features like collaborative lists and AI tools."
    },
  ];

  return (
    <div className="flex flex-col items-center justify-start p-4 text-center w-full">

      {/* 1. Hero Section */}
      <section className="flex flex-col items-center justify-center pt-16 pb-16 w-full max-w-7xl min-h-[calc(100vh-64px)]">
        <div
          className="max-w-4xl w-full p-4 md:p-8 space-y-6 transition-all duration-500 ease-out text-white"
        >
          <div className="space-y-6">
            {/* Hero Headline */}
            <h1 className="text-4xl sm:text-5xl md:text-7xl font-extrabold tracking-tight leading-tight text-white drop-shadow-lg break-words">
              Ride the{" "}
              <span className="relative inline-block">
                <span className="bg-gradient-to-r from-teal-300 to-cyan-300 bg-clip-text text-transparent">
                  TaskFlow
                </span>

                {/* Curved SVG underline */}
                <svg
                  className="absolute left-0 -bottom-1 w-full h-2 pointer-events-none sm:-bottom-2 sm:h-3"
                  viewBox="0 0 100 10"
                  preserveAspectRatio="none"
                >
                  <path
                    d="M2,5 Q50,10 98,5"
                    stroke="rgb(94 234 212)"   // teal/cyan tone
                    strokeWidth="2"
                    fill="none"
                    strokeLinecap="round"
                    opacity="0.8"
                  />
                </svg>
              </span>
            </h1>
            <p className="text-lg sm:text-xl max-w-2xl mx-auto transition-colors text-gray-300 px-2">
              The minimalist, modern way to manage your tasks. Start working smarter with an interface that's easy on the eyes.
            </p>

            {/* CTA Buttons with Shadow Glow - Centered */}
            <div className="flex flex-col sm:flex-row gap-4 sm:gap-4 items-center justify-center">
              <button
                onClick={() => {
                  // Sign in the user first, then redirect to the tasks dashboard
                  handleAuthAction('signin');
                }}
                className="inline-flex items-center justify-center px-6 py-3 sm:px-8 sm:py-4 text-base sm:text-lg font-semibold rounded-lg sm:rounded-xl bg-cyan-500 hover:bg-cyan-600 text-white
                        shadow-lg sm:shadow-2xl shadow-cyan-500/50 hover:shadow-cyan-400/70 transition-all duration-300 transform hover:scale-[1.03] active:scale-95 min-h-[48px] w-full sm:w-auto"
              >
                Get Started
                <ArrowRight className="w-4 h-4 sm:w-5 sm:h-5 ml-2" />
              </button>

              <a
                href="/about"
                className="inline-flex items-center justify-center px-6 py-3 sm:px-8 sm:py-4 text-base sm:text-lg font-semibold rounded-lg sm:rounded-xl bg-slate-700 hover:bg-slate-600 text-white
                        shadow-lg sm:shadow-2xl shadow-slate-500/30 hover:shadow-slate-400/50 transition-all duration-300 transform hover:scale-[1.03] active:scale-95 min-h-[48px] border border-slate-600/50 w-full sm:w-auto"
              >
                About Us
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* 2. Main Feature Section */}
      <section className="w-full max-w-7xl py-8 sm:py-16 px-4 sm:px-6 lg:px-8">
<h2 className="text-3xl sm:text-4xl font-extrabold mb-3 sm:mb-4 text-white">
  Designed for{" "}
  <span className="relative inline-block">
    <span className="bg-gradient-to-r from-teal-300 to-cyan-300 bg-clip-text text-transparent">
      Productivity
    </span>

    {/* Curved underline */}
    <svg
      className="absolute -bottom-1 w-full h-2 sm:-bottom-2 sm:h-3"
      viewBox="0 0 100 10"
      preserveAspectRatio="none"
    >
      <path
        d="M2,5 Q50,10 98,5"
        stroke="url(#grad)"
        strokeWidth="2"
        fill="none"
        strokeLinecap="round"
        opacity="0.85"
      />
      <defs>
        <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#5eead4" />
          <stop offset="100%" stopColor="#67e8f9" />
        </linearGradient>
      </defs>
    </svg>
  </span>
</h2>

        <p className="text-lg max-w-3xl mx-auto mb-8 sm:mb-12 text-gray-400 px-2">
          Simple tools, powerful results. We give you exactly what you need to organize your daily life.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-8">
          {features.map((feature) => (
            <div
              key={feature.title}
              className={`p-4 sm:p-6 rounded-lg sm:rounded-xl border transition-all duration-300 transform hover:-translate-y-1 shadow ${featureItemClasses}`}
            >
              <feature.icon className="w-6 h-6 sm:w-8 sm:h-8 text-teal-400 mb-3 sm:mb-4 mx-auto" />
              <h3 className="text-lg sm:text-xl font-semibold mb-2 text-white">{feature.title}</h3>
              <p className="text-xs sm:text-sm text-gray-400">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default LandingPage;