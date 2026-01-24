# Implementation Plan: Phase 4 - K8s Minikube Deployment

**Feature Branch**: `024-k8s-minikube-deployment`
**Created**: 2026-01-19
**Status**: Ready for Implementation
**Spec**: [spec.md](./spec.md)

---

## Technical Context

### Current State
- Phase 3 Todo AI Chatbot fully functional
- Frontend: Next.js 16 deployed on Vercel
- Backend: FastAPI deployed on Render
- Database: Neon PostgreSQL (external, remains unchanged)
- Features: Task CRUD, AI Chatbot with MCP, Auth with Google OAuth

### Target State
- Both services containerized with Docker
- Deployed on local Kubernetes (Minikube)
- Managed via Helm Charts
- All features working identically

### Technology Decisions (from research.md)
| Decision | Choice | Rationale |
|----------|--------|-----------|
| Frontend Base Image | node:22-alpine | Smallest, secure |
| Backend Base Image | python:3.11-slim | Balance size/compatibility |
| Build Strategy | Multi-stage | Optimized image size |
| Service Communication | ClusterIP + DNS | Standard K8s pattern |
| Helm Structure | Separate charts | Independent deployment |
| Minikube Integration | docker-env | No registry needed |

---

## Constitution Check

### Principles Compliance

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Development | ✅ PASS | All artifacts generated via Claude Code |
| II. Clean Code / SRP | ✅ PASS | Each Dockerfile single purpose |
| III. Type Safety | ✅ PASS | No application code changes |
| IV. Accessibility | ✅ PASS | No UI changes |
| V. Performance-First | ✅ PASS | Optimized images < 500MB |
| VI. Modular Architecture | ✅ PASS | Separate Helm charts |
| VII. Stateless Server | ✅ PASS | No state changes |

### Constraints Check

| Constraint | Status | Implementation |
|------------|--------|----------------|
| No manual YAML | ✅ PASS | Helm templates generate YAML |
| Must use Helm | ✅ PASS | Two Helm charts created |
| External database | ✅ PASS | Neon URL in secrets |
| Service DNS communication | ✅ PASS | `taskwave-backend:8000` |
| Feature parity | ✅ PASS | All features tested |
| Image size < 500MB | ✅ PASS | Multi-stage builds |
| WSL2 compatible | ✅ PASS | Docker Desktop driver |

---

## Implementation Phases

### Phase 1: Dockerization (P1 - Critical Path)

**Goal**: Create optimized Docker images for frontend and backend

#### 1.1 Backend Dockerfile
**File**: `/backend/Dockerfile`

```dockerfile
# Stage 1: Build dependencies
FROM python:3.11-slim AS builder
WORKDIR /app
RUN pip install uv
COPY pyproject.toml ./
COPY requirements.txt ./
RUN uv pip install --system --no-cache-dir -r requirements.txt

# Stage 2: Production
FROM python:3.11-slim AS runner
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
ENV HOST=0.0.0.0 PORT=8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 1.2 Frontend Dockerfile
**File**: `/frontend/Dockerfile`

```dockerfile
# Stage 1: Dependencies
FROM node:22-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

# Stage 2: Build
FROM node:22-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# Stage 3: Production
FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
USER nextjs
EXPOSE 3000
ENV PORT=3000
CMD ["node", "server.js"]
```

#### 1.3 Docker Ignore Files
**Files**: `/frontend/.dockerignore`, `/backend/.dockerignore`

#### 1.4 Docker Compose
**File**: `/docker-compose.yml`

#### 1.5 Verification
- [ ] `docker build` succeeds for both images
- [ ] Images under 500MB each
- [ ] `docker-compose up` starts both services
- [ ] All features work at localhost

---

### Phase 2: Helm Charts (P1 - Critical Path)

**Goal**: Create Helm charts for Kubernetes deployment

#### 2.1 Frontend Helm Chart
**Directory**: `/infrastructure/helm/taskwave-frontend/`

Files to create:
- `Chart.yaml` - Chart metadata
- `values.yaml` - Default values
- `templates/deployment.yaml` - Deployment spec
- `templates/service.yaml` - Service spec
- `templates/configmap.yaml` - ConfigMap spec
- `templates/secret.yaml` - Secret spec (optional, use existing)
- `templates/_helpers.tpl` - Template helpers

#### 2.2 Backend Helm Chart
**Directory**: `/infrastructure/helm/taskwave-backend/`

Same structure as frontend with backend-specific values.

#### 2.3 Verification
- [ ] `helm lint` passes for both charts
- [ ] `helm template` renders valid YAML
- [ ] Values are parameterized correctly

---

### Phase 3: Minikube Deployment (P2)

**Goal**: Deploy to local Kubernetes cluster

#### 3.1 Cluster Setup
```bash
minikube start --driver=docker --memory=4096 --cpus=2
eval $(minikube docker-env)
```

#### 3.2 Build Images in Minikube
```bash
docker build -t taskwave-frontend:latest ./frontend
docker build -t taskwave-backend:latest ./backend
```

#### 3.3 Create Secrets
```bash
kubectl create secret generic taskwave-secrets \
  --from-literal=DATABASE_URL="..." \
  --from-literal=BETTER_AUTH_SECRET="..." \
  --from-literal=OPENAI_API_KEY="..." \
  --from-literal=GOOGLE_OAUTH_CLIENT_ID="..." \
  --from-literal=GOOGLE_OAUTH_CLIENT_SECRET="..."
```

#### 3.4 Deploy with Helm
```bash
helm install taskwave-backend ./infrastructure/helm/taskwave-backend \
  --set image.pullPolicy=Never

helm install taskwave-frontend ./infrastructure/helm/taskwave-frontend \
  --set image.pullPolicy=Never
```

#### 3.5 Verification
- [ ] All pods Running
- [ ] Services created
- [ ] Application accessible via `minikube service`
- [ ] All features work

---

### Phase 4: Documentation (P3)

**Goal**: Update documentation for deployment

#### 4.1 README Updates
- Add Docker section
- Add Minikube deployment section
- Add troubleshooting guide

#### 4.2 Environment Templates
- `/frontend/.env.example`
- `/backend/.env.example`

---

## File Structure After Implementation

```
phase-2-fullstack-todo/
├── frontend/
│   ├── Dockerfile              # NEW
│   ├── .dockerignore           # NEW
│   └── .env.example            # NEW/UPDATE
├── backend/
│   ├── Dockerfile              # NEW
│   ├── .dockerignore           # NEW
│   └── .env.example            # NEW/UPDATE
├── infrastructure/
│   └── helm/
│       ├── taskwave-frontend/  # NEW
│       │   ├── Chart.yaml
│       │   ├── values.yaml
│       │   └── templates/
│       │       ├── deployment.yaml
│       │       ├── service.yaml
│       │       ├── configmap.yaml
│       │       └── _helpers.tpl
│       └── taskwave-backend/   # NEW
│           ├── Chart.yaml
│           ├── values.yaml
│           └── templates/
│               ├── deployment.yaml
│               ├── service.yaml
│               ├── configmap.yaml
│               └── _helpers.tpl
├── docker-compose.yml          # NEW
├── README.md                   # UPDATE
└── specs/
    └── 024-k8s-minikube-deployment/
        ├── spec.md
        ├── plan.md             # THIS FILE
        ├── research.md
        ├── data-model.md
        ├── quickstart.md
        ├── checklists/
        │   └── requirements.md
        └── contracts/
            ├── helm-values-frontend.yaml
            ├── helm-values-backend.yaml
            └── docker-compose.yaml
```

---

## Risk Mitigation

| Risk | Mitigation | Fallback |
|------|------------|----------|
| Docker build fails | Multi-stage builds, clear errors | Debug with single-stage |
| Image too large | Alpine base, multi-stage | Optimize dependencies |
| Network issues | Health probes, retry logic | Manual DNS config |
| Minikube resources | Conservative limits | Reduce replicas to 1 |
| AI tools unavailable | Claude Code fallback | Manual with templates |

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Frontend image size | < 500MB | `docker images` |
| Backend image size | < 500MB | `docker images` |
| Docker Compose startup | < 60s | Manual timing |
| Pod startup time | < 3min | `kubectl get pods` |
| Feature parity | 100% | Manual testing |
| Health check pass | 100% | Probe success |

---

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| Phase 3 codebase | ✅ Ready | All features working |
| Docker Desktop | Required | User must install |
| Minikube | Required | User must install |
| Helm CLI | Required | User must install |
| Environment variables | Required | User provides secrets |

---

## Next Steps

1. Run `/sp.tasks` to generate implementation tasks
2. Execute tasks in order (Phase 1 → Phase 2 → Phase 3 → Phase 4)
3. Test each phase before proceeding
4. Document any issues and solutions

---

## Architectural Decision

**ADR Candidate**: Container orchestration strategy (Minikube for local, cloud K8s for production)

This decision affects Phase 4 and Phase 5 deployment approaches. Consider documenting via `/sp.adr` if needed.
