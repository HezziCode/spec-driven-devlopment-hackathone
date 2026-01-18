# Implementation Plan: Fix FastAPI Authentication Errors in Next.js Chat App

**Feature**: 001-auth-errors
**Created**: 2026-01-04
**Status**: Draft
**Author**: Claude Code

## Technical Context

This plan addresses the "Failed to fetch" errors occurring in the Next.js chat application due to missing Authorization tokens in API requests to the FastAPI backend. The issue affects three core functions: loadThreadMessages, sendMessage, and deleteThread.

**Known Technologies**:
- Frontend: Next.js 16+ with TypeScript
- Backend: FastAPI with JWT authentication
- Authentication: Better Auth with JWT tokens
- Database: Neon Serverless PostgreSQL

**Unknowns/Dependencies**:
- Location of authentication token storage in the frontend
- Current implementation of the three failing functions
- API client/service architecture used in the frontend

## Constitution Check

This implementation must comply with the following constitution principles:

- **Clean Code (II)**: Functions must have single responsibility; comprehensive docstrings required
- **Type Safety (III)**: All code must be fully typed; no 'any' types in TypeScript
- **Modular Architecture (VI)**: Clear separation between frontend and backend with well-defined API contracts
- **Security Requirements (NFRs)**: JWT tokens must be properly validated and attached to requests

## Gates

- ✅ **Spec Clarity**: Feature specification is complete with clear requirements
- ✅ **Architecture Alignment**: Solution aligns with existing Next.js/FastAPI architecture
- ✅ **Security Compliance**: Implementation will enforce JWT-based authentication
- ✅ **Type Safety**: TypeScript strict mode will be maintained

## Phase 0: Research

### Research Tasks

1. **Locate Token Storage**: Find where authentication tokens are stored after login (localStorage, cookies, auth context)
2. **Analyze Current Implementation**: Examine the three failing functions (loadThreadMessages, sendMessage, deleteThread) to understand current implementation
3. **Identify API Client Pattern**: Determine if there's an existing API client/service that handles authenticated requests
4. **Check Environment Configuration**: Verify API URL configuration in frontend environment variables

### Research Findings

**Decision**: Locate authentication token and user_id storage mechanisms
**Rationale**: The token and user_id are essential for making authenticated API requests
**Alternatives considered**:
- localStorage (most common)
- cookies
- React context/state management
- JWT token decoding

**Decision**: Update the three failing functions to include proper authentication headers
**Rationale**: The core issue is missing Authorization header with Bearer token
**Alternatives considered**:
- Global axios interceptors
- Custom fetch wrapper
- Individual function updates (selected approach)

## Phase 1: Data Model & Contracts

### Data Model

No new data models needed - this is a client-side authentication fix.

### API Contracts

The following endpoints require authentication headers:

```
GET /api/users/{user_id}/chat/threads
POST /api/users/{user_id}/chat/messages
DELETE /api/users/{user_id}/chat/threads/{thread_id}
```

All endpoints require:
- Authorization: Bearer {token} header
- user_id in the path parameter
- Proper Content-Type header for POST requests

## Phase 2: Implementation Strategy

### Implementation Steps

1. **Fix Backend Auth Middleware**: Update the get_current_user function to properly handle user data from request.state
2. **Verify Frontend Implementation**: Confirm frontend functions already include proper authentication headers
3. **Test Implementation**: Verify all functions work correctly

### File Structure

- Frontend components that need updates:
  - Chat interface component containing the failing functions
  - API service/client file (if exists)
  - Environment configuration

### Dependencies

- Better Auth for token management
- Existing API endpoints in FastAPI backend
- Environment variables for API base URL

## Phase 3: Risk Assessment

### Risks

1. **Token Storage Location**: If token is stored in multiple places, all locations must be identified
2. **Token Expiration**: Implementation must handle expired tokens gracefully
3. **User ID Retrieval**: User ID must be correctly retrieved for path parameters
4. **Existing API Patterns**: New implementation should follow existing patterns in the codebase

### Mitigation Strategies

1. **Comprehensive Search**: Thoroughly search codebase for all token storage locations
2. **Error Handling**: Implement proper 401 handling with user-friendly messages
3. **Fallback Mechanisms**: Provide fallback for user ID retrieval if primary method fails
4. **Code Consistency**: Follow existing patterns in the codebase for consistency

## Phase 4: Testing Strategy

### Test Cases

1. **Successful API Calls**: Verify all three functions work with proper authentication
2. **Token Missing**: Verify proper error handling when token is not available
3. **Token Expired**: Verify proper handling of 401 responses
4. **User ID Missing**: Verify proper error handling when user_id is not available

### Validation Criteria

- All API calls include Authorization: Bearer {token} header
- All API calls include correct user_id in path
- Error responses are handled gracefully with user-friendly messages
- No "Failed to fetch" errors occur in console