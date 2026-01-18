/**
 * Unit Tests for SSE Parser
 *
 * Tests for Server-Sent Events parsing utility functions
 * Validates clean text extraction and protocol artifact filtering
 */

import {
  parseSSELine,
  parseSSEEvent,
  extractTextContent,
  filterMetadata,
  parseSSEStream,
  parseSSEStreamSafe,
  combineDataLines,
  isValidSSEEvent,
} from '@/lib/sse-parser';
import type { RawSSEEvent, ParsedSSEChunk } from '@/types/sse';

describe('SSE Parser', () => {
  describe('parseSSELine', () => {
    it('should parse valid SSE line with data field', () => {
      const result = parseSSELine('data: Hello World');
      expect(result).toEqual({ field: 'data', value: 'Hello World' });
    });

    it('should parse valid SSE line with event field', () => {
      const result = parseSSELine('event: done');
      expect(result).toEqual({ field: 'event', value: 'done' });
    });

    it('should remove leading space after colon per SSE spec', () => {
      const result = parseSSELine('data: test');
      expect(result).toEqual({ field: 'data', value: 'test' });
    });

    it('should handle line without leading space after colon', () => {
      const result = parseSSELine('data:test');
      expect(result).toEqual({ field: 'data', value: 'test' });
    });

    it('should return null for empty line', () => {
      expect(parseSSELine('')).toBeNull();
      expect(parseSSELine('   ')).toBeNull();
    });

    it('should return null for comment line starting with colon', () => {
      expect(parseSSELine(': this is a comment')).toBeNull();
    });

    it('should return null for line without colon', () => {
      expect(parseSSELine('invalid line')).toBeNull();
    });

    it('should handle id field', () => {
      const result = parseSSELine('id: 123');
      expect(result).toEqual({ field: 'id', value: '123' });
    });

    it('should handle retry field', () => {
      const result = parseSSELine('retry: 3000');
      expect(result).toEqual({ field: 'retry', value: '3000' });
    });
  });

  describe('parseSSEEvent', () => {
    it('should parse single data line event', () => {
      const lines = ['data: Hello'];
      const result = parseSSEEvent(lines);
      expect(result).toEqual({
        data: 'Hello',
      });
    });

    it('should parse event with multiple fields', () => {
      const lines = [
        'event: message',
        'data: Hello World',
        'id: 123',
      ];
      const result = parseSSEEvent(lines);
      expect(result).toEqual({
        event: 'message',
        data: 'Hello World',
        id: '123',
      });
    });

    it('should concatenate multiple data lines with newlines', () => {
      const lines = [
        'data: Line 1',
        'data: Line 2',
        'data: Line 3',
      ];
      const result = parseSSEEvent(lines);
      expect(result).toEqual({
        data: 'Line 1\nLine 2\nLine 3',
      });
    });

    it('should parse retry field as number', () => {
      const lines = [
        'data: test',
        'retry: 5000',
      ];
      const result = parseSSEEvent(lines);
      expect(result).toEqual({
        data: 'test',
        retry: 5000,
      });
    });

    it('should return null if no data field present', () => {
      const lines = ['event: ping'];
      const result = parseSSEEvent(lines);
      expect(result).toBeNull();
    });

    it('should ignore comment lines', () => {
      const lines = [
        ': comment',
        'data: Hello',
      ];
      const result = parseSSEEvent(lines);
      expect(result).toEqual({
        data: 'Hello',
      });
    });

    it('should ignore invalid lines', () => {
      const lines = [
        'invalid line',
        'data: Hello',
      ];
      const result = parseSSEEvent(lines);
      expect(result).toEqual({
        data: 'Hello',
      });
    });
  });

  describe('extractTextContent', () => {
    it('should extract plain text data', () => {
      const result = extractTextContent('Hello World');
      expect(result).toBe('Hello World');
    });

    it('should extract delta field from JSON (OpenAI Agents SDK format)', () => {
      const result = extractTextContent('{"delta": "Hi there"}');
      expect(result).toBe('Hi there');
    });

    it('should extract content field from JSON', () => {
      const result = extractTextContent('{"content": "Test message"}');
      expect(result).toBe('Test message');
    });

    it('should extract text field from JSON', () => {
      const result = extractTextContent('{"text": "Another message"}');
      expect(result).toBe('Another message');
    });

    it('should return empty string for JSON without text fields', () => {
      const result = extractTextContent('{"thread_id": "abc123"}');
      expect(result).toBe('');
    });

    it('should return empty string for empty data', () => {
      expect(extractTextContent('')).toBe('');
    });

    it('should handle JSON with multiple fields, prioritizing delta', () => {
      const result = extractTextContent('{"delta": "Delta text", "content": "Content text"}');
      expect(result).toBe('Delta text');
    });
  });

  describe('filterMetadata', () => {
    it('should extract thread_id from JSON', () => {
      const result = filterMetadata('{"thread_id": "abc123"}');
      expect(result).toEqual({ threadId: 'abc123' });
    });

    it('should extract threadId (camelCase) from JSON', () => {
      const result = filterMetadata('{"threadId": "xyz789"}');
      expect(result).toEqual({ threadId: 'xyz789' });
    });

    it('should extract message_id from JSON', () => {
      const result = filterMetadata('{"message_id": "msg_001"}');
      expect(result).toEqual({ messageId: 'msg_001' });
    });

    it('should extract messageId (camelCase) from JSON', () => {
      const result = filterMetadata('{"messageId": "msg_002"}');
      expect(result).toEqual({ messageId: 'msg_002' });
    });

    it('should extract timestamp from JSON', () => {
      const result = filterMetadata('{"timestamp": "2026-01-05T12:00:00Z"}');
      expect(result).toEqual({ timestamp: '2026-01-05T12:00:00Z' });
    });

    it('should extract tool_calls from JSON', () => {
      const toolCalls = [{ id: '1', name: 'test', arguments: {} }];
      const result = filterMetadata(JSON.stringify({ tool_calls: toolCalls }));
      expect(result).toEqual({ toolCalls });
    });

    it('should extract multiple metadata fields', () => {
      const result = filterMetadata('{"thread_id": "abc", "message_id": "msg_1", "timestamp": "2026-01-05"}');
      expect(result).toEqual({
        threadId: 'abc',
        messageId: 'msg_1',
        timestamp: '2026-01-05',
      });
    });

    it('should return undefined for plain text data', () => {
      const result = filterMetadata('Plain text message');
      expect(result).toBeUndefined();
    });

    it('should return undefined for JSON without metadata fields', () => {
      const result = filterMetadata('{"delta": "Hello"}');
      expect(result).toBeUndefined();
    });

    it('should return undefined for empty data', () => {
      expect(filterMetadata('')).toBeUndefined();
    });
  });

  describe('parseSSEStream', () => {
    it('should parse single event with clean text', () => {
      const rawData = 'data: Hello World\n\n';
      const result = parseSSEStream(rawData);

      expect(result).toHaveLength(1);
      expect(result[0].content).toBe('Hello World');
      expect(result[0].isComplete).toBe(false);
    });

    it('should parse multiple events', () => {
      const rawData = 'data: First\n\ndata: Second\n\n';
      const result = parseSSEStream(rawData);

      expect(result).toHaveLength(2);
      expect(result[0].content).toBe('First');
      expect(result[1].content).toBe('Second');
    });

    it('should parse event with done marker', () => {
      const rawData = 'event: done\ndata: {"thread_id": "abc123"}\n\n';
      const result = parseSSEStream(rawData);

      expect(result).toHaveLength(1);
      expect(result[0].isComplete).toBe(true);
      expect(result[0].metadata?.threadId).toBe('abc123');
    });

    it('should parse JSON data with delta field', () => {
      const rawData = 'data: {"delta": "Hi there"}\n\n';
      const result = parseSSEStream(rawData);

      expect(result).toHaveLength(1);
      expect(result[0].content).toBe('Hi there');
    });

    it('should separate metadata from content', () => {
      const rawData = 'data: {"delta": "Hello", "thread_id": "abc"}\n\n';
      const result = parseSSEStream(rawData);

      expect(result).toHaveLength(1);
      expect(result[0].content).toBe('Hello');
      expect(result[0].metadata?.threadId).toBe('abc');
    });

    it('should handle incomplete event at end of buffer', () => {
      const rawData = 'data: Complete\n\ndata: Incomplete';
      const result = parseSSEStream(rawData);

      expect(result).toHaveLength(2);
      expect(result[0].content).toBe('Complete');
      expect(result[1].content).toBe('Incomplete');
    });

    it('should return empty array for empty data', () => {
      const result = parseSSEStream('');
      expect(result).toEqual([]);
    });

    it('should handle multi-line data fields', () => {
      const rawData = 'data: Line 1\ndata: Line 2\n\n';
      const result = parseSSEStream(rawData);

      expect(result).toHaveLength(1);
      expect(result[0].content).toBe('Line 1\nLine 2');
    });
  });

  describe('Test Cases: Protocol Artifact Removal', () => {
    it('T012: should remove "data:" prefixes from output', () => {
      const rawData = 'data: Hi\ndata:  there\ndata: !\n\n';
      const result = parseSSEStream(rawData);

      expect(result).toHaveLength(1);
      expect(result[0].content).not.toContain('data:');
      expect(result[0].content).toBe('Hi\n there\n!');
    });

    it('T013: should remove "event:" markers from output', () => {
      const rawData = 'event: message\ndata: Hello\n\n';
      const result = parseSSEStream(rawData);

      expect(result).toHaveLength(1);
      expect(result[0].content).not.toContain('event:');
      expect(result[0].content).toBe('Hello');
      expect(result[0].eventType).toBe('message');
    });

    it('T014: should separate thread_id metadata and not display it', () => {
      const rawData = 'event: done\ndata: {"thread_id": "abc123"}\n\n';
      const result = parseSSEStream(rawData);

      expect(result).toHaveLength(1);
      expect(result[0].content).not.toContain('thread_id');
      expect(result[0].content).not.toContain('abc123');
      expect(result[0].metadata?.threadId).toBe('abc123');
    });

    it('T015: should combine multi-line data fields with proper spacing', () => {
      const rawData = 'data: Hello\ndata: World\ndata: Test\n\n';
      const result = parseSSEStream(rawData);

      expect(result).toHaveLength(1);
      // Multi-line data fields are concatenated with newlines per SSE spec
      expect(result[0].content).toBe('Hello\nWorld\nTest');
    });
  });

  describe('parseSSEStreamSafe', () => {
    it('should return chunks and no errors for valid data', () => {
      const rawData = 'data: Hello\n\n';
      const result = parseSSEStreamSafe(rawData);

      expect(result.chunks).toHaveLength(1);
      expect(result.errors).toHaveLength(0);
      expect(result.isComplete).toBe(false);
    });

    it('should detect completion from done event', () => {
      const rawData = 'event: done\ndata: test\n\n';
      const result = parseSSEStreamSafe(rawData);

      expect(result.isComplete).toBe(true);
    });

    it('should detect completion from complete event', () => {
      const rawData = 'event: complete\ndata: test\n\n';
      const result = parseSSEStreamSafe(rawData);

      expect(result.isComplete).toBe(true);
    });

    it('should handle empty data gracefully', () => {
      const result = parseSSEStreamSafe('');

      expect(result.chunks).toEqual([]);
      expect(result.errors).toHaveLength(0);
      expect(result.isComplete).toBe(false);
    });
  });

  describe('combineDataLines', () => {
    it('should combine multiple lines with spaces', () => {
      const result = combineDataLines(['Hello', 'World', 'Test']);
      expect(result).toBe('Hello World Test');
    });

    it('should trim whitespace from each line', () => {
      const result = combineDataLines(['  Hello  ', '  World  ']);
      expect(result).toBe('Hello World');
    });

    it('should filter out empty lines', () => {
      const result = combineDataLines(['Hello', '', 'World', '   ', 'Test']);
      expect(result).toBe('Hello World Test');
    });

    it('should handle single line', () => {
      const result = combineDataLines(['Single']);
      expect(result).toBe('Single');
    });

    it('should handle empty array', () => {
      const result = combineDataLines([]);
      expect(result).toBe('');
    });
  });

  describe('isValidSSEEvent', () => {
    it('should validate event with data field', () => {
      const event: RawSSEEvent = { data: 'Hello' };
      expect(isValidSSEEvent(event)).toBe(true);
    });

    it('should validate event with all fields', () => {
      const event: RawSSEEvent = {
        event: 'message',
        data: 'Hello',
        id: '123',
        retry: 3000,
      };
      expect(isValidSSEEvent(event)).toBe(true);
    });

    it('should reject event without data field', () => {
      const event = { event: 'ping' } as RawSSEEvent;
      expect(isValidSSEEvent(event)).toBe(false);
    });

    it('should reject event with non-string data', () => {
      const event = { data: 123 } as unknown as RawSSEEvent;
      expect(isValidSSEEvent(event)).toBe(false);
    });

    it('should reject event with non-string event type', () => {
      const event = { data: 'test', event: 123 } as unknown as RawSSEEvent;
      expect(isValidSSEEvent(event)).toBe(false);
    });

    it('should reject event with non-string id', () => {
      const event = { data: 'test', id: 123 } as unknown as RawSSEEvent;
      expect(isValidSSEEvent(event)).toBe(false);
    });

    it('should reject event with non-number retry', () => {
      const event = { data: 'test', retry: '3000' } as unknown as RawSSEEvent;
      expect(isValidSSEEvent(event)).toBe(false);
    });
  });
});
