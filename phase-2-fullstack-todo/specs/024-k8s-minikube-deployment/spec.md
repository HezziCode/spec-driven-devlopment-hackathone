# Feature Specification: Phase 4 - Local Kubernetes Deployment (Minikube)

**Feature Branch**: `024-k8s-minikube-deployment`
**Created**: 2026-01-19
**Status**: Draft
**Phase**: Phase 4 of Hackathon II - Evolution of Todo

## Context

Phase 3 Todo AI Chatbot is fully functional and deployed in production:
- **Frontend**: Next.js 16 on Vercel (https://secure-todoz.vercel.app)
- **Backend**: FastAPI on Render (https://taskwave-api-5qyu.onrender.com)
- **Database**: Neon Serverless PostgreSQL (external, stays as-is)
- **Features**: Task CRUD, AI Chatbot with MCP tools, User Authentication, Google OAuth

## Objective

Containerize the Phase 3 application and deploy it on a local Kubernetes cluster (Minikube) using Helm Charts. Use AI-assisted DevOps tools (Gordon, kubectl-ai, kagent) where available to follow the spec-driven approach.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Developer Containerizes Application (Priority: P1)

A developer wants to package the frontend and backend applications into Docker containers so the application runs consistently across all environments (development, staging, production, Kubernetes).

**Why this priority**: Containerization is the foundation for Kubernetes deployment. Without working Docker images, no K8s deployment is possible. This is the critical path.

**Independent Test**: Can be fully tested by running `docker-compose up` and verifying all features work at localhost:3000 (frontend) and localhost:8000 (backend).

**Acceptance Scenarios**:

1. **Given** the Phase 3 codebase is complete and working, **When** developer runs `docker build` for frontend, **Then** a Docker image is created successfully under 500MB
2. **Given** the Phase 3 codebase is complete and working, **When** developer runs `docker build` for backend, **Then** a Docker image is created successfully under 500MB
3. **Given** both Docker images are built, **When** developer runs `docker-compose up`, **Then** both services start and communicate with each other
4. **Given** containers are running, **When** user accesses the chat page, **Then** AI chatbot responds and MCP tools work correctly
5. **Given** containers are running, **When** user accesses the tasks page, **Then** all CRUD operations work correctly
6. **Given** containers are running, **When** user tries to login/signup, **Then** authentication works including Google OAuth

---

### User Story 2 - Developer Deploys to Minikube (Priority: P2)

A developer wants to deploy the containerized application to a local Kubernetes cluster (Minikube) to simulate production K8s environment.

**Why this priority**: Once containers work, K8s deployment is the next logical step. This validates the application works in orchestrated environment before cloud deployment.

**Independent Test**: Can be tested by running `helm install` commands and accessing services via `minikube service` command.

**Acceptance Scenarios**:

1. **Given** Minikube is installed, **When** developer runs `minikube start`, **Then** local K8s cluster starts successfully
2. **Given** Docker images are built, **When** developer builds images in Minikube's Docker daemon, **Then** images are available to the cluster
3. **Given** Helm charts are created, **When** developer runs `helm install taskwave-frontend`, **Then** frontend pods start with Running status
4. **Given** Helm charts are created, **When** developer runs `helm install taskwave-backend`, **Then** backend pods start with Running status
5. **Given** both services are deployed, **When** developer runs `minikube service taskwave-frontend`, **Then** application is accessible in browser
6. **Given** application is accessible, **When** user tests chat, tasks, and auth features, **Then** all features work correctly

---

### User Story 3 - AI-Assisted DevOps Workflow (Priority: P3)

A developer wants to use AI tools (Gordon, kubectl-ai, kagent) for Docker and Kubernetes operations to follow the hackathon's spec-driven approach.

**Why this priority**: AI-assisted DevOps is a hackathon requirement but not a blocker. Features should work even without AI tools.

**Independent Test**: Can be tested by documenting AI tool usage and verifying generated artifacts are valid.

**Acceptance Scenarios**:

1. **Given** Docker Desktop 4.53+ with Gordon enabled, **When** developer asks Gordon for Dockerfile help, **Then** Gordon provides valid Dockerfile suggestions
2. **Given** kubectl-ai is installed, **When** developer asks for K8s resource generation, **Then** kubectl-ai provides valid YAML manifests
3. **Given** kagent is available, **When** developer asks for cluster health analysis, **Then** kagent provides insights
4. **Given** AI tools are unavailable, **When** developer uses Claude Code as fallback, **Then** valid configurations are still generated

---

### Edge Cases

- What happens when Neon database is unreachable from container? → Application should show connection error gracefully
- What happens when OpenAI API key is invalid? → Chat should show meaningful error, tasks should still work
- What happens when Docker builds fail due to network issues? → Clear error messages, retry mechanism in compose
- What happens when Minikube runs out of resources? → Pods should show resource pressure, configurable limits
- What happens when secrets are not configured? → Pods should fail fast with clear error in logs

---

## Requirements *(mandatory)*

### Functional Requirements

#### Dockerization

- **FR-001**: System MUST provide a multi-stage Dockerfile for the Next.js 16 frontend that produces an optimized production image
- **FR-002**: System MUST provide a multi-stage Dockerfile for the FastAPI backend that includes all dependencies (MCP server, AI agents)
- **FR-003**: System MUST provide a docker-compose.yml file that orchestrates both services for local development testing
- **FR-004**: Docker images MUST be under 500MB each for efficient deployment
- **FR-005**: Containers MUST support environment variable injection for configuration

#### Kubernetes Deployment

- **FR-006**: System MUST deploy frontend as a Kubernetes Deployment with configurable replicas (default: 2)
- **FR-007**: System MUST deploy backend as a Kubernetes Deployment with configurable replicas (default: 2)
- **FR-008**: System MUST expose frontend via a Kubernetes Service (NodePort for Minikube access)
- **FR-009**: System MUST expose backend via a Kubernetes Service for internal communication
- **FR-010**: System MUST use ConfigMaps for non-sensitive configuration (API URLs, environment settings)
- **FR-011**: System MUST use Secrets for sensitive data (API keys, database credentials, auth secrets)

#### Helm Charts

- **FR-012**: System MUST provide a Helm chart for frontend deployment with parameterized values
- **FR-013**: System MUST provide a Helm chart for backend deployment with parameterized values
- **FR-014**: Helm values.yaml MUST allow customization of replicas, resources, and environment variables
- **FR-015**: Helm charts MUST include health check probes (liveness and readiness)

#### Feature Parity

- **FR-016**: All chat features MUST work in containerized environment (MCP tool calls, streaming responses)
- **FR-017**: All task CRUD operations MUST work in containerized environment
- **FR-018**: User authentication MUST work including login, signup, and Google OAuth
- **FR-019**: Frontend MUST communicate with backend via Kubernetes service DNS name

### Key Entities

- **Docker Image (Frontend)**: Next.js 16 application, Node.js v22 runtime, static assets, port 3000
- **Docker Image (Backend)**: FastAPI application, Python 3.11 runtime, MCP server, AI agents, port 8000
- **Helm Chart (Frontend)**: Deployment, Service, ConfigMap, Secret templates for frontend
- **Helm Chart (Backend)**: Deployment, Service, ConfigMap, Secret templates for backend
- **ConfigMap**: Non-sensitive configuration like API URLs, environment flags
- **Secret**: Sensitive data like DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developer can build both Docker images successfully in under 5 minutes each
- **SC-002**: `docker-compose up` starts both services and application is accessible within 60 seconds
- **SC-003**: All existing features (chat, tasks, auth) work identically in containerized environment
- **SC-004**: Minikube deployment completes successfully with all pods in Running state within 3 minutes
- **SC-005**: Application accessed via Minikube has response times comparable to local development (under 500ms for page loads)
- **SC-006**: 100% of acceptance scenarios pass during testing
- **SC-007**: Zero manual Kubernetes YAML files required (all generated via Helm or AI tools)

---

## Scope

### In Scope

1. **Dockerization**
   - Dockerfile for frontend (Next.js 16, Node v22, multi-stage build)
   - Dockerfile for backend (FastAPI, Python 3.11, multi-stage build)
   - docker-compose.yml for local development testing
   - .dockerignore files for optimized builds

2. **Kubernetes Deployment (Minikube)**
   - Frontend Deployment + Service (NodePort)
   - Backend Deployment + Service (ClusterIP/NodePort)
   - ConfigMaps for non-sensitive configuration
   - Secrets for sensitive data
   - Health check probes

3. **Helm Charts**
   - taskwave-frontend chart with templates and values
   - taskwave-backend chart with templates and values
   - Parameterized configuration

4. **Environment Configuration**
   - Frontend: NEXT_PUBLIC_API_URL, auth secrets, Google OAuth
   - Backend: DATABASE_URL, OPENAI_API_KEY, auth secrets, Google OAuth

5. **Documentation**
   - Deployment instructions in README
   - AI tool usage documentation

### Out of Scope

- Database containerization (Neon PostgreSQL remains external cloud service)
- Cloud Kubernetes deployment (AWS EKS, GCP GKE, Azure AKS - Phase 5)
- Kafka/Dapr integration (Phase 5)
- CI/CD pipeline automation (Phase 5)
- Ingress controller setup (optional enhancement)
- TLS/SSL certificates for local deployment
- Horizontal Pod Autoscaler (HPA)

---

## Constraints

- No manual YAML editing where AI tools can generate configurations
- Must use Helm for deployment (not raw kubectl apply)
- External database (Neon) - no local PostgreSQL container needed
- Frontend must communicate with backend via K8s service DNS
- All existing functionality must work after containerization
- Docker images must be under 500MB each
- Must work on Windows WSL2 with Docker Desktop

---

## Assumptions

- Docker Desktop is installed with Kubernetes enabled
- Minikube is installed and configured (using Docker driver)
- kubectl CLI is installed and configured
- Helm CLI is installed (v3+)
- Gordon (Docker AI) is available in Docker Desktop 4.53+ (or fallback to Claude Code)
- kubectl-ai is installed for AI-assisted K8s operations
- Neon database is accessible from local network (internet connectivity)
- Developer has valid API keys (OpenAI, Google OAuth)
- WSL2 is properly configured on Windows

---

## Dependencies

- Phase 3 codebase (complete and working) - **SATISFIED**
- Neon PostgreSQL database (external) - **SATISFIED**
- OpenAI API key (for AI agents) - **REQUIRED**
- Google OAuth credentials - **REQUIRED**
- Docker Desktop - **REQUIRED**
- Minikube - **REQUIRED**
- Helm CLI - **REQUIRED**

---

## Deliverables

| # | Deliverable | Path |
|---|-------------|------|
| 1 | Frontend Dockerfile | `/frontend/Dockerfile` |
| 2 | Backend Dockerfile | `/backend/Dockerfile` |
| 3 | Docker Compose file | `/docker-compose.yml` |
| 4 | Frontend Helm Chart | `/infrastructure/helm/taskwave-frontend/` |
| 5 | Backend Helm Chart | `/infrastructure/helm/taskwave-backend/` |
| 6 | Docker ignore files | `/frontend/.dockerignore`, `/backend/.dockerignore` |
| 7 | Environment templates | `/frontend/.env.example`, `/backend/.env.example` |
| 8 | Updated README | `/README.md` (deployment section) |
| 9 | Spec documentation | `/specs/024-k8s-minikube-deployment/` |

---

## Technical Notes

### Docker Image Specifications

| Service | Base Image | Port | Target Size |
|---------|-----------|------|-------------|
| Frontend | node:22-alpine | 3000 | < 500MB |
| Backend | python:3.11-slim | 8000 | < 500MB |

### Kubernetes Resources

| Resource | Frontend | Backend |
|----------|----------|---------|
| Deployment | 2 replicas | 2 replicas |
| Service | NodePort | ClusterIP + NodePort |
| ConfigMap | API URLs | Environment config |
| Secret | Auth secrets | DB + API keys |
| Probes | Liveness + Readiness | Liveness + Readiness |

### Environment Variables

**Frontend ConfigMap:**
- `NEXT_PUBLIC_API_URL` - Backend K8s service URL

**Frontend Secret:**
- `BETTER_AUTH_SECRET`
- `NEXT_PUBLIC_GOOGLE_OAUTH_CLIENT_ID`
- `GOOGLE_OAUTH_CLIENT_SECRET`

**Backend ConfigMap:**
- `ENVIRONMENT=production`
- `LOG_LEVEL=INFO`
- `HOST=0.0.0.0`
- `PORT=8000`

**Backend Secret:**
- `DATABASE_URL`
- `BETTER_AUTH_SECRET`
- `OPENAI_API_KEY`
- `GOOGLE_OAUTH_CLIENT_ID`
- `GOOGLE_OAUTH_CLIENT_SECRET`

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Docker build failures | Medium | High | Multi-stage builds, clear error handling |
| Network connectivity in containers | Medium | High | Proper service DNS, health probes |
| Resource constraints in Minikube | Medium | Medium | Configurable resource limits |
| AI tools unavailable | Low | Low | Claude Code as fallback |
| Google OAuth redirect issues | Medium | Medium | Configurable redirect URLs |
