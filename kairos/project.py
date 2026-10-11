"""Projects on disk and the long-video pipeline.

data/projects/<id>/
  project.json            meta, brief, pipeline progress, moments, clip ids
  source.<ext>            the original upload (never re-encoded)
  audio16k.wav            analysis audio
  words.json speech.json  transcript, speech spans
  clips/<clip>.json       one Timeline per clip (the EditGraph, versioned)
  renders/<clip>_vN.mp4   previews and finals
"""
from __future__ import annotations

import json
import shutil
import threading
import time
import traceback
import uuid
from pathlib import Path

from . import autoedit, config, media, moments, render, styles, transcribe
from .config import PROJECTS
from .timeline import Timeline

STEPS = [("probe", "Reading your video"), ("listen", "Listening"), ("moments", "Finding the best moments"),
         ("edit", "Editing"), ("render", "Rendering previews")]
_lock = threading.Lock()


def pdir(pid: str) -> Path:
    return PROJECTS / pid


def load(pid: str) -> dict:
    return json.loads((pdir(pid) / "project.json").read_text())


def save(p: dict) -> dict:
    with _lock:
        tmp = pdir(p["id"]) / "project.json.tmp"
        tmp.write_text(json.dumps(p, indent=2))
        tmp.replace(pdir(p["id"]) / "project.json")
    return p


def list_projects() -> list[dict]:
    out = []
    for d in sorted(PROJECTS.glob("*/project.json"), key=lambda x: -x.stat().st_mtime):
        p = json.loads(d.read_text())
        out.append({k: p.get(k) for k in ("id", "name", "created", "status", "info", "clips", "progress")})
    return out


def create(source: str | Path, name: str = "", brief: dict | None = None, move: bool = False) -> dict:
    pid = "p_" + uuid.uuid4().hex[:10]
    d = pdir(pid)
    (d / "clips").mkdir(parents=True)
    (d / "renders").mkdir()
    source = Path(source)
    dst = d / f"source{source.suffix.lower() or '.mp4'}"
    (shutil.move if move else shutil.copy2)(str(source), dst)
    p = {"id": pid, "name": name or source.stem, "created": time.time(), "source": dst.name,
         "brief": brief or {}, "status": "queued", "progress": {"step": None, "pct": 0, "steps": [s for s, _ in STEPS]},
         "moments": [], "clips": [], "engine": {}, "error": None}
    return save(p)


def set_brief(pid: str, brief: dict) -> dict:
    p = load(pid)
    p["brief"].update(brief)
    return save(p)


def _progress(p: dict, step: str, pct: float, note: str = "") -> None:
    p["progress"].update({"step": step, "pct": round(pct, 3), "note": note,
                          "label": dict(STEPS).get(step, step)})
    save(p)


def get_words(pid: str) -> list[dict]:
    f = pdir(pid) / "words.json"
    return json.loads(f.read_text()) if f.exists() else []


def get_speech(pid: str) -> list[tuple[float, float]]:
    f = pdir(pid) / "speech.json"
    return [tuple(x) for x in json.loads(f.read_text())] if f.exists() else []


def analyze(pid: str) -> dict:
    """probe -> audio -> transcript (cached: a 1-hour video is only ever transcribed once)."""
    p = load(pid)
    d = pdir(pid)
    src = d / p["source"]
    _progress(p, "probe", 0.02)
    p["info"] = media.probe(src)
    media.thumbnail(src, d / "thumb.jpg", t=min(2.0, p["info"]["duration"] / 3))
    save(p)
    _progress(p, "listen", 0.05, "Pulling the audio")
    wav = d / "audio16k.wav"
    if not wav.exists():
        media.extract_audio(src, wav)
    if not (d / "speech.json").exists():
        sil = media.silences(wav)
        (d / "speech.json").write_text(json.dumps(media.speech_spans(p["info"]["duration"], sil)))
    if not (d / "words.json").exists():
        engine = config.settings()["transcriber"]
        words = transcribe.transcribe(wav, engine, progress=lambda f: _progress(p, "listen", 0.05 + 0.4 * f, "Transcribing"))
        (d / "words.json").write_text(json.dumps(words))
        p["engine"]["transcriber"] = (transcribe.available() or ["none"])[0] if engine == "auto" else engine
    save(p)
    return p


def find_moments(pid: str, n: int | None = None, min_s: float | None = None, max_s: float | None = None) -> list[dict]:
    p = load(pid)
    b = p["brief"]
    n = n or int(b.get("count", 5))
    lo, hi = (min_s, max_s) if min_s else {"short": (15, 30), "medium": (30, 60), "long": (60, 90)}.get(b.get("length", "medium"), (30, 60))
    style = styles.get(b.get("style", "jason"))
    brief = " ".join(x for x in (b.get("about", ""), b.get("rules", "")) if x)
    ms, engine = moments.mine(get_words(pid), n, lo, hi or 60, brief, style, get_speech(pid))
    p = load(pid)
    p["moments"], p["engine"]["moments"] = ms, engine
    save(p)
    return ms


def clip_path(pid: str, cid: str) -> Path:
    return pdir(pid) / "clips" / f"{cid}.json"


def get_clip(pid: str, cid: str) -> Timeline:
    return Timeline.model_validate_json(clip_path(pid, cid).read_text())


def save_clip(pid: str, tl: Timeline, bump: bool = True) -> Timeline:
    tl = Timeline.model_validate(tl.model_dump())     # agents edit with model_copy; re-check before it hits disk
    f = clip_path(pid, tl.id)
    if bump and f.exists():
        tl.version += 1
    tmp = f.with_suffix(f".{threading.get_ident()}.tmp")   # atomic: readers never see a half-written clip
    tmp.write_text(tl.model_dump_json(indent=1))
    tmp.replace(f)
    return tl


def edit_moment(pid: str, moment: dict, style_name: str | None = None) -> Timeline:
    p = load(pid)
    style_name = style_name or p["brief"].get("style", "jason")
    tl = autoedit.build(str(pdir(pid) / p["source"]), p["info"], get_words(pid), get_speech(pid), moment,
                        styles.get(style_name), style_name)
    save_clip(pid, tl, bump=False)
    p = load(pid)
    p["clips"].append(tl.id)
    save(p)
    return tl


def render_clip(pid: str, cid: str, preview: bool = True) -> Path:
    p = load(pid)
    tl = get_clip(pid, cid)
    out = pdir(pid) / "renders" / f"{cid}_v{tl.version}{'_preview' if preview else ''}.mp4"
    render.render(tl, str(pdir(pid) / p["source"]), p["info"], styles.get(tl.style), out, preview=preview,
                  workdir=pdir(pid) / "renders")
    return out


def latest_render(pid: str, cid: str) -> Path | None:
    tl = get_clip(pid, cid)
    for suffix in ("", "_preview"):
        f = pdir(pid) / "renders" / f"{cid}_v{tl.version}{suffix}.mp4"
        if f.exists():
            return f
    return None


def run_pipeline(pid: str) -> None:
    """The whole thing, for the web app's 'Make my clips' button."""
    p = load(pid)
    try:
        p["status"] = "working"
        p["error"] = None
        save(p)
        analyze(pid)
        p = load(pid)
        _progress(p, "moments", 0.5)
        ms = find_moments(pid)
        p = load(pid)
        p["clips"] = []
        save(p)
        for i, m in enumerate(ms):
            _progress(load(pid), "edit", 0.55 + 0.1 * i / max(len(ms), 1), f"Clip {i + 1} of {len(ms)}")
            edit_moment(pid, m)
        p = load(pid)
        for i, cid in enumerate(p["clips"]):
            _progress(load(pid), "render", 0.65 + 0.35 * i / max(len(p["clips"]), 1), f"Clip {i + 1} of {len(p['clips'])}")
            render_clip(pid, cid, preview=True)
        p = load(pid)
        p["status"] = "ready"
        p.pop("trace", None)
        _progress(p, "done", 1.0)
    except Exception as e:  # surface to the UI, keep the trace for agents
        p = load(pid)
        p["status"] = "error"
        p["error"] = f"{e}"
        p["trace"] = traceback.format_exc()[-3000:]
        save(p)


def start(pid: str) -> threading.Thread:
    t = threading.Thread(target=run_pipeline, args=(pid,), daemon=True)
    t.start()
    return t
