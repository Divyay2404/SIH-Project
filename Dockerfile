# =============================================================================
# Production Dockerfile for StudyForge / SIH-Project FastAPI Backend
# Includes PyMuPDF, ReportLab, python-pptx, and native Tesseract OCR runtime
# =============================================================================

FROM python:3.11-slim

# Prevent Python from buffering stdout/stderr and writing .pyc files
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

# Install core runtime dependencies, Tesseract OCR engine, English language data, and graphic libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1 \
    libglib2.0-0 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# Copy entire backend source code
COPY backend /app/backend

# Configure Python path so `import app` resolves backend/app directly
ENV PYTHONPATH=/app/backend:/app
ENV PORT=8000
ENV ENVIRONMENT=production

# Verify tessdata discovery directory
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

# Expose standard container port
EXPOSE 8000

# Container Healthcheck Probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/api/health || exit 1

# Production startup command matching acceptance criteria
WORKDIR /app/backend
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
