// Authentication utilities for TaskWave Dashboard
// Integrates Backend API with JWT token management

'use client';

import { useState, useEffect } from 'react';
import { jwtDecode } from 'jwt-decode';
import type { AuthResponse, LoginRequest, SignupRequest } from '@/types/api';
import { authApi } from './api';

/**
 * JWT Token payload structure
 */
interface JwtPayload {
  exp: number;
  iat: number;
  user_id: string;
  email: string;
  username?: string;
  [key: string]: any;
}

/**
 * Session data structure
 */
export interface Session {
  user: {
    id: string;
    email: string;
    username: string;
  };
  token: string;
  expiresAt: number;
}

/**
 * Auth hook return type
 */
export interface UseAuthReturn {
  session: Session | null;
  status: 'authenticated' | 'unauthenticated' | 'loading';
  isLoading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (username: string, email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
}

// Storage key for JWT token
const TOKEN_STORAGE_KEY = 'better-auth-session-token';

/**
 * Get authentication token from storage
 */
export function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;

  // Try localStorage first
  const token = localStorage.getItem(TOKEN_STORAGE_KEY);
  if (token) return token;

  // Fallback to cookies
  const cookieValue = document.cookie
    .split('; ')
    .find(row => row.startsWith(`${TOKEN_STORAGE_KEY}=`))
    ?.split('=')[1];

  return cookieValue || null;
}

/**
 * Store authentication token
 */
function setAuthToken(token: string): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(TOKEN_STORAGE_KEY, token);
}

/**
 * Clear authentication token
 */
function clearAuthToken(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(TOKEN_STORAGE_KEY);
}

/**
 * Decode JWT token and extract payload
 */
function decodeToken(token: string): JwtPayload | null {
  try {
    return jwtDecode<JwtPayload>(token);
  } catch (error) {
    console.error('Error decoding JWT token:', error);
    return null;
  }
}

/**
 * Check if token is valid and not expired
 */
export function isTokenValid(token: string): boolean {
  const payload = decodeToken(token);
  if (!payload) return false;

  const currentTime = Math.floor(Date.now() / 1000);
  return payload.exp > currentTime;
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  const token = getAuthToken();
  return token !== null && isTokenValid(token);
}

/**
 * Get current user ID from token
 */
export function getCurrentUserId(): string | null {
  const token = getAuthToken();
  if (!token) return null;

  const payload = decodeToken(token);
  return payload?.user_id || null;
}

/**
 * Get current user email from token
 */
export function getCurrentUserEmail(): string | null {
  const token = getAuthToken();
  if (!token) return null;

  const payload = decodeToken(token);
  return payload?.email || null;
}

/**
 * Get current username from token
 */
export function getCurrentUsername(): string | null {
  const token = getAuthToken();
  if (!token) return null;

  const payload = decodeToken(token);
  return payload?.username || payload?.email?.split('@')[0] || null;
}

/**
 * Convert AuthResponse to Session
 */
function authResponseToSession(authResponse: AuthResponse): Session {
  const payload = decodeToken(authResponse.token);

  return {
    user: {
      id: authResponse.user.id,
      email: authResponse.user.email,
      username: authResponse.user.username,
    },
    token: authResponse.token,
    expiresAt: payload?.exp || 0,
  };
}

/**
 * Load session from stored token
 */
function loadSessionFromToken(): Session | null {
  const token = getAuthToken();
  if (!token || !isTokenValid(token)) {
    clearAuthToken();
    return null;
  }

  const payload = decodeToken(token);
  if (!payload) return null;

  return {
    user: {
      id: payload.user_id,
      email: payload.email,
      username: payload.username || payload.email.split('@')[0],
    },
    token,
    expiresAt: payload.exp,
  };
}

/**
 * Main authentication hook
 */
export function useAuth(): UseAuthReturn {
  const [session, setSession] = useState<Session | null>(null);
  const [status, setStatus] = useState<'authenticated' | 'unauthenticated' | 'loading'>('loading');
  const [isLoading, setIsLoading] = useState(true);

  // Load session on mount
  useEffect(() => {
    const loadedSession = loadSessionFromToken();
    setSession(loadedSession);
    setStatus(loadedSession ? 'authenticated' : 'unauthenticated');
    setIsLoading(false);
  }, []);

  // Sign in function
  const signIn = async (email: string, password: string): Promise<void> => {
    try {
      const loginRequest: LoginRequest = { email, password };
      const authResponse = await authApi.login(loginRequest);

      // Store token
      setAuthToken(authResponse.token);

      // Update session
      const newSession = authResponseToSession(authResponse);
      setSession(newSession);
      setStatus('authenticated');
    } catch (error) {
      console.error('Sign in error:', error);
      throw error;
    }
  };

  // Sign up function
  const signUp = async (username: string, email: string, password: string): Promise<void> => {
    try {
      const signupRequest: SignupRequest = { username, email, password };
      const authResponse = await authApi.signup(signupRequest);

      // Store token
      setAuthToken(authResponse.token);

      // Update session
      const newSession = authResponseToSession(authResponse);
      setSession(newSession);
      setStatus('authenticated');
    } catch (error) {
      console.error('Sign up error:', error);
      throw error;
    }
  };

  // Sign out function
  const signOut = async (): Promise<void> => {
    try {
      // Call backend logout (optional, since JWT is stateless)
      try {
        await authApi.logout();
      } catch (error) {
        // Ignore errors from logout endpoint
        console.warn('Logout endpoint error (ignored):', error);
      }

      // Clear token and session
      clearAuthToken();
      setSession(null);
      setStatus('unauthenticated');
    } catch (error) {
      console.error('Sign out error:', error);
      throw error;
    }
  };

  return {
    session,
    status,
    isLoading,
    signIn,
    signUp,
    signOut,
  };
}

/**
 * Hook for backward compatibility (alias for useAuth)
 */
export const useSession = useAuth;

/**
 * Check if token is about to expire (within 5 minutes)
 */
export function isTokenExpiringSoon(): boolean {
  const token = getAuthToken();
  if (!token) return false;

  const payload = decodeToken(token);
  if (!payload) return false;

  const currentTime = Math.floor(Date.now() / 1000);
  const fiveMinutes = 5 * 60;

  return payload.exp - currentTime < fiveMinutes;
}

/**
 * Get token expiration time
 */
export function getTokenExpiration(): number | null {
  const token = getAuthToken();
  if (!token) return null;

  const payload = decodeToken(token);
  return payload?.exp || null;
}

/**
 * Redirect to auth page if not authenticated
 */
export function requireAuth(redirectUrl?: string): void {
  if (!isAuthenticated() && typeof window !== 'undefined') {
    const url = redirectUrl || '/auth';
    window.location.href = url;
  }
}

/**
 * Verify token validity
 */
export function verifyToken(token: string): boolean {
  return isTokenValid(token);
}
