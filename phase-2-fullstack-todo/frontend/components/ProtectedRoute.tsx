'use client';

// ProtectedRoute component for TaskWave Dashboard
// Redirects unauthenticated users to the auth page

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthHook as useAuth } from '@/lib/auth';
import WaveSpinner from './WaveSpinner';

interface ProtectedRouteProps {
  children: React.ReactNode;
  fallback?: React.ReactNode; // Custom fallback component (default is WaveSpinner)
  redirectPath?: string; // Path to redirect to if not authenticated (default is '/auth')
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  fallback,
  redirectPath = '/auth'
}) => {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    // If user is not authenticated and not loading, redirect to auth
    if (!isLoading && !isAuthenticated) {
      router.push(redirectPath);
    }
  }, [isAuthenticated, isLoading, router, redirectPath]);

  // Show loading state while checking authentication
  if (isLoading) {
    return fallback || <WaveSpinner />;
  }

  // If authenticated, render the protected content
  if (isAuthenticated) {
    return <>{children}</>;
  }

  // If not authenticated, show fallback (which will typically redirect via useEffect)
  return fallback || <WaveSpinner />;
};

export default ProtectedRoute;