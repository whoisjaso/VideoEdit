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
    "you": 0.6, "your": 0.6, "nobody": 2.0, "never": 1.5, "stop": 2.0, "secret": 2.5, "truth": 2.0,
    "why": 1.2, "money": 2.0, "rich": 2.0, "broke": 2.0, "mistake": 2.0, "wrong": 1.5,
    "everyone": 1.5, "nobody's": 2.0, "biggest": 1.5, "god": 1.5, "million": 2.5,
    "dollars": 2.0, "fail": 1.5, "discipline": 1.5, "purpose": 1.5, "ego": 2.0, "problem": 1.5,
    "listen": 1.5, "here's": 1.5, "fear": 1.5, "lie": 2.0, "successful": 1.5, "holding": 1.0, "belief": 1.2,
}
# Thesis openers: the lines a creator builds a video around (cold-open material).
THESIS = [r"\ba lot of (people|y'?all|you)\b", r"\bmost people\b", r"\bthe (only|real|biggest) (thing|reason|problem)\b",
          r"\bthe reason (why )?\b", r"\bnobody\b", r"\bevery single\b", r"\byou (have|need) to\b", r"\byour ego\b",
          r"\bhere'?s (the|why|how)\b", r"\bstop\b", r"\bif you (want|stop)\b", r"\bthe truth\b", r"\bnever\b"]
CONTINUATION = {"and", "but", "so", "because", "or", "then", "cuz", "like", "not", "which", "that", "yourself", "broke",
                "actions", "oftentimes", "also", "too", "even", "you", "they"}
CURSES = {"fuck", "fucking", "shit", "damn", "bitch", "ass", "hell", "motherfucker", "bullshit", "nigga", "niggas"}
MONEY_NUM = re.compile(r"^\$\d|^\d+k$|^(hundred|thousand|million|billion)$")
STOP = {"the", "a", "an", "and", "to", "of", "it", "is", "that", "you", "i", "in", "on", "so", "like", "uh", "um", "just",
        "for", "with", "be", "this", "my", "we", "they", "but", "was", "are", "at", "bro", "your", "if", "me", "do", "don't",
        "i'm", "it's", "that's", "y'all", "nigga", "niggas", "gonna", "about", "because", "what", "when", "all", "really",
        "literally", "can", "have", "not", "he", "she", "them", "said", "say", "get", "got", "know", "think", "there",
        "their", "or", "as", "by", "from", "how", "who", "would", "could", "lot", "people", "fucking", "fuck", "shit",
        "than", "then", "want", "way", "thing", "things", "going", "make", "need", "being", "into", "out", "up", "more"}
DANGLING = {"a", "an", "the", "to", "of", "and", "in", "for", "is", "my", "your", "with", "on", "at", "that", "than",
            "if", "so", "but", "or", "be", "like", "about", "because"}
norm = lambda w: re.sub(r"[^a-z0-9$']", "", w.lower())


def _hook_score(text: str) -> float:
    low = text.lower()
    ws = [norm(w) for w in text.split()]
    s = sum(HOOK_WORDS.get(w, 0) for w in ws[:16])
    s += 2.5 * sum(1 for pat in THESIS if re.search(pat, low))
    s += 1.5 * sum(1 for w in ws[:16] if MONEY_NUM.match(w))
    s += 0.6 * min(2, sum(1 for w in ws[:16] if w in CURSES))
    if text.strip().endswith("?"):
        s += 1.0
    if len(ws) < 4:                        # "Think about it." is not a hook
        s -= 2.0
    return s


def _opens_thought(sents: list[dict], i: int) -> float:
    """Penalty for starting a clip mid-thought."""
    first = norm(sents[i]["text"].split()[0]) if sents[i]["text"] else ""
    pen = 2.5 if first in CONTINUATION else 0.0
    if i > 0:
        prev = sents[i - 1]
        if not prev["text"].rstrip().endswith((".", "?", "!")) and sents[i]["start"] - prev["end"] < 0.8:
            pen += 2.0                     # the previous line runs straight into this one
    return pen


def _topic(text: str) -> str:
    """The idea a clip keeps returning to: its most repeated 1-3 word content phrase."""
    ws = [norm(w) for w in text.split()]
    best, best_n = "", 1
    for n in (3, 2, 1):
        counts: dict[tuple, int] = {}
        for k in range(len(ws) - n + 1):
            g = tuple(ws[k:k + n])
            if g[0] in STOP or g[-1] in STOP or all(x in STOP for x in g) or any(len(x) < 3 for x in g):
                continue
            counts[g] = counts.get(g, 0) + 1
        for g, c in counts.items():
            if c > best_n or (c == best_n and n > len(best.split())):
                best, best_n = " ".join(g), c
        if best_n >= 2 and len(best.split()) >= n:
            break
    return best


def heuristic(words: list[dict], n: int, min_s: float, max_s: float) -> list[dict]:
    sents = to_sentences(words)
    hooks = [_hook_score(s["text"]) for s in sents]
    cands = []
    for i, first in enumerate(sents):
        j = i
        while j < len(sents) and sents[j]["end"] - first["start"] <= max_s:
            dur = sents[j]["end"] - first["start"]
            if dur >= min_s:
                body = " ".join(s["text"] for s in sents[i:j + 1])
                density = len(body.split()) / max(dur, 1)                    # talking, not dead air
                tail_gap = (sents[j + 1]["start"] - sents[j]["end"]) if j + 1 < len(sents) else 2.0
                ends_clean = sents[j]["text"].rstrip().endswith((".", "!", "?"))
                inner = max(hooks[i:j + 1])
                score = (hooks[i] * 1.5 + inner * 0.6 + min(density, 3.5) * 0.8 + min(tail_gap, 1.5) * 1.2
                         + (1.0 if ends_clean else 0) - _opens_thought(sents, i))
                cands.append({"start": first["start"], "end": sents[j]["end"], "score": score, "first": i, "last": j, "text": body})
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
        i, j = p["first"], p["last"]
        best = max(range(i, j + 1), key=lambda k: hooks[k])
        cold = None
        if best != i and hooks[best] > hooks[i] + 2 and sents[best]["end"] - sents[best]["start"] <= 4.5:
            cold = [sents[best]["start"], sents[best]["end"]]                # open loop: strongest line first
        topic = _topic(p["text"])
        if len(topic.split()) >= 2:
            title = topic.upper()
        else:   # one repeated word isn't a title: use the hook's opening, cut before a dangling word
            ws = (sents[best]["text"] if cold else sents[i]["text"]).rstrip(".?!,").split()[:6]
            while len(ws) > 2 and norm(ws[-1]) in DANGLING:
                ws.pop()
            title = " ".join(ws).upper()
        kw = [w for w in topic.split()] if topic else []
        out.append({
            "start": round(p["start"], 2), "end": round(p["end"], 2), "title": title,
            "hook": sents[best]["text"] if cold else sents[i]["text"], "cold_open": cold,
            "why": ("Opens on its strongest line, then plays in order. " if cold else "Opens on a thesis line. ")
                   + (f"Keeps returning to \u201c{topic}\u201d." if topic else "Ends on a clean pause."),
            "score": round(max(0.0, 5 + 4.5 * p["score"] / top), 1), "keywords": kw,
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
            for m in out:
                m["engine"] = "claude"
            return sorted(out, key=lambda m: -m["score"])[:n], "claude"
    return heuristic(words, n, min_s, max_s), "heuristic"
