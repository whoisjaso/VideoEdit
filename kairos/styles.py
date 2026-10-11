"""Style profiles: the playbook as data the engine (and Claude) can read, and feedback can tune.

Each profile is a JSON file in data/styles/. The built-ins below are the seeds; once a profile
is saved, learn.py adjusts it from feedback and the saved copy wins.
"""
from __future__ import annotations

import copy
import json

from .config import STYLES

# Event -> SFX, decoded in playbook §3c ("MASTER SFX MAP"). Proven rules are seen in 3+ reels.
JASON_SFX = {
    "hook": "deep_bass",           # Bass impact on the hook word (x2)
    "zoom": "whoosh",              # every zoom gets a whoosh (x3)
    "cut": "camera_shutter",       # transitions: camera shutter (x4)
    "popup": ["pop", "click"],     # pop + click layered on every appearance (x4)
    "reveal": "metallic_hit",      # riser -> reveal sting (x3)
    "riser": "riser",              # ends exactly on the payoff (x2)
    "money": "kaching",            # money / numbers
    "caption": "typing",           # soft typing under new caption lines (x1, sparingly)
    "cta": "ding",                 # bell when Follow flips to Following
    "slowmo": "whoosh",            # the curse-word slow-mo is a zoom
}

BUILTIN = {
    "jason": {
        "name": "Jason (the 8.3 standard)",
        "blurb": "Gold keywords, raw captions, punch zooms, a sound on every beat.",
        "colors": {"white": "#FFFFFF", "gold": "#FFD24A", "green": "#2BE37A", "red": "#FF3B3B"},
        "caption": {"font": "Montserrat ExtraBold", "size": 92, "y": 0.62, "max_words": 3,
                    "uppercase_keywords": True, "glow": True, "keyword_ratio": 0.08},
        "title": {"font": "Bebas Neue", "size": 170, "hold_min": 1.5},
        "cut": {"gap_max": 1.4, "gap_keep": 0.75, "cold_open": True, "cold_open_max": 3.0},
        "zoom": {"scale": 1.14, "every": 6.0, "drift": 0.035},
        "slowmo": {"enabled": True, "max": 2},
        "sfx": JASON_SFX,
        "sfx_gain": 0.8,
        "caption_sfx": False,      # typing under every caption is noisy; on only when asked
        "grade": "moody",
        "cta": {"enabled": True, "text": "FOLLOW FOR MORE"},
        "raw": True,               # never bleep, mute or asterisk
        "lessons": [
            "Hook = the boldest line, untouched, in the first 2 seconds.",
            "Keep the speaker's pauses; only shorten dead air over 1.4s.",
            "Never reorder the argument: hook -> problem -> argument -> payoff -> CTA.",
            "Gold is rationed: about one keyword per idea.",
            "Never show the same words twice on screen.",
        ],
    },
    "ios": {
        "name": "Clean iOS",
        "blurb": "Restraint. Soft springs, clean type, real iOS sounds.",
        "colors": {"white": "#FFFFFF", "gold": "#FFD60A", "green": "#30D158", "red": "#FF453A"},
        "caption": {"font": "Montserrat SemiBold", "size": 78, "y": 0.66, "max_words": 4,
                    "uppercase_keywords": False, "glow": False, "keyword_ratio": 0.05},
        "title": {"font": "Montserrat ExtraBold", "size": 120, "hold_min": 1.5},
        "cut": {"gap_max": 1.0, "gap_keep": 0.6, "cold_open": False, "cold_open_max": 2.5},
        "zoom": {"scale": 1.08, "every": 9.0, "drift": 0.02},
        "slowmo": {"enabled": False, "max": 0},
        "shake": False,
        "sfx": {"hook": "ios/ios_note", "zoom": "swoosh", "cut": "ios/ios_tink", "popup": ["ios/ios_tink"],
                "reveal": "ios/ios_success", "riser": "riser", "money": "ios/ios_received",
                "caption": "ios/ios_key", "cta": "ios/ios_tritone", "slowmo": "swoosh"},
        "sfx_gain": 0.6,
        "caption_sfx": False,
        "grade": "cool_clean",
        "cta": {"enabled": True, "text": "FOLLOW"},
        "raw": True,
        "lessons": ["Restraint over noise.", "Motion is smooth, never jarring."],
    },
    "cinematic": {
        "name": "Cinematic",
        "blurb": "Moody grade, big serif-free titles, bass hits on the lines that land.",
        "colors": {"white": "#F2F2F2", "gold": "#E8C27A", "green": "#7BE0A0", "red": "#E05A4F"},
        "caption": {"font": "Montserrat SemiBold", "size": 72, "y": 0.72, "max_words": 5,
                    "uppercase_keywords": True, "glow": True, "keyword_ratio": 0.05},
        "title": {"font": "Bebas Neue", "size": 200, "hold_min": 2.0},
        "cut": {"gap_max": 1.8, "gap_keep": 1.0, "cold_open": True, "cold_open_max": 3.0},
        "zoom": {"scale": 1.06, "every": 10.0, "drift": 0.05},
        "slowmo": {"enabled": False, "max": 0},
        "sfx": {"hook": "pack4/cinestrike", "zoom": "pack3/cinematic_woosh", "cut": "pack4/basscrack",
                "popup": ["pop"], "reveal": "pack4/cinestrike", "riser": "pack3/riser", "money": "kaching",
                "caption": "typing", "cta": "ding", "slowmo": "pack3/cinematic_woosh"},
        "sfx_gain": 0.75,
        "caption_sfx": False,
        "grade": "teal_orange",
        "cta": {"enabled": False, "text": "FOLLOW"},
        "raw": True,
        "lessons": ["Let lines breathe.", "One hit per section, not per sentence."],
    },
}


def list_styles() -> list[dict]:
    names = set(BUILTIN) | {p.stem for p in STYLES.glob("*.json")}
    out = []
    order = list(BUILTIN)
    for n in sorted(names, key=lambda x: (order.index(x) if x in order else len(order), x)):
        s = get(n)
        out.append({"id": n, "name": s.get("name", n), "blurb": s.get("blurb", ""),
                    "learned": len(s.get("history", []))})
    return out


def get(name: str) -> dict:
    p = STYLES / f"{name}.json"
    if p.exists():
        return json.loads(p.read_text())
    if name in BUILTIN:
        return copy.deepcopy(BUILTIN[name])
    return copy.deepcopy(BUILTIN["jason"])


def save(name: str, style: dict) -> None:
    (STYLES / f"{name}.json").write_text(json.dumps(style, indent=2))


def set_param(name: str, path: str, value) -> dict:
    """Agent-facing: set e.g. 'zoom.scale' = 1.1."""
    s = get(name)
    node = s
    keys = path.split(".")
    for k in keys[:-1]:
        node = node.setdefault(k, {})
    node[keys[-1]] = value
    save(name, s)
    return s
