# Implementation Plan: Google OAuth Authentication Integration

**Branch**: `012-google-oauth-auth` | **Date**: 2025-12-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/012-google-oauth-auth/spec.md`

## Summary

Integrate Google OAuth 2.0 as an additional authentication method alongside existing email/password authentication. Users can sign up/sign in using their Google account via Better Auth Google provider on the frontend. Backend implements OAuth callback endpoint to verify Google ID tokens, create or authenticate users, and issue standard JWT tokens. Account linking with user confirmation is supported when Google email matches existing email/password account. Database extended with auth_provider ('local'|'google') and google_id fields.

## Technical Context

**Language/Version**: Python 3.11+ (Backend), TypeScript (Frontend with Next.js 16+)
**Primary Dependencies**: FastAPI, SQLModel, python-jose, google-auth, Better Auth (Next.js), google-oauth-provider
**Storage**: Neon Serverless PostgreSQL (existing database with User table extension)
**Testing**: Pytest (backend OAuth flow, token verification), Jest/Vitest (frontend OAuth integration)
**Target Platform**: Web application (backend: Linux server, frontend: modern browsers)
**Project Type**: Web (monorepo with separate backend/frontend)
**Performance Goals**: OAuth authentication completes in <30s (first time), <15s (subsequent); p95 <500ms for callback endpoint
**Constraints**: HTTPS required for OAuth callback; Google Cloud Console OAuth credentials required; CSRF protection mandatory; no cross-user access
**Scale/Scope**: Multi-user application with ~10k users; supports concurrent OAuth flows; stateless JWT authentication

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Spec-Driven Development (SDD) Check
- [X] Feature has complete specification (spec.md) → **PASS** (spec.md complete with clarifications resolved)
- [X] All agents/skills documented for code generation → **PASS** (will use existing backend-api-builder and frontend-feature-builder agents)
- [X] No manual code writing planned → **PASS** (all implementation via agents/skills)

### ✅ Clean Code with SRP Check
- [X] Single responsibility per module planned → **PASS** (OAuth callback endpoint, token verification service, frontend OAuth button component)
- [X] Comprehensive docstrings planned → **PASS** (all functions will include Google-style docstrings)
- [X] Short, focused functions → **PASS** (token verification, user creation, account linking as separate functions)

### ✅ Type Safety Check (NON-NEGOTIABLE)
- [X] No 'any' or 'object' types in TypeScript → **PASS** (Better Auth types, Google OAuth types fully typed)
- [X] Python type hints for all signatures → **PASS** (FastAPI dependencies, Pydantic schemas, service functions all typed)
- [X] Strict mode enabled → **PASS** (TypeScript strict mode, mypy for Python)

### ✅ Accessibility Check (WCAG 2.1 AA)
- [X] Semantic HTML for OAuth button → **PASS** ("Sign in with Google" button with proper ARIA labels)
- [X] Keyboard navigation supported → **PASS** (button accessible via Tab, activated with Enter/Space)
- [X] Screen reader compatible → **PASS** (ARIA labels describe OAuth action)

### ✅ Performance Check
- [X] OAuth flow O(1) complexity → **PASS** (database lookups by indexed google_id/email)
- [X] Backend endpoint <200ms p95 → **PASS** (token verification cached, single DB query)
- [X] Frontend rendering optimized → **PASS** (Better Auth handles OAuth client-side efficiently)

### ✅ Modular Architecture Check
- [X] Clear frontend/backend separation → **PASS** (frontend: OAuth button + Better Auth; backend: callback endpoint + token verification)
- [X] Well-defined API contracts → **PASS** (OAuth callback endpoint, account linking confirmation API)
- [X] Feature encapsulation → **PASS** (OAuth logic in dedicated routes/services, not mixed with email/password auth)

**Constitution Gate Status**: ✅ **PASS** - All principles satisfied, proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/012-google-oauth-auth/
├── spec.md              # Complete (feature specification)
├── plan.md              # This file (implementation plan)
├── research.md          # Phase 0 output (OAuth best practices, library selection)
├── data-model.md        # Phase 1 output (User model extensions, OAuth state)
├── quickstart.md        # Phase 1 output (OAuth integration guide)
├── contracts/           # Phase 1 output (API contracts for OAuth endpoints)
│   └── oauth-api.yaml   # OpenAPI spec for /auth/google/* endpoints
├── checklists/          # Validation checklists
│   └── requirements.md  # Complete (all items passed)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT YET CREATED)
```

### Source Code (repository root)

```text
backend/
├── routes/
│   └── auth.py                       # [MODIFY] Add Google OAuth callback endpoint
├── services/
│   └── oauth_service.py              # [NEW] Google OAuth token verification and user management
├── schemas/
│   └── auth.py                       # [MODIFY] Add GoogleOAuthRequest, GoogleCallbackRequest schemas
├── models.py                         # [MODIFY] Extend User model with auth_provider, google_id
├── middleware/
│   └── auth_middleware.py            # [NO CHANGE] JWT verification unchanged
├── tests/
│   ├── test_oauth_routes.py          # [NEW] Test OAuth callback, account linking
│   ├── test_oauth_service.py         # [NEW] Test token verification, user creation
│   └── test_auth_routes.py           # [MODIFY] Add tests for OAuth-specific scenarios
├── requirements.txt or pyproject.toml # [MODIFY] Add google-auth, google-auth-oauthlib
└── .env                              # [MODIFY] Add GOOGLE_OAUTH_CLIENT_ID, GOOGLE_OAUTH_CLIENT_SECRET

frontend/
├── app/
│   └── auth/
│       └── page.tsx                  # [MODIFY] Add "Sign in with Google" button
├── lib/
│   ├── auth.ts                       # [MODIFY] Configure Better Auth with Google provider
│   └── api.ts                        # [MODIFY] Add OAuth callback API client functions
├── components/
│   └── GoogleOAuthButton.tsx         # [NEW] Reusable Google OAuth button component
├── package.json                      # [MODIFY] Ensure Better Auth and dependencies installed
└── .env.local                        # [MODIFY] Add NEXT_PUBLIC_GOOGLE_OAUTH_CLIENT_ID
```

**Structure Decision**: Web application structure (Option 2 from template). Backend handles OAuth callback, token verification, and user account management. Frontend uses Better Auth Google provider for OAuth client-side flow. Both backend and frontend require environment variable configuration for Google OAuth credentials.

## Complexity Tracking

> **No constitution violations identified - this section is empty.**

All constitution principles are satisfied without requiring justifications. OAuth integration adds new functionality without violating existing architectural constraints.

## Phase 0: Research & Technology Selection

### Research Tasks

1. **Google OAuth 2.0 Integration Best Practices**
   - Research OAuth 2.0 authorization code flow
   - Identify security best practices (CSRF protection via state parameter, HTTPS requirement)
   - Determine token verification approach (google-auth library vs manual JWT verification)

2. **Better Auth Google Provider Setup**
   - Review Better Auth documentation for Google provider configuration
   - Identify required environment variables and callback URL structure
   - Determine how Better Auth handles OAuth state management

3. **Account Linking Security Patterns**
   - Research secure account linking workflows (confirmation prompts, email verification)
   - Identify risk mitigation strategies (prevent unauthorized account takeover)
   - Determine user experience patterns for linking confirmation

4. **Database Schema Evolution**
   - Research strategies for adding nullable columns to existing User table
   - Identify migration approach (alembic for SQLModel or raw SQL)
   - Determine indexing requirements for google_id column

### Technology Decisions

| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| **google-auth library** for token verification | Official Google library with automatic public key fetching and signature verification | Manual JWT verification (rejected: complex key rotation handling) |
| **Better Auth Google provider** for frontend | Integrated with existing Better Auth setup; handles OAuth flow client-side | react-google-login (rejected: deprecated), custom OAuth implementation (rejected: too complex) |
| **SQLModel nullable fields** for auth_provider/google_id | Backward compatible; existing users have NULL google_id | Separate OAuth users table (rejected: complicates user management), required fields with migration (rejected: breaks existing users) |
| **State parameter in session/Redis** for CSRF | Stateful CSRF protection; state validated on callback | JWT-based state (rejected: requires signing overhead), database state (rejected: cleanup complexity) |
| **User confirmation dialog** for account linking | Secure; prevents unauthorized linking; aligns with clarification | Auto-linking (rejected: security risk), prevent linking (rejected: poor UX) |

**Output**: research.md documenting OAuth flow, library choices, security considerations, and database migration strategy

## Critical Files

| File | Purpose | Change Type | Dependencies |
|------|---------|-------------|--------------|
| `backend/routes/auth.py` | Add OAuth callback endpoint | MODIFY | google-auth, oauth_service |
| `backend/services/oauth_service.py` | Google token verification, user creation/linking | NEW | google-auth, models.User |
| `backend/models.py` | Extend User with auth_provider, google_id | MODIFY | SQLModel migration |
| `backend/schemas/auth.py` | Add OAuth request/response schemas | MODIFY | Pydantic |
| `frontend/lib/auth.ts` | Configure Better Auth Google provider | MODIFY | better-auth |
| `frontend/app/auth/page.tsx` | Add "Sign in with Google" button | MODIFY | Better Auth client |
| `frontend/components/GoogleOAuthButton.tsx` | Reusable OAuth button component | NEW | Better Auth hooks |

## Testing Strategy

### Backend Tests

1. **test_oauth_routes.py**:
   - Test OAuth callback with valid Google ID token → creates new user
   - Test OAuth callback with existing google_id → authenticates user
   - Test OAuth callback with email match → returns linking prompt
   - Test OAuth callback with invalid state → 403 Forbidden
   - Test OAuth callback with invalid token signature → 401 Unauthorized
   - Test link-confirm endpoint with valid token → links accounts
   - Test link-confirm endpoint with confirmed=false → cancels linking

2. **test_oauth_service.py**:
   - Test Google ID token verification with valid token
   - Test Google ID token verification with expired token
   - Test user creation from Google profile data
   - Test google_id uniqueness enforcement
   - Test account linking logic (email match detection)

### Frontend Tests

1. **GoogleOAuthButton.test.tsx**:
   - Test button renders with "Sign in with Google" text
   - Test button initiates OAuth flow on click
   - Test button shows loading state during OAuth
   - Test button handles OAuth success (redirects to dashboard)
   - Test button handles OAuth cancellation (shows message)

### Integration Tests

1. **test_oauth_flow_integration.py**:
   - Full OAuth flow: frontend → Google → callback → JWT issued
   - Account linking flow: existing user → Google OAuth → confirmation → linked
   - Backward compatibility: email/password users unaffected by OAuth feature

## Deployment Checklist

- [ ] Google Cloud Console OAuth credentials configured
- [ ] Authorized redirect URIs whitelisted in Google Console
- [ ] Environment variables set in production (backend + frontend)
- [ ] Database migration applied (auth_provider, google_id columns added)
- [ ] HTTPS enabled for OAuth callback endpoint
- [ ] Better Auth configured with Google provider
- [ ] OAuth callback endpoint tested with real Google account
- [ ] Account linking confirmation flow tested
- [ ] Existing email/password authentication still works
- [ ] Logging configured for OAuth authentication events
- [ ] Rate limiting enabled for OAuth callback endpoint

## Security Considerations

1. **CSRF Protection**: State parameter generated on authorization request, validated on callback
2. **Token Verification**: Google ID token signature verified using Google's public keys
3. **HTTPS Requirement**: OAuth callback URL must use HTTPS (Google requirement)
4. **Account Linking Security**: User confirmation required before linking accounts
5. **No Token Storage**: Google access/refresh tokens not stored (only ID token verified)
6. **Rate Limiting**: OAuth callback endpoint rate-limited to prevent abuse
7. **JWT Consistency**: OAuth-authenticated users receive same JWT structure as email/password users
8. **User Isolation**: JWT token enforcement ensures users only access their own data

## Rollout Strategy

1. **Phase 1**: Deploy backend OAuth callback endpoint (no frontend changes yet)
2. **Phase 2**: Add "Sign in with Google" button to frontend auth page (feature flag enabled)
3. **Phase 3**: Monitor OAuth authentication success rate and errors for 48 hours
4. **Phase 4**: If success rate >95%, remove feature flag and make OAuth generally available
5. **Rollback Plan**: If critical issues, disable OAuth button in frontend (backend remains deployed)

## Success Metrics

- [ ] Google OAuth sign-up completes in <30 seconds (measured)
- [ ] Google OAuth sign-in completes in <15 seconds (measured)
- [ ] 100% of existing email/password users can still sign in (verified)
- [ ] OAuth authentication success rate >99% (monitored)
- [ ] Zero duplicate accounts created via OAuth (verified in database)
- [ ] CSRF protection validated (security testing)
- [ ] Account linking confirmation flow works (tested)

---

**Phase 0 Status**: Research outline complete - ready for research.md generation
**Phase 1 Status**: Awaiting Phase 0 completion before generating data-model.md and contracts/
**Next Command**: Generate research.md, data-model.md, contracts/, and quickstart.md (continuing with Phase 0 and Phase 1)
