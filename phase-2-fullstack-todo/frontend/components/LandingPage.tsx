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
  isDarkMode: boolean;
}

const LandingPage: React.FC<LandingPageProps> = ({ handleAuthAction, isDarkMode }) => {
  // State to track mouse position relative to the container for the spotlight effect
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  // Handler to update mouse position on movement
  const handleMouseMove = useCallback((e) => {
    // Calculate coordinates relative to the bounding box of the target element (e.currentTarget)
    const bounds = e.currentTarget.getBoundingClientRect();
    setMousePosition({
      x: e.clientX - bounds.left,
      y: e.clientY - bounds.top,
    });
  }, []);

  // Dynamic background classes for light/dark mode card
  const backgroundClasses = isDarkMode
    ? 'bg-slate-800/80 text-white'
    : 'bg-white text-gray-800'; // Removed transparency for cleaner light theme appearance

  const featureItemClasses = isDarkMode
    ? 'bg-slate-800 border-slate-700 hover:border-cyan-500'
    : 'bg-white border-gray-200 hover:border-cyan-500';

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
    <div className="flex flex-col items-center justify-start p-4 text-center">

      {/* 1. Hero Section */}
      <section className="flex flex-col items-center justify-center pt-24 pb-32 w-full max-w-7xl min-h-[calc(100vh-64px)]">
        <div
          className={`max-w-4xl w-full p-8 md:p-12 space-y-8 transition-all duration-500 ease-out ${isDarkMode ? 'text-white' : 'text-gray-800'}`}
        >
          <div className="space-y-8">
            {/* Hero Headline */}
            <h1 className="text-6xl md:text-8xl font-extrabold tracking-tighter leading-none whitespace-nowrap">
              Ride the <span className={isDarkMode ? 'bg-gradient-to-r from-teal-400 to-cyan-400 bg-clip-text text-transparent' : 'bg-gradient-to-r from-teal-600 to-cyan-500 bg-clip-text text-transparent'}>TaskWave</span>
</h1>

            <p className={`text-xl max-w-2xl mx-auto transition-colors ${isDarkMode ? 'text-gray-300' : 'text-gray-800'}`}>
              The minimalist, modern way to manage your tasks. Start working smarter with an interface that's easy on the eyes.
            </p>

            {/* CTA Button with Shadow Glow */}
            <button
              onClick={() => handleAuthAction('signin')}
              className="inline-flex items-center justify-center px-8 py-3 text-lg font-semibold rounded-xl bg-cyan-500 hover:bg-cyan-600 text-white
                      shadow-2xl shadow-cyan-500/50 hover:shadow-cyan-400/70 transition-all duration-300 transform hover:scale-[1.03] active:scale-95"
            >
              Get Started - It's Free
              <ArrowRight className="w-5 h-5 ml-2" />
            </button>
          </div>
        </div>
      </section>

      {/* 2. Main Feature Section */}
      <section className="w-full max-w-7xl py-16 px-4 sm:px-6 lg:px-8">
          <h2 className={`text-4xl font-extrabold mb-4 ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
              Designed for Productivity
          </h2>
          <p className={`text-xl max-w-3xl mx-auto mb-12 ${isDarkMode ? 'text-gray-400' : 'text-gray-800'}`}>
              Simple tools, powerful results. We give you exactly what you need to organize your daily life.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              {features.map((feature) => (
                  <div
                      key={feature.title}
                      className={`p-6 rounded-xl border-2 transition-all duration-300 transform hover:-translate-y-1 shadow-lg ${featureItemClasses}`}
                  >
                      <feature.icon className={`w-8 h-8 ${isDarkMode ? 'text-teal-400' : 'text-cyan-600'} mb-4`} />
                      <h3 className={`text-xl font-semibold mb-2 ${isDarkMode ? 'text-white' : 'text-gray-800'}`}>{feature.title}</h3>
                      <p className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-800'}`}>{feature.description}</p>
                  </div>
              ))}
          </div>
      </section>
    </div>
  );
};

export default LandingPage;