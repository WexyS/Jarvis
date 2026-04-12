@echo off
title J.A.R.V.I.S v2.0 — Web GUI Launcher
color 0B
echo.
echo ============================================================
echo  J.A.R.V.I.S v2.0 — Web GUI (React + FastAPI)
echo  Backend: http://localhost:8000
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

:: ─────────────────────────────────────────────────────────────
:: HATA #1 DÜZELTİLDİ: --host 0.0.0.0 → 127.0.0.1
::   Eski: --host 0.0.0.0  (tüm ağa açık, güvenlik açığı)
::   Yeni: --host 127.0.0.1 (sadece yerel makine)
:: HATA #2 DÜZELTİLDİ: Eksik kapanış tırnağı eklendi
::   Eski: ...--port 8000      ← tırnak yok, backend başlamaz
::   Yeni: ...--port 8000"     ← kapanış tırnağı var
:: ─────────────────────────────────────────────────────────────
echo [2/4] Starting FastAPI Backend (port 8000)...
start "Jarvis Backend" cmd /k "cd /d %~dp0 && call .venv\Scripts\activate.bat && python -m uvicorn jarvis.api.main:app --host 127.0.0.1 --port 8000"

:: ─────────────────────────────────────────────────────────────
:: HATA #3 DÜZELTİLDİ: Race condition — kör timeout → health check
::   Eski: timeout /t 5  (backend hazır olmasa da 5sn sonra devam)
::   Yeni: /health endpoint hazır olana kadar döngüyle bekle
::         max 30 deneme × 2sn = 60sn zaman aşımı
:: ─────────────────────────────────────────────────────────────
echo [3/4] Waiting for backend to be ready...
set RETRY=0
:WAIT_LOOP
    timeout /t 2 /nobreak >nul
    curl -s http://127.0.0.1:8000/health >nul 2>&1
    if %errorlevel% == 0 goto BACKEND_READY
    set /a RETRY+=1
    if %RETRY% geq 30 (
        echo [-] Backend did not start within 60 seconds. Check the Jarvis Backend window for errors.
        pause
        exit /b 1
    )
    echo     Still waiting... (%RETRY%/30)
    goto WAIT_LOOP

:BACKEND_READY
echo     Backend is ready.
echo.

:: Start Frontend
echo [4/4] Starting React Frontend (port 5173)...
echo.
cd /d "%~dp0jarvis-desktop"
call npm run dev

:: This line only executes if frontend stops
echo.
echo [-] Frontend stopped.
pause
