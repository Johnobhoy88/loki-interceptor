@echo off
title LOKI Interceptor EXPERIMENTAL - Cloudflare Tunnel
color 0E

echo.
echo  ==========================================
echo   LOKI EXPERIMENTAL V2 - CLOUDFLARE MODE
echo   Port 5002 ^+ Public Tunnel
echo  ==========================================
echo.

:: Check for cloudflared.exe
if not exist "cloudflared.exe" (
    echo [ERROR] cloudflared.exe not found in project directory
    echo.
    echo Please download cloudflared.exe and place it in:
    echo %CD%
    echo.
    echo Download from: https://github.com/cloudflare/cloudflared/releases
    echo Look for: cloudflared-windows-amd64.exe
    echo Rename it to: cloudflared.exe
    echo.
    pause
    exit /b 1
)

:: Start backend
echo [1/3] Starting backend server on port 5002...
cd backend
start "LOKI Backend" cmd /c "python server.py & pause"
cd ..
timeout /t 5 /nobreak >nul

:: Start Cloudflare tunnel
echo [2/3] Starting Cloudflare tunnel...
echo.
echo IMPORTANT: Cloudflare will generate a unique URL
echo Copy the URL that appears (ends with .trycloudflare.com)
echo.
start "Cloudflare Tunnel" cmd /k "%CD%\cloudflared.exe tunnel --url http://localhost:5002"
timeout /t 10 /nobreak >nul

:: Display instructions
cls
echo.
echo  ==========================================
echo   LOKI EXPERIMENTAL - CLOUDFLARE READY
echo  ==========================================
echo.
echo  Local:     http://localhost:5002
echo  Public:    [Check Cloudflare window for URL]
echo.
echo  The Cloudflare tunnel window will show your public URL
echo  Example: https://xxxxx-xx-xxx-xxx-xx.trycloudflare.com
echo.
echo  Copy that URL and share it for remote access
echo.
echo  Press any key to launch Electron app...
pause >nul

:: Launch Electron
echo [3/3] Launching Electron app...
cd electron
call npx electron .
cd ..

:: Cleanup
echo.
echo Shutting down services...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq LOKI Backend*" >nul 2>&1
taskkill /F /IM cloudflared.exe >nul 2>&1
echo.
echo All services stopped.
pause
