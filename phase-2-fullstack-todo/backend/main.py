import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

# Load environment variables FIRST before any other imports that might need them
load_dotenv()

# Configure agents library at module level before other imports
import openai
from openai import AsyncOpenAI  # Use AsyncOpenAI for agents library

# Get and validate API key FIRST
# Note: WSL2 may mask environment variables, so we read directly from .env file if masked
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key and len(openai_api_key) < 50:  # Masked keys are much shorter
    # Read directly from .env file to bypass WSL2 masking
    try:
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        with open(env_path, "r") as f:
            for line in f:
                if line.startswith("OPENAI_API_KEY="):
                    openai_api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    logging.info(
                        "Loaded API key directly from .env file (bypassed masking)"
                    )
                    break
    except Exception as e:
        logging.error(f"Failed to read API key from .env file: {e}")
if not openai_api_key:
    logging.error("OPENAI_API_KEY environment variable is not set!")
    raise ValueError("OPENAI_API_KEY must be set in environment variables")

# Validate API key format
if not openai_api_key.startswith("sk-"):
    logging.error(
        f"Invalid API key format. Key should start with 'sk-' but got: {openai_api_key[:10]}..."
    )
    raise ValueError("Invalid OpenAI API key format")

logging.info(f"Loaded OpenAI API key: {openai_api_key[:8]}...{openai_api_key[-4:]}")

# Set environment variable (for any modules that read it directly)
os.environ["OPENAI_API_KEY"] = openai_api_key

# Configure the agents package with the API key using proper methods at module level
try:
    # Import the agents functions - only import what we need
    from agents import (
        set_default_openai_api,
        set_default_openai_client,
        set_default_openai_key,
        set_tracing_disabled,
    )

    # Set the API key for the standard OpenAI library
    openai.api_key = openai_api_key
    openai.default_headers = {"Authorization": f"Bearer {openai_api_key}"}

    # Disable tracing to avoid 401 errors with tracing
    set_tracing_disabled(True)

    # Set the default API to use chat_completions instead of the deprecated responses API
    set_default_openai_api("chat_completions")

    # Set default API key for agents
    set_default_openai_key(openai_api_key)

    # Create a proper OpenAI client for agents SDK
    client = AsyncOpenAI(api_key=openai_api_key)
    set_default_openai_client(client)

except ImportError as e:
    # If agents package functions are not available, just set the API key in environment
    if openai_api_key:
        os.environ["OPENAI_API_KEY"] = openai_api_key
        openai.api_key = openai_api_key
        logging.warning(
            f"Agents package not available, using basic OpenAI configuration: {e}"
        )
except Exception as e:
    logging.error(
        f"Failed to configure agents package with API key at module level: {e}"
    )
    if openai_api_key:
        os.environ["OPENAI_API_KEY"] = openai_api_key
        openai.api_key = openai_api_key

# Import MCP server tools to register them
import mcp_server.tools  # noqa: F401
from mcp_server.server import mcp
from middleware.auth_middleware import verify_jwt_middleware
from routes import auth, tasks, users
from services.chat_service import start_persistence_worker, stop_persistence_worker

# Load environment variables
load_dotenv()

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Combined lifespan for FastAPI and MCP server
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Combined lifespan handler for FastAPI application and MCP server.

    Handles startup and shutdown events for both the main FastAPI app
    and the mounted MCP server.
    """
    # Startup
    logger.info("Starting Phase II/III Todo API with MCP Server...")
    logger.info(f"Log level: {os.getenv('LOG_LEVEL', 'INFO')}")
    logger.info(f"Frontend URL: {os.getenv('FRONTEND_URL', 'http://localhost:3000')}")

    # Start persistence worker for chat messages
    await start_persistence_worker()

    # Verify database connection
    try:
        from db import engine

        with engine.connect() as connection:
            logger.info("Database connection successful")
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise

    logger.info("MCP Server mounted at /mcp endpoint")
    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down application...")
    stop_persistence_worker()


app = FastAPI(
    title="Phase II/III Todo API",
    description="Full-stack todo application backend with user authentication, task management, advanced filtering, and MCP server for AI agents",
    version="2.0.0",
    contact={"name": "Phase II/III Todo Team", "email": "support@phase2todo.com"},
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
    lifespan=lifespan,
)

# Add custom validation error handler for user-friendly messages
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom handler for validation errors (422).
    Returns user-friendly messages instead of technical Pydantic errors.
    """
    errors = exc.errors()

    # Build user-friendly error messages
    friendly_errors = []
    for error in errors:
        field = error.get("loc", [])[-1] if error.get("loc") else "field"
        error_type = error.get("type", "")

        # Map technical errors to friendly messages
        if "string_too_short" in error_type:
            min_length = error.get("ctx", {}).get("min_length", "required")
            friendly_errors.append(f"{field} must be at least {min_length} characters long")
        elif "value_error.email" in error_type or "string_pattern_mismatch" in error_type:
            friendly_errors.append(f"{field} must be a valid email address")
        elif "missing" in error_type:
            friendly_errors.append(f"{field} is required")
        else:
            msg = error.get("msg", "Invalid value")
            friendly_errors.append(f"{field}: {msg}")

    error_message = ". ".join(friendly_errors) + "."

    return JSONResponse(
        status_code=422,
        content={
            "error": error_message,
            "message": error_message,
            "code": "VALIDATION_ERROR",
            "details": errors  # Keep technical details for debugging
        }
    )

# Add ProxyHeadersMiddleware to trust X-Forwarded-Proto from nginx ingress
# This ensures request.url.scheme is 'https' when behind TLS-terminating proxy
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=["*"])

# Add CORS middleware (must be before other middleware)
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        frontend_url,
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://secure-todoz.vercel.app",
        "http://40.64.64.9",
        "http://chat-task.site",
        "http://www.chat-task.site",
        "https://chat-task.site",
        "https://www.chat-task.site",
    ],  # Development and production
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
            "timestamp": datetime.utcnow().isoformat(),
        },
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

# Chat routes - require JWT authentication for AI agent
from routes import chat

app.include_router(chat.router)

# Additional routes for proxy/load balancer support
# Mount auth routes with /api prefix to match Google Cloud Console configuration
# This will expose the same auth endpoints at both /auth/ and /api/auth/ paths
from fastapi import APIRouter

from routes.auth import router as auth_router

# Create a new router and include the auth routes with the /api prefix
api_router = APIRouter()
api_router.include_router(auth_router, prefix="/api")

# Mount the API-prefixed routes
app.include_router(api_router)

# Custom chat API routes without ChatKit dependencies
from routes import custom_chat

app.include_router(custom_chat.router)

# AI tools routes - direct HTTP endpoints for AI agents
from routes import ai_tools

app.include_router(ai_tools.router)

# Mount MCP server at /mcp endpoint
# This exposes todo management tools for AI agents
app.mount("/mcp", mcp.http_app())


@app.get("/")
def read_root():
    """Root endpoint - publicly accessible."""
    return {
        "message": "Phase II/III Todo Backend API",
        "version": "2.0.0",
        "docs": "/docs",
        "mcp_endpoint": "/mcp",
    }


@app.get("/health")
def health_check():
    """Health check endpoint - publicly accessible."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
