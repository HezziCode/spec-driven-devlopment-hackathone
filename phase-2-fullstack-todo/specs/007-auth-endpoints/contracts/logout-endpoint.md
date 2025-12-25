# API Contract: POST /auth/logout

**Endpoint**: `POST /auth/logout`
**Purpose**: Signal user logout (stateless JWT - client-side token clearing)
**Authentication**: None required (public endpoint, stateless operation)

## Request

### Method
```
POST
```

### Path
```
/auth/logout
```

### Headers
```
None required
```

### Body
```
Empty body (no request payload needed)
```

### Request Example
```bash
curl -X POST http://localhost:8000/auth/logout
```

**Note**: Authorization header is optional. Since JWTs are stateless, logout is a client-side operation. This endpoint exists for API consistency and future enhancements (e.g., token blacklisting).

## Response

### Success Response (200 OK)

**Status Code**: `200 OK`

**Body Schema**:
```json
{
  "message": "Successfully logged out"
}
```

**Body Example**:
```json
{
  "message": "Successfully logged out"
}
```

**Response Guarantees**:
- Always returns 200 OK (never fails)
- No server-side state modified (stateless JWT approach)
- Client expected to discard token locally

### Error Responses

**None** - This endpoint always returns 200 OK

**Rationale**: Since JWT tokens are stateless, there's no server-side session to invalidate. The logout operation is purely client-side (clearing stored token). The endpoint always succeeds to provide consistent API behavior.

## Business Logic

### Execution Flow

1. **Request Received**
   - No validation required (empty body)
   - No authentication required (public endpoint)

2. **Return Success**
   - Return 200 OK with success message
   - Total operation time: < 5ms (no database or crypto operations)

### What Actually Happens on Logout?

**Server Side**:
- Nothing - JWT tokens are stateless
- No database operations
- No token revocation (not implemented in Phase 2)
- Simply returns success message

**Client Side** (frontend responsibility):
- Clear stored JWT token from localStorage/sessionStorage/cookies
- Redirect to login page
- Clear any cached user data

### Why This Endpoint Exists

1. **API Consistency**: Provides standard REST endpoint for logout operation
2. **Future Enhancements**: Enables token blacklisting/revocation in future phases
3. **Client Simplicity**: Single logout API call handles both client and server concerns
4. **Audit Trail**: Can be logged for security monitoring (future enhancement)

### JWT Token After Logout

**Important**: The JWT token remains technically valid until expiration (7 days). The server has no knowledge of logout and will continue accepting the token if presented.

**Security Implications**:
- Client MUST clear token from storage after logout
- If token is intercepted before logout, it can still be used
- Token revocation/blacklisting is a future security enhancement

## Testing Examples

### Test Case 1: Basic Logout

**Request**:
```bash
curl -X POST http://localhost:8000/auth/logout
```

**Expected Response**: 200 OK with success message

### Test Case 2: Logout with Authorization Header (Optional)

**Request**:
```bash
curl -X POST http://localhost:8000/auth/logout \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Expected Response**: 200 OK with success message (header ignored)

### Test Case 3: Multiple Logout Calls

**Request**: Call logout endpoint multiple times in succession

**Expected Response**: Each call returns 200 OK (idempotent operation)

## Frontend Integration

### Example: React Logout Handler

```typescript
async function handleLogout() {
  try {
    // Call logout endpoint
    await fetch('http://localhost:8000/auth/logout', {
      method: 'POST',
    });

    // Clear stored token
    localStorage.removeItem('auth_token');

    // Clear user state
    setUser(null);

    // Redirect to login
    router.push('/login');
  } catch (error) {
    // Logout endpoint never fails, but handle network errors
    console.error('Logout error:', error);
    // Still clear token and redirect
    localStorage.removeItem('auth_token');
    router.push('/login');
  }
}
```

### Example: Full Logout Flow

```javascript
// 1. Call logout API
const response = await fetch('/auth/logout', { method: 'POST' });
// Response: { "message": "Successfully logged out" }

// 2. Clear token from storage
localStorage.removeItem('auth_token');
// OR
sessionStorage.removeItem('auth_token');
// OR
document.cookie = 'auth_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';

// 3. Clear application state
dispatch({ type: 'LOGOUT' }); // Redux/Zustand
// OR
setUser(null); // React state

// 4. Redirect to login page
window.location.href = '/login';
// OR
router.push('/login'); // Next.js router
```

## Security Considerations

### Limitations

**No Server-Side Token Revocation**: In Phase 2, tokens cannot be revoked before expiration. If a user's device is compromised after logout, the token can still be used until it expires (7 days).

**Mitigation Strategies**:
- Use short-lived tokens (7 days is reasonable balance)
- Implement refresh token pattern (future enhancement)
- Implement token blacklist (future enhancement)
- Use secure token storage (httpOnly cookies recommended)

### Future Enhancements

**Phase 3+ Features**:
1. **Token Blacklist**: Store logged-out tokens in Redis with TTL matching token expiration
2. **Refresh Tokens**: Short-lived access tokens (15 minutes) + long-lived refresh tokens (30 days)
3. **Device Tracking**: Track active sessions per device, allow revocation
4. **Audit Logging**: Log all logout events for security monitoring

## Performance

**Response Time**: < 50ms (typically < 5ms)
**Resource Usage**: Minimal (no database or crypto operations)
**Scalability**: Infinite (stateless, no server-side storage)

## Comparison with Session-Based Logout

| Aspect | JWT Logout (Stateless) | Session Logout (Stateful) |
|--------|------------------------|---------------------------|
| Server Storage | None | Must store session ID |
| Revocation | Not possible (Phase 2) | Immediate |
| Performance | Fast (no DB lookup) | Slower (session deletion) |
| Scalability | Excellent (no state) | Good (needs session store) |
| Security | Token valid until exp | Token invalid immediately |

## Notes

- This endpoint is intentionally simple for Phase 2
- Always returns 200 OK for consistency
- No authentication required (stateless operation)
- Client responsible for clearing stored token
- Token remains valid until expiration
- Endpoint enables future token revocation features
- Can be extended with blacklist/refresh token in future phases
- Useful for API completeness and future monitoring/logging
