# JWT Authentication Middleware - Quick Start Guide

**Feature**: JWT Authentication Middleware
**Date**: 2025-12-24
**Status**: Ready for Implementation

## Overview

This quickstart guide provides step-by-step instructions for setting up and testing the JWT authentication middleware in the FastAPI backend. Follow these steps to configure JWT verification, run tests, and verify the middleware is working correctly.

---

## Prerequisites

Before starting, ensure you have:

- ✅ Python 3.11+ installed
- ✅ UV package manager installed
- ✅ Database foundation complete (User model available)
- ✅ Backend directory initialized with FastAPI
- ✅ Better Auth configured on frontend (JWT plugin enabled)

---

## Step 1: Configure BETTER_AUTH_SECRET

The JWT middleware requires a shared secret between frontend (Better Auth) and backend (FastAPI) for signature verification.

### 1.1 Generate Secure Secret

Generate a secure 32+ character secret using OpenSSL:

```bash
openssl rand -base64 32
```

**Example Output**:
```
8kF9mN2pQ7vR1sT3uW5xY6zA8bC0dE4fG9hJ1kL3mN5oP7qR9sT2uV4wX6yZ
```

### 1.2 Add to Backend .env

Open or create `backend/.env` file and add:

```bash
# Authentication (must match frontend BETTER_AUTH_SECRET)
BETTER_AUTH_SECRET=8kF9mN2pQ7vR1sT3uW5xY6zA8bC0dE4fG9hJ1kL3mN5oP7qR9sT2uV4wX6yZ

# Database (should already be configured)
DATABASE_URL=postgresql://user:password@hostname/database?sslmode=require
```

### 1.3 Add to Frontend .env.local

Open or create `frontend/.env.local` file and add the SAME secret:

```bash
# Better Auth (must match backend BETTER_AUTH_SECRET)
BETTER_AUTH_SECRET=8kF9mN2pQ7vR1sT3uW5xY6zA8bC0dE4fG9hJ1kL3mN5oP7qR9sT2uV4wX6yZ

# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**IMPORTANT**: Both secrets MUST match exactly. If they don't match, JWT verification will fail with "Invalid token signature" errors.

### 1.4 Verify Configuration

```bash
# Check backend secret
cd backend
grep BETTER_AUTH_SECRET .env

# Check frontend secret
cd ../frontend
grep BETTER_AUTH_SECRET .env.local
```

---

## Step 2: Install Dependencies

Install python-jose library for JWT operations:

```bash
cd backend
uv add python-jose[cryptography]
```

**Expected Output**:
```
Resolved 15 packages in 2.3s
Installed python-jose[cryptography] v3.3.0
```

### Verify Installation

```bash
uv pip list | grep jose
```

**Expected Output**:
```
python-jose    3.3.0
```

---

## Step 3: Run Tests

Before implementing, run the test suite to ensure everything is configured correctly:

### 3.1 Run JWT Utility Tests

```bash
cd backend
python -m pytest tests/test_jwt_utils.py -v
```

**Expected Output** (after implementation):
```
tests/test_jwt_utils.py::test_decode_token_valid PASSED
tests/test_jwt_utils.py::test_decode_token_expired PASSED
tests/test_jwt_utils.py::test_decode_token_invalid_signature PASSED
tests/test_jwt_utils.py::test_verify_token_valid PASSED
tests/test_jwt_utils.py::test_verify_token_expired PASSED
tests/test_jwt_utils.py::test_extract_user_existing PASSED
tests/test_jwt_utils.py::test_extract_user_nonexistent PASSED
```

### 3.2 Run Middleware Tests

```bash
python -m pytest tests/test_auth_middleware.py -v
```

**Expected Output** (after implementation):
```
tests/test_auth_middleware.py::test_middleware_valid_token PASSED
tests/test_auth_middleware.py::test_middleware_missing_token PASSED
tests/test_auth_middleware.py::test_middleware_expired_token PASSED
tests/test_auth_middleware.py::test_middleware_invalid_signature PASSED
tests/test_auth_middleware.py::test_middleware_malformed_header PASSED
tests/test_auth_middleware.py::test_middleware_public_routes PASSED
tests/test_auth_middleware.py::test_middleware_user_context PASSED
```

### 3.3 Run All Tests with Coverage

```bash
python -m pytest tests/ --cov=middleware --cov=utils --cov-report=term-missing
```

**Target Coverage**: 100% for middleware and utils modules

---

## Step 4: Start the Server

Start FastAPI development server:

```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Expected Output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Verify Middleware Registration**:
Look for log message indicating JWT middleware is active (if logging is configured).

---

## Step 5: Generate Test JWT Token

Use the utility script to generate a test JWT token for manual testing:

### 5.1 Create Test User in Database

```bash
# Using Python REPL
python
```

```python
from db import engine
from models import User
from sqlmodel import Session
from uuid import uuid4

user_id = uuid4()
with Session(engine) as session:
    user = User(
        id=user_id,
        username="testuser",
        email="test@example.com",
        password_hash="dummy_hash"  # Not used for JWT
    )
    session.add(user)
    session.commit()
    print(f"Created user: {user_id}")
```

**Output**: Save the user_id (UUID) for next step.

### 5.2 Generate JWT Token

```bash
# Using the generate_test_token.py script
python scripts/generate_test_token.py \
  --user-id "123e4567-e89b-12d3-a456-426614174000" \
  --email "test@example.com"
```

**Expected Output**:
```
Generated JWT Token:
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjNlNDU2Ny1lODliLTEyZDMtYTQ1Ni00MjY2MTQxNzQwMDAiLCJlbWFpbCI6InRlc3RAZXhhbXBsZS5jb20iLCJleHAiOjE3MDM0NjI0MDAsImlhdCI6MTcwMzM3NjAwMH0.Xk5YJN8LqH3qR9sT2uV4wX6yZ8kF9mN2pQ7vR1sT3uW

Valid for: 1 hour
```

**Save this token** for testing API requests.

---

## Step 6: Test Middleware with curl

Test the middleware with various scenarios using curl:

### 6.1 Test Public Route (No Token Required)

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

**Expected Result**: Request succeeds without JWT token (middleware bypasses `/auth/*` routes).

### 6.2 Test Protected Route without Token (Should Fail)

```bash
curl -X GET http://localhost:8000/api/users/123e4567-e89b-12d3-a456-426614174000/tasks
```

**Expected Response**:
```json
{
  "error": "Missing authentication token",
  "code": "UNAUTHORIZED",
  "timestamp": "2025-12-24T12:34:56.789Z"
}
```

**Status Code**: 401 Unauthorized

### 6.3 Test Protected Route with Valid Token (Should Pass)

```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." # Use token from Step 5.2

curl -X GET http://localhost:8000/api/users/123e4567-e89b-12d3-a456-426614174000/tasks \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Result**: Request succeeds, middleware attaches user context to `request.state`.

### 6.4 Test with Malformed Header (Should Fail)

```bash
curl -X GET http://localhost:8000/api/users/123e4567-e89b-12d3-a456-426614174000/tasks \
  -H "Authorization: $TOKEN"  # Missing "Bearer " prefix
```

**Expected Response**:
```json
{
  "error": "Malformed authorization header",
  "code": "MALFORMED_TOKEN",
  "timestamp": "2025-12-24T12:34:56.789Z"
}
```

**Status Code**: 400 Bad Request

### 6.5 Test with Expired Token (Should Fail)

Generate an expired token or wait for token to expire, then:

```bash
EXPIRED_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." # Expired token

curl -X GET http://localhost:8000/api/users/123e4567-e89b-12d3-a456-426614174000/tasks \
  -H "Authorization: Bearer $EXPIRED_TOKEN"
```

**Expected Response**:
```json
{
  "error": "Token has expired",
  "code": "TOKEN_EXPIRED",
  "timestamp": "2025-12-24T12:34:56.789Z"
}
```

**Status Code**: 401 Unauthorized

---

## Step 7: Verify Middleware in Route Handler

Create a test endpoint that accesses `request.state` to verify user context is attached:

### 7.1 Create Test Endpoint

Add to `backend/main.py`:

```python
@app.get("/api/test/auth")
async def test_auth(request: Request):
    """Test endpoint to verify JWT middleware is working."""
    return {
        "authenticated": True,
        "user_id": request.state.user_id,
        "email": request.state.email,
        "message": "JWT middleware is working!"
    }
```

### 7.2 Test with Valid Token

```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." # Use valid token

curl -X GET http://localhost:8000/api/test/auth \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response**:
```json
{
  "authenticated": true,
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "test@example.com",
  "message": "JWT middleware is working!"
}
```

**Verification**: `user_id` and `email` match the values in the JWT token payload.

---

## Step 8: Check Logs

Review server logs to verify middleware execution:

### 8.1 Expected Log Messages

- JWT verification successful: `INFO: JWT verified for user <user_id>`
- JWT verification failed: `WARNING: JWT verification failed: <error>`
- Public route bypass: `DEBUG: Bypassing auth for public route: /auth/login`

### 8.2 Enable Debug Logging (Optional)

Add to `backend/main.py`:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
```

---

## Troubleshooting

### Issue: "Invalid token signature" Error

**Cause**: BETTER_AUTH_SECRET mismatch between frontend and backend.

**Solution**:
1. Verify both `.env` files contain identical secrets
2. Restart both frontend and backend servers
3. Generate new token with backend secret
4. Test again

### Issue: "Missing authentication token" on Protected Routes

**Cause**: Authorization header not included in request.

**Solution**:
1. Verify curl command includes `-H "Authorization: Bearer <token>"`
2. Check frontend is attaching token to API requests
3. Inspect browser DevTools Network tab to verify header

### Issue: "Token has expired" Immediately

**Cause**: Clock skew between token generation and verification, or token was generated with past expiration.

**Solution**:
1. Check system clock: `date`
2. Ensure token expiration is in future (1 hour from now)
3. Regenerate token with `generate_test_token.py` script

### Issue: Middleware Not Running

**Cause**: Middleware not registered in `main.py`.

**Solution**:
1. Verify `app.middleware("http")(verify_jwt_middleware)` line in `main.py`
2. Ensure line is BEFORE route inclusions
3. Restart server

### Issue: Database Connection Error in extract_user_from_token

**Cause**: DATABASE_URL not configured or invalid.

**Solution**:
1. Verify DATABASE_URL in `.env`
2. Test connection: `python scripts/test_connection.py`
3. Check Neon PostgreSQL credentials

---

## Verification Checklist

Before considering the feature complete, verify:

- ✅ BETTER_AUTH_SECRET configured in both frontend and backend
- ✅ python-jose[cryptography] installed in backend
- ✅ All tests passing (test_jwt_utils.py, test_auth_middleware.py)
- ✅ 100% test coverage for middleware and utils modules
- ✅ Server starts without errors
- ✅ Public routes accessible without tokens
- ✅ Protected routes reject requests without tokens (401)
- ✅ Protected routes accept requests with valid tokens
- ✅ Expired tokens rejected (401)
- ✅ Malformed headers rejected (400)
- ✅ User context (user_id, email) accessible in route handlers
- ✅ Error responses follow standardized format
- ✅ Mypy type checking passes (strict mode)

---

## Next Steps

After completing this quickstart:

1. **Implement Task CRUD Endpoints**: Use `request.state.user_id` to filter tasks by user
2. **Add Authorization Checks**: Verify user owns resource before modification
3. **Implement Token Refresh**: Add endpoint for refreshing expired tokens (future feature)
4. **Add Audit Logging**: Log authenticated requests for security monitoring

---

## Useful Commands

### Generate Secure Secret
```bash
openssl rand -base64 32
```

### Generate Test JWT Token
```bash
python scripts/generate_test_token.py --user-id <uuid> --email <email>
```

### Run Tests with Coverage
```bash
python -m pytest tests/ --cov=middleware --cov=utils --cov-report=html
```

### Start Development Server
```bash
uvicorn main:app --reload --port 8000
```

### Test with curl (Valid Token)
```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/test/auth
```

### Test with curl (Missing Token)
```bash
curl http://localhost:8000/api/test/auth
```

### Check BETTER_AUTH_SECRET
```bash
grep BETTER_AUTH_SECRET backend/.env frontend/.env.local
```

---

## Additional Resources

- **Feature Spec**: [spec.md](./spec.md)
- **Implementation Plan**: [plan.md](./plan.md)
- **Research Document**: [research.md](./research.md)
- **Middleware Contract**: [contracts/middleware-contract.md](./contracts/middleware-contract.md)
- **JWT Utils Contract**: [contracts/jwt-utils-contract.md](./contracts/jwt-utils-contract.md)
- **python-jose Documentation**: https://python-jose.readthedocs.io/
- **FastAPI Middleware**: https://fastapi.tiangolo.com/tutorial/middleware/
- **Better Auth JWT Plugin**: https://www.better-auth.com/docs/plugins/jwt

---

## Support

If you encounter issues not covered in this guide:

1. Check server logs for detailed error messages
2. Review the research document for technical decisions
3. Consult the contracts for interface specifications
4. Run tests in verbose mode: `pytest -vv`
5. Verify environment variables are loaded: `python -c "import os; print(os.getenv('BETTER_AUTH_SECRET'))"`

Happy coding! 🎉
