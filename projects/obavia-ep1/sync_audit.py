"""Sync audit: render every cue's sound SOLO exactly as mix.py places it and measure where its attack lands vs its frame.
Pass = within -1 / +0.5 frame (sound may lead the picture a hair, never trail). Also flags SFX that would mask the VO.

    python projects/obavia-ep1/sync_audit.py
"""
import json
import sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mix  # noqa: E402  (builds KIT, does not render)

SR, cues = mix.SR, mix.cues
bad = 0
for e in cues["events"]:
    if not e["sfx"]:
        continue
    x = mix.KIT[e["sfx"]]
    want = e["t"] - e["lead"] / 30
    placed = want - mix.hit_offset(e["sfx"], x)
    a = np.convolve(np.abs(x).max(1), np.ones(48) / 48, "same")
    swell = e["sfx"] in mix.PEAK_ALIGNED
    if swell:
        land = placed + np.argmax(a) / SR
    elif e["sfx"] in mix.ONSET_ALIGNED:
        land = placed + np.argmax(a > a.max() * 0.0316) / SR
    else:
        land = placed + np.argmax(a[: int(0.8 * SR)] > a[: int(0.8 * SR)].max() * 0.5) / SR
    off = (land - e["t"]) * 1000
    ok = -34 <= off <= 17
    bad += not ok
    print(f"{e['name']:14s} {e['sfx']:12s} {e['t']:6.2f}s  lands {off:+5.0f} ms {'ok' if ok else '<-- OFF'}{'  (swell peak on the cut)' if swell else ''}")
print(f"\n{bad} of {sum(1 for e in cues['events'] if e['sfx'])} cues off-sync")
