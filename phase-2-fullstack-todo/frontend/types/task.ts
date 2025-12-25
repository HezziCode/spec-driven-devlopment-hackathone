// TypeScript interfaces for TaskFlow Dashboard entities

export interface Task {
  id: string; // UUID
  title: string; // Required title (max 200 characters)
  description: string; // Optional description (max 1000 characters)
  completed: boolean; // Status indicating if the task is completed
  priority: 'high' | 'medium' | 'low'; // Priority level
  tags: string[]; // Array of tags for categorization (max 10 items)
  createdAt: string; // ISO 8601 timestamp when the task was created
  updatedAt: string; // ISO 8601 timestamp when the task was last updated
  userId: string; // Foreign key to the user who owns the task
}

export interface TaskCreateRequest {
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  tags: string[];
}

export interface TaskUpdateRequest {
  title?: string;
  description?: string;
  completed?: boolean;
  priority?: 'high' | 'medium' | 'low';
  tags?: string[];
}

export interface TaskResponse {
  id: string;
  title: string;
  description: string;
  completed: boolean;
  priority: 'high' | 'medium' | 'low';
  tags: string[];
  user_id: string; // Note: API uses snake_case
  created_at: string; // Note: API uses snake_case
  updated_at: string; // Note: API uses snake_case
}

export interface TaskListResponse {
  tasks: TaskResponse[];
  total: number;
}

export interface StreakData {
  currentStreak: number;
  longestStreak: number;
  lastCompletedDate: string; // ISO 8601 date
}

export interface StreakResponse {
  currentStreak: number;
  longestStreak: number;
  lastCompletedDate: string; // ISO 8601 date
}

export type PriorityLevel = 'high' | 'medium' | 'low';

export interface PriorityDisplay {
  level: PriorityLevel;
  label: string;
  color: string; // Tailwind color class
  icon: string; // Icon identifier for flame/clock/leaf
}