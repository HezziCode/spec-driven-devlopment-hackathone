# Phase 2: Full-Stack Todo Web Application

> **Evolution from Phase 1** - Transforming console app into a production web application

**Live Demo (Azure Cloud):** [chat-task.site](https://chat-task.site)
**Live Demo (Vercel):** [secure-todoz.vercel.app](https://secure-todoz.vercel.app)

**🔗 See all phases:** [Main Project README](../giaic-hackathone/README.md)

---

## 🎯 Phase 2 Overview

This phase transforms the Phase 1 console application into a full-stack web application with:
- Multi-user authentication system
- Persistent database storage (PostgreSQL)
- RESTful API backend
- Modern responsive web UI
- Production deployment capabilities

### Evolution from Phase 1
- ❌ In-memory storage → ✅ PostgreSQL database
- ❌ Single user → ✅ Multi-user with authentication
- ❌ Console interface → ✅ Modern web UI
- ❌ Local only → ✅ Cloud-deployed

---

## ✨ Key Features

### Authentication & Security
- 🔐 JWT-based authentication
- 🔑 Email/password signup and login
- 🌐 Google OAuth integration
- 🛡️ Rate limiting (abuse protection)
- 👤 User data isolation

### Task Management
- ✅ Full CRUD operations (Create, Read, Update, Delete)
- 🎯 Task priorities (low, medium, high, critical)
- 🏷️ Tags and categories
- 🔍 Advanced search and filtering
- 📊 Sort by date, priority, or status
- ✏️ Rich task descriptions

### User Experience
- 🎨 Modern, responsive UI with Tailwind CSS
- 🌙 Dark mode optimized
- 📱 Mobile-friendly design
- ⚡ Real-time updates
- 🔔 User-friendly error messages (English + Urdu)
- 🚫 Duplicate action prevention

---

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Auth**: Better Auth with JWT plugin
- **State**: React hooks

### Backend
- **Framework**: FastAPI
- **ORM**: SQLModel
- **Database**: PostgreSQL (Neon Serverless)
- **Auth**: JWT tokens + Google OAuth
- **Validation**: Pydantic

### DevOps
- **Containerization**: Docker
- **Orchestration**: Kubernetes
- **Cloud**: Azure AKS
- **Domain**: Namecheap (chat-task.site)
- **CDN**: Vercel (backup deployment)

---

## 📋 API Endpoints

### Authentication
```
POST   /auth/signup          - Register new user
POST   /auth/login           - Login with email/password
GET    /auth/google          - Initiate Google OAuth
GET    /auth/callback/google - Google OAuth callback
```

### Tasks
```
GET    /users/{user_id}/tasks              - List all tasks (with filters)
POST   /users/{user_id}/tasks              - Create new task
GET    /users/{user_id}/tasks/{task_id}    - Get specific task
PUT    /users/{user_id}/tasks/{task_id}    - Update task (full)
PATCH  /users/{user_id}/tasks/{task_id}    - Update task (partial)
DELETE /users/{user_id}/tasks/{task_id}    - Delete task
```

---

## 🚀 Quick Start

### Prerequisites
- Node.js 22+
- Python 3.11+
- PostgreSQL (or use Neon/Docker)
- Docker (optional)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/HezziCode/spec-driven-devlopment-hackathone.git
   cd giaic-hackathone/phase-2-fullstack-todo
   ```

2. **Backend Setup**
   ```bash
   cd backend

   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt

   # Create .env file with:
   # DATABASE_URL=postgresql://user:pass@host/db
   # BETTER_AUTH_SECRET=your-secret-key
   # GOOGLE_OAUTH_CLIENT_ID=your-client-id
   # GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret

   # Run server
   uvicorn main:app --reload
   ```

3. **Frontend Setup**
   ```bash
   cd frontend

   # Install dependencies
   npm install

   # Create .env.local with:
   # NEXT_PUBLIC_API_URL=http://localhost:8000
   # NEXT_PUBLIC_GOOGLE_OAUTH_CLIENT_ID=your-client-id
   # BETTER_AUTH_SECRET=your-secret-key
   # BETTER_AUTH_URL=http://localhost:8000

   # Run development server
   npm run dev
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

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

## 🔄 Project Evolution

**Phase 1 (Console App)** → **Phase 2 (You are here)** → Phase 3 (AI Chatbot) → Phase 4 (Kubernetes) → Phase 5 (Cloud Production)

### What's Next?
- **Phase 3**: AI-powered chatbot with MCP server integration
- **Phase 4**: Container orchestration and local Kubernetes deployment
- **Phase 5**: Production cloud deployment on Azure AKS

---

## 📄 License

MIT License - Open source and free to use.

---

## 👨‍💻 Developer

**Huzaifa**
- GitHub: [@HezziCode](https://github.com/HezziCode)
- Project: [GIAIC Hackathon - Spec-Driven Development](https://github.com/HezziCode/spec-driven-devlopment-hackathone)

---

**⭐ Star the repo if you find it helpful!**
