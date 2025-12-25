# Feature Specification: User Authentication Endpoints

**Feature Branch**: `007-auth-endpoints`
**Created**: 2025-12-24
**Status**: Draft
**Input**: User description: "User Authentication Endpoints: Implement three authentication API endpoints in FastAPI - POST /auth/signup accepts {username: string 3-50 chars, email: string valid format, password: string min 8 chars}, validates input with Pydantic schema, checks username and email uniqueness returns 409 Conflict if duplicate, hashes password using bcrypt via passlib with 12 rounds, creates User record in database, generates JWT token with payload {sub: user_id, email: email, exp: 7 days} using BETTER_AUTH_SECRET, returns 201 Created with {user: {id, username, email, created_at}, token: string}. POST /auth/login accepts {email: string, password: string}, finds user by email returns 401 if not found, verifies password hash with passlib returns 401 if incorrect, generates JWT token with 7-day expiration, returns 200 OK with {user: {id, username, email}, token: string}. POST /auth/logout returns 200 OK with {message: "Successfully logged out"} (stateless JWT so just success response). Create Pydantic schemas in schemas/auth.py for SignupRequest, LoginRequest, AuthResponse with validation. Acceptance criteria: All three endpoints functional, password hashing with bcrypt working, JWT tokens generated with proper expiration, duplicate username/email returns 409, invalid credentials returns 401, input validation errors return 422 with details, no password_hash exposed in responses, all tests passing for success and error cases."

## User Scenarios & Testing

### User Story 1 - New User Registers Account via Signup (Priority: P1)

As a new user, I need to create an account with username, email, and password so that I can access the todo application and manage my personal tasks securely.

**Why this priority**: User registration is the entry point to the application. Without signup capability, no users can be created and no other features can be used. This is the foundation of user management and must be implemented before login or any other user-related functionality.

**Independent Test**: Can be fully tested by sending POST requests to /auth/signup endpoint with valid user data (should create user and return token), duplicate username/email (should return 409), invalid input (should return 422), weak passwords (should return 422), and verifying password is hashed in database. Delivers value by allowing new users to onboard to the application with secure credentials.

**Acceptance Scenarios**:

1. **Given** valid registration data with username "johndoe", email "john@example.com", and password "SecurePass123", **When** a POST request is made to /auth/signup, **Then** the system validates the input, hashes the password with bcrypt (12 rounds), creates a User record in the database, generates a JWT token with 7-day expiration, and returns 201 Created with {user: {id, username, email, created_at}, token: string}
2. **Given** registration data with a username that already exists in the database, **When** a POST request is made to /auth/signup, **Then** the system checks username uniqueness, finds a duplicate, and returns 409 Conflict with error message "Username already exists"
3. **Given** registration data with an email that already exists in the database, **When** a POST request is made to /auth/signup, **Then** the system checks email uniqueness, finds a duplicate, and returns 409 Conflict with error message "Email already registered"
4. **Given** registration data with username less than 3 characters (e.g., "ab"), **When** a POST request is made to /auth/signup, **Then** the Pydantic schema validation fails and returns 422 Unprocessable Entity with error details indicating username must be 3-50 characters
5. **Given** registration data with invalid email format (e.g., "notanemail"), **When** a POST request is made to /auth/signup, **Then** the Pydantic schema validation fails and returns 422 Unprocessable Entity with error details indicating invalid email format
6. **Given** registration data with password less than 8 characters (e.g., "Pass1"), **When** a POST request is made to /auth/signup, **Then** the Pydantic schema validation fails and returns 422 Unprocessable Entity with error details indicating password must be at least 8 characters
7. **Given** a successfully created user, **When** querying the database for the user's password_hash field, **Then** the stored value is a bcrypt hash (starts with $2b$) and does not match the original plaintext password, confirming password hashing worked correctly

---

### User Story 2 - Existing User Logs In with Credentials (Priority: P2)

As an existing user, I need to log in with my email and password so that I can access my todo data and continue using the application securely.

**Why this priority**: After users can register (P1), they need to authenticate to access their data. Login is the second critical authentication step that enables returning users to access the application. Without login, registered users cannot re-authenticate and use the system.

**Independent Test**: Can be fully tested by creating a test user, then sending POST requests to /auth/login with correct credentials (should return token), wrong password (should return 401), non-existent email (should return 401), and verifying password verification logic works correctly. Delivers value by allowing registered users to authenticate and access their personalized data.

**Acceptance Scenarios**:

1. **Given** a registered user with email "john@example.com" and password "SecurePass123", **When** a POST request is made to /auth/login with matching credentials, **Then** the system finds the user by email, verifies the password hash with passlib, generates a JWT token with 7-day expiration, and returns 200 OK with {user: {id, username, email}, token: string}
2. **Given** a registered user with email "john@example.com", **When** a POST request is made to /auth/login with incorrect password "WrongPassword", **Then** the system finds the user, attempts password verification, detects mismatch, and returns 401 Unauthorized with error message "Invalid credentials"
3. **Given** no user exists with email "nonexistent@example.com", **When** a POST request is made to /auth/login with that email, **Then** the system queries the database, finds no matching user, and returns 401 Unauthorized with error message "Invalid credentials"
4. **Given** valid login credentials, **When** the JWT token is decoded, **Then** the payload contains "sub" field with user_id (UUID format), "email" field with user's email, "exp" field set to 7 days from issuance, and "iat" field with issued-at timestamp
5. **Given** login request with missing email field, **When** a POST request is made to /auth/login, **Then** the Pydantic schema validation fails and returns 422 Unprocessable Entity with error indicating email is required
6. **Given** login request with missing password field, **When** a POST request is made to /auth/login, **Then** the Pydantic schema validation fails and returns 422 Unprocessable Entity with error indicating password is required

---

### User Story 3 - Authenticated User Logs Out (Priority: P3)

As an authenticated user, I need to log out of the application so that I can signal the end of my session and the frontend can clear my local authentication state.

**Why this priority**: After signup (P1) and login (P2), logout provides session management from the user's perspective. Since JWTs are stateless, the backend simply confirms the logout request. This is lower priority because the frontend can clear tokens client-side, but having an endpoint provides consistency and enables future token revocation.

**Independent Test**: Can be fully tested by sending POST requests to /auth/logout endpoint and verifying it returns 200 OK with success message regardless of token validity (stateless). Delivers value by providing a standard logout flow and enabling future enhancements like token blacklisting.

**Acceptance Scenarios**:

1. **Given** an authenticated user with valid JWT token, **When** a POST request is made to /auth/logout, **Then** the system returns 200 OK with response {message: "Successfully logged out"}
2. **Given** the logout endpoint is called, **When** the response is examined, **Then** no server-side state is modified (stateless JWT approach) and the client is expected to discard the token locally
3. **Given** a POST request to /auth/logout with no Authorization header, **When** the middleware is configured to allow /auth/* routes without authentication, **Then** the logout endpoint still returns 200 OK allowing client-side logout regardless of token presence

---

### Edge Cases

- What happens when signup is attempted with whitespace-only username? System should trim whitespace in validation and reject if resulting string is too short or empty
- How does the system handle signup with email in mixed case (e.g., "John@Example.COM")? System should normalize email to lowercase before uniqueness check to prevent duplicate accounts with different casing
- What happens when password contains special characters or unicode? System should accept any UTF-8 password that meets length requirements and hash it correctly with bcrypt
- How does the system handle concurrent signup requests with the same email? Database unique constraint should catch duplicate at commit time, returning 409 for the second request
- What happens when bcrypt hashing fails (extremely rare)? System should catch passlib exceptions and return 500 Internal Server Error with generic error message
- How does the system handle JWT generation failure? System should catch jose exceptions and return 500 Internal Server Error without exposing secret key
- What happens when login is attempted with SQL injection in email field? Pydantic email validation and parameterized ORM queries prevent SQL injection
- How does the system handle very long passwords (> 72 characters)? Bcrypt truncates passwords at 72 bytes, so system should either enforce max length or document this limitation
- What happens when database is unavailable during signup/login? System should catch database connection errors and return 503 Service Unavailable
- How does the system handle user trying to signup with both duplicate username AND duplicate email? System should check both, returning first duplicate encountered in a consistent order

## Requirements

### Functional Requirements

- **FR-001**: System MUST provide POST /auth/signup endpoint that accepts JSON request body with username (string), email (string), and password (string) fields
- **FR-002**: System MUST validate signup request using Pydantic schema with constraints: username 3-50 characters, email valid format (RFC 5322), password minimum 8 characters
- **FR-003**: System MUST return 422 Unprocessable Entity with detailed validation errors when signup request fails Pydantic schema validation
- **FR-004**: System MUST check username uniqueness by querying User table and return 409 Conflict with error "Username already exists" if duplicate found
- **FR-005**: System MUST check email uniqueness by querying User table (case-insensitive) and return 409 Conflict with error "Email already registered" if duplicate found
- **FR-006**: System MUST normalize email to lowercase before uniqueness check and database storage to ensure case-insensitive uniqueness
- **FR-007**: System MUST hash passwords using passlib CryptContext with bcrypt scheme and 12 rounds before storing in database
- **FR-008**: System MUST create User record in database with id (auto-generated UUID), username, email (lowercase), password_hash, created_at (current timestamp), updated_at (current timestamp)
- **FR-009**: System MUST generate JWT token after successful user creation using python-jose with HS256 algorithm, BETTER_AUTH_SECRET from environment, and payload containing sub (user_id as string), email, exp (current time + 7 days), iat (current timestamp)
- **FR-010**: System MUST return 201 Created on successful signup with JSON response {user: {id: string, username: string, email: string, created_at: ISO8601 string}, token: string}
- **FR-011**: System MUST provide POST /auth/login endpoint that accepts JSON request body with email (string) and password (string) fields
- **FR-012**: System MUST validate login request using Pydantic schema requiring both email and password fields with valid email format
- **FR-013**: System MUST query User table by email (case-insensitive) and return 401 Unauthorized with error "Invalid credentials" if user not found
- **FR-014**: System MUST verify password against stored password_hash using passlib verify method and return 401 Unauthorized with error "Invalid credentials" if verification fails
- **FR-015**: System MUST generate JWT token after successful login verification with same payload structure and expiration as signup (7 days)
- **FR-016**: System MUST return 200 OK on successful login with JSON response {user: {id: string, username: string, email: string}, token: string}
- **FR-017**: System MUST provide POST /auth/logout endpoint that returns 200 OK with JSON response {message: "Successfully logged out"}
- **FR-018**: System MUST NOT include password_hash field in any API response (user objects should only include id, username, email, created_at)
- **FR-019**: System MUST create Pydantic schema SignupRequest in schemas/auth.py with username: str (min_length=3, max_length=50), email: EmailStr, password: str (min_length=8)
- **FR-020**: System MUST create Pydantic schema LoginRequest in schemas/auth.py with email: EmailStr, password: str fields
- **FR-021**: System MUST create Pydantic schema UserResponse in schemas/auth.py with id: UUID, username: str, email: str, created_at: datetime fields
- **FR-022**: System MUST create Pydantic schema AuthResponse in schemas/auth.py with user: UserResponse, token: str fields
- **FR-023**: System MUST handle database exceptions (e.g., connection failures) by catching and returning 500 Internal Server Error with generic error message
- **FR-024**: System MUST handle passlib exceptions during hashing/verification by catching and returning 500 Internal Server Error
- **FR-025**: System MUST handle python-jose exceptions during JWT generation by catching and returning 500 Internal Server Error without exposing secret key

### Key Entities

- **SignupRequest**: Pydantic schema representing user registration input with username (3-50 chars), email (valid format), and password (min 8 chars). Used for input validation on POST /auth/signup endpoint. Ensures data quality before processing.

- **LoginRequest**: Pydantic schema representing user authentication input with email (valid format) and password. Used for input validation on POST /auth/login endpoint. Minimal required fields for credential verification.

- **UserResponse**: Pydantic schema representing safe user data for API responses with id (UUID), username, email, and created_at timestamp. Explicitly excludes password_hash for security. Used in both signup and login success responses.

- **AuthResponse**: Pydantic schema representing successful authentication result with user (UserResponse) and token (JWT string). Returned by both signup and login endpoints on successful authentication.

- **JWT Token**: JSON Web Token containing user identity claims (sub: user_id, email: user email, exp: expiration 7 days from issuance, iat: issued-at timestamp). Signed with HS256 algorithm using BETTER_AUTH_SECRET. Used for stateless authentication in subsequent API requests.

- **Hashed Password**: Bcrypt hash of user's plaintext password generated with 12 rounds. Stored in User.password_hash field. Verified using passlib during login. Never exposed in API responses or logs.

## Success Criteria

### Measurable Outcomes

- **SC-001**: POST /auth/signup endpoint creates new users successfully with valid input, verified by user record existing in database with hashed password
- **SC-002**: Password hashing uses bcrypt with 12 rounds, verified by password_hash starting with "$2b$12$" in database
- **SC-003**: Signup with duplicate username returns 409 Conflict 100% of the time, verified by attempting duplicate registrations
- **SC-004**: Signup with duplicate email (case-insensitive) returns 409 Conflict 100% of the time, verified by attempting registrations with same email in different cases
- **SC-005**: Signup with invalid input (short username, invalid email, short password) returns 422 with detailed validation errors 100% of the time
- **SC-006**: POST /auth/login endpoint authenticates users successfully with correct credentials, verified by receiving valid JWT token
- **SC-007**: Login with incorrect password returns 401 Unauthorized 100% of the time, verified by attempting login with wrong passwords
- **SC-008**: Login with non-existent email returns 401 Unauthorized 100% of the time, verified by attempting login with unregistered emails
- **SC-009**: JWT tokens generated contain correct payload structure (sub, email, exp, iat) with 7-day expiration, verified by decoding tokens
- **SC-010**: No password_hash appears in any API response, verified by inspecting all auth endpoint responses
- **SC-011**: POST /auth/logout endpoint returns 200 OK with success message 100% of the time
- **SC-012**: All authentication endpoints complete within 500ms for 95th percentile (excluding network latency)
- **SC-013**: Unit tests achieve 100% code coverage for all authentication logic (signup validation, login verification, password hashing, JWT generation)
- **SC-014**: Integration tests cover all success and error scenarios (valid signup, duplicate user, invalid input, correct login, wrong credentials, logout)

## Scope Boundaries

### In Scope

- POST /auth/signup endpoint with input validation and user creation
- POST /auth/login endpoint with credential verification
- POST /auth/logout endpoint with success response
- Pydantic schemas for request validation and response formatting (SignupRequest, LoginRequest, UserResponse, AuthResponse)
- Password hashing with bcrypt via passlib (12 rounds)
- JWT token generation with 7-day expiration using BETTER_AUTH_SECRET
- Username and email uniqueness validation returning 409 Conflict
- Input validation returning 422 Unprocessable Entity with error details
- Secure response formatting excluding password_hash from all responses
- Error handling for database, passlib, and JWT generation failures
- Case-insensitive email handling (normalization to lowercase)
- Unit and integration tests for all success and error paths

### Out of Scope

- JWT token verification middleware (already implemented in 006-jwt-auth-middleware)
- Password reset or forgot password functionality (future feature)
- Email verification or confirmation workflow (future feature)
- Account activation or deactivation (future feature)
- Social authentication (OAuth, Google, GitHub) (future feature)
- Multi-factor authentication (MFA/2FA) (future feature)
- Token refresh mechanism (future feature)
- Token revocation or blacklisting (future feature)
- Rate limiting for authentication endpoints (separate security feature)
- User profile update endpoints (separate user management feature)
- Password strength meter or complexity requirements beyond minimum length
- Username validation beyond length (e.g., allowed characters, reserved names)
- Database migrations (handled in database foundation feature)
- Frontend Better Auth integration (frontend concern)
- Session management beyond stateless JWT

## Dependencies

### Required Before This Feature

- Database foundation complete with User model defined (id, username, email, password_hash, created_at, updated_at)
- Database connection and session management working (db.py module)
- BETTER_AUTH_SECRET environment variable configured in backend/.env
- passlib library installed in backend dependencies (for bcrypt password hashing)
- python-jose library installed in backend dependencies (for JWT generation)
- Pydantic and FastAPI installed for schema validation and routing
- Backend directory structure includes routes/ and schemas/ folders

### Enables These Features

- User authentication flow (users can register and log in to access application)
- JWT token issuance for authenticated API access
- Protected task CRUD endpoints (users can access their tasks after authentication)
- User profile management endpoints (users can update their profile after authentication)
- Frontend authentication integration with Better Auth
- User-specific data isolation (tasks filtered by authenticated user_id)

## Assumptions

- BETTER_AUTH_SECRET is at least 32 characters and kept secure in environment variables
- Frontend will store JWT token (e.g., localStorage) and attach to subsequent API requests
- Logout is client-side action (frontend clears token) with backend endpoint for consistency
- Bcrypt with 12 rounds provides adequate security for password hashing
- 7-day JWT expiration balances security and user convenience (no refresh token initially)
- Email addresses are case-insensitive and normalized to lowercase
- Usernames are case-sensitive but must be unique
- Password minimum length of 8 characters is sufficient security policy
- No CAPTCHA or bot protection is required for signup endpoint initially
- Database unique constraints on username and email will be enforced at database level
- PostgreSQL is used as database (for case-insensitive email queries with ILIKE)
- FastAPI exception handlers will format error responses consistently
- Users can only signup with email (no phone number or other identifiers)
- No email verification is required to complete signup (account is immediately active)
- Password can contain any UTF-8 characters within bcrypt's 72-byte limit
- JWT tokens do not need to be stored in database (fully stateless authentication)
- User deletion or account deactivation is not handled by authentication endpoints
