# Proper window-only recording

This version does not record the whole desktop. It lists visible Windows and lets you select the running video window.

1. Open the video window first.
2. Double-click `run_recorder.bat`.
3. If the video window is not listed, click **Refresh**.
4. Select the video window.
5. Select the speaker/headphones output that plays the video sound.
6. Enter a duration in minutes, such as `15`.
7. Click **START RECORDING**.
8. Keep the selected video window visible and do not minimize it.
9. Click **STOP RECORDING**, or let the duration finish.

The final MP4 is saved in:

`Videos\\BengaliVideoCaptures`

The recorder captures the selected top-level video window through FFmpeg `gdigrab` and records system playback audio through Windows loopback (`soundcard`). It does not capture other desktop windows, the taskbar, or notifications.

If FFmpeg is installed in a different location, edit `FFMPEG` near the top of `screen_recorder.py`.
