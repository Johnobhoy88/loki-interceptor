@echo off
title LOKI EXPERIMENTAL - Port 5002
color 0E

echo.
echo  ==========================================
echo   LOKI INTERCEPTOR - EXPERIMENTAL
echo   Port 5002 (Demo on 5001)
echo  ==========================================
echo.

cd backend
echo Starting experimental backend on port 5002...
python server.py

pause
