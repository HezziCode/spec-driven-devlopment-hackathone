// Authentication utilities for TaskWave Dashboard
// Simple auth management with JWT tokens

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
  sub: string;  // User ID
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
const TOKEN_STORAGE_KEY = 'auth-token';

/**
 * Get authentication token from storage
 */
export function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(TOKEN_STORAGE_KEY);
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
 * Main authentication hook
 */
export function useAuth(): UseAuthReturn {
  const [session, setSession] = useState<Session | null>(null);
  const [status, setStatus] = useState<'authenticated' | 'unauthenticated' | 'loading'>('loading');
  const [isLoading, setIsLoading] = useState(true);

  // Load session on mount
  useEffect(() => {
    // Check for token in URL parameters (from Google OAuth callback)
    const urlParams = new URLSearchParams(window.location.search);
    const urlToken = urlParams.get('token');

    if (urlToken) {
      // If token is in URL, store it and remove from URL
      setAuthToken(urlToken);
      // Clean URL without token parameter
      const newUrl = window.location.pathname + window.location.hash;
      window.history.replaceState({}, document.title, newUrl);

      // Redirect to original destination or default to tasks
      const redirectUrl = localStorage.getItem('authRedirectUrl') || '/tasks';
      localStorage.removeItem('authRedirectUrl'); // Clean up
      window.location.href = redirectUrl;
      return; // Exit early to avoid setting session here since redirect will happen
    }

    const token = urlToken || getAuthToken();
    if (token && isTokenValid(token)) {
      const payload = decodeToken(token);
      if (payload) {
        setSession({
          user: {
            id: payload.sub,
            email: payload.email,
            username: payload.username || payload.email.split('@')[0],
          },
          token,
          expiresAt: payload.exp,
        });
        setStatus('authenticated');
      } else {
        clearAuthToken();
        setStatus('unauthenticated');
      }
    } else {
      setStatus('unauthenticated');
    }
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
      const payload = decodeToken(authResponse.token);
      if (payload) {
        const newSession: Session = {
          user: {
            id: payload.sub,
            email: payload.email,
            username: payload.username || email.split('@')[0],
          },
          token: authResponse.token,
          expiresAt: payload.exp,
        };
        setSession(newSession);
        setStatus('authenticated');

        // Redirect to original destination or default to tasks
        const redirectUrl = localStorage.getItem('authRedirectUrl') || '/tasks';
        localStorage.removeItem('authRedirectUrl'); // Clean up
        window.location.href = redirectUrl;
      }
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
      const payload = decodeToken(authResponse.token);
      if (payload) {
        const newSession: Session = {
          user: {
            id: payload.sub,
            email: payload.email,
            username: payload.username || username,
          },
          token: authResponse.token,
          expiresAt: payload.exp,
        };
        setSession(newSession);
        setStatus('authenticated');

        // Redirect to original destination or default to tasks
        const redirectUrl = localStorage.getItem('authRedirectUrl') || '/tasks';
        localStorage.removeItem('authRedirectUrl'); // Clean up
        window.location.href = redirectUrl;
      }
    } catch (error) {
      console.error('Sign up error:', error);
      throw error;
    }
  };

  // Sign out function
  const signOut = async (): Promise<void> => {
    try {
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