# Authentication Troubleshooting Guide

**Error**: `[API] POST http://localhost:8000/auth/login 401 null`
**Meaning**: Login failed with "Invalid credentials"

---

## Common Causes

### 1. **User doesn't exist in database** ⚠️ MOST COMMON
**Symptom**: 401 error on login
**Solution**: You must **SIGN UP first** before you can sign in!

**Steps**:
1. Go to http://localhost:3000/auth
2. You'll see the signin form by default
3. **Click the "Sign Up" toggle link** at the bottom
4. Fill the signup form:
   - Username (3+ characters)
   - Email (valid format)
   - Password (8+ characters)
   - Confirm Password (must match)
5. Click "Sign Up" button
6. After successful signup, you'll be logged in automatically
7. Now you can sign out and sign in again with those credentials

---

### 2. **Wrong email or password**
**Symptom**: 401 error with "Invalid credentials"
**Solution**:
- Make sure you're using the **exact email** you signed up with (case-insensitive)
- Make sure your **password is correct** (case-sensitive)

---

### 3. **Backend server not running**
**Symptom**: Connection refused errors
**Solution**:
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

### 4. **Database not initialized**
**Symptom**: 500 errors or database connection errors
**Solution**:
```bash
cd backend
python migrations/create_tables.py
```

---

## Testing the Backend Directly

### Test Signup:
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"john","email":"john@example.com","password":"mypassword123"}'
```

**Expected**: 201 Created with user data and JWT token

### Test Login (after signup):
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"john@example.com","password":"mypassword123"}'
```

**Expected**: 200 OK with user data and JWT token

---

## Current Test Account

I just created a test account:
- **Email**: test@example.com
- **Password**: testpass123
- **Username**: testuser

You can log in with these credentials now!

---

## How to Reset and Start Fresh

If you want to clear the database and start over:

```bash
cd backend

# Drop all tables (WARNING: Deletes all data)
python -c "from db import engine; from sqlmodel import SQLModel, text; \
from models import User, Task, TaskTag; \
with engine.begin() as conn: \
    SQLModel.metadata.drop_all(conn)"

# Recreate tables
python migrations/create_tables.py
```

Then signup again with fresh credentials.

---

## Status Check

✅ **Backend is running** - Server responds on port 8000
✅ **Signup works** - Successfully created test account
✅ **Login works** - Successfully logged in with test credentials
✅ **JWT tokens generated** - Authentication working

**The system is working correctly!** 🎉

The 401 error you saw was because you were trying to login **before creating an account**.

---

## Next Steps

1. **Go to**: http://localhost:3000
2. **Click**: "Sign Up" button in navbar
3. **Toggle to Sign Up mode** (if showing signin form)
4. **Create your account**
5. **You'll be auto-logged in** and redirected to tasks page
6. **Try creating a task!** ✅

Or use the test account I created:
- Email: test@example.com
- Password: testpass123
