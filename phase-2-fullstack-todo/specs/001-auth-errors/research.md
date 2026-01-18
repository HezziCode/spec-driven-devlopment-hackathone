# Research: Authentication Token Storage and API Implementation

## Findings Summary

### 1. Token Storage Location
- **Status**: FOUND - Located in frontend/lib/auth.ts
- **Storage Key**: 'better-auth-session-token' stored in localStorage
- **Functions**: getAuthToken(), getCurrentUserId(), useAuth() hook
- **Token Type**: JWT token from Better Auth

### 2. Current Implementation of Failing Functions
- **loadThreadMessages**: Located in frontend/components/CustomChatInterface.tsx:100
- **sendMessage**: Located in frontend/components/CustomChatInterface.tsx:200
- **deleteThread**: Located in frontend/components/CustomChatInterface.tsx:160
- **Status**: IMPLEMENTED with proper auth headers but may have backend issues

### 3. API Client Pattern
- **Current Pattern**: Direct fetch calls with Authorization headers in components
- **Auth Integration**: Using getAuthToken() and useAuth() from frontend/lib/auth.ts
- **Headers Format**: 'Authorization': `Bearer ${token}`

## Detailed Investigation

### Token Storage Analysis
1. **localStorage key**: 'better-auth-session-token'
2. **Better Auth integration**: Working properly in auth.ts
3. **React context**: useAuth() hook provides session data

### Frontend Implementation Analysis
All three functions already have proper authentication implementation:
- loadThreadMessages: ✓ Uses getAuthToken() and Authorization header
- sendMessage: ✓ Uses getAuthToken() and Authorization header
- deleteThread: ✓ Uses getAuthToken() and Authorization header

### Backend Issue Discovery
Found an issue in backend/middleware/auth_middleware.py:
- The `get_current_user` function expects `request.state.user` but middleware only sets `request.state.user_id`
- This creates a mismatch in the authentication flow
- The route functions expect a user object but only get user_id
- **RESOLVED**: Fixed by updating the `get_current_user` function to work with the actual data set by the middleware

### API Configuration
1. **Environment variables**: NEXT_PUBLIC_API_URL configured properly
2. **API base URL**: Using process.env.NEXT_PUBLIC_API_URL
3. **Current fetch patterns**: Proper Authorization header usage

## Implementation Approach

Based on the investigation, the issue is likely in the backend auth middleware. The solution will involve:

1. **Fix auth middleware**: Correct the mismatch between what's set in request.state and what's expected
2. **Update get_current_user**: Make it compatible with what the middleware actually sets
3. **Verify token validation**: Ensure JWT verification is working properly

The frontend implementation is already correct with proper authentication headers.