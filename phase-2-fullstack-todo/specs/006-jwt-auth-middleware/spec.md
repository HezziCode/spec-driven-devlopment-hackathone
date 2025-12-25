# Feature Specification: JWT Authentication Middleware

**Feature Branch**: `006-jwt-auth-middleware`
**Created**: 2025-12-24
**Status**: Draft
**Input**: User description: "JWT Authentication Middleware: Implement JWT token verification middleware for FastAPI backend - Create auth_middleware.py that intercepts all API requests except /auth/* endpoints, extracts Bearer token from Authorization header, verifies JWT signature using BETTER_AUTH_SECRET environment variable with python-jose library, decodes token payload to extract user_id and email, validates token expiration, attaches authenticated user to request.state.user for route handler access, returns 401 Unauthorized for missing token, 401 Unauthorized for invalid/expired token, 400 Bad Request for malformed token. Create jwt_utils.py helper module with functions decode_token(token: str) returns dict, verify_token(token: str) returns bool, extract_user_from_token(token: str) returns User object or None. Configure middleware in FastAPI app to run on all routes except authentication routes. Acceptance criteria: Middleware registered in FastAPI app, JWT tokens verified correctly using shared secret, user context attached to all protected requests, proper error responses for auth failures with error format {error: string, code: string, timestamp: ISO8601}, test cases for valid token passing, expired token failing 401, missing token failing 401, malformed token failing 400, middleware bypasses /auth/* routes."

## User Scenarios & Testing

### User Story 1 - API Developer Protects Endpoints with JWT (Priority: P1)

As an API developer, I need JWT authentication middleware that automatically validates tokens on protected endpoints so that I can ensure only authenticated users access their data without writing authentication logic in every route handler.

**Why this priority**: This is the security foundation for the entire API. Without JWT verification, all endpoints would be vulnerable to unauthorized access. This must be implemented before any protected endpoints (task CRUD, user management) can be safely deployed.

**Independent Test**: Can be fully tested by making API requests with valid JWT tokens (should pass through middleware), invalid tokens (should reject with 401), missing tokens (should reject with 401), and malformed tokens (should reject with 400), to authentication endpoints (should bypass middleware), verifying user context is attached to request.state for protected endpoints. Delivers value by providing centralized authentication enforcement that protects all API routes automatically.

**Acceptance Scenarios**:

1. **Given** a valid JWT token in the Authorization header, **When** a request is made to a protected endpoint like /api/users/{user_id}/tasks, **Then** the middleware decodes the token, extracts user_id and email from payload, attaches them to request.state, and allows the request to proceed to the route handler
2. **Given** a request with no Authorization header, **When** a request is made to a protected endpoint, **Then** the middleware returns 401 Unauthorized with error response {error: "Missing authentication token", code: "UNAUTHORIZED", timestamp: ISO8601 format}
3. **Given** an expired JWT token in the Authorization header, **When** a request is made to a protected endpoint, **Then** the middleware verifies the token signature, detects expiration, and returns 401 Unauthorized with error "Token expired"
4. **Given** a JWT token with invalid signature (tampered or wrong secret), **When** a request is made to a protected endpoint, **Then** the middleware signature verification fails and returns 401 Unauthorized with error "Invalid token signature"
5. **Given** a malformed Authorization header (missing "Bearer " prefix or invalid format), **When** a request is made to a protected endpoint, **Then** the middleware returns 400 Bad Request with error "Malformed authorization header"
6. **Given** any request to /auth/signup or /auth/login or /auth/logout endpoints, **When** the request is processed, **Then** the middleware bypasses authentication checks and allows the request to proceed without requiring a token
7. **Given** a valid JWT token attached to a request, **When** the route handler executes, **Then** it can access request.state.user_id and request.state.email to identify the authenticated user

---

### User Story 2 - Security Engineer Validates Token Security (Priority: P2)

As a security engineer, I need comprehensive JWT token validation utilities so that I can ensure tokens are cryptographically verified, properly formatted, and contain valid user information before granting access.

**Why this priority**: Building on P1 middleware, this provides the utility functions for secure token handling. These utilities enable robust token validation, user information extraction, and support future features like token refresh and revocation.

**Independent Test**: Can be fully tested by calling utility functions with various token inputs: valid tokens return correct user data, expired tokens return False on verification, invalid signatures fail verification, malformed tokens raise appropriate exceptions, user extraction from token returns User model or None. Delivers value by providing reusable, well-tested token handling functions that can be used across the application.

**Acceptance Scenarios**:

1. **Given** a valid JWT token string, **When** decode_token(token) function is called, **Then** it returns a dictionary containing payload fields including "sub" (user_id), "email", "exp" (expiration), and "iat" (issued at) with all values correctly decoded
2. **Given** a JWT token signed with correct BETTER_AUTH_SECRET, **When** verify_token(token) function is called, **Then** it verifies the signature matches, checks expiration is in the future, and returns True
3. **Given** an expired JWT token, **When** verify_token(token) is called, **Then** it detects the "exp" claim is in the past and returns False without raising an exception
4. **Given** a JWT token with valid user_id in payload, **When** extract_user_from_token(token) is called with database session, **Then** it decodes the token, queries the User table for the user_id, and returns the User model instance if found
5. **Given** a JWT token with user_id that doesn't exist in database, **When** extract_user_from_token(token) is called, **Then** it queries the database, finds no matching user, and returns None
6. **Given** a JWT token with invalid signature (wrong secret or tampered), **When** any utility function attempts to decode it, **Then** it raises JWTError which can be caught and handled appropriately by the calling code

---

### Edge Cases

- What happens when BETTER_AUTH_SECRET environment variable is missing? Middleware should raise clear configuration error on startup indicating the secret is required for JWT verification
- How does the system handle requests with multiple Authorization headers? Middleware should use the first Authorization header or return 400 for ambiguous auth
- What happens when JWT token payload is missing required fields (sub, email)? decode_token should return dict with missing keys as None, extract_user_from_token should return None
- How does the middleware handle very large JWT tokens (> 4KB)? Token extraction should work regardless of size, but extremely large tokens might indicate malicious payload
- What happens if the JWT uses a different signing algorithm than HS256? Verification should fail with invalid signature error as only HS256 is supported
- How does the system handle concurrent requests with different tokens? Each request has isolated request.state, so concurrent requests are handled independently without interference
- What happens when a route handler tries to access request.state.user_id but token wasn't provided? If middleware ran, state will have None values; if middleware was bypassed (auth routes), state might not have user_id attribute at all

## Requirements

### Functional Requirements

- **FR-001**: System MUST provide FastAPI middleware that intercepts all incoming HTTP requests before they reach route handlers
- **FR-002**: Middleware MUST check request path and bypass authentication for all requests to /auth/* endpoints allowing signup and login without tokens
- **FR-003**: Middleware MUST extract Authorization header from incoming requests and verify it contains "Bearer " prefix followed by JWT token string
- **FR-004**: Middleware MUST return 401 Unauthorized with error response {error: "Missing authentication token", code: "UNAUTHORIZED", timestamp: ISO8601} when Authorization header is missing or doesn't start with "Bearer "
- **FR-005**: Middleware MUST verify JWT token signature using BETTER_AUTH_SECRET environment variable as the signing key with HS256 algorithm via python-jose library
- **FR-006**: Middleware MUST validate token expiration by checking "exp" claim is in the future and return 401 Unauthorized for expired tokens
- **FR-007**: Middleware MUST decode valid JWT token payload and extract "sub" field (user_id) and "email" field from token claims
- **FR-008**: Middleware MUST attach decoded user_id and email to request.state object (request.state.user_id and request.state.email) making them accessible to route handlers
- **FR-009**: Middleware MUST return 401 Unauthorized with error "Invalid token signature" when JWT signature verification fails indicating token was tampered or signed with wrong secret
- **FR-010**: Middleware MUST return 400 Bad Request with error "Malformed authorization header" when token format is invalid (not "Bearer <token>" pattern)
- **FR-011**: System MUST provide jwt_utils.py module with decode_token(token: str) function that decodes JWT and returns payload dictionary or raises JWTError
- **FR-012**: System MUST provide verify_token(token: str) function in jwt_utils module that returns True for valid non-expired tokens, False for expired tokens, and raises JWTError for invalid signatures
- **FR-013**: System MUST provide extract_user_from_token(token: str, session: Session) function that decodes token, extracts user_id from "sub" claim, queries User model from database, and returns User object or None if not found
- **FR-014**: System MUST configure middleware in FastAPI application to run on all routes except /auth/*, /docs, /redoc, and /openapi.json (public documentation endpoints)
- **FR-015**: Error responses MUST follow standardized format with "error" (string message), "code" (error code string), and "timestamp" (ISO8601 datetime) fields
- **FR-016**: Middleware MUST handle python-jose JWTError exceptions and convert them to appropriate HTTP responses (401 for verification/expiration failures, 400 for malformed tokens)
- **FR-017**: System MUST provide complete type hints for all middleware and utility functions with no use of Any type for type safety

### Key Entities

- **JWT Token**: Cryptographically signed JSON Web Token issued by Better Auth frontend containing user identity claims (sub for user_id, email for user email, exp for expiration timestamp, iat for issued-at timestamp). Signed with HS256 algorithm using BETTER_AUTH_SECRET shared between frontend and backend.

- **Request State**: FastAPI request.state object that holds request-scoped data including authenticated user_id and email extracted from verified JWT token. Accessible to route handlers for user identification and authorization checks.

- **Authenticated User Context**: User information (user_id, email) extracted from validated JWT token and attached to request state for consumption by protected route handlers. Used for user isolation (filtering data by user_id) and authorization (verifying user owns requested resources).

## Success Criteria

### Measurable Outcomes

- **SC-001**: All protected API endpoints automatically verify JWT tokens without requiring authentication code in individual route handlers, measured by zero authentication logic in route files
- **SC-002**: Invalid authentication attempts (missing, expired, or tampered tokens) are rejected with appropriate error responses within 50ms, measured by middleware execution time
- **SC-003**: 100% of requests to /auth/* endpoints bypass authentication middleware successfully allowing signup and login without tokens
- **SC-004**: JWT token verification accuracy is 100% with zero false positives (valid tokens rejected) or false negatives (invalid tokens accepted), verified through comprehensive test suite
- **SC-005**: Route handlers access authenticated user information via request.state.user_id with 100% reliability for all protected endpoints
- **SC-006**: Error responses follow standardized format 100% of the time with consistent structure for all authentication failures
- **SC-007**: Type safety is complete with mypy strict mode passing with zero errors on all middleware and utility code
- **SC-008**: Token expiration checking prevents access from expired tokens 100% of the time without false rejections of valid tokens

## Scope Boundaries

### In Scope

- JWT token verification middleware for FastAPI application
- Authorization header parsing and Bearer token extraction
- Token signature verification using BETTER_AUTH_SECRET
- Token expiration validation
- User context extraction and attachment to request state
- Utility functions for token decoding, verification, and user extraction
- Error response formatting for authentication failures (401, 400)
- Middleware configuration to bypass authentication routes
- Complete type hints and type safety validation
- Test cases for valid, expired, invalid, and missing tokens

### Out of Scope

- JWT token generation and issuance (handled by Better Auth in frontend)
- User authentication endpoints (/auth/signup, /auth/login, /auth/logout) - separate feature
- Password hashing and validation - covered in authentication endpoints feature
- User registration and profile management - separate feature
- Authorization logic (checking if user owns resources) - handled in route handlers
- Token refresh mechanism - future feature
- Token revocation or blacklisting - future feature
- Rate limiting for authentication attempts - separate security feature
- Frontend Better Auth configuration - frontend concern
- Session management beyond JWT stateless authentication
- User permission system or role-based access control (RBAC)

## Dependencies

### Required Before This Feature

- Database foundation complete with User model defined (provides User type for user extraction)
- BETTER_AUTH_SECRET environment variable configured in backend/.env matching frontend secret
- python-jose library available for JWT operations (already installed in dependencies)
- FastAPI application initialized in main.py (for middleware registration)
- Error response format standardized across application
- Database session dependency injection working (for user extraction from database)

### Enables These Features

- User authentication endpoints can rely on middleware for JWT verification
- Task CRUD endpoints can access request.state.user_id for user isolation
- User management endpoints can verify user identity from JWT
- All protected API routes automatically secured without per-route authentication code
- Authorization checks in route handlers (verifying user owns resources)
- Audit logging with authenticated user context
- Rate limiting per authenticated user

## Assumptions

- BETTER_AUTH_SECRET is at least 32 characters for strong signature verification
- Frontend Better Auth is configured to issue JWT tokens with HS256 algorithm
- JWT token payload includes "sub" claim with user_id and "email" claim with user email
- Token expiration is set by frontend (typically 7 days) and included in "exp" claim
- All protected endpoints require user context from JWT (no anonymous access to protected routes)
- Database contains User table with id field matching JWT "sub" claim for user extraction
- FastAPI request.state is available for attaching user context
- Middleware runs before route handlers in request processing pipeline
- Public endpoints (/auth/*, /docs, /redoc) do not require authentication
- Error responses follow JSON format with error/code/timestamp structure
- Token format is standard JWT with three base64-encoded parts (header.payload.signature)
- No token refresh is needed at middleware level (handled by frontend)
- Invalid tokens should fail fast with clear error messages for debugging
- Middleware should not cache or store tokens (stateless verification)
