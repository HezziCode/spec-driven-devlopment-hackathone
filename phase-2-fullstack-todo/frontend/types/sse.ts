/**
 * SSE Event Type Contracts
 *
 * TypeScript type definitions for Server-Sent Events (SSE) parsing
 * and chat message display in the frontend.
 *
 * @module sse-events
 * @see ../specs/018-fix-chat-sse-parsing/data-model.md for detailed documentation
 */

// ============================================================================
// SSE Protocol Layer
// ============================================================================

/**
 * Raw SSE event structure following the Server-Sent Events protocol
 * @see https://html.spec.whatwg.org/multipage/server-sent-events.html
 */
export interface RawSSEEvent {
  /** Event type (e.g., 'message', 'error', 'done') */
  event?: string;

  /** Event data payload (may contain multiple lines) */
  data: string;

  /** Optional event ID for reconnection */
  id?: string;

  /** Retry interval in milliseconds */
  retry?: number;
}

/**
 * SSE event types
 */
export type SSEEventType =
  | 'message'           // Regular message content
  | 'delta'             // Text delta (streaming chunk)
  | 'done'              // Stream completion
  | 'error'             // Error event
  | 'ping'              // Keep-alive ping
  | 'thread_created'    // New thread created
  | 'complete';         // Alternative completion marker

/**
 * Metadata extracted from SSE events (not displayed to users)
 */
export interface SSEMetadata {
  /** Thread/conversation identifier */
  threadId?: string;

  /** Message identifier */
  messageId?: string;

  /** Tool calls or function invocations */
  toolCalls?: ToolCall[];

  /** Timestamp of the event */
  timestamp?: string;

  /** Any other metadata fields */
  [key: string]: unknown;
}

/**
 * Tool call information from agent responses
 */
export interface ToolCall {
  id: string;
  name: string;
  arguments: Record<string, unknown>;
}

/**
 * Parsed SSE chunk with clean content and separated metadata
 */
export interface ParsedSSEChunk {
  /** Clean text content without protocol artifacts */
  content: string;

  /** Whether this chunk completes the current message */
  isComplete: boolean;

  /** Event type from SSE protocol */
  eventType?: SSEEventType;

  /** Optional metadata that should not be displayed */
  metadata?: SSEMetadata;
}

// ============================================================================
// Message Display Layer
// ============================================================================

/**
 * Chat message for display in the UI
 */
export interface ChatMessage {
  /** Unique message identifier */
  id: string;

  /** Message sender role */
  role: 'user' | 'assistant' | 'system';

  /** Clean message content (no protocol artifacts) */
  content: string;

  /** Message timestamp */
  timestamp: Date;

  /** Whether message is currently streaming */
  isStreaming?: boolean;

  /** Error information if message failed */
  error?: MessageError;
}

/**
 * Error information for failed messages
 */
export interface MessageError {
  /** Error message for display */
  message: string;

  /** Error code for debugging */
  code?: string;

  /** Whether error is recoverable */
  recoverable: boolean;
}

/**
 * State of a streaming message
 */
export interface StreamingState {
  /** Whether stream is currently active */
  isActive: boolean;

  /** Accumulated content so far */
  accumulatedContent: string;

  /** Message being streamed */
  messageId: string;

  /** Error if stream failed */
  error?: MessageError;
}

// ============================================================================
// SSE Parser Configuration
// ============================================================================

/**
 * Handler function for specific SSE event types
 */
export type SSEEventHandler = (event: RawSSEEvent) => ParsedSSEChunk | null;

/**
 * Configuration for SSE parser behavior
 */
export interface SSEParserConfig {
  /** Whether to include metadata in parsed chunks */
  includeMetadata?: boolean;

  /** Custom event type handlers */
  eventHandlers?: Record<string, SSEEventHandler>;

  /** Whether to auto-reconnect on connection loss */
  autoReconnect?: boolean;

  /** Reconnection delay in milliseconds */
  reconnectDelay?: number;

  /** Maximum reconnection attempts */
  maxReconnectAttempts?: number;
}

/**
 * Error encountered during SSE parsing
 */
export interface ParserError {
  /** Error message */
  message: string;

  /** Raw event that caused the error */
  rawEvent?: string;

  /** Error type */
  type: 'parse' | 'network' | 'protocol';
}

/**
 * Result of SSE parsing operation
 */
export interface SSEParseResult {
  /** Successfully parsed chunks */
  chunks: ParsedSSEChunk[];

  /** Any errors encountered during parsing */
  errors: ParserError[];

  /** Whether stream is complete */
  isComplete: boolean;
}

// ============================================================================
// OpenAI Agents SDK Event Types
// ============================================================================

/**
 * Text delta event data
 */
export interface TextDeltaData {
  /** Text content delta */
  delta: string;

  /** Optional message ID */
  messageId?: string;
}

/**
 * Stream completion event data
 */
export interface DoneData {
  /** Thread/conversation ID */
  threadId: string;

  /** Final message ID */
  messageId: string;

  /** Completion reason */
  reason?: 'stop' | 'length' | 'error';
}

/**
 * Error event data
 */
export interface ErrorData {
  /** Error message */
  error: string;

  /** Error code */
  code?: string;
}

/**
 * Agent event data payload
 */
export type AgentEventData =
  | TextDeltaData
  | DoneData
  | ErrorData;

/**
 * OpenAI Agent response event (from backend)
 */
export interface AgentResponseEvent {
  /** Event type */
  type: 'response.text.delta' | 'response.done' | 'response.error';

  /** Event data */
  data: AgentEventData;
}

// ============================================================================
// Stream State Types
// ============================================================================

/**
 * Connection state for SSE stream
 */
export type ConnectionState =
  | 'idle'
  | 'connecting'
  | 'connected'
  | 'streaming'
  | 'complete'
  | 'error'
  | 'reconnecting'
  | 'failed';

/**
 * SSE connection info
 */
export interface SSEConnectionInfo {
  /** Current connection state */
  state: ConnectionState;

  /** Number of reconnection attempts */
  reconnectAttempts: number;

  /** Last error if any */
  lastError?: ParserError;

  /** Connection start time */
  connectedAt?: Date;
}

// ============================================================================
// Utility Types
// ============================================================================

/**
 * Type guard to check if data is TextDeltaData
 */
export function isTextDeltaData(data: AgentEventData): data is TextDeltaData {
  return 'delta' in data;
}

/**
 * Type guard to check if data is DoneData
 */
export function isDoneData(data: AgentEventData): data is DoneData {
  return 'threadId' in data && 'messageId' in data;
}

/**
 * Type guard to check if data is ErrorData
 */
export function isErrorData(data: AgentEventData): data is ErrorData {
  return 'error' in data;
}

// ============================================================================
// Constants
// ============================================================================

/**
 * Default SSE parser configuration
 */
export const DEFAULT_SSE_CONFIG: Required<SSEParserConfig> = {
  includeMetadata: false,
  eventHandlers: {},
  autoReconnect: true,
  reconnectDelay: 1000,
  maxReconnectAttempts: 3,
};

/**
 * SSE protocol field names
 */
export const SSE_FIELDS = {
  DATA: 'data',
  EVENT: 'event',
  ID: 'id',
  RETRY: 'retry',
  COMMENT: ':',
} as const;

/**
 * Common SSE event types
 */
export const SSE_EVENT_TYPES = {
  MESSAGE: 'message',
  DELTA: 'delta',
  DONE: 'done',
  ERROR: 'error',
  PING: 'ping',
  THREAD_CREATED: 'thread_created',
  COMPLETE: 'complete',
} as const;
