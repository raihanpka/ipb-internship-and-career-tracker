"""
FastAPI Application
Entry point aplikasi FastAPI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app_backend.shared.database import engine, Base
from app_backend.routers.api import auth

# Buat semua tabel database
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="IPB Internship and Career Tracker API",
    description="API untuk tracking magang dan karir mahasiswa IPB",
    version="1.0.0"
)

# Konfigurasi CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Selamat datang di IPB Internship and Career Tracker API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
