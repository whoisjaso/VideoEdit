"""The prompt library + "say it messy" ideation.

Library: reusable prompts (hooks, edit directions, image prompts, B-roll, titles) stored in
data/library/prompts.json, seeded from the skill's playbook. Enhance: turn rambling speech into a
clear, structured creative brief or a production-ready prompt, grounded in the library and the
style's lessons.
"""
from __future__ import annotations

import json
import re
import time
import uuid

from . import brain, styles
from .config import LIBRARY, SKILL

FILE = LIBRARY / "prompts.json"

STYLE_LOCK = ("vertical 9:16, dark moody editorial photography, desaturated palette with a single warm yellow "
              "(#FFD24A) accent, deep shadows, soft film grain, shallow depth of field, cinematic, magazine quality, "
              "no text, no letters, no logos")

SEED = [
    {"kind": "hook", "title": "Proof + promise", "text": "I took [thing] from [before] to [after]. If you want the same, here are [N] things you need to fix."},
    {"kind": "hook", "title": "Taboo opener", "text": "Nobody wants to say this, but [uncomfortable truth]."},
    {"kind": "hook", "title": "Cold open on the result", "text": "Open on the payoff line ([result]) for 2 seconds, then: \"Here's how.\""},
    {"kind": "hook", "title": "Direct callout", "text": "If you're [specific person] and you keep [specific pain], stop."},
    {"kind": "edit", "title": "The 8.3 standard", "text": "Every sentence gets a designed visual beat. Nouns become full-screen cards, 2-4 hero words behind the speaker, numbers roll, one accent color on a moody grade."},
    {"kind": "edit", "title": "Clean iOS", "text": "Restraint: frosted-glass iOS cards as B-roll, soft spring motion, real iOS sounds 1:1, clean type."},
    {"kind": "edit", "title": "Music-led recap", "text": "Beat-synced kinetic lyric type, film burns, a grade, editorial corner labels."},
    {"kind": "image", "title": "Style lock", "text": STYLE_LOCK},
    {"kind": "image", "title": "Polaroid drop-in", "text": "...as a single instant polaroid photo with white border, lying on a dark surface, slight rotation, " + STYLE_LOCK},
    {"kind": "broll", "title": "Money proof", "text": "Real payment-processor screenshot, cropped to the one metric, from -> to arrow, max 6 elements on screen."},
]


def _load() -> list[dict]:
    if not FILE.exists():
        items = [{"id": uuid.uuid4().hex[:8], "created": time.time(), "uses": 0, **x} for x in SEED]
        FILE.write_text(json.dumps(items, indent=2))
    return json.loads(FILE.read_text())


def library(kind: str | None = None) -> list[dict]:
    return [p for p in _load() if not kind or p["kind"] == kind]


def add(kind: str, title: str, text: str) -> dict:
    items = _load()
    item = {"id": uuid.uuid4().hex[:8], "created": time.time(), "uses": 0, "kind": kind, "title": title, "text": text}
    items.insert(0, item)
    FILE.write_text(json.dumps(items, indent=2))
    return item


def remove(pid: str) -> None:
    FILE.write_text(json.dumps([p for p in _load() if p["id"] != pid], indent=2))


SCHEMA = {
    "type": "object",
    "properties": {
        "vision": {"type": "string"},
        "hook_options": {"type": "array", "items": {"type": "string"}},
        "beats": {"type": "array", "items": {"type": "string"}},
        "edit_direction": {"type": "string"},
        "prompt": {"type": "string"},
        "title": {"type": "string"},
    },
    "required": ["vision", "hook_options", "beats", "edit_direction", "prompt", "title"],
    "additionalProperties": False,
}

TARGETS = {
    "video": "a short-form video concept (what to say, how to open, how to edit it)",
    "image": "an image-generation prompt (150-250 words, one pasteable paragraph, ending with the style lock)",
    "edit": "editing directions for this clip (cuts, captions, sound, graphics, grade)",
    "script": "a tight spoken script in the creator's own voice",
}


def enhance(messy: str, target: str = "video", style_name: str = "jason") -> dict:
    style = styles.get(style_name)
    refs = "\n".join(f"- [{p['kind']}] {p['title']}: {p['text']}" for p in _load()[:30])
    lessons = "\n".join(f"- {x}" for x in style.get("lessons", []))
    playbook = ""
    pb = SKILL / "references" / "playbook.md"
    if pb.exists():
        playbook = pb.read_text()[:30000]
    system = (
        "You turn a creator's messy, spoken ideation into a clear vision and a production-ready result. Keep their voice, "
        "their slang and their conviction; never sanitise it. Be concrete: name the hook, the beats, the visuals, the sounds. "
        f"The output target is {TARGETS.get(target, TARGETS['video'])}; put it in `prompt`.\n\n"
        f"House-style lessons:\n{lessons}\n\nPrompt library (reuse what fits):\n{refs}\n\n"
        f"Editing playbook (decoded from reference reels):\n{playbook}")
    res = brain.ask_json(system, f"Messy idea, as spoken:\n{messy}", SCHEMA, effort="medium", max_tokens=8000)
    if res:
        res["engine"] = "claude"
        return res
    return _offline(messy, target)


def _offline(messy: str, target: str) -> dict:
    """No Claude: clean the speech and drop it into the best-fitting template."""
    text = re.sub(r"\b(um+|uh+|so like|like,|you know,?|i mean,?|kind of|sort of|basically|literally)\s*", "", messy, flags=re.I)
    text = re.sub(r"^(so,?\s+)?(i want (a|to make a) video about (how )?)", "", text.strip(), flags=re.I)
    text = re.sub(r"\s+", " ", text).strip()
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\s+(?:and then|so then)\s+", text) if s.strip()]
    core = sents[0] if sents else text
    hooks = [h["text"].replace("[uncomfortable truth]", core.rstrip(".").lower()) for h in SEED if h["kind"] == "hook"][:3]
    prompt = (f"Vertical 9:16 cinematic editorial photograph. {text} " + STYLE_LOCK) if target == "image" else (
        f"Open on: {core}\nThen: " + " -> ".join(sents[1:5] or ["the argument", "the payoff"]) +
        "\nEdit: the 8.3 standard (gold keywords, punch zooms with whooshes, pop+click on graphics, riser into the payoff, follow CTA).")
    return {"vision": core, "hook_options": hooks, "beats": sents[:6], "edit_direction": SEED[4]["text"],
            "prompt": prompt, "title": " ".join(core.split()[:5]).upper(), "engine": "offline"}
