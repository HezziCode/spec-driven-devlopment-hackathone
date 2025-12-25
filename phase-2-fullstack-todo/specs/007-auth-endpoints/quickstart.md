# Quickstart Guide: User Authentication Endpoints

**Feature**: 007-auth-endpoints
**Purpose**: Quick setup and testing guide for authentication endpoints
**Audience**: Developers implementing or testing authentication

## Prerequisites

Before starting, ensure:

- ✅ Database foundation complete (User model exists)
- ✅ JWT middleware complete (token verification working)
- ✅ BETTER_AUTH_SECRET configured in backend/.env
- ✅ Database connection working
- ✅ FastAPI server can start

## Setup Steps

### 1. Install Dependencies

Navigate to backend directory and install passlib:

```bash
cd backend
uv add "passlib[bcrypt]"
```

**Verify Installation**:
```bash
python -c "from passlib.context import CryptContext; print('passlib installed successfully')"
```

### 2. Verify Environment Configuration

Check that BETTER_AUTH_SECRET is set:

```bash
# View .env file
cat backend/.env | grep BETTER_AUTH_SECRET
```

Expected output:
```
BETTER_AUTH_SECRET=your-secret-key-here-minimum-32-characters
```

**If missing**, add to backend/.env:
```bash
echo "BETTER_AUTH_SECRET=$(openssl rand -base64 32)" >> backend/.env
```

**Important**: BETTER_AUTH_SECRET must be at least 32 characters and match between backend and frontend.

### 3. Run Database Migration (if needed)

If User table doesn't exist yet:

```bash
cd backend
python migrations/create_tables.py
```

Verify User table exists:
```bash
# Using psql (if available)
psql $DATABASE_URL -c "\d users"

# Or check in Python
python -c "from db import engine; from sqlmodel import inspect; print(inspect(engine).get_table_names())"
```

### 4. Start Backend Server

```bash
cd backend
uvicorn main:app --reload --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 5. Verify API Documentation

Open browser to http://localhost:8000/docs

You should see Swagger UI with three auth endpoints:
- POST /auth/signup
- POST /auth/login
- POST /auth/logout

## Testing with curl

### Test 1: User Signup (Happy Path)

**Create New User**:
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123"
  }'
```

**Expected Response** (201 Created):
```json
{
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "testuser",
    "email": "test@example.com",
    "created_at": "2025-12-24T04:30:00Z"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Verify**:
- Status code is 201
- Response includes `user` object with `id`, `username`, `email`, `created_at`
- Response includes `token` (long JWT string)
- `password_hash` is NOT in response

**Check Database**:
```bash
# Save user_id from response, then query database
USER_ID="123e4567-e89b-12d3-a456-426614174000"
python -c "
from db import engine
from sqlmodel import Session, select
from models import User
with Session(engine) as session:
    user = session.get(User, '$USER_ID')
    print(f'Username: {user.username}')
    print(f'Email: {user.email}')
    print(f'Password hash starts with: {user.password_hash[:10]}')
"
```

Expected output:
```
Username: testuser
Email: test@example.com
Password hash starts with: $2b$12$...
```

### Test 2: Duplicate Username (Error Case)

**Attempt Duplicate Username**:
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "different@example.com",
    "password": "SecurePass123"
  }'
```

**Expected Response** (409 Conflict):
```json
{
  "error": "Username already exists",
  "code": "CONFLICT",
  "timestamp": "2025-12-24T04:30:00Z"
}
```

### Test 3: Duplicate Email (Case-Insensitive)

**Attempt Duplicate Email with Different Casing**:
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "differentuser",
    "email": "TEST@Example.COM",
    "password": "SecurePass123"
  }'
```

**Expected Response** (409 Conflict):
```json
{
  "error": "Email already registered",
  "code": "CONFLICT",
  "timestamp": "2025-12-24T04:30:00Z"
}
```

### Test 4: Invalid Input (Short Password)

**Attempt Signup with Short Password**:
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "new@example.com",
    "password": "Short1"
  }'
```

**Expected Response** (422 Unprocessable Entity):
```json
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "ensure this value has at least 8 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

### Test 5: User Login (Happy Path)

**Login with Correct Credentials**:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123"
  }'
```

**Expected Response** (200 OK):
```json
{
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "testuser",
    "email": "test@example.com"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Note**: Response does NOT include `created_at` (differs from signup).

### Test 6: Login with Case-Insensitive Email

**Login with Different Email Casing**:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "TEST@Example.COM",
    "password": "SecurePass123"
  }'
```

**Expected Response** (200 OK):
Same as Test 5 - login succeeds with any email casing

### Test 7: Login with Wrong Password

**Attempt Login with Incorrect Password**:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "WrongPassword"
  }'
```

**Expected Response** (401 Unauthorized):
```json
{
  "error": "Invalid credentials",
  "code": "UNAUTHORIZED",
  "timestamp": "2025-12-24T04:30:00Z"
}
```

### Test 8: Logout

**Call Logout Endpoint**:
```bash
curl -X POST http://localhost:8000/auth/logout
```

**Expected Response** (200 OK):
```json
{
  "message": "Successfully logged out"
}
```

**Note**: Logout always succeeds (stateless JWT).

## Verify JWT Token

### Decode JWT Token

Save token from signup/login response, then decode:

```bash
# Save token to variable
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Decode token (requires python-jose)
python -c "
from jose import jwt
token = '$TOKEN'
# Decode without verification (for inspection)
payload = jwt.get_unverified_claims(token)
print('Token payload:')
print(f'  User ID (sub): {payload.get(\"sub\")}')
print(f'  Email: {payload.get(\"email\")}')
print(f'  Expires (exp): {payload.get(\"exp\")}')
print(f'  Issued (iat): {payload.get(\"iat\")}')
"
```

Expected output:
```
Token payload:
  User ID (sub): 123e4567-e89b-12d3-a456-426614174000
  Email: test@example.com
  Expires (exp): 1735684800
  Issued (iat): 1735080000
```

### Verify Token Expiration

Check that token expires 7 days from issuance:

```python
from datetime import datetime, timedelta

iat = datetime.fromtimestamp(1735080000)
exp = datetime.fromtimestamp(1735684800)
delta = exp - iat

print(f"Issued: {iat}")
print(f"Expires: {exp}")
print(f"Duration: {delta.days} days")  # Should be 7
```

### Use Token in Protected Endpoint

Test token with protected endpoint (requires JWT middleware):

```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X GET http://localhost:8000/api/users/me \
  -H "Authorization: Bearer $TOKEN"
```

Expected: Request succeeds if JWT middleware accepts token.

## Testing with Python Script

### Complete Test Script

Save as `test_auth.py`:

```python
import requests
import json

BASE_URL = "http://localhost:8000"

def test_signup():
    print("Test 1: Signup")
    response = requests.post(
        f"{BASE_URL}/auth/signup",
        json={
            "username": "testuser2",
            "email": "test2@example.com",
            "password": "SecurePass123"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json().get("token")

def test_login():
    print("\nTest 2: Login")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "test2@example.com",
            "password": "SecurePass123"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json().get("token")

def test_logout():
    print("\nTest 3: Logout")
    response = requests.post(f"{BASE_URL}/auth/logout")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    token = test_signup()
    print(f"\nReceived JWT token: {token[:50]}...")

    token = test_login()
    print(f"\nReceived JWT token: {token[:50]}...")

    test_logout()
```

Run script:
```bash
python test_auth.py
```

## Troubleshooting

### Issue: "passlib not found"

**Solution**: Install passlib with bcrypt extra
```bash
cd backend
uv add "passlib[bcrypt]"
```

### Issue: "BETTER_AUTH_SECRET environment variable is not set"

**Solution**: Add to backend/.env
```bash
echo "BETTER_AUTH_SECRET=$(openssl rand -base64 32)" >> backend/.env
```

Restart server after adding.

### Issue: "Table 'users' doesn't exist"

**Solution**: Run database migration
```bash
cd backend
python migrations/create_tables.py
```

### Issue: "422 Unprocessable Entity" on valid input

**Check**: Request Content-Type header is "application/json"
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \  # Must include this
  -d '{"username": "test", "email": "test@example.com", "password": "password123"}'
```

### Issue: "Token signature is invalid"

**Check**: BETTER_AUTH_SECRET matches between signup and verification
```bash
# Check backend secret
grep BETTER_AUTH_SECRET backend/.env

# Check frontend secret (if applicable)
grep BETTER_AUTH_SECRET frontend/.env.local
```

Secrets must match exactly.

### Issue: Password hash doesn't start with "$2b$12$"

**Check**: Bcrypt rounds configured correctly
```python
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], bcrypt__rounds=12)
print(pwd_context.hash("test")[:10])  # Should print "$2b$12$..."
```

## Performance Benchmarking

### Measure Response Times

```bash
# Signup performance
time curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"username": "perftest", "email": "perf@example.com", "password": "SecurePass123"}'

# Login performance
time curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "perf@example.com", "password": "SecurePass123"}'
```

Expected timings:
- Signup: < 500ms
- Login: < 300ms
- Logout: < 50ms

## Next Steps

After successful testing:

1. ✅ Run automated test suite: `cd backend && pytest tests/test_auth_routes.py`
2. ✅ Check test coverage: `pytest --cov=routes.auth --cov=schemas.auth`
3. ✅ Run type checking: `mypy routes/auth.py schemas/auth.py`
4. ✅ Test with frontend: Integrate with Better Auth on frontend
5. ✅ Document API: Update API documentation with authentication flow

## Reference Commands

```bash
# Install dependencies
uv add "passlib[bcrypt]"

# Run server
uvicorn main:app --reload --port 8000

# Run tests
pytest tests/test_auth_routes.py -v

# Check coverage
pytest --cov=routes.auth --cov=schemas.auth --cov-report=term-missing

# Type checking
mypy routes/auth.py schemas/auth.py

# Database query
python -c "from db import engine; from sqlmodel import Session, select; from models import User; session = Session(engine); print(session.exec(select(User)).all())"
```

## Common Workflows

### Clean Slate Testing

```bash
# Delete test users
python -c "
from db import engine
from sqlmodel import Session, select, delete
from models import User
with Session(engine) as session:
    # Delete test users
    stmt = delete(User).where(User.email.like('%example.com'))
    session.exec(stmt)
    session.commit()
    print('Test users deleted')
"

# Now run signup tests again
curl -X POST http://localhost:8000/auth/signup ...
```

### Load Testing

```bash
# Install apache bench
sudo apt install apache2-utils  # Ubuntu/Debian

# Run load test (100 requests, 10 concurrent)
ab -n 100 -c 10 -p signup_body.json -T application/json http://localhost:8000/auth/signup
```

Where `signup_body.json`:
```json
{"username": "loadtest", "email": "load@example.com", "password": "SecurePass123"}
```

---

**Quickstart Complete!** You should now have working authentication endpoints with signup, login, and logout functionality.
