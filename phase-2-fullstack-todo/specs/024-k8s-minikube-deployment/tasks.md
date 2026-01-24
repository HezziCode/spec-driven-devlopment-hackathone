# Implementation Tasks: Phase 4 - K8s Minikube Deployment

**Feature Branch**: `024-k8s-minikube-deployment`
**Created**: 2026-01-19
**Status**: Ready for Implementation
**Spec**: [spec.md](./spec.md)
**Plan**: [plan.md](./plan.md)

---

## User Stories Summary

| Story | Priority | Description | Independent Test |
|-------|----------|-------------|------------------|
| US1 | P1 | Developer Containerizes Application | `docker-compose up` + verify all features |
| US2 | P2 | Developer Deploys to Minikube | `helm install` + `minikube service` |
| US3 | P3 | AI-Assisted DevOps Workflow | Document AI tool usage |

---

## Phase 1: Setup

**Goal**: Prepare project structure for containerization

- [x] T001 Create infrastructure directory structure at `/infrastructure/helm/`
- [x] T002 Create backend `.dockerignore` file at `/backend/.dockerignore`
- [x] T003 Create frontend `.dockerignore` file at `/frontend/.dockerignore`
- [x] T004 Create environment template at `/backend/.env.example`
- [x] T005 Create environment template at `/frontend/.env.example`
- [x] T006 [P] Verify Next.js standalone output configuration in `/frontend/next.config.ts`

**Verification**: Directory structure exists, ignore files created

---

## Phase 2: Foundational (Blocking Prerequisites)

**Goal**: Ensure application has required health endpoints

- [x] T007 Verify health endpoint exists at `/backend/main.py` (GET /health)
- [x] T008 [P] Verify frontend can build in standalone mode by running `npm run build`

**Verification**: Health endpoint returns 200, frontend builds successfully

---

## Phase 3: User Story 1 - Docker Containerization (P1)

**Goal**: Package frontend and backend into Docker containers
**Independent Test**: Run `docker-compose up` and verify all features work at localhost

### Backend Docker Image

- [x] T009 [US1] Create multi-stage Dockerfile at `/backend/Dockerfile`
  - Stage 1: builder - Install dependencies with UV
  - Stage 2: runner - Production image with non-root user
  - Base image: python:3.11-slim
  - Expose port 8000

- [ ] T010 [US1] Verify backend Docker build succeeds
  ```bash
  docker build -t taskwave-backend:latest ./backend
  ```

- [ ] T011 [US1] Verify backend image size is under 500MB
  ```bash
  docker images taskwave-backend:latest --format "{{.Size}}"
  ```

### Frontend Docker Image

- [x] T012 [US1] Create multi-stage Dockerfile at `/frontend/Dockerfile`
  - Stage 1: deps - Install node_modules
  - Stage 2: builder - Build Next.js app
  - Stage 3: runner - Production with standalone output
  - Base image: node:22-alpine
  - Expose port 3000

- [ ] T013 [US1] Verify frontend Docker build succeeds
  ```bash
  docker build -t taskwave-frontend:latest ./frontend
  ```

- [ ] T014 [US1] Verify frontend image size is under 500MB
  ```bash
  docker images taskwave-frontend:latest --format "{{.Size}}"
  ```

### Docker Compose

- [x] T015 [US1] Create docker-compose.yml at `/docker-compose.yml`
  - Define frontend service (port 3000)
  - Define backend service (port 8000)
  - Configure network for inter-service communication
  - Environment variable injection from .env
  - Health checks for backend

- [ ] T016 [US1] Test docker-compose startup
  ```bash
  docker-compose up -d
  docker-compose ps
  ```

### Feature Verification (US1)

- [ ] T017 [US1] Verify backend health endpoint at http://localhost:8000/health
- [ ] T018 [US1] Verify frontend loads at http://localhost:3000
- [ ] T019 [US1] Verify authentication works (login/signup)
- [ ] T020 [US1] Verify task CRUD operations work
- [ ] T021 [US1] Verify AI chat feature works with MCP tools
- [ ] T022 [US1] Cleanup: Run `docker-compose down`

**US1 Complete When**: All T009-T022 pass, features work in containers

---

## Phase 4: User Story 2 - Minikube Deployment (P2)

**Goal**: Deploy containerized app to local Kubernetes cluster
**Independent Test**: Run `helm install` and access via `minikube service`

### Backend Helm Chart

- [x] T023 [US2] Create Chart.yaml at `/infrastructure/helm/taskwave-backend/Chart.yaml`
  - apiVersion: v2
  - name: taskwave-backend
  - version: 0.1.0
  - appVersion: "1.0.0"

- [x] T024 [US2] Create values.yaml at `/infrastructure/helm/taskwave-backend/values.yaml`
  - image.repository: taskwave-backend
  - image.tag: latest
  - image.pullPolicy: Never (for Minikube)
  - replicaCount: 2
  - service.type: ClusterIP
  - service.port: 8000
  - resources (requests/limits)
  - config (non-sensitive env vars)

- [x] T025 [US2] Create _helpers.tpl at `/infrastructure/helm/taskwave-backend/templates/_helpers.tpl`

- [x] T026 [US2] Create deployment.yaml at `/infrastructure/helm/taskwave-backend/templates/deployment.yaml`
  - Pod spec with container
  - Environment from ConfigMap and Secret
  - Liveness and readiness probes
  - Resource limits

- [x] T027 [US2] Create service.yaml at `/infrastructure/helm/taskwave-backend/templates/service.yaml`
  - ClusterIP service
  - Port 8000

- [x] T028 [US2] Create configmap.yaml at `/infrastructure/helm/taskwave-backend/templates/configmap.yaml`
  - ENVIRONMENT, LOG_LEVEL, HOST, PORT

- [x] T029 [US2] Verify backend Helm chart with `helm lint ./infrastructure/helm/taskwave-backend`

### Frontend Helm Chart

- [x] T030 [US2] Create Chart.yaml at `/infrastructure/helm/taskwave-frontend/Chart.yaml`

- [x] T031 [US2] Create values.yaml at `/infrastructure/helm/taskwave-frontend/values.yaml`
  - image.repository: taskwave-frontend
  - image.tag: latest
  - image.pullPolicy: Never
  - replicaCount: 2
  - service.type: NodePort
  - service.port: 80
  - service.targetPort: 3000
  - config.NEXT_PUBLIC_API_URL: http://taskwave-backend:8000

- [x] T032 [US2] Create _helpers.tpl at `/infrastructure/helm/taskwave-frontend/templates/_helpers.tpl`

- [x] T033 [US2] Create deployment.yaml at `/infrastructure/helm/taskwave-frontend/templates/deployment.yaml`

- [x] T034 [US2] Create service.yaml at `/infrastructure/helm/taskwave-frontend/templates/service.yaml`
  - NodePort service for external access

- [x] T035 [US2] Create configmap.yaml at `/infrastructure/helm/taskwave-frontend/templates/configmap.yaml`

- [x] T036 [US2] Verify frontend Helm chart with `helm lint ./infrastructure/helm/taskwave-frontend`

### Minikube Deployment

- [ ] T037 [US2] Start Minikube cluster
  ```bash
  minikube start --driver=docker --memory=4096 --cpus=2
  ```

- [ ] T038 [US2] Configure Docker to use Minikube daemon
  ```bash
  eval $(minikube docker-env)
  ```

- [ ] T039 [US2] Build images in Minikube Docker
  ```bash
  docker build -t taskwave-backend:latest ./backend
  docker build -t taskwave-frontend:latest ./frontend
  ```

- [ ] T040 [US2] Create Kubernetes secrets
  ```bash
  kubectl create secret generic taskwave-secrets \
    --from-literal=DATABASE_URL="$DATABASE_URL" \
    --from-literal=BETTER_AUTH_SECRET="$BETTER_AUTH_SECRET" \
    --from-literal=OPENAI_API_KEY="$OPENAI_API_KEY" \
    --from-literal=GOOGLE_OAUTH_CLIENT_ID="$GOOGLE_OAUTH_CLIENT_ID" \
    --from-literal=GOOGLE_OAUTH_CLIENT_SECRET="$GOOGLE_OAUTH_CLIENT_SECRET"
  ```

- [ ] T041 [US2] Deploy backend with Helm
  ```bash
  helm install taskwave-backend ./infrastructure/helm/taskwave-backend
  ```

- [ ] T042 [US2] Verify backend pods are Running
  ```bash
  kubectl get pods -l app.kubernetes.io/name=taskwave-backend
  ```

- [ ] T043 [US2] Deploy frontend with Helm
  ```bash
  helm install taskwave-frontend ./infrastructure/helm/taskwave-frontend
  ```

- [ ] T044 [US2] Verify frontend pods are Running
  ```bash
  kubectl get pods -l app.kubernetes.io/name=taskwave-frontend
  ```

### Feature Verification (US2)

- [ ] T045 [US2] Get frontend URL
  ```bash
  minikube service taskwave-frontend --url
  ```

- [ ] T046 [US2] Verify application loads in browser
- [ ] T047 [US2] Verify authentication works in K8s environment
- [ ] T048 [US2] Verify task CRUD operations work in K8s environment
- [ ] T049 [US2] Verify AI chat feature works in K8s environment

**US2 Complete When**: All T023-T049 pass, app works on Minikube

---

## Phase 5: User Story 3 - AI-Assisted DevOps (P3)

**Goal**: Document AI tool usage for DevOps operations
**Independent Test**: Verify AI-generated artifacts are valid

### Gordon (Docker AI) - Optional

- [ ] T050 [P] [US3] Test Gordon availability
  ```bash
  docker ai "What can you do?"
  ```

- [ ] T051 [P] [US3] Document Gordon usage for Dockerfile optimization (if available)

### kubectl-ai - Optional

- [ ] T052 [P] [US3] Test kubectl-ai availability
  ```bash
  kubectl-ai "list all pods"
  ```

- [ ] T053 [P] [US3] Document kubectl-ai usage for K8s operations (if available)

### kagent - Optional

- [ ] T054 [P] [US3] Test kagent availability and document usage (if available)

### Documentation

- [ ] T055 [US3] Create AI tools usage documentation at `/docs/ai-devops.md`
  - Tools tested
  - Commands used
  - Results obtained
  - Fallback to Claude Code if tools unavailable

**US3 Complete When**: AI tool usage documented

---

## Phase 6: Polish & Documentation

**Goal**: Update documentation and cleanup

- [x] T056 Update README.md with Docker deployment section
- [x] T057 Update README.md with Minikube deployment section
- [x] T058 Update README.md with troubleshooting guide
- [x] T059 Verify all environment templates are complete
- [x] T060 Final cleanup: Remove any temporary files

**Verification**: README has complete deployment instructions

---

## Dependencies

```
Phase 1 (Setup)
    │
    ▼
Phase 2 (Foundational)
    │
    ▼
Phase 3 (US1: Docker) ──────────────────┐
    │                                    │
    ▼                                    │
Phase 4 (US2: Minikube) ◄───────────────┘
    │                         (depends on Docker images)
    ▼
Phase 5 (US3: AI Tools) ◄─── Can run in parallel after US1
    │
    ▼
Phase 6 (Polish)
```

---

## Parallel Execution Opportunities

### Within Phase 1 (Setup)
```
T002 (backend .dockerignore) ─┬─ Can run in parallel
T003 (frontend .dockerignore) ┘

T004 (backend .env.example) ─┬─ Can run in parallel
T005 (frontend .env.example) ┘
```

### Within Phase 3 (US1: Docker)
```
T009-T011 (Backend Docker) ─┬─ Can run in parallel
T012-T014 (Frontend Docker) ┘
```

### Within Phase 4 (US2: Minikube)
```
T023-T029 (Backend Helm) ─┬─ Can run in parallel
T030-T036 (Frontend Helm) ┘
```

### Cross-Phase Parallelism
```
Phase 5 (US3) can start after Phase 3 completes
  - AI tool testing doesn't depend on Minikube deployment
```

---

## Implementation Strategy

### MVP Scope (Recommended First)
**User Story 1 only**: Docker containerization
- Delivers: Working Docker images, docker-compose
- Test: `docker-compose up` runs full app
- Value: Portability, consistency across environments

### Incremental Delivery
1. **Increment 1**: US1 (Docker) - ~60% of effort
2. **Increment 2**: US2 (Minikube) - ~30% of effort
3. **Increment 3**: US3 (AI Tools) - ~10% of effort

### Rollback Points
- After US1: Can revert to pre-Docker state
- After US2: Can uninstall Helm releases
- After US3: Documentation only, no system changes

---

## Task Summary

| Phase | Task Range | Count | Parallelizable |
|-------|------------|-------|----------------|
| Setup | T001-T006 | 6 | 4 |
| Foundational | T007-T008 | 2 | 1 |
| US1: Docker | T009-T022 | 14 | 6 |
| US2: Minikube | T023-T049 | 27 | 14 |
| US3: AI Tools | T050-T055 | 6 | 4 |
| Polish | T056-T060 | 5 | 0 |
| **TOTAL** | T001-T060 | **60** | **29** |

---

## Success Criteria

- [ ] All 60 tasks completed
- [ ] US1: Docker images < 500MB each
- [ ] US1: docker-compose up works with all features
- [ ] US2: All pods in Running state
- [ ] US2: App accessible via minikube service
- [ ] US3: AI tools documented (or fallback noted)
- [ ] README updated with deployment instructions
