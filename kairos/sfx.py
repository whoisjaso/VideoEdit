"""The sound library: the skill's packs (stand-ins for Jason's CapCut sounds) + anything uploaded."""
from __future__ import annotations

import json
from pathlib import Path

from .config import LIBRARY, SKILL

ROOTS = [SKILL / "assets" / "sfx", LIBRARY / "sfx"]

# What each built-in is for, from the playbook. Shown in the Library and given to agents.
JOBS = {
    "deep_bass": "Hook / statement that must land (Bass impact)",
    "whoosh": "Every zoom-in", "swoosh": "Soft zoom / swipe",
    "camera_shutter": "Transition between sections",
    "pop": "Anything appears (layer with click)", "click": "Anything appears (layer with pop)",
    "riser": "Build-up, ends exactly on the payoff", "metallic_hit": "Reveal sting",
    "synth_hit": "Reveal / magic", "kaching": "Money, numbers", "typing": "New caption line (sparingly)",
    "ding": "Follow button flips to Following", "snap": "Snap cut / list item",
}


def index() -> dict[str, Path]:
    """key -> file. Keys are relative paths without extension: 'whoosh', 'ios/ios_tink', 'pack4/cinestrike'."""
    out: dict[str, Path] = {}
    for root in ROOTS:
        if not root.exists():
            continue
        for p in sorted(root.rglob("*")):
            if p.suffix.lower() in (".wav", ".mp3", ".m4a", ".ogg", ".aac"):
                out[str(p.relative_to(root).with_suffix(""))] = p
    return out


def resolve(key: str) -> Path | None:
    idx = index()
    if key in idx:
        return idx[key]
    tail = [k for k in idx if k.split("/")[-1] == key]
    return idx[tail[0]] if tail else None


def catalog() -> list[dict]:
    out = []
    for key, path in index().items():
        pack = key.split("/")[0] if "/" in key else "core"
        job = JOBS.get(key.split("/")[-1], "")
        man = path.parent / "manifest.json"
        if not job and man.exists():
            try:
                names = {m["name"] for m in json.loads(man.read_text())}
                if path.stem in names:
                    job = f"{pack} pack"
            except (ValueError, KeyError, TypeError):
                pass
        out.append({"key": key, "pack": pack, "job": job, "file": path.name,
                    "uploaded": LIBRARY in path.parents})
    return out
