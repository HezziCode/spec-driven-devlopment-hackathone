'use client';

// User Profile Management Page
// Displays and allows editing of user profile information
// Integrated with Backend API for user data persistence

import React, { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { User, Mail, Calendar, ArrowLeft, Save, X, Edit3 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import NeuralBackground from '@/components/NeuralBackground';
import PageRouteTransitionProvider from '@/components/providers/PageRouteTransitionProvider';
import ProtectedRoute from '@/components/ProtectedRoute';
import WaveSpinner from '@/components/WaveSpinner';
import { useToast } from '@/components/Toast';
import { useAuth } from '@/lib/auth';
import { userApi } from '@/lib/api';
import type { UserResponse } from '@/types/api';

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
  `}</style>
);

// --- Global Cursor Follow Glow Component ---
const CursorGlow = ({ mousePosition }: { mousePosition: { x: number; y: number } }) => (
  <div
    className="fixed inset-0 z-0 pointer-events-none transition-opacity duration-300"
    style={{
      background: `radial-gradient(450px at ${mousePosition.x}px ${mousePosition.y}px, rgba(6, 182, 212, 0.1), transparent 80%)`,
      transition: 'background 0.05s ease-out',
    }}
  />
);

// Mock notifications data
const initialNotifications: Notification[] = [];

const ProfilePage = () => {
  // Authentication
  const { session, status } = useAuth();
  const router = useRouter();
  const toast = useToast();

  // Profile state
  const [profile, setProfile] = useState<UserResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  // Form state
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [usernameError, setUsernameError] = useState('');
  const [emailError, setEmailError] = useState('');

  // UI state
  const [notifications] = useState<Notification[]>(initialNotifications);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  // Global Mouse Position Handler
  const handleMouseMove = useCallback((e: MouseEvent) => {
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

  // Fetch user profile on mount
  useEffect(() => {
    const fetchProfile = async () => {
      if (!session?.user?.id) {
        setIsLoading(false);
        return;
      }

      try {
        const profileData = await userApi.getProfile(session.user.id);
        setProfile(profileData);
        setUsername(profileData.username);
        setEmail(profileData.email);
      } catch (error: any) {
        console.error('Error fetching profile:', error);
        toast.error(error.message || 'Failed to load profile. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    if (status === 'authenticated') {
      fetchProfile();
    }
  }, [session?.user?.id, status, toast]);

  // Validate username
  const validateUsername = (value: string): string => {
    if (!value || value.trim().length === 0) {
      return 'Username is required';
    }
    if (value.length < 3) {
      return 'Username must be at least 3 characters';
    }
    if (value.length > 50) {
      return 'Username must be less than 50 characters';
    }
    return '';
  };

  // Validate email
  const validateEmail = (value: string): string => {
    if (!value || value.trim().length === 0) {
      return 'Email is required';
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) {
      return 'Invalid email format';
    }
    return '';
  };

  // Handle username input change
  const handleUsernameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setUsername(value);
    setUsernameError(validateUsername(value));
  };

  // Handle email input change
  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setEmail(value);
    setEmailError(validateEmail(value));
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!session?.user?.id) {
      toast.error('You must be logged in to update your profile.');
      return;
    }

    // Validate inputs
    const usernameErr = validateUsername(username);
    const emailErr = validateEmail(email);

    setUsernameError(usernameErr);
    setEmailError(emailErr);

    if (usernameErr || emailErr) {
      toast.error('Please fix validation errors before submitting.');
      return;
    }

    // Check if anything changed
    if (profile && username === profile.username && email === profile.email) {
      toast.info('No changes to save.');
      setIsEditing(false);
      return;
    }

    setIsSaving(true);

    try {
      const updatedProfile = await userApi.updateProfile(session.user.id, {
        username: username !== profile?.username ? username : undefined,
        email: email !== profile?.email ? email : undefined,
      });

      setProfile(updatedProfile);
      setUsername(updatedProfile.username);
      setEmail(updatedProfile.email);
      setIsEditing(false);
      toast.success('Profile updated successfully!');
    } catch (error: any) {
      console.error('Error updating profile:', error);

      // Handle 409 Conflict errors (duplicate username or email)
      if (error.status === 409) {
        const errorMessage = error.message || '';
        if (errorMessage.toLowerCase().includes('username')) {
          setUsernameError('This username is already taken');
          toast.error('Username is already taken. Please choose another.');
        } else if (errorMessage.toLowerCase().includes('email')) {
          setEmailError('This email is already in use');
          toast.error('Email is already in use. Please use another.');
        } else {
          toast.error('Username or email is already taken.');
        }
      } else {
        toast.error(error.message || 'Failed to update profile. Please try again.');
      }
    } finally {
      setIsSaving(false);
    }
  };

  // Handle cancel editing
  const handleCancel = () => {
    if (profile) {
      setUsername(profile.username);
      setEmail(profile.email);
      setUsernameError('');
      setEmailError('');
    }
    setIsEditing(false);
  };

  // Format date for display
  const formatDate = (dateString: string): string => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      });
    } catch {
      return dateString;
    }
  };

  return (
    <ProtectedRoute>
      <PageRouteTransitionProvider>
        <div className="min-h-screen w-full bg-slate-900/40 transition-colors duration-300 relative overflow-x-hidden">
          <GlobalStyles />

          {/* Toast Container */}
          <toast.ToastContainer />

          {/* Neural Background */}
          <NeuralBackground />

          {/* Global Cursor Glow */}
          <CursorGlow mousePosition={mousePosition} />

          <div className="relative z-10 w-full max-w-full">
            <Navbar
              userId={session?.user?.id || 'guest'}
              handleAuthAction={() => {}}
              setView={() => {}}
              notifications={notifications}
              onMarkAllRead={() => {}}
              onNotificationClick={() => {}}
            />

            <main className="w-full px-4 py-8">
              <div className="max-w-4xl mx-auto w-full">
                {/* Back to Tasks Button */}
                <motion.div
                  initial={{ x: -20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  className="mb-6"
                >
                  <button
                    onClick={() => router.push('/tasks')}
                    className="flex items-center space-x-2 text-cyan-400 hover:text-cyan-300 transition-colors duration-200"
                  >
                    <ArrowLeft size={20} />
                    <span className="font-medium">Back to Tasks</span>
                  </button>
                </motion.div>

                {/* Premium Animated Hero Section */}
                <motion.section
                  initial={{ scale: 0.95, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  className="relative w-full flex flex-col items-center justify-center text-center overflow-visible mb-8"
                >
                  {/* Premium background elements */}
                  <div className="absolute top-0 left-0 w-64 h-64 bg-gradient-to-br from-teal-500/5 to-cyan-500/10 rounded-full blur-[120px] -mt-24 -ml-24" />
                  <div className="absolute bottom-0 right-0 w-64 h-64 bg-gradient-to-br from-cyan-500/5 to-blue-500/10 rounded-full blur-[120px] -mb-24 -mr-24" />

                  <div className="relative z-10 space-y-4 max-w-4xl w-full">
                    <motion.h1
                      initial={{ y: 20, opacity: 0 }}
                      animate={{ y: 0, opacity: 1 }}
                      transition={{ delay: 0.1 }}
                      className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-black tracking-tight leading-tight text-white"
                    >
                      <span className="relative inline-block">
                        Your Profile
                        <svg
                          className="absolute left-0 -bottom-2 w-full h-3 pointer-events-none sm:-bottom-3 sm:h-4"
                          viewBox="0 0 100 10"
                          preserveAspectRatio="none"
                        >
                          <path
                            d="M2,5 Q50,10 98,5"
                            stroke="url(#profile-grad)"
                            strokeWidth="2"
                            fill="none"
                            strokeLinecap="round"
                            opacity="0.8"
                          />
                          <defs>
                            <linearGradient id="profile-grad" x1="0%" y1="0%" x2="100%" y2="0%">
                              <stop offset="0%" stopColor="#5eead4" />
                              <stop offset="100%" stopColor="#67e8f9" />
                            </linearGradient>
                          </defs>
                        </svg>
                      </span>
                    </motion.h1>

                    <motion.p
                      initial={{ y: 20, opacity: 0 }}
                      animate={{ y: 0, opacity: 1 }}
                      transition={{ delay: 0.2 }}
                      className="text-base md:text-lg text-slate-300/90 font-medium max-w-2xl mx-auto leading-relaxed"
                    >
                      Manage your account information and preferences
                    </motion.p>
                  </div>
                </motion.section>

                {/* Profile Card */}
                <motion.div
                  initial={{ y: 20, opacity: 0 }}
                  animate={{ y: 1, opacity: 1 }}
                  transition={{ delay: 0.3 }}
                  className="bg-slate-800/20 backdrop-blur-sm rounded-xl p-6 sm:p-8 border border-slate-700/20 shadow-xl"
                >
                  {isLoading ? (
                    <div className="flex justify-center items-center py-12">
                      <WaveSpinner />
                    </div>
                  ) : !profile ? (
                    <div className="text-center py-12">
                      <div className="text-5xl mb-4">😕</div>
                      <h3 className="text-xl font-semibold text-white mb-2">Profile not found</h3>
                      <p className="text-slate-400">Unable to load your profile information.</p>
                    </div>
                  ) : (
                    <div className="space-y-6">
                      {/* Header with Edit Button */}
                      <div className="flex items-center justify-between pb-4 border-b border-slate-700/30">
                        <h2 className="text-2xl sm:text-3xl font-bold text-white">Account Details</h2>
                        {!isEditing && (
                          <button
                            onClick={() => setIsEditing(true)}
                            className="flex items-center space-x-2 px-4 py-2 bg-cyan-600 text-white rounded-lg font-medium hover:bg-cyan-700 transition-all duration-200 shadow-lg shadow-cyan-500/30"
                          >
                            <Edit3 size={18} />
                            <span>Edit</span>
                          </button>
                        )}
                      </div>

                      <AnimatePresence mode="wait">
                        {isEditing ? (
                          /* Edit Mode */
                          <motion.form
                            key="edit-form"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            onSubmit={handleSubmit}
                            className="space-y-6"
                          >
                            {/* Username Field */}
                            <div>
                              <label htmlFor="username" className="flex items-center space-x-2 text-sm font-medium text-slate-300 mb-2">
                                <User size={16} className="text-cyan-400" />
                                <span>Username</span>
                              </label>
                              <input
                                type="text"
                                id="username"
                                value={username}
                                onChange={handleUsernameChange}
                                className={`w-full px-4 py-3 bg-slate-900/50 border ${
                                  usernameError ? 'border-red-500' : 'border-slate-700'
                                } rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 ${
                                  usernameError ? 'focus:ring-red-500' : 'focus:ring-cyan-500'
                                } transition-all duration-200`}
                                placeholder="Enter your username"
                                disabled={isSaving}
                              />
                              {usernameError && (
                                <p className="mt-1 text-sm text-red-400">{usernameError}</p>
                              )}
                            </div>

                            {/* Email Field */}
                            <div>
                              <label htmlFor="email" className="flex items-center space-x-2 text-sm font-medium text-slate-300 mb-2">
                                <Mail size={16} className="text-cyan-400" />
                                <span>Email</span>
                              </label>
                              <input
                                type="email"
                                id="email"
                                value={email}
                                onChange={handleEmailChange}
                                className={`w-full px-4 py-3 bg-slate-900/50 border ${
                                  emailError ? 'border-red-500' : 'border-slate-700'
                                } rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 ${
                                  emailError ? 'focus:ring-red-500' : 'focus:ring-cyan-500'
                                } transition-all duration-200`}
                                placeholder="Enter your email"
                                disabled={isSaving}
                              />
                              {emailError && (
                                <p className="mt-1 text-sm text-red-400">{emailError}</p>
                              )}
                            </div>

                            {/* Form Actions */}
                            <div className="flex items-center space-x-3 pt-4">
                              <button
                                type="submit"
                                disabled={isSaving || !!usernameError || !!emailError}
                                className="flex items-center space-x-2 px-6 py-3 bg-cyan-600 text-white rounded-lg font-medium hover:bg-cyan-700 disabled:bg-slate-700 disabled:cursor-not-allowed transition-all duration-200 shadow-lg shadow-cyan-500/30"
                              >
                                {isSaving ? (
                                  <>
                                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                                    <span>Saving...</span>
                                  </>
                                ) : (
                                  <>
                                    <Save size={18} />
                                    <span>Save Changes</span>
                                  </>
                                )}
                              </button>
                              <button
                                type="button"
                                onClick={handleCancel}
                                disabled={isSaving}
                                className="flex items-center space-x-2 px-6 py-3 bg-slate-700/50 text-slate-300 rounded-lg font-medium hover:bg-slate-600 disabled:cursor-not-allowed transition-all duration-200"
                              >
                                <X size={18} />
                                <span>Cancel</span>
                              </button>
                            </div>
                          </motion.form>
                        ) : (
                          /* View Mode */
                          <motion.div
                            key="view-mode"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            className="space-y-6"
                          >
                            {/* Username Display */}
                            <div className="flex items-start space-x-4 p-4 bg-slate-900/30 rounded-lg border border-slate-700/20">
                              <div className="flex-shrink-0 w-10 h-10 bg-cyan-600/20 rounded-lg flex items-center justify-center">
                                <User size={20} className="text-cyan-400" />
                              </div>
                              <div className="flex-1">
                                <p className="text-sm text-slate-400 mb-1">Username</p>
                                <p className="text-lg font-semibold text-white">{profile.username}</p>
                              </div>
                            </div>

                            {/* Email Display */}
                            <div className="flex items-start space-x-4 p-4 bg-slate-900/30 rounded-lg border border-slate-700/20">
                              <div className="flex-shrink-0 w-10 h-10 bg-emerald-600/20 rounded-lg flex items-center justify-center">
                                <Mail size={20} className="text-emerald-400" />
                              </div>
                              <div className="flex-1">
                                <p className="text-sm text-slate-400 mb-1">Email</p>
                                <p className="text-lg font-semibold text-white">{profile.email}</p>
                              </div>
                            </div>

                            {/* Account Created Date */}
                            <div className="flex items-start space-x-4 p-4 bg-slate-900/30 rounded-lg border border-slate-700/20">
                              <div className="flex-shrink-0 w-10 h-10 bg-amber-600/20 rounded-lg flex items-center justify-center">
                                <Calendar size={20} className="text-amber-400" />
                              </div>
                              <div className="flex-1">
                                <p className="text-sm text-slate-400 mb-1">Account Created</p>
                                <p className="text-lg font-semibold text-white">{formatDate(profile.created_at)}</p>
                              </div>
                            </div>

                            {/* Last Updated Date */}
                            {profile.updated_at !== profile.created_at && (
                              <div className="flex items-start space-x-4 p-4 bg-slate-900/30 rounded-lg border border-slate-700/20">
                                <div className="flex-shrink-0 w-10 h-10 bg-purple-600/20 rounded-lg flex items-center justify-center">
                                  <Calendar size={20} className="text-purple-400" />
                                </div>
                                <div className="flex-1">
                                  <p className="text-sm text-slate-400 mb-1">Last Updated</p>
                                  <p className="text-lg font-semibold text-white">{formatDate(profile.updated_at)}</p>
                                </div>
                              </div>
                            )}
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>
                  )}
                </motion.div>
              </div>
            </main>

            <Footer />
          </div>
        </div>
      </PageRouteTransitionProvider>
    </ProtectedRoute>
  );
};

export default ProfilePage;
