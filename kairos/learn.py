"""Recursive improvement: every score and note you give tunes the style, and the next edit uses it.

Loop:  edit -> you react (score, quick chips, a sentence) -> style params shift + a written lesson ->
       the clip is rebuilt -> lessons also steer Claude's moment picking on the next video.
Everything is logged to data/journal.jsonl, the same idea as the skill's scored journal.md.
"""
from __future__ import annotations

import json
import time

from . import brain, styles
from .config import DATA

JOURNAL = DATA / "journal.jsonl"

# Quick chips in the feedback sheet -> (param path, op, amount). Bounded so no single tap breaks a style.
CHIPS = {
    "More zooms": [("zoom.every", "mul", 0.75)],
    "Fewer zooms": [("zoom.every", "mul", 1.35)],
    "Stronger zooms": [("zoom.scale", "add", 0.03)],
    "Bigger captions": [("caption.size", "add", 8)],
    "Smaller captions": [("caption.size", "add", -8)],
    "More gold words": [("caption.keyword_ratio", "add", 0.02)],
    "Less gold": [("caption.keyword_ratio", "add", -0.02)],
    "Fewer sounds": [("sfx_gain", "mul", 0.8)],
    "Louder sounds": [("sfx_gain", "mul", 1.2)],
    "Tighter cuts": [("cut.gap_max", "add", -0.25), ("cut.gap_keep", "add", -0.1)],
    "Keep more pauses": [("cut.gap_max", "add", 0.3), ("cut.gap_keep", "add", 0.1)],
    "Darker look": [("grade_intensity", "add", 0.2)],
    "Lighter look": [("grade_intensity", "add", -0.2)],
    "Hit the hook harder": [("title.size", "add", 14), ("cut.cold_open", "set", True)],
    "No cold open": [("cut.cold_open", "set", False)],
}
BOUNDS = {"zoom.every": (2.5, 20), "zoom.scale": (1.0, 1.3), "caption.size": (56, 130),
          "caption.keyword_ratio": (0.02, 0.18), "sfx_gain": (0.2, 1.4), "cut.gap_max": (0.4, 3.0),
          "cut.gap_keep": (0.2, 1.4), "grade_intensity": (0.0, 1.5), "title.size": (90, 240)}


def _get(d: dict, path: str, default=None):
    for k in path.split("."):
        d = d.get(k, {}) if isinstance(d, dict) else {}
    return d if d != {} else default


def _apply(style: dict, path: str, op: str, amount) -> tuple[str, object, object]:
    old = _get(style, path, 1.0 if path == "grade_intensity" else None)
    if op == "set":
        new = amount
    elif old is None:
        return path, None, None
    else:
        new = old * amount if op == "mul" else old + amount
        lo, hi = BOUNDS.get(path, (-1e9, 1e9))
        new = round(max(lo, min(hi, new)), 3)
    node = style
    keys = path.split(".")
    for k in keys[:-1]:
        node = node.setdefault(k, {})
    node[keys[-1]] = new
    return path, old, new


NOTE_SCHEMA = {
    "type": "object",
    "properties": {
        "changes": {"type": "array", "items": {
            "type": "object",
            "properties": {"param": {"type": "string", "enum": sorted(BOUNDS) + ["cut.cold_open", "slowmo.enabled", "caption_sfx"]},
                           "op": {"type": "string", "enum": ["add", "mul", "set"]},
                           "amount": {"type": ["number", "boolean"]}},
            "required": ["param", "op", "amount"], "additionalProperties": False}},
        "lesson": {"type": "string"},
    },
    "required": ["changes", "lesson"],
    "additionalProperties": False,
}


def feedback(style_name: str, score: float | None, chips: list[str], note: str, clip_summary: dict) -> dict:
    style = styles.get(style_name)
    applied = []
    for chip in chips:
        for path, op, amount in CHIPS.get(chip, []):
            applied.append(_apply(style, path, op, amount))
    lesson = ""
    if note.strip():
        res = brain.ask_json(
            "You tune a short-form video editor's style from the creator's feedback. Map the note to at most 4 "
            "bounded parameter changes, and write one short imperative lesson the editor must remember forever. "
            f"Current style: {json.dumps({k: style.get(k) for k in ('caption', 'cut', 'zoom', 'sfx_gain', 'grade', 'grade_intensity')})}",
            f"Clip: {json.dumps(clip_summary)}\nScore: {score}\nCreator's note: {note}", NOTE_SCHEMA, effort="low", max_tokens=2000)
        if res:
            for c in res["changes"][:4]:
                applied.append(_apply(style, c["param"], c["op"], c["amount"]))
            lesson = res["lesson"].strip()
        else:
            lesson = note.strip()            # no Claude: keep his words verbatim as the lesson
    if score is not None and score >= 8 and not note.strip():
        lesson = f"Locked: a {score}/10 clip used zoom every {_get(style, 'zoom.every')}s, captions {_get(style, 'caption.size')}px, grade {style.get('grade')}."
    applied = [a for a in applied if a[0] and a[1] != a[2]]            # drop no-ops (already at a bound)
    if lesson.startswith("Locked:"):                                     # keep only the latest locked recipe
        style["lessons"] = [x for x in style.get("lessons", []) if not x.startswith("Locked:")]
    if lesson and lesson not in style.get("lessons", []):
        style.setdefault("lessons", []).append(lesson)
        style["lessons"] = style["lessons"][-25:]
    entry = {"t": time.time(), "style": style_name, "score": score, "chips": chips, "note": note, "lesson": lesson,
             "changes": [{"param": p, "from": o, "to": n} for p, o, n in applied if p], "clip": clip_summary}
    style.setdefault("history", []).append({k: entry[k] for k in ("t", "score", "lesson", "changes")})
    style["history"] = style["history"][-100:]
    styles.save(style_name, style)
    with JOURNAL.open("a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def journal(limit: int = 50) -> list[dict]:
    if not JOURNAL.exists():
        return []
    return [json.loads(x) for x in JOURNAL.read_text().splitlines()[-limit:]][::-1]


def scoreboard() -> dict:
    j = journal(1000)
    scores = [e["score"] for e in j if e.get("score") is not None]
    return {"edits_scored": len(scores), "average": round(sum(scores) / len(scores), 2) if scores else None,
            "best": max(scores) if scores else None, "last5": scores[:5]}
