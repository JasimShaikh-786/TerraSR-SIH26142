@echo off
taskkill /FI "WINDOWTITLE eq SIH26142 Backend" /T /F >nul 2>nul
taskkill /FI "WINDOWTITLE eq SIH26142 Frontend" /T /F >nul 2>nul
echo Prototype services stopped.
