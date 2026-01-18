'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';

export default function AuthPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { signUp, signIn, session, signOut } = useAuth();
  const [isSignUp, setIsSignUp] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [googleOAuthEnabled, setGoogleOAuthEnabled] = useState(false);
  const [showLinkingConfirmation, setShowLinkingConfirmation] = useState(false);
  const [linkingEmail, setLinkingEmail] = useState('');
  const [linkingToken, setLinkingToken] = useState('');

  // Check if Google OAuth is enabled based on environment variables
  useEffect(() => {
    const isEnabled =
      typeof process.env.NEXT_PUBLIC_GOOGLE_OAUTH_CLIENT_ID !== 'undefined' &&
      process.env.NEXT_PUBLIC_GOOGLE_OAUTH_CLIENT_ID !== '';

    setGoogleOAuthEnabled(isEnabled);

    // Check for linking required parameters from Google OAuth callback
    const linkingRequired = searchParams.get('linking_required');
    const emailParam = searchParams.get('email');
    const tokenParam = searchParams.get('linking_token');

    if (linkingRequired === 'true' && emailParam && tokenParam) {
      setLinkingEmail(emailParam);
      setLinkingToken(tokenParam);
      setShowLinkingConfirmation(true);
      setError(`An account with email ${emailParam} already exists. Do you want to link your Google account to this existing account?`);
    }
  }, [searchParams]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (error) setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (isSignUp) {
      // Validation for signup
      if (formData.password !== formData.confirmPassword) {
        setError('Passwords do not match');
        setLoading(false);
        return;
      }

      if (formData.password.length < 6) {
        setError('Password must be at least 6 characters');
        setLoading(false);
        return;
      }

      try {
        await signUp(formData.username, formData.email, formData.password);
        router.push('/tasks');
      } catch (err: any) {
        setError(err.message || 'Signup failed');
      } finally {
        setLoading(false);
      }
    } else {
      // Validation for signin
      if (formData.email && formData.password) {
        try {
          await signIn(formData.email, formData.password);
          router.push('/tasks');
        } catch (err: any) {
          setError(err.message || 'Login failed');
        } finally {
          setLoading(false);
        }
      } else {
        setError('Please enter both email and password');
        setLoading(false);
      }
    }
  };

  // Handle Google OAuth callback
  const handleGoogleOAuth = () => {
    // Redirect to backend Google OAuth endpoint
    // Ensure we're using the correct API URL without /api suffix since backend serves auth at /auth
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    // Remove any trailing /api from the base URL to ensure proper auth endpoint
    const cleanBaseUrl = baseUrl.endsWith('/api') ? baseUrl.slice(0, -4) : baseUrl;
    window.location.href = `${cleanBaseUrl}/auth/google`;
  };

  // Handle logout
  const handleLogout = async () => {
    try {
      await signOut();
      router.push('/');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  // Handle Google account linking confirmation
  const handleLinkConfirmation = async (confirm: boolean) => {
    try {
      // Construct API URL properly
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const cleanBaseUrl = baseUrl.endsWith('/api') ? baseUrl.slice(0, -4) : baseUrl;
      const response = await fetch(`${cleanBaseUrl}/auth/google/link-confirm`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          linking_token: linkingToken,
          confirm: confirm
        })
      });

      const result = await response.json();

      if (response.ok) {
        // Store the token and redirect to original destination or default to tasks
        localStorage.setItem('auth-token', result.token);

        // Check for redirect URL from query params or fallback to stored redirect URL
        const urlParams = new URLSearchParams(window.location.search);
        const redirectParam = urlParams.get('redirect');
        const redirectUrl = redirectParam ? decodeURIComponent(redirectParam) : localStorage.getItem('authRedirectUrl') || '/tasks';
        localStorage.removeItem('authRedirectUrl'); // Clean up

        router.push(redirectUrl);
      } else {
        setError(result.error || 'Failed to link accounts');
      }
    } catch (err) {
      console.error('Link confirmation error:', err);
      setError('Failed to link accounts');
    } finally {
      setShowLinkingConfirmation(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-900">
      <Navbar />

      <main className="flex-grow flex items-center justify-center py-12">
        <div className="w-full max-w-md p-8 space-y-8 bg-slate-800/50 backdrop-blur-sm rounded-xl shadow-2xl border border-slate-700/50">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-white">
              {isSignUp ? 'Create Account' : 'Welcome Back'}
            </h2>
            <p className="mt-2 text-slate-300">
              {isSignUp ? 'Sign up to get started' : 'Sign in to your account'}
            </p>
          </div>

          {error && !showLinkingConfirmation && (
            <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-4 text-red-300">
              {error}
            </div>
          )}

          {showLinkingConfirmation ? (
            // Show account linking confirmation
            <div className="space-y-6">
              <div className="bg-yellow-500/20 border border-yellow-500/50 rounded-lg p-4 text-yellow-300">
                {error}
              </div>

              <div className="flex space-x-4">
                <button
                  onClick={() => handleLinkConfirmation(true)}
                  className="flex-1 py-2 px-4 bg-green-600 hover:bg-green-700 rounded-lg text-white font-medium transition-colors duration-200"
                >
                  Yes, Link Accounts
                </button>
                <button
                  onClick={() => handleLinkConfirmation(false)}
                  className="flex-1 py-2 px-4 bg-red-600 hover:bg-red-700 rounded-lg text-white font-medium transition-colors duration-200"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6">
              {isSignUp && (
                <div>
                  <label htmlFor="username" className="block text-sm font-medium text-slate-300 mb-1">
                    Username
                  </label>
                  <input
                    id="username"
                    name="username"
                    type="text"
                    required={isSignUp}
                    value={formData.username}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-slate-600 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-transparent bg-slate-700 text-white placeholder-slate-400"
                    placeholder="Enter username"
                  />
                </div>
              )}

              <div>
                <label htmlFor="email" className="block text-sm font-medium text-slate-300 mb-1">
                  Email
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  required
                  value={formData.email}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-slate-600 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-transparent bg-slate-700 text-white placeholder-slate-400"
                  placeholder="Enter email"
                />
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-slate-300 mb-1">
                  Password
                </label>
                <input
                  id="password"
                  name="password"
                  type="password"
                  required
                  value={formData.password}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-slate-600 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-transparent bg-slate-700 text-white placeholder-slate-400"
                  placeholder="Enter password"
                />
              </div>

              {isSignUp && (
                <div>
                  <label htmlFor="confirmPassword" className="block text-sm font-medium text-slate-300 mb-1">
                    Confirm Password
                  </label>
                  <input
                    id="confirmPassword"
                    name="confirmPassword"
                    type="password"
                    required={isSignUp}
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    className="w-full px-4 py-2 border border-slate-600 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-transparent bg-slate-700 text-white placeholder-slate-400"
                    placeholder="Confirm password"
                  />
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 px-4 bg-cyan-600 hover:bg-cyan-700 rounded-lg text-white font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-cyan-500 disabled:opacity-50 transition-all duration-200"
              >
                {loading ? (isSignUp ? 'Creating Account...' : 'Signing In...') : (isSignUp ? 'Sign Up' : 'Sign In')}
              </button>
            </form>
          )}

          {googleOAuthEnabled && !showLinkingConfirmation && (
            <div className="mt-6">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-slate-600"></div>
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-slate-800 text-slate-400">
                    Or continue with
                  </span>
                </div>
              </div>

              <div className="mt-6">
                <button
                  onClick={handleGoogleOAuth}
                  className="w-full flex items-center justify-center px-4 py-2 border border-slate-600 rounded-md shadow-sm text-sm font-medium text-slate-300 bg-slate-700 hover:bg-slate-600 transition-colors duration-200"
                >
                  <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M22.56 12.25C22.56 11.47 22.49 10.72 22.36 10H12V14.26H17.92C17.66 15.63 16.88 16.79 15.71 17.57V20.34H19.28C21.36 18.42 22.56 15.6 22.56 12.25Z" fill="#4285F4"/>
                    <path d="M12 23C14.97 23 17.46 22.02 19.28 20.34L15.71 17.57C14.73 18.23 13.48 18.64 12 18.64C9.14 18.64 6.71 16.69 5.84 14.09H2.18V16.96C4 20.53 7.7 23 12 23Z" fill="#34A853"/>
                    <path d="M5.84 14.09C5.62 13.43 5.49 12.73 5.49 12C5.49 11.27 5.62 10.57 5.84 9.91V7.04H2.18C1.43 8.55 1 10.22 1 12C1 13.78 1.43 15.45 2.18 16.96L5.84 14.09Z" fill="#FBBC05"/>
                    <path d="M12 5.36C13.62 5.36 15.06 5.93 16.21 7.04L19.36 3.89C17.45 2.09 14.97 1 12 1C7.7 1 4 3.47 2.18 7.04L5.84 9.91C6.71 7.31 9.14 5.36 12 5.36Z" fill="#EA4335"/>
                  </svg>
                  {isSignUp ? 'Sign up with Google' : 'Sign in with Google'}
                </button>
              </div>
            </div>
          )}

          {!showLinkingConfirmation && (
            <div className="text-center text-sm text-slate-400">
              {isSignUp ? 'Already have an account?' : "Don't have an account?"}{' '}
              <button
                onClick={() => {
                  setIsSignUp(!isSignUp);
                  setError('');
                }}
                className="font-medium text-cyan-400 hover:text-cyan-300 transition-colors duration-200"
              >
                {isSignUp ? 'Sign In' : 'Sign Up'}
              </button>
            </div>
          )}
        </div>
      </main>

      <Footer variant="minimal" />
    </div>
  );
}