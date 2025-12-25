'use client';

import React, { useState, useRef, useEffect } from 'react';
import { ListTodo, LogOut, Bell, Menu, X } from 'lucide-react';
import { usePathname } from 'next/navigation';

interface Notification {
  id: string;
  taskId: string;
  title: string;
  type: 'task-created' | 'task-completed' | 'task-deleted' | 'reminder';
  read: boolean;
  timestamp: string;
}

interface NavbarProps {
  userId: string | null;
  handleAuthAction: (action: string) => Promise<void> | void;
  setView: (view: string) => void;
  notifications?: Notification[];
  onMarkAllRead?: () => void;
  onNotificationClick?: (notificationId: string) => void;
}

const Navbar: React.FC<NavbarProps> = ({
  userId,
  handleAuthAction,
  setView,
  notifications = [],
  onMarkAllRead,
  onNotificationClick
}) => {
  const pathname = usePathname();
  const accentColor = 'text-cyan-600';
  const borderColor = 'border-slate-700/50';
  const textColor = 'text-slate-200';
  const iconColor = 'text-slate-400';
  const hoverBgColor = 'hover:bg-slate-800/50'; // Darker hover background for dark theme

  const [showNotifications, setShowNotifications] = useState(false);
  const [showMobileMenu, setShowMobileMenu] = useState(false);
  const notificationsRef = useRef<HTMLDivElement>(null);
  const mobileMenuRef = useRef<HTMLDivElement>(null);

  // Close notifications dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Node;

      // Close notifications dropdown if clicked outside
      if (notificationsRef.current && !notificationsRef.current.contains(target)) {
        setShowNotifications(false);
      }

      // Close mobile menu if clicked outside
      if (mobileMenuRef.current && !mobileMenuRef.current.contains(target)) {
        setShowMobileMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Get unread notifications count
  const unreadCount = notifications.filter(n => !n.read).length;

  // Mark notification as read
  const markAsRead = (id: string) => {
    onNotificationClick?.(id);
    setShowNotifications(false); // Close notifications on mobile after clicking
  };

  // Format date for display
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <nav className="sticky top-0 z-50 w-full backdrop-blur-md bg-slate-900/80 border-b border-slate-700/50 transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex justify-between items-center">

        {/* Logo and Name - Always visible */}
        <a href="/" className="inline-block">
          <div
            className="flex items-center space-x-2 cursor-pointer"
            onClick={() => setView('landing')}
          >
            <ListTodo className={`w-6 h-6 ${accentColor}`} />
            <span className="text-xl font-extrabold tracking-wide text-white transition-colors">
              TaskFlow
            </span>
          </div>
        </a>

        {/* Desktop Navigation - Hidden on mobile */}
        <div className="hidden md:flex items-center space-x-4">
          {/* Notification Bell - Only visible on tasks page */}
          {userId && pathname === '/tasks' && (
            <div className="relative" ref={notificationsRef}>
              <button
                onClick={() => setShowNotifications(!showNotifications)}
                className="p-2 rounded-full hover:bg-slate-800/50 transition-colors relative"
                aria-label="Notifications"
              >
                <Bell className={`w-5 h-5 ${iconColor}`} />
                {unreadCount > 0 && (
                  <span className="absolute -top-1 -right-1 bg-rose-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                    {unreadCount}
                  </span>
                )}
              </button>

              {/* Notification Dropdown */}
              {showNotifications && (
                <div className="absolute right-0 mt-2 w-80 bg-slate-800 border border-slate-700 rounded-xl shadow-lg z-50 overflow-hidden">
                  <div className="p-4 border-b border-slate-700 flex justify-between items-center">
                    <h3 className="font-semibold text-white">Notifications</h3>
                    {notifications.length > 0 && (
                      <button
                        onClick={onMarkAllRead}
                        className="text-sm text-cyan-400 hover:text-cyan-300 font-medium"
                      >
                        Mark all read
                      </button>
                    )}
                  </div>

                  <div className="max-h-96 overflow-y-auto">
                    {notifications.length === 0 ? (
                      <div className="p-6 text-center text-slate-400">
                        No notifications yet
                      </div>
                    ) : (
                      <ul>
                        {notifications.map(notification => (
                          <li
                            key={notification.id}
                            className={`p-4 border-b border-slate-700/50 last:border-b-0 cursor-pointer transition-colors ${
                              notification.read ? 'bg-slate-800/50 hover:bg-slate-700/50' : 'bg-slate-700/30 hover:bg-slate-700/50'
                            }`}
                            onClick={() => markAsRead(notification.id)}
                          >
                            <div className="flex items-start">
                              {!notification.read && (
                                <div className="w-2 h-2 bg-cyan-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                              )}
                              <div className="flex-1">
                                <p className={`font-medium ${notification.read ? 'text-slate-400' : 'text-white'}`}>
                                  {notification.title}
                                </p>
                                <p className="text-xs text-slate-500 mt-1">
                                  {formatDate(notification.timestamp)}
                                </p>
                              </div>
                            </div>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Auth Button */}
          {userId ? (
            <button
              onClick={() => handleAuthAction('signout')}
              className="px-4 py-2 flex items-center bg-red-500 hover:bg-red-600 text-white font-medium rounded-lg shadow-md transition-all duration-200 text-sm min-w-[100px] justify-center"
            >
              <LogOut className="w-4 h-4 mr-2" /> Sign Out
            </button>
          ) : (
            <button
              onClick={() => handleAuthAction('signin')}
              className="px-4 py-2 flex items-center bg-cyan-600 hover:bg-cyan-700 text-white font-medium rounded-lg shadow-md transition-all duration-200 text-sm min-w-[100px] justify-center"
            >
              Sign Up
            </button>
          )}
        </div>

        {/* Mobile menu button - Only visible on mobile */}
        <div className="md:hidden flex items-center">
          {userId && pathname === '/tasks' && (
            <div className="relative mr-3" ref={notificationsRef}>
              <button
                onClick={() => setShowNotifications(!showNotifications)}
                className="p-2 rounded-full hover:bg-slate-800/50 transition-colors relative"
                aria-label="Notifications"
              >
                <Bell className={`w-5 h-5 ${iconColor}`} />
                {unreadCount > 0 && (
                  <span className="absolute -top-1 -right-1 bg-rose-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                    {unreadCount}
                  </span>
                )}
              </button>

              {/* Notification Dropdown for mobile */}
              {showNotifications && (
                <div className="absolute right-0 mt-2 w-64 bg-slate-800 border border-slate-700 rounded-xl shadow-lg z-50 overflow-hidden">
                  <div className="p-3 border-b border-slate-700 flex justify-between items-center">
                    <h3 className="font-semibold text-white text-sm">Notifications</h3>
                    {notifications.length > 0 && (
                      <button
                        onClick={onMarkAllRead}
                        className="text-xs text-cyan-400 hover:text-cyan-300 font-medium"
                      >
                        Mark all read
                      </button>
                    )}
                  </div>

                  <div className="max-h-60 overflow-y-auto">
                    {notifications.length === 0 ? (
                      <div className="p-4 text-center text-slate-400 text-sm">
                        No notifications yet
                      </div>
                    ) : (
                      <ul>
                        {notifications.map(notification => (
                          <li
                            key={notification.id}
                            className={`p-3 border-b border-slate-700/50 last:border-b-0 cursor-pointer transition-colors text-sm ${
                              notification.read ? 'bg-slate-800/50 hover:bg-slate-700/50' : 'bg-slate-700/30 hover:bg-slate-700/50'
                            }`}
                            onClick={() => markAsRead(notification.id)}
                          >
                            <div className="flex items-start">
                              {!notification.read && (
                                <div className="w-2 h-2 bg-cyan-500 rounded-full mt-2 mr-2 flex-shrink-0"></div>
                              )}
                              <div className="flex-1">
                                <p className={`font-medium ${notification.read ? 'text-slate-400' : 'text-white'}`}>
                                  {notification.title}
                                </p>
                                <p className="text-xs text-slate-500 mt-1">
                                  {formatDate(notification.timestamp)}
                                </p>
                              </div>
                            </div>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}

          <button
            onClick={() => setShowMobileMenu(!showMobileMenu)}
            className="p-2 rounded-md hover:bg-slate-800/50 transition-colors"
            aria-label="Menu"
          >
            {showMobileMenu ? <X className={`w-6 h-6 ${iconColor}`} /> : <Menu className={`w-6 h-6 ${iconColor}`} />}
          </button>
        </div>
      </div>

      {/* Mobile menu - Hidden on desktop */}
      {showMobileMenu && (
        <div
          ref={mobileMenuRef}
          className="md:hidden bg-slate-900/95 backdrop-blur-md border-t border-slate-700/50"
        >
          <div className="px-4 py-3 space-y-3">
            {/* Auth Button for Mobile */}
            {userId ? (
              <button
                onClick={() => {
                  handleAuthAction('signout');
                  setShowMobileMenu(false);
                }}
                className="w-full py-3 flex items-center justify-center bg-red-500 hover:bg-red-600 text-white font-medium rounded-lg shadow-md transition-all duration-200"
              >
                <LogOut className="w-5 h-5 mr-2" /> Sign Out
              </button>
            ) : (
              <button
                onClick={() => {
                  handleAuthAction('signin');
                  setShowMobileMenu(false);
                }}
                className="w-full py-3 flex items-center justify-center bg-cyan-600 hover:bg-cyan-700 text-white font-medium rounded-lg shadow-md transition-all duration-200"
              >
                Sign Up
              </button>
            )}
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;