# Quickstart Guide: Database Foundation Setup

**Feature**: 005-database-foundation
**Last Updated**: 2025-12-23
**Estimated Setup Time**: 15-20 minutes

## Prerequisites

Before you begin, ensure you have:

- ✅ Python 3.11 or higher installed
- ✅ UV package manager installed (`pip install uv`)
- ✅ Neon PostgreSQL account created (https://neon.tech)
- ✅ Git repository cloned and on branch `005-database-foundation`

---

## Step 1: Create Neon PostgreSQL Database (5 minutes)

### 1.1 Sign up for Neon

Visit https://neon.tech and create a free account.

### 1.2 Create New Project

1. Click "Create Project"
2. Project name: `phase2-todo-backend`
3. Select region closest to your location (e.g., `us-east-1`)
4. PostgreSQL version: 16 (latest)
5. Click "Create Project"

### 1.3 Get Connection String

1. In your Neon dashboard, click on your project
2. Navigate to "Connection Details"
3. Copy the connection string (it looks like):
   ```
   postgresql://neondb_owner:abc123xyz@ep-cool-breeze-123456.us-east-1.aws.neon.tech/neondb?sslmode=require
   ```
4. Save this for the next step

---

## Step 2: Configure Environment Variables (2 minutes)

### 2.1 Navigate to Backend Directory

```bash
cd phase-2-fullstack-todo/backend
```

### 2.2 Create .env File

Create a new file named `.env` in the backend directory:

```bash
# Create .env file
touch .env
```

### 2.3 Add Database Configuration

Open `.env` in your editor and add:

```bash
# Neon PostgreSQL Connection String
# Replace with your actual connection string from Step 1.3
DATABASE_URL=postgresql://neondb_owner:your-password@ep-your-instance.region.aws.neon.tech/neondb?sslmode=require
```

**⚠️ IMPORTANT**: Replace the entire URL with your actual Neon connection string!

### 2.4 Verify .env is in .gitignore

Ensure `.env` is excluded from git:

```bash
# Check if .env is ignored
git check-ignore .env
# Should output: .env
```

If not ignored, add to `.gitignore`:
```bash
echo ".env" >> .gitignore
```

---

## Step 3: Install Dependencies (3 minutes)

### 3.1 Install Backend Dependencies

```bash
cd backend  # if not already there
uv sync
```

This installs all required packages:
- sqlmodel
- psycopg2-binary
- fastapi
- python-dotenv
- pytest (dev)
- mypy (dev)

### 3.2 Verify Installation

```bash
uv pip list | grep -E "sqlmodel|psycopg2|fastapi"
```

Expected output:
```
fastapi        0.104.1
psycopg2-binary 2.9.9
sqlmodel       0.0.14
```

---

## Step 4: Run Database Migration (2 minutes)

### 4.1 Create Database Tables

```bash
python migrations/create_tables.py
```

Expected output:
```
Loading database connection...
Creating tables...
✓ Table 'users' created successfully
✓ Table 'tasks' created successfully
✓ Table 'task_tags' created successfully
✓ All indexes created successfully
✓ All foreign key constraints created successfully
Migration complete!
```

### 4.2 Verify Tables Created

Use the test connection script:

```bash
python scripts/test_connection.py
```

Expected output:
```
Testing connection to Neon PostgreSQL...
✓ Connection successful!
✓ Database: neondb
✓ Host: ep-your-instance.region.aws.neon.tech
✓ Tables found: users, tasks, task_tags

All systems ready!
```

---

## Step 5: Run Tests (3 minutes)

### 5.1 Run Model Tests

```bash
pytest tests/test_models.py -v
```

Expected: All tests pass (8-10 test cases)

### 5.2 Run Connection Tests

```bash
pytest tests/test_connection.py -v
```

Expected: All tests pass (5-6 test cases)

### 5.3 Run Migration Tests

```bash
pytest tests/test_migration.py -v
```

Expected: All tests pass (6-8 test cases)

### 5.4 Run All Tests with Coverage

```bash
pytest --cov=backend --cov-report=html
```

Expected output:
```
---------- coverage: platform linux, python 3.11.x -----------
Name                                  Stmts   Miss  Cover
-----------------------------------------------------------
backend/models.py                        45      0   100%
backend/db.py                            15      0   100%
backend/migrations/create_tables.py      20      0   100%
backend/scripts/test_connection.py       12      0   100%
-----------------------------------------------------------
TOTAL                                    92      0   100%

Generated HTML coverage report: htmlcov/index.html
```

---

## Step 6: Verify Type Safety (1 minute)

### 6.1 Run Mypy Type Checking

```bash
mypy backend/models.py backend/db.py --strict
```

Expected output:
```
Success: no issues found in 2 source files
```

---

## Verification Checklist

After completing all steps, verify:

- [X] Neon PostgreSQL database created and accessible
- [X] DATABASE_URL configured in .env file
- [X] All dependencies installed via UV
- [X] Migration script created all three tables
- [X] All indexes and constraints exist in database
- [X] Test connection script reports success
- [X] All pytest tests passing (100% coverage)
- [X] Mypy type checking passes with zero errors
- [X] Models importable: `from backend.models import User, Task, TaskTag`
- [X] Database session works: `from backend.db import get_session`

---

## Troubleshooting

### Issue: "No module named 'sqlmodel'"

**Solution**: Install dependencies
```bash
cd backend
uv sync
```

### Issue: "Connection refused" or "Connection timeout"

**Solution**: Check DATABASE_URL
1. Verify .env file exists in backend directory
2. Check DATABASE_URL format includes `?sslmode=require`
3. Verify Neon database is not paused (check Neon dashboard)
4. Test connection manually: `psql $DATABASE_URL`

### Issue: "FATAL: password authentication failed"

**Solution**: Reset database password
1. Go to Neon dashboard
2. Navigate to your project → Connection Details
3. Click "Reset Password"
4. Copy new connection string to .env file

### Issue: "relation 'users' already exists"

**Solution**: This is normal if you run migration twice
- Migration script is idempotent (safe to re-run)
- Tables are only created if they don't exist
- This message is informational, not an error

### Issue: "mypy: error: No module named 'sqlmodel'"

**Solution**: Install dev dependencies
```bash
uv sync --dev
```

### Issue: "psycopg2-binary: command not found"

**Solution**: Install psycopg2-binary package
```bash
uv add psycopg2-binary
```

---

## Next Steps

Once verification checklist is complete:

1. **Commit your work**:
   ```bash
   git add backend/models.py backend/db.py backend/migrations/
   git commit -m "feat: Add database foundation with User, Task, TaskTag models"
   ```

2. **Proceed to next feature**:
   ```bash
   # Return to main branch or continue with authentication feature
   git checkout main
   ```

3. **Reference in other features**:
   ```python
   # Import models in future features
   from backend.models import User, Task, TaskTag
   from backend.db import get_session
   ```

---

## Quick Command Reference

```bash
# Navigate to backend
cd backend

# Install dependencies
uv sync

# Run migration
python migrations/create_tables.py

# Test connection
python scripts/test_connection.py

# Run tests
pytest

# Run tests with coverage
pytest --cov=backend --cov-report=html

# Type checking
mypy backend/models.py backend/db.py --strict

# Check database tables
psql $DATABASE_URL -c "\dt"

# Check indexes
psql $DATABASE_URL -c "\di"

# Check foreign keys
psql $DATABASE_URL -c "SELECT conname, conrelid::regclass, confrelid::regclass FROM pg_constraint WHERE contype = 'f';"
```

---

**Setup Complete!** 🎉

Your database foundation is ready. Models can now be imported and used by authentication and API endpoint features.
