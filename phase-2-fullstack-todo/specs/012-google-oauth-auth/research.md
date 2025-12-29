# Research: Google OAuth Authentication Integration

**Feature**: 012-google-oauth-auth
**Date**: 2025-12-26
**Research Phase**: Phase 0 of Implementation Plan

## Overview

This document consolidates research findings for integrating Google OAuth 2.0 authentication into the TaskWave application. Research focuses on OAuth 2.0 best practices, library selection, security considerations, and database schema evolution strategies.

## 1. Google OAuth 2.0 Integration Best Practices

### OAuth 2.0 Authorization Code Flow

**Decision**: Use Authorization Code Flow (not Implicit Flow)

**Rationale**:
- Most secure OAuth 2.0 flow for web applications
- Authorization code exchanged for tokens on backend (client secret protected)
- Tokens never exposed to browser/frontend
- Industry standard for confidential clients

**Flow Steps**:
1. User clicks "Sign in with Google" → Frontend redirects to Google authorization endpoint
2. User grants consent on Google's page
3. Google redirects back with authorization code + state parameter
4. Backend exchanges code for access token and ID token (using client secret)
5. Backend verifies ID token signature and extracts user claims
6. Backend creates/authenticates user and issues JWT token

**Key Parameters**:
- `response_type=code` (authorization code flow)
- `client_id` (public, identifies application)
- `redirect_uri` (must match whitelisted URI in Google Console)
- `scope=openid email profile` (user identity and email)
- `state` (random string for CSRF protection)

**Alternatives Considered**:
- **Implicit Flow**: Rejected (deprecated by OAuth 2.0 Security Best Practices, tokens exposed in URL)
- **PKCE Flow**: Not needed for confidential clients with client secret

### Security Best Practices

1. **CSRF Protection via State Parameter**
   - Generate random UUID as state before redirecting to Google
   - Store state in session/Redis with 10-minute expiration
   - Validate state matches on callback
   - Prevents attacker from injecting their own authorization code

2. **HTTPS Requirement**
   - OAuth redirect URIs must use HTTPS (enforced by Google)
   - Prevents man-in-the-middle attacks
   - Development exception: `http://localhost` allowed for testing

3. **Token Verification**
   - Verify ID token signature using Google's public keys
   - Validate `iss` (issuer) is `https://accounts.google.com`
   - Validate `aud` (audience) matches application's client ID
   - Validate `exp` (expiration) is in the future
   - Use official Google library to handle key rotation automatically

4. **No Access Token Storage**
   - Only verify ID token for user identity
   - Do not store Google access/refresh tokens (not needed for authentication)
   - Reduces security risk and complexity

### Token Verification Approach

**Decision**: Use `google-auth` library for ID token verification

**Rationale**:
- Official Google library maintained by Google
- Automatically fetches and caches Google's public keys
- Handles key rotation (Google rotates keys periodically)
- Validates all required claims (iss, aud, exp, iat)
- Production-ready error handling

**Implementation**:
```python
from google.auth.transport import requests
from google.oauth2 import id_token

def verify_google_token(token: str, client_id: str) -> dict:
    """
    Verify Google ID token and return user claims.

    Raises:
        ValueError: If token is invalid or expired
    """
    idinfo = id_token.verify_oauth2_token(token, requests.Request(), client_id)

    # Validate issuer
    if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
        raise ValueError('Invalid issuer')

    return idinfo  # Contains: sub (google_id), email, name, picture, etc.
```

**Alternatives Considered**:
- **Manual JWT verification with PyJWT**: Rejected (complex key fetching and rotation)
- **google-auth-oauthlib**: Rejected (adds unnecessary OAuth flow complexity; google-auth sufficient)

## 2. Better Auth Google Provider Setup

### Better Auth Integration

**Decision**: Use Better Auth's Google provider (part of better-auth library)

**Rationale**:
- Already integrated in application for email/password auth
- Handles OAuth authorization URL generation
- Manages OAuth state parameter automatically
- Provides React hooks for OAuth flow
- Consistent authentication API across providers

### Configuration

**File**: `frontend/lib/auth.ts`

```typescript
import { betterAuth } from "better-auth";
import { google } from "better-auth/providers";

export const auth = betterAuth({
  database: {
    // Existing database config...
  },
  emailAndPassword: {
    // Existing email/password config...
  },
  socialProviders: {
    google: {
      clientId: process.env.NEXT_PUBLIC_GOOGLE_OAUTH_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_OAUTH_CLIENT_SECRET!,
      redirectURI: `${process.env.BETTER_AUTH_URL}/api/auth/callback/google`,
    },
  },
});

export const { signIn, signUp, signOut, useSession } = auth;
```

**Callback URL Structure**: Better Auth expects callbacks at `/api/auth/callback/{provider}`
- Example: `https://yourdomain.com/api/auth/callback/google`
- Must be whitelisted in Google Cloud Console OAuth settings

### State Management

**How Better Auth Handles State**:
- Automatically generates state parameter when initiating OAuth flow
- Stores state in session (encrypted cookie or server-side session)
- Validates state on callback
- No manual state management required

**Decision**: Trust Better Auth's built-in state management

**Rationale**:
- Library handles CSRF protection correctly
- Reduces implementation complexity
- Standard practice for OAuth libraries

### Frontend OAuth Button

**Implementation Approach**:
```typescript
// components/GoogleOAuthButton.tsx
import { signIn } from "@/lib/auth";

export function GoogleOAuthButton() {
  const handleGoogleSignIn = async () => {
    try {
      await signIn.social({
        provider: "google",
        callbackURL: "/tasks",  // Redirect after success
      });
    } catch (error) {
      // Handle OAuth errors (user cancelled, network failure, etc.)
      console.error("Google OAuth failed:", error);
    }
  };

  return (
    <button
      onClick={handleGoogleSignIn}
      className="w-full px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50"
      aria-label="Sign in with Google"
    >
      <div className="flex items-center justify-center gap-3">
        <img src="/google-icon.svg" alt="" className="w-5 h-5" />
        <span>Sign in with Google</span>
      </div>
    </button>
  );
}
```

**Alternatives Considered**:
- **@react-oauth/google**: Rejected (deprecated, migrated to @react-oauth/google v2 which is less maintained)
- **Custom OAuth implementation**: Rejected (complex, error-prone, reinvents wheel)

## 3. Account Linking Security Patterns

### Linking Strategy

**Decision**: Require user confirmation before linking accounts (per spec clarification)

**Rationale**:
- Prevents unauthorized account takeover if email is compromised
- Aligns with security best practices (OWASP guidelines)
- User retains control over account associations
- Better user experience than preventing linking entirely

### Linking Flow

1. User with email/password account tries to sign in with Google (same email)
2. Backend detects email match during OAuth callback
3. Backend returns `requires_confirmation: true` response with temporary linking token
4. Frontend displays confirmation dialog: "Account exists with this email. Link your Google account? [Yes] [No]"
5. If user clicks Yes:
   - Frontend sends linking token to `/auth/google/link-confirm` endpoint
   - Backend verifies token, links google_id to existing user
   - Backend issues JWT token for authenticated user
6. If user clicks No:
   - Frontend clears OAuth state
   - User returned to sign-in page

### Linking Token Security

**Temporary Linking Token**:
- JWT signed with BETTER_AUTH_SECRET
- Contains: `user_id`, `google_id`, `exp` (5-minute expiration)
- Single-use token (invalidated after confirmation)
- Prevents replay attacks

**Implementation**:
```python
def generate_linking_token(user_id: UUID, google_id: str) -> str:
    """Generate temporary token for account linking confirmation."""
    payload = {
        "user_id": str(user_id),
        "google_id": google_id,
        "exp": datetime.utcnow() + timedelta(minutes=5),
        "purpose": "link_google_account"
    }
    return jwt.encode(payload, BETTER_AUTH_SECRET, algorithm="HS256")
```

### Risk Mitigation

**Prevented Attacks**:
1. **Unauthorized Linking**: Attacker cannot link their Google account to victim's email/password account without victim's active confirmation
2. **Email Enumeration**: Backend returns generic "OAuth failed" error (does not reveal if email exists)
3. **Replay Attacks**: Linking token expires after 5 minutes and is single-use

**Alternatives Considered**:
- **Auto-linking with email match**: Rejected (security risk if email compromised)
- **Prevent linking entirely**: Rejected (poor UX, forces users to create duplicate accounts)
- **Email verification for linking**: Considered but deferred (adds complexity; confirmation prompt sufficient)

## 4. Database Schema Evolution

### Schema Changes Required

**User Table Extensions**:
```sql
ALTER TABLE user ADD COLUMN auth_provider VARCHAR(10) DEFAULT 'local';
ALTER TABLE user ADD COLUMN google_id VARCHAR(255) UNIQUE;
ALTER TABLE user ADD COLUMN oauth_data JSONB;
ALTER TABLE user ALTER COLUMN password_hash DROP NOT NULL;
CREATE INDEX idx_user_google_id ON user(google_id);
CREATE INDEX idx_user_auth_provider ON user(auth_provider);
```

**Field Descriptions**:
- `auth_provider`: Enum ('local', 'google') indicating primary auth method
- `google_id`: Google user ID (sub claim from ID token), unique across all users
- `oauth_data`: Optional JSON field for additional OAuth metadata (profile picture URL, last OAuth login timestamp)
- `password_hash`: Now nullable (NULL for OAuth-only users)

### Migration Strategy

**Decision**: Use nullable columns with default values (backward compatible)

**Rationale**:
- Existing users automatically get `auth_provider='local'` and `google_id=NULL`
- No data migration required for existing users
- New OAuth users get `auth_provider='google'` and non-null `google_id`
- Users who link accounts have both `password_hash` and `google_id` populated

**Backward Compatibility**:
- Existing email/password authentication code unchanged
- Password validation still checks `password_hash IS NOT NULL`
- OAuth users without password cannot use email/password sign-in (enforced in login endpoint)

### Indexing Strategy

**Indexes Required**:
1. `idx_user_google_id ON user(google_id)`: Fast lookup for OAuth sign-in
2. `idx_user_auth_provider ON user(auth_provider)`: Analytics queries (count OAuth vs local users)
3. Existing `idx_user_email`: Reused for account linking detection

**Performance Impact**:
- OAuth sign-in: O(1) lookup by google_id (indexed)
- Account linking check: O(1) lookup by email (already indexed)
- Minimal write overhead (two additional indexes updated on user creation)

### Migration Tool

**Decision**: Use Alembic for database migrations (SQLModel compatible)

**Rationale**:
- Standard Python migration tool
- Supports SQLModel models
- Rollback capability
- Version control for schema changes

**Migration File**:
```python
# alembic/versions/add_oauth_fields.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('user', sa.Column('auth_provider', sa.String(10), server_default='local'))
    op.add_column('user', sa.Column('google_id', sa.String(255), unique=True, nullable=True))
    op.add_column('user', sa.Column('oauth_data', sa.JSON, nullable=True))
    op.alter_column('user', 'password_hash', nullable=True)
    op.create_index('idx_user_google_id', 'user', ['google_id'])
    op.create_index('idx_user_auth_provider', 'user', ['auth_provider'])

def downgrade():
    op.drop_index('idx_user_auth_provider')
    op.drop_index('idx_user_google_id')
    op.alter_column('user', 'password_hash', nullable=False)
    op.drop_column('user', 'oauth_data')
    op.drop_column('user', 'google_id')
    op.drop_column('user', 'auth_provider')
```

**Alternatives Considered**:
- **Separate OAuth users table**: Rejected (complicates user management, joins required)
- **Required fields with data migration**: Rejected (breaks existing users during migration)
- **SQLModel create_all()**: Rejected (no rollback, no version control)

## 5. Environment Variables Required

### Backend Environment Variables

**File**: `backend/.env`

```
# Existing variables (unchanged)
DATABASE_URL=postgresql://user:pass@neon-host/db
BETTER_AUTH_SECRET=your-32-character-secret-key

# New OAuth variables
GOOGLE_OAUTH_CLIENT_ID=123456789-abc123.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=GOCSPX-abc123def456
```

### Frontend Environment Variables

**File**: `frontend/.env.local`

```
# Existing variables (unchanged)
BETTER_AUTH_URL=http://localhost:3000  # Or production URL

# New OAuth variables
NEXT_PUBLIC_GOOGLE_OAUTH_CLIENT_ID=123456789-abc123.apps.googleusercontent.com
```

**Note**: Frontend only needs client ID (public); client secret stays on backend (private)

### Google Cloud Console Setup

1. Navigate to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project: "TaskWave Production"
3. Enable APIs: Google+ API (for OAuth scopes)
4. Create OAuth 2.0 Client ID:
   - Application type: Web application
   - Name: TaskWave OAuth Client
   - Authorized JavaScript origins: `https://yourdomain.com`
   - Authorized redirect URIs: `https://yourdomain.com/api/auth/callback/google`
5. Copy Client ID and Client Secret to environment variables

**Development Setup**:
- Authorized JavaScript origins: `http://localhost:3000`
- Authorized redirect URIs: `http://localhost:3000/api/auth/callback/google`
- Use separate OAuth client for development (recommended) or same client with multiple redirect URIs

## 6. Testing Strategy

### Unit Tests (Backend)

**File**: `backend/tests/test_oauth_service.py`

Test Cases:
1. `test_verify_valid_google_token()`: Verify valid ID token returns user claims
2. `test_verify_expired_token()`: Expired token raises ValueError
3. `test_verify_invalid_signature()`: Tampered token raises ValueError
4. `test_verify_wrong_audience()`: Token for different client_id raises ValueError
5. `test_create_user_from_google_profile()`: Creates User with auth_provider='google'
6. `test_link_google_to_existing_user()`: Updates existing user with google_id
7. `test_google_id_uniqueness()`: Duplicate google_id raises IntegrityError

**Mocking Strategy**:
- Mock `google.oauth2.id_token.verify_oauth2_token()` to return fake claims
- Mock database session for user creation/updates
- Use pytest fixtures for test users and Google profiles

### Integration Tests (Backend)

**File**: `backend/tests/test_oauth_routes.py`

Test Cases:
1. `test_oauth_callback_new_user()`: POST /auth/google/callback with new Google user → 201 Created
2. `test_oauth_callback_existing_user()`: POST /auth/google/callback with existing google_id → 200 OK
3. `test_oauth_callback_linking_prompt()`: POST /auth/google/callback with email match → returns `requires_confirmation`
4. `test_oauth_callback_invalid_state()`: POST /auth/google/callback with wrong state → 403 Forbidden
5. `test_link_confirm_accept()`: POST /auth/google/link-confirm with confirmed=true → links accounts
6. `test_link_confirm_reject()`: POST /auth/google/link-confirm with confirmed=false → cancels linking
7. `test_link_confirm_expired_token()`: POST /auth/google/link-confirm with expired token → 401 Unauthorized

**Test Setup**:
- Use TestClient from FastAPI
- Create test database with User table (sqlite in-memory for speed)
- Generate valid linking tokens for testing confirmation flow

### End-to-End Tests (Frontend)

**File**: `frontend/tests/GoogleOAuthButton.test.tsx`

Test Cases:
1. `test_button_renders()`: Button displays "Sign in with Google" text
2. `test_button_click_initiates_oauth()`: Click triggers Better Auth signIn.social()
3. `test_oauth_success_redirects()`: Successful OAuth redirects to /tasks
4. `test_oauth_cancelled()`: User cancels OAuth → shows appropriate message
5. `test_linking_confirmation_dialog()`: Email match → displays confirmation dialog
6. `test_linking_accept()`: User confirms → accounts linked and authenticated
7. `test_linking_reject()`: User rejects → returns to sign-in page

**Testing Tools**:
- Jest + React Testing Library
- Mock Better Auth signIn.social() function
- Mock API responses for linking flow

## 7. Performance Considerations

### OAuth Callback Latency

**Target**: <500ms p95 for `/auth/google/callback` endpoint

**Optimizations**:
1. **Google public key caching**: `google-auth` library caches keys (reduces external API calls)
2. **Single database query**: Lookup by google_id or email (both indexed)
3. **JWT generation**: O(1) operation, minimal CPU overhead
4. **No external API calls**: Only ID token verification (uses cached keys)

**Bottlenecks to Avoid**:
- Multiple database round-trips (batch user creation + JWT generation in single transaction)
- Synchronous Google API calls (use cached public keys, not real-time verification)

### Frontend OAuth Flow Performance

**Target**: <30s first-time OAuth, <15s subsequent OAuth

**Performance Factors**:
1. **Google consent screen load time**: ~2-5s (controlled by Google)
2. **User interaction time**: ~5-10s (user clicks "Allow")
3. **Backend callback processing**: <500ms (optimized above)
4. **Frontend redirect**: <1s

**Optimizations**:
- **Preload Google OAuth library**: Include in initial bundle for faster authorization URL generation
- **Optimistic UI**: Show loading state immediately on button click (perceived performance)
- **Skip consent on repeat**: Google skips consent screen if user previously granted permissions

## 8. Security Checklist

- [X] CSRF protection via state parameter (handled by Better Auth)
- [X] ID token signature verification (google-auth library)
- [X] HTTPS requirement for production OAuth callback
- [X] Client secret never exposed to frontend
- [X] Linking tokens expire after 5 minutes
- [X] Linking tokens are single-use
- [X] No storage of Google access/refresh tokens
- [X] Rate limiting on OAuth callback endpoint (prevents brute-force)
- [X] google_id uniqueness enforced at database level
- [X] User confirmation required for account linking
- [X] Generic error messages (no email enumeration)
- [X] JWT structure consistent between OAuth and email/password

## 9. Documentation Requirements

### Developer Documentation

**Files to Create**:
1. `quickstart.md`: Step-by-step guide for setting up Google OAuth locally
2. `oauth-api.yaml`: OpenAPI specification for OAuth endpoints
3. `data-model.md`: Updated User model schema with OAuth fields

### User Documentation

**Sections to Add to README**:
1. "Signing in with Google": Explains OAuth option to end users
2. "Linking Your Google Account": Instructions for linking existing account
3. "Unlinking Google Account": Future feature (not in scope for this phase)

## Conclusion

All research tasks completed. Key decisions:
1. Use `google-auth` library for secure token verification
2. Better Auth Google provider for frontend OAuth flow
3. Nullable database columns for backward compatibility
4. User confirmation required for account linking (security + UX balance)
5. Alembic for database schema migrations

**Next Steps**: Proceed to Phase 1 (data-model.md, contracts/, quickstart.md generation)

---

**Research Status**: ✅ Complete
**Phase 0 Output**: This file (research.md)
**Ready for Phase 1**: Yes
