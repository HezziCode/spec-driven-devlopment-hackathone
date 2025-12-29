// API Response Types for Frontend-Backend Integration
// These types match the backend FastAPI schemas

/**
 * Priority levels for tasks
 */
export type PriorityEnum = "low" | "medium" | "high" | "critical";

/**
 * Sort options for task lists
 */
export type SortEnum = "created" | "title" | "priority" | "updated";

/**
 * Status filter options
 */
export type StatusEnum = "pending" | "completed" | "all";

/**
 * User data returned from authentication
 */
export interface User {
  id: string;
  username: string;
  email: string;
  created_at?: string;
  updated_at?: string;
  profile_picture?: string;
  auth_provider?: string;
}

/**
 * Authentication response from signup/login
 */
export interface AuthResponse {
  user: User;
  token: string;
}

/**
 * Task data matching backend TaskResponse schema
 */
export interface TaskResponse {
  id: string;
  title: string;
  description: string;
  completed: boolean;
  priority: PriorityEnum;
  tags: string[];
  user_id: string;
  created_at: string;
  updated_at: string;
}

/**
 * Task list response with pagination metadata
 */
export interface TaskListResponse {
  tasks: TaskResponse[];
  total: number;
  page: number;
  limit: number;
}

/**
 * User profile response (excludes password)
 */
export interface UserResponse {
  id: string;
  username: string;
  email: string;
  created_at: string;
  updated_at: string;
  profile_picture?: string;
  auth_provider?: string;
}

/**
 * Standardized error response from API
 */
export interface ErrorResponse {
  error: string;
  code?: string;
  timestamp?: string;
  detail?: string | Record<string, any>;
}

/**
 * Request payload for creating a new task
 */
export interface CreateTaskRequest {
  title: string;
  description: string;
  priority: PriorityEnum;
  tags?: string[];
}

/**
 * Request payload for updating a task (full update)
 */
export interface UpdateTaskRequest {
  title: string;
  description: string;
  completed: boolean;
  priority: PriorityEnum;
  tags?: string[];
}

/**
 * Request payload for partially updating a task
 */
export interface PatchTaskRequest {
  title?: string;
  description?: string;
  completed?: boolean;
  priority?: PriorityEnum;
  tags?: string[];
}

/**
 * Request payload for user signup
 */
export interface SignupRequest {
  username: string;
  email: string;
  password: string;
}

/**
 * Request payload for user login
 */
export interface LoginRequest {
  email: string;
  password: string;
}

/**
 * Request payload for updating user profile
 */
export interface UpdateUserRequest {
  username?: string;
  email?: string;
}

/**
 * Query parameters for fetching tasks
 */
export interface TaskQueryParams {
  limit?: number;
  offset?: number;
  completed?: boolean;
  priority?: PriorityEnum;
  tag?: string;
  search?: string;
  sort?: SortEnum;
}
