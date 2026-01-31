@echo off
REM CyberSentinel Service Startup Script for Windows (moved to scripts/)
setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════════════════════╗
echo ║           CYBERSENTIAL - SERVICE STARTUP SCRIPT                           ║
echo ╚════════════════════════════════════════════════════════════════════════════╝
echo.

echo Cleaning up ports...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000"') do taskkill /PID %%a /F 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8501"') do taskkill /PID %%a /F 2>nul
timeout /t 2 /nobreak > nul
echo Done.
echo.

echo Starting Backend API on port 8000...
start "CyberSentinel Backend" python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --log-level warning
timeout /t 3 /nobreak > nul
echo Backend started (check http://127.0.0.1:8000)
echo.

echo Starting Frontend Dashboard on port 8501...
start "CyberSentinel Frontend" streamlit run frontend/app.py --server.port 8501 --logger.level=error
timeout /t 5 /nobreak > nul
echo Frontend started (check http://localhost:8501)
echo.

echo ╔════════════════════════════════════════════════════════════════════════════╗
echo ║                    ✅ SERVICES STARTED SUCCESSFULLY                       ║
echo ╚════════════════════════════════════════════════════════════════════════════╝
echo.
echo 🔵 Backend API:      http://127.0.0.1:8000
echo 🎨 Frontend:         http://localhost:8501
echo 📚 API Docs:         http://127.0.0.1:8000/docs
echo.
echo ⚠️  Two new windows opened. Keep them open!
echo.
echo To stop services: Close both windows or press CTRL+C in each
echo To restart: Run this script again

echo.
pause