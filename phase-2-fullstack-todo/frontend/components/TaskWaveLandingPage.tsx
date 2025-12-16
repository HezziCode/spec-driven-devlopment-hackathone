'use client';

import { useState, useRef, useEffect } from 'react';
import { Home, Zap, Layers, Users } from 'lucide-react';

const TaskWaveLandingPage = () => {
  const [darkMode, setDarkMode] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  // Toggle dark mode
  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  // Handle mouse move for spotlight effect
  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      setMousePosition({ x, y });
    }
  };

  // Feature data
  const features = [
    {
      title: "Minimalist Design",
      icon: Home,
      description: "Focus on what matters with a clean, distraction-free interface."
    },
    {
      title: "Real-time Sync",
      icon: Zap,
      description: "Data updates instantly across all your devices using Firestore."
    },
    {
      title: "Cross-Device Support",
      icon: Layers,
      description: "Use TaskWave on mobile, tablet, or desktop with no issues."
    },
    {
      title: "Easy Authentication",
      icon: Users,
      description: "Start managing tasks instantly with anonymous sign-in."
    }
  ];

  return (
    <div className={`min-h-screen transition-colors duration-300 ${darkMode ? 'bg-slate-900' : 'bg-sky-50'}`}>
      {/* Hero Section */}
      <div
        ref={containerRef}
        onMouseMove={handleMouseMove}
        className="relative min-h-screen flex items-center justify-center px-4 py-16"
        style={{
          background: darkMode
            ? `radial-gradient(600px circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(14, 165, 233, 0.1), ${darkMode ? '#0f172a' : '#f0f9ff'})`
            : `radial-gradient(600px circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(14, 165, 233, 0.2), ${darkMode ? '#0f172a' : '#f0f9ff'})`
        }}
      >
        {/* Spotlight effect - more subtle in dark mode */}
        <div className="absolute inset-0 overflow-hidden">
          <div
            className="absolute w-[600px] h-[600px] rounded-full opacity-20 blur-[80px] transition-all duration-300"
            style={{
              left: mousePosition.x - 300,
              top: mousePosition.y - 300,
              background: darkMode
                ? 'radial-gradient(circle, rgba(14, 165, 233, 0.2) 0%, transparent 70%)'
                : 'radial-gradient(circle, rgba(14, 165, 233, 0.3) 0%, transparent 70%)',
            }}
          />
        </div>

        {/* Hero Content */}
        <div className="relative z-10 text-center max-w-4xl mx-auto">
          <h1 className="text-6xl md:text-7xl lg:text-8xl font-bold mb-6">
            Ride the <span className="bg-gradient-to-r from-teal-600 to-cyan-500 bg-clip-text text-transparent">TaskWave</span>
          </h1>
          <p className={`text-xl md:text-2xl mb-10 max-w-2xl mx-auto ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
            The minimalist, modern way to manage your tasks. Start working smarter...
          </p>
          <button
            className={`px-8 py-4 rounded-full text-lg font-semibold transition-all duration-300 transform hover:scale-105 hover:shadow-lg ${
              darkMode
                ? 'bg-cyan-600 hover:bg-cyan-500 text-white hover:shadow-cyan-500/30'
                : 'bg-cyan-500 hover:bg-cyan-400 text-white hover:shadow-cyan-400/50'
            }`}
          >
            Get Started - It's Free
          </button>
        </div>
      </div>

      {/* Feature Section */}
      <div className="py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => {
              const IconComponent = feature.icon;
              return (
                <div
                  key={index}
                  className={`rounded-xl p-6 border transition-all duration-300 transform hover:-translate-y-1 ${
                    darkMode
                      ? 'bg-slate-800 border-slate-700 hover:border-cyan-500'
                      : 'bg-white border-gray-200 hover:border-cyan-400'
                  }`}
                >
                  <div className={`w-12 h-12 rounded-lg flex items-center justify-center mb-4 ${
                    darkMode ? 'bg-slate-700 text-cyan-400' : 'bg-cyan-50 text-cyan-600'
                  }`}>
                    <IconComponent size={24} />
                  </div>
                  <h3 className={`text-xl font-semibold mb-2 ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                    {feature.title}
                  </h3>
                  <p className={darkMode ? 'text-gray-300' : 'text-gray-600'}>
                    {feature.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Dark Mode Toggle Button */}
      <button
        onClick={toggleDarkMode}
        className={`fixed top-4 right-4 p-3 rounded-full ${
          darkMode ? 'bg-slate-700 text-cyan-400' : 'bg-cyan-100 text-cyan-600'
        }`}
        aria-label="Toggle dark mode"
      >
        {darkMode ? '☀️' : '🌙'}
      </button>
    </div>
  );
};

export default TaskWaveLandingPage;