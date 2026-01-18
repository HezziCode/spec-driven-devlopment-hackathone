'use client';

// Toast notification component for TaskFlow Dashboard
// Features wave-themed styling with accessibility support

import React, { useEffect, useState } from 'react';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

interface ToastProps {
  message: string;
  type?: ToastType;
  visible: boolean;
  onClose: () => void;
  duration?: number; // Auto-close duration in ms, set to 0 to disable auto-close
  className?: string;
}

const Toast: React.FC<ToastProps> = ({
  message,
  type = 'info',
  visible,
  onClose,
  duration = 5000,
  className = ''
}) => {
  const [isVisible, setIsVisible] = useState(false);

  // Handle visibility changes
  useEffect(() => {
    setIsVisible(visible);
  }, [visible]);

  // Auto-close functionality
  useEffect(() => {
    if (isVisible && duration > 0) {
      const timer = setTimeout(() => {
        setIsVisible(false);
        onClose();
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [isVisible, duration, onClose]);

  // Don't render if not visible
  if (!isVisible) return null;

  // Type-based styling
  const typeStyles = {
    success: {
      bg: 'bg-green-100 dark:bg-green-900/30',
      border: 'border-green-500 dark:border-green-700',
      text: 'text-green-800 dark:text-green-200',
      icon: '✓'
    },
    error: {
      bg: 'bg-red-100 dark:bg-red-900/30',
      border: 'border-red-500 dark:border-red-700',
      text: 'text-red-800 dark:text-red-200',
      icon: '✕'
    },
    warning: {
      bg: 'bg-yellow-100 dark:bg-yellow-900/30',
      border: 'border-yellow-500 dark:border-yellow-700',
      text: 'text-yellow-800 dark:text-yellow-200',
      icon: '⚠'
    },
    info: {
      bg: 'bg-blue-100 dark:bg-blue-900/30',
      border: 'border-blue-500 dark:border-blue-700',
      text: 'text-blue-800 dark:text-blue-200',
      icon: 'ℹ'
    }
  };

  const styles = typeStyles[type];

  return (
    <div
      className={`
        fixed bottom-4 right-4 z-50
        transform transition-all duration-300 ease-in-out
        ${isVisible ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'}
        ${styles.bg} ${styles.border}
        border-l-4 rounded-md shadow-lg
        max-w-xs w-full p-4
        ${className}
      `}
      role="alert"
      aria-live="polite"
    >
      <div className="flex items-start">
        <div className={`
          flex-shrink-0 w-5 h-5 rounded-full flex items-center justify-center
          ${type === 'success' ? 'bg-green-500' :
            type === 'error' ? 'bg-red-500' :
            type === 'warning' ? 'bg-yellow-500' : 'bg-blue-500'}
          text-white text-xs font-bold
        `}>
          {styles.icon}
        </div>
        <div className={`ml-3 ${styles.text} flex-1`}>
          <p className="text-sm font-medium">{message}</p>
        </div>
        <button
          onClick={() => {
            setIsVisible(false);
            setTimeout(onClose, 300); // Wait for animation to complete
          }}
          className={`
            ml-4 flex-shrink-0 rounded-md
            ${styles.text} hover:opacity-80 focus:outline-none
            focus:ring-2 focus:ring-offset-2
            ${type === 'success' ? 'focus:ring-green-500' :
              type === 'error' ? 'focus:ring-red-500' :
              type === 'warning' ? 'focus:ring-yellow-500' : 'focus:ring-blue-500'}
          `}
          aria-label="Close notification"
        >
          <span className="text-lg">×</span>
        </button>
      </div>
    </div>
  );
};

// Toast container to manage multiple toasts
interface ToastContainerProps {
  toasts: Array<{
    id: string;
    message: string;
    type: ToastType;
    duration?: number;
  }>;
  onRemove: (id: string) => void;
}

export const ToastContainer: React.FC<ToastContainerProps> = ({ toasts, onRemove }) => {
  return (
    <div className="fixed bottom-4 right-4 z-50 space-y-2">
      {toasts.map((toast) => (
        <Toast
          key={toast.id}
          message={toast.message}
          type={toast.type}
          visible={true}
          onClose={() => onRemove(toast.id)}
          duration={toast.duration}
        />
      ))}
    </div>
  );
};

// Toast hook for easy usage
export const useToast = () => {
  const [toasts, setToasts] = useState<Array<{
    id: string;
    message: string;
    type: ToastType;
    duration?: number;
  }>>([]);

  const addToast = (message: string, type: ToastType, duration?: number) => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, message, type, duration }]);
  };

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  };

  const success = (message: string, duration?: number) => {
    addToast(message, 'success', duration);
  };

  const error = (message: string, duration?: number) => {
    addToast(message, 'error', duration);
  };

  const warning = (message: string, duration?: number) => {
    addToast(message, 'warning', duration);
  };

  const info = (message: string, duration?: number) => {
    addToast(message, 'info', duration);
  };

  return {
    toasts,
    addToast,
    removeToast,
    success,
    error,
    warning,
    info,
    ToastContainer: () => <ToastContainer toasts={toasts} onRemove={removeToast} />
  };
};

export default Toast;