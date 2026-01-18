'use client';

// Wave-themed loading spinner component for TaskFlow Dashboard
// Features wave animations with teal/cyan colors

import React from 'react';

interface WaveSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  color?: 'primary' | 'secondary' | 'accent';
  className?: string;
  label?: string; // Accessibility label for screen readers
}

const WaveSpinner: React.FC<WaveSpinnerProps> = ({
  size = 'md',
  color = 'primary',
  className = '',
  label = 'Loading...'
}) => {
  // Size classes
  const sizeClasses = {
    sm: 'w-6 h-6',
    md: 'w-10 h-10',
    lg: 'w-16 h-16'
  };

  // Color classes for the spinner
  const colorClasses = {
    primary: 'text-teal-500',
    secondary: 'text-cyan-500',
    accent: 'text-teal-600'
  };

  // Animation classes
  const animationClass = 'animate-spin-slow';

  // Wave ripple effect for the spinner
  const waveEffectClass = 'animate-wave-pulse';

  return (
    <div className="flex items-center justify-center">
      <div
        className={`
          relative ${sizeClasses[size]} ${colorClasses[color]}
          ${animationClass} ${waveEffectClass} ${className}
        `}
        role="status"
        aria-label={label}
      >
        {/* Main spinner circle */}
        <div className={`
          absolute inset-0 rounded-full border-4 border-current border-t-transparent
          ${sizeClasses[size]}
        `}></div>

        {/* Wave ripple effect 1 */}
        <div className={`
          absolute inset-0 rounded-full border-4 border-current border-t-transparent
          ${sizeClasses[size]} ${waveEffectClass}
          animate-wave-ripple-1
        `} style={{ animationDelay: '0s' }}></div>

        {/* Wave ripple effect 2 */}
        <div className={`
          absolute inset-0 rounded-full border-4 border-current border-t-transparent
          ${sizeClasses[size]} ${waveEffectClass}
          animate-wave-ripple-2
          opacity-70
        `} style={{ animationDelay: '0.3s' }}></div>

        {/* Wave ripple effect 3 */}
        <div className={`
          absolute inset-0 rounded-full border-4 border-current border-t-transparent
          ${sizeClasses[size]} ${waveEffectClass}
          animate-wave-ripple-3
          opacity-40
        `} style={{ animationDelay: '0.6s' }}></div>
      </div>

      {/* Screen reader accessible label */}
      <span className="sr-only">{label}</span>
    </div>
  );
};

export default WaveSpinner;

// Add the necessary CSS animations to be included in global styles
// These would typically go in your global CSS file or Tailwind config
const waveSpinnerStyles = `
  @keyframes spin-slow {
    to {
      transform: rotate(360deg);
    }
  }

  @keyframes wave-pulse {
    0%, 100% {
      transform: scale(1);
      opacity: 1;
    }
    50% {
      transform: scale(1.1);
      opacity: 0.7;
    }
  }

  @keyframes wave-ripple-1 {
    0% {
      transform: scale(0.8);
      opacity: 1;
    }
    100% {
      transform: scale(1.5);
      opacity: 0;
    }
  }

  @keyframes wave-ripple-2 {
    0% {
      transform: scale(0.9);
      opacity: 1;
    }
    100% {
      transform: scale(1.6);
      opacity: 0;
    }
  }

  @keyframes wave-ripple-3 {
    0% {
      transform: scale(1);
      opacity: 1;
    }
    100% {
      transform: scale(1.7);
      opacity: 0;
    }
  }

  .animate-spin-slow {
    animation: spin-slow 1.5s linear infinite;
  }

  .animate-wave-pulse {
    animation: wave-pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  }

  .animate-wave-ripple-1 {
    animation: wave-ripple-1 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  }

  .animate-wave-ripple-2 {
    animation: wave-ripple-2 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    animation-delay: 0.3s;
  }

  .animate-wave-ripple-3 {
    animation: wave-ripple-3 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    animation-delay: 0.6s;
  }
`;

// The above styles should be added to your global CSS file or Tailwind config
// For Tailwind, you might need to extend the theme to include these animations