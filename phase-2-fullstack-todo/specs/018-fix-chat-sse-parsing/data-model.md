# Data Model: SSE Event Types and Message Structures

**Feature**: Fix Chat SSE Parsing
**Date**: 2026-01-05
**Purpose**: Define TypeScript types and interfaces for SSE event parsing and message display

## Overview

This document defines the data structures used for parsing Server-Sent Events (SSE) streams and displaying clean chat messages. The model separates protocol-level SSE events from user-facing message display.

## SSE Protocol Layer

### Raw SSE Event

Represents a single SSE event as received from the server following the SSE protocol specification.

```typescript
/**
 * Raw SSE event structure following the Server-Sent Events protocol
 * @see https://html.spec.whatwg.org/multipage/server-sent-events.html
 */
interface RawSSEEvent {
  /** Event type (e.g., 'message', 'error', 'done') */
  event?: string;

  /** Event data payload (may contain multiple lines) */
  data: string;

  /** Optional event ID for reconnection */
  id?: string;

  /** Retry interval in milliseconds */
  retry?: number;
}
```

### Parsed SSE Chunk

Represents a processed SSE event with extracted content and metadata separated.

```typescript
/**
 * Parsed SSE chunk with clean content and separated metadata
 */
interface ParsedSSEChunk {
  /** Clean text content without protocol artifacts */
  content: string;

  /** Whether this chunk completes the current message */
  isComplete: boolean;

  /** Event type from SSE protocol */
  eventType?: SSEEventType;

  /** Optional metadata that should not be displayed */
  metadata?: SSEMetadata;
}

/**
 * SSE event types
 */
type SSEEventType =
  | 'message'      // Regular message content
  | 'delta'        // Text delta (streaming chunk)
  | 'done'         // Stream completion
  | 'error'        // Error event
  | 'ping';        // Keep-alive ping

/**
 * Metadata extracted from SSE events (not displayed to users)
 */
interface SSEMetadata {
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
interface ToolCall {
  id: string;
  name: string;
  arguments: Record<string, unknown>;
}
```

## Message Display Layer

### Chat Message

Represents a complete message in the chat interface.

```typescript
/**
 * Chat message for display in the UI
 */
interface ChatMessage {
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
interface MessageError {
  /** Error message for display */
  message: string;

  /** Error code for debugging */
  code?: string;

  /** Whether error is recoverable */
  recoverable: boolean;
}
```

### Streaming State

Represents the current state of a streaming message.

```typescript
/**
 * State of a streaming message
 */
interface StreamingState {
  /** Whether stream is currently active */
  isActive: boolean;

  /** Accumulated content so far */
  accumulatedContent: string;

  /** Message being streamed */
  messageId: string;

  /** Error if stream failed */
  error?: MessageError;
}
```

## SSE Parser Types

### Parser Configuration

Configuration options for the SSE parser.

```typescript
/**
 * Configuration for SSE parser behavior
 */
interface SSEParserConfig {
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
 * Handler function for specific SSE event types
 */
type SSEEventHandler = (event: RawSSEEvent) => ParsedSSEChunk | null;
```

### Parser Result

Result of parsing an SSE stream.

```typescript
/**
 * Result of SSE parsing operation
 */
interface SSEParseResult {
  /** Successfully parsed chunks */
  chunks: ParsedSSEChunk[];

  /** Any errors encountered during parsing */
  errors: ParserError[];

  /** Whether stream is complete */
  isComplete: boolean;
}

/**
 * Error encountered during SSE parsing
 */
interface ParserError {
  /** Error message */
  message: string;

  /** Raw event that caused the error */
  rawEvent?: string;

  /** Error type */
  type: 'parse' | 'network' | 'protocol';
}
```

## OpenAI Agents SDK Event Types

### Agent Response Events

Types specific to OpenAI Agents SDK streaming responses.

```typescript
/**
 * OpenAI Agent response event (from backend)
 */
interface AgentResponseEvent {
  /** Event type */
  type: 'response.text.delta' | 'response.done' | 'response.error';

  /** Event data */
  data: AgentEventData;
}

/**
 * Agent event data payload
 */
type AgentEventData =
  | TextDeltaData
  | DoneData
  | ErrorData;

/**
 * Text delta event data
 */
interface TextDeltaData {
  /** Text content delta */
  delta: string;

  /** Optional message ID */
  messageId?: string;
}

/**
 * Stream completion event data
 */
interface DoneData {
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
interface ErrorData {
  /** Error message */
  error: string;

  /** Error code */
  code?: string;
}
```

## Validation Rules

### Content Validation

Rules for validating parsed content:

1. **Content must not contain protocol artifacts**:
   - No "data:" prefixes
   - No "event:" markers
   - No "id:" fields
   - No thread_id or metadata in display text

2. **Content must preserve semantic meaning**:
   - Word spacing must be correct
   - Special characters and emojis preserved
   - Unicode content handled correctly

3. **Streaming content must be progressive**:
   - Each chunk appends to previous content
   - No duplicate content
   - No missing chunks

### Event Validation

Rules for validating SSE events:

1. **Event format must follow SSE protocol**:
   - Events separated by double newlines
   - Field format: `field: value\n`
   - Multi-line data fields supported

2. **Event types must be recognized**:
   - Unknown event types logged but not rejected
   - Default to 'message' type if not specified

3. **Metadata must be separated from content**:
   - Thread IDs extracted to metadata
   - Tool calls extracted to metadata
   - Only text content in display field

## State Transitions

### Message Streaming States

```
IDLE → CONNECTING → STREAMING → COMPLETE
                  ↓
                ERROR → RECONNECTING → STREAMING
                  ↓
                FAILED
```

**State Descriptions**:
- **IDLE**: No active stream
- **CONNECTING**: Establishing SSE connection
- **STREAMING**: Receiving and displaying chunks
- **COMPLETE**: Stream finished successfully
- **ERROR**: Temporary error occurred
- **RECONNECTING**: Attempting to reconnect
- **FAILED**: Permanent failure, no retry

## Usage Examples

### Parsing SSE Event

```typescript
// Raw SSE data from server
const rawData = "data: Hello\ndata:  there!\nevent: done\ndata: {\"thread_id\": \"abc123\"}\n\n";

// Parse into clean chunks
const result = parseSSEStream(rawData);

// result.chunks[0]
{
  content: "Hello there!",
  isComplete: true,
  eventType: "done",
  metadata: {
    threadId: "abc123"
  }
}
```

### Displaying Chat Message

```typescript
// Create chat message from parsed chunk
const message: ChatMessage = {
  id: generateId(),
  role: 'assistant',
  content: chunk.content, // "Hello there!" (clean text)
  timestamp: new Date(),
  isStreaming: !chunk.isComplete
};

// Display in UI - no protocol artifacts visible
```

## Type Exports

All types should be exported from `frontend/types/sse.ts`:

```typescript
export type {
  RawSSEEvent,
  ParsedSSEChunk,
  SSEEventType,
  SSEMetadata,
  ToolCall,
  ChatMessage,
  MessageError,
  StreamingState,
  SSEParserConfig,
  SSEEventHandler,
  SSEParseResult,
  ParserError,
  AgentResponseEvent,
  AgentEventData,
  TextDeltaData,
  DoneData,
  ErrorData
};
```

## Notes

- All types use TypeScript strict mode
- No `any` types allowed
- All optional fields explicitly marked with `?`
- Metadata is always optional and never displayed to users
- Content field always contains clean, display-ready text
