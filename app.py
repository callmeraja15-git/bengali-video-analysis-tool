import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

ROOT = Path(__file__).resolve().parent


def install(log):
    log("Installing Python packages...\n")
    result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(ROOT / "requirements.txt")], text=True, capture_output=True)
    log(result.stdout + result.stderr)
    if result.returncode: raise RuntimeError("Package installation failed")


def has_ffmpeg():
    try: subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); return True
    except FileNotFoundError: return False


def main():
    root = tk.Tk(); root.title("Bengali Video Clip Analyzer"); root.geometry("760x620"); root.columnconfigure(1, weight=1); root.rowconfigure(7, weight=1)
    fields = {}
    definitions = [("Main video", ""), ("Start timestamp (HH:MM:SS)", "00:00:00"), ("Duration in minutes", "0.5"), ("Clip name", "clip_01")]
    for row, (label, default) in enumerate(definitions):
        ttk.Label(root, text=label).grid(row=row, column=0, sticky="w", padx=12, pady=8)
        fields[label] = tk.StringVar(value=default); ttk.Entry(root, textvariable=fields[label], width=58).grid(row=row, column=1, sticky="ew", padx=12, pady=8)
    def browse():
        value = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.mov *.mkv *.avi"), ("All files", "*.*")])
        if value: fields["Main video"].set(value)
    ttk.Button(root, text="Browse", command=browse).grid(row=0, column=2, padx=10)
    ttk.Label(root, text="Language").grid(row=4, column=0, sticky="w", padx=12); language = tk.StringVar(value="Bengali (bn)"); ttk.Combobox(root, textvariable=language, values=["Bengali (bn)", "English (en)", "Auto detect"], state="readonly").grid(row=4, column=1, sticky="w", padx=12)
    ttk.Label(root, text="Whisper model").grid(row=5, column=0, sticky="w", padx=12); model = tk.StringVar(value="small"); ttk.Combobox(root, textvariable=model, values=["tiny", "base", "small", "medium", "large-v3"], state="readonly").grid(row=5, column=1, sticky="w", padx=12)
    log_box = tk.Text(root, height=17, wrap="word"); log_box.grid(row=7, column=0, columnspan=3, sticky="nsew", padx=12, pady=12)
    def log(text): log_box.insert("end", text); log_box.see("end"); root.update_idletasks()
    def start():
        video = Path(fields["Main video"].get())
        if not video.exists(): return messagebox.showerror("Missing video", "Choose a saved video file first.")
        try: minutes = float(fields["Duration in minutes"].get()); assert minutes > 0
        except (ValueError, AssertionError): return messagebox.showerror("Invalid duration", "Enter a positive number such as 0.5 or 1.")
        name = fields["Clip name"].get().strip() or "clip_01"; lang = {"Bengali (bn)":"bn", "English (en)":"en", "Auto detect":"auto"}[language.get()]
        clip = ROOT / "clips" / f"{name}.mp4"; report = ROOT / "results" / f"{name}_report.json"; clip.parent.mkdir(exist_ok=True); report.parent.mkdir(exist_ok=True)
        def worker():
            try:
                if not has_ffmpeg(): raise RuntimeError("FFmpeg was not found. Install it and add it to PATH.")
                install(log); log("Creating clip...\n")
                command = ["ffmpeg", "-y", "-ss", fields["Start timestamp (HH:MM:SS)"].get(), "-i", str(video), "-t", str(round(minutes * 60)), "-c:v", "libx264", "-c:a", "aac", str(clip)]
                result = subprocess.run(command, text=True, capture_output=True); log(result.stdout + result.stderr)
                if result.returncode: raise RuntimeError("FFmpeg could not create the clip")
                log("Transcribing and analyzing...\n")
                command = [sys.executable, str(ROOT / "video_analysis.py"), "--video", str(clip), "--output", str(report), "--model", model.get(), "--language", lang]
                result = subprocess.run(command, text=True, capture_output=True); log(result.stdout + result.stderr)
                if result.returncode: raise RuntimeError("Analysis failed")
                messagebox.showinfo("Complete", f"Saved clip and reports in:\n{ROOT / 'clips'}\n{ROOT / 'results'}")
            except Exception as error: messagebox.showerror("Error", str(error))
        threading.Thread(target=worker, daemon=True).start()
    ttk.Button(root, text="Create clip and analyze", command=start).grid(row=6, column=1, pady=10); ttk.Label(root, text="Reports include JSON and HTML. Measurements are observations, not diagnoses.").grid(row=8, column=0, columnspan=3, pady=6); root.mainloop()


if __name__ == "__main__": main()
