# Quickstart: Authentication Fix Verification

## Overview
This guide provides steps to verify that the authentication errors in the Next.js chat app have been fixed. The "Failed to fetch" errors were caused by a mismatch in the backend auth middleware between what was set in request.state and what was expected by the get_current_user dependency.

## Changes Made

### Backend Fix
- **File**: `backend/middleware/auth_middleware.py`
- **Issue**: `get_current_user` function expected `request.state.user` but middleware only set `request.state.user_id`
- **Solution**: Updated `get_current_user` to properly extract user information from `request.state.user_id`

### Before
```python
async def get_current_user(request: Request) -> Any:
    if not hasattr(request.state, 'user') or request.state.user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return request.state.user
```

### After
```python
async def get_current_user(request: Request) -> dict:
    if not hasattr(request.state, 'user_id') or request.state.user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Return user information from the request state
    return {
        "id": request.state.user_id,
        "email": getattr(request.state, 'email', None)
    }
```

## Verification Steps

### 1. Start the Backend Server
```bash
cd backend
uv venv  # If not already created
source .venv/bin/activate  # Or appropriate activation command
uv run uvicorn main:app --reload
```

### 2. Start the Frontend Server
```bash
cd frontend
npm install  # If dependencies not installed
npm run dev
```

### 3. Test the Chat Functions
1. **Login/Register** to the application to ensure you have a valid JWT token
2. **Test loadThreadMessages**: Navigate to the chat page and verify threads load without errors
3. **Test sendMessage**: Send a message in the chat and verify it works without "Failed to fetch" errors
4. **Test deleteThread**: Delete a thread and verify it works without "Failed to fetch" errors

### 4. Check Browser Console
- Open browser developer tools
- Go to Console tab
- Verify no "Failed to fetch" errors appear when using chat functions
- Check Network tab to verify requests include proper Authorization headers

## Expected Results

✅ **loadThreadMessages**: Successfully loads threads with proper Authorization header
✅ **sendMessage**: Successfully sends messages with proper Authorization header
✅ **deleteThread**: Successfully deletes threads with proper Authorization header
✅ **No console errors**: No "Failed to fetch" errors in browser console
✅ **Proper headers**: Network requests include "Authorization: Bearer <token>" header

## Troubleshooting

### If errors persist:
1. Verify that BETTER_AUTH_SECRET matches in both frontend and backend
2. Check that you're properly logged in and have a valid token in localStorage
3. Verify the token hasn't expired
4. Check that the backend server is running on the expected port

### Common Issues:
- **Token not found**: Make sure you're logged in and the token is stored properly
- **Token expired**: Login again to get a fresh token
- **Secret mismatch**: Verify BETTER_AUTH_SECRET is identical in frontend and backend
- **CORS issues**: Ensure frontend and backend URLs are properly configured

## Environment Variables

### Backend (.env)
```bash
BETTER_AUTH_SECRET=your-secret-key-here-minimum-32-characters
```

### Frontend (.env.local)
```bash
BETTER_AUTH_SECRET=your-secret-key-here-minimum-32-characters
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## API Endpoints Affected

- `GET /api/users/{user_id}/chat/threads` - Load chat threads
- `POST /api/users/{user_id}/chat/messages` - Send messages
- `DELETE /api/users/{user_id}/chat/threads/{thread_id}` - Delete threads

All these endpoints now properly authenticate using the fixed middleware and should work without "Failed to fetch" errors.