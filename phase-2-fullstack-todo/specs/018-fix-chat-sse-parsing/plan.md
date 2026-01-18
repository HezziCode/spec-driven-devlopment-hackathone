# Implementation Plan: Fix Chat SSE Parsing

**Branch**: `018-fix-chat-sse-parsing` | **Date**: 2026-01-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/018-fix-chat-sse-parsing/spec.md`

## Summary

Fix the chat interface SSE (Server-Sent Events) parsing to display clean, readable text without protocol artifacts. The current implementation displays raw SSE data including "data:" prefixes, "event:" markers, and thread IDs directly to users. This plan focuses on implementing proper SSE event parsing in the frontend chat component to extract and display only the message content while maintaining streaming functionality.

**Technical Approach**: Implement EventSource or fetch-based SSE parsing in the frontend chat component to properly parse SSE protocol format, extract text content from data fields, filter out event markers and metadata, and display clean streaming text to users.

## Technical Context

**Language/Version**: TypeScript 5.x with Next.js 16+ (App Router)
**Primary Dependencies**: React 19.x, Next.js 16+, OpenAI ChatKit (if used), native EventSource API or fetch with ReadableStream
**Storage**: N/A (frontend display fix only)
**Testing**: Jest/Vitest for frontend component testing, React Testing Library for component behavior
**Target Platform**: Web browsers (Chrome, Firefox, Safari, Edge) with SSE support
**Project Type**: Web application (frontend fix)
**Performance Goals**: Display first text chunk within 100ms of receiving SSE data, maintain smooth streaming without UI blocking
**Constraints**: Must not modify backend SSE implementation, must preserve streaming functionality, must handle all SSE event types gracefully
**Scale/Scope**: Single frontend component fix affecting chat interface display logic

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle II: Clean Code with Single Responsibility Principle
✅ **PASS** - SSE parsing logic will be extracted into a dedicated utility function or hook with single responsibility of parsing SSE streams

### Principle III: Type Safety and Strict TypeScript Typing
✅ **PASS** - All SSE parsing functions will be fully typed with TypeScript interfaces for SSE events, message chunks, and parsed content. No 'any' types will be used.

### Principle IV: Accessibility Compliance (WCAG 2.1 AA)
✅ **PASS** - Fix improves accessibility by making chat responses readable. Screen readers will announce clean text instead of protocol artifacts.

### Principle V: Performance-First Architecture
✅ **PASS** - SSE parsing will use O(n) string operations for each chunk. Streaming display maintains progressive rendering without blocking UI thread.

### Principle VI: Modular Architecture with Clear Boundaries
✅ **PASS** - SSE parsing logic will be isolated in utility functions/hooks, separating protocol handling from UI rendering concerns.

### Principle VII: Stateless Server Architecture
✅ **PASS** - This is a frontend-only fix. No server-side changes required. Backend remains stateless.

**Constitution Compliance**: ✅ ALL GATES PASSED

## Project Structure

### Documentation (this feature)

```text
specs/018-fix-chat-sse-parsing/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output - SSE parsing patterns and best practices
├── data-model.md        # Phase 1 output - SSE event type definitions
├── quickstart.md        # Phase 1 output - Quick reference for SSE parsing implementation
├── contracts/           # Phase 1 output - SSE event format contracts
│   └── sse-events.ts    # TypeScript interfaces for SSE event types
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
frontend/
├── app/
│   └── chat/
│       └── page.tsx                    # Chat page component (may need updates)
├── components/
│   ├── ChatInterface.tsx               # Main chat component (PRIMARY FIX TARGET)
│   ├── CustomChatInterface.tsx         # Alternative chat component (may need updates)
│   └── MessageDisplay.tsx              # New component for clean message rendering
├── lib/
│   ├── chatkit-api.ts                  # Chat API client (may need updates)
│   └── sse-parser.ts                   # NEW: SSE parsing utility functions
├── hooks/
│   └── useSSEStream.ts                 # NEW: Custom hook for SSE stream handling
├── types/
│   ├── chatkit.ts                      # Existing chat types (may need updates)
│   └── sse.ts                          # NEW: SSE event type definitions
└── __tests__/
    ├── components/
    │   └── ChatInterface.test.tsx      # Tests for chat component
    └── lib/
        └── sse-parser.test.ts          # Tests for SSE parsing logic
```

**Structure Decision**: Web application structure with frontend-only changes. The fix targets the chat interface components and adds new SSE parsing utilities. No backend modifications required as the issue is isolated to frontend display logic.

## Complexity Tracking

> **No violations detected** - All constitution principles are satisfied without requiring additional complexity.

## Phase 0: Research & Analysis

### Research Tasks

1. **Analyze Current SSE Implementation**
   - Locate the exact component(s) handling chat SSE streams
   - Identify how SSE data is currently being received and displayed
   - Document the current data flow from backend to UI
   - Capture example raw SSE data format from backend

2. **SSE Protocol Standards Research** (Completed via Context7)
   - Standard SSE format: `data: <content>\n\n` with optional `event:` and `id:` fields
   - Multiple `data:` lines can be part of single event
   - Events are separated by double newlines (`\n\n`)
   - Comments start with `:` and should be ignored

3. **OpenAI Agents SDK Streaming Format** (Completed via Context7)
   - Uses `ResponseTextDeltaEvent` for text streaming
   - Events include `type` field and `data` payload
   - Text content is in `event.data.delta` for text delta events
   - Completion events include metadata like thread_id

4. **Frontend SSE Parsing Patterns** (Completed via Context7)
   - EventSource API: Built-in browser API for SSE, auto-parses protocol
   - Fetch + ReadableStream: Manual parsing with more control
   - React patterns: Custom hooks for SSE stream management
   - Progressive rendering: Display chunks as they arrive

### Key Findings from Context7 Research

**Next.js Streaming Patterns**:
- Use `ReadableStream` with async iterators for progressive rendering
- `TextEncoder`/`TextDecoder` for handling text chunks
- Stream responses using `new Response(stream)` pattern

**OpenAI Agents SDK Streaming**:
- `Runner.run_streamed()` returns streaming result
- `stream_events()` provides async iterator over events
- Filter for `ResponseTextDeltaEvent` to get text deltas
- `event.data.delta` contains the actual text content
- Other event types include metadata (thread_id, tool calls, etc.)

**React SSE Best Practices**:
- Use custom hooks to encapsulate SSE logic
- Separate parsing logic from rendering logic
- Handle connection errors and reconnection gracefully
- Clean up event listeners on component unmount

### Decision: SSE Parsing Approach

**Selected Approach**: Fetch API with ReadableStream + Custom Parser

**Rationale**:
- More control over parsing than EventSource API
- Can filter and transform events before display
- Better error handling and retry logic
- Aligns with OpenAI Agents SDK streaming patterns
- Supports custom event types and metadata filtering

**Implementation Strategy**:
1. Create `sse-parser.ts` utility with functions to parse SSE protocol
2. Create `useSSEStream.ts` hook to manage SSE connection and parsing
3. Update chat components to use the new hook
4. Filter out protocol artifacts (data:, event:, thread_id) before display
5. Maintain streaming functionality with progressive text display

## Phase 1: Design & Contracts

### Data Model

See [data-model.md](./data-model.md) for complete type definitions.

**Key Types**:

```typescript
// SSE Event Types
interface SSEEvent {
  type: 'message' | 'error' | 'done';
  data: string;
  id?: string;
  event?: string;
}

interface ParsedSSEChunk {
  content: string;
  isComplete: boolean;
  metadata?: {
    threadId?: string;
    eventType?: string;
  };
}

// Chat Message Display
interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
}
```

### API Contracts

See [contracts/](./contracts/) directory for complete contract definitions.

**No Backend API Changes Required** - This is a frontend-only fix.

**Frontend Contract Changes**:
- New SSE parsing utility functions
- New custom hook for SSE stream management
- Updated chat component props to handle streaming state

### Component Architecture

```
ChatInterface (Main Component)
├── useSSEStream (Custom Hook)
│   ├── Fetch SSE endpoint
│   ├── Parse SSE stream with sse-parser
│   └── Return clean text chunks
├── MessageDisplay (New Component)
│   ├── Display user messages
│   ├── Display assistant messages
│   └── Handle streaming state (typing indicator)
└── MessageInput (Existing Component)
    └── Send user messages
```

### File Changes Summary

**New Files**:
- `frontend/lib/sse-parser.ts` - SSE parsing utilities
- `frontend/hooks/useSSEStream.ts` - SSE stream management hook
- `frontend/types/sse.ts` - SSE type definitions
- `frontend/components/MessageDisplay.tsx` - Clean message rendering component

**Modified Files**:
- `frontend/components/ChatInterface.tsx` - Use new SSE parsing hook
- `frontend/components/CustomChatInterface.tsx` - Use new SSE parsing hook (if applicable)
- `frontend/lib/chatkit-api.ts` - May need updates to return raw stream

**Test Files**:
- `frontend/__tests__/lib/sse-parser.test.ts` - Unit tests for parsing logic
- `frontend/__tests__/hooks/useSSEStream.test.ts` - Hook behavior tests
- `frontend/__tests__/components/ChatInterface.test.tsx` - Integration tests

## Phase 2: Implementation Tasks

Tasks will be generated in the next phase using `/sp.tasks` command.

**High-Level Task Categories**:

1. **Setup & Dependencies** (if needed)
   - Verify no additional dependencies required
   - Set up test environment for SSE testing

2. **Core SSE Parsing Logic** (TDD)
   - Write tests for SSE parser utility
   - Implement SSE event parsing functions
   - Implement text extraction from data fields
   - Implement metadata filtering

3. **Custom Hook Implementation** (TDD)
   - Write tests for useSSEStream hook
   - Implement SSE connection management
   - Implement stream reading and parsing
   - Implement error handling and reconnection

4. **Component Updates** (TDD)
   - Write tests for updated ChatInterface
   - Update ChatInterface to use new hook
   - Update CustomChatInterface (if applicable)
   - Create MessageDisplay component for clean rendering

5. **Integration & Testing**
   - Test with real backend SSE endpoint
   - Verify streaming functionality preserved
   - Verify all protocol artifacts removed
   - Test error scenarios (network failure, timeout)

6. **Edge Cases & Polish**
   - Test with special characters and emojis
   - Test with very long messages
   - Test with rapid message succession
   - Verify accessibility with screen readers

## Risk Assessment

### Technical Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Breaking existing streaming functionality | High | Medium | Comprehensive testing, feature flag for rollback |
| Performance degradation from parsing overhead | Medium | Low | Optimize parsing logic, benchmark performance |
| Incompatibility with backend SSE format | High | Low | Document backend format, add format validation |
| Browser compatibility issues with fetch streams | Medium | Low | Test across browsers, provide EventSource fallback |

### Implementation Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Missing edge cases in parsing logic | Medium | Medium | Extensive unit tests, real-world testing |
| Race conditions in streaming state | Medium | Low | Proper state management, React best practices |
| Memory leaks from unclosed streams | Medium | Low | Proper cleanup in useEffect, connection management |

## Success Criteria Validation

Mapping spec success criteria to implementation validation:

- **SC-001**: 100% clean text display
  - **Validation**: Visual inspection + automated tests checking for absence of "data:", "event:", thread_id in rendered output

- **SC-002**: Immediate readability
  - **Validation**: User acceptance testing, no confusion reported

- **SC-003**: Correct word spacing
  - **Validation**: Automated tests checking for proper spacing, no concatenated words

- **SC-004**: Progressive streaming display
  - **Validation**: Performance tests measuring chunk display latency, visual confirmation of progressive rendering

- **SC-005**: Zero user-reported issues
  - **Validation**: Post-deployment monitoring, user feedback collection

- **SC-006**: Sub-100ms display latency
  - **Validation**: Performance benchmarks measuring time from chunk arrival to DOM update

## Next Steps

1. **Run `/sp.tasks`** to generate detailed implementation tasks
2. **Review and approve** the task breakdown
3. **Execute `/sp.implement`** to begin TDD implementation
4. **Test thoroughly** with real backend integration
5. **Deploy and monitor** for any issues

## Dependencies

- No new external dependencies required
- Uses native browser APIs (fetch, ReadableStream, TextDecoder)
- Existing React and Next.js dependencies sufficient

## Timeline Considerations

- **Complexity**: Low-Medium (frontend-only fix, well-defined scope)
- **Testing Requirements**: Medium (unit, integration, and browser testing needed)
- **Risk Level**: Low (isolated change, easy to rollback)

## Notes

- This fix is isolated to frontend display logic
- Backend SSE implementation remains unchanged
- Streaming functionality must be preserved
- Focus on clean, maintainable parsing logic
- Comprehensive testing critical for edge cases
