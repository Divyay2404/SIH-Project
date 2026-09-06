"""Vercel serverless entry point for the StudyForge FastAPI application."""

import sys
from pathlib import Path

BACKEND_DIRECTORY = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIRECTORY))

from app.main import app
