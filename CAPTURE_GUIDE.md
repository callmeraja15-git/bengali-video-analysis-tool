# How to capture a running video

The capture tool is `capture_running_video.bat`.

1. Download the repository ZIP and extract it.
2. Install Python and FFmpeg. Run `start_app.bat` if needed.
3. Open the running video and keep it visible on the desktop.
4. Double-click `capture_running_video.bat`.
5. Enter `15` for a 15-minute recording, or any other duration in minutes.
6. Enter an output name, such as `running_video`.
7. Choose audio mode 2 if the video has speech. Select an exact Windows audio device when prompted.
8. The recording is saved under `recordings`.
9. Open `start_app.bat`, select the saved recording, choose Bengali, and click **Create clip and analyze**.

Audio is required for transcription. If no suitable Windows audio device appears, use OBS Studio with Display Capture and Desktop Audio, then analyze the resulting MP4.

The script captures the visible desktop, so do not show private windows or notifications. It does not capture a video that is still being downloaded as a file; it records what is visible on screen.
