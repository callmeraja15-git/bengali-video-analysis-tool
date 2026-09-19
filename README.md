# Bengali Video Clip Analyzer

A Windows starter app for selecting a saved video, entering a timestamp and duration, creating an MP4 clip, transcribing Bengali/English speech, and generating JSON + HTML reports.

## Quick start
1. Install Python 3.10+ from https://www.python.org/downloads/.
2. Install FFmpeg and add it to PATH. `start_app.bat` attempts installation with `winget` when available.
3. Double-click `start_app.bat`.
4. Choose the video, timestamp, duration in minutes, language, and model.
5. Click **Create clip and analyze**.

Outputs are written to `clips` and `results`.

The first run downloads the selected Whisper model. `tiny` is fastest; `small` is a useful test default.

This tool reports observable measurements only: transcript, speaking rate, pauses, face-detection visibility, and brightness. It does not determine truthfulness, mental health, personality, intent, or diagnosis.

To create a ZIP beside the project folder, double-click `make_zip.bat`.
