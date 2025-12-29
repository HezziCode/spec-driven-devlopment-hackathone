'use client';

import React from 'react';
import { ListTodo } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import ProfileDropdown from '@/components/ProfileDropdown';
import { getUserDisplayName } from '@/lib/utils/getUserDisplayName';

interface NavbarProps {
  // Keeping for backward compatibility with existing pages
  userId?: string | null;
  handleAuthAction?: (action: string) => Promise<void> | void;
  setView?: (view: string) => void;
  notifications?: any[];
  onMarkAllRead?: () => void;
  onNotificationClick?: (id: string) => void;
}

const Navbar: React.FC<NavbarProps> = () => {
  const router = useRouter();
  const { session, signOut } = useAuth();

  // Handle logout
  const handleLogout = async () => {
    try {
      await signOut();
      router.push('/');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  // Navigate to auth page
  const navigateToAuth = () => {
    router.push('/auth');
  };

  return (
    <nav className="sticky top-0 z-50 w-full backdrop-blur-md bg-slate-900/80 border-b border-slate-700/50 transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex justify-between items-center">

        {/* Logo - Left side */}
        <a href="/" className="inline-block">
          <div className="flex items-center space-x-2 cursor-pointer">
            <ListTodo className="w-6 h-6 text-cyan-600" />
            <span className="text-xl font-extrabold tracking-wide text-white transition-colors">
              TaskWave
            </span>
          </div>
        </a>

        {/* Right side - Auth button or Profile dropdown */}
        <div className="flex items-center space-x-3">
          {session ? (
            /* Profile Dropdown */
            <ProfileDropdown
              user={session.user}
              displayName={getUserDisplayName(session.user)}
              onLogout={handleLogout}
            />
          ) : (
            /* Sign Up Button - Only shown when NOT authenticated */
            <button
              onClick={navigateToAuth}
              className="px-6 py-2 flex items-center bg-cyan-600 hover:bg-cyan-700 text-white font-semibold rounded-lg shadow-md hover:shadow-lg transition-all duration-200 transform hover:-translate-y-0.5"
            >
              Sign Up
            </button>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
