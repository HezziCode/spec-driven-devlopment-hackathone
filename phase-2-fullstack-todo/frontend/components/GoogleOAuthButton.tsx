'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { GoogleLogin, GoogleOAuthProvider } from '@react-oauth/google';

interface GoogleOAuthButtonProps {
  mode?: 'signin' | 'signup';
  onSuccess?: () => void;
  onError?: (error: string) => void;
}

/**
 * GoogleOAuthButton Component
 *
 * Provides "Sign in with Google" OAuth authentication button.
 * Handles Google OAuth flow, token verification with backend, and user authentication.
 *
 * @param mode - Display mode ('signin' or 'signup'), affects button text
 * @param onSuccess - Callback fired on successful authentication
 * @param onError - Callback fired on authentication error
 */
export default function GoogleOAuthButton({
  mode = 'signin',
  onSuccess,
  onError
}: GoogleOAuthButtonProps) {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const clientId = process.env.NEXT_PUBLIC_GOOGLE_OAUTH_CLIENT_ID;

  if (!clientId) {
    console.error('NEXT_PUBLIC_GOOGLE_OAUTH_CLIENT_ID is not configured');
    return (
      <div className="w-full p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
        <p className="text-yellow-800 dark:text-yellow-200 text-sm">
          ⚠️ Google OAuth not configured. Please set NEXT_PUBLIC_GOOGLE_OAUTH_CLIENT_ID in .env.local
        </p>
      </div>
    );
  }

  const handleGoogleSuccess = async (credentialResponse: any) => {
    setIsLoading(true);
    setError(null);

    try {
      const idToken = credentialResponse.credential;

      if (!idToken) {
        throw new Error('No credential received from Google');
      }

      // Send ID token to backend for verification
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/google/callback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          id_token: idToken
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Google authentication failed');
      }

      // Check if account linking is required
      if (data.requires_confirmation) {
        // Store linking data and redirect to confirmation page
        sessionStorage.setItem('google_linking_data', JSON.stringify({
          email: data.email,
          linking_token: data.linking_token,
          message: data.message
        }));
        router.push('/auth/link-account');
        return;
      }

      // Successful authentication - store JWT token
      if (data.token) {
        localStorage.setItem('better-auth-session-token', data.token);

        // Store user data
        if (data.user) {
          localStorage.setItem('user', JSON.stringify(data.user));
        }

        // Call success callback
        if (onSuccess) {
          onSuccess();
        }

        // Force full page reload to refresh auth state
        // Using window.location instead of router.push ensures useAuth() re-initializes
        window.location.href = '/tasks';
      } else {
        throw new Error('No token received from backend');
      }

    } catch (err: any) {
      const errorMessage = err.message || 'Failed to authenticate with Google';
      console.error('Google OAuth error:', errorMessage);
      setError(errorMessage);

      if (onError) {
        onError(errorMessage);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleError = () => {
    const errorMessage = 'Google sign-in was cancelled or failed';
    setError(errorMessage);

    if (onError) {
      onError(errorMessage);
    }
  };

  return (
    <div className="w-full">
      <GoogleOAuthProvider clientId={clientId}>
        <div className="flex flex-col items-stretch">
          {error && (
            <div className="mb-4 w-full p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg transition-opacity duration-150">
              <p className="text-red-800 dark:text-red-200 text-sm">{error}</p>
            </div>
          )}

          <div className="w-full flex justify-center">
            <GoogleLogin
              onSuccess={handleGoogleSuccess}
              onError={handleGoogleError}
              useOneTap={false}
              theme="outline"
              size="large"
              text={mode === 'signup' ? 'signup_with' : 'signin_with'}
              shape="rectangular"
              logo_alignment="left"
              width="320"
            />
          </div>

          {isLoading && (
            <div className="mt-3 flex items-center justify-center">
              <div className="inline-block animate-spin rounded-full h-5 w-5 border-b-2 border-indigo-600"></div>
              <span className="ml-2 text-sm text-gray-600 dark:text-gray-400">
                Authenticating with Google...
              </span>
            </div>
          )}
        </div>
      </GoogleOAuthProvider>
    </div>
  );
}
