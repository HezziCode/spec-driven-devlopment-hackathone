/**
 * ChatKit API Client Functions
 *
 * This module provides API client functions for ChatKit session management
 * and thread persistence. All functions use JWT authentication.
 */

import { getAuthToken, getCurrentUserId } from './auth';

/**
 * Backend API base URL
 */
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Get ChatKit client secret by exchanging JWT token
 *
 * This function is called by useChatKit to initialize the session.
 * The backend verifies the JWT and returns a client_secret for ChatKit.
 *
 * @returns ChatKit client secret string
 * @throws Error if session creation fails or user is not authenticated
 */
export async function getClientSecret(): Promise<string> {
  const token = getAuthToken();

  if (!token) {
    throw new Error('Authentication required. Please sign in.');
  }

  const res = await fetch(`${API_BASE_URL}/api/chatkit/session`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ error: 'Unknown error' }));
    throw new Error(errorData.error || 'Failed to get ChatKit client secret');
  }

  const { client_secret } = await res.json();
  return client_secret;
}

/**
 * Thread metadata interface matching backend response
 */
interface ThreadMetadata {
  id: string;
  name: string;
  last_message_preview: string | null;
  message_count: number;
  created_at: string;
  updated_at: string;
}

/**
 * Fetch user's chat threads from backend
 *
 * Retrieves thread metadata for thread list display and persistence.
 *
 * @param userId - User ID to fetch threads for
 * @param limit - Maximum number of threads to return (default: 50)
 * @param offset - Offset for pagination (default: 0)
 * @returns Array of thread metadata objects
 * @throws Error if fetch fails or user is not authenticated
 */
export async function fetchThreads(
  userId: string,
  limit: number = 50,
  offset: number = 0
): Promise<ThreadMetadata[]> {
  const token = getAuthToken();

  if (!token) {
    throw new Error('Authentication required. Please sign in.');
  }

  const url = `${API_BASE_URL}/api/users/${userId}/chat/threads?limit=${limit}&offset=${offset}`;

  const res = await fetch(url, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ error: 'Unknown error' }));
    throw new Error(errorData.error || 'Failed to fetch threads');
  }

  const { threads } = await res.json();
  return threads;
}

/**
 * Thread sync request data
 */
interface ThreadSyncData {
  thread_id: string;
  name: string;
  last_message_preview: string | null;
  message_count: number;
}

/**
 * Sync thread metadata to backend for persistence
 *
 * This function is called when thread changes occur to persist
 * metadata to the backend. It's debounced on the client side.
 *
 * @param userId - User ID who owns the thread
 * @param threadData - Thread metadata to sync
 * @throws Error if sync fails or user is not authenticated
 */
export async function syncThread(userId: string, threadData: ThreadSyncData): Promise<void> {
  const token = getAuthToken();

  if (!token) {
    throw new Error('Authentication required. Please sign in.');
  }

  const url = `${API_BASE_URL}/api/users/${userId}/chat/threads/${threadData.thread_id}/sync`;

  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(threadData),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ error: 'Unknown error' }));
    throw new Error(errorData.error || 'Failed to sync thread');
  }
}

/**
 * Delete a chat thread
 *
 * Removes thread metadata from backend storage. The actual ChatKit
 * thread may still exist in OpenAI's system.
 *
 * @param userId - User ID who owns the thread
 * @param threadId - Thread ID to delete
 * @throws Error if deletion fails or user is not authenticated
 */
export async function deleteThread(userId: string, threadId: string): Promise<void> {
  const token = getAuthToken();

  if (!token) {
    throw new Error('Authentication required. Please sign in.');
  }

  const url = `${API_BASE_URL}/api/users/${userId}/chat/threads/${threadId}`;

  const res = await fetch(url, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ error: 'Unknown error' }));
    throw new Error(errorData.error || 'Failed to delete thread');
  }
}

/**
 * Get current authenticated user ID
 *
 * Helper function to get user ID for API calls.
 *
 * @returns User ID or null if not authenticated
 */
export function getAuthenticatedUserId(): string | null {
  return null; // TODO: Implement based on actual auth module exports
}
