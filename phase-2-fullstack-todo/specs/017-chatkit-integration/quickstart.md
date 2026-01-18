# Quickstart: ChatKit Frontend-Backend Integration

## Overview
This guide provides instructions for setting up and testing the ChatKit frontend-backend integration that enables intelligent conversations with AI.

## Prerequisites
- Node.js 18+ and npm for frontend
- Python 3.11+ for backend
- uv package manager for Python dependencies
- PostgreSQL database (Neon recommended)
- Better Auth configured with JWT
- OpenAI API key
- MCP server configured for task operations

## Setup Instructions

### 1. Environment Variables
Set up the following environment variables:

**Backend (.env):**
```bash
DATABASE_URL="postgresql://user:password@localhost:5432/taskwave"
BETTER_AUTH_SECRET="your-better-auth-secret"
OPENAI_API_KEY="your-openai-api-key"
```

**Frontend (.env.local):**
```bash
NEXT_PUBLIC_CHATKIT_URL="http://localhost:8000/api/chatkit"
NEXT_PUBLIC_BACKEND_URL="http://localhost:8000"
```

### 2. Install Dependencies
```bash
# Backend
cd backend
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### 3. Database Setup
```bash
cd backend
# Run database migrations to create ChatKit tables
uv run alembic revision --autogenerate -m "Add ChatKit tables"
uv run alembic upgrade head
```

### 4. Start Services
```bash
# Terminal 1: Start backend
cd backend
uv run uvicorn main:app --reload

# Terminal 2: Start frontend
cd frontend
npm run dev
```

## Testing the Integration

### 1. Basic Chat Functionality
1. Navigate to http://localhost:3000/chat
2. Verify the chat interface loads without errors
3. Send a test message: "Hello"
4. Verify AI responds appropriately

### 2. Task Operations via Chat
1. Click "Create Task" tool in composer
2. Send message: "Add a task to buy groceries"
3. Verify task is created (check /tasks page)
4. Confirm the task appears in the task list automatically

### 3. Thread Management
1. Create a new thread
2. Switch between threads
3. Reload page and verify last thread is restored

### 4. Client Effect Events
1. Create a task via chat
2. Verify task list updates automatically
3. Update a task via chat
4. Verify task updates in the list without refresh

### 5. Error Handling
1. Test with invalid JWT token
2. Verify appropriate error messages
3. Test rate limiting scenarios
4. Confirm graceful error recovery

## Key Endpoints
- `POST /api/chatkit/session` - Create ChatKit session with JWT
- `GET /api/users/{user_id}/chat/threads` - Get user's chat threads
- `POST /api/users/{user_id}/chat/messages` - Send chat message
- `GET /api/users/{user_id}/tasks` - Get user's tasks (for synchronization)

## Troubleshooting
- If chat doesn't connect, verify backend is running and JWT is valid
- If AI doesn't respond, check OpenAI API key and network connectivity
- If task synchronization doesn't work, verify MCP server is configured correctly
- If session expires, check JWT expiration time in configuration

## Performance Expectations
- Session establishment: <2 seconds
- AI response time: <5 seconds for 95% of messages
- Task list updates: <1 second
- Loading state feedback: <200ms