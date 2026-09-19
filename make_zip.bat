@echo off
setlocal
cd /d "%~dp0"
where powershell >nul 2>nul || (echo PowerShell is required.&pause&exit /b 1)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0package_project.ps1"
pause
