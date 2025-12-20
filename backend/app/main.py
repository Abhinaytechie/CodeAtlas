import sys
import os

# Force current directory to be first in sys.path to avoid importing 'app' from other projects
sys.path.insert(0, os.getcwd())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_router
# from app.core.database import engine, Base

# Create tables
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for the AI-Powered DSA Preparation Platform",
    version="1.0.0",
)

@app.on_event("startup")
async def startup_db_client():
    try:
        from app.core.database import client
        client.admin.command('ping')
        print("INFO:     ✅ MongoDB Connected Successfully!")
    except Exception as e:
        print(f"ERROR:    ❌ MongoDB Connection Failed: {e}")

# CORS Configuration
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://localhost:3000",
    "http://localhost:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Welcome to the DSA Platform API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
