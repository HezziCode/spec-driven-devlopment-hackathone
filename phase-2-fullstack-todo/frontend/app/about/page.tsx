'use client';

import React from 'react';
import { ListTodo, Heart, Code, Users, Globe, User } from 'lucide-react';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import NeuralBackground from '@/components/NeuralBackground';

// Custom styles for theme and typography
const GlobalStyles = () => (
  <style>{`
    body {
      transition: background-color 0.3s ease-in-out;
      background-color: #0f172a; /* Dark background */
    }

    /* Gradient text for headlines */
    .gradient-text-teal {
      background-clip: text;
      -webkit-background-clip: text;
      color: transparent;
      background-image: linear-gradient(to right, #2dd4bf, #06b6d4, #0e7490); /* Teal-Cyan blend */
      transition: all 0.3s ease-in-out;
    }
  `}</style>
);

const AboutPage = () => {
  const accentColor = 'text-cyan-400';
  const borderColor = 'border-slate-700/50';
  const textColor = 'text-slate-200';
  const iconColor = 'text-slate-400';
  const hoverBgColor = 'hover:bg-slate-800/50';

  // Mock user data (in a real app, this would come from auth context)
  const mockUser = {
    id: 'demo-user',
    username: 'Demo User',
    email: 'demo@example.com'
  };

  // Mock notifications data
  const mockNotifications = [];

  return (
    <div className="min-h-screen bg-slate-900/40 transition-colors duration-300 relative">
      <GlobalStyles />

      {/* Neural Background - positioned just behind content but above base background */}
      <NeuralBackground />

      <div className="relative z-10">
        <Navbar
          userId={mockUser.id}
          handleAuthAction={() => {}}
          setView={() => {}}
          notifications={mockNotifications}
          onMarkAllRead={() => {}}
          onNotificationClick={() => {}}
        />

        <main className="container mx-auto px-4 py-8">
          <div className="max-w-6xl mx-auto">
            {/* Premium Hero Section */}
            <section className="relative w-full flex flex-col items-center justify-center text-center overflow-visible py-16">
              {/* Premium background elements */}
              <div className="absolute top-0 left-0 w-64 h-64 bg-gradient-to-br from-teal-500/5 to-cyan-500/10 rounded-full blur-[120px] -mt-24 -ml-24" />
              <div className="absolute bottom-0 right-0 w-64 h-64 bg-gradient-to-br from-cyan-500/5 to-blue-500/10 rounded-full blur-[120px] -mb-24 -mr-24" />

              <div className="relative z-10 space-y-6 max-w-4xl w-full">
                {/* Status tag */}
                <div className="inline-flex items-center space-x-2.5 px-4 py-2 rounded-full bg-gradient-to-r from-cyan-500/15 to-teal-500/15 border border-cyan-500/30 backdrop-blur-sm shadow-lg shadow-cyan-500/10">
                  <Globe size={14} className="text-cyan-400" />
                  <span className="text-sm font-semibold text-slate-200">Our Story</span>
                </div>

                {/* Premium animated heading */}
                <h1 className="text-4xl md:text-6xl lg:text-7xl font-black tracking-tight leading-tight text-white max-w-3xl mx-auto relative">
                  <span className="relative inline-block">
                    About TaskFlow<br />
                    Our Mission to Simplify
                    {/* Curved SVG underline */}
                    <svg
                      className="absolute left-0 -bottom-4 w-full h-4 pointer-events-none sm:-bottom-5 sm:h-5"
                      viewBox="0 0 100 10"
                      preserveAspectRatio="none"
                    >
                      <path
                        d="M2,5 Q50,10 98,5"
                        stroke="url(#taskflow-about-grad)"
                        strokeWidth="2"
                        fill="none"
                        strokeLinecap="round"
                        opacity="0.8"
                      />
                      <defs>
                        <linearGradient id="taskflow-about-grad" x1="0%" y1="0%" x2="100%" y2="0%">
                          <stop offset="0%" stopColor="#5eead4" />
                          <stop offset="100%" stopColor="#67e8f9" />
                        </linearGradient>
                      </defs>
                    </svg>
                  </span>
                </h1>

                {/* Premium animated paragraph */}
                <p className="text-base md:text-lg text-slate-300/90 font-medium max-w-2xl mx-auto leading-relaxed">
                  Learn about our journey to create the most intuitive, beautiful task management experience.
                </p>
              </div>
            </section>

            {/* Our Story Section */}
            <section className="py-16">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                <div className="space-y-6">
                  <h2 className="text-3xl font-bold text-white">Our Journey</h2>
                  <p className="text-slate-300 leading-relaxed">
                    TaskFlow was born from a simple frustration: existing task managers were either too complex with overwhelming features,
                    or too simplistic to handle real-world workflows. We set out to create something different—a tool that stays out
                    of your way while helping you accomplish more.
                  </p>
                  <p className="text-slate-300 leading-relaxed">
                    Our mission is to help individuals and teams focus on what matters most by providing a clean, intuitive interface
                    that makes task management feel effortless rather than burdensome.
                  </p>
                  <div className="flex items-center space-x-4 pt-4">
                    <div className="p-3 bg-slate-800/50 backdrop-blur-sm rounded-lg border border-slate-700/30">
                      <Heart className={`w-6 h-6 ${accentColor}`} />
                    </div>
                    <p className="text-slate-300">
                      Built with passion for productivity and user experience
                    </p>
                  </div>
                </div>
                <div className="bg-slate-800/30 backdrop-blur-sm rounded-2xl p-8 border border-slate-700/30">
                  <div className="aspect-video bg-gradient-to-br from-slate-700/40 to-slate-800/40 rounded-xl flex items-center justify-center">
                    <div className="text-center">
                      <ListTodo className="w-16 h-16 text-cyan-400 mx-auto mb-4" />
                      <p className="text-slate-400">TaskFlow Interface Preview</p>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            {/* Values Section */}
            <section className="py-16">
              <h2 className="text-3xl font-bold text-white text-center mb-12">Our Core Values</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div className="bg-slate-800/30 backdrop-blur-sm rounded-2xl p-6 border border-slate-700/30 text-center">
                  <div className="p-4 bg-cyan-500/10 rounded-xl inline-block mb-4">
                    <Code className={`w-8 h-8 ${accentColor}`} />
                  </div>
                  <h3 className="text-xl font-bold text-white mb-2">Simplicity First</h3>
                  <p className="text-slate-400">
                    We believe in removing friction, not features. Every addition undergoes rigorous simplicity testing.
                  </p>
                </div>
                <div className="bg-slate-800/30 backdrop-blur-sm rounded-2xl p-6 border border-slate-700/30 text-center">
                  <div className="p-4 bg-teal-500/10 rounded-xl inline-block mb-4">
                    <Users className={`w-8 h-8 ${accentColor}`} />
                  </div>
                  <h3 className="text-xl font-bold text-white mb-2">User Focused</h3>
                  <p className="text-slate-400">
                    Every decision starts with how it impacts your daily workflow and productivity goals.
                  </p>
                </div>
                <div className="bg-slate-800/30 backdrop-blur-sm rounded-2xl p-6 border border-slate-700/30 text-center">
                  <div className="p-4 bg-emerald-500/10 rounded-xl inline-block mb-4">
                    <Globe className={`w-8 h-8 ${accentColor}`} />
                  </div>
                  <h3 className="text-xl font-bold text-white mb-2">Privacy First</h3>
                  <p className="text-slate-400">
                    Your tasks are yours alone. We employ industry-leading security practices to protect your data.
                  </p>
                </div>
              </div>
            </section>

            {/* Creator Section */}
            <section className="py-16">
              <h2 className="text-3xl font-bold text-white text-center mb-12">Meet the Creator</h2>
              <div className="flex justify-center">
                <div className="bg-slate-800/30 backdrop-blur-sm rounded-2xl p-8 border border-slate-700/30 text-center max-w-md w-full">
                  <div className="w-32 h-32 mx-auto mb-6 rounded-full overflow-hidden border-4 border-cyan-500/30">
                    <img
                      src="/man.png"
                      alt="Creator"
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <h3 className="text-2xl font-bold text-white mb-2">Huzaifa</h3>
                  <p className="text-cyan-400 font-medium mb-4">Founder & Developer</p>
                  <p className="text-slate-300">
                    Passionate developer who created TaskFlow to help people manage their tasks more effectively.
                  </p>
                </div>
              </div>
            </section>
          </div>
        </main>

        <Footer setView={() => {}} />
      </div>
    </div>
  );
};

export default AboutPage;