'use client';

import React from 'react';
import { Sun, Moon, ListTodo, LogOut, ArrowRight } from 'lucide-react';

interface NavbarProps {
  userId: string | null;
  handleAuthAction: (action: string) => void;
  isDarkMode: boolean;
  setIsDarkMode: (isDark: boolean) => void;
  setView: (view: string) => void;
}

const Navbar: React.FC<NavbarProps> = ({
  userId,
  handleAuthAction,
  isDarkMode,
  setIsDarkMode,
  setView
}) => {
  const accentColor = isDarkMode ? 'text-teal-400' : 'text-cyan-600';
  const bgColor = isDarkMode ? 'bg-slate-900/80' : 'bg-white/90';
  const borderColor = isDarkMode ? 'border-slate-700/50' : 'border-gray-200/50';
  const textColor = isDarkMode ? 'text-white' : 'text-gray-800';
  const iconColor = isDarkMode ? 'text-gray-400' : 'text-gray-500';
  const hoverBgColor = isDarkMode ? 'hover:bg-slate-800' : 'hover:bg-gray-50'; // Lighter hover background in light mode

  return (
    <nav className="sticky top-0 z-50 w-full backdrop-blur-md bg-white/90 dark:bg-slate-900/80 border-b border-gray-200/50 dark:border-slate-700/50 transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex justify-between items-center">

        {/* Logo and Name */}
        <div className="flex items-center space-x-2 cursor-pointer" onClick={() => setView('landing')}>
          <ListTodo className={`w-6 h-6 ${accentColor}`} />
          <span className="text-xl font-extrabold tracking-wide text-gray-800 dark:text-white transition-colors">
            TaskWave
          </span>
        </div>

        {/* Actions (Theme Switcher, Auth Button) */}
        <div className="flex items-center space-x-4">

          {/* Theme Switcher */}
          <button
            onClick={() => setIsDarkMode(prev => !prev)}
            className="p-2 rounded-full text-gray-500 hover:bg-gray-200 dark:text-gray-400 dark:hover:bg-slate-800 transition-all duration-300 transform hover:scale-110"
            aria-label="Toggle theme"
          >
            {isDarkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          </button>

          {/* Navigation/Auth Button */}
          {userId ? (
            <button
              onClick={() => handleAuthAction('signout')}
              className="px-3 py-1.5 flex items-center bg-red-500 hover:bg-red-600 text-white font-medium rounded-lg shadow-md transition-all duration-200 transform hover:scale-105 text-sm"
            >
              <LogOut className="w-4 h-4 mr-1" /> Sign Out
            </button>
          ) : (
            <button
              onClick={() => handleAuthAction('signin')}
              className="px-3 py-1.5 flex items-center bg-cyan-600 hover:bg-cyan-700 text-white font-medium rounded-lg shadow-md transition-all duration-200 transform hover:scale-105 text-sm"
            >
              Get Started
            </button>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;