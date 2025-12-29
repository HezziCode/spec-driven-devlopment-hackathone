/**
 * Extract display name from user data with fallback hierarchy.
 *
 * Priority:
 * 1. Google OAuth profile name (from oauth_data.name)
 * 2. Local username
 * 3. Email-derived fallback (email prefix before @)
 *
 * @param user - User object from authentication response
 * @returns Display name for UI (max 20 characters, truncated with ellipsis)
 *
 * @example
 * // Google OAuth user
 * const googleUser = { username: 'user123', email: 'user@gmail.com', auth_provider: 'google', oauth_data: {name: 'John Doe'} };
 * getUserDisplayName(googleUser); // Returns: "John Doe"
 *
 * @example
 * // Email/password user
 * const localUser = { username: 'johndoe', email: 'john@example.com', auth_provider: 'local' };
 * getUserDisplayName(localUser); // Returns: "johndoe"
 */
export function getUserDisplayName(user: {
  username: string;
  email: string;
  auth_provider?: string;
  profile_picture?: string;
  oauth_data?: any;
}): string {
  try {
    // Priority 1: Try Google OAuth profile name
    if (user.auth_provider === 'google') {
      // oauth_data might be a string (JSON) or already parsed object
      let oauthData = user.oauth_data;

      // Parse if it's a JSON string
      if (typeof oauthData === 'string') {
        try {
          oauthData = JSON.parse(oauthData);
        } catch (e) {
          console.warn('Failed to parse oauth_data:', e);
        }
      }

      // Extract name from parsed data
      if (oauthData && oauthData.name) {
        const displayName = oauthData.name;
        return displayName.length > 20 ? `${displayName.substring(0, 20)}...` : displayName;
      }
    }

    // Priority 2: Use local username
    if (user.username) {
      const displayName = user.username;
      return displayName.length > 20 ? `${displayName.substring(0, 20)}...` : displayName;
    }

    // Priority 3: Fallback to email prefix (before @)
    if (user.email) {
      const emailPrefix = user.email.split('@')[0];
      return emailPrefix.length > 20 ? `${emailPrefix.substring(0, 20)}...` : emailPrefix;
    }

    // Ultimate fallback (should never reach here)
    return 'User';

  } catch (error) {
    console.error('Error extracting display name:', error);
    // Fallback to username or email prefix
    return user.username || user.email?.split('@')[0] || 'User';
  }
}
