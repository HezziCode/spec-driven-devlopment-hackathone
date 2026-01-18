# Quick Start Guide: SSE Parsing Implementation

**Feature**: Fix Chat SSE Parsing
**Date**: 2026-01-05
**Audience**: Developers implementing the SSE parsing fix

## Overview

This guide provides a quick reference for implementing the SSE parsing fix in the chat interface. For detailed information, see [plan.md](./plan.md) and [data-model.md](./data-model.md).

## Problem Summary

**Current Behavior**: Chat displays raw SSE data with protocol artifacts
```
data: Hidata:  theredata: !event: donedata: {"thread_id": "abc123"}
```

**Expected Behavior**: Clean, readable text
```
Hi there!
```

## Solution Architecture

```
Backend SSE Stream → Fetch API → SSE Parser → Clean Text → React Component → User Display
```

## Implementation Checklist

### Phase 1: Core SSE Parser (TDD)

- [ ] Create `frontend/types/sse.ts` with type definitions
- [ ] Create `frontend/lib/sse-parser.ts` with parsing functions
- [ ] Write unit tests for SSE parser
- [ ] Implement `parseSSELine()` - Parse single SSE line
- [ ] Implement `parseSSEEvent()` - Parse complete SSE event
- [ ] Implement `extractTextContent()` - Extract clean text from data field
- [ ] Implement `filterMetadata()` - Separate metadata from content

### Phase 2: Custom Hook (TDD)

- [ ] Create `frontend/hooks/useSSEStream.ts`
- [ ] Write tests for hook behavior
- [ ] Implement connection management
- [ ] Implement stream reading with ReadableStream
- [ ] Implement progressive text accumulation
- [ ] Implement error handling and reconnection
- [ ] Implement cleanup on unmount

### Phase 3: Component Updates (TDD)

- [ ] Create `frontend/components/MessageDisplay.tsx`
- [ ] Update `frontend/components/ChatInterface.tsx`
- [ ] Update `frontend/components/CustomChatInterface.tsx` (if needed)
- [ ] Write component integration tests
- [ ] Test with real backend SSE endpoint

### Phase 4: Testing & Validation

- [ ] Test with various message types
- [ ] Test with special characters and emojis
- [ ] Test with long messages
- [ ] Test error scenarios (network failure, timeout)
- [ ] Test browser compatibility
- [ ] Verify accessibility with screen readers

## Key Code Patterns

### 1. SSE Parser Utility

```typescript
// frontend/lib/sse-parser.ts

/**
 * Parse SSE stream and extract clean text content
 */
export function parseSSEStream(rawData: string): ParsedSSEChunk[] {
  const lines = rawData.split('\n');
  const chunks: ParsedSSEChunk[] = [];
  let currentEvent: Partial<RawSSEEvent> = {};

  for (const line of lines) {
    if (line.startsWith('data:')) {
      const data = line.substring(5).trim();
      currentEvent.data = (currentEvent.data || '') + data;
    } else if (line.startsWith('event:')) {
      currentEvent.event = line.substring(6).trim();
    } else if (line === '') {
      // Empty line signals end of event
      if (currentEvent.data) {
        chunks.push(parseEvent(currentEvent as RawSSEEvent));
        currentEvent = {};
      }
    }
  }

  return chunks;
}

/**
 * Parse single SSE event into clean chunk
 */
function parseEvent(event: RawSSEEvent): ParsedSSEChunk {
  // Extract clean text content
  const content = extractTextContent(event.data);

  // Extract metadata (thread_id, etc.)
  const metadata = extractMetadata(event.data);

  // Determine if event signals completion
  const isComplete = event.event === 'done';

  return {
    content,
    isComplete,
    eventType: event.event as SSEEventType,
    metadata,
  };
}

/**
 * Extract clean text from data field
 */
function extractTextContent(data: string): string {
  try {
    // Try parsing as JSON (for structured events)
    const parsed = JSON.parse(data);
    if (parsed.delta) return parsed.delta;
    if (parsed.content) return parsed.content;
    if (parsed.text) return parsed.text;
    return '';
  } catch {
    // Plain text data
    return data;
  }
}

/**
 * Extract metadata from data field
 */
function extractMetadata(data: string): SSEMetadata | undefined {
  try {
    const parsed = JSON.parse(data);
    return {
      threadId: parsed.thread_id,
      messageId: parsed.message_id,
      // Extract other metadata fields
    };
  } catch {
    return undefined;
  }
}
```

### 2. Custom SSE Stream Hook

```typescript
// frontend/hooks/useSSEStream.ts

import { useState, useEffect, useCallback } from 'react';
import { parseSSEStream } from '@/lib/sse-parser';
import type { ChatMessage, StreamingState } from '@/types/sse';

export function useSSEStream(url: string, enabled: boolean = true) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [streaming, setStreaming] = useState<StreamingState | null>(null);
  const [error, setError] = useState<Error | null>(null);

  const startStream = useCallback(async () => {
    if (!enabled) return;

    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Accept': 'text/event-stream',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No response body');
      }

      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();

        if (done) break;

        // Decode chunk and add to buffer
        buffer += decoder.decode(value, { stream: true });

        // Parse complete events from buffer
        const chunks = parseSSEStream(buffer);

        for (const chunk of chunks) {
          if (chunk.content) {
            // Update streaming state with new content
            setStreaming(prev => ({
              isActive: !chunk.isComplete,
              accumulatedContent: (prev?.accumulatedContent || '') + chunk.content,
              messageId: chunk.metadata?.messageId || prev?.messageId || '',
            }));
          }

          if (chunk.isComplete) {
            // Finalize message
            setMessages(prev => [...prev, {
              id: chunk.metadata?.messageId || Date.now().toString(),
              role: 'assistant',
              content: streaming?.accumulatedContent || '',
              timestamp: new Date(),
              isStreaming: false,
            }]);
            setStreaming(null);
          }
        }

        // Clear processed events from buffer
        buffer = '';
      }
    } catch (err) {
      setError(err as Error);
      setStreaming(null);
    }
  }, [url, enabled, streaming?.accumulatedContent]);

  useEffect(() => {
    startStream();
  }, [startStream]);

  return {
    messages,
    streaming,
    error,
    isStreaming: streaming?.isActive || false,
  };
}
```

### 3. Updated Chat Component

```typescript
// frontend/components/ChatInterface.tsx

import { useSSEStream } from '@/hooks/useSSEStream';
import { MessageDisplay } from './MessageDisplay';

export function ChatInterface() {
  const [input, setInput] = useState('');
  const { messages, streaming, isStreaming } = useSSEStream('/api/chat/stream');

  return (
    <div className="chat-interface">
      <div className="messages">
        {messages.map(msg => (
          <MessageDisplay key={msg.id} message={msg} />
        ))}
        {streaming && (
          <MessageDisplay
            message={{
              id: 'streaming',
              role: 'assistant',
              content: streaming.accumulatedContent,
              timestamp: new Date(),
              isStreaming: true,
            }}
          />
        )}
      </div>
      <input
        value={input}
        onChange={e => setInput(e.target.value)}
        disabled={isStreaming}
      />
    </div>
  );
}
```

### 4. Message Display Component

```typescript
// frontend/components/MessageDisplay.tsx

import type { ChatMessage } from '@/types/sse';

interface MessageDisplayProps {
  message: ChatMessage;
}

export function MessageDisplay({ message }: MessageDisplayProps) {
  return (
    <div className={`message message-${message.role}`}>
      <div className="message-content">
        {message.content}
        {message.isStreaming && <span className="cursor">▊</span>}
      </div>
      {message.error && (
        <div className="message-error">{message.error.message}</div>
      )}
    </div>
  );
}
```

## Testing Strategy

### Unit Tests

```typescript
// frontend/__tests__/lib/sse-parser.test.ts

describe('parseSSEStream', () => {
  it('should parse simple text event', () => {
    const raw = 'data: Hello world\n\n';
    const chunks = parseSSEStream(raw);

    expect(chunks).toHaveLength(1);
    expect(chunks[0].content).toBe('Hello world');
  });

  it('should remove protocol artifacts', () => {
    const raw = 'data: Hello\nevent: done\ndata: {"thread_id": "123"}\n\n';
    const chunks = parseSSEStream(raw);

    expect(chunks[0].content).not.toContain('data:');
    expect(chunks[0].content).not.toContain('event:');
    expect(chunks[0].content).not.toContain('thread_id');
  });

  it('should handle multi-line data', () => {
    const raw = 'data: Hello\ndata:  world\n\n';
    const chunks = parseSSEStream(raw);

    expect(chunks[0].content).toBe('Hello world');
  });
});
```

### Integration Tests

```typescript
// frontend/__tests__/components/ChatInterface.test.tsx

describe('ChatInterface', () => {
  it('should display clean text from SSE stream', async () => {
    const { getByText } = render(<ChatInterface />);

    // Simulate SSE stream
    mockSSEStream('data: Hello\n\ndata: world\n\n');

    await waitFor(() => {
      expect(getByText('Hello world')).toBeInTheDocument();
    });
  });

  it('should not display protocol artifacts', async () => {
    const { queryByText } = render(<ChatInterface />);

    mockSSEStream('data: Test\nevent: done\n\n');

    await waitFor(() => {
      expect(queryByText(/data:/)).not.toBeInTheDocument();
      expect(queryByText(/event:/)).not.toBeInTheDocument();
    });
  });
});
```

## Common Issues & Solutions

### Issue 1: Concatenated Words

**Problem**: Words appear concatenated like "Hidata:theredata:"

**Solution**: Properly parse multi-line data fields and preserve spacing
```typescript
// Combine multiple data lines with space
const dataLines = event.data.split('\n');
const combined = dataLines.join(' ');
```

### Issue 2: Metadata Visible to Users

**Problem**: Thread IDs and other metadata appear in chat

**Solution**: Separate metadata extraction from content extraction
```typescript
// Extract metadata separately
const metadata = extractMetadata(data);
// Only return clean content for display
return { content: cleanText, metadata };
```

### Issue 3: Streaming Stops Working

**Problem**: Messages don't appear progressively

**Solution**: Ensure buffer is processed incrementally
```typescript
// Process buffer as chunks arrive, don't wait for complete message
while (true) {
  const { done, value } = await reader.read();
  buffer += decoder.decode(value, { stream: true });
  processBuffer(buffer); // Process immediately
}
```

## Performance Considerations

1. **Minimize Re-renders**: Use `useMemo` for parsed chunks
2. **Efficient String Operations**: Avoid repeated string concatenation
3. **Buffer Management**: Clear processed events from buffer
4. **Debounce Updates**: For very fast streams, debounce UI updates

## Browser Compatibility

- ✅ Chrome 52+
- ✅ Firefox 65+
- ✅ Safari 10.1+
- ✅ Edge 79+

All modern browsers support `fetch` with `ReadableStream`.

## Next Steps

1. Review [plan.md](./plan.md) for complete implementation strategy
2. Review [data-model.md](./data-model.md) for type definitions
3. Run `/sp.tasks` to generate detailed task breakdown
4. Begin TDD implementation with `/sp.implement`

## References

- [SSE Specification](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- [MDN: Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [OpenAI Agents SDK Streaming](https://github.com/openai/openai-agents-python/blob/main/docs/streaming.md)
- [Next.js Streaming](https://nextjs.org/docs/app/building-your-application/routing/loading-ui-and-streaming)
