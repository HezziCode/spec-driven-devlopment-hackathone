// Centralized API Client for TaskWave Dashboard
// Handles all communication with the backend FastAPI with proper authentication
// TypeScript types and comprehensive error handling

import type {
  TaskResponse,
  TaskListResponse,
  CreateTaskRequest,
  UpdateTaskRequest,
  PatchTaskRequest,
  AuthResponse,
  User,
  UserResponse,
  LoginRequest,
  SignupRequest,
  UpdateUserRequest,
  TaskQueryParams,
} from '@/types/api';
import { getAuthToken } from './auth';

// ===== Configuration =====
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || '/api';

// Development logging flag
const isDevelopment = process.env.NODE_ENV === 'development';

// ===== Logging Utilities =====

/**
 * Development logger for API requests
 */
const logRequest = (method: string, url: string, config: RequestInit): void => {
  if (!isDevelopment) return;

  console.log(`[API] ${method} ${url}`, {
    headers: config.headers,
    body: config.body ? JSON.parse(config.body as string) : undefined,
  });
};

/**
 * Development logger for API responses
 */
const logResponse = (method: string, url: string, status: number, data: any): void => {
  if (!isDevelopment) return;

  const logLevel = status >= 400 ? 'error' : 'log';
  console[logLevel as any](`[API] ${method} ${url} ${status}`, data);
};

/**
 * Development logger for API errors
 */
const logError = (method: string, url: string, error: Error): void => {
  if (!isDevelopment) return;

  console.error(`[API] ${method} ${url} ERROR`, {
    message: error.message,
    stack: error.stack,
  });
};

// ===== Query String Building =====

/**
 * Build query string from parameters object
 * Filters out undefined values and properly encodes special characters
 */
const buildQueryString = (params?: Record<string, any>): string => {
  if (!params || Object.keys(params).length === 0) {
    return '';
  }

  const queryParams = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      queryParams.append(key, String(value));
    }
  });

  const queryString = queryParams.toString();
  return queryString ? `?${queryString}` : '';
};

// ===== Core API Request Function =====

/**
 * Generic API request function with JWT token attachment
 * Handles authentication, error parsing, and response transformation
 *
 * @template T The expected response type
 * @param endpoint - The API endpoint path (e.g., '/users/123/tasks')
 * @param options - Fetch RequestInit options (method, body, headers, etc.)
 * @returns Promise resolving to the API response data
 * @throws Error with descriptive message on failure
 */
const apiRequest = async <T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> => {
  const url = `${API_BASE_URL}${endpoint}`;
  const method = options.method || 'GET';

  // Build request configuration with authentication
  const config: RequestInit = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    },
  };

  // Attach JWT token if available
  const token = getAuthToken();
  if (token) {
    config.headers = {
      ...config.headers,
      'Authorization': `Bearer ${token}`,
    };
  }

  // Log request in development
  logRequest(method, url, config);

  try {
    const response = await fetch(url, config);

    // Log response in development
    logResponse(method, url, response.status, null);

    // Handle error responses
    if (!response.ok) {
      let errorData: any = {};
      try {
        errorData = await response.json();
      } catch {
        // Response body is not JSON
        errorData = { error: response.statusText };
      }

      logError(method, url, new Error(JSON.stringify(errorData)));

      const error = new Error(
        errorData.error ||
        errorData.message ||
        errorData.detail ||
        `HTTP ${response.status}: ${response.statusText}`
      );

      (error as any).status = response.status;
      (error as any).data = errorData;

      throw error;
    }

    // Handle responses with no body (204 No Content, DELETE, etc.)
    const contentLength = response.headers.get('content-length');
    if (
      response.status === 204 ||
      contentLength === '0' ||
      response.headers.get('content-type')?.includes('text/plain')
    ) {
      logResponse(method, url, response.status, {});
      return {} as T;
    }

    // Parse and return JSON response
    const data = await response.json();
    logResponse(method, url, response.status, data);

    return data as T;
  } catch (error) {
    logError(method, url, error as Error);
    throw error;
  }
};

// ===== Authentication Endpoints =====

/**
 * Authentication API endpoints
 */
export const authApi = {
  /**
   * Register a new user account
   * @param data Signup credentials (username, email, password)
   * @returns User info and JWT token
   */
  signup: async (data: SignupRequest): Promise<AuthResponse> => {
    return apiRequest<AuthResponse>('/auth/signup', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Authenticate existing user
   * @param data Login credentials (email, password)
   * @returns User info and JWT token
   */
  login: async (data: LoginRequest): Promise<AuthResponse> => {
    return apiRequest<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Logout and invalidate session
   * @returns Success message
   */
  logout: async (): Promise<{ message: string }> => {
    return apiRequest<{ message: string }>('/auth/logout', {
      method: 'POST',
    });
  },
};

// ===== Task Endpoints =====

/**
 * Task management API endpoints
 */
export const taskApi = {
  /**
   * Retrieve all tasks for the authenticated user with optional filtering
   * @param userId User ID from auth token
   * @param params Filter, search, and pagination parameters
   * @returns List of tasks with pagination metadata
   */
  getTasks: async (
    userId: string,
    params?: TaskQueryParams
  ): Promise<TaskListResponse> => {
    const queryString = buildQueryString(params);
    return apiRequest<TaskListResponse>(
      `/users/${userId}/tasks${queryString}`
    );
  },

  /**
   * Retrieve a specific task by ID
   * @param userId User ID from auth token
   * @param taskId Task ID to retrieve
   * @returns Single task object
   */
  getTask: async (userId: string, taskId: string): Promise<TaskResponse> => {
    return apiRequest<TaskResponse>(`/users/${userId}/tasks/${taskId}`);
  },

  /**
   * Create a new task
   * @param userId User ID from auth token
   * @param data Task creation payload (title, description, priority, tags)
   * @returns Created task object with ID and timestamps
   */
  createTask: async (
    userId: string,
    data: CreateTaskRequest
  ): Promise<TaskResponse> => {
    return apiRequest<TaskResponse>(`/users/${userId}/tasks`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Fully replace an existing task (PUT)
   * Requires all fields to be provided
   * @param userId User ID from auth token
   * @param taskId Task ID to update
   * @param data Complete task update payload
   * @returns Updated task object
   */
  updateTask: async (
    userId: string,
    taskId: string,
    data: UpdateTaskRequest
  ): Promise<TaskResponse> => {
    return apiRequest<TaskResponse>(
      `/users/${userId}/tasks/${taskId}`,
      {
        method: 'PUT',
        body: JSON.stringify(data),
      }
    );
  },

  /**
   * Partially update an existing task (PATCH)
   * Only provided fields are updated
   * @param userId User ID from auth token
   * @param taskId Task ID to update
   * @param data Partial task update payload (any subset of fields)
   * @returns Updated task object
   */
  patchTask: async (
    userId: string,
    taskId: string,
    data: PatchTaskRequest
  ): Promise<TaskResponse> => {
    return apiRequest<TaskResponse>(
      `/users/${userId}/tasks/${taskId}`,
      {
        method: 'PATCH',
        body: JSON.stringify(data),
      }
    );
  },

  /**
   * Delete a task by ID
   * @param userId User ID from auth token
   * @param taskId Task ID to delete
   * @returns Success message
   */
  deleteTask: async (
    userId: string,
    taskId: string
  ): Promise<{ message: string }> => {
    return apiRequest<{ message: string }>(
      `/users/${userId}/tasks/${taskId}`,
      { method: 'DELETE' }
    );
  },
};

// ===== User Profile Endpoints =====

/**
 * User profile management API endpoints
 */
export const userApi = {
  /**
   * Retrieve authenticated user's profile
   * @param userId User ID from auth token
   * @returns User profile (username, email, timestamps)
   */
  getProfile: async (userId: string): Promise<UserResponse> => {
    return apiRequest<UserResponse>(`/users/${userId}`);
  },

  /**
   * Update authenticated user's profile
   * @param userId User ID from auth token
   * @param data Profile update payload (username, email)
   * @returns Updated user profile
   */
  updateProfile: async (
    userId: string,
    data: UpdateUserRequest
  ): Promise<UserResponse> => {
    return apiRequest<UserResponse>(`/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },
};

// ===== Exports =====

export {
  buildQueryString,
  logRequest,
  logResponse,
  logError,
};

export default {
  authApi,
  taskApi,
  userApi,
  apiRequest,
  buildQueryString,
};