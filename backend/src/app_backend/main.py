"""
FastAPI Application
Entry point aplikasi FastAPI
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

import app_backend.models  # noqa: F401 – registrasi semua tabel ke metadata
from app_backend.models.base import Base
from app_backend.routers.api import admin, application, auth, profile, vacancy, placement
from app_backend.shared.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    import os
    # Buat semua tabel saat server start; dilewati ketika TESTING=1
    if not os.environ.get("TESTING"):
        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="IPB Internship and Career Tracker API",
    description="IPB Internship and Career Tracker API | V1.0.0",
    version="1.0.0",
    lifespan=lifespan,
)

# Konfigurasi CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(admin.router)
app.include_router(vacancy.router)
app.include_router(application.router)
app.include_router(placement.router)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "message": "IPB Internship and Career Tracker API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
