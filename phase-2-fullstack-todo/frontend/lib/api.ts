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
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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

  try {
    const response = await fetch(url, config);

    // Handle error responses
    if (!response.ok) {
      let errorData: unknown = {};
      try {
        errorData = await response.json();
      } catch {
        // Response body is not JSON
        errorData = { error: response.statusText };
      }

      // Extract error message from various formats
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
      let errorCode = `HTTP_${response.status}`;

      // Type guard for error data object
      const isErrorObject = (data: unknown): data is Record<string, unknown> => {
        return typeof data === 'object' && data !== null;
      };

      // Handle 422 Validation Error with user-friendly messages
      if (response.status === 422 && isErrorObject(errorData)) {
        // FastAPI validation errors come in detail array format
        if (Array.isArray(errorData.detail)) {
          const validationErrors = errorData.detail.map((err: any) => {
            const field = err.loc?.[err.loc.length - 1] || 'field';
            const msg = err.msg || 'Invalid value';
            return `${field}: ${msg}`;
          }).join(', ');
          errorMessage = `Please check your input: ${validationErrors}`;
        } else if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail;
        } else {
          errorMessage = 'Please check your input and try again.';
        }
        errorCode = 'VALIDATION_ERROR';
      }

      if (isErrorObject(errorData)) {
        // Handle nested format: {detail: {error: "...", code: "..."}}
        if ('detail' in errorData && errorData.detail && typeof errorData.detail === 'object' && errorData.detail !== null) {
          const detail = errorData.detail as Record<string, unknown>;
          errorMessage = (detail.error as string) || (detail.message as string) || errorMessage;
          errorCode = (detail.code as string) || errorCode;
        }
        // Handle flat format: {error: "...", code: "..."}
        else if (typeof errorData.error === 'string') {
          errorMessage = errorData.error;
          errorCode = (typeof errorData.code === 'string' ? errorData.code : errorCode);
        }
        // Handle simple string detail: {detail: "..."}
        else if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail;
        }
        // Handle message field
        else if (typeof errorData.message === 'string') {
          errorMessage = errorData.message;
          errorCode = (typeof errorData.code === 'string' ? errorData.code : errorCode);
        }
      }

      const error = new Error(errorMessage);
      (error as any).status = response.status;
      (error as any).statusCode = response.status;
      (error as any).code = errorCode;
      (error as any).data = errorData;
      (error as any).details = isErrorObject(errorData) ? errorData.detail : undefined;

      throw error;
    }

    // Handle responses with no body (204 No Content, DELETE, etc.)
    const contentLength = response.headers.get('content-length');
    if (
      response.status === 204 ||
      contentLength === '0' ||
      response.headers.get('content-type')?.includes('text/plain')
    ) {
      return {} as T;
    }

    // Parse and return JSON response
    const data = await response.json();
    return data as T;
  } catch (error) {
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
    const searchParams = new URLSearchParams();
    if (params?.limit) searchParams.set('limit', params.limit.toString());
    if (params?.offset) searchParams.set('offset', params.offset.toString());
    if (params?.status) searchParams.set('status', params.status.toString());
    if (params?.priority) searchParams.set('priority', params.priority.toString());
    if (params?.tag) searchParams.set('tag', params.tag.toString());
    if (params?.search) searchParams.set('search', params.search.toString());

    const queryString = searchParams.toString();
    return apiRequest<TaskListResponse>(
      `/users/${userId}/tasks${queryString ? '?' + queryString : ''}`
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

export default {
  authApi,
  taskApi,
  userApi,
  apiRequest,
};