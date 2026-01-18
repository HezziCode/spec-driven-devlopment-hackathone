# Quickstart: Phase 4 Local Kubernetes Deployment

## Prerequisites
1. Docker Desktop running with WSL2 integration enabled.
2. Gordon (Docker AI) toggled ON in Beta Settings.
3. Minikube installed and started: `minikube start --driver=docker`.
4. `kubectl-ai` installed via Krew.

## AI Command Sequence

### Step 1: Containerize
```bash
docker ai "Create a multi-stage Dockerfile for my Next.js App in ./frontend"
docker ai "Create a multi-stage Dockerfile for my FastAPI App in ./backend"
```

### Step 2: Build & Push (Local)
```bash
eval $(minikube docker-env)
docker build -t taskwave-frontend:latest -f infrastructure/docker/frontend.Dockerfile .
docker build -t taskwave-backend:latest -f infrastructure/docker/backend.Dockerfile .
```

### Step 3: Deploy via AI
```bash
kubectl-ai "create a kubernetes secret for DATABASE_URL and BETTER_AUTH_SECRET"
kubectl-ai "deploy frontend and backend images using helm patterns"
```

### Step 4: Verify
```bash
kagent "check if all taskwave pods are healthy"
minikube service taskwave-frontend
```
