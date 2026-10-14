"""Lay the locked script out in time: generate every voice clip, then tune pauses to hit the spec's timestamps.

    python projects/lead-with-questions/lwq_timeline.py night|morning   # -> /tmp/lwq/<cut>/timeline.json

Only pause lengths change (spec §7). IMPACT pauses (after a [TONE]) are never shortened.
"""
import hashlib
import json
import os
import re
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "theta-identity"))
import build                       # noqa: E402  (phonemes + DSP helpers from the theta engine)
from lwq_script import parse       # noqa: E402

SR = 48000
WORK = Path(os.environ.get("LWQ_WORK", "/tmp/lwq"))
MODELS = Path(os.environ.get("KOKORO_MODELS", "/tmp/theta-identity/models"))

VOICE_A = "am_michael"   # [DEFAULT] Kokoro stand-in for Narrator A (ElevenLabs not available here)
VOICE_B = "am_fenrir"    # [DEFAULT] lighter, clearly different timbre for Narrator B
TONE_LEN = 1.2
TONE_GAP = 0.25

CUTS = {
    "night": dict(script=HERE / "script/night-locked.md", total=1680.0, voice_end={"N9": 1540.0},
                  speed={"A": {"N0": .92, "N1": .92, "N2": .9, "N9": .84, "*": .88}, "B": {"*": .88}}),
    "morning": dict(script=HERE / "script/morning-locked.md", total=630.0, voice_end={"M7": 603.0},
                    speed={"A": {"M0": .98, "M1": .98, "M2": .98, "*": 1.06}, "B": {"*": 1.02}}),
}

_kokoro = None


def tts(text, voice, speed):
    """Raw dry clip, 48 kHz mono, trimmed. Cached by phonemes."""
    global _kokoro
    ph = build.phonemes(text)
    key = hashlib.sha1(f"{voice}|{speed}|{ph}".encode()).hexdigest()[:16]
    path = WORK / "tts" / f"{key}.wav"
    if not path.exists():
        if _kokoro is None:
            from kokoro_onnx import Kokoro
            _kokoro = Kokoro(str(MODELS / "kokoro.onnx"), str(MODELS / "voices.bin"))
        s, sr = _kokoro.create(ph, voice=voice, speed=speed, lang="en-us", is_phonemes=True)
        path.parent.mkdir(parents=True, exist_ok=True)
        sf.write(path, s, sr)
    x, sr = sf.read(path, dtype="float32")
    x = build.resample(x, sr, SR)
    idx = np.flatnonzero(np.abs(x) > 0.008)
    if len(idx):
        x = x[max(0, idx[0] - 480): idx[-1] + 1440]
    return x, path.name


def speed_for(cut, role, sid):
    table = CUTS[cut]["speed"]["B" if role == "B" else "A"]
    return table.get(sid.split(".")[0], table["*"])


NUM = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6}
COUNTED = re.compile(r"\btwo\.\.\. three")


def chunks_for(item, cut, sid):
    """Voice clips for one 'say' item. Counted-breath lines split on '...' and land on 1 s beats."""
    voice = VOICE_B if item.role == "B" else VOICE_A
    sp = speed_for(cut, item.role, sid)
    if item.embedded:
        sp = round(sp * 0.94, 3)   # with the -0.75 st resample below: ~10% slower overall
    if sid.split(".")[0] in ("N1", "M1") and COUNTED.search(item.text):
        parts = [p.strip(" .") for p in item.text.split("...") if p.strip(" .")]
        out = []
        for p in parts:
            x, key = tts(p + ".", voice, sp)
            out.append(dict(text=p, key=key, dur=len(x) / SR, beat=NUM.get(p.lower())))
        return out, True
    x, key = tts(item.text, voice, sp)
    if item.embedded:
        x = emb_shift(x)
    return [dict(text=item.text, key=key, dur=len(x) / SR, beat=None)], False


def emb_shift(x):
    """-0.75 semitone (slower playback by resampling)."""
    return build.resample(x, SR, int(round(SR * 2 ** (0.75 / 12))))


def layout(unit, cut, k, t0, prepared):
    """Place a unit's items from t0 with ordinary pauses scaled by k. Returns (events, end, last_speech_end)."""
    ev = []
    t = t0
    last_speech = t0
    prev_line = None
    for item, (chunks, counted) in zip(unit.items, prepared):
        if item.kind == "say":
            if prev_line is not None and item.line != prev_line and ev and ev[-1]["kind"] == "say":
                t += 0.35
            if counted:
                start = t
                first_end = start + chunks[0]["dur"]
                beat = 1
                base = max(start + 1.0, first_end + 0.1)
                cur = start
                breath_kind = "out" if re.match(r"(and )?out", chunks[0]["text"].lower()) else "in"
                for i, c in enumerate(chunks):
                    if i == 0:
                        at = start
                    else:
                        beat = c["beat"] or beat + 1
                        at = max(base + (beat - 2) * 1.0, cur + 0.05)
                    ev.append(dict(kind="say", role=item.role, text=c["text"], key=c["key"], t=at, dur=c["dur"],
                                   emb=False, line=item.line, counted=True))
                    cur = at + c["dur"]
                    beat = max(beat, 1)
                end_breath = max(cur, base + (beat - 1) * 1.0)
                ev.append(dict(kind="breath", phase=breath_kind, t=start, end=end_breath))
                t = cur
            else:
                c = chunks[0]
                ev.append(dict(kind="say", role=item.role, text=c["text"], key=c["key"], t=t, dur=c["dur"],
                               emb=item.embedded, line=item.line, counted=False))
                t += c["dur"] + (0.45 if c["text"].rstrip().endswith("...") else 0.12)
            last_speech = ev[-1]["t"] + ev[-1]["dur"] if ev[-1]["kind"] == "say" else ev[-2]["t"] + ev[-2]["dur"]
            prev_line = item.line
        elif item.kind == "tone":
            ev.append(dict(kind="tone", t=t + TONE_GAP))
            t += TONE_GAP + TONE_LEN
        elif item.kind == "br":
            ev.append(dict(kind="br", t=t + 0.1))
            t += 1.9
        elif item.kind == "pause":
            secs = item.secs * (max(k, 1.0) if item.after_tone else k)
            ev.append(dict(kind="pause", t=t, dur=secs, scripted=item.secs, impact=item.after_tone, line=item.line))
            t += secs
    return ev, t, last_speech


def fit(unit, cut, t0, prepared, voice_end=None):
    """Find the pause scale that makes the unit end on its target (or its voice end on voice_end)."""
    target = (voice_end if voice_end else unit.end) - t0

    def length(k):
        ev, end, last = layout(unit, cut, k, t0, prepared)
        return (last if voice_end else end) - t0

    lo, hi = 0.35, 6.0
    if length(lo) >= target:
        return lo
    if length(hi) <= target:
        return hi
    for _ in range(40):
        mid = (lo + hi) / 2
        if length(mid) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def build_timeline(cut):
    cfg = CUTS[cut]
    sections = parse(cfg["script"])
    out = dict(cut=cut, total=cfg["total"], sections=[], events=[], units=[])
    t = 0.0
    for sec in sections:
        sec_start = t
        for u in sec.units:
            prepared = [chunks_for(it, cut, u.sid) if it.kind == "say" else (None, False) for it in u.items]
            t0 = max(t, u.start) if u.start - t < 10 else u.start   # start on target (pad if early)
            ve = cfg["voice_end"].get(u.sid)
            k = fit(u, cut, t0, prepared, ve)
            ev, end, last = layout(u, cut, k, t0, prepared)
            for e in ev:
                e["unit"] = u.sid
            out["events"] += ev
            first = next(e["t"] for e in ev if e["kind"] == "say")
            out["units"].append(dict(sid=u.sid, title=u.title, label=u.label, target_start=u.start,
                                     target_end=u.end, start=t0, first_voice=first, end=end, voice_end=last, k=round(k, 3)))
            t = end
            if u is sec.units[0]:
                sec_start = t0
        out["sections"].append(dict(sid=sec.sid, title=sec.title, target_start=sec.start, target_end=sec.end,
                                    start=sec_start, end=t))
    return out


if __name__ == "__main__":
    for cut in sys.argv[1:] or ["night", "morning"]:
        tl = build_timeline(cut)
        p = WORK / cut / "timeline.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(tl, indent=1))
        for u in tl["units"]:
            print(f"{cut:8s} {u['sid']:6s} target {u['target_start']:7.1f}-{u['target_end']:7.1f}  "
                  f"actual {u['start']:7.1f}-{u['end']:7.1f}  voice_end {u['voice_end']:7.1f}  k={u['k']}")
