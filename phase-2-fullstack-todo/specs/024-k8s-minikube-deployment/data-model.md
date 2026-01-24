# Data Model: Phase 4 - K8s Minikube Deployment

**Created**: 2026-01-19
**Purpose**: Define infrastructure entities and their relationships for containerization and Kubernetes deployment

---

## Overview

Phase 4 does not introduce new application data models. Instead, it defines **infrastructure entities** - the Docker and Kubernetes resources that package and deploy the existing Phase 3 application.

---

## Infrastructure Entities

### 1. Docker Image (Frontend)

**Description**: Containerized Next.js 16 application

| Attribute | Type | Description |
|-----------|------|-------------|
| name | string | `taskwave-frontend` |
| tag | string | Version tag (e.g., `latest`, `v1.0.0`) |
| base_image | string | `node:22-alpine` |
| exposed_port | integer | `3000` |
| size_limit | string | `< 500MB` |
| build_context | path | `./frontend` |

**Build Stages**:
1. `deps` - Install production dependencies
2. `builder` - Build Next.js application
3. `runner` - Production runtime

---

### 2. Docker Image (Backend)

**Description**: Containerized FastAPI application with MCP server and AI agents

| Attribute | Type | Description |
|-----------|------|-------------|
| name | string | `taskwave-backend` |
| tag | string | Version tag (e.g., `latest`, `v1.0.0`) |
| base_image | string | `python:3.11-slim` |
| exposed_port | integer | `8000` |
| size_limit | string | `< 500MB` |
| build_context | path | `./backend` |

**Build Stages**:
1. `builder` - Install Python dependencies with UV
2. `runner` - Production runtime with non-root user

---

### 3. Kubernetes Deployment (Frontend)

**Description**: K8s Deployment resource managing frontend pods

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| name | string | `taskwave-frontend` | Deployment name |
| namespace | string | `default` | K8s namespace |
| replicas | integer | `2` | Number of pod replicas |
| image | string | `taskwave-frontend:latest` | Docker image reference |
| port | integer | `3000` | Container port |
| resources.requests.memory | string | `256Mi` | Memory request |
| resources.requests.cpu | string | `100m` | CPU request |
| resources.limits.memory | string | `512Mi` | Memory limit |
| resources.limits.cpu | string | `500m` | CPU limit |

**Probes**:
- Liveness: `GET /` on port 3000
- Readiness: `GET /` on port 3000

---

### 4. Kubernetes Deployment (Backend)

**Description**: K8s Deployment resource managing backend pods

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| name | string | `taskwave-backend` | Deployment name |
| namespace | string | `default` | K8s namespace |
| replicas | integer | `2` | Number of pod replicas |
| image | string | `taskwave-backend:latest` | Docker image reference |
| port | integer | `8000` | Container port |
| resources.requests.memory | string | `256Mi` | Memory request |
| resources.requests.cpu | string | `100m` | CPU request |
| resources.limits.memory | string | `512Mi` | Memory limit |
| resources.limits.cpu | string | `500m` | CPU limit |

**Probes**:
- Liveness: `GET /health` on port 8000
- Readiness: `GET /health` on port 8000

---

### 5. Kubernetes Service (Frontend)

**Description**: K8s Service exposing frontend pods

| Attribute | Type | Value | Description |
|-----------|------|-------|-------------|
| name | string | `taskwave-frontend` | Service name |
| type | string | `NodePort` | Service type for Minikube access |
| port | integer | `80` | Service port |
| targetPort | integer | `3000` | Container port |
| nodePort | integer | `30080` (optional) | External port on node |

---

### 6. Kubernetes Service (Backend)

**Description**: K8s Service exposing backend pods

| Attribute | Type | Value | Description |
|-----------|------|-------|-------------|
| name | string | `taskwave-backend` | Service name |
| type | string | `ClusterIP` | Internal service |
| port | integer | `8000` | Service port |
| targetPort | integer | `8000` | Container port |

**DNS**: `taskwave-backend.default.svc.cluster.local`

---

### 7. ConfigMap (Frontend)

**Description**: Non-sensitive frontend configuration

| Key | Value | Description |
|-----|-------|-------------|
| NEXT_PUBLIC_API_URL | `http://taskwave-backend:8000` | Backend service URL |

---

### 8. ConfigMap (Backend)

**Description**: Non-sensitive backend configuration

| Key | Value | Description |
|-----|-------|-------------|
| ENVIRONMENT | `production` | Environment flag |
| LOG_LEVEL | `INFO` | Logging level |
| HOST | `0.0.0.0` | Server host |
| PORT | `8000` | Server port |

---

### 9. Secret (Frontend)

**Description**: Sensitive frontend credentials

| Key | Description |
|-----|-------------|
| BETTER_AUTH_SECRET | JWT authentication secret |
| NEXT_PUBLIC_GOOGLE_OAUTH_CLIENT_ID | Google OAuth client ID |
| GOOGLE_OAUTH_CLIENT_SECRET | Google OAuth client secret |

---

### 10. Secret (Backend)

**Description**: Sensitive backend credentials

| Key | Description |
|-----|-------------|
| DATABASE_URL | Neon PostgreSQL connection string |
| BETTER_AUTH_SECRET | JWT authentication secret |
| OPENAI_API_KEY | OpenAI API key for AI agents |
| GOOGLE_OAUTH_CLIENT_ID | Google OAuth client ID |
| GOOGLE_OAUTH_CLIENT_SECRET | Google OAuth client secret |

---

### 11. Helm Chart (Frontend)

**Description**: Helm chart packaging frontend deployment

| File | Purpose |
|------|---------|
| Chart.yaml | Chart metadata (name, version, description) |
| values.yaml | Default configuration values |
| templates/deployment.yaml | Deployment template |
| templates/service.yaml | Service template |
| templates/configmap.yaml | ConfigMap template |
| templates/secret.yaml | Secret template |
| templates/_helpers.tpl | Template helper functions |

---

### 12. Helm Chart (Backend)

**Description**: Helm chart packaging backend deployment

| File | Purpose |
|------|---------|
| Chart.yaml | Chart metadata (name, version, description) |
| values.yaml | Default configuration values |
| templates/deployment.yaml | Deployment template |
| templates/service.yaml | Service template |
| templates/configmap.yaml | ConfigMap template |
| templates/secret.yaml | Secret template |
| templates/_helpers.tpl | Template helper functions |

---

## Entity Relationships

```
┌─────────────────────────────────────────────────────────────────┐
│                      HELM CHARTS                                │
│  ┌─────────────────────┐      ┌─────────────────────┐          │
│  │ taskwave-frontend   │      │ taskwave-backend    │          │
│  │ (Chart)             │      │ (Chart)             │          │
│  └──────────┬──────────┘      └──────────┬──────────┘          │
└─────────────┼───────────────────────────┼───────────────────────┘
              │                           │
              ▼                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    KUBERNETES RESOURCES                         │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Deployment   │  │ Deployment   │  │ ConfigMap    │         │
│  │ (Frontend)   │  │ (Backend)    │  │ (Frontend)   │         │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘         │
│         │                 │                                    │
│         ▼                 ▼          ┌──────────────┐         │
│  ┌──────────────┐  ┌──────────────┐  │ ConfigMap    │         │
│  │ Service      │  │ Service      │  │ (Backend)    │         │
│  │ (NodePort)   │  │ (ClusterIP)  │  └──────────────┘         │
│  └──────────────┘  └──────────────┘                           │
│                                      ┌──────────────┐         │
│                                      │ Secret       │         │
│                                      │ (Frontend)   │         │
│                                      └──────────────┘         │
│                                      ┌──────────────┐         │
│                                      │ Secret       │         │
│                                      │ (Backend)    │         │
│                                      └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
              │                           │
              ▼                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DOCKER IMAGES                              │
│  ┌─────────────────────┐      ┌─────────────────────┐          │
│  │ taskwave-frontend   │      │ taskwave-backend    │          │
│  │ :latest             │      │ :latest             │          │
│  └─────────────────────┘      └─────────────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

---

## State Transitions

### Docker Image Build States

```
Source Code → Building → Built → Tagged → Available in Registry
```

### Kubernetes Pod States

```
Pending → ContainerCreating → Running → (Ready)
                                    ↓
                              Terminating → Terminated
```

### Deployment Rollout States

```
Progressing → Available
     ↓
  Failed (rollback possible)
```

---

## Validation Rules

### Docker Images
- Image size MUST be under 500MB
- Image MUST expose correct port (3000 for frontend, 8000 for backend)
- Image MUST include health check endpoint

### Kubernetes Resources
- Deployment MUST have at least 1 replica
- Service MUST target correct deployment labels
- ConfigMap/Secret keys MUST match expected environment variables
- Resource limits MUST be set to prevent resource exhaustion

### Helm Charts
- Chart.yaml MUST include valid apiVersion, name, and version
- values.yaml MUST provide sensible defaults
- Templates MUST be valid YAML when rendered
