# Research Document: Fix Chat Thread and API Key Errors

**Feature**: Fix Chat Thread and API Key Errors
**Date**: 2026-01-13
**Author**: Claude Code

## Executive Summary

This research addresses two critical errors in the chat functionality:
1. HTTP 404 errors when loading chat threads due to timing/race conditions between thread creation and access
2. HTTP 401 API authentication errors when connecting to OpenAI services

## Technical Challenges Identified

### Challenge 1: Thread Synchronization Issue (404 Error)
- **Problem**: Thread is created in database but not immediately available for access due to database transaction timing
- **Root Cause**: Race condition between thread creation commit and frontend access attempt
- **Evidence**: Console shows "Thread not found" with retry mechanism, indicating timing issue
- **Solution Approach**: Implement proper database synchronization with `session.commit()`, `session.expire_all()`, and small delays to ensure transaction visibility

### Challenge 2: OpenAI API Authentication (401 Error)
- **Problem**: Incorrect API key configuration for OpenAI Agents SDK during runtime
- **Root Cause**: API key properly configured at startup but not maintained during runtime operations
- **Evidence**: SSE error shows "Incorrect API key provided: sk-xxxxx*******xxxx"
- **Solution Approach**: Use proper OpenAI Agents SDK configuration with `set_default_openai_api()` and `set_default_openai_client()` functions

## Research Findings

### Finding 1: Database Transaction Synchronization
- **Source**: Analysis of existing chatkit_service.py implementation
- **Method**: Use SQLAlchemy session synchronization methods (`commit`, `expire_all`, `expunge`)
- **Implementation**: Add synchronization after thread creation before signaling completion
- **Reference**: SQLAlchemy documentation on session management and transaction visibility

### Finding 2: OpenAI Agents SDK Configuration
- **Source**: OpenAI Agents SDK documentation and Context7 research
- **Method**: Use `set_default_openai_api()` at application startup and ensure client availability
- **Implementation**: Configure in main.py lifespan function with proper fallbacks
- **Reference**: OpenAI Agents SDK best practices for production deployment

### Finding 3: Frontend Retry Logic Enhancement
- **Source**: Analysis of CustomChatInterface.tsx error handling
- **Method**: Improve retry mechanism with proper error classification
- **Implementation**: Distinguish between temporary and permanent errors, clear invalid thread IDs
- **Reference**: Best practices for resilient frontend API interactions

### Finding 4: SSE Connection Stability
- **Source**: Analysis of SSE streaming implementation in chatkit server
- **Method**: Proper error handling and reconnection logic for streaming responses
- **Implementation**: Ensure proper event parsing and error propagation
- **Reference**: Server-Sent Events specification and error handling patterns

## Recommended Solutions

### Solution 1: Backend Thread Synchronization
1. Update `services/chatkit_service.py` to add proper database synchronization after thread creation
2. Implement `session.commit()` followed by `session.expire_all()` to ensure visibility
3. Add small delay (100ms) after thread creation to allow for database propagation

### Solution 2: OpenAI API Key Configuration
1. Update `main.py` to use `set_default_openai_api()` and `set_default_openai_client()` functions
2. Ensure API key is available as environment variable for subprocesses
3. Add proper error handling and fallback mechanisms

### Solution 3: Frontend Error Handling
1. Update `CustomChatInterface.tsx` to improve retry logic and error classification
2. Implement proper invalid thread ID clearing to prevent repeated failed requests
3. Enhance SSE error handling with proper event parsing

### Solution 4: SSE Stability Improvements
1. Update `lib/sse-parser.ts` to properly handle thread_created and error events
2. Ensure proper metadata extraction for threadId from SSE events
3. Add connection stability mechanisms with proper reconnection logic

## Risks and Mitigations

### Risk 1: Increased Latency Due to Synchronization Delays
- **Mitigation**: Keep delays minimal (under 200ms) and implement them only when necessary
- **Monitoring**: Track performance metrics to ensure response times remain acceptable

### Risk 2: API Key Exposure in Runtime Errors
- **Mitigation**: Ensure proper error sanitization and avoid logging sensitive information
- **Implementation**: Use environment variables and secure configuration management

### Risk 3: Race Conditions in Multi-User Scenarios
- **Mitigation**: Implement proper user isolation with thread ownership verification
- **Implementation**: Add user_id validation in all thread access operations

## Decision Log

### Decision: Use Session Synchronization Instead of Increasing Timeout
- **Rationale**: Direct database synchronization is more reliable than arbitrary timeout increases
- **Alternative Rejected**: Simply increasing timeout values without addressing root cause
- **Impact**: More robust solution that addresses the actual timing issue

### Decision: Implement Proper OpenAI SDK Configuration Instead of Manual Headers
- **Rationale**: Using official SDK configuration functions ensures consistency and best practices
- **Alternative Rejected**: Manually setting API key in request headers
- **Impact**: More maintainable and follows OpenAI's recommended patterns

### Decision: Enhance Frontend Error Handling Rather Than Just Backend Fixes
- **Rationale**: Comprehensive solution requires both frontend and backend improvements
- **Alternative Rejected**: Backend-only fix without frontend resilience
- **Impact**: Better user experience with graceful error handling

## Implementation Priority

1. **High Priority**: Backend thread synchronization and API key configuration
2. **Medium Priority**: Frontend error handling and retry logic
3. **Low Priority**: SSE connection enhancements and monitoring

## Success Metrics

- 404 errors reduced to 0% occurrence rate
- 401 API authentication errors eliminated
- Thread creation and access success rate of 100%
- SSE connection stability maintained above 99%

## References

1. SQLAlchemy Session Management Documentation
2. OpenAI Agents SDK Configuration Guide
3. Server-Sent Events Specification (W3C)
4. Next.js Error Handling Best Practices
5. FastAPI Dependency Injection Patterns