from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from routes import tasks
from routes import auth
import os
from dotenv import load_dotenv
from middleware.auth_middleware import verify_jwt_middleware

# Load environment variables
load_dotenv()

app = FastAPI(title="Phase 2 Todo API", version="1.0.0")

# Add CORS middleware (must be before other middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

@app.get("/")
def read_root():
    """Root endpoint - publicly accessible."""
    return {"message": "Welcome to the Phase 2 Todo API"}

@app.get("/health")
def health_check():
    """Health check endpoint - publicly accessible."""
    return {"status": "healthy"}