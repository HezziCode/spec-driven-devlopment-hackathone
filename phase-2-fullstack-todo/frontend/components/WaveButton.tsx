'use client';

// Reusable wave-themed button component for TaskWave Dashboard
// Features wave animations and teal/cyan gradient theme

import React from 'react';

interface WaveButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'ghost' | 'destructive';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  className?: string;
  type?: 'button' | 'submit' | 'reset';
  href?: string; // For link buttons
}

const WaveButton: React.FC<WaveButtonProps> = ({
  children,
  onClick,
  variant = 'primary',
  size = 'md',
  disabled = false,
  className = '',
  type = 'button',
  href
}) => {
  // Base classes for all buttons
  const baseClasses = `
    inline-flex items-center justify-center rounded-md font-medium
    transition-all duration-300 ease-in-out
    focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2
    disabled:opacity-50 disabled:cursor-not-allowed
    transform hover:scale-105 active:scale-95
    relative overflow-hidden
  `;

  // Size classes
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg'
  };

  // Variant classes
  const variantClasses = {
    primary: `
      bg-gradient-to-r from-teal-500 to-cyan-500 text-white
      hover:from-teal-600 hover:to-cyan-600
      focus-visible:ring-teal-500
      shadow-lg hover:shadow-teal-500/30
      before:absolute before:inset-0 before:bg-gradient-to-r before:from-cyan-400 before:to-teal-400
      before:opacity-0 before:transition-opacity before:duration-300
      before:-z-10 hover:before:opacity-100
    `,
    secondary: `
      bg-gradient-to-r from-slate-100 to-slate-200 text-gray-900
      dark:from-slate-700 dark:to-slate-800 dark:text-white
      hover:from-slate-200 hover:to-slate-300
      dark:hover:from-slate-600 dark:hover:to-slate-700
      focus-visible:ring-slate-500
      shadow hover:shadow-md
    `,
    ghost: `
      bg-transparent text-gray-700 hover:bg-slate-100
      dark:text-gray-300 dark:hover:bg-slate-800
      focus-visible:ring-slate-500
    `,
    destructive: `
      bg-gradient-to-r from-red-500 to-rose-500 text-white
      hover:from-red-600 hover:to-rose-600
      focus-visible:ring-red-500
      shadow-lg hover:shadow-red-500/30
    `
  };

  const classes = `
    ${baseClasses}
    ${sizeClasses[size]}
    ${variantClasses[variant]}
    ${className}
  `;

  // Wave animation effect using CSS
  const waveEffect = `
    hover:animate-wave-ripple
  `;

  // If href is provided, render as a link
  if (href) {
    return (
      <a
        href={href}
        className={`${classes} ${waveEffect}`}
        onClick={disabled ? undefined : onClick}
      >
        {children}
      </a>
    );
  }

  // Otherwise, render as a button
  return (
    <button
      type={type}
      className={`${classes} ${waveEffect}`}
      onClick={disabled ? undefined : onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
};

export default WaveButton;