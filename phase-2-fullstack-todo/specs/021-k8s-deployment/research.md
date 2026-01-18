# Research: Phase 4 Kubernetes Deployment Patterns

## Findings

### 1. Multi-stage Docker Builds
- **Decision**: Use `node:20-alpine` for frontend build and `python:3.11-slim` for backend.
- **Rationale**: Reduces image size and attack surface. Multi-stage builds separate build dependencies from runtime environments.
- **AI Tool**: Gordon AI will be asked to: "Create a multi-stage Dockerfile for Next.js 16 optimizing for production size."

### 2. Secret Management
- **Decision**: Use Kubernetes `Secrets` for `DATABASE_URL` and `BETTER_AUTH_SECRET`.
- **Rationale**: Keeps sensitive data out of `values.yaml` and manifests. AI will generate the `kubectl create secret` commands.
- **Alternatives**: ConfigMaps (rejected for sensitive data).

### 3. Minikube Service Exposure
- **Decision**: Use `ServiceType: NodePort`.
- **Rationale**: Simple and reliable for local development without needing a cloud load balancer.
- **AI Tool**: `kubectl-ai "expose frontend deployment via NodePort on port 3000"`.

### 4. Helm Packaging
- **Decision**: Create a single "TaskWave" umbrella chart with subcomponents for frontend and backend.
- **Rationale**: Simplifies life-cycle management (one `helm install` for everything).
