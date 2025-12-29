'use client';

import { useState, useRef, useEffect } from 'react';
import { User, LogOut } from 'lucide-react';
import { useClickOutside } from '@/lib/hooks/useClickOutside';

interface ProfileDropdownProps {
  user: {
    username: string;
    email: string;
    profile_picture?: string;
    auth_provider?: string;
  };
  displayName: string;
  onLogout: () => Promise<void> | void;
}

/**
 * ProfileDropdown Component
 *
 * Displays user's profile picture or default icon with a clickable dropdown menu.
 * Dropdown contains logout option and can be extended with additional menu items.
 *
 * Features:
 * - Profile picture with fallback to default icon
 * - Click to toggle dropdown
 * - Click outside to close
 * - Escape key to close
 * - Keyboard accessible (Tab, Enter, Escape)
 * - ARIA attributes for screen readers
 *
 * @param user - User object with profile data
 * @param displayName - Pre-computed display name from getUserDisplayName()
 * @param onLogout - Callback function to execute when logout is clicked
 */
export default function ProfileDropdown({
  user,
  displayName,
  onLogout
}: ProfileDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [imageError, setImageError] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useClickOutside(dropdownRef, () => setIsOpen(false));

  // Close dropdown on Escape key
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isOpen) {
        setIsOpen(false);
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen]);

  const toggleDropdown = () => {
    setIsOpen(!isOpen);
  };

  const handleLogoutClick = async () => {
    setIsOpen(false); // Close dropdown first
    await onLogout();
  };

  const handleImageError = () => {
    setImageError(true);
  };

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Profile Trigger Button - Icon Only */}
      <button
        onClick={toggleDropdown}
        className="w-10 h-10 rounded-full overflow-hidden flex items-center justify-center bg-slate-800/50 border-2 border-slate-700/30 hover:bg-slate-800/70 hover:border-cyan-600/50 transition-all duration-200 cursor-pointer"
        aria-label="User menu"
        aria-expanded={isOpen}
        aria-haspopup="menu"
        title={displayName}
      >
        {/* Profile Picture or Default Icon */}
        {user.profile_picture && !imageError ? (
          <img
            src={user.profile_picture}
            alt={`${displayName}'s profile`}
            className="w-full h-full object-cover"
            onError={handleImageError}
          />
        ) : (
          <User className="w-6 h-6 text-cyan-400" />
        )}
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div
          className="absolute right-0 mt-2 w-48 bg-slate-800 border border-slate-700/50 rounded-lg shadow-xl overflow-hidden z-50 transition-all duration-150 ease-out origin-top-right"
          role="menu"
          aria-label="User menu"
        >
          {/* Logout Menu Item */}
          <button
            onClick={handleLogoutClick}
            className="w-full px-4 py-3 text-left flex items-center space-x-3 hover:bg-slate-700/50 transition-colors duration-150 text-slate-200 hover:text-white"
            role="menuitem"
            tabIndex={0}
          >
            <LogOut className="w-4 h-4 text-red-400" />
            <span className="text-sm font-medium">Logout</span>
          </button>

          {/* Future menu items can be added here */}
          {/* Example: Profile, Settings, etc. */}
        </div>
      )}
    </div>
  );
}
