# Tasks: Phase 4 Local Kubernetes Deployment

**Input**: Design documents from `/specs/021-k8s-deployment/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, quickstart.md

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)

## Path Conventions
- **Infrastructure**: `infrastructure/docker/`, `infrastructure/helm/`
- **Specs**: `specs/021-k8s-deployment/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create infrastructure directory structure per implementation plan: `mkdir -p infrastructure/docker infrastructure/helm`
- [ ] T002 Initialize Minikube cluster with Docker driver: `minikube start --driver=docker`
- [ ] T003 [P] Verify AI tools presence: `docker ai --version`, `kubectl krew list | grep ai`, `kagent --version`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core configurations needed for all deployments

- [ ] T004 Setup local Docker environment for Minikube: `eval $(minikube docker-env)`
- [ ] T005 [US2] Create Kubernetes namespace for the application: `kubectl create namespace taskwave`
- [ ] T006 [US2] Configure base Helm Chart scaffolding: `helm create infrastructure/helm/taskwave`

---

## Phase 3: User Story 1 - AI-Assisted Containerization (Priority: P1) 🎯 MVP

**Goal**: Generate optimized Docker images using Gordon AI

- [ ] T007 [US1] Ask Gordon AI to generate Next.js multi-stage Dockerfile: `docker ai "Create a multi-stage Dockerfile for Next.js 16 in ./frontend"`
- [ ] T008 [US1] Save frontend Dockerfile to `infrastructure/docker/frontend.Dockerfile`
- [ ] T009 [US1] Ask Gordon AI to generate FastAPI multi-stage Dockerfile: `docker ai "Create a multi-stage Dockerfile for FastAPI in ./backend"`
- [ ] T010 [US1] Save backend Dockerfile to `infrastructure/docker/backend.Dockerfile`
- [ ] T011 [P] [US1] Build frontend image: `docker build -t taskwave-frontend:latest -f infrastructure/docker/frontend.Dockerfile .`
- [ ] T012 [P] [US1] Build backend image: `docker build -t taskwave-backend:latest -f infrastructure/docker/backend.Dockerfile .`

**Checkpoint**: Application services are successfully containerized and available in local registry.

---

## Phase 4: User Story 2 - Automated Kubernetes Orchestration (Priority: P2)

**Goal**: Deploy services to Minikube using Helm & kubectl-ai

- [ ] T013 [US2] Generate Kubernetes Secrets using kubectl-ai: `kubectl-ai "create secret taskwave-secrets --from-literal=DATABASE_URL=$DB_URL --from-literal=BETTER_AUTH_SECRET=$AUTH_SECRET"`
- [ ] T014 [US2] Configure frontend deployment in Helm: update `infrastructure/helm/taskwave/values.yaml` with frontend image and env vars
- [ ] T015 [US2] Configure backend deployment in Helm: update `infrastructure/helm/taskwave/values.yaml` with backend image and env vars
- [ ] T016 [US2] Validate Helm chart templates: `helm lint infrastructure/helm/taskwave`
- [ ] T017 [US2] Deploy TaskWave application via Helm: `helm install taskwave-app infrastructure/helm/taskwave -n taskwave`
- [ ] T018 [US2] Expose frontend service using NodePort: `kubectl expose deployment taskwave-frontend --type=NodePort --port=3000 -n taskwave`

**Checkpoint**: All pods are running in Minikube and accessible via NodePort.

---

## Phase 5: User Story 3 - Infrastructure Health Monitoring (Priority: P3)

**Goal**: Verify and optimize cluster health with kagent

- [ ] T019 [US3] Run initial kagent health report: `kagent "analyze the cluster health for namespace taskwave"`
- [ ] T020 [US3] Verify connectivity between frontend and backend pods: `kubectl exec -it [frontend-pod] -- curl http://taskwave-backend:8000/api/health`
- [ ] T021 [US3] Apply resource optimizations suggested by kagent (if any) to `values.yaml`
- [ ] T022 [US3] Final cluster stability check: `kagent "check for pod restarts or resource bottlenecks"`

---

## Phase N: Polish & Cross-Cutting Concerns

- [ ] T023 Update root README.md with Phase 4 deployment instructions
- [ ] T024 Document AI tool versions and prompts used in `history/prompts/`
- [ ] T025 Run final `minikube status` check

## Dependencies & Execution Order

1. **Setup (Phase 1)** -> Core Infra
2. **Foundational (Phase 2)** -> Blocks all stories
3. **User Story 1 (P1)** -> Blocks US2 (needs images)
4. **User Story 2 (P2)** -> Blocks US3 (needs running cluster)
5. **User Story 3 (P3)** -> Observability

## Implementation Strategy

### MVP First (User Story 1 + Basic US2)
1. Build images via Gordon.
2. Direct deployment via `kubectl-ai` before full Helm automation.

### Incremental Delivery
1. Add full Helm packaging.
2. Add kagent monitoring.
