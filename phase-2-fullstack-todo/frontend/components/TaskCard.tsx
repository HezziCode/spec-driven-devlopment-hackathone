'use client';

// Interactive task card component with flow-themed animations for TaskFlow Dashboard
// Displays task information with priority badges and completion toggle - Dashboard Style

import React, { useState } from 'react';

interface TaskCardProps {
  id: string;
  title: string;
  description: string;
  completed: boolean;
  priority: 'high' | 'medium' | 'low' | 'critical';
  tags: string[];
  createdAt: string;
  updatedAt: string;
  userId: string;
  onToggleComplete?: (id: string, completed: boolean) => void;
  onDelete?: (id: string) => void;
  onEdit?: (task: any) => void;
}

const TaskCard: React.FC<TaskCardProps> = ({
  id,
  title,
  description,
  completed,
  priority,
  tags,
  createdAt,
  updatedAt,
  userId,
  onToggleComplete,
  onDelete,
  onEdit
}) => {
  // Handle completion toggle
  const handleToggleComplete = () => {
    if (onToggleComplete) {
      onToggleComplete(id, !completed);
    }
  };

  // Format date for display
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  // Priority color configuration for dashboard style
  const priorityColors = {
    high: "from-red-100 to-red-200 dark:from-red-500/20 dark:to-red-600/5 border-red-200 dark:border-red-500/30 text-red-700 dark:text-red-400",
    medium: "from-amber-100 to-amber-200 dark:from-amber-500/20 dark:to-amber-600/5 border-amber-200 dark:border-amber-500/30 text-amber-700 dark:text-amber-400",
    low: "from-emerald-100 to-emerald-200 dark:from-emerald-500/20 dark:to-emerald-600/5 border-emerald-200 dark:border-emerald-500/30 text-emerald-700 dark:text-emerald-400",
    critical: "from-rose-100 to-rose-200 dark:from-rose-500/20 dark:to-rose-600/5 border-rose-200 dark:border-rose-500/30 text-rose-700 dark:text-rose-400",
  };

  return (
    <div className="h-full">
      <div className={`relative h-full p-5 rounded-xl bg-slate-800/30 backdrop-blur-sm border border-slate-700/20 overflow-hidden group transition-all duration-300 hover:bg-slate-800/40`}>
        <div className="relative z-10 flex flex-col h-full">
          <div className="flex justify-between items-start mb-3">
            <span className={`px-2.5 py-0.5 rounded-md text-xs font-bold bg-gradient-to-r ${priorityColors[priority]} font-display backdrop-blur-sm`}>
              {priority.charAt(0).toUpperCase() + priority.slice(1)}
            </span>
            <div className="text-xs text-slate-500">
              {formatDate(createdAt)}
            </div>
          </div>

          <h3 className={`text-base font-semibold text-white mb-2 line-clamp-2 ${completed ? 'line-through text-slate-500' : ''} font-display`}>
            {title}
          </h3>
          <p className="text-xs text-slate-400 mb-3 line-clamp-2 flex-grow font-body">
            {description}
          </p>

          <div className="flex flex-wrap gap-1 mb-4">
            {tags.map(tag => (
                <span key={tag} className="text-[10px] uppercase font-medium text-slate-400 bg-slate-700/30 backdrop-blur-sm px-1.5 py-0.5 rounded border border-slate-600/20">
                    #{tag}
                </span>
            ))}
          </div>

          <div className="mt-auto">
            <button
                onClick={handleToggleComplete}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-300
                ${completed
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 backdrop-blur-sm'
                    : 'bg-gradient-to-r from-cyan-600/20 to-blue-600/20 hover:shadow-sm hover:shadow-cyan-500/10 text-cyan-300 border border-cyan-500/30 backdrop-blur-sm'}`}
            >
                {completed ? <><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-check w-3 h-3"><polyline points="20 6 9 17 4 12"></polyline></svg> Completed</> : 'Mark Complete'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TaskCard;