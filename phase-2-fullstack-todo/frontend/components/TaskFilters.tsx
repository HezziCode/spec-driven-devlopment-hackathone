'use client';

// Task filtering component with flow-themed styling for TaskFlow Dashboard
// Provides UI controls for filtering tasks by status and priority

import React, { useState } from 'react';

interface TaskFiltersProps {
  onFilterChange?: (status: 'all' | 'active' | 'completed', priority: 'all' | 'low' | 'medium' | 'high' | 'critical') => void;
  initialStatus?: 'all' | 'active' | 'completed';
  initialPriority?: 'all' | 'low' | 'medium' | 'high' | 'critical';
}

const TaskFilters: React.FC<TaskFiltersProps> = ({
  onFilterChange,
  initialStatus = 'all',
  initialPriority = 'all'
}) => {
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'completed'>(initialStatus);
  const [priorityFilter, setPriorityFilter] = useState<'all' | 'low' | 'medium' | 'high' | 'critical'>(initialPriority);

  // Handle filter changes
  const handleStatusChange = (newStatus: 'all' | 'active' | 'completed') => {
    setStatusFilter(newStatus);
    onFilterChange?.(newStatus, priorityFilter);
  };

  const handlePriorityChange = (newPriority: 'all' | 'low' | 'medium' | 'high' | 'critical') => {
    setPriorityFilter(newPriority);
    onFilterChange?.(statusFilter, newPriority);
  };

  return (
    <div className="bg-slate-800/90 rounded-xl p-4 border border-slate-700/50">
      <h3 className="text-lg font-bold text-white mb-4">Task Filters</h3>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Status Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Status</label>
          <div className="flex flex-wrap gap-2">
            {(['all', 'active', 'completed'] as const).map(option => (
              <button
                key={option}
                type="button"
                onClick={() => handleStatusChange(option)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200
                  ${statusFilter === option
                    ? 'bg-cyan-600 text-white shadow-lg shadow-cyan-500/30'
                    : 'bg-slate-700 text-slate-300 hover:bg-slate-600'}`}
              >
                {option === 'all' ? 'All Tasks' :
                 option === 'active' ? 'Active' : 'Completed'}
              </button>
            ))}
          </div>
        </div>

        {/* Priority Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Priority</label>
          <div className="flex flex-wrap gap-2">
            {(['all', 'low', 'medium', 'high', 'critical'] as const).map(option => (
              <button
                key={option}
                type="button"
                onClick={() => handlePriorityChange(option)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200
                  ${priorityFilter === option
                    ? option === 'high' || option === 'critical'
                      ? 'bg-red-600 text-white shadow-lg shadow-red-500/30'
                      : option === 'medium'
                        ? 'bg-amber-600 text-white shadow-lg shadow-amber-500/30'
                        : 'bg-emerald-600 text-white shadow-lg shadow-emerald-500/30'
                    : 'bg-slate-700 text-slate-300 hover:bg-slate-600'}`}
              >
                {option === 'all' ? 'All Priorities' :
                 option === 'high' ? 'High' :
                 option === 'critical' ? 'Critical' :
                 option.charAt(0).toUpperCase() + option.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TaskFilters;