# Implementation Plan: Full TaskWave Application Kubernetes Deployment

**Feature**: 022-chatbot-only (renamed to full-k8s-deployment)
**Created**: 2026-01-09
**Updated**: 2026-01-09
**Status**: Ready for Implementation

## Executive Summary

Deploy the complete TaskWave application (Phase 2 + Phase 3) to Kubernetes including:
- Full Next.js frontend (landing, auth, tasks, chat, profile pages)
- Complete FastAPI backend (auth, tasks, chat, user routes)
- Better Auth with JWT authentication
- Multi-user support with proper user isolation
- AI chatbot with OpenAI Agents SDK + MCP server
- Containerized deployment to Docker Desktop Kubernetes

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Kubernetes Cluster                        │
│                                                                   │
│  ┌────────────────────┐         ┌─────────────────────┐         │
│  │  Frontend Pod      │         │   Backend Pod       │         │
│  │  (Next.js 16)      │────────▶│   (FastAPI)         │         │
│  │                    │  HTTP   │                     │         │
│  │  - Landing Page    │         │  - Auth Routes      │         │
│  │  - Auth Pages      │         │  - Task Routes      │         │
│  │  - Task UI         │         │  - Chat Routes      │─────┐   │
│  │  - Chat UI         │         │  - User Routes      │     │   │
│  │  - Profile UI      │         │  - MCP Server       │     │   │
│  └────────────────────┘         └─────────────────────┘     │   │
│         │                                  │                 │   │
│         │ Port 3000                       │ Port 8000       │   │
│         ▼                                  ▼                 │   │
│  ┌────────────────────┐         ┌─────────────────────┐     │   │
│  │ Frontend Service   │         │  Backend Service    │     │   │
│  │ (ClusterIP)        │         │  (ClusterIP)        │     │   │
│  └────────────────────┘         └─────────────────────┘     │   │
│                                                              │   │
│  ┌──────────────────────────────────────────────────────────┘   │
│  │                                                                │
│  ▼                                                                │
│  ┌─────────────────────┐                                         │
│  │  OpenAI Agents SDK  │                                         │
│  │  + MCP Tools        │                                         │
│  └─────────────────────┘                                         │
└───────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  External Services     │
                    │  - Neon PostgreSQL     │
                    │  - OpenAI API          │
                    │  - Better Auth         │
                    └────────────────────────┘
```

## Key Technical Decisions

### Decision 1: Reuse Existing 021-k8s-deployment Infrastructure

**Context**: We already have Dockerfiles and K8s manifests from 021-k8s-deployment attempt.

**Decision**: Update and fix existing infrastructure rather than create new minimal deployments.

**Rationale**:
- Existing Dockerfiles already built and tested (with fixes applied)
- K8s manifests already created (need updates for proper configuration)
- Faster implementation - build on what's working
- All source code is already complete and functional

**Trade-offs**:
- ✅ Faster deployment
- ✅ All features included
- ✅ Production-ready configuration
- ⚠️ Larger image sizes (but acceptable for local K8s)

### Decision 2: Fix Authentication Configuration

**Context**: Previous deployment had authentication errors due to missing/incorrect env vars.

**Decision**: Properly configure all Better Auth environment variables in K8s secrets.

**Required Environment Variables**:
- Frontend: `NEXT_PUBLIC_API_URL`, `BETTER_AUTH_URL`, `BETTER_AUTH_SECRET`
- Backend: `DATABASE_URL`, `OPENAI_API_KEY`, `BETTER_AUTH_SECRET`, `CORS_ORIGINS`

**Implementation**:
```yaml
# K8s Secret
apiVersion: v1
kind: Secret
metadata:
  name: taskwave-secrets
type: Opaque
stringData:
  DATABASE_URL: "postgresql://..."
  OPENAI_API_KEY: "sk-..."
  BETTER_AUTH_SECRET: "..."
  BETTER_AUTH_URL: "http://localhost:3000"
  CORS_ORIGINS: "http://localhost:3000"
```

### Decision 3: Use Existing Images with imagePullPolicy: Never

**Context**: Images are built locally, not pushed to registry.

**Decision**: Use `imagePullPolicy: Never` to prevent K8s from trying to pull from registry.

**Rationale**:
- Local development with Docker Desktop K8s
- No container registry setup required
- Faster deployments (no pull time)

### Decision 4: Port-Forward for Local Access

**Context**: Need to access K8s services from host machine.

**Decision**: Use `kubectl port-forward` for both frontend and backend access.

**Commands**:
```bash
kubectl port-forward service/taskwave-frontend-service 3000:3000
kubectl port-forward service/taskwave-backend-service 8000:8000
```

**Update Frontend Config**:
```bash
kubectl set env deployment/taskwave-frontend NEXT_PUBLIC_API_URL=http://localhost:8000
kubectl rollout restart deployment/taskwave-frontend
```

## Implementation Phases

### Phase 0: Prerequisites ✅ COMPLETED

- [x] Docker Desktop installed with Kubernetes enabled
- [x] kubectl CLI installed and configured
- [x] All Phase 2/3 source code complete
- [x] Backend dependencies updated (fastmcp, openai-agents, sse-starlette)
- [x] Frontend dependencies complete

### Phase 1: Docker Image Building ✅ COMPLETED

**Backend Image**:
- [x] Updated backend/requirements.txt with all dependencies
- [x] Built using infrastructure/docker/backend.Dockerfile
- [x] Tagged as `taskwave-backend:latest`
- [x] Fixed Python venv issues

**Frontend Image**:
- [x] Built using infrastructure/docker/frontend.Dockerfile
- [x] Tagged as `taskwave-frontend:latest`
- [x] Fixed non-root user permissions
- [x] Fixed npm cache issues

### Phase 2: Kubernetes Secret Configuration ⚠️ NEEDS UPDATE

**Current State**: Secrets exist but may have incorrect values causing auth errors.

**Tasks**:
1. Delete existing secrets: `kubectl delete secret taskwave-secrets`
2. Create new secrets with correct values:
```bash
kubectl create secret generic taskwave-secrets \
  --from-literal=DATABASE_URL='postgresql://...' \
  --from-literal=OPENAI_API_KEY='sk-...' \
  --from-literal=BETTER_AUTH_SECRET='...' \
  --from-literal=BETTER_AUTH_URL='http://localhost:3000' \
  --from-literal=CORS_ORIGINS='http://localhost:3000'
```
3. Verify secrets: `kubectl get secret taskwave-secrets -o yaml`

### Phase 3: Kubernetes Deployment ⚠️ NEEDS UPDATE

**Current State**: Deployments exist but need configuration updates.

**Backend Deployment Updates Needed**:
```yaml
# infrastructure/helm/templates/backend-deployment.yaml
spec:
  template:
    spec:
      containers:
      - name: backend
        image: taskwave-backend:latest
        imagePullPolicy: Never  # Critical for local images
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: taskwave-secrets
              key: DATABASE_URL
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: taskwave-secrets
              key: OPENAI_API_KEY
        - name: BETTER_AUTH_SECRET
          valueFrom:
            secretKeyRef:
              name: taskwave-secrets
              key: BETTER_AUTH_SECRET
        - name: CORS_ORIGINS
          valueFrom:
            secretKeyRef:
              name: taskwave-secrets
              key: CORS_ORIGINS
```

**Frontend Deployment Updates Needed**:
```yaml
# infrastructure/helm/templates/frontend-deployment.yaml
spec:
  template:
    spec:
      containers:
      - name: frontend
        image: taskwave-frontend:latest
        imagePullPolicy: Never  # Critical for local images
        ports:
        - containerPort: 3000
        env:
        - name: NEXT_PUBLIC_API_URL
          value: "http://localhost:8000"  # Will update after port-forward
        - name: BETTER_AUTH_URL
          valueFrom:
            secretKeyRef:
              name: taskwave-secrets
              key: BETTER_AUTH_URL
        - name: BETTER_AUTH_SECRET
          valueFrom:
            secretKeyRef:
              name: taskwave-secrets
              key: BETTER_AUTH_SECRET
```

**Apply Updates**:
```bash
kubectl apply -f infrastructure/helm/templates/backend-deployment.yaml
kubectl apply -f infrastructure/helm/templates/frontend-deployment.yaml
```

### Phase 4: Service Configuration ✅ SHOULD BE OK

**Verify Services Exist**:
```bash
kubectl get services
# Expected:
# taskwave-backend-service    ClusterIP   10.x.x.x   8000/TCP
# taskwave-frontend-service   ClusterIP   10.x.x.x   3000/TCP
```

If missing, apply:
```bash
kubectl apply -f infrastructure/helm/templates/backend-service.yaml
kubectl apply -f infrastructure/helm/templates/frontend-service.yaml
```

### Phase 5: Port-Forward Setup 🔄 IN PROGRESS

**Start Port Forwards** (need 2 terminals):

Terminal 1 - Backend:
```powershell
kubectl port-forward service/taskwave-backend-service 8000:8000
```

Terminal 2 - Frontend:
```powershell
kubectl port-forward service/taskwave-frontend-service 3000:3000
```

**Update Frontend API URL**:
```bash
kubectl set env deployment/taskwave-frontend NEXT_PUBLIC_API_URL=http://localhost:8000
kubectl rollout restart deployment/taskwave-frontend
```

**Wait for Rollout**:
```bash
kubectl rollout status deployment/taskwave-frontend
kubectl rollout status deployment/taskwave-backend
```

### Phase 6: Testing and Validation ⏳ PENDING

**Test Checklist**:

1. **Health Check**:
   - [ ] Backend health: `curl http://localhost:8000/health`
   - [ ] Frontend loads: Open `http://localhost:3000`

2. **Authentication Flow**:
   - [ ] Landing page loads
   - [ ] Navigate to /auth
   - [ ] Sign up with new account
   - [ ] Verify JWT token issued
   - [ ] Log out
   - [ ] Log in with existing account
   - [ ] Protected routes redirect when not authenticated

3. **Task Management UI**:
   - [ ] Navigate to /tasks
   - [ ] Create new task with form
   - [ ] View task list
   - [ ] Edit existing task
   - [ ] Mark task as complete
   - [ ] Delete task
   - [ ] Search/filter tasks

4. **Chat Interface**:
   - [ ] Navigate to /chat
   - [ ] Send message: "Add task to buy groceries"
   - [ ] Verify task created
   - [ ] Send message: "Show me all my tasks"
   - [ ] Verify tasks listed
   - [ ] Send message: "Mark buy groceries as done"
   - [ ] Verify task completed

5. **User Isolation**:
   - [ ] Create account as User A
   - [ ] Create tasks as User A
   - [ ] Log out
   - [ ] Create account as User B
   - [ ] Verify User B doesn't see User A's tasks

6. **Responsive Design**:
   - [ ] Test on mobile screen size (320px+)
   - [ ] Test on tablet screen size
   - [ ] Test on desktop screen size

## File Structure

```
phase-2-fullstack-todo/
├── frontend/
│   ├── app/
│   │   ├── page.tsx              # Landing page
│   │   ├── auth/page.tsx         # Authentication page
│   │   ├── tasks/page.tsx        # Task management UI
│   │   ├── chat/page.tsx         # Chat interface
│   │   └── profile/page.tsx      # User profile
│   ├── components/
│   │   ├── Navbar.tsx            # Navigation bar
│   │   ├── Footer.tsx            # Footer
│   │   ├── TaskCard.tsx          # Task display
│   │   ├── TaskForm.tsx          # Task creation/editing
│   │   └── ChatInterface.tsx     # Chat UI
│   └── lib/
│       └── api.ts                # API client
├── backend/
│   ├── main.py                   # FastAPI application
│   ├── routes/
│   │   ├── auth.py               # Authentication routes
│   │   ├── tasks.py              # Task CRUD routes
│   │   ├── chat.py               # Chat endpoint
│   │   └── users.py              # User profile routes
│   ├── ai_agents/
│   │   ├── agent.py              # OpenAI Agents SDK agent
│   │   ├── tools.py              # MCP tool wrappers
│   │   └── context.py            # Agent context
│   ├── mcp_server/
│   │   └── server.py             # MCP server implementation
│   ├── middleware/
│   │   └── auth_middleware.py    # JWT verification
│   ├── models.py                 # SQLModel models
│   └── db.py                     # Database connection
└── infrastructure/
    ├── docker/
    │   ├── backend.Dockerfile    # Backend container
    │   └── frontend.Dockerfile   # Frontend container
    └── helm/templates/
        ├── backend-deployment.yaml
        ├── backend-service.yaml
        ├── frontend-deployment.yaml
        └── frontend-service.yaml
```

## Constitution Compliance Check

Verifying against `.specify/memory/constitution.md`:

### ✅ Principle I: Spec-Driven Development (SDD)
- All implementation follows spec.md
- Plan.md created before implementation
- Tasks will be generated via /sp.tasks

### ✅ Principle II: Clean Code and Single Responsibility
- Frontend components are modular
- Backend routes separated by concern
- Clear separation between UI, API, AI agent, and MCP server

### ✅ Principle III: Type Safety and Code Quality
- TypeScript for frontend (strict mode)
- Python type hints for backend
- SQLModel for type-safe database operations

### ✅ Principle IV: Accessibility and Inclusive Design
- Responsive design for all screen sizes
- ARIA labels for screen readers
- Keyboard navigation support

### ✅ Principle V: Performance and Optimization
- Database connection pooling
- Efficient queries with SQLModel
- React optimizations (memo, useCallback where needed)

### ✅ Principle VI: Modular and Reusable Architecture
- Shared components (Navbar, Footer, TaskCard)
- Reusable API client
- Modular backend routes

### ✅ Principle VII: Stateless Architecture
- JWT for stateless auth
- No server-side sessions
- Ephemeral chat (no persistence)

## Risk Analysis and Mitigation

### Risk 1: Authentication Configuration Errors
**Likelihood**: Medium
**Impact**: High (blocks all features)
**Mitigation**:
- Double-check all env var names match between frontend and backend
- Use same BETTER_AUTH_SECRET in both deployments
- Test auth flow before proceeding to other features

### Risk 2: Database Connection Issues from K8s
**Likelihood**: Low
**Impact**: High (no data persistence)
**Mitigation**:
- Verify DATABASE_URL is correct and accessible
- Test connection from pod: `kubectl exec -it <pod> -- python -c "from db import engine; engine.connect()"`
- Check Neon firewall allows connections from K8s cluster IPs

### Risk 3: CORS Errors Between Frontend and Backend
**Likelihood**: Medium
**Impact**: Medium (API calls fail)
**Mitigation**:
- Configure CORS_ORIGINS to include frontend URL
- Update after port-forward setup
- Test with browser dev tools network tab

### Risk 4: Image Size Too Large for K8s
**Likelihood**: Low
**Impact**: Low (slower deployments)
**Mitigation**:
- Multi-stage builds already in place
- Monitor image sizes with `docker images`
- Optimize if exceeds 2GB per image

### Risk 5: Pod Crashes or CrashLoopBackOff
**Likelihood**: Medium
**Impact**: High (services unavailable)
**Mitigation**:
- Check logs immediately: `kubectl logs <pod> --previous`
- Verify all env vars are set
- Add liveness and readiness probes (future improvement)

## Success Metrics

1. **Deployment Success**: All pods in Running state
2. **Authentication Works**: Users can signup, login, logout
3. **User Isolation Works**: Each user sees only their own tasks
4. **Task CRUD Works**: Full lifecycle via UI
5. **Chat Works**: Task operations via natural language
6. **Responsive**: Works on mobile, tablet, desktop
7. **Performance**: API responses < 2s
8. **Zero Manual Code**: All implementation via agents/skills

## Next Steps

After plan approval, run:
```bash
/sp.tasks
```

This will generate actionable tasks for each phase of implementation.

## Notes for Implementation

**PowerShell Commands** (user will run):
- Docker builds (if needed to rebuild)
- kubectl apply commands
- kubectl port-forward commands
- kubectl set env commands

**WSL/Bash Commands** (I will run):
- File modifications
- Git operations
- Spec-Kit-Plus commands
- PHR creation

**Verification Commands**:
```bash
# Check everything is running
kubectl get pods
kubectl get services
kubectl get deployments

# Check logs
kubectl logs deployment/taskwave-backend
kubectl logs deployment/taskwave-frontend

# Describe resources
kubectl describe pod <pod-name>
kubectl describe deployment <deployment-name>
```

## Timeline Estimate

(Note: Per CLAUDE.md guidelines, no time estimates. Focus on what needs to be done.)

**Phase 0**: Prerequisites ✅ Done
**Phase 1**: Docker Images ✅ Done
**Phase 2**: Secret Configuration - Next task
**Phase 3**: Deployment Updates - Next task
**Phase 4**: Service Verification - Quick check
**Phase 5**: Port-Forward Setup - User action
**Phase 6**: Testing - Comprehensive validation

---

**Document Status**: Ready for /sp.tasks
**Constitution Check**: ✅ All principles verified
**Blockers**: None (all prerequisites met)
**User Actions Required**: Run PowerShell kubectl commands as provided
