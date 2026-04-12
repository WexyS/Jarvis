@echo off
title J.A.R.V.I.S v2.0 — Web GUI Launcher
color 0B
echo.
echo ============================================================
echo  J.A.R.V.I.S v2.0 — Web GUI (React + FastAPI)
echo  Backend:  http://localhost:8000
echo  Frontend: http://localhost:5173
echo ============================================================
echo.

:: Set working directory to script location
cd /d "%~dp0"

:: Activate virtual environment
if exist "%~dp0.venv\Scripts\activate.bat" (
    call "%~dp0.venv\Scripts\activate.bat"
    echo [1/4] Virtual environment activated.
) else (
    echo [-] Virtual environment not found: .venv
    pause
    exit /b 1
)

:: Start Backend (in background, but output visible)
echo [2/4] Starting FastAPI Backend (port 8000)...
start "Jarvis Backend" cmd /k "cd /d %~dp0 && python -m uvicorn jarvis.api.main:app --host 0.0.0.0 --port 8000
timeout /t 5 /nobreak >nul
echo      Backend is starting...

:: Start Frontend (in foreground — output visible in VSCode)
echo [3/4] Starting React Frontend (port 5173)...
echo.
cd /d "%~dp0jarvis-desktop"
call npm run dev

:: This line only executes if frontend stops
echo.
echo [-] Frontend stopped.
pause
