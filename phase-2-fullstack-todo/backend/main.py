from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import tasks
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Phase 2 Todo API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(tasks.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Phase 2 Todo API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}