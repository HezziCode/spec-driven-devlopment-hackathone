# Feature Specification: Fix FastAPI Authentication Errors in Next.js Chat App

**Feature Branch**: `001-auth-errors`
**Created**: 2026-01-04
**Status**: Draft
**Input**: User description: "CopyPublishFix FastAPI Authentication Errors in Next.js Chat App
Critical Issue: Missing Authorization Token
My Next.js chat application is getting \"Failed to fetch\" errors because the frontend is not sending authentication tokens to the FastAPI backend.
Backend Information

API Base: http://localhost:8000
Authentication: Bearer Token required in Authorization header
Error Response: {\"error\": \"Authorization header is required\", \"code\": \"MISSING_TOKEN\"}

API Endpoints That Need Fixing
bash# All these require: Authorization: Bearer <token>

GET /api/users/{user_id}/chat/threads
POST /api/users/{user_id}/chat/messages
DELETE /api/users/{user_id}/chat/threads/{thread_id}
Three Functions Failing (All Missing Auth Token)
Error 1: loadThreadMessages
at loadThreadMessages (frontend/.next/dev/static/chunks/_086fdfaa._.js:646:36)
Context: Runs on page load via useEffect, tries to fetch threads without auth token
Error 2: sendMessage
at sendMessage (frontend/.next/dev/static/chunks/_086fdfaa._.js:766:36)
Context: Triggered when user sends a message, no auth token sent
Error 3: deleteThread
at deleteThread (frontend/.next/dev/static/chunks/_086fdfaa._.js:703:36)
Context: Triggered when user deletes a thread, no auth token sent
What Needs To Be Fixed
1. Find Token Storage
Locate where the authentication token is stored after login:

Check localStorage for keys like: token, access_token, auth_token, jwt
Check cookies
Check any auth context/state management (useAuth, useUser, etc.)
Look for login/signup components to see what token key is used

2. Find user_id Storage
Locate where user_id is stored:

Check localStorage.getItem('user_id')
Check auth context for user object with id property
May be in JWT token (need to decode)

3. Update All Three Functions
Add these to each function:

Get token from storage
Add Authorization: Bearer ${token} header
Get user_id and add to URL path
Add proper error handling for missing token
Add try-catch with meaningful error messages

4. Code Pattern to Implement
typescript// Helper to get auth headers
const getAuthHeaders = () => {
  const token = localStorage.getItem('access_token'); // Find correct key
  if (!token) {
    throw new Error('Not authenticated');
  }
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
  };
};

// Helper to get user ID
const getUserId = () => {
  const userId = localStorage.getItem('user_id'); // Find correct key
  if (!userId) {
    throw new Error('User ID not found');
  }
  return userId;
};

// Example fixed function
const loadThreadMessages = async () => {
  try {
    const userId = getUserId();
    const headers = getAuthHeaders();

    const response = await fetch(
      `${API_BASE_URL}/api/users/${userId}/chat/threads`,
      { headers }
    );

    if (response.status === 401) {
      // Handle unauthorized - maybe redirect to login
      throw new Error('Session expired. Please login again.');
    }

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to load threads:', error);
    // Show error to user
    throw error;
  }
};
5. Check Environment Variables
Verify .env.local in frontend has:
NEXT_PUBLIC_API_URL=http://localhost:8000
6. Additional Checks

Look for API client/service file (might be in lib/, utils/, services/)
Check if there's axios instance or fetch wrapper already configured
Verify CORS is enabled in FastAPI backend for http://localhost:3000
Check if token refresh logic exists for expired tokens

Expected Results After Fix

✅ loadThreadMessages successfully fetches threads with auth token
✅ sendMessage successfully sends messages with auth token
✅ deleteThread successfully deletes threads with auth token
✅ Proper error handling shows user-friendly messages
✅ 401 errors redirect to login or show \"session expired\" message

Testing Checklist
After implementing fixes:

 Navigate to chat page - threads should load
 Send a message - should work without \"Failed to fetch\"
 Delete a thread - should work without errors
 Check browser console - no fetch errors
 Check Network tab - requests have Authorization header
 Test with expired/invalid token - should show proper error

Priority
HIGHEST PRIORITY: Find where the authentication token is stored after user login, then add that token to all three API calls with Authorization: Bearer ${token} header.
Start by searching the codebase for:

Login/signup components
localStorage.setItem('token' or similar
Auth context providers
Any existing authenticated API calls that work (to see the pattern"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Load Chat Threads Successfully (Priority: P1)

As a logged-in user, I want to be able to load my chat threads when I visit the chat page, so that I can see my previous conversations without encountering "Failed to fetch" errors.

**Why this priority**: This is the foundational functionality that enables users to access their chat history. Without this working, the entire chat experience is broken.

**Independent Test**: Can be fully tested by navigating to the chat page and verifying that threads load without errors, delivering the core value of accessing previous conversations.

**Acceptance Scenarios**:

1. **Given** user is logged in and has chat threads, **When** user visits the chat page, **Then** chat threads are displayed without any "Failed to fetch" errors
2. **Given** user is logged in but has no chat threads, **When** user visits the chat page, **Then** an appropriate message is shown without errors

---

### User Story 2 - Send Messages Successfully (Priority: P1)

As a logged-in user, I want to be able to send messages in the chat interface, so that I can participate in conversations without encountering "Failed to fetch" errors.

**Why this priority**: This is the core functionality of the chat application. Without being able to send messages, users cannot engage in real-time communication.

**Independent Test**: Can be fully tested by typing a message and sending it, verifying that it succeeds without errors, delivering the core value of real-time communication.

**Acceptance Scenarios**:

1. **Given** user is logged in and on the chat page, **When** user types a message and sends it, **Then** the message is sent successfully without "Failed to fetch" errors
2. **Given** user is logged in and on the chat page, **When** user sends a message with special characters or formatting, **Then** the message is sent successfully

---

### User Story 3 - Delete Chat Threads Successfully (Priority: P2)

As a logged-in user, I want to be able to delete my chat threads, so that I can manage my conversations without encountering "Failed to fetch" errors.

**Why this priority**: This provides users with control over their data and helps maintain a clean interface, but is secondary to basic messaging functionality.

**Independent Test**: Can be fully tested by deleting a thread and verifying the action completes without errors, delivering the value of data management.

**Acceptance Scenarios**:

1. **Given** user is logged in and has chat threads, **When** user deletes a thread, **Then** the thread is removed without "Failed to fetch" errors

---

### Edge Cases

- What happens when the authentication token has expired?
- How does the system handle network failures during API calls?
- What happens when the user_id cannot be retrieved from storage?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST include Authorization header with Bearer token in all chat API requests
- **FR-002**: System MUST retrieve the authentication token from storage before making API calls
- **FR-003**: System MUST retrieve the user_id from storage to include in API endpoints
- **FR-004**: System MUST handle 401 Unauthorized responses by showing appropriate error messages
- **FR-005**: System MUST properly format API endpoints with user_id path parameters
- **FR-006**: System MUST implement proper error handling for missing authentication tokens
- **FR-007**: System MUST send appropriate Content-Type headers for API requests

### Key Entities

- **Authentication Token**: Represents the user's session and authorization to access protected resources
- **User ID**: Represents the unique identifier for the authenticated user, used for data isolation

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can load their chat threads without "Failed to fetch" errors (100% success rate)
- **SC-002**: Users can send messages without "Failed to fetch" errors (100% success rate)
- **SC-003**: Users can delete chat threads without "Failed to fetch" errors (100% success rate)
- **SC-004**: API requests include proper Authorization headers with Bearer tokens (100% of requests)