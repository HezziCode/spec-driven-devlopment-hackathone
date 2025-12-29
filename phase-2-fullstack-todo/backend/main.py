from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
from routes import tasks, auth, users
import os
import logging
from dotenv import load_dotenv
from middleware.auth_middleware import verify_jwt_middleware

# Load environment variables
load_dotenv()

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Phase II Todo API",
    description="Full-stack todo application backend with user authentication, task management, and advanced filtering",
    version="1.0.0",
    contact={
        "name": "Phase II Todo Team",
        "email": "support@phase2todo.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# Add CORS middleware (must be before other middleware)
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "http://localhost:3000"],  # Development and production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "An unexpected error occurred",
            "code": "INTERNAL_ERROR",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Add JWT authentication middleware
# This middleware will run on all requests and validate JWT tokens
# Public routes (/auth/*, /docs, /redoc, /openapi.json, /health, /) bypass authentication
@app.middleware("http")
async def authentication_middleware(request: Request, call_next):
    """
    JWT authentication middleware wrapper.

    Validates JWT tokens on protected endpoints and attaches user context
    to request.state for use in route handlers.
    """
    return await verify_jwt_middleware(request, call_next)

# Include routes (after middleware registration)
# Authentication routes - publicly accessible (signup, login, logout)
app.include_router(auth.router)

# Task management routes - require JWT authentication
app.include_router(tasks.router)

# User profile routes - require JWT authentication
app.include_router(users.router)

@app.on_event("startup")
async def startup_event():
    """Verify database connection and log configuration on startup."""
    logger.info("Starting Phase II Todo API...")
    logger.info(f"Log level: {log_level}")
    logger.info(f"Frontend URL: {frontend_url}")

    # Verify database connection
    try:
        from db import engine
        with engine.connect() as connection:
            logger.info("Database connection successful")
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise

    logger.info("Application startup complete")


@app.get("/")
def read_root():
    """Root endpoint - publicly accessible."""
    return {
        "message": "Phase II Todo Backend API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint - publicly accessible."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }