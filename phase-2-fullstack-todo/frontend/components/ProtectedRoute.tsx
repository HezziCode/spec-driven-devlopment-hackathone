'use client';

// ProtectedRoute component for TaskFlow Dashboard
// Redirects unauthenticated users to the auth page with redirect URL

import React, { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import WaveSpinner from './WaveSpinner';

interface ProtectedRouteProps {
  children: React.ReactNode;
  fallback?: React.ReactNode; // Custom fallback component (default is WaveSpinner)
  redirectPath?: string; // Path to redirect to if not authenticated (default is '/auth')
  authMode?: 'signin' | 'signup'; // Authentication mode to use (default is 'signin')
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  fallback,
  redirectPath = '/auth',
  authMode = 'signin'
}) => {
  const router = useRouter();
  const pathname = usePathname();
  const { session, status, isLoading } = useAuth();

  useEffect(() => {
    // If user is not authenticated and not loading, redirect to auth with redirect URL
    if (!isLoading && status === 'unauthenticated') {
      // Only add redirect URL if we're not already on the auth page
      if (pathname !== '/auth') {
        // Store the redirect URL in localStorage for use after authentication
        localStorage.setItem('authRedirectUrl', pathname);

        const params = new URLSearchParams();
        params.set('redirect', encodeURIComponent(pathname));
        params.set('mode', authMode);
        const redirectUrl = `${redirectPath}?${params.toString()}`;
        router.push(redirectUrl);
      } else {
        router.push(redirectPath);
      }
    }
  }, [status, isLoading, router, redirectPath, pathname, authMode]);

  // Show loading state while checking authentication
  if (isLoading || status === 'loading') {
    return fallback || <WaveSpinner />;
  }

  // If authenticated, render the protected content
  if (status === 'authenticated' && session) {
    return <>{children}</>;
  }

  // If not authenticated, show fallback (which will typically redirect via useEffect)
  return fallback || <WaveSpinner />;
};

export default ProtectedRoute;