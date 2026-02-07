'use client';

// Interactive task card component with flow-themed animations for TaskFlow Dashboard
// Displays task information with priority badges, completion toggle, edit, and delete actions

import React, { useState } from 'react';
import { Edit2, Trash2, X, Check } from 'lucide-react';

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
  const [isHovered, setIsHovered] = useState(false);
  const [showConfirmDelete, setShowConfirmDelete] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);

  // Handle completion toggle with double-click prevention
  const handleToggleComplete = async () => {
    if (onToggleComplete && !isProcessing) {
      setIsProcessing(true);
      onToggleComplete(id, !completed);
      // Reset after a short delay to allow the action to complete
      setTimeout(() => setIsProcessing(false), 500);
    }
  };

  // Handle delete confirmation with double-click prevention
  const handleDelete = () => {
    if (onDelete && !isProcessing) {
      setIsProcessing(true);
      onDelete(id);
      setShowConfirmDelete(false);
    }
  };

  // Handle edit
  const handleEdit = () => {
    if (onEdit) {
      onEdit({ id, title, description, completed, priority, tags, userId, createdAt, updatedAt });
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

  // Subtle tag styling system - minimal and clean
  const getTagColor = (tag: string) => {
    const tagLower = tag.toLowerCase();

    // work - Subtle blue
    if (tagLower === 'work') {
      return "bg-blue-500/20 text-blue-300 border-blue-500/30";
    }

    // personal - Subtle purple
    if (tagLower === 'personal') {
      return "bg-purple-500/20 text-purple-300 border-purple-500/30";
    }

    // focus - Subtle indigo
    if (tagLower === 'focus') {
      return "bg-indigo-500/20 text-indigo-300 border-indigo-500/30";
    }

    // meeting - Subtle orange
    if (tagLower === 'meeting') {
      return "bg-orange-500/20 text-orange-300 border-orange-500/30";
    }

    // urgent - Red (slightly more visible)
    if (tagLower === 'urgent') {
      return "bg-red-500/25 text-red-300 border-red-500/40";
    }

    // health - Subtle green
    if (tagLower === 'health') {
      return "bg-emerald-500/20 text-emerald-300 border-emerald-500/30";
    }

    // Legacy support for existing user tags
    if (tagLower === 'enjoyment') return "bg-indigo-500/20 text-indigo-300 border-indigo-500/30";
    if (tagLower === 'friend zone') return "bg-pink-500/20 text-pink-300 border-pink-500/30";

    // Default for any other tags - Neutral gray/slate
    return "bg-slate-600/20 text-slate-400 border-slate-500/30";
  };

  return (
    <div className="h-full">
      <div className={`relative h-full p-5 rounded-xl bg-slate-800/30 backdrop-blur-sm border border-slate-700/20 overflow-hidden group transition-all duration-300 hover:bg-slate-800/40`}>
        <div className="relative z-10 flex flex-col h-full">
          <div className="flex justify-between items-start mb-3">
            <span className={`px-2.5 py-0.5 rounded-md text-xs font-bold bg-gradient-to-r ${priorityColors[priority]} font-display backdrop-blur-sm`}>
              {priority.charAt(0).toUpperCase() + priority.slice(1)}
            </span>
          </div>

          <h3 className={`text-base font-semibold text-white mb-2 line-clamp-2 ${completed ? 'line-through text-slate-500' : ''} font-display`}>
            {title}
          </h3>
          <p className="text-xs text-slate-400 mb-3 line-clamp-2 flex-grow font-body">
            {description}
          </p>

          <div className="flex flex-wrap gap-1 mb-4">
            {tags.map(tag => (
                <span key={tag} className={`text-[10px] uppercase font-medium backdrop-blur-sm px-1.5 py-0.5 rounded border ${getTagColor(tag)}`}>
                    #{tag}
                </span>
            ))}
          </div>

          <div className="mt-auto space-y-2">
            <button
                onClick={handleToggleComplete}
                disabled={isProcessing}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-300 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed
                ${completed
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 backdrop-blur-sm'
                    : 'bg-gradient-to-r from-cyan-600/20 to-blue-600/20 hover:shadow-sm hover:shadow-cyan-500/10 text-cyan-300 border border-cyan-500/30 backdrop-blur-sm'}`}
            >
                {isProcessing ? 'Processing...' : completed ? <><Check className="w-3 h-3" /> Completed</> : 'Mark Complete'}
            </button>

            <div className="text-[10px] text-slate-500 flex justify-between items-center pt-1">
              <span>Created: {formatDate(createdAt)}</span>
              {updatedAt !== createdAt && (
                <span>Updated: {formatDate(updatedAt)}</span>
              )}
            </div>
          </div>

          {/* Edit and Delete Actions */}
          <div className="absolute top-2 right-2 flex gap-1 opacity-100 transition-opacity duration-200 z-30">
            <button
              onClick={handleEdit}
              className="p-1.5 rounded-lg bg-slate-700/50 hover:bg-cyan-600/30 text-slate-400 hover:text-cyan-300 transition-colors cursor-pointer"
              title="Edit task"
            >
              <Edit2 className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setShowConfirmDelete(true)}
              className="p-1.5 rounded-lg bg-slate-700/50 hover:bg-red-600/30 text-slate-400 hover:text-red-400 transition-colors cursor-pointer"
              title="Delete task"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Delete Confirmation Modal */}
          {showConfirmDelete && (
            <div className="absolute inset-0 bg-slate-900/80 backdrop-blur-sm flex items-center justify-center z-20 rounded-xl">
              <div className="bg-slate-800 border border-slate-600 rounded-lg p-4 shadow-xl max-w-xs mx-4">
                <p className="text-white text-sm font-medium mb-3 text-center">
                  Delete this task?
                </p>
                <div className="flex gap-2 justify-center">
                  <button
                    onClick={() => setShowConfirmDelete(false)}
                    className="px-3 py-1.5 rounded-lg bg-slate-700 text-slate-300 text-xs font-medium hover:bg-slate-600 transition-colors cursor-pointer"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleDelete}
                    disabled={isProcessing}
                    className="px-3 py-1.5 rounded-lg bg-red-600/80 text-white text-xs font-medium hover:bg-red-600 transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isProcessing ? 'Deleting...' : 'Delete'}
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TaskCard;