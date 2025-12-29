'use client';

// Enhanced Task filtering component with search, tag, sort, and advanced filtering
// Provides comprehensive UI controls for filtering tasks by multiple criteria
// Features debounced search input for optimal performance

import React, { useState, useEffect, useCallback } from 'react';
import { Search, X, Filter, SortAsc } from 'lucide-react';
import type { SortEnum } from '@/types/api';

interface TaskFiltersProps {
  statusFilter: 'all' | 'active' | 'completed';
  priorityFilter: 'all' | 'low' | 'medium' | 'high' | 'critical';
  searchQuery: string;
  tagFilter: string;
  sortOrder: SortEnum;
  onStatusChange: (status: 'all' | 'active' | 'completed') => void;
  onPriorityChange: (priority: 'all' | 'low' | 'medium' | 'high' | 'critical') => void;
  onSearchChange: (search: string) => void;
  onTagChange: (tag: string) => void;
  onSortChange: (sort: SortEnum) => void;
}

const TaskFilters: React.FC<TaskFiltersProps> = ({
  statusFilter,
  priorityFilter,
  searchQuery,
  tagFilter,
  sortOrder,
  onStatusChange,
  onPriorityChange,
  onSearchChange,
  onTagChange,
  onSortChange,
}) => {
  // Local state for search input with debouncing
  const [localSearch, setLocalSearch] = useState<string>(searchQuery);
  const [localTag, setLocalTag] = useState<string>(tagFilter);

  // Debounce search input (300ms)
  useEffect(() => {
    const timer = setTimeout(() => {
      if (localSearch !== searchQuery) {
        onSearchChange(localSearch);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [localSearch, searchQuery, onSearchChange]);

  // Debounce tag input (300ms)
  useEffect(() => {
    const timer = setTimeout(() => {
      if (localTag !== tagFilter) {
        onTagChange(localTag);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [localTag, tagFilter, onTagChange]);

  // Sync with prop changes (for URL-based initialization)
  useEffect(() => {
    setLocalSearch(searchQuery);
  }, [searchQuery]);

  useEffect(() => {
    setLocalTag(tagFilter);
  }, [tagFilter]);

  // Clear search
  const clearSearch = () => {
    setLocalSearch('');
    onSearchChange('');
  };

  // Clear tag filter
  const clearTag = () => {
    setLocalTag('');
    onTagChange('');
  };

  // Clear all filters
  const clearAllFilters = () => {
    onStatusChange('all');
    onPriorityChange('all');
    setLocalSearch('');
    onSearchChange('');
    setLocalTag('');
    onTagChange('');
    onSortChange('created');
  };

  return (
    <div className="mb-8 bg-slate-800/20 backdrop-blur-sm rounded-xl p-6 border border-slate-700/20">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <Filter className="text-cyan-400" size={20} />
          <h3 className="text-lg font-bold text-white">Filters & Search</h3>
        </div>
        <button
          onClick={clearAllFilters}
          className="text-sm text-cyan-400 hover:text-cyan-300 transition-colors"
        >
          Clear All
        </button>
      </div>

      <div className="space-y-4">
        {/* Search Input */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            <Search size={14} className="inline mr-1" />
            Search Tasks
          </label>
          <div className="relative">
            <input
              type="text"
              value={localSearch}
              onChange={(e) => setLocalSearch(e.target.value)}
              placeholder="Search by title or description..."
              className="w-full bg-slate-700/40 backdrop-blur-sm border border-slate-600/50 rounded-lg px-4 py-2.5 pr-10 text-sm text-slate-300 placeholder-slate-500 focus:ring-2 focus:ring-cyan-500 outline-none"
            />
            {localSearch && (
              <button
                onClick={clearSearch}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-300 transition-colors"
              >
                <X size={16} />
              </button>
            )}
          </div>
        </div>

        {/* Tag Filter Input */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Filter by Tag
          </label>
          <div className="relative">
            <input
              type="text"
              value={localTag}
              onChange={(e) => setLocalTag(e.target.value)}
              placeholder="Enter tag name..."
              className="w-full bg-slate-700/40 backdrop-blur-sm border border-slate-600/50 rounded-lg px-4 py-2.5 pr-10 text-sm text-slate-300 placeholder-slate-500 focus:ring-2 focus:ring-cyan-500 outline-none"
            />
            {localTag && (
              <button
                onClick={clearTag}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-300 transition-colors"
              >
                <X size={16} />
              </button>
            )}
          </div>
        </div>

        {/* Status and Priority Filters */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Status Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Status</label>
            <select
              value={statusFilter}
              onChange={(e) => onStatusChange(e.target.value as 'all' | 'active' | 'completed')}
              className="w-full bg-slate-700/40 backdrop-blur-sm border border-slate-600/50 rounded-lg px-4 py-2.5 text-sm text-slate-300 focus:ring-2 focus:ring-cyan-500 outline-none appearance-none cursor-pointer [&>option]:bg-slate-800 [&>option]:text-slate-200"
            >
              <option value="all">All Tasks</option>
              <option value="active">Active</option>
              <option value="completed">Completed</option>
            </select>
          </div>

          {/* Priority Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Priority</label>
            <select
              value={priorityFilter}
              onChange={(e) => onPriorityChange(e.target.value as 'all' | 'low' | 'medium' | 'high' | 'critical')}
              className="w-full bg-slate-700/40 backdrop-blur-sm border border-slate-600/50 rounded-lg px-4 py-2.5 text-sm text-slate-300 focus:ring-2 focus:ring-cyan-500 outline-none appearance-none cursor-pointer [&>option]:bg-slate-800 [&>option]:text-slate-200"
            >
              <option value="all">All Priorities</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
          </div>
        </div>

        {/* Sort Order */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            <SortAsc size={14} className="inline mr-1" />
            Sort By
          </label>
          <select
            value={sortOrder}
            onChange={(e) => onSortChange(e.target.value as SortEnum)}
            className="w-full bg-slate-700/40 backdrop-blur-sm border border-slate-600/50 rounded-lg px-4 py-2.5 text-sm text-slate-300 focus:ring-2 focus:ring-cyan-500 outline-none appearance-none cursor-pointer [&>option]:bg-slate-800 [&>option]:text-slate-200"
          >
            <option value="created">Newest First</option>
            <option value="updated">Recently Updated</option>
            <option value="title">Alphabetical (A-Z)</option>
            <option value="priority">Priority (High to Low)</option>
          </select>
        </div>
      </div>
    </div>
  );
};

export default TaskFilters;
