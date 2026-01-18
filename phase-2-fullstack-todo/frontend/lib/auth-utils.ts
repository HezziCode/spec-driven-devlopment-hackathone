/**
 * Utility functions for authentication-related operations
 */

/**
 * Check if Google OAuth is enabled based on environment variables
 * @returns boolean indicating if Google OAuth is configured
 */
export const isGoogleOAuthEnabled = (): boolean => {
  if (typeof window !== 'undefined') {
    // Client-side check
    return !!(
      process.env.NEXT_PUBLIC_GOOGLE_OAUTH_CLIENT_ID &&
      process.env.NEXT_PUBLIC_GOOGLE_OAUTH_CLIENT_ID.trim() !== ''
    );
  }

  // For server-side rendering
  return !!(
    process.env.NEXT_PUBLIC_GOOGLE_OAUTH_CLIENT_ID &&
    process.env.NEXT_PUBLIC_GOOGLE_OAUTH_CLIENT_ID.trim() !== ''
  );
};

/**
 * Get the Google OAuth client ID
 * @returns string Google OAuth client ID or null if not configured
 */
export const getGoogleOAuthClientId = (): string | null => {
  const clientId = process.env.NEXT_PUBLIC_GOOGLE_OAUTH_CLIENT_ID;
  return clientId && clientId.trim() !== '' ? clientId : null;
};

/**
 * Get the Google OAuth client secret
 * @returns string Google OAuth client secret or null if not configured
 */
export const getGoogleOAuthClientSecret = (): string | null => {
  const clientSecret = process.env.NEXT_PUBLIC_GOOGLE_OAUTH_CLIENT_SECRET;
  return clientSecret && clientSecret.trim() !== '' ? clientSecret : null;
};