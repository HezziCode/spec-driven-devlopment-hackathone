'use client';

// ProtectedRoute component for TaskWave Dashboard
// Redirects unauthenticated users to the auth page

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';
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
  const { session, status, isLoading } = useAuth();

  useEffect(() => {
    // If user is not authenticated and not loading, redirect to auth
    if (!isLoading && status === 'unauthenticated') {
      router.push(redirectPath);
    }
  }, [status, isLoading, router, redirectPath]);

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