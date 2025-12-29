# Implementation Plan: Frontend-Backend Integration

**Feature**: Frontend-Backend Integration
**Branch**: `013-frontend-backend-integration`
**Created**: 2025-12-25
**Status**: Planning

---

## Executive Summary

This plan integrates the complete FastAPI backend (8 chunks, 13 endpoints) with the Next.js frontend. Implementation focuses on Better Auth configuration, API client creation, and connecting UI components to backend services.

---

## Integration Architecture

### Authentication Flow

```
User → Frontend (Better Auth) → JWT Token → Backend (FastAPI)
  ↓
Better Auth login → Issues JWT → Store in cookie
  ↓
Frontend API calls → Attach JWT to header → Backend verifies
  ↓
Backend validates → Extracts user_id → Returns user's data
```

---

## Implementation Components

### 1. Better Auth Configuration (`frontend/lib/auth.ts`)

Configure Better Auth with JWT plugin:
- Enable JWT plugin
- Set secret to match backend BETTER_AUTH_SECRET
- Configure token storage (httpOnly cookie)
- Set expiration (7 days default)

### 2. API Client (`frontend/lib/api.ts`)

Create centralized API client:
- Base URL from environment variable
- Automatic JWT token attachment
- Error handling wrapper
- Type-safe method signatures

**Methods**:
- Auth: signup(), login(), logout()
- Tasks: getTasks(), createTask(), updateTask(), deleteTask()
- Users: getProfile(), updateProfile()

### 3. Component Updates

**Pages**:
- `/app/tasks/page.tsx` - Connect to getTasks(), createTask(), etc.
- `/app/profile/page.tsx` - Connect to getProfile(), updateProfile()
- `/app/auth/page.tsx` - Use Better Auth hooks

**Components**:
- Update TaskForm to call createTask()
- Update TaskCard to call updateTask(), deleteTask()
- Update TaskFilters to call getTasks() with parameters
- Add loading spinners during API calls
- Add error toasts for API failures

---

## Implementation Order

1. **Configure Better Auth** (1 hour)
2. **Create API Client** (2 hours)
3. **Connect Auth Flow** (2 hours)
4. **Connect Task Operations** (3 hours)
5. **Connect Filters/Search** (1 hour)
6. **Connect Profile** (1 hour)
7. **Error Handling & Polish** (2 hours)

**Total**: ~12 hours

---

## Success Metrics

- ✅ All API endpoints accessible from frontend
- ✅ Authentication flow working end-to-end
- ✅ Task CRUD operations functional
- ✅ Search and filters working
- ✅ Error handling graceful
- ✅ Loading states visible

---

## Next Steps

Run `/sp.tasks` to generate detailed implementation tasks.
