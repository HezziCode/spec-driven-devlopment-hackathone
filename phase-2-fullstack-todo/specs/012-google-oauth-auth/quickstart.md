# Quickstart Guide: Google OAuth Authentication Integration

**Feature**: 012-google-oauth-auth
**Last Updated**: 2025-12-26

## Prerequisites

- Existing TaskWave application with email/password authentication
- Google account for testing
- Access to Google Cloud Console
- HTTPS enabled (production) or http://localhost (development)

## Step 1: Google Cloud Console Setup

### Create OAuth 2.0 Credentials

1. Navigate to [Google Cloud Console](https://console.cloud.google.com/)
2. Select or create project: "TaskWave"
3. Go to **APIs & Services** → **Credentials**
4. Click **Create Credentials** → **OAuth Client ID**
5. Configure OAuth consent screen (if first time):
   - User Type: External
   - App name: TaskWave
   - User support email: your-email@example.com
   - Developer contact: your-email@example.com
   - Scopes: email, profile, openid
   - Save and continue
6. Create OAuth Client ID:
   - Application type: **Web application**
   - Name: TaskWave OAuth Client
   - **Authorized JavaScript origins**:
     - Development: `http://localhost:3000`
     - Production: `https://yourdomain.com`
   - **Authorized redirect URIs**:
     - Development: `http://localhost:3000/api/auth/callback/google`
     - Production: `https://yourdomain.com/api/auth/callback/google`
   - Click **Create**
7. Copy **Client ID** and **Client Secret**

## Step 2: Environment Variables

### Backend Configuration

**File**: `backend/.env`

```bash
# Existing variables
DATABASE_URL=postgresql://user:pass@neon-host/db
BETTER_AUTH_SECRET=your-32-character-secret-key

# Add Google OAuth credentials
GOOGLE_OAUTH_CLIENT_ID=123456789-abc123.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=GOCSPX-abc123def456
```

### Frontend Configuration

**File**: `frontend/.env.local`

```bash
# Existing variables
BETTER_AUTH_URL=http://localhost:3000

# Add Google OAuth client ID (public, safe for frontend)
NEXT_PUBLIC_GOOGLE_OAUTH_CLIENT_ID=123456789-abc123.apps.googleusercontent.com
```

**Important**: Never commit `.env` files to version control. Add to `.gitignore`.

## Step 3: Database Migration

Run database migration to add OAuth fields:

```bash
cd backend
uv run alembic upgrade head
```

This adds:
- `auth_provider` column (default: 'local')
- `google_id` column (unique, nullable)
- `oauth_data` column (JSON, nullable)
- Makes `password_hash` nullable
- Creates indexes on `google_id` and `auth_provider`

Verify migration:
```bash
uv run python -c "from models import User; print(User.__table__.columns)"
```

## Step 4: Install Dependencies

### Backend

```bash
cd backend
uv add google-auth google-auth-oauthlib
```

### Frontend

Better Auth is already installed. Verify:
```bash
cd frontend
npm list better-auth
```

If missing:
```bash
npm install better-auth
```

## Step 5: Test OAuth Flow

### Backend Test

```bash
cd backend
uv run pytest tests/test_oauth_routes.py -v
```

Expected output:
- `test_oauth_callback_new_user` ✅ PASSED
- `test_oauth_callback_existing_user` ✅ PASSED
- `test_oauth_callback_linking_prompt` ✅ PASSED
- `test_oauth_callback_invalid_state` ✅ PASSED
- `test_link_confirm_accept` ✅ PASSED

### Frontend Manual Test

1. Start backend: `cd backend && uvicorn main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Navigate to `http://localhost:3000`
4. Click "Sign in with Google"
5. Complete Google OAuth consent screen
6. Verify redirect to `/tasks` dashboard
7. Verify JWT token in localStorage
8. Check database: User record created with `auth_provider='google'`

## Step 6: Account Linking Test

1. Create email/password user:
   - Sign up with email `test@example.com` and password
   - Log out
2. Attempt Google OAuth sign-in:
   - Use Google account with same email `test@example.com`
   - **Expected**: Confirmation dialog appears
   - Click "Yes" to link accounts
3. Verify linking:
   - Sign out
   - Sign in with email/password → ✅ Works
   - Sign out
   - Sign in with Google → ✅ Works (same user account)

## Troubleshooting

### Common Issues

**Issue**: "redirect_uri_mismatch" error from Google

**Solution**: Verify redirect URI in Google Cloud Console exactly matches Better Auth callback URL:
- Format: `http://localhost:3000/api/auth/callback/google`
- Must include protocol (http/https), domain, and full path
- No trailing slash

---

**Issue**: "Invalid token signature" error

**Solution**:
- Verify GOOGLE_OAUTH_CLIENT_ID matches the client ID from Google Console
- Check system clock is accurate (JWT exp validation depends on it)
- Verify google-auth library is installed: `uv pip list | grep google-auth`

---

**Issue**: Database error "column auth_provider does not exist"

**Solution**: Run migration:
```bash
cd backend
uv run alembic upgrade head
```

---

**Issue**: Better Auth not configured

**Solution**: Verify `frontend/lib/auth.ts` includes Google provider:
```typescript
import { google } from "better-auth/providers";

export const auth = betterAuth({
  socialProviders: {
    google: {
      clientId: process.env.NEXT_PUBLIC_GOOGLE_OAUTH_CLIENT_ID!,
      // ...
    },
  },
});
```

## Security Checklist

Before deploying to production:

- [ ] HTTPS enabled for OAuth callback URL (required by Google)
- [ ] Google Cloud Console redirect URIs whitelisted
- [ ] Client secret stored securely in environment variables (never in code)
- [ ] State parameter validation implemented (CSRF protection)
- [ ] Rate limiting enabled on OAuth callback endpoint
- [ ] Linking tokens expire after 5 minutes
- [ ] OAuth authentication events logged
- [ ] Error messages do not reveal user email existence

## Support

For issues or questions:
- Review [spec.md](./spec.md) for requirements
- Review [plan.md](./plan.md) for technical approach
- Review [research.md](./research.md) for implementation decisions
- Check Google OAuth 2.0 documentation: https://developers.google.com/identity/protocols/oauth2
- Check Better Auth documentation: https://better-auth.com/docs

---

**Quickstart Status**: ✅ Complete
**Ready for Development**: Yes
