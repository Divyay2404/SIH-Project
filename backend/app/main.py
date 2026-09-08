"""
SIH 2026 FastAPI Application Entry Point.
Team Tech_Warriors - StudyCopilot & StudyForge Integration.
"""

import os
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.schemas.api_schemas import RootHealthResponse, HealthCheckResponse

# Allowed CORS origins - Explicitly allow React/Vite development server
ALLOWED_ORIGINS: List[str] = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# Allow additional origins from environment variable if provided
env_origins = os.getenv("CORS_ORIGINS")
if env_origins:
    ALLOWED_ORIGINS.extend([origin.strip() for origin in env_origins.split(",") if origin.strip()])

app = FastAPI(
    title="StudyCopilot & StudyForge Unified Learning OS API",
    description="Backend services powering coordinate-grounded RAG, marks-aware Q&A, diagnostic error taxonomy, and PPT/PDF generator engines.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware to allow React Frontend connectivity
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Asynchronous Router Mounting
app.include_router(router)


@app.get(
    "/",
    response_model=RootHealthResponse,
    summary="Gateway Root Information",
    tags=["Health"]
)
async def root() -> RootHealthResponse:
    """Root entry point providing discovery URLs and engine information."""
    return RootHealthResponse(
        message="Welcome to SIH 2026 StudyCopilot & StudyForge Core Gateway API",
        docs_url="/docs",
        health_check="/api/health"
    )


@app.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Gateway Root Health Check",
    tags=["Health"]
)
async def root_health_check() -> HealthCheckResponse:
    """Direct root health check endpoint."""
    return HealthCheckResponse(
        status="online",
        system="StudyCopilot & StudyForge Engine",
        version="1.0.0"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
