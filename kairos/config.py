"""Paths and settings. Everything lives under one data directory so a project is portable."""
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # repo root
PKG = Path(__file__).resolve().parent                   # kairos/
WEB = ROOT / "web"
FONTS = PKG / "assets" / "fonts"
SKILL = ROOT / ".claude" / "skills" / "jason-video-editor"   # the 8.3 playbook + SFX library

DATA = Path(os.environ.get("KAIROS_DATA", ROOT / "data")).resolve()
PROJECTS = DATA / "projects"
UPLOADS = DATA / "uploads"
LIBRARY = DATA / "library"
STYLES = DATA / "styles"
SETTINGS_FILE = DATA / "settings.json"

for d in (PROJECTS, UPLOADS, LIBRARY / "sfx", LIBRARY / "references", STYLES):
    d.mkdir(parents=True, exist_ok=True)

DEFAULTS = {
    "model": "claude-opus-5-5",
    "transcriber": "auto",        # auto | whisper | vosk | none
    "preview_height": 960,        # previews render at 540x960, finals at 1080x1920
    "chunk_mb": 8,                # upload chunk size the web app uses
}


def settings() -> dict:
    s = dict(DEFAULTS)
    if SETTINGS_FILE.exists():
        s.update(json.loads(SETTINGS_FILE.read_text()))
    return s


def save_settings(patch: dict) -> dict:
    s = settings()
    s.update({k: v for k, v in patch.items() if k in DEFAULTS or k == "anthropic_api_key"})
    SETTINGS_FILE.write_text(json.dumps(s, indent=2))
    return s


def api_key() -> str | None:
    return os.environ.get("ANTHROPIC_API_KEY") or settings().get("anthropic_api_key") or None
