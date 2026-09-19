# Quick start

Double-click `start_app.bat`. It checks Python and FFmpeg, installs Python dependencies, and opens a Windows GUI. Select a saved video, timestamp, duration in minutes, language, and Whisper model. Click **Create clip and analyze**.

The app creates an MP4 in `clips` and JSON and HTML reports in `results`. The first run downloads the selected Whisper model.

Double-click `make_zip.bat` to create a ZIP beside the project directory. Generated clips, reports, caches, and Git metadata are excluded.

Supported transcription choices: Bengali (`bn`), English (`en`), or auto detect.
