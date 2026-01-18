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

---

_If you encounter issues, check that your `.env` files are present and correctly configured for both backend and frontend._
