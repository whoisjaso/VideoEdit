"""ffmpeg/ffprobe wrappers: probe, proxies, silence and scene detection, auto-reframe."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

FFMPEG = shutil.which("ffmpeg") or "ffmpeg"
FFPROBE = shutil.which("ffprobe") or "ffprobe"


def run(args: list[str], timeout: int | None = None) -> subprocess.CompletedProcess:
    p = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    if p.returncode != 0:
        raise RuntimeError(f"{Path(args[0]).name} failed: {p.stderr.strip()[-1500:]}")
    return p


def probe(path: str | Path) -> dict:
    p = run([FFPROBE, "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)])
    info = json.loads(p.stdout)
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    w, h = (int(v["width"]), int(v["height"])) if v else (0, 0)
    rot = 0
    if v:
        for sd in v.get("side_data_list", []) or []:
            if "rotation" in sd:
                rot = int(sd["rotation"])
        rot = int(v.get("tags", {}).get("rotate", rot) or rot)
    if abs(rot) in (90, 270):
        w, h = h, w
    fps = 30.0
    if v and v.get("avg_frame_rate", "0/0") != "0/0":
        n, d = v["avg_frame_rate"].split("/")
        fps = float(n) / float(d) if float(d) else 30.0
    return {
        "duration": float(info["format"].get("duration", 0)),
        "size": int(info["format"].get("size", 0)),
        "width": w, "height": h, "fps": round(fps, 3),
        "has_video": bool(v), "has_audio": bool(a),
        "vcodec": v.get("codec_name") if v else None,
    }


def extract_audio(src: str | Path, out: str | Path, rate: int = 16000) -> Path:
    """Mono analysis track for transcription and silence detection."""
    run([FFMPEG, "-v", "error", "-y", "-i", str(src), "-vn", "-ac", "1", "-ar", str(rate), str(out)])
    return Path(out)


def make_proxy(src: str | Path, out: str | Path, height: int = 720) -> Path:
    """Light H.264 proxy: fast to scrub, fast to cut from (the 'Create Proxies' step in Premiere)."""
    run([FFMPEG, "-v", "error", "-y", "-i", str(src), "-vf", f"scale=-2:{height}", "-c:v", "libx264",
         "-preset", "veryfast", "-crf", "23", "-g", "30", "-c:a", "aac", "-b:a", "128k",
         "-movflags", "+faststart", str(out)])
    return Path(out)


def thumbnail(src: str | Path, out: str | Path, t: float = 1.0, width: int = 540) -> Path:
    run([FFMPEG, "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(src), "-frames:v", "1",
         "-vf", f"scale={width}:-2", str(out)])
    return Path(out)


def silences(audio: str | Path, noise_db: float = -35, min_dur: float = 0.35) -> list[tuple[float, float]]:
    p = subprocess.run([FFMPEG, "-v", "info", "-i", str(audio), "-af",
                        f"silencedetect=noise={noise_db}dB:d={min_dur}", "-f", "null", "-"],
                       capture_output=True, text=True)
    out, start = [], None
    for line in p.stderr.splitlines():
        m = re.search(r"silence_start: ([\d.]+)", line)
        if m:
            start = float(m.group(1))
        m = re.search(r"silence_end: ([\d.]+)", line)
        if m and start is not None:
            out.append((start, float(m.group(1))))
            start = None
    return out


def speech_spans(duration: float, sil: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Complement of silences: where someone is talking."""
    spans, t = [], 0.0
    for a, b in sil:
        if a - t > 0.05:
            spans.append((t, a))
        t = b
    if duration - t > 0.05:
        spans.append((t, duration))
    return spans


def scene_cuts(src: str | Path, threshold: float = 10.0) -> list[float]:
    """Scene Edit Detection: timestamps of hard cuts in the source."""
    p = subprocess.run([FFMPEG, "-v", "info", "-i", str(src), "-vf", f"scale=320:-2,scdet=threshold={threshold}",
                        "-an", "-f", "null", "-"], capture_output=True, text=True)
    return [float(m.group(1)) for m in re.finditer(r"lavfi\.scd\.time: ([\d.]+)", p.stderr)]


def face_center_x(src: str | Path, start: float, end: float, samples: int = 6) -> float:
    """Auto Reframe: median horizontal face position (0..1) across the range. 0.5 if unknown."""
    try:
        import cv2  # optional (installed by setup)
    except ImportError:
        return 0.5
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    cap = cv2.VideoCapture(str(src))
    xs = []
    for i in range(samples):
        t = start + (end - start) * (i + 0.5) / samples
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ok, frame = cap.read()
        if not ok:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = cascade.detectMultiScale(gray, 1.2, 5, minSize=(40, 40))
        if len(faces):
            x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
            xs.append((x + w / 2) / frame.shape[1])
    cap.release()
    if not xs:
        return 0.5
    xs.sort()
    return float(xs[len(xs) // 2])
