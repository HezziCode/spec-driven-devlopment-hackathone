'use client';

// Main Tasks Dashboard page
// Shows user tasks with filtering, creation, and management capabilities
// Integrated with Backend API for real data persistence

import React, { useState, useEffect, useCallback, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { ListTodo, LogOut, ArrowRight, Bell, Command, Flame, Target } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import TaskCard from '@/components/TaskCard';
import TaskForm from '@/components/TaskForm';
import TaskFilters from '@/components/TaskFilters';
import NeuralBackground from '@/components/NeuralBackground';
import PageRouteTransitionProvider from '@/components/providers/PageRouteTransitionProvider';
import ProtectedRoute from '@/components/ProtectedRoute';
import WaveSpinner from '@/components/WaveSpinner';
import { useToast } from '@/components/Toast';
import { useAuth } from '@/lib/auth';
import { taskApi } from '@/lib/api';
import type { TaskResponse, PriorityEnum, SortEnum, TaskQueryParams } from '@/types/api';

// Define the Task interface (matching API response)
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

// Define the Notification interface (matching Navbar component)
interface Notification {
  id: string;
  taskId: string;
  title: string;
  type: 'task-created' | 'task-completed' | 'task-deleted' | 'reminder';
  read: boolean;
  timestamp: string;
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

// Mock notifications data
const initialNotifications: Notification[] = [
  {
    id: '1',
    taskId: 'task-1',
    type: 'task-created',
    title: 'New task created',
    read: false,
    timestamp: '2025-12-17T08:00:00Z'
  },
  {
    id: '2',
    taskId: 'task-2',
    type: 'reminder',
    title: 'Task reminder',
    read: false,
    timestamp: '2025-12-17T09:00:00Z'
  }
];


const TasksPageContent = () => {
  // Authentication
  const { session, status } = useAuth();

  // Router and search params for URL state management
  const router = useRouter();
  const searchParams = useSearchParams();

  // Toast notifications
  const toast = useToast();

  // Initialize filters from URL query parameters
  const initialStatus = (searchParams.get('status') || 'all') as 'all' | 'active' | 'completed';
  const initialPriority = (searchParams.get('priority') || 'all') as 'all' | 'low' | 'medium' | 'high' | 'critical';
  const initialSearch = searchParams.get('search') || '';
  const initialTag = searchParams.get('tag') || '';
  const initialSort = (searchParams.get('sort') || 'created') as SortEnum;
  const initialPage = parseInt(searchParams.get('page') || '1', 10);

  // State for tasks and filters
  const [tasks, setTasks] = useState<Task[]>([]);
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'completed'>(initialStatus);
  const [priorityFilter, setPriorityFilter] = useState<'all' | 'low' | 'medium' | 'high' | 'critical'>(initialPriority);
  const [searchQuery, setSearchQuery] = useState<string>(initialSearch);
  const [tagFilter, setTagFilter] = useState<string>(initialTag);
  const [sortOrder, setSortOrder] = useState<SortEnum>(initialSort);
  const [currentPage, setCurrentPage] = useState<number>(initialPage);
  const [totalTasks, setTotalTasks] = useState<number>(0);
  const [itemsPerPage] = useState<number>(20);
  const [notifications, setNotifications] = useState<Notification[]>(initialNotifications);
  const [isLoadingTasks, setIsLoadingTasks] = useState(false);
  const [currentDate, setCurrentDate] = useState<Date>(new Date());

  // Always in dark mode now
  const isDarkMode = true;

  // Helper function to check if a task was completed today
  const isCompletedToday = (task: Task): boolean => {
    if (!task.completed) return false;

    const taskDate = new Date(task.updated_at);
    const today = currentDate;

    return (
      taskDate.getDate() === today.getDate() &&
      taskDate.getMonth() === today.getMonth() &&
      taskDate.getFullYear() === today.getFullYear()
    );
  };

  // Calculate today's completed tasks
  const todayCompletedCount = tasks.filter(isCompletedToday).length;

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

  // Set up midnight reset timer for completion counter
  useEffect(() => {
    // Calculate milliseconds until next midnight
    const now = new Date();
    const tomorrow = new Date(now);
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(0, 0, 0, 0);
    const msUntilMidnight = tomorrow.getTime() - now.getTime();

    // Set timer to update current date at midnight
    const midnightTimer = setTimeout(() => {
      setCurrentDate(new Date());

      // Set up recurring daily timer after first midnight
      const dailyInterval = setInterval(() => {
        setCurrentDate(new Date());
      }, 24 * 60 * 60 * 1000); // 24 hours in milliseconds

      return () => clearInterval(dailyInterval);
    }, msUntilMidnight);

    return () => clearTimeout(midnightTimer);
  }, []);

  // Update URL query parameters when filters change
  const updateUrlParams = useCallback((params: Record<string, string | number>) => {
    const newSearchParams = new URLSearchParams();

    Object.entries(params).forEach(([key, value]) => {
      if (value && value !== 'all' && value !== '') {
        newSearchParams.set(key, String(value));
      }
    });

    const queryString = newSearchParams.toString();
    router.push(queryString ? `?${queryString}` : '/tasks', { scroll: false });
  }, [router]);

  // Fetch tasks from API with current filters
  const fetchTasks = useCallback(async () => {
    if (!session?.user?.id) return;

    setIsLoadingTasks(true);
    try {
      // Build query parameters
      const params: TaskQueryParams = {
        limit: itemsPerPage,
        offset: (currentPage - 1) * itemsPerPage,
        sort: sortOrder,
      };

      // Add optional filters
      if (statusFilter === 'active') {
        params.completed = false;
      } else if (statusFilter === 'completed') {
        params.completed = true;
      }

      if (priorityFilter !== 'all') {
        params.priority = priorityFilter as PriorityEnum;
      }

      if (searchQuery.trim()) {
        params.search = searchQuery.trim();
      }

      if (tagFilter.trim()) {
        params.tag = tagFilter.trim();
      }

      const response = await taskApi.getTasks(session.user.id, params);

      // Convert API response to local Task format
      const fetchedTasks: Task[] = response.tasks.map((task: TaskResponse) => ({
        id: task.id,
        title: task.title,
        description: task.description,
        completed: task.completed,
        priority: task.priority,
        tags: task.tags,
        user_id: task.user_id,
        created_at: task.created_at,
        updated_at: task.updated_at,
      }));

      setTasks(fetchedTasks);
      setTotalTasks(response.total);

      // Update URL with current filter state
      updateUrlParams({
        status: statusFilter,
        priority: priorityFilter,
        search: searchQuery,
        tag: tagFilter,
        sort: sortOrder,
        page: currentPage,
      });
    } catch (error) {
      console.error('Error fetching tasks:', error);
      toast.error('Failed to load tasks. Please try again.');
    } finally {
      setIsLoadingTasks(false);
    }
  }, [
    session?.user?.id,
    toast,
    statusFilter,
    priorityFilter,
    searchQuery,
    tagFilter,
    sortOrder,
    currentPage,
    itemsPerPage,
    updateUrlParams,
  ]);

  // Fetch tasks when filters change or on mount
  useEffect(() => {
    if (status === 'authenticated' && session?.user?.id) {
      fetchTasks();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [
    status,
    session?.user?.id,
    statusFilter,
    priorityFilter,
    searchQuery,
    tagFilter,
    sortOrder,
    currentPage,
    // Note: fetchTasks is NOT included to prevent infinite loop
    // All of fetchTasks' dependencies are already tracked above
  ]);

  // Add a new task
  const addTask = async (title: string, description: string, priority: 'low' | 'medium' | 'high' | 'critical', tags: string[]) => {
    if (!session?.user?.id) {
      toast.error('You must be logged in to create tasks.');
      return;
    }

    try {
      const newTask = await taskApi.createTask(session.user.id, {
        title,
        description,
        priority: priority as PriorityEnum,
        tags,
      });

      // Convert API response to local Task format
      const createdTask: Task = {
        id: newTask.id,
        title: newTask.title,
        description: newTask.description,
        completed: newTask.completed,
        priority: newTask.priority,
        tags: newTask.tags,
        user_id: newTask.user_id,
        created_at: newTask.created_at,
        updated_at: newTask.updated_at,
      };

      setTasks([createdTask, ...tasks]);
      toast.success('Task created successfully!');
    } catch (error: any) {
      console.error('Error creating task:', error);
      toast.error(error.message || 'Failed to create task. Please try again.');
    }
  };

  // Toggle task completion - Remove completed tasks from UI immediately
  const toggleTaskCompletion = async (id: string, completed: boolean) => {
    if (!session?.user?.id) {
      toast.error('You must be logged in to update tasks.');
      return;
    }

    try {
      // Update task on backend
      await taskApi.patchTask(session.user.id, id, { completed });

      // Update the task status and updated_at timestamp in local state
      setTasks(tasks.map(task =>
        task.id === id ? { ...task, completed, updated_at: new Date().toISOString() } : task
      ));

      if (completed) {
        toast.success('Task completed!');
      } else {
        toast.info('Task marked as active.');
      }
    } catch (error: any) {
      console.error('Error updating task:', error);
      toast.error(error.message || 'Failed to update task. Please try again.');
    }
  };

  // Delete a task
  const deleteTask = async (id: string) => {
    if (!session?.user?.id) {
      toast.error('You must be logged in to delete tasks.');
      return;
    }

    try {
      await taskApi.deleteTask(session.user.id, id);
      setTasks(tasks.filter(task => task.id !== id));
      toast.success('Task deleted successfully!');
    } catch (error: any) {
      console.error('Error deleting task:', error);
      toast.error(error.message || 'Failed to delete task. Please try again.');
    }
  };

  // Pagination calculations
  const totalPages = Math.ceil(totalTasks / itemsPerPage);
  const hasNextPage = currentPage < totalPages;
  const hasPrevPage = currentPage > 1;

  // Handle page navigation
  const goToNextPage = () => {
    if (hasNextPage) {
      setCurrentPage(currentPage + 1);
    }
  };

  const goToPrevPage = () => {
    if (hasPrevPage) {
      setCurrentPage(currentPage - 1);
    }
  };

  const goToPage = (page: number) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
    }
  };

  // Handle filter changes - reset to page 1 when filters change
  const handleStatusFilterChange = (newStatus: 'all' | 'active' | 'completed') => {
    setStatusFilter(newStatus);
    setCurrentPage(1);
  };

  const handlePriorityFilterChange = (newPriority: 'all' | 'low' | 'medium' | 'high' | 'critical') => {
    setPriorityFilter(newPriority);
    setCurrentPage(1);
  };

  const handleSearchChange = (newSearch: string) => {
    setSearchQuery(newSearch);
    setCurrentPage(1);
  };

  const handleTagFilterChange = (newTag: string) => {
    setTagFilter(newTag);
    setCurrentPage(1);
  };

  const handleSortChange = (newSort: SortEnum) => {
    setSortOrder(newSort);
    setCurrentPage(1);
  };

  return (
    <ProtectedRoute>
      <PageRouteTransitionProvider>
        <div className="min-h-screen w-full bg-slate-900/40 transition-colors duration-300 relative overflow-x-hidden">
          <GlobalStyles />

          {/* Toast Container */}
          <toast.ToastContainer />

          {/* Neural Background - positioned just behind content but above base background */}
          <NeuralBackground />

          {/* Global Cursor Glow rendered as a fixed element */}
          <CursorGlow mousePosition={mousePosition} />

          <div className="relative z-10 w-full max-w-full">
            <Navbar
              userId={session?.user?.id || 'guest'}
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
                    {todayCompletedCount}
                  </h3>
                  <p className="text-xs sm:text-sm text-slate-400">Today Complete</p>
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

              {/* Task Filters - Enhanced with search, tag, and sort */}
              <TaskFilters
                statusFilter={statusFilter}
                priorityFilter={priorityFilter}
                searchQuery={searchQuery}
                tagFilter={tagFilter}
                sortOrder={sortOrder}
                onStatusChange={handleStatusFilterChange}
                onPriorityChange={handlePriorityFilterChange}
                onSearchChange={handleSearchChange}
                onTagChange={handleTagFilterChange}
                onSortChange={handleSortChange}
              />

              {/* Task List */}
              <div className="mb-8 bg-slate-800/20 backdrop-blur-sm rounded-lg sm:rounded-xl p-4 sm:p-6 border border-slate-700/20">
                <div className="flex items-center justify-between mb-4 sm:mb-6">
                  <h2 className="text-xl sm:text-2xl font-bold text-white">
                    {statusFilter === 'all' ? 'All Tasks' : statusFilter === 'active' ? 'Active Tasks' : 'Completed Tasks'}
                  </h2>
                  <span className="text-sm text-slate-400">
                    {totalTasks} {totalTasks === 1 ? 'task' : 'tasks'} found
                  </span>
                </div>

                {isLoadingTasks ? (
                  <div className="flex justify-center items-center py-12">
                    <WaveSpinner />
                  </div>
                ) : tasks.length === 0 ? (
                  <div className="text-center py-8 sm:py-12">
                    <div className="text-4xl sm:text-5xl mb-3 sm:mb-4">📝</div>
                    <h3 className="text-lg sm:text-xl font-semibold text-white mb-2">No tasks found</h3>
                    <p className="text-sm sm:text-gray-400">
                      {searchQuery || tagFilter
                        ? 'Try adjusting your search or filters.'
                        : statusFilter === 'completed'
                        ? "You haven't completed any tasks yet."
                        : "You're all caught up! Add a new task to get started."}
                    </p>
                  </div>
                ) : (
                  <AnimatePresence>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
                      {tasks.map(task => (
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

              {/* Pagination Controls */}
              {totalPages > 1 && (
                <div className="mb-12 bg-slate-800/20 backdrop-blur-sm rounded-lg sm:rounded-xl p-4 border border-slate-700/20">
                  <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
                    {/* Page Info */}
                    <div className="text-sm text-slate-400">
                      Page {currentPage} of {totalPages}
                    </div>

                    {/* Navigation Buttons */}
                    <div className="flex items-center gap-2">
                      {/* Previous Button */}
                      <button
                        onClick={goToPrevPage}
                        disabled={!hasPrevPage}
                        className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                          hasPrevPage
                            ? 'bg-cyan-600 text-white hover:bg-cyan-700 shadow-lg shadow-cyan-500/30'
                            : 'bg-slate-700/50 text-slate-500 cursor-not-allowed'
                        }`}
                      >
                        Previous
                      </button>

                      {/* Page Numbers */}
                      <div className="flex items-center gap-1">
                        {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                          let pageNum: number;
                          if (totalPages <= 5) {
                            pageNum = i + 1;
                          } else if (currentPage <= 3) {
                            pageNum = i + 1;
                          } else if (currentPage >= totalPages - 2) {
                            pageNum = totalPages - 4 + i;
                          } else {
                            pageNum = currentPage - 2 + i;
                          }

                          return (
                            <button
                              key={pageNum}
                              onClick={() => goToPage(pageNum)}
                              className={`w-10 h-10 rounded-lg font-medium transition-all duration-200 ${
                                currentPage === pageNum
                                  ? 'bg-cyan-600 text-white shadow-lg shadow-cyan-500/30'
                                  : 'bg-slate-700/50 text-slate-300 hover:bg-slate-600'
                              }`}
                            >
                              {pageNum}
                            </button>
                          );
                        })}
                      </div>

                      {/* Next Button */}
                      <button
                        onClick={goToNextPage}
                        disabled={!hasNextPage}
                        className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                          hasNextPage
                            ? 'bg-cyan-600 text-white hover:bg-cyan-700 shadow-lg shadow-cyan-500/30'
                            : 'bg-slate-700/50 text-slate-500 cursor-not-allowed'
                        }`}
                      >
                        Next
                      </button>
                    </div>

                    {/* Items Per Page Info */}
                    <div className="text-sm text-slate-400">
                      {itemsPerPage} per page
                    </div>
                  </div>
                </div>
              )}

            </div>
          </main>

          <Footer />
        </div>
      </div>
    </PageRouteTransitionProvider>
    </ProtectedRoute>
  );
};

const TasksPage = () => {
  return (
    <Suspense fallback={
      <ProtectedRoute>
        <div className="min-h-screen flex items-center justify-center bg-slate-900">
          <WaveSpinner />
        </div>
      </ProtectedRoute>
    }>
      <TasksPageContent />
    </Suspense>
  );
};

export default TasksPage;