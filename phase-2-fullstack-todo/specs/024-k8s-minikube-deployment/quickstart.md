# Quickstart Guide: Phase 4 - K8s Minikube Deployment

**Created**: 2026-01-19
**Purpose**: Step-by-step guide to containerize and deploy TaskWave on Minikube

---

## Prerequisites

Before starting, ensure you have the following installed:

| Tool | Version | Check Command | Install Guide |
|------|---------|---------------|---------------|
| Docker Desktop | 4.53+ | `docker --version` | [docker.com/get-docker](https://docker.com/get-docker) |
| Minikube | Latest | `minikube version` | [minikube.sigs.k8s.io](https://minikube.sigs.k8s.io/docs/start/) |
| kubectl | Latest | `kubectl version --client` | Comes with Docker Desktop |
| Helm | v3+ | `helm version` | [helm.sh/docs/intro/install](https://helm.sh/docs/intro/install/) |

### Optional AI Tools
| Tool | Purpose | Install |
|------|---------|---------|
| Gordon | Docker AI Agent | Enable in Docker Desktop Settings > Beta features |
| kubectl-ai | K8s AI Assistant | `brew install kubectl-ai` or npm |
| kagent | K8s AI Operations | See kagent documentation |

---

## Part 1: Docker Containerization

### Step 1.1: Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# Copy from existing .env files or create new
cat > .env << 'EOF'
DATABASE_URL=your_neon_connection_string
BETTER_AUTH_SECRET=your_auth_secret
OPENAI_API_KEY=your_openai_key
GOOGLE_OAUTH_CLIENT_ID=your_google_client_id
GOOGLE_OAUTH_CLIENT_SECRET=your_google_client_secret
EOF
```

### Step 1.2: Build Docker Images

```bash
# Build frontend image
docker build -t taskwave-frontend:latest ./frontend

# Build backend image
docker build -t taskwave-backend:latest ./backend

# Verify images
docker images | grep taskwave
```

**Expected Output**:
```
taskwave-frontend   latest   abc123   < 500MB
taskwave-backend    latest   def456   < 500MB
```

### Step 1.3: Test with Docker Compose

```bash
# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Test endpoints
curl http://localhost:3000        # Frontend
curl http://localhost:8000/health # Backend
```

### Step 1.4: Verify Features

Open browser and test:
1. **Auth**: http://localhost:3000/auth - Login/Signup
2. **Tasks**: http://localhost:3000/tasks - CRUD operations
3. **Chat**: http://localhost:3000/chat - AI chatbot

### Step 1.5: Clean Up Docker Compose

```bash
docker-compose down
```

---

## Part 2: Minikube Deployment

### Step 2.1: Start Minikube

```bash
# Start Minikube with Docker driver
minikube start --driver=docker --memory=4096 --cpus=2

# Verify cluster
kubectl cluster-info
kubectl get nodes
```

### Step 2.2: Configure Docker Environment

```bash
# Point shell to Minikube's Docker daemon
eval $(minikube docker-env)

# Verify (should show Minikube's Docker)
docker info | grep -i name
```

### Step 2.3: Build Images in Minikube

```bash
# Build images (now in Minikube's daemon)
docker build -t taskwave-frontend:latest ./frontend
docker build -t taskwave-backend:latest ./backend

# Verify images are in Minikube
docker images | grep taskwave
```

### Step 2.4: Create Kubernetes Secrets

```bash
# Create secrets from .env file
kubectl create secret generic taskwave-secrets \
  --from-literal=DATABASE_URL="$DATABASE_URL" \
  --from-literal=BETTER_AUTH_SECRET="$BETTER_AUTH_SECRET" \
  --from-literal=OPENAI_API_KEY="$OPENAI_API_KEY" \
  --from-literal=GOOGLE_OAUTH_CLIENT_ID="$GOOGLE_OAUTH_CLIENT_ID" \
  --from-literal=GOOGLE_OAUTH_CLIENT_SECRET="$GOOGLE_OAUTH_CLIENT_SECRET"

# Verify
kubectl get secrets
```

### Step 2.5: Deploy with Helm

```bash
# Install backend first (frontend depends on it)
helm install taskwave-backend ./infrastructure/helm/taskwave-backend \
  --set image.pullPolicy=Never \
  --set secrets.existingSecret=taskwave-secrets

# Install frontend
helm install taskwave-frontend ./infrastructure/helm/taskwave-frontend \
  --set image.pullPolicy=Never \
  --set secrets.existingSecret=taskwave-secrets

# Verify deployments
kubectl get deployments
kubectl get pods
kubectl get services
```

### Step 2.6: Access the Application

```bash
# Get frontend URL
minikube service taskwave-frontend --url

# Or use port forwarding
kubectl port-forward svc/taskwave-frontend 3000:80
```

Open the URL in your browser and test all features.

---

## Part 3: AI-Assisted Operations (Optional)

### Using Gordon (Docker AI)

```bash
# Ask Gordon for help
docker ai "How do I optimize my Dockerfile for production?"
docker ai "What's wrong with my container that keeps crashing?"
```

### Using kubectl-ai

```bash
# Generate resources
kubectl-ai "create a deployment for my frontend with 2 replicas"
kubectl-ai "show me pods that are not running"

# Troubleshoot
kubectl-ai "why is my pod in CrashLoopBackOff?"
kubectl-ai "check resource usage across all pods"
```

### Using kagent

```bash
# Cluster analysis
kagent "analyze cluster health"
kagent "suggest resource optimizations"
```

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Image not found in Minikube | Run `eval $(minikube docker-env)` before building |
| Pod CrashLoopBackOff | Check logs: `kubectl logs <pod-name>` |
| Service not accessible | Verify service type is NodePort: `kubectl get svc` |
| Database connection failed | Check DATABASE_URL in secrets |
| Health check failing | Ensure `/health` endpoint exists in backend |

### Useful Commands

```bash
# View pod logs
kubectl logs -f deployment/taskwave-backend

# Describe pod for events
kubectl describe pod <pod-name>

# Execute into container
kubectl exec -it <pod-name> -- /bin/sh

# Check resource usage
kubectl top pods

# Restart deployment
kubectl rollout restart deployment/taskwave-frontend

# Uninstall Helm releases
helm uninstall taskwave-frontend
helm uninstall taskwave-backend

# Stop Minikube
minikube stop

# Delete Minikube cluster
minikube delete
```

---

## Verification Checklist

- [ ] Docker images build successfully (< 500MB each)
- [ ] Docker Compose starts both services
- [ ] Frontend accessible at localhost:3000
- [ ] Backend health check passes at localhost:8000/health
- [ ] Auth features work (login, signup, Google OAuth)
- [ ] Task CRUD operations work
- [ ] Chat with AI works (MCP tools functional)
- [ ] Minikube cluster starts
- [ ] Helm charts install without errors
- [ ] All pods in Running state
- [ ] Application accessible via Minikube service URL
- [ ] All features work in K8s environment

---

## Next Steps

After successful local deployment:
1. Document any issues and solutions
2. Optimize resource limits based on actual usage
3. Prepare for Phase 5: Cloud Kubernetes deployment
