# Quickstart: Add Task Feature

## Overview
This guide provides a quick start for developers implementing the Add Task feature. It covers the essential components, API usage, and testing procedures.

## Prerequisites
- Python 3.11+ with UV package manager
- Node.js 18+ with npm
- Next.js 16+ development environment
- PostgreSQL database (Neon Serverless recommended)
- Better Auth configured for authentication

## Backend Setup

### 1. Install Dependencies
```bash
cd backend
uv venv  # Create virtual environment
source .venv/bin/activate  # Activate virtual environment
uv add fastapi sqlmodel python-jose[cryptography] python-multipart
uv add better-auth uvicorn pytest
```

### 2. Environment Variables
Create a `.env` file in the backend directory:
```env
DATABASE_URL="postgresql://username:password@localhost/dbname"
BETTER_AUTH_SECRET="your-secret-key-here"
ENVIRONMENT="development"
LOG_LEVEL="INFO"
```

### 3. Run Backend Server
```bash
cd backend
uvicorn main:app --reload --port 8000
```

## Frontend Setup

### 1. Install Dependencies
```bash
cd frontend
npm install
# Dependencies should include: next, react, react-dom, better-auth, typescript
```

### 2. Environment Variables
Create a `.env.local` file in the frontend directory:
```env
NEXT_PUBLIC_API_BASE_URL="http://localhost:8000/api/v1"
NEXT_PUBLIC_BETTER_AUTH_URL="http://localhost:4000"
```

### 3. Run Frontend Server
```bash
cd frontend
npm run dev
```

## API Usage

### Creating a Task
To create a new task, make a POST request to:
```
POST /api/v1/users/{user_id}/tasks
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

Request body example:
```json
{
  "title": "Complete project documentation",
  "description": "Write comprehensive docs for the new feature",
  "priority": "high",
  "tags": ["documentation", "important"]
}
```

Successful response (201 Created):
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Complete project documentation",
  "description": "Write comprehensive docs for the new feature",
  "completed": false,
  "priority": "high",
  "tags": ["documentation", "important"],
  "user_id": "123e4567-e89b-12d3-a456-426614174001",
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z"
}
```

## Frontend Component Usage

### TaskForm Component
The TaskForm component can be used in any Next.js page:

```tsx
// Example usage in a page
'use client';

import { TaskForm } from '@/components/task/task-form';

export default function CreateTaskPage() {
  const handleTaskCreate = async (taskData) => {
    // Handle the created task
    console.log('Task created:', taskData);
  };

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-2xl font-bold mb-6">Create New Task</h1>
      <TaskForm onSubmit={handleTaskCreate} />
    </div>
  );
}
```

## Testing

### Backend Tests
Run backend tests with pytest:
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
Run frontend tests:
```bash
cd frontend
npm test
```

### End-to-End Tests
To run integration tests for the complete flow:
```bash
# Run both backend and frontend servers
# Then run integration tests
```

## Key Implementation Files

### Backend
- `backend/models.py` - SQLModel definitions for Task and User
- `backend/routes/tasks.py` - Task creation endpoint
- `backend/services/task_service.py` - Business logic for tasks
- `backend/middleware/auth_middleware.py` - JWT authentication
- `backend/schemas/task.py` - Pydantic schemas for validation

### Frontend
- `frontend/components/task/task-form.tsx` - Task creation form component
- `frontend/lib/api.ts` - API client with JWT handling
- `frontend/lib/types.ts` - TypeScript interfaces
- `frontend/app/tasks/page.tsx` - Task management page

## Common Issues and Solutions

### 1. JWT Authentication Issues
**Problem**: Getting 401 Unauthorized errors
**Solution**: Verify JWT token is included in Authorization header and is valid

### 2. Database Connection Issues
**Problem**: Cannot connect to database
**Solution**: Check DATABASE_URL in environment variables and database credentials

### 3. CORS Issues
**Problem**: Cross-origin errors between frontend and backend
**Solution**: Configure CORS middleware in FastAPI to allow frontend origin

### 4. Validation Errors
**Problem**: Getting 422 validation errors
**Solution**: Ensure request body matches API contract specifications

## Development Workflow

1. **Plan**: Review the implementation plan in `specs/features/plan.md`
2. **Code**: Implement using agents and skills as specified
3. **Test**: Run both unit and integration tests
4. **Validate**: Ensure compliance with constitution principles
5. **Commit**: Make atomic commits with "Co-authored-by: Claude" attribution

## Next Steps
- Implement task listing and viewing functionality
- Add task update and deletion features
- Implement advanced filtering and search capabilities
- Add comprehensive error handling and user feedback