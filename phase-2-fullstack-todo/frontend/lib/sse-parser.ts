/**
 * SSE Parser Utility
 *
 * Parses Server-Sent Events (SSE) streams and extracts clean text content
 * while filtering out protocol artifacts (data:, event:, thread_id, etc.)
 *
 * @module sse-parser
 */

import type {
  RawSSEEvent,
  ParsedSSEChunk,
  SSEMetadata,
  SSEEventType,
  SSEParseResult,
  ParserError,
} from '@/types/sse';

/**
 * Parse a single SSE protocol line
 *
 * @param line - Raw SSE line (e.g., "data: Hello" or "event: done")
 * @returns Parsed field and value, or null if invalid
 */
export function parseSSELine(line: string): { field: string; value: string } | null {
  if (!line || line.trim() === '') {
    return null;
  }

  // Comments start with ':'
  if (line.startsWith(':')) {
    return null;
  }

  const colonIndex = line.indexOf(':');
  if (colonIndex === -1) {
    return null;
  }

  const field = line.substring(0, colonIndex).trim();
  let value = line.substring(colonIndex + 1);

  // Remove leading space after colon (SSE spec)
  if (value.startsWith(' ')) {
    value = value.substring(1);
  }

  return { field, value };
}

/**
 * Parse a complete SSE event from accumulated lines
 *
 * @param lines - Array of SSE lines for a single event
 * @returns Parsed RawSSEEvent object
 */
export function parseSSEEvent(lines: string[]): RawSSEEvent | null {
  const event: Partial<RawSSEEvent> = {
    data: '',
  };

  for (const line of lines) {
    const parsed = parseSSELine(line);
    if (!parsed) continue;

    const { field, value } = parsed;

    switch (field) {
      case 'data':
        // Multiple data lines are concatenated with newlines
        if (event.data) {
          event.data += '\n' + value;
        } else {
          event.data = value;
        }
        break;
      case 'event':
        event.event = value;
        break;
      case 'id':
        event.id = value;
        break;
      case 'retry':
        event.retry = parseInt(value, 10);
        break;
    }
  }

  // Event must have data
  if (!event.data) {
    return null;
  }

  return event as RawSSEEvent;
}

/**
 * Extract clean text content from SSE data field
 *
 * Handles both plain text and JSON-formatted data.
 * For JSON data, extracts text from common fields (delta, content, text).
 *
 * @param data - Raw data field from SSE event
 * @returns Clean text content without protocol artifacts
 */
export function extractTextContent(data: string): string {
  if (!data) {
    return '';
  }

  // Try parsing as JSON first (for structured events)
  try {
    const parsed = JSON.parse(data);

    // OpenAI Agents SDK format: { delta: "text" }
    if (typeof parsed.delta === 'string') {
      return parsed.delta;
    }

    // Alternative formats
    if (typeof parsed.content === 'string') {
      return parsed.content;
    }

    if (typeof parsed.text === 'string') {
      return parsed.text;
    }

    // If JSON but no text field, return empty
    return '';
  } catch {
    // Plain text data - return as is
    return data;
  }
}

/**
 * Extract metadata from SSE data field
 *
 * Separates metadata (thread_id, message_id, etc.) from content
 * so it's not displayed to users.
 *
 * @param data - Raw data field from SSE event
 * @returns Metadata object or undefined if no metadata
 */
export function filterMetadata(data: string): SSEMetadata | undefined {
  if (!data) {
    return undefined;
  }

  try {
    const parsed = JSON.parse(data);

    const metadata: SSEMetadata = {};
    let hasMetadata = false;

    // Extract common metadata fields
    if (parsed.thread_id || parsed.threadId) {
      metadata.threadId = parsed.thread_id || parsed.threadId;
      hasMetadata = true;
    }

    if (parsed.message_id || parsed.messageId) {
      metadata.messageId = parsed.message_id || parsed.messageId;
      hasMetadata = true;
    }

    if (parsed.timestamp) {
      metadata.timestamp = parsed.timestamp;
      hasMetadata = true;
    }

    if (parsed.tool_calls || parsed.toolCalls) {
      metadata.toolCalls = parsed.tool_calls || parsed.toolCalls;
      hasMetadata = true;
    }

    return hasMetadata ? metadata : undefined;
  } catch {
    // Plain text data has no metadata
    return undefined;
  }
}

/**
 * Parse SSE stream and extract clean text chunks
 *
 * Main parsing function that processes raw SSE data and returns
 * clean text content with metadata separated.
 *
 * @param rawData - Raw SSE stream data
 * @returns Array of parsed chunks with clean content
 */
export function parseSSEStream(rawData: string): ParsedSSEChunk[] {
  if (!rawData) {
    return [];
  }

  const chunks: ParsedSSEChunk[] = [];
  // Handle both \r\n (Windows) and \n (Unix) line endings
  const lines = rawData.split(/\r?\n/);
  let currentEventLines: string[] = [];

  for (const line of lines) {
    // Empty line signals end of event
    if (line.trim() === '') {
      if (currentEventLines.length > 0) {
        const event = parseSSEEvent(currentEventLines);
        if (event) {
          const chunk = parseEvent(event);
          if (chunk) {
            chunks.push(chunk);
          }
        }
        currentEventLines = [];
      }
    } else {
      currentEventLines.push(line);
    }
  }

  // Handle any remaining lines (incomplete event)
  if (currentEventLines.length > 0) {
    const event = parseSSEEvent(currentEventLines);
    if (event) {
      const chunk = parseEvent(event);
      if (chunk) {
        chunks.push(chunk);
      }
    }
  }

  return chunks;
}

/**
 * Parse a single SSE event into a clean chunk
 *
 * Internal helper function that converts RawSSEEvent to ParsedSSEChunk.
 *
 * @param event - Raw SSE event
 * @returns Parsed chunk with clean content and metadata
 */
function parseEvent(event: RawSSEEvent): ParsedSSEChunk | null {
  // Extract clean text content
  const content = extractTextContent(event.data);

  // Extract metadata (not displayed to users)
  const metadata = filterMetadata(event.data);

  // Determine if event signals completion
  const isComplete = event.event === 'done' || event.event === 'complete';

  // Determine event type
  const eventType: SSEEventType = (event.event as SSEEventType) || 'message';

  // For thread_created events, ensure we mark them as complete
  if (event.event === 'thread_created') {
    return {
      content: '',  // No visible content for thread_created events
      isComplete: true,  // Mark as complete so metadata is processed
      eventType: 'thread_created',
      metadata,
    };
  }

  return {
    content,
    isComplete,
    eventType,
    metadata,
  };
}

/**
 * Parse SSE stream with error handling
 *
 * Enhanced version that catches parsing errors and returns them
 * along with successfully parsed chunks.
 *
 * @param rawData - Raw SSE stream data
 * @returns Parse result with chunks and errors
 */
export function parseSSEStreamSafe(rawData: string): SSEParseResult {
  const result: SSEParseResult = {
    chunks: [],
    errors: [],
    isComplete: false,
  };

  try {
    result.chunks = parseSSEStream(rawData);

    // Check if any chunk signals completion
    result.isComplete = result.chunks.some(chunk => chunk.isComplete);
  } catch (error) {
    const parserError: ParserError = {
      message: error instanceof Error ? error.message : 'Unknown parsing error',
      rawEvent: rawData.substring(0, 100), // First 100 chars for debugging
      type: 'parse',
    };
    result.errors.push(parserError);
  }

  return result;
}

/**
 * Combine multiple data lines with proper spacing
 *
 * Helper function to handle multi-line SSE data fields.
 * Ensures proper word spacing when combining lines.
 *
 * @param lines - Array of data line values
 * @returns Combined text with proper spacing
 */
export function combineDataLines(lines: string[]): string {
  return lines
    .map(line => line.trim())
    .filter(line => line.length > 0)
    .join(' ');
}

/**
 * Validate SSE event format
 *
 * Checks if an event follows the SSE protocol specification.
 *
 * @param event - Event to validate
 * @returns True if valid, false otherwise
 */
export function isValidSSEEvent(event: RawSSEEvent): boolean {
  // Must have data field
  if (!event.data || typeof event.data !== 'string') {
    return false;
  }

  // Event type must be valid if present
  if (event.event && typeof event.event !== 'string') {
    return false;
  }

  // ID must be string if present
  if (event.id !== undefined && typeof event.id !== 'string') {
    return false;
  }

  // Retry must be number if present
  if (event.retry !== undefined && typeof event.retry !== 'number') {
    return false;
  }

  return true;
}
