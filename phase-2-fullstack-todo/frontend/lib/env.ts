// Environment Variable Validation Utility
// Validates required environment variables at application startup
// Ensures proper configuration for authentication and API communication

/**
 * Required environment variables for the application
 */
interface RequiredEnvVars {
  NEXT_PUBLIC_API_URL: string;
  BETTER_AUTH_SECRET: string;
}

/**
 * Optional environment variables with defaults
 */
interface OptionalEnvVars {
  NODE_ENV: string;
  BETTER_AUTH_URL: string;
}

/**
 * Validated environment configuration
 */
export interface EnvConfig extends RequiredEnvVars, OptionalEnvVars {
  isDevelopment: boolean;
  isProduction: boolean;
  isTest: boolean;
}

/**
 * Custom error for environment validation failures
 */
class EnvValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'EnvValidationError';
  }
}

/**
 * Validate that a URL string is properly formatted
 * @param url - URL string to validate
 * @returns true if valid URL, false otherwise
 */
const isValidUrl = (url: string): boolean => {
  try {
    const parsed = new URL(url);
    return parsed.protocol === 'http:' || parsed.protocol === 'https:';
  } catch {
    return false;
  }
};

/**
 * Get environment variable value
 * @param key - Environment variable key
 * @returns Environment variable value or undefined
 */
const getEnvVar = (key: string): string | undefined => {
  // Server-side (Node.js)
  if (typeof process !== 'undefined' && process.env) {
    return process.env[key];
  }

  // Client-side (Browser) - only NEXT_PUBLIC_ vars are available
  return undefined;
};

/**
 * Validate and load all required environment variables
 * @throws {EnvValidationError} if any required variable is missing or invalid
 * @returns Validated environment configuration
 */
export function validateEnv(): EnvConfig {
  const errors: string[] = [];

  // Validate NEXT_PUBLIC_API_URL
  const apiUrl = getEnvVar('NEXT_PUBLIC_API_URL');
  if (!apiUrl) {
    errors.push('NEXT_PUBLIC_API_URL is required but not defined');
  } else if (!isValidUrl(apiUrl)) {
    errors.push(`NEXT_PUBLIC_API_URL is not a valid URL: ${apiUrl}`);
  }

  // Validate BETTER_AUTH_SECRET
  const authSecret = getEnvVar('BETTER_AUTH_SECRET');
  if (!authSecret) {
    errors.push('BETTER_AUTH_SECRET is required but not defined');
  } else if (authSecret.length < 32) {
    errors.push('BETTER_AUTH_SECRET must be at least 32 characters long for security');
  }

  // Throw aggregated errors if any validation failed
  if (errors.length > 0) {
    const errorMessage = [
      'Environment validation failed:',
      ...errors.map(err => `  - ${err}`),
      '',
      'Please check your .env.local file and ensure all required variables are set.',
    ].join('\n');

    throw new EnvValidationError(errorMessage);
  }

  // Get optional variables with defaults
  const nodeEnv = getEnvVar('NODE_ENV') || 'development';
  const betterAuthUrl = getEnvVar('BETTER_AUTH_URL') || 'http://localhost:3000';

  // Build validated config
  const config: EnvConfig = {
    NEXT_PUBLIC_API_URL: apiUrl!,
    BETTER_AUTH_SECRET: authSecret!,
    NODE_ENV: nodeEnv,
    BETTER_AUTH_URL: betterAuthUrl,
    isDevelopment: nodeEnv === 'development',
    isProduction: nodeEnv === 'production',
    isTest: nodeEnv === 'test',
  };

  // Log configuration in development (server-side only)
  if (config.isDevelopment && typeof window === 'undefined') {
    console.log('\n=== Environment Configuration ===');
    console.log('NODE_ENV:', config.NODE_ENV);
    console.log('NEXT_PUBLIC_API_URL:', config.NEXT_PUBLIC_API_URL);
    console.log('BETTER_AUTH_URL:', config.BETTER_AUTH_URL);
    console.log('BETTER_AUTH_SECRET:', authSecret ? `${authSecret.substring(0, 8)}...` : 'NOT SET');
    console.log('=================================\n');
  }

  return config;
}

/**
 * Get validated environment configuration
 * Safe to call multiple times - returns cached result
 */
let cachedConfig: EnvConfig | null = null;

export function getEnvConfig(): EnvConfig {
  if (!cachedConfig) {
    cachedConfig = validateEnv();
  }
  return cachedConfig;
}

/**
 * Check if environment is properly configured
 * @returns true if all required variables are valid
 */
export function isEnvValid(): boolean {
  try {
    validateEnv();
    return true;
  } catch {
    return false;
  }
}

/**
 * Get specific environment variable with validation
 * @param key - Environment variable key
 * @returns Environment variable value
 * @throws {EnvValidationError} if variable is not set
 */
export function requireEnv(key: string): string {
  const value = getEnvVar(key);
  if (!value) {
    throw new EnvValidationError(`Required environment variable ${key} is not set`);
  }
  return value;
}

// Initialize and validate on module load (server-side only)
if (typeof window === 'undefined') {
  try {
    validateEnv();
  } catch (error) {
    console.error('\n❌ FATAL: Environment validation failed\n');
    if (error instanceof EnvValidationError) {
      console.error(error.message);
    }
    console.error('\nApplication cannot start without proper environment configuration.\n');
    // Don't exit process in Next.js - let it handle the error
  }
}

export default {
  validateEnv,
  getEnvConfig,
  isEnvValid,
  requireEnv,
};
