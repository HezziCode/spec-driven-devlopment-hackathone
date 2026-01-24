# TaskWave - Full Stack Todo Application

TaskWave is a full-stack todo web application built with FastAPI (backend), Next.js (frontend), and PostgreSQL (database). The application features user authentication, task management with priorities and tags, and a modern responsive UI.

## Features

- **User Authentication**: Secure authentication using Better Auth with JWT tokens
- **Task Management**: Create, read, update, delete tasks with priorities and tags
- **Advanced Filtering**: Filter tasks by status, priority, tags, and search
- **Responsive UI**: Modern interface built with Next.js and Tailwind CSS
- **Containerized**: Ready for Docker and Kubernetes deployment

## Development Setup

### Prerequisites

(Previous Docker instructions remain the same)

## Running the Project with Docker

This project provides a full-stack environment with a FastAPI backend, a Next.js frontend, and a PostgreSQL database, all orchestrated via Docker Compose.

### Project-Specific Requirements

- **Backend**: Python 3.11 (as specified in the Dockerfile)
- **Frontend**: Node.js v22.13.1 (as specified in the Dockerfile)
- **Database**: PostgreSQL (official image, latest)

### Required Environment Variables

- **Backend**: Place a `.env` file in `./backend/` for backend-specific environment variables (see `backend/.env.example` for guidance if available).
- **Frontend**: Place a `.env` file in `./frontend/` for frontend-specific environment variables.
- **Database**: The following variables are set in `docker-compose.yml` for the PostgreSQL service:
  - `POSTGRES_USER=user`
  - `POSTGRES_PASSWORD=password`
  - `POSTGRES_DB=database`

### Ports Exposed

- **Backend (FastAPI)**: [http://localhost:8000](http://localhost:8000)
- **Frontend (Next.js)**: [http://localhost:3000](http://localhost:3000)
- **Database (PostgreSQL)**: [localhost:5432](localhost:5432)

### Build and Run Instructions

1. **Ensure Docker and Docker Compose are installed.**
2. **Prepare environment files:**
   - Copy or create `.env` files in both `./backend/` and `./frontend/` as needed.
3. **From the project root, run:**
   ```sh
   docker compose up --build
   ```
   This will build and start all services (backend, frontend, and database).

### Special Configuration Notes

- The backend and frontend Dockerfiles create a non-root `appuser` for improved security.
- The backend uses a Python virtual environment (`.venv`) for dependencies, installed during the build.
- The frontend uses `npm ci` for deterministic dependency installation and builds the Next.js app before starting.
- The PostgreSQL data is persisted in a Docker volume (`postgres-data`).
- The backend service depends on the database, and the frontend depends on the backend; Docker Compose manages startup order.
- If you need to customize database credentials, update the `environment` section for `postgres-db` in `docker-compose.yml` and ensure your backend `.env` matches.

## Kubernetes Deployment (Minikube)

The project includes Helm charts for Kubernetes deployment to Minikube clusters.

### Prerequisites

- **Minikube**: Local Kubernetes cluster
- **kubectl**: Kubernetes command-line tool
- **Helm**: Kubernetes package manager

### Deploy to Minikube

1. **Start Minikube cluster:**
   ```sh
   minikube start
   ```

2. **Enable Minikube addons:**
   ```sh
   minikube addons enable ingress
   minikube addons enable metrics-server
   ```

3. **Build Docker images with Minikube Docker daemon:**
   ```sh
   eval $(minikube docker-env)
   docker build -f backend/Dockerfile -t taskwave-backend:latest ./backend
   docker build -f frontend/Dockerfile -t taskwave-frontend:latest ./frontend
   ```

4. **Deploy Helm charts:**
   ```sh
   # Deploy backend
   helm install taskwave-backend ./infrastructure/helm/taskwave-backend/

   # Deploy frontend
   helm install taskwave-frontend ./infrastructure/helm/taskwave-frontend/
   ```

5. **Access the application:**
   ```sh
   # Get frontend service URL
   minikube service taskwave-frontend --url
   ```

### Helm Chart Configuration

Both Helm charts support custom configuration through `values.yaml`:

- **Replica count**: Number of pod replicas
- **Resource limits**: CPU and memory resources
- **Environment variables**: Configured via ConfigMaps and Secrets
- **Service type**: ClusterIP, NodePort, or LoadBalancer
- **Probe configuration**: Liveness and readiness probe settings

### Cleanup

To remove the deployment:
```sh
helm uninstall taskwave-frontend
helm uninstall taskwave-backend
minikube stop
```

## Project Structure

```
.
├── backend/              # FastAPI backend
├── frontend/            # Next.js frontend
├── infrastructure/      # Deployment configurations
│   ├── helm/           # Helm charts
│   └── k8s/            # Kubernetes manifests
├── specs/              # Project specifications
├── history/            # ADRs and PHRs
└── docker-compose.yml  # Docker Compose configuration
```

## API Documentation

The backend API follows RESTful principles with JWT authentication. See `specs/api/rest-endpoints.md` for detailed API documentation.

## Security

- All API endpoints require JWT authentication
- User data isolation with user_id validation
- Environment variable-based configuration
- Non-root container users
- Health probes for Kubernetes

## Development

### Backend Setup
```sh
cd backend
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
uv run uvicorn main:app --reload
```

### Frontend Setup
```sh
cd frontend
npm install
npm run dev
```

## Troubleshooting

- **Port conflicts**: Ensure ports 3000 and 8000 are not in use
- **Database connection**: Check PostgreSQL service is running
- **Environment variables**: Verify `.env` files are properly configured
- **Docker builds**: Clear Docker cache with `--no-cache` flag if needed
- **Minikube issues**: Restart Minikube with `minikube delete && minikube start`

---

_If you encounter issues, check that your `.env` files are present and correctly configured for both backend and frontend._
