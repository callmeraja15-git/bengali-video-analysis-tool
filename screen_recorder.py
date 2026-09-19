import os
import subprocess
import threading
import time
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk

import soundcard as sc
import soundfile as sf
import win32gui

ROOT = Path(__file__).resolve().parent
FFMPEG = r"C:\MOVIES\ffmpeg-2026-08-27-git-a6f573a1db-essentials_build\bin\ffmpeg.exe"
OUTPUT_FOLDER = Path.home() / "Videos" / "BengaliVideoCaptures"
SAMPLE_RATE = 48000
CHANNELS = 2
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

recording = False
stop_event = threading.Event()
video_process = None
audio_thread = None
temp_video = None
temp_audio = None
final_output = None
record_started = 0.0


def visible_windows():
    result = []

    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd).strip():
            title = win32gui.GetWindowText(hwnd).strip()
            if title not in [item[1] for item in result]:
                result.append((hwnd, title))
        return True

    win32gui.EnumWindows(callback, None)
    return sorted(result, key=lambda item: item[1].lower())


def speakers():
    return sc.all_speakers()


def capture_audio(device_name, path):
    try:
        speaker = next((x for x in speakers() if x.name == device_name), None)
        if speaker is None:
            raise RuntimeError(f"Audio device not found: {device_name}")
        loopback = sc.get_microphone(speaker.name, include_loopback=True)
        frames = SAMPLE_RATE
        with sf.SoundFile(path, mode="w", samplerate=SAMPLE_RATE, channels=CHANNELS, subtype="PCM_16") as wav:
            with loopback.recorder(samplerate=SAMPLE_RATE, channels=CHANNELS) as recorder:
                while not stop_event.is_set():
                    data = recorder.record(numframes=frames)
                    if data is not None and len(data):
                        wav.write(data)
                        wav.flush()
    except Exception as exc:
        root.after(0, lambda message=str(exc): messagebox.showerror("Audio capture error", message))


def stop_ffmpeg():
    global video_process
    if video_process is None:
        return
    try:
        video_process.stdin.write(b"q\n")
        video_process.stdin.flush()
        video_process.wait(timeout=15)
    except Exception:
        try:
            video_process.terminate()
        except Exception:
            pass
    video_process = None


def combine_files():
    if not temp_video or not temp_audio or not Path(temp_video).exists() or not Path(temp_audio).exists():
        raise RuntimeError("The temporary video or audio file was not created.")
    command = [FFMPEG, "-y", "-i", str(temp_video), "-i", str(temp_audio), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(final_output)]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr[-3000:])
    Path(temp_video).unlink(missing_ok=True)
    Path(temp_audio).unlink(missing_ok=True)


def finish_recording():
    global recording, audio_thread
    status.set("Finishing recording and combining audio...")
    stop_event.set()
    if audio_thread:
        audio_thread.join(timeout=15)
    stop_ffmpeg()
    try:
        combine_files()
        recording = False
        start_button.config(state=tk.NORMAL)
        stop_button.config(state=tk.DISABLED)
        status.set(f"Saved: {final_output}")
        messagebox.showinfo("Recording complete", f"Video and system audio saved to:\n\n{final_output}")
    except Exception as exc:
        recording = False
        start_button.config(state=tk.NORMAL)
        stop_button.config(state=tk.DISABLED)
        status.set("Recording failed")
        messagebox.showerror("Recording error", str(exc))


def stop_recording():
    if recording:
        stop_button.config(state=tk.DISABLED)
        root.after(50, finish_recording)


def start_recording():
    global recording, stop_event, video_process, audio_thread, temp_video, temp_audio, final_output, record_started
    if recording:
        return
    if not Path(FFMPEG).exists():
        messagebox.showerror("FFmpeg not found", f"Update FFMPEG in screen_recorder.py or install FFmpeg at:\n{FFMPEG}")
        return
    selected = window_box.get()
    if not selected:
        messagebox.showerror("Choose a video window", "Open the running video first, refresh the list, and select its window.")
        return
    if not audio_box.get():
        messagebox.showerror("Choose audio", "Select the speaker/headphones output that plays the video sound.")
        return
    try:
        minutes = float(duration.get())
        if minutes <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid duration", "Enter a positive duration in minutes, such as 15 or 0.5.")
        return

    title = selected.split(" | ", 1)[-1]
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_video = OUTPUT_FOLDER / f"TEMP_VIDEO_{stamp}.mkv"
    temp_audio = OUTPUT_FOLDER / f"TEMP_AUDIO_{stamp}.wav"
    final_output = OUTPUT_FOLDER / f"screen_recording_{stamp}.mp4"
    stop_event.clear()

    # gdigrab receives the selected top-level window, not the desktop.
    command = [FFMPEG, "-y", "-f", "gdigrab", "-framerate", "30", "-draw_mouse", "0", "-i", f"title={title}", "-t", str(int(minutes * 60)), "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p", str(temp_video)]
    try:
        audio_thread = threading.Thread(target=capture_audio, args=(audio_box.get(), temp_audio), daemon=True)
        audio_thread.start()
        time.sleep(0.7)
        video_process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        recording = True
        record_started = time.time()
        start_button.config(state=tk.DISABLED)
        stop_button.config(state=tk.NORMAL)
        status.set(f"Recording selected window: {title}")
        update_timer()
        root.after(int(minutes * 60000) + 1000, lambda: stop_recording() if recording else None)
    except Exception as exc:
        stop_event.set()
        stop_ffmpeg()
        messagebox.showerror("Could not start recording", str(exc))


def update_timer():
    if recording:
        elapsed = int(time.time() - record_started)
        timer.set(time.strftime("%H:%M:%S", time.gmtime(elapsed)))
        root.after(1000, update_timer)


def refresh_windows():
    values = [f"{hwnd} | {title}" for hwnd, title in visible_windows()]
    window_box["values"] = values
    if values and not window_box.get():
        window_box.current(0)


def refresh_audio():
    values = [speaker.name for speaker in speakers()]
    audio_box["values"] = values
    if values and not audio_box.get():
        audio_box.current(0)


def close():
    if recording:
        if messagebox.askyesno("Recording active", "Stop and save the recording before closing?"):
            stop_recording()
            root.after(2000, root.destroy)
    else:
        root.destroy()


root = tk.Tk()
root.title("Video Window Recorder with System Audio")
root.geometry("760x430")
root.columnconfigure(1, weight=1)

tk.Label(root, text="Capture only the running video window", font=("Arial", 17, "bold")).grid(row=0, column=0, columnspan=3, pady=15)
tk.Label(root, text="Open the video first. The recorder does not capture the entire desktop.").grid(row=1, column=0, columnspan=3, pady=4)
tk.Label(root, text="Video window").grid(row=2, column=0, sticky="w", padx=12, pady=8)
window_box = ttk.Combobox(root, width=72, state="readonly")
window_box.grid(row=2, column=1, sticky="ew", padx=8)
ttk.Button(root, text="Refresh", command=refresh_windows).grid(row=2, column=2, padx=8)
tk.Label(root, text="Audio output").grid(row=3, column=0, sticky="w", padx=12, pady=8)
audio_box = ttk.Combobox(root, width=72, state="readonly")
audio_box.grid(row=3, column=1, sticky="ew", padx=8)
ttk.Button(root, text="Refresh", command=refresh_audio).grid(row=3, column=2, padx=8)
tk.Label(root, text="Duration (minutes)").grid(row=4, column=0, sticky="w", padx=12, pady=8)
duration = tk.StringVar(value="15")
tk.Entry(root, textvariable=duration).grid(row=4, column=1, sticky="w", padx=8)
timer = tk.StringVar(value="00:00:00")
tk.Label(root, textvariable=timer, font=("Arial", 24)).grid(row=5, column=0, columnspan=3, pady=10)
status = tk.StringVar(value="Ready")
tk.Label(root, textvariable=status, wraplength=720).grid(row=6, column=0, columnspan=3, pady=8)
start_button = tk.Button(root, text="START RECORDING", width=25, height=2, command=start_recording)
start_button.grid(row=7, column=0, columnspan=2, pady=12)
stop_button = tk.Button(root, text="STOP RECORDING", width=25, height=2, state=tk.DISABLED, command=stop_recording)
stop_button.grid(row=7, column=1, columnspan=2, pady=12)
root.protocol("WM_DELETE_WINDOW", close)
refresh_windows()
refresh_audio()
root.mainloop()
