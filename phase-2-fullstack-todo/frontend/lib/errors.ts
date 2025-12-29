// Error Handling Utilities for API Interactions
import type { ErrorResponse } from "@/types/api";

/**
 * Custom error class for API errors
 */
export class APIError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public code?: string,
    public details?: any
  ) {
    super(message);
    this.name = "APIError";
  }
}

/**
 * Parse API error response and extract meaningful error message
 */
export function parseAPIError(error: any): APIError {
  // Network errors (no response)
  if (!error.response) {
    if (error.message === "Failed to fetch" || error.code === "ECONNREFUSED") {
      return new APIError(
        "Unable to connect to server. Please check your internet connection or try again later.",
        0,
        "NETWORK_ERROR"
      );
    }
    return new APIError(
      error.message || "An unexpected error occurred",
      0,
      "UNKNOWN_ERROR"
    );
  }

  const statusCode = error.response?.status || error.status;
  const data: any = error.response?.data || error.data;

  // Extract error message
  let message = "An unexpected error occurred";
  let code = "UNKNOWN_ERROR";
  let details = undefined;

  if (data) {
    // Handle nested error format: {detail: {error: "...", code: "..."}}
    if (data.detail && typeof data.detail === "object" && data.detail.error) {
      message = data.detail.error;
      code = data.detail.code || `HTTP_${statusCode}`;
      details = data.detail;
    }
    // Handle flat error format: {error: "...", code: "..."}
    else if (data.error) {
      message = data.error;
      code = data.code || `HTTP_${statusCode}`;
      details = data.detail;
    }
    // Handle simple string detail: {detail: "error message"}
    else if (typeof data.detail === "string") {
      message = data.detail;
      code = `HTTP_${statusCode}`;
      details = data.detail;
    }
    // Fallback to detail object
    else {
      message = data.detail || data.error || message;
      code = data.code || `HTTP_${statusCode}`;
      details = data.detail;
    }

    // Handle validation errors (422)
    if (statusCode === 422 && typeof details === "object" && !details.error) {
      const validationErrors = Object.entries(details)
        .map(([field, msgs]) => `${field}: ${Array.isArray(msgs) ? msgs.join(", ") : msgs}`)
        .join("; ");
      message = `Validation error: ${validationErrors}`;
    }
  }

  return new APIError(message, statusCode, code, details);
}

/**
 * Map error codes to user-friendly messages
 */
export function getUserFriendlyMessage(error: APIError): string {
  const { statusCode, code } = error;

  // Authentication errors
  if (statusCode === 401) {
    if (code === "TOKEN_EXPIRED") {
      return "Your session has expired. Please sign in again.";
    }
    // Check if error message indicates user not found
    if (error.message.toLowerCase().includes("invalid credentials") ||
        error.message.toLowerCase().includes("user not found") ||
        error.message.toLowerCase().includes("not found")) {
      return "Account not found. Please sign up first or check your email address.";
    }
    if (error.message.toLowerCase().includes("incorrect password") ||
        error.message.toLowerCase().includes("wrong password")) {
      return "Incorrect password. Please try again.";
    }
    return "Authentication failed. Please check your credentials and try again.";
  }

  // Authorization errors
  if (statusCode === 403) {
    return "You don't have permission to perform this action.";
  }

  // Not found errors
  if (statusCode === 404) {
    return "The requested resource was not found.";
  }

  // Duplicate resource errors
  if (statusCode === 409) {
    if (error.message.toLowerCase().includes("email")) {
      return "This email address is already registered.";
    }
    if (error.message.toLowerCase().includes("username")) {
      return "This username is already taken.";
    }
    return "This resource already exists.";
  }

  // Validation errors
  if (statusCode === 422) {
    return error.message; // Already formatted in parseAPIError
  }

  // Server errors
  if (statusCode && statusCode >= 500) {
    return "A server error occurred. Please try again later.";
  }

  // Network errors
  if (code === "NETWORK_ERROR") {
    return error.message;
  }

  // Default to the error message from API
  return error.message || "An unexpected error occurred. Please try again.";
}

/**
 * Check if error is a network error
 */
export function isNetworkError(error: APIError): boolean {
  return error.code === "NETWORK_ERROR" || error.statusCode === 0;
}

/**
 * Check if error is due to token expiration
 */
export function isTokenExpiredError(error: APIError): boolean {
  return (
    error.statusCode === 401 &&
    (error.code === "TOKEN_EXPIRED" ||
      error.message.toLowerCase().includes("expired") ||
      error.message.toLowerCase().includes("invalid token"))
  );
}

/**
 * Check if error is an authentication error
 */
export function isAuthError(error: APIError): boolean {
  return error.statusCode === 401 || error.statusCode === 403;
}

/**
 * Check if error is a validation error
 */
export function isValidationError(error: APIError): boolean {
  return error.statusCode === 422;
}

/**
 * Format error for logging (includes full details)
 */
export function formatErrorForLogging(error: APIError): string {
  return JSON.stringify(
    {
      message: error.message,
      statusCode: error.statusCode,
      code: error.code,
      details: error.details,
      stack: error.stack,
    },
    null,
    2
  );
}

/**
 * Handle API error globally (log and optionally redirect)
 */
export function handleAPIError(error: any, redirectOnAuth: boolean = false): APIError {
  const apiError = parseAPIError(error);

  // Log error for debugging
  if (process.env.NODE_ENV === "development") {
    console.error("API Error:", formatErrorForLogging(apiError));
  }

  // Redirect to login on auth errors if requested
  if (redirectOnAuth && isAuthError(apiError) && typeof window !== "undefined") {
    // Clear any stored tokens
    localStorage.removeItem("better-auth-session-token");
    // Redirect to auth page
    window.location.href = "/auth?error=session_expired";
  }

  return apiError;
}
