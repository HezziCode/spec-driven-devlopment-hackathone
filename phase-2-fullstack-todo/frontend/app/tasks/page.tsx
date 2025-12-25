'use client';

// Main Tasks Dashboard page
// Shows user tasks with filtering, creation, and management capabilities

import React, { useState, useEffect, useCallback } from 'react';
import { ListTodo, LogOut, ArrowRight, Bell, Command, Flame, Target } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import TaskCard from '@/components/TaskCard';
import TaskForm from '@/components/TaskForm';
import TaskFilters from '@/components/TaskFilters';
import NeuralBackground from '@/components/NeuralBackground';
import PageRouteTransitionProvider from '@/components/providers/PageRouteTransitionProvider';

// Define the Task interface
interface Task {
  id: string;
  title: string;
  description: string;
  completed: boolean;
  priority: 'low' | 'medium' | 'high' | 'critical';
  tags: string[];
  user_id: string;
  created_at: string;
  updated_at: string;
}

// Define the Notification interface
interface Notification {
  id: string;
  type: 'system' | 'task' | 'reminder';
  title: string;
  message: string;
  read: boolean;
  timestamp: string;
  user_id: string;
}


// --- Custom Styles for Theme & Typography ---
const GlobalStyles = () => (
  <style>{`
    body {
      transition: background-color 0.3s ease-in-out;
      background-color: #0f172a; /* Dark background */
    }

    /* Gradient Text for Landing Page Headline */
    .gradient-text-teal {
      background-clip: text;
      -webkit-background-clip: text;
      color: transparent;
      background-image: linear-gradient(to right, #2dd4bf, #06b6d4, #0e7490); /* Teal-Cyan blend */
      transition: all 0.3s ease-in-out;
    }
  `}</style>
);

// --- Global Cursor Follow Glow Component ---
// This component displays the subtle glow animation that follows the mouse position globally.
const CursorGlow = ({ mousePosition }: { mousePosition: { x: number; y: number } }) => (
    <div
        className="fixed inset-0 z-0 pointer-events-none transition-opacity duration-300"
        style={{
            // Dynamic background with radial gradient following the mouse position relative to the viewport
            background: `radial-gradient(450px at ${mousePosition.x}px ${mousePosition.y}px, rgba(6, 182, 212, 0.1), transparent 80%)`,
            transition: 'background 0.05s ease-out',
        }}
    />
);

// Mock initial tasks data
const initialTasks: Task[] = [
  {
    id: '1',
    title: 'Complete project proposal',
    description: 'Finish the project proposal document and send for review',
    completed: false,
    priority: 'high',
    tags: ['work', 'important'],
    user_id: 'demo-user',
    created_at: '2025-12-17T10:00:00Z',
    updated_at: '2025-12-17T10:00:00Z'
  },
  {
    id: '2',
    title: 'Schedule team meeting',
    description: 'Schedule a team meeting for next week to discuss progress',
    completed: true,
    priority: 'medium',
    tags: ['meeting', 'team'],
    user_id: 'demo-user',
    created_at: '2025-12-17T09:00:00Z',
    updated_at: '2025-12-17T09:30:00Z'
  },
  {
    id: '3',
    title: 'Research new technologies',
    description: 'Look into new technologies that could improve our workflow',
    completed: false,
    priority: 'low',
    tags: ['research', 'learning'],
    user_id: 'demo-user',
    created_at: '2025-12-17T08:00:00Z',
    updated_at: '2025-12-17T08:00:00Z'
  }
];

// Mock notifications data
const initialNotifications: Notification[] = [
  {
    id: '1',
    type: 'system',
    title: 'System Update',
    message: 'New features have been added to the dashboard',
    read: false,
    timestamp: '2025-12-17T08:00:00Z',
    user_id: 'demo-user'
  },
  {
    id: '2',
    type: 'task',
    title: 'Task Reminder',
    message: 'You have 3 pending tasks for today',
    read: false,
    timestamp: '2025-12-17T09:00:00Z',
    user_id: 'demo-user'
  }
];


const TasksPage = () => {
  // State for tasks and filters
  const [tasks, setTasks] = useState<Task[]>(initialTasks);
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'completed'>('all');
  const [priorityFilter, setPriorityFilter] = useState<'all' | 'low' | 'medium' | 'high' | 'critical'>('all');
  const [notifications, setNotifications] = useState<Notification[]>(initialNotifications);

  // Always in dark mode now
  const isDarkMode = true;

  // Global Mouse Position State and Handler
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  const handleMouseMove = useCallback((e: MouseEvent) => {
    // Track mouse position relative to the viewport for global glow
    setMousePosition({
      x: e.clientX,
      y: e.clientY,
    });
  }, []);


  // Set up global mouse tracking
  useEffect(() => {
    window.addEventListener('mousemove', handleMouseMove);
    return () => {
        window.removeEventListener('mousemove', handleMouseMove);
    };
  }, [handleMouseMove]);

  // User data (mock for now)
  const mockUser = {
    id: 'demo-user',
    username: 'Demo User',
    email: 'demo@example.com'
  };

  // Add a new task
  const addTask = (title: string, description: string, priority: 'low' | 'medium' | 'high' | 'critical', tags: string[]) => {
    const newTask: Task = {
      id: Date.now().toString(),
      title,
      description,
      completed: false,
      priority,
      tags,
      user_id: mockUser.id,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    setTasks([newTask, ...tasks]);
  };

  // Toggle task completion - Remove completed tasks from UI immediately
  const toggleTaskCompletion = (id: string, completed: boolean) => {
    if (completed) {
      // If marking as completed, remove the task from the UI
      setTasks(tasks.filter(task => task.id !== id));
    } else {
      // If marking as not completed, update the task status
      setTasks(tasks.map(task =>
        task.id === id ? { ...task, completed } : task
      ));
    }
  };

  // Delete a task
  const deleteTask = (id: string) => {
    setTasks(tasks.filter(task => task.id !== id));
  };

  // Filter tasks based on current filters
  const filteredTasks = tasks.filter(task => {
    const statusMatch = statusFilter === 'all' ||
                      (statusFilter === 'active' && !task.completed) ||
                      (statusFilter === 'completed' && task.completed);

    const priorityMatch = priorityFilter === 'all' || task.priority === priorityFilter;

    return statusMatch && priorityMatch;
  });

  return (
    <PageRouteTransitionProvider>
      <div className="min-h-screen w-full bg-slate-900/40 transition-colors duration-300 relative overflow-x-hidden">
        <GlobalStyles />

        {/* Neural Background - positioned just behind content but above base background */}
        <NeuralBackground />

        {/* Global Cursor Glow rendered as a fixed element */}
        <CursorGlow mousePosition={mousePosition} />

        <div className="relative z-10 w-full max-w-full">
          <Navbar
            userId={mockUser.id}
            handleAuthAction={() => {}}
            setView={() => {}}
            notifications={notifications}
            onMarkAllRead={() => setNotifications(notifications.map(n => ({ ...n, read: true })))}
            onNotificationClick={(id) => {
              setNotifications(notifications.map(n =>
                n.id === id ? { ...n, read: true } : n
              ));
            }}
          />

          <main className="w-full px-4 py-8">
            <div className="max-w-6xl mx-auto w-full">
              {/* Premium Animated Hero Section */}
              <motion.section
                initial={{ scale: 0.95, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className="relative w-full flex flex-col items-center justify-center text-center overflow-visible"
              >
                {/* Premium background elements */}
                <div className="absolute top-0 left-0 w-64 h-64 bg-gradient-to-br from-teal-500/5 to-cyan-500/10 rounded-full blur-[120px] -mt-24 -ml-24" />
                <div className="absolute bottom-0 right-0 w-64 h-64 bg-gradient-to-br from-cyan-500/5 to-blue-500/10 rounded-full blur-[120px] -mb-24 -mr-24" />
                <div
                  className="absolute inset-0 opacity-[0.02]"
                  style={{
                    backgroundImage: 'radial-gradient(circle at 25% 25%, #2dd4bf 0.8px, transparent 0.8px), radial-gradient(circle at 75% 75%, #06b6d4 0.8px, transparent 0.8px)',
                    backgroundSize: '30px 30px'
                  }}
                />

                {/* Inner content container */}
                <div className="relative z-10 space-y-6 max-w-4xl w-full">
                  {/* Status tag */}
                  <motion.div
                    initial={{ y: 20, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ delay: 0.1 }}
                    className="inline-flex items-center space-x-2.5 px-4 py-2 rounded-full bg-gradient-to-r from-cyan-500/15 to-teal-500/15 border border-cyan-500/30 backdrop-blur-sm shadow-lg shadow-cyan-500/10"
                  >
                    <Command size={14} className="text-cyan-400" />
                    <span className="text-sm font-semibold text-slate-200">Mission Control Active</span>
                  </motion.div>

                  {/* Premium animated heading */}
                  <motion.h1
                    initial={{ y: 20, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ delay: 0.2 }}
                    className="text-3xl sm:text-4xl md:text-6xl lg:text-7xl font-black tracking-tight leading-tight text-white max-w-3xl mx-auto relative break-words"
                  >
                    <span className="relative inline-block">
                      Conquer Your Tasks<br />
                      Master Your Flow Today
                      {/* Curved SVG underline */}
                      <svg
                        className="absolute left-0 -bottom-3 w-full h-3 pointer-events-none sm:-bottom-4 sm:h-4"
                        viewBox="0 0 100 10"
                        preserveAspectRatio="none"
                      >
                        <path
                          d="M2,5 Q50,10 98,5"
                          stroke="url(#taskflow-grad)"
                          strokeWidth="2"
                          fill="none"
                          strokeLinecap="round"
                          opacity="0.8"
                        />
                        <defs>
                          <linearGradient id="taskflow-grad" x1="0%" y1="0%" x2="100%" y2="0%">
                            <stop offset="0%" stopColor="#5eead4" />
                            <stop offset="100%" stopColor="#67e8f9" />
                          </linearGradient>
                        </defs>
                      </svg>
                    </span>
                  </motion.h1>

                  {/* Premium animated paragraph */}
                  <motion.p
                    initial={{ y: 20, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ delay: 0.3 }}
                    className="text-base md:text-lg text-slate-300/90 font-medium max-w-2xl mx-auto leading-relaxed mb-6 sm:mb-8"
                  >
                    Your streamlined task dashboard. Focus on what matters with our premium productivity suite.
                  </motion.p>

                </div>

                {/* Add the premium shine animation styles */}
                <style jsx global>{`
                  @keyframes premium-shine {
                    0%, 100% { background-position: 0% 50%; }
                    50% { background-position: 100% 50%; }
                  }
                `}</style>
              </motion.section>

              {/* Task Creation Form - Positioned as Primary Element */}
              <div className="mb-8 bg-slate-800/20 backdrop-blur-sm rounded-xl p-6 border border-slate-700/20">
                <h2 className="text-2xl font-bold text-white mb-4">Create New Task</h2>
                <TaskForm onSubmit={addTask} />
              </div>

              {/* Premium Stats Section */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-6 mb-8">
                <div className="bg-slate-800/20 backdrop-blur-sm rounded-lg sm:rounded-xl p-4 sm:p-6 text-center border border-slate-700/20">
                  <h3 className="text-xl sm:text-2xl font-bold text-cyan-400">{tasks.length}</h3>
                  <p className="text-xs sm:text-sm text-slate-400">Total Tasks</p>
                </div>
                <div className="bg-slate-800/20 backdrop-blur-sm rounded-lg sm:rounded-xl p-4 sm:p-6 text-center border border-slate-700/20">
                  <h3 className="text-xl sm:text-2xl font-bold text-emerald-400">
                    {tasks.filter(t => t.completed).length}
                  </h3>
                  <p className="text-xs sm:text-sm text-slate-400">Completed</p>
                </div>
                <div className="bg-slate-800/20 backdrop-blur-sm rounded-lg sm:rounded-xl p-4 sm:p-6 text-center border border-slate-700/20">
                  <h3 className="text-xl sm:text-2xl font-bold text-amber-400">
                    {tasks.filter(t => !t.completed).length}
                  </h3>
                  <p className="text-xs sm:text-sm text-slate-400">Pending</p>
                </div>
                <div className="bg-slate-800/20 backdrop-blur-sm rounded-lg sm:rounded-xl p-4 sm:p-6 text-center border border-slate-700/20">
                  <h3 className="text-xl sm:text-2xl font-bold text-rose-400">
                    {tasks.filter(t => t.priority === 'high' && !t.completed).length}
                  </h3>
                  <p className="text-xs sm:text-sm text-slate-400">High Priority</p>
                </div>
              </div>

              {/* Task Filters */}
              <div className="mb-8 bg-slate-800/20 backdrop-blur-sm rounded-xl p-4 border border-slate-700/20">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Status</label>
                    <select
                      value={statusFilter}
                      onChange={(e) => setStatusFilter(e.target.value as 'all' | 'active' | 'completed')}
                      className="w-full bg-slate-700/40 backdrop-blur-sm border border-slate-600/50 rounded-lg px-4 py-2.5 text-sm text-slate-300 focus:ring-2 focus:ring-cyan-500 outline-none appearance-none cursor-pointer"
                    >
                      <option value="all">All Tasks</option>
                      <option value="active">Active</option>
                      <option value="completed">Completed</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Priority</label>
                    <select
                      value={priorityFilter}
                      onChange={(e) => setPriorityFilter(e.target.value as 'all' | 'low' | 'medium' | 'high' | 'critical')}
                      className="w-full bg-slate-700/40 backdrop-blur-sm border border-slate-600/50 rounded-lg px-4 py-2.5 text-sm text-slate-300 focus:ring-2 focus:ring-cyan-500 outline-none appearance-none cursor-pointer"
                    >
                      <option value="all">All Priorities</option>
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                      <option value="critical">Critical</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Task List */}
              <div className="mb-12 bg-slate-800/20 backdrop-blur-sm rounded-lg sm:rounded-xl p-4 sm:p-6 border border-slate-700/20">
                <h2 className="text-xl sm:text-2xl font-bold text-white mb-4 sm:mb-6">
                  {statusFilter === 'all' ? 'All Tasks' : statusFilter === 'active' ? 'Active Tasks' : 'Completed Tasks'}
                </h2>

                {filteredTasks.length === 0 ? (
                  <div className="text-center py-8 sm:py-12">
                    <div className="text-4xl sm:text-5xl mb-3 sm:mb-4">📝</div>
                    <h3 className="text-lg sm:text-xl font-semibold text-white mb-2">No tasks found</h3>
                    <p className="text-sm sm:text-gray-400">
                      {statusFilter === 'completed'
                        ? "You haven't completed any tasks yet."
                        : "You're all caught up! Add a new task to get started."}
                    </p>
                  </div>
                ) : (
                  <AnimatePresence>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
                      {filteredTasks.map(task => (
                        <motion.div
                          layout
                          initial={{ opacity: 0, scale: 0.8 }}
                          animate={{ opacity: 1, scale: 1 }}
                          exit={{ opacity: 0, scale: 0.8, height: 0 }}
                          transition={{ duration: 0.3 }}
                          key={task.id}
                        >
                          <TaskCard
                            id={task.id}
                            title={task.title}
                            description={task.description}
                            completed={task.completed}
                            priority={task.priority}
                            tags={task.tags}
                            createdAt={task.created_at}
                            updatedAt={task.updated_at}
                            userId={task.user_id}
                            onToggleComplete={toggleTaskCompletion}
                            onDelete={deleteTask}
                          />
                        </motion.div>
                      ))}
                    </div>
                  </AnimatePresence>
                )}
              </div>

            </div>
          </main>

          <Footer setView={() => {}} />
        </div>
      </div>
    </PageRouteTransitionProvider>
  );
};

export default TasksPage;