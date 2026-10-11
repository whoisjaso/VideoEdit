"""Moment mining: find the clips worth cutting out of a long video.

With Claude: the whole timestamped transcript + the brief + the style's lessons go in one call,
and Claude returns ranked, self-contained moments with a hook line for each.
Without Claude: a transparent heuristic (hook words, density, payoff, clean boundaries).
Without a transcript: speech-energy windows, so silent-model setups still get clips.
"""
from __future__ import annotations

import re

from . import brain
from .transcribe import sentences as to_sentences

HOOK_WORDS = {
    "you": 1.0, "your": 1.0, "nobody": 2.0, "never": 1.5, "stop": 2.0, "secret": 2.5, "truth": 2.0,
    "why": 1.5, "how": 1.2, "money": 2.0, "rich": 2.0, "broke": 2.0, "mistake": 2.0, "wrong": 1.5,
    "everyone": 1.5, "nobody's": 2.0, "biggest": 1.5, "real": 1.0, "god": 1.5, "million": 2.5,
    "thousand": 1.5, "dollars": 2.0, "fail": 1.5, "win": 1.5, "discipline": 1.5, "purpose": 1.5,
    "listen": 1.5, "here's": 1.5, "this": 0.5, "problem": 1.5, "fear": 1.5, "lie": 2.0,
}
CURSES = {"fuck", "fucking", "shit", "damn", "bitch", "ass", "hell", "motherfucker", "bullshit", "nigga", "niggas"}
NUM = re.compile(r"^\$?\d|^(one|two|three|four|five|six|seven|eight|nine|ten|hundred|thousand|million|billion)$")
PAYOFF = {"so", "that's", "because", "which", "means", "result", "therefore", "and"}


def _hook_score(text: str) -> float:
    ws = [re.sub(r"[^a-z0-9$']", "", w.lower()) for w in text.split()]
    s = sum(HOOK_WORDS.get(w, 0) for w in ws[:14])
    s += 1.5 * sum(1 for w in ws[:14] if NUM.match(w))
    s += 1.0 * sum(1 for w in ws[:14] if w in CURSES)
    if text.strip().endswith("?") or ws[:1] in (["why"], ["how"], ["what"]):
        s += 1.5
    return s


def heuristic(words: list[dict], n: int, min_s: float, max_s: float) -> list[dict]:
    sents = to_sentences(words)
    cands = []
    for i, first in enumerate(sents):
        dur, j = 0.0, i
        while j < len(sents) and sents[j]["end"] - first["start"] <= max_s:
            dur = sents[j]["end"] - first["start"]
            if dur >= min_s:
                body = " ".join(s["text"] for s in sents[i:j + 1])
                nwords = len(body.split())
                density = nwords / max(dur, 1)                     # talking, not dead air
                tail_gap = (sents[j + 1]["start"] - sents[j]["end"]) if j + 1 < len(sents) else 2.0
                score = (_hook_score(first["text"]) * 1.4 + min(density, 3.5) * 1.2 + min(tail_gap, 1.5) * 1.5
                         + sum(1 for s in sents[i:j + 1] if NUM.search(s["text"].split()[0].lower())) * 0.3)
                cands.append({"start": first["start"], "end": sents[j]["end"], "score": score,
                              "first": i, "last": j, "hook": first["text"], "text": body})
            j += 1
    cands.sort(key=lambda c: -c["score"])
    picked: list[dict] = []
    for c in cands:
        if all(c["end"] <= p["start"] or c["start"] >= p["end"] for p in picked):
            picked.append(c)
        if len(picked) >= n:
            break
    top = max((p["score"] for p in picked), default=1) or 1
    out = []
    for p in picked:
        words_in = p["hook"].split()[:6]
        while len(words_in) > 2 and words_in[-1].lower() in {"in", "the", "a", "to", "of", "and", "for", "is", "my", "your", "with", "on", "at"}:
            words_in.pop()
        out.append({
            "start": round(p["start"], 2), "end": round(p["end"], 2),
            "title": " ".join(words_in).upper(),
            "hook": p["hook"], "cold_open": None,
            "why": "Strong opening words, steady talking, ends on a clean pause.",
            "score": round(5 + 4.5 * p["score"] / top, 1), "keywords": [],
        })
    return sorted(out, key=lambda m: -m["score"])


def energy_windows(spans: list[tuple[float, float]], n: int, min_s: float, max_s: float) -> list[dict]:
    """No transcript: pick windows with the most continuous speech, cut on pauses."""
    cands = []
    for i, (a, _) in enumerate(spans):
        talk, j = 0.0, i
        while j < len(spans) and spans[j][1] - a <= max_s:
            talk += spans[j][1] - spans[j][0]
            b = spans[j][1]
            if b - a >= min_s:
                cands.append((talk / (b - a), a, b))
            j += 1
    cands.sort(reverse=True)
    picked = []
    for ratio, a, b in cands:
        if all(b <= p[1] or a >= p[2] for p in picked):
            picked.append((ratio, a, b))
        if len(picked) >= n:
            break
    return [{"start": round(a, 2), "end": round(b, 2), "title": f"MOMENT {k + 1}", "hook": "",
             "cold_open": None, "why": f"{int(r * 100)}% continuous speech, cut on natural pauses.",
             "score": round(5 + 4 * r, 1), "keywords": []} for k, (r, a, b) in enumerate(picked)]


SCHEMA = {
    "type": "object",
    "properties": {
        "moments": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "first_sentence": {"type": "integer"},
                    "last_sentence": {"type": "integer"},
                    "cold_open_sentence": {"type": ["integer", "null"]},
                    "title": {"type": "string"},
                    "hook": {"type": "string"},
                    "why": {"type": "string"},
                    "score": {"type": "number"},
                    "keywords": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["first_sentence", "last_sentence", "cold_open_sentence", "title", "hook",
                             "why", "score", "keywords"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["moments"],
    "additionalProperties": False,
}

SYSTEM = """You are the senior short-form editor for a creator. You read a long video's transcript and pick the
moments that will make the strongest standalone short-form clips (TikTok / Reels / Shorts).

What makes a moment:
- It stands alone: a viewer with no context understands it and gets a payoff.
- Its first sentence is a hook: a bold claim, a taboo, a number, a question, or a direct promise to the viewer.
  If the best hook line sits later in the moment, give it as cold_open_sentence (it plays first, 1.5-3s, then the clip runs in order).
- It keeps the speaker's logic order: hook -> problem -> argument -> payoff. Never a fragment that ends mid-thought.
- It ends on a landed line, not a trailing "and so...".

Rules from the creator's house style:
{lessons}

Captions are raw: never censor, soften or "correct" slang or curses. Titles are 2-6 words, uppercase-friendly.
score is 0-10, your honest prediction of how hard the clip hits. keywords: 3-6 exact words from the clip that carry the idea."""


def mine(words: list[dict], n: int = 5, min_s: float = 20, max_s: float = 60, brief: str = "",
         style: dict | None = None, speech: list[tuple[float, float]] | None = None) -> tuple[list[dict], str]:
    """Returns (moments, engine_used)."""
    if not words:
        return energy_windows(speech or [], n, min_s, max_s), "energy"
    sents = to_sentences(words)
    lessons = "\n".join(f"- {x}" for x in (style or {}).get("lessons", []))
    lines = "\n".join(f"[{s['i']}] {s['start']:.1f}-{s['end']:.1f} {s['text']}" for s in sents)
    user = (f"Brief from the creator: {brief or '(none)'}\n"
            f"Find the best {n} moments, each {min_s:.0f}-{max_s:.0f} seconds long, non-overlapping.\n\n"
            f"Transcript (sentence index, start-end seconds, words):\n{lines}")
    res = brain.ask_json(SYSTEM.format(lessons=lessons or "- (none yet)"), user, SCHEMA, effort="high")
    if res and res.get("moments"):
        out = []
        for m in res["moments"]:
            a, b = m["first_sentence"], m["last_sentence"]
            if not (0 <= a <= b < len(sents)):
                continue
            co = m.get("cold_open_sentence")
            out.append({
                "start": sents[a]["start"], "end": sents[b]["end"], "title": m["title"], "hook": m["hook"],
                "cold_open": ([sents[co]["start"], sents[co]["end"]] if isinstance(co, int) and 0 <= co < len(sents) and co != a else None),
                "why": m["why"], "score": max(0.0, min(10.0, float(m["score"]))), "keywords": m["keywords"],
            })
        if out:
            return sorted(out, key=lambda m: -m["score"])[:n], "claude"
    return heuristic(words, n, min_s, max_s), "heuristic"
