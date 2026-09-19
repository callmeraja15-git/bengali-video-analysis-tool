@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul || (echo Python 3.10+ is required.&pause&exit /b 1)
py -m pip install -r requirements.txt
py screen_recorder.py
