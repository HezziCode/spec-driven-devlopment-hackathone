'use client';

// Streak counter component with wave-themed animations for TaskWave Dashboard
// Displays user's completion streak with visual feedback

import React, { useState, useEffect } from 'react';
import WaveSpinner from './WaveSpinner';

interface StreakCounterProps {
  currentStreak: number;
  longestStreak: number;
  lastCompletedDate: string;
  userId?: string;
  loading?: boolean;
}

const StreakCounter: React.FC<StreakCounterProps> = ({
  currentStreak,
  longestStreak,
  lastCompletedDate,
  loading = false
}) => {
  const [currentStreakCount, setCurrentStreakCount] = useState(currentStreak);
  const [longestStreakCount, setLongestStreakCount] = useState(longestStreak);
  const [lastCompleted, setLastCompleted] = useState(lastCompletedDate);
  const [isLoading, setIsLoading] = useState(loading);

  // Simulate loading data
  useEffect(() => {
    if (isLoading) {
      // Simulate API response
      setTimeout(() => {
        setCurrentStreakCount(currentStreak);
        setLongestStreakCount(longestStreak);
        setLastCompleted(lastCompletedDate);
        setIsLoading(false);
      }, 800);
    } else {
      setCurrentStreakCount(currentStreak);
      setLongestStreakCount(longestStreak);
      setLastCompleted(lastCompletedDate);
    }
  }, [currentStreak, longestStreak, lastCompletedDate, isLoading]);

  // Format date for display
  const formatDate = (dateString: string) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  // Calculate days since last completion
  const daysSinceLastCompletion = lastCompleted ?
    Math.floor((new Date().getTime() - new Date(lastCompleted).getTime()) / (1000 * 60 * 60 * 24)) :
    null;

  if (isLoading) {
    return (
      <div className="flex justify-center items-center p-8 bg-slate-800/90 rounded-xl border border-slate-700/50">
        <WaveSpinner size="md" color="primary" />
      </div>
    );
  }

  return (
    <div className="bg-slate-800/90 rounded-xl p-6 border border-slate-700/50">
      <div className="flex flex-col md:flex-row justify-between items-center">
        <div className="text-center md:text-left mb-4 md:mb-0">
          <h2 className="text-xl font-bold text-slate-200 mb-1">
            Wave Streak: <span className="text-cyan-400 font-extrabold">{currentStreakCount} days</span>
          </h2>
          <p className="text-slate-400 text-sm">
            Your longest streak: <span className="font-semibold">{longestStreakCount} days</span>
          </p>
        </div>

        <div className="flex items-center space-x-6">
          {/* Current streak visualization */}
          <div className="flex items-center">
            <div className="flex">
              {Array.from({ length: Math.min(7, currentStreakCount) }).map((_, index) => (
                <div
                  key={index}
                  className={`
                    w-3 h-8 mx-0.5 rounded-t-lg
                    ${index < 3 ? 'bg-red-500' : index < 5 ? 'bg-yellow-500' : 'bg-green-500'}
                    animate-wave-pulse
                    ${index === Math.min(6, currentStreakCount - 1) ? 'animate-wave-ripple' : ''}
                  `}
                  style={{ animationDelay: `${index * 0.1}s` }}
                ></div>
              ))}
              {currentStreakCount === 0 && (
                <div className="text-slate-500 italic">No streak yet</div>
              )}
            </div>
          </div>

          {/* Last completed date */}
          {lastCompleted && (
            <div className="text-center md:text-right">
              <p className="text-xs text-slate-500">Last completed</p>
              <p className="font-medium text-slate-300">
                {formatDate(lastCompleted)}
              </p>
              {daysSinceLastCompletion !== null && daysSinceLastCompletion > 0 && (
                <p className="text-xs text-slate-500">
                  {daysSinceLastCompletion} days ago
                </p>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Motivational message */}
      {currentStreakCount > 0 && (
        <div className="mt-4 text-center">
          <p className="text-sm text-slate-300 italic">
            {currentStreakCount >= 7
              ? '🎉 Amazing streak! Keep up the great work!'
              : currentStreakCount >= 3
              ? '🔥 You\'re on fire! Keep going!'
              : '💪 Great job maintaining your streak!'}
          </p>
        </div>
      )}

      {/* Wave animation styles */}
      <style jsx>{`
        @keyframes wave-pulse {
          0%, 100% { transform: scaleY(1); }
          50% { transform: scaleY(1.1); }
        }

        @keyframes wave-ripple {
          0% {
            transform: scaleY(1);
            box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4);
          }
          70% {
            transform: scaleY(1.1);
            box-shadow: 0 0 0 10px rgba(16, 185, 129, 0);
          }
          100% {
            transform: scaleY(1);
            box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
          }
        }

        .animate-wave-pulse {
          animation: wave-pulse 2s ease-in-out infinite;
        }

        .animate-wave-ripple {
          animation: wave-ripple 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
      `}</style>
    </div>
  );
};

export default StreakCounter;