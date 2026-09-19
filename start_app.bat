@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul || (echo Install Python 3.10+ from https://www.python.org/downloads/ and enable Add Python to PATH.&pause&exit /b 1)
where ffmpeg >nul 2>nul
if errorlevel 1 (
  echo FFmpeg is missing. Attempting installation with winget...
  where winget >nul 2>nul && winget install --id Gyan.FFmpeg.Shared --exact --source winget
  where ffmpeg >nul 2>nul || (echo Install FFmpeg from https://ffmpeg.org/download.html and add it to PATH.&pause&exit /b 1)
)
py -m pip install -r requirements.txt
py app.py
