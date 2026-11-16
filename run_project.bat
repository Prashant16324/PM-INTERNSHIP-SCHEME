@echo off
TITLE AI-Based Smart Allocation Engine - Launcher
echo =====================================================================
echo   AI-Based Smart Allocation Engine for PM Internship Scheme
echo   Academic Prototype Launcher (Windows 11)
echo =====================================================================
echo.

cd /d "%~dp0"
powershell.exe -ExecutionPolicy Bypass -File "%~dp0run_project.ps1"

pause
