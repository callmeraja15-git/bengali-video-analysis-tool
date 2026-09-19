@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

echo ================================================
echo Running Video Screen Capture
 echo ================================================
echo.
echo This records the visible Windows desktop for a custom duration.
echo Keep the running video visible during recording.
echo.

where ffmpeg >nul 2>nul
if errorlevel 1 (
  echo ERROR: FFmpeg is not installed or is not on PATH.
  echo Run start_app.bat first, or install FFmpeg from https://ffmpeg.org/
  pause
  exit /b 1
)

set /p "DURATION_MIN=Capture duration in minutes (example 15): "
set /p "OUTPUT_NAME=Output name without extension (example running_video): "
if "%OUTPUT_NAME%"=="" set "OUTPUT_NAME=running_video"

for /f %%D in ('powershell -NoProfile -Command "try {[int]([double]('%DURATION_MIN%')*60)} catch {0}"') do set "DURATION_SECONDS=%%D"
if not defined DURATION_SECONDS set "DURATION_SECONDS=0"
if "%DURATION_SECONDS%"=="0" (
  echo ERROR: Enter a valid duration greater than zero.
  pause
  exit /b 1
)

if not exist recordings mkdir recordings
set "OUTPUT_FILE=recordings\%OUTPUT_NAME%.mp4"

echo.
echo Choose audio mode:
echo 1. Record screen only (no audio; transcription will not work)
echo 2. Record screen and select a Windows audio device
set /p "AUDIO_MODE=Enter 1 or 2: "

if "%AUDIO_MODE%"=="2" goto audio
if not "%AUDIO_MODE%"=="1" (
  echo ERROR: Choose 1 or 2.
  pause
  exit /b 1
)

echo.
echo Starting screen-only recording for %DURATION_MIN% minute(s)...
echo Keep the video visible. Press Ctrl+C to stop early.
ffmpeg -y -f gdigrab -framerate 30 -draw_mouse 1 -i desktop -t "%DURATION_SECONDS%" -c:v libx264 -preset ultrafast -pix_fmt yuv420p "%OUTPUT_FILE%"
goto finish

:audio

echo.
echo Available Windows DirectShow devices:
ffmpeg -list_devices true -f dshow -i dummy 2>&1 | findstr /i "audio"
echo.
set /p "AUDIO_DEVICE=Enter the exact audio device name between quotes, or type NONE: "
if /i "%AUDIO_DEVICE%"=="NONE" goto screenonly

echo Starting screen plus audio recording for %DURATION_MIN% minute(s)...
ffmpeg -y -f gdigrab -framerate 30 -draw_mouse 1 -i desktop -f dshow -i audio="%AUDIO_DEVICE%" -t "%DURATION_SECONDS%" -c:v libx264 -preset ultrafast -pix_fmt yuv420p -c:a aac -b:a 128k -shortest "%OUTPUT_FILE%"
goto finish

:screenonly
ffmpeg -y -f gdigrab -framerate 30 -draw_mouse 1 -i desktop -t "%DURATION_SECONDS%" -c:v libx264 -preset ultrafast -pix_fmt yuv420p "%OUTPUT_FILE%"

:finish
if errorlevel 1 (
  echo.
  echo Recording failed. Check the FFmpeg/audio-device message above.
  pause
  exit /b 1
)
echo.
echo Recording saved to: %CD%\%OUTPUT_FILE%
echo.
echo To analyze it, run start_app.bat and choose this file, or use:
echo py video_analysis.py --video "%OUTPUT_FILE%" --output "results\%OUTPUT_NAME%_report.json" --model small --language bn
pause
