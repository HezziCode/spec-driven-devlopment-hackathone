'use client';

// Enhanced task creation form with flow-themed styling for TaskFlow Dashboard - Dashboard Style
// Includes title, description, priority selection, and tag management with clickable chips

import React, { useState } from 'react';

interface TaskFormProps {
  onSubmit?: (title: string, description: string, priority: 'low' | 'medium' | 'high' | 'critical', tags: string[]) => void;
  onCancel?: () => void;
  initialData?: Partial<{ title: string; description: string; priority: 'low' | 'medium' | 'high' | 'critical'; tags: string[] }>;
  submitButtonText?: string;
}

const TaskForm: React.FC<TaskFormProps> = ({
  onSubmit,
  onCancel,
  initialData = {},
  submitButtonText = 'Deploy Strategy'
}) => {
  const [title, setTitle] = useState(initialData.title || '');
  const [description, setDescription] = useState(initialData.description || '');
  const [priority, setPriority] = useState(initialData.priority || 'medium');
  const [tags, setTags] = useState<string[]>(initialData.tags || []);
  const [tagInput, setTagInput] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Predefined tag options
  const predefinedTags = ['Design', 'Dev', 'Marketing', 'Meeting', 'Strategy', 'Urgent'];

  // Validate form fields
  const validate = () => {
    const newErrors: Record<string, string> = {};

    if (!title.trim()) {
      newErrors.title = 'Title is required';
    } else if (title.trim().length > 200) {
      newErrors.title = 'Title must be 200 characters or less';
    }

    if (description && description.length > 1000) {
      newErrors.description = 'Description must be 1000 characters or less';
    }

    if (tags.length > 10) {
      newErrors.tags = 'Maximum 10 tags allowed';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (validate()) {
      onSubmit?.(title.trim(), description, priority as 'low' | 'medium' | 'high' | 'critical', tags);

      // Reset form if not editing existing task
      if (!initialData?.title) {
        setTitle('');
        setDescription('');
        setPriority('medium');
        setTags([]);
        setTagInput('');
      }
    }
  };

  // Add a tag
  const addTag = (tag: string) => {
    const trimmedTag = tag.trim();
    if (trimmedTag && !tags.includes(trimmedTag) && tags.length < 10) {
      setTags([...tags, trimmedTag]);
      setTagInput(''); // Clear input when adding predefined tag
    }
  };

  // Remove a tag
  const removeTag = (tagToRemove: string) => {
    setTags(tags.filter(tag => tag !== tagToRemove));
  };

  // Add tag from input
  const addTagFromInput = () => {
    const trimmedInput = tagInput.trim();
    if (trimmedInput && !tags.includes(trimmedInput) && tags.length < 10) {
      setTags([...tags, trimmedInput]);
      setTagInput('');
    }
  };

  // Handle Enter key in tag input
  const handleTagInputKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addTagFromInput();
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 bg-slate-800/20 backdrop-blur-sm p-4 rounded-xl border border-slate-700/20">
      {/* Title field */}
      <div>
        <label htmlFor="title" className="block text-sm font-medium text-slate-300 mb-1">
          Task Title
        </label>
        <input
          type="text"
          id="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
          placeholder="e.g., Complete project proposal"
          className="w-full bg-slate-700/40 border border-slate-600/30 rounded-lg px-3 py-2 text-sm text-white focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 outline-none placeholder:text-slate-500"
        />
        {errors.title && <p className="mt-1 text-xs text-rose-400">{errors.title}</p>}
      </div>

      {/* Description field */}
      <div>
        <label htmlFor="description" className="block text-sm font-medium text-slate-300 mb-1">
          Description (Optional)
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Add details..."
          rows={2}
          className="w-full bg-slate-700/40 border border-slate-600/30 rounded-lg px-3 py-2 text-sm text-white focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 outline-none placeholder:text-slate-500 resize-none"
        />
        {errors.description && <p className="mt-1 text-xs text-rose-400">{errors.description}</p>}
      </div>

      {/* Priority & Tags */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="flex-1">
          <label htmlFor="priority" className="block text-sm font-medium text-slate-300 mb-1">
            Priority
          </label>
          <select
            id="priority"
            value={priority}
            onChange={(e) => setPriority(e.target.value)}
            className="w-full bg-slate-700/40 border border-slate-600/30 rounded-lg px-3 py-2 text-sm text-slate-300 focus:ring-2 focus:ring-cyan-500 outline-none appearance-none cursor-pointer"
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>
        </div>

        {/* Tags section */}
        <div className="flex-1">
          <label className="block text-sm font-medium text-slate-300 mb-1">
            Tags
          </label>
          <div className="flex flex-wrap gap-1.5">
            {predefinedTags.map(tag => (
              <button
                key={tag}
                type="button"
                onClick={() => addTag(tag)}
                className={`text-[10px] font-medium px-2 py-1 rounded-full border transition-all duration-200
                ${tags.includes(tag)
                    ? 'bg-cyan-500/20 border-cyan-500 text-cyan-400'
                    : 'bg-slate-700/40 border-slate-600/30 text-slate-400 hover:bg-slate-600/50 hover:text-slate-300'}`}
              >
                #{tag}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Custom tag input */}
      <div>
        <label htmlFor="custom-tag" className="block text-sm font-medium text-slate-300 mb-1">
          Add Custom Tag
        </label>
        <div className="flex">
          <input
            type="text"
            id="custom-tag"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            onKeyDown={handleTagInputKeyDown}
            placeholder="Enter tag..."
            className="flex-1 bg-slate-700/40 border border-slate-600/30 rounded-l-lg px-3 py-2 text-sm text-white focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 outline-none placeholder:text-slate-500"
          />
          <button
            type="button"
            onClick={addTagFromInput}
            className="px-3 bg-slate-700/50 hover:bg-slate-600/50 text-slate-300 font-medium rounded-r-lg transition-colors duration-200 border border-slate-600/30"
          >
            Add
          </button>
        </div>
        {errors.tags && <p className="mt-1 text-xs text-rose-400">{errors.tags}</p>}
      </div>

      {/* Selected tags display */}
      {tags.length > 0 && (
        <div className="mt-1.5">
          <label className="block text-xs font-medium text-slate-400 mb-1">
            Selected:
          </label>
          <div className="flex flex-wrap gap-1.5">
            {tags.map(tag => (
              <span
                key={tag}
                className="inline-flex items-center text-xs font-medium px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20"
              >
                #{tag}
                <button
                  type="button"
                  onClick={() => removeTag(tag)}
                  className="ml-1 text-cyan-400 hover:text-cyan-300 focus:outline-none text-[12px]"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>
      )}

      <button
        type="submit"
        className="w-full py-2.5 mt-2 bg-gradient-to-r from-cyan-600/80 to-teal-600/80 hover:from-cyan-500/80 hover:to-teal-500/80 text-white font-semibold rounded-lg transition-all duration-300 active:scale-[0.98] border border-cyan-500/30 backdrop-blur-sm"
      >
        {submitButtonText}
      </button>
    </form>
  );
};

export default TaskForm;