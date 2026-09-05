@echo off
echo =====================================================================
echo 🎓 Launching SIH 2026 Unified Hybrid Adaptive Learning OS Prototype
echo Team Tech_Warriors | StudyCopilot & StudyForge Integration
echo =====================================================================
echo.

:: Launch Backend in separate window
echo Starting FastAPI Backend Service on http://localhost:8000...
start "SIH FastAPI Backend" cmd /k "cd backend && run_backend.bat"

:: Wait 2 seconds for backend initialization
timeout /t 2 /nobreak > nul

:: Launch Frontend in separate window
echo Starting Vite React Frontend Service on http://localhost:5173...
start "SIH React Frontend" cmd /k "cd frontend && run_frontend.bat"

echo.
echo =====================================================================
echo 🚀 Startup scripts executed! 
echo Frontend UI: http://localhost:5173
echo Backend API: http://localhost:8000/docs
echo =====================================================================
