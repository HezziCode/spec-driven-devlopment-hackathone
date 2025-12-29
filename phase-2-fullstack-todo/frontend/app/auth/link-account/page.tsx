'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

/**
 * Account Linking Confirmation Page
 *
 * Shown when a Google OAuth user's email matches an existing email/password account.
 * Requires user confirmation to link their Google account to the existing account.
 */
export default function LinkAccountPage() {
  const router = useRouter();
  const [linkingData, setLinkingData] = useState<{
    email: string;
    linking_token: string;
    message: string;
  } | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Load linking data from sessionStorage
    const dataStr = sessionStorage.getItem('google_linking_data');
    if (!dataStr) {
      // No linking data - redirect to auth page
      router.push('/auth');
      return;
    }

    try {
      const data = JSON.parse(dataStr);
      setLinkingData(data);
    } catch (err) {
      console.error('Failed to parse linking data:', err);
      router.push('/auth');
    }
  }, [router]);

  const handleConfirm = async (confirm: boolean) => {
    if (!linkingData) return;

    setIsSubmitting(true);
    setError(null);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/auth/google/link-confirm`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            linking_token: linkingData.linking_token,
            confirm: confirm
          })
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Account linking failed');
      }

      if (confirm) {
        // User confirmed - store token and redirect
        if (data.token) {
          localStorage.setItem('better-auth-session-token', data.token);

          if (data.user) {
            localStorage.setItem('user', JSON.stringify(data.user));
          }

          // Clear linking data
          sessionStorage.removeItem('google_linking_data');

          // Redirect to tasks
          router.push('/tasks');
        } else {
          throw new Error('No token received after linking');
        }
      } else {
        // User cancelled - clear data and return to auth
        sessionStorage.removeItem('google_linking_data');
        router.push('/auth');
      }

    } catch (err: any) {
      const errorMessage = err.message || 'Failed to process account linking';
      console.error('Account linking error:', errorMessage);
      setError(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancel = () => {
    // Clear linking data and return to auth page
    sessionStorage.removeItem('google_linking_data');
    router.push('/auth');
  };

  if (!linkingData) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 px-4 py-8">
      <div className="max-w-md w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            Link Google Account
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Account confirmation required
          </p>
        </div>

        {/* Confirmation Card */}
        <div className="bg-white dark:bg-gray-800 shadow-2xl rounded-2xl p-8">
          {/* Info Icon */}
          <div className="flex justify-center mb-6">
            <div className="w-16 h-16 rounded-full bg-indigo-100 dark:bg-indigo-900/30 flex items-center justify-center">
              <svg className="w-8 h-8 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>

          {/* Message */}
          <div className="mb-6">
            <p className="text-gray-800 dark:text-gray-200 text-center mb-4">
              {linkingData.message}
            </p>
            <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
              <p className="text-sm text-blue-800 dark:text-blue-200">
                <strong>Email:</strong> {linkingData.email}
              </p>
              <p className="text-sm text-blue-800 dark:text-blue-200 mt-2">
                If you link this account, you'll be able to sign in using either your password or Google in the future.
              </p>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <p className="text-red-800 dark:text-red-200 text-sm font-medium">
                {error}
              </p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="space-y-3">
            <button
              onClick={() => handleConfirm(true)}
              disabled={isSubmitting}
              className="w-full py-3 px-4 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white font-semibold rounded-lg shadow-md hover:shadow-lg transform hover:-translate-y-0.5 transition duration-200 disabled:cursor-not-allowed disabled:transform-none"
            >
              {isSubmitting ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Linking accounts...
                </span>
              ) : (
                'Yes, Link My Google Account'
              )}
            </button>

            <button
              onClick={handleCancel}
              disabled={isSubmitting}
              className="w-full py-3 px-4 bg-white dark:bg-gray-700 border-2 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 font-semibold rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              No, Cancel
            </button>
          </div>

          {/* Security Note */}
          <div className="mt-6 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
            <p className="text-xs text-gray-600 dark:text-gray-400 text-center">
              <svg className="inline w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
              </svg>
              Your password will remain secure. Linking only adds Google as an additional sign-in method.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
