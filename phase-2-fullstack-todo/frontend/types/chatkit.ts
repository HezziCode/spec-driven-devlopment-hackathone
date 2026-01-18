/**
 * ChatKit Type Definitions for TaskWave AI Assistant
 *
 * This file defines TypeScript interfaces for ChatKit session management,
 * thread persistence, and composer tool configuration.
 */

export interface ChatSession {
  /** ChatKit client secret for session authentication */
  clientSecret: string;

  /** Session creation timestamp */
  createdAt: Date;

  /** Session expiry timestamp */
  expiresAt: Date;

  /** Current session status */
  status: 'initializing' | 'ready' | 'error' | 'expired';

  /** User ID associated with this session */
  userId: string;

  /** Error message if status is 'error' */
  error?: string;
}

export interface ChatThread {
  /** Unique thread identifier from ChatKit */
  id: string;

  /** Display name for the thread */
  name: string;

  /** Preview of the last message */
  lastMessagePreview: string | null;

  /** Timestamp of last message */
  lastUpdated: Date;

  /** Total number of messages in thread */
  messageCount: number;

  /** Whether this is the currently active thread */
  isActive: boolean;

  /** Thread creation timestamp */
  createdAt: Date;

  /** User ID who owns this thread */
  userId: string;
}

/**
 * ChatKit icon type from @openai/chatkit
 */
export type ChatKitIcon =
  | 'plus'
  | 'search'
  | 'notebook'
  | 'check'
  | 'document'
  | 'write';

export interface ComposerTool {
  /** Unique tool identifier */
  id: string;

  /** Icon name from ChatKit icon set */
  icon: ChatKitIcon;

  /** Full label shown in menu */
  label: string;

  /** Short label for compact views */
  shortLabel?: string;

  /** Custom placeholder text for composer */
  placeholderOverride?: string;
}

/**
 * Predefined composer tools for task operations
 *
 * These tools appear in the ChatKit composer menu to trigger
 * specific task management actions via natural language.
 */
export const COMPOSER_TOOLS: ComposerTool[] = [
  {
    id: 'create_task',
    icon: 'plus',
    label: 'Create Task',
    shortLabel: 'Create',
    placeholderOverride: 'What would you like to add?',
  },
  {
    id: 'search_tasks',
    icon: 'search',
    label: 'Search Tasks',
    shortLabel: 'Search',
    placeholderOverride: 'Search by title or tag...',
  },
  {
    id: 'view_tasks',
    icon: 'notebook',
    label: 'View All Tasks',
    shortLabel: 'View',
  },
];

export interface ChatUIState {
  /** Current active session */
  session: ChatSession | null;

  /** List of user's threads */
  threads: ChatThread[];

  /** Currently active thread ID */
  currentThreadId: string | null;

  /** Whether AI is currently responding */
  isResponding: boolean;

  /** Loading state for various operations */
  loading: {
    session: boolean;
    threads: boolean;
    messages: boolean;
  };

  /** Error states */
  errors: {
    session?: string;
    threads?: string;
    messages?: string;
  };

  /** Whether thread sidebar is open (mobile) */
  sidebarOpen: boolean;
}
