# Research: Phase 4 - K8s Minikube Deployment

**Created**: 2026-01-19
**Purpose**: Research findings for containerization and Kubernetes deployment decisions

---

## Research Area 1: Next.js Docker Best Practices

### Decision
Use multi-stage Docker build with `node:22-alpine` base image and standalone output mode.

### Rationale
- **Multi-stage build**: Separates build dependencies from runtime, reducing final image size
- **Alpine base**: Smallest Node.js image (~50MB vs ~350MB for full image)
- **Standalone output**: Next.js 14+ supports `output: 'standalone'` which bundles only production dependencies
- **Security**: Alpine has fewer packages = smaller attack surface

### Best Practice Implementation
```dockerfile
# Stage 1: Dependencies
FROM node:22-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Stage 2: Build
FROM node:22-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Stage 3: Production
FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
EXPOSE 3000
CMD ["node", "server.js"]
```

### Alternatives Considered
| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Single-stage build | Simple | Large image (~1GB) | Rejected |
| Debian base | More compatible | 3x larger | Rejected |
| Distroless | Most secure | Complex debugging | Future consideration |

---

## Research Area 2: FastAPI Docker Best Practices

### Decision
Use multi-stage Docker build with `python:3.11-slim` base image and UV for dependency management.

### Rationale
- **python:3.11-slim**: Balance between size (~150MB) and compatibility
- **UV package manager**: Faster than pip, already used in project
- **Multi-stage**: Build dependencies (gcc, etc.) not needed in production
- **Non-root user**: Security best practice

### Best Practice Implementation
```dockerfile
# Stage 1: Build
FROM python:3.11-slim AS builder
WORKDIR /app
RUN pip install uv
COPY pyproject.toml ./
RUN uv pip install --system --no-cache-dir -r pyproject.toml

# Stage 2: Production
FROM python:3.11-slim AS runner
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . .
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Alternatives Considered
| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| python:3.11-alpine | Smallest | Compilation issues with some packages | Rejected |
| python:3.11 (full) | Most compatible | ~900MB image | Rejected |
| Distroless Python | Most secure | No shell for debugging | Future consideration |

---

## Research Area 3: Kubernetes Service Communication

### Decision
Use Kubernetes ClusterIP service for backend with DNS-based service discovery.

### Rationale
- **ClusterIP**: Internal-only service, not exposed externally (secure)
- **DNS**: Kubernetes provides automatic DNS (`<service>.<namespace>.svc.cluster.local`)
- **Environment variable**: Simpler alternative but DNS is more flexible

### Service Communication Pattern
```
Frontend Pod → Backend Service (ClusterIP) → Backend Pods
              http://taskwave-backend:8000
```

### Frontend Configuration
```yaml
# In frontend deployment
env:
  - name: NEXT_PUBLIC_API_URL
    value: "http://taskwave-backend:8000"
```

### Alternatives Considered
| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Service DNS | Auto-updated, standard | Requires CoreDNS | Selected |
| Environment variables | Simple | Manual updates on IP change | Backup option |
| Ingress routing | Single entry point | Overkill for local | Phase 5 |

---

## Research Area 4: Helm Chart Structure

### Decision
Create separate Helm charts for frontend and backend with shared values pattern.

### Rationale
- **Separate charts**: Independent deployment and scaling
- **Parameterized values**: Easy environment configuration
- **Templates**: Reusable deployment, service, configmap, secret templates

### Recommended Structure
```
infrastructure/helm/
├── taskwave-frontend/
│   ├── Chart.yaml           # Chart metadata
│   ├── values.yaml          # Default values
│   ├── values-dev.yaml      # Development overrides
│   └── templates/
│       ├── deployment.yaml
│       ├── service.yaml
│       ├── configmap.yaml
│       ├── secret.yaml
│       └── _helpers.tpl
└── taskwave-backend/
    ├── Chart.yaml
    ├── values.yaml
    ├── values-dev.yaml
    └── templates/
        ├── deployment.yaml
        ├── service.yaml
        ├── configmap.yaml
        ├── secret.yaml
        └── _helpers.tpl
```

### Alternatives Considered
| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Separate charts | Independent, clear | More files | Selected |
| Umbrella chart | Single install | Coupled deployment | Phase 5 |
| Kustomize | K8s native | Less portable | Rejected |

---

## Research Area 5: Health Probes Configuration

### Decision
Implement both liveness and readiness probes with appropriate thresholds.

### Rationale
- **Liveness probe**: Restarts container if app is stuck
- **Readiness probe**: Removes from service if not ready to receive traffic
- **Different endpoints**: Health check vs ready check may differ

### Recommended Configuration

**Frontend (Next.js)**:
```yaml
livenessProbe:
  httpGet:
    path: /
    port: 3000
  initialDelaySeconds: 30
  periodSeconds: 10
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /
    port: 3000
  initialDelaySeconds: 5
  periodSeconds: 5
  failureThreshold: 3
```

**Backend (FastAPI)**:
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 15
  periodSeconds: 10
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
  failureThreshold: 3
```

---

## Research Area 6: Minikube Docker Integration

### Decision
Use `eval $(minikube docker-env)` to build images directly in Minikube's Docker daemon.

### Rationale
- **No registry needed**: Images available immediately in cluster
- **Faster iteration**: No push/pull cycle
- **Simple setup**: Single command to configure

### Workflow
```bash
# Configure shell to use Minikube's Docker
eval $(minikube docker-env)

# Build images (now in Minikube's daemon)
docker build -t taskwave-frontend:latest ./frontend
docker build -t taskwave-backend:latest ./backend

# Deploy with Helm (imagePullPolicy: Never)
helm install taskwave-frontend ./infrastructure/helm/taskwave-frontend \
  --set image.pullPolicy=Never

helm install taskwave-backend ./infrastructure/helm/taskwave-backend \
  --set image.pullPolicy=Never
```

### Alternatives Considered
| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| Minikube docker-env | Simple, fast | Session-specific | Selected |
| Local registry | Persistent | Extra setup | Backup option |
| minikube image load | Works across drivers | Slower for large images | Alternative |

---

## Research Area 7: Environment Variable Management

### Decision
Use ConfigMaps for non-sensitive config and Secrets for sensitive data.

### Rationale
- **ConfigMaps**: Base64 encoded but not encrypted, visible in kubectl describe
- **Secrets**: Also base64 but treated specially by K8s, can integrate with vault
- **Clear separation**: Security best practice

### Classification

| Variable | Type | Reason |
|----------|------|--------|
| NEXT_PUBLIC_API_URL | ConfigMap | Public URL, not sensitive |
| ENVIRONMENT | ConfigMap | Environment flag |
| LOG_LEVEL | ConfigMap | Configuration |
| HOST | ConfigMap | Network config |
| PORT | ConfigMap | Network config |
| DATABASE_URL | Secret | Contains credentials |
| OPENAI_API_KEY | Secret | API key |
| BETTER_AUTH_SECRET | Secret | Auth secret |
| GOOGLE_OAUTH_CLIENT_ID | Secret | OAuth credential |
| GOOGLE_OAUTH_CLIENT_SECRET | Secret | OAuth credential |

---

## Research Area 8: Resource Limits for Minikube

### Decision
Set conservative resource limits suitable for local development.

### Rationale
- **Minikube default**: 2 CPU, 4GB RAM
- **Two replicas each**: Need to fit 4 pods
- **Leave headroom**: For system pods and overhead

### Recommended Limits

**Frontend**:
```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "100m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

**Backend**:
```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "100m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

### Total Resource Budget
- 4 pods × 256Mi request = 1GB memory reserved
- 4 pods × 100m CPU request = 400m CPU reserved
- Leaves ~3GB memory and ~1.6 CPU for overhead

---

## Summary of Decisions

| Area | Decision | Confidence |
|------|----------|------------|
| Frontend Docker | Multi-stage, node:22-alpine, standalone | High |
| Backend Docker | Multi-stage, python:3.11-slim, UV | High |
| Service Communication | ClusterIP + DNS | High |
| Helm Structure | Separate charts | High |
| Health Probes | Liveness + Readiness | High |
| Minikube Integration | docker-env | High |
| Env Vars | ConfigMap + Secret split | High |
| Resources | Conservative limits | Medium |

---

## Open Questions (None)

All technical decisions have been made based on research. No clarifications needed.
