import argparse
import html
import json
from pathlib import Path

import cv2
import numpy as np
from faster_whisper import WhisperModel


def metadata(path):
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {path}")
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    result = {"fps": round(fps, 2), "frame_count": int(frames),
              "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
              "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
              "duration_seconds": round(frames / fps, 2) if fps else 0}
    cap.release()
    return result


def transcribe(path, model_name, language):
    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    options = {"vad_filter": True, "beam_size": 5}
    if language != "auto":
        options["language"] = language
    segments, info = model.transcribe(str(path), **options)
    rows = [{"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()} for s in segments]
    return {"language": info.language, "language_probability": info.language_probability,
            "text": " ".join(x["text"] for x in rows), "segments": rows}


def speech_stats(t):
    rows = t["segments"]
    if not rows:
        return {"speech_duration_seconds": 0, "word_count": 0, "words_per_minute": 0,
                "pause_count": 0, "average_pause_seconds": 0, "longest_pause_seconds": 0}
    words = len(t["text"].split())
    pauses = [b["start"] - a["end"] for a, b in zip(rows, rows[1:]) if b["start"] - a["end"] >= .5]
    duration = max(rows[-1]["end"] - rows[0]["start"], 1)
    return {"speech_duration_seconds": round(sum(x["end"] - x["start"] for x in rows), 2),
            "word_count": words, "words_per_minute": round(words / duration * 60, 2),
            "pause_count": len(pauses), "average_pause_seconds": round(sum(pauses) / len(pauses), 2) if pauses else 0,
            "longest_pause_seconds": round(max(pauses), 2) if pauses else 0}


def video_stats(path):
    cap = cv2.VideoCapture(str(path)); fps = cap.get(cv2.CAP_PROP_FPS) or 25
    classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    step = max(int(fps * 2), 1); sampled = faces = number = 0; brightness = []
    while True:
        ok, frame = cap.read()
        if not ok: break
        if number % step == 0:
            sampled += 1; gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY); brightness.append(float(np.mean(gray)))
            if len(classifier.detectMultiScale(gray, 1.1, 5, minSize=(40, 40))) > 0: faces += 1
        number += 1
    cap.release()
    return {"sampled_frames": sampled, "frames_with_detected_faces": faces,
            "face_visibility_percentage": round(faces / sampled * 100, 2) if sampled else 0,
            "average_brightness": round(float(np.mean(brightness)), 2) if brightness else 0}


def write_html(report, path):
    t, s, v = report["transcription"], report["observable_speech_analysis"], report["observable_video_analysis"]
    rows = "".join(f"<tr><td>{x['start']}</td><td>{x['end']}</td><td>{html.escape(x['text'])}</td></tr>" for x in t["segments"])
    content = f'''<!doctype html><meta charset="utf-8"><title>Video analysis report</title><style>body{{font:16px Arial;max-width:1000px;margin:30px auto}}.card{{border:1px solid #ddd;padding:16px;margin:14px 0;border-radius:8px}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ddd;padding:8px;text-align:left}}th{{background:#eef3f8}}.notice{{background:#fff4ce;padding:12px}}</style><h1>Video analysis report</h1><div class="notice">{html.escape(report['interpretation_notice'])}</div><div class="card"><h2>Summary</h2><p>Language: {html.escape(str(t['language']))}</p><p>Speech: {s['speech_duration_seconds']} seconds; words: {s['word_count']}; words/minute: {s['words_per_minute']}</p><p>Pauses: {s['pause_count']}; face visibility: {v['face_visibility_percentage']}%</p></div><div class="card"><h2>Transcript</h2><p>{html.escape(t['text'])}</p><table><tr><th>Start</th><th>End</th><th>Text</th></tr>{rows}</table></div><div class="card"><h2>Measurements</h2><pre>{html.escape(json.dumps(report['video_metadata'], ensure_ascii=False, indent=2))}</pre><pre>{html.escape(json.dumps(v, ensure_ascii=False, indent=2))}</pre></div>'''
    Path(path).write_text(content, encoding="utf-8")


def main():
    p = argparse.ArgumentParser(); p.add_argument("--video", required=True); p.add_argument("--output", default="report.json"); p.add_argument("--html-output"); p.add_argument("--model", default="small", choices=["tiny", "base", "small", "medium", "large-v3"]); p.add_argument("--language", default="bn", help="bn, en, or auto")
    args = p.parse_args(); video = Path(args.video)
    if not video.exists(): raise FileNotFoundError(video)
    report = {"video": str(video), "video_metadata": metadata(video)}
    report["transcription"] = transcribe(video, args.model, args.language)
    report["observable_speech_analysis"] = speech_stats(report["transcription"])
    report["observable_video_analysis"] = video_stats(video)
    report["interpretation_notice"] = "This report describes measurable audio and video signals only. It does not establish truthfulness, mental health, personality, or diagnosis."
    out = Path(args.output); out.parent.mkdir(parents=True, exist_ok=True); out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    html_path = Path(args.html_output) if args.html_output else out.with_suffix(".html"); write_html(report, html_path)
    print(f"JSON report: {out}\nHTML report: {html_path}")


if __name__ == "__main__": main()
