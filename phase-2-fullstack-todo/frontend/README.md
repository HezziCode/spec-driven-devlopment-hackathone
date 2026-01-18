This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

# TaskWave - Full-Stack Todo Application with AI Chatbot

TaskWave is a modern, full-stack task management application with AI-powered natural language interactions. Built with Next.js, FastAPI, PostgreSQL, and ChatKit React.

## Features

### Core Features
- **User Authentication**: Sign up, sign in, and Google OAuth integration
- **Task Management**: Create, view, update, delete, and complete tasks
- **Task Organization**: Filter by status, search by keyword, sort by criteria
- **Task Properties**: Priority levels (low, medium, high, critical), tags/categories
- **User Profiles**: Manage user account information

### AI Chatbot (Phase 3)
- **ChatKit Integration**: Natural language interface for task management powered by @openai/chatkit-react
- **Session Management**: Secure JWT-based session initialization
- **Multi-Thread Conversations**: Create and switch between multiple chat threads
- **Tool Menu**: Quick access to task operations (Create Task, Search Tasks, View All Tasks)
- **Real-Time Responses**: Streaming AI responses with thinking indicators
- **Thread Persistence**: Automatic sync to backend and localStorage
- **TaskWave Theme**: Consistent teal-cyan gradients, wave animations, dark mode support

## Getting Started

### Prerequisites
- Node.js 18+ and npm/yarn/pnpm/bun
- Python 3.11+ and UV (for backend)
- Neon PostgreSQL database
- OpenAI API key (for AI chatbot features)

### Environment Variables

#### Frontend (.env.local)
```bash
# Database API
NEXT_PUBLIC_API_URL=http://localhost:8000

# Auth (Better Auth)
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_APP_URL=http://localhost:3000

# ChatKit (AI Chatbot)
NEXT_PUBLIC_CHATKIT_ENABLED=true
```

#### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Auth
BETTER_AUTH_SECRET=your-jwt-secret-min-32-characters

# OpenAI (for ChatKit)
OPENAI_API_KEY=your-openai-api-key

# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### Running the Application

First, run the development server:

```bash
# Frontend
cd frontend
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev

# Backend (in a separate terminal)
cd backend
uv run uvicorn main:app --reload
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the application.

### Using the AI Chatbot

1. Navigate to `/chat` or click "AI Assistant" in the navigation
2. Authenticate (sign in or sign up) if not already logged in
3. Start chatting naturally:
   - "Add a task to buy groceries"
   - "Show me all pending tasks"
   - "Mark my grocery task as complete"
   - "Search for work tasks"

### Available Chat Tools

The AI chatbot provides three quick-access tools:
- **Create Task**: Quickly create a new task
- **Search Tasks**: Find tasks by keyword
- **View All Tasks**: See your complete task list

## Project Structure

```
/
├── frontend/              # Next.js 16+ App Router application
│   ├── app/              # Pages and layouts
│   │   ├── chat/         # AI chatbot interface
│   │   ├── tasks/         # Task management pages
│   │   └── auth/         # Authentication pages
│   ├── components/        # React components
│   ├── lib/              # Utilities and API clients
│   │   ├── chatkit-api.ts # ChatKit API integration
│   │   └── auth.ts       # Authentication utilities
│   └── types/            # TypeScript type definitions
├── backend/              # FastAPI application
│   ├── routes/            # API endpoints
│   ├── services/          # Business logic
│   ├── models/            # SQLModel database models
│   ├── schemas/           # Pydantic schemas
│   └── middleware/        # Custom middleware
└── specs/               # Feature specifications
```

## Learn More

To learn more about the technologies used:

- [Next.js Documentation](https://nextjs.org/docs) - Learn about Next.js features and API
- [FastAPI Documentation](https://fastapi.tiangolo.com/) - Modern, fast web framework for building APIs
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/) - SQLModel ORM for database operations
- [ChatKit React](https://github.com/openai/chatkit-react) - React components for AI chat interfaces
- [Better Auth](https://www.better-auth.com/) - Authentication library for Next.js

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
