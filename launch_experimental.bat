@echo off
title LOKI Interceptor EXPERIMENTAL - Starting
color 0E

echo.
echo  ==========================================
echo   LOKI INTERCEPTOR EXPERIMENTAL V2
echo   Port 5002 (Demo on 5001)
echo  ==========================================
echo.
echo [DEBUG] Current directory: %CD%
echo.

:: Start backend
echo [1/2] Starting backend server on port 5002...
echo [DEBUG] Checking if backend folder exists...
if not exist "backend" (
    echo [ERROR] backend folder not found!
    pause
    exit /b 1
)
cd backend
echo [DEBUG] Changed to: %CD%
echo [DEBUG] Starting Python server...
start "LOKI Backend" cmd /c "python server.py & pause"
timeout /t 2 /nobreak >nul
cd ..
echo [DEBUG] Backend started, waiting 5 seconds...

:: Wait for backend
timeout /t 5 /nobreak >nul

:: Display info
cls
echo.
echo  ==========================================
echo   LOKI EXPERIMENTAL - READY
echo  ==========================================
echo.
echo  Backend running on: http://localhost:5002
echo.
echo  Press Ctrl+C to stop all services
echo.

:: Launch Electron
echo [2/2] Launching LOKI EXPERIMENTAL app...
echo [DEBUG] Checking if electron folder exists...
if not exist "electron" (
    echo [ERROR] electron folder not found!
    pause
    exit /b 1
)
cd electron
echo [DEBUG] Changed to: %CD%
echo [DEBUG] Launching Electron directly...
call npx electron .
if errorlevel 1 (
    echo [ERROR] Electron launch failed
    cd ..
    pause
    exit /b 1
)

:: Cleanup
echo [DEBUG] Cleaning up processes...
taskkill /F /IM python.exe >nul 2>&1
