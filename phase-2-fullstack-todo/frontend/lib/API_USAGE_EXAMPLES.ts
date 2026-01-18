// Comprehensive API Client Usage Examples
// Reference file demonstrating all available API endpoints and patterns

import {
  authApi,
  taskApi,
  userApi,
  buildQueryString,
} from '@/lib/api';
import { getCurrentUserId } from '@/lib/auth';
import type {
  AuthResponse,
  TaskResponse,
  TaskListResponse,
  UserResponse,
} from '@/types/api';

// ===== AUTHENTICATION EXAMPLES =====

/**
 * Example: User Registration
 */
export async function exampleSignup(): Promise<void> {
  try {
    const response: AuthResponse = await authApi.signup({
      username: 'john_doe',
      email: 'john@example.com',
      password: 'SecurePassword123!',
    });

    console.log('User registered:', response.user);
    console.log('JWT Token:', response.token);
    // Token is typically stored in localStorage via Better Auth

  } catch (error: any) {
    console.error('Signup failed:', error.message);
    if (error.status === 409) {
      console.error('User already exists');
    }
  }
}

/**
 * Example: User Login
 */
export async function exampleLogin(): Promise<void> {
  try {
    const response: AuthResponse = await authApi.login({
      email: 'john@example.com',
      password: 'SecurePassword123!',
    });

    console.log('Login successful:', response.user);
    console.log('Token expires at:', new Date(response.user.updated_at || ''));

  } catch (error: any) {
    if (error.status === 401) {
      console.error('Invalid credentials');
    } else if (error.status === 404) {
      console.error('User not found');
    }
  }
}

/**
 * Example: User Logout
 */
export async function exampleLogout(): Promise<void> {
  try {
    const response = await authApi.logout();
    console.log(response.message);
    // Frontend should clear token storage after logout
    localStorage.removeItem('better-auth-session-token');

  } catch (error: any) {
    console.error('Logout error:', error.message);
  }
}

// ===== TASK EXAMPLES =====

/**
 * Example: Get All Tasks with Basic Filtering
 */
export async function exampleGetAllTasks(): Promise<void> {
  try {
    const userId = getCurrentUserId();
    if (!userId) {
      console.error('User not authenticated');
      return;
    }

    // Fetch all tasks (uses defaults: limit=20, offset=0)
    const result: TaskListResponse = await taskApi.getTasks(userId);
    console.log(`Retrieved ${result.tasks.length} tasks`);
    console.log(`Total tasks: ${result.total}`);

  } catch (error: any) {
    console.error('Failed to fetch tasks:', error.message);
  }
}

/**
 * Example: Get Tasks with Advanced Filtering
 */
export async function exampleGetTasksFiltered(): Promise<void> {
  try {
    const userId = getCurrentUserId();
    if (!userId) return;

    // Get high-priority pending tasks, sorted by creation date
    const result: TaskListResponse = await taskApi.getTasks(userId, {
      limit: 50,
      offset: 0,
      completed: false,
      priority: 'high',
      search: 'urgent feature',
      sort: 'created',
    });

    console.log('Filtered tasks:', result.tasks);

  } catch (error: any) {
    console.error('Filter failed:', error.message);
  }
}

/**
 * Example: Get Tasks by Priority
 */
export async function exampleGetTasksByPriority(
  priority: 'low' | 'medium' | 'high' | 'critical'
): Promise<TaskResponse[]> {
  const userId = getCurrentUserId();
  if (!userId) throw new Error('Not authenticated');

  const result = await taskApi.getTasks(userId, {
    priority,
    limit: 100,
  });

  return result.tasks;
}

/**
 * Example: Search Tasks
 */
export async function exampleSearchTasks(searchTerm: string): Promise<TaskResponse[]> {
  const userId = getCurrentUserId();
  if (!userId) throw new Error('Not authenticated');

  const result = await taskApi.getTasks(userId, {
    search: searchTerm,
    limit: 50,
  });

  return result.tasks;
}

/**
 * Example: Get Single Task
 */
export async function exampleGetTask(taskId: string): Promise<void> {
  try {
    const userId = getCurrentUserId();
    if (!userId) return;

    const task: TaskResponse = await taskApi.getTask(userId, taskId);
    console.log('Task:', task);
    console.log('Created:', new Date(task.created_at));
    console.log('Last modified:', new Date(task.updated_at));

  } catch (error: any) {
    if (error.status === 404) {
      console.error('Task not found');
    } else {
      console.error('Error fetching task:', error.message);
    }
  }
}

/**
 * Example: Create Task
 */
export async function exampleCreateTask(): Promise<void> {
  try {
    const userId = getCurrentUserId();
    if (!userId) return;

    const newTask: TaskResponse = await taskApi.createTask(userId, {
      title: 'Implement user authentication',
      description: 'Add JWT-based authentication with Better Auth',
      priority: 'high',
      tags: ['backend', 'security', 'required'],
    });

    console.log('Task created:', newTask.id);
    console.log('Task:', newTask);

  } catch (error: any) {
    if (error.status === 422) {
      console.error('Validation error:', error.data);
    } else {
      console.error('Failed to create task:', error.message);
    }
  }
}

/**
 * Example: Create Multiple Tasks
 */
export async function exampleCreateMultipleTasks(): Promise<TaskResponse[]> {
  const userId = getCurrentUserId();
  if (!userId) throw new Error('Not authenticated');

  const taskData = [
    { title: 'Design UI mockups', description: 'Figma designs for dashboard', priority: 'high' as const, tags: ['design'] },
    { title: 'Setup database', description: 'Create PostgreSQL schema', priority: 'critical' as const, tags: ['backend', 'database'] },
    { title: 'Write API documentation', description: 'OpenAPI/Swagger docs', priority: 'medium' as const, tags: ['docs'] },
  ];

  const createdTasks: TaskResponse[] = [];

  for (const data of taskData) {
    const task = await taskApi.createTask(userId, data);
    createdTasks.push(task);
  }

  return createdTasks;
}

/**
 * Example: Full Update Task (PUT) - All fields required
 */
export async function exampleUpdateTaskFull(taskId: string): Promise<void> {
  try {
    const userId = getCurrentUserId();
    if (!userId) return;

    // First get the current task to preserve fields
    const currentTask = await taskApi.getTask(userId, taskId);

    // PUT requires all fields
    const updated: TaskResponse = await taskApi.updateTask(userId, taskId, {
      title: 'Updated: ' + currentTask.title,
      description: currentTask.description + ' [updated]',
      completed: false,
      priority: 'critical',
      tags: [...currentTask.tags, 'urgent'],
    });

    console.log('Task updated:', updated);

  } catch (error: any) {
    console.error('Update failed:', error.message);
  }
}

/**
 * Example: Partial Update Task (PATCH) - Only changed fields
 */
export async function exampleUpdateTaskPartial(taskId: string): Promise<void> {
  try {
    const userId = getCurrentUserId();
    if (!userId) return;

    // PATCH only updates provided fields
    const updated: TaskResponse = await taskApi.patchTask(userId, taskId, {
      completed: true,
      // Other fields remain unchanged
    });

    console.log('Task marked complete:', updated);

  } catch (error: any) {
    console.error('Update failed:', error.message);
  }
}

/**
 * Example: Mark Task as Complete
 */
export async function exampleMarkTaskComplete(taskId: string): Promise<TaskResponse> {
  const userId = getCurrentUserId();
  if (!userId) throw new Error('Not authenticated');

  return await taskApi.patchTask(userId, taskId, { completed: true });
}

/**
 * Example: Update Task Priority
 */
export async function exampleUpdateTaskPriority(
  taskId: string,
  priority: 'low' | 'medium' | 'high' | 'critical'
): Promise<TaskResponse> {
  const userId = getCurrentUserId();
  if (!userId) throw new Error('Not authenticated');

  return await taskApi.patchTask(userId, taskId, { priority });
}

/**
 * Example: Update Task Tags
 */
export async function exampleUpdateTaskTags(
  taskId: string,
  tags: string[]
): Promise<TaskResponse> {
  const userId = getCurrentUserId();
  if (!userId) throw new Error('Not authenticated');

  return await taskApi.patchTask(userId, taskId, { tags });
}

/**
 * Example: Delete Task
 */
export async function exampleDeleteTask(taskId: string): Promise<void> {
  try {
    const userId = getCurrentUserId();
    if (!userId) return;

    const response = await taskApi.deleteTask(userId, taskId);
    console.log(response.message);

  } catch (error: any) {
    if (error.status === 404) {
      console.error('Task not found');
    } else {
      console.error('Delete failed:', error.message);
    }
  }
}

/**
 * Example: Delete Multiple Tasks
 */
export async function exampleDeleteMultipleTasks(taskIds: string[]): Promise<void> {
  const userId = getCurrentUserId();
  if (!userId) return;

  for (const taskId of taskIds) {
    try {
      await taskApi.deleteTask(userId, taskId);
      console.log(`Deleted task: ${taskId}`);
    } catch (error: any) {
      console.error(`Failed to delete ${taskId}:`, error.message);
    }
  }
}

// ===== USER PROFILE EXAMPLES =====

/**
 * Example: Get User Profile
 */
export async function exampleGetProfile(): Promise<void> {
  try {
    const userId = getCurrentUserId();
    if (!userId) return;

    const profile: UserResponse = await userApi.getProfile(userId);
    console.log('Profile:', profile);
    console.log('Member since:', new Date(profile.created_at));

  } catch (error: any) {
    if (error.status === 404) {
      console.error('User not found');
    } else {
      console.error('Failed to fetch profile:', error.message);
    }
  }
}

/**
 * Example: Update User Profile
 */
export async function exampleUpdateProfile(): Promise<void> {
  try {
    const userId = getCurrentUserId();
    if (!userId) return;

    const updated: UserResponse = await userApi.updateProfile(userId, {
      username: 'john_doe_updated',
      email: 'john.new@example.com',
    });

    console.log('Profile updated:', updated);

  } catch (error: any) {
    if (error.status === 409) {
      console.error('Email or username already in use');
    } else if (error.status === 422) {
      console.error('Validation error:', error.data);
    } else {
      console.error('Update failed:', error.message);
    }
  }
}

/**
 * Example: Update Username Only
 */
export async function exampleUpdateUsername(newUsername: string): Promise<UserResponse> {
  const userId = getCurrentUserId();
  if (!userId) throw new Error('Not authenticated');

  return await userApi.updateProfile(userId, { username: newUsername });
}

/**
 * Example: Update Email Only
 */
export async function exampleUpdateEmail(newEmail: string): Promise<UserResponse> {
  const userId = getCurrentUserId();
  if (!userId) throw new Error('Not authenticated');

  return await userApi.updateProfile(userId, { email: newEmail });
}

// ===== HELPER FUNCTION EXAMPLES =====

/**
 * Example: Using buildQueryString Helper
 */
export function exampleBuildQueryString(): void {
  // Example 1: Simple parameters
  const qs1 = buildQueryString({ limit: 20, offset: 0 });
  console.log(qs1); // "?limit=20&offset=0"

  // Example 2: With special characters
  const qs2 = buildQueryString({
    search: 'my task',
    priority: 'high',
  });
  console.log(qs2); // "?search=my+task&priority=high"

  // Example 3: Filters out undefined values
  const qs3 = buildQueryString({
    limit: 20,
    search: undefined,
    priority: 'high',
  });
  console.log(qs3); // "?limit=20&priority=high"

  // Example 4: Empty object
  const qs4 = buildQueryString({});
  console.log(qs4); // ""
}

// ===== ERROR HANDLING PATTERNS =====

/**
 * Example: Comprehensive Error Handling
 */
export async function exampleErrorHandling(): Promise<void> {
  try {
    const userId = getCurrentUserId();
    if (!userId) {
      throw new Error('User not authenticated');
    }

    await taskApi.createTask(userId, {
      title: '',
      description: '',
      priority: 'high',
      tags: [],
    });

  } catch (error: any) {
    // Handle different error types
    if (!error.status) {
      // Network error
      console.error('Network error:', error.message);
    } else if (error.status === 400) {
      // Bad request
      console.error('Bad request:', error.data);
    } else if (error.status === 401) {
      // Unauthorized - token expired
      console.error('Session expired. Please login again.');
      // Redirect to login page
    } else if (error.status === 403) {
      // Forbidden
      console.error('You do not have permission to perform this action.');
    } else if (error.status === 404) {
      // Not found
      console.error('Resource not found.');
    } else if (error.status === 409) {
      // Conflict - resource already exists
      console.error('Resource already exists:', error.data);
    } else if (error.status === 422) {
      // Validation error
      console.error('Validation failed:', error.data);
    } else if (error.status >= 500) {
      // Server error
      console.error('Server error. Please try again later.');
    } else {
      // Unknown error
      console.error('Unknown error:', error.message);
    }
  }
}

// ===== PAGINATION EXAMPLE =====

/**
 * Example: Paginating Through All Tasks
 */
export async function examplePaginateTasks(): Promise<TaskResponse[]> {
  const userId = getCurrentUserId();
  if (!userId) throw new Error('Not authenticated');

  const allTasks: TaskResponse[] = [];
  let offset = 0;
  const limit = 50;
  let hasMore = true;

  while (hasMore) {
    const result = await taskApi.getTasks(userId, { limit, offset });
    allTasks.push(...result.tasks);

    // Check if there are more tasks
    if (result.tasks.length < limit) {
      hasMore = false;
    } else {
      offset += limit;
    }
  }

  console.log(`Retrieved all ${allTasks.length} tasks`);
  return allTasks;
}

// ===== REAL-WORLD WORKFLOW EXAMPLE =====

/**
 * Example: Complete Workflow - Create, Update, Mark Complete, Delete
 */
export async function exampleCompleteWorkflow(): Promise<void> {
  const userId = getCurrentUserId();
  if (!userId) {
    console.error('Not authenticated');
    return;
  }

  try {
    // 1. Create a task
    console.log('Creating task...');
    const task = await taskApi.createTask(userId, {
      title: 'Implement feature X',
      description: 'Build and test feature X',
      priority: 'high',
      tags: ['feature', 'in-progress'],
    });
    console.log('Task created:', task.id);

    // 2. Update task details
    console.log('Updating task...');
    const updated = await taskApi.patchTask(userId, task.id, {
      description: 'Build and test feature X - includes unit tests',
      tags: ['feature', 'in-progress', 'testing'],
    });
    console.log('Task updated');

    // 3. Mark as complete
    console.log('Marking as complete...');
    const completed = await taskApi.patchTask(userId, task.id, {
      completed: true,
    });
    console.log('Task completed');

    // 4. Delete after review
    console.log('Deleting task...');
    await taskApi.deleteTask(userId, task.id);
    console.log('Task deleted');

  } catch (error: any) {
    console.error('Workflow failed:', error.message);
  }
}

// ===== LOGGING EXAMPLES =====

/**
 * Example: Development Logging (automatic)
 * These logs only appear when NODE_ENV === 'development'
 */
export async function exampleLogging(): Promise<void> {
  const userId = getCurrentUserId();
  if (!userId) return;

  // All requests are logged automatically:
  // [API] GET /api/users/123/tasks?limit=20 { headers: {...}, body: undefined }
  // [API] GET /api/users/123/tasks?limit=20 200 { tasks: [...], total: 42, ... }

  await taskApi.getTasks(userId, { limit: 20 });
}

// Export all examples for use in documentation or testing
export default {
  exampleSignup,
  exampleLogin,
  exampleLogout,
  exampleGetAllTasks,
  exampleGetTasksFiltered,
  exampleGetTasksByPriority,
  exampleSearchTasks,
  exampleGetTask,
  exampleCreateTask,
  exampleCreateMultipleTasks,
  exampleUpdateTaskFull,
  exampleUpdateTaskPartial,
  exampleMarkTaskComplete,
  exampleUpdateTaskPriority,
  exampleUpdateTaskTags,
  exampleDeleteTask,
  exampleDeleteMultipleTasks,
  exampleGetProfile,
  exampleUpdateProfile,
  exampleUpdateUsername,
  exampleUpdateEmail,
  exampleBuildQueryString,
  exampleErrorHandling,
  examplePaginateTasks,
  exampleCompleteWorkflow,
  exampleLogging,
};
