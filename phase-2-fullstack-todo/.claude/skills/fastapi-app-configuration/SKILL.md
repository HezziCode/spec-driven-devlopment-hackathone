---
name: fastapi-app-configuration
description: Configure FastAPI application with routes, middleware, CORS, logging, and error handling. Use when setting up main application entry points, integrating components, or configuring production-ready FastAPI apps.
---

# FastAPI App Configuration

## Purpose

Configure FastAPI application with routes, middleware, CORS, logging, and error handling.

## Context

Used for main application setup and integration of all components.

## Pattern

```python
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
import os

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Create app
app = FastAPI(
    title="Phase II Todo API",
    description="RESTful API for multi-user task management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "code": "INTERNAL_ERROR",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Register routes
app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(users_router)

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# Root
@app.get("/")
async def root():
    return {
        "message": "Phase II Todo Backend API",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Startup event
@app.on_event("startup")
async def startup():
    logger.info("Starting Phase II Todo API")
    try:
        # Test database connection
        logger.info("Database connection verified")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise