"""
SIH 2026 FastAPI Application Entry Point.
Team Tech_Warriors - StudyCopilot & StudyForge Integration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

app = FastAPI(
    title="StudyCopilot & StudyForge Unified Learning OS API",
    description="Backend services powering coordinate-grounded RAG, marks-aware Q&A, diagnostic error taxonomy, and PPT/PDF generator engines.",
    version="1.0.0"
)

# CORS Middleware to allow React Frontend connectivity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local hackathon testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Router
app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "Welcome to SIH 2026 StudyCopilot & StudyForge Core Gateway API",
        "docs_url": "/docs",
        "health_check": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
