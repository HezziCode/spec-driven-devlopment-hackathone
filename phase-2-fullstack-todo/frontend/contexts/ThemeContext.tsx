'use client';

// Theme Context for TaskFlow Dashboard
// Manages light/dark mode and provides theme-related utilities

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';

// Define theme types
type Theme = 'light' | 'dark';

// Define context type
interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
  setTheme: (theme: Theme) => void;
  isDarkMode: boolean;
}

// Create context with default values
const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

// Theme provider component
interface ThemeProviderProps {
  children: ReactNode;
  defaultTheme?: Theme;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({
  children,
  defaultTheme = 'light'
}) => {
  const [theme, setThemeState] = useState<Theme>(defaultTheme);

  // Check for saved theme in localStorage or prefer-color-scheme
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') as Theme | null;
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    if (savedTheme) {
      setThemeState(savedTheme);
    } else if (systemPrefersDark) {
      setThemeState('dark');
    }
  }, []);

  // Apply theme to document
  useEffect(() => {
    if (theme) {
      document.documentElement.classList.remove('light', 'dark');
      document.documentElement.classList.add(theme);
      localStorage.setItem('theme', theme);
    }
  }, [theme]);

  // Toggle between light and dark themes
  const toggleTheme = () => {
    setThemeState(prev => {
      const newTheme = prev === 'light' ? 'dark' : 'light';
      localStorage.setItem('theme', newTheme);
      return newTheme;
    });
  };

  // Set theme directly
  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme);
    localStorage.setItem('theme', newTheme);
  };

  // Check if current theme is dark mode
  const isDarkMode = theme === 'dark';

  const contextValue: ThemeContextType = {
    theme,
    toggleTheme,
    setTheme,
    isDarkMode
  };

  return (
    <ThemeContext.Provider value={contextValue}>
      {children}
    </ThemeContext.Provider>
  );
};

// Custom hook to use the theme context
export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

// Utility function to get current theme
export const getCurrentTheme = (): Theme => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('theme') as Theme || 'light';
  }
  return 'light';
};

// Theme-related CSS variables for consistent styling
export const themeVariables = {
  light: {
    // Teal/Cyan gradient colors
    'primary-gradient-start': '#14b8a6', // teal-500
    'primary-gradient-end': '#06b6d4',  // cyan-500
    'primary-accent': '#0891b2',        // teal-600
    'secondary-accent': '#0e7490',      // cyan-600

    // Backgrounds
    'bg-primary': '#f0f9ff',            // bg-sky-50
    'bg-secondary': '#ffffff',          // white
    'bg-card': '#ffffff',               // white
    'bg-hover': '#f8fafc',              // gray-50

    // Text
    'text-primary': '#1e293b',          // gray-800
    'text-secondary': '#64748b',        // gray-500
    'text-muted': '#94a3b8',            // gray-400

    // Wave-themed elements
    'wave-primary': '#2dd4bf',          // teal-400
    'wave-secondary': '#06b6d4',        // cyan-500
    'wave-accent': '#0891b2',           // teal-600
  },
  dark: {
    // Teal/Cyan gradient colors (adjusted for dark mode)
    'primary-gradient-start': '#0d9488', // teal-600
    'primary-gradient-end': '#0891b2',  // cyan-600
    'primary-accent': '#115e59',        // teal-700
    'secondary-accent': '#0e7490',      // cyan-700

    // Backgrounds
    'bg-primary': '#0f172a',            // slate-900
    'bg-secondary': '#1e293b',          // slate-800
    'bg-card': '#1e293b',               // slate-800
    'bg-hover': '#334155',              // slate-700

    // Text
    'text-primary': '#f1f5f9',          // slate-100
    'text-secondary': '#cbd5e1',        // slate-300
    'text-muted': '#94a3b8',            // slate-400

    // Wave-themed elements
    'wave-primary': '#5eead4',          // teal-300
    'wave-secondary': '#22d3ee',        // cyan-400
    'wave-accent': '#0d9488',           // teal-600
  }
};

// Function to apply theme variables to document
export const applyThemeVariables = (theme: Theme) => {
  const root = document.documentElement;
  const vars = themeVariables[theme];

  Object.entries(vars).forEach(([key, value]) => {
    root.style.setProperty(`--${key}`, value);
  });
};

// Wave animation theme colors
export const getWaveAnimationColors = (theme: Theme) => {
  return theme === 'dark'
    ? { primary: '#5eead4', secondary: '#22d3ee' }
    : { primary: '#2dd4bf', secondary: '#06b6d4' };
};