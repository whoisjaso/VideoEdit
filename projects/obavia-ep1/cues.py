"""Every named event, derived from the VO word times -> src/data/cues.json (read by Remotion AND mix.py).

    python projects/obavia-ep1/cues.py

Sound palette: native iOS sounds for every UI beat (tink, key, lock, note, success, camera shutter),
subtle story foley underneath (siren chirp, footsteps, pen, heartbeat).
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "src" / "data"
FPS = 30
tl = json.loads((DATA / "timeline.json").read_text())
W = tl["words"]
SHOT = {s["id"]: s for s in tl["shots"]}
S = {k: v["start"] for k, v in SHOT.items()}
E = {k: v["end"] for k, v in SHOT.items()}


def n(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


def at(shot, target, occ=1, end=False):
    k = 0
    for w in W:
        if w["shot"] == shot and n(w["w"]).startswith(target.lower()):
            k += 1
            if k == occ:
                return w["e"] if end else w["s"]
    raise KeyError((shot, target, occ))


events = []


def ev(name, t, sfx=None, gain=0.0, lead=1):
    events.append(dict(name=name, t=round(t, 3), f=int(round(t * FPS)), sfx=sfx, gain=gain, lead=lead))


# --- hook + title
ev("siren", 0.05, "siren", -8, lead=0)
ev("judged", at("hook", "judged"), "ios_tink", -10)
ev("title", S["title"], "ios_note", -8, lead=0)
ev("title_hit", S["title"], "lowhit", -12, lead=0)
# --- problem one: his side
for i, w in enumerate(["paper", "loud", "tank"]):
    ev(f"tagH{i + 1}", at("hispov", w), "pop", -8)
ev("tagH4", at("hispov", "rest"), "thump", -6)
ev("card_danger", S["danger"], "ios_key", -10, lead=0)
ev("cut_danger", S["danger"], "whoosh_soft", -17, lead=1)
ev("dangerB", at("danger", "one"), "whoosh_soft", -12)        # ball dives into the card
LAND = at("danger", "one") + 0.4
ev("seed_land", LAND, "pop", -9)                              # ...and bursts into the grid
# the count-up 0 -> 6,500,000 ticks like a rolling odometer: one soft key per eased tenth, decelerating (same curve as the picture)
def bez(p1x, p1y, p2x, p2y, x):
    lo, hi = 0.0, 1.0
    for _ in range(40):
        m = (lo + hi) / 2
        bx = 3 * (1 - m) ** 2 * m * p1x + 3 * (1 - m) * m * m * p2x + m ** 3
        lo, hi = (m, hi) if bx < x else (lo, m)
    return 3 * (1 - m) ** 2 * m * p1y + 3 * (1 - m) * m * m * p2y + m ** 3
_dur = at("danger", "one", 2) - LAND
_us = [i / 400 for i in range(401)]
_ys = [bez(0.16, 1, 0.3, 1, u) for u in _us]
for k in range(1, 10):
    u = next(u for u, y in zip(_us, _ys) if y >= k / 10)
    ev(f"count{k}", LAND + u * _dur, "tick_soft", -16 - k * 0.6, lead=0)
ev("dot", at("danger", "one", 2), "ios_tink", -8)
ev("dangerC", at("danger", "but"), "lowhit", -10)
# --- problem two: your side
for i, w in enumerate(["power", "quota", "badge"]):
    ev(f"tagY{i + 1}", at("p2", w), "pop", -8)
ev("card_bias", S["bias"], "ios_key", -10, lead=0)
ev("cut_bias", S["bias"], "whoosh_soft", -17, lead=1)
ev("biasB", at("bias", "even"), None)
ev("stamp_bias", at("bias", "prejudice"), "ios_lock", -6)
ev("tenth", at("slice", "tenth"), "shutter", -6, lead=0)
ev("sliceB", at("slice", "what"), None)
# --- rule one: disarm
ev("rule", S["rule"], "ios_note", -8, lead=0)
ev("cut_rule", S["rule"], "whoosh_soft", -17, lead=1)
ev("fear_drain", S["rule"] + 0.9, "whoosh_down", -18, lead=0)       # "the fear" bleeds from red to white
for i, w in enumerate(["hazards", "dome", "window", "hands"]):
    ev(f"toggle{i + 1}", at("disarm", w), "ios_tink", -8)
ev("handbook", at("disarm", "driver"), "ios_key", -12, lead=0)
ev("letsee", at("disarm", "let"), "ios_success", -8)
# --- the approach
t_steps = at("approach", "footsteps")
steps = [t_steps + 0.06 + i * 0.4 for i in range(4)]
for i, t in enumerate(steps):
    ev(f"step{i + 1}", t, "step", -8, lead=0)
ev("danger_tag", S["approach"] + 0.1, "pop", -10)
ev("flashlight", at("approach", "flashlight") + 0.1, "click", -6, lead=0)
ev("drop", at("approach", "drop"), "whoosh_soft", -12)
officer1 = next(c for c in tl["clips"] if c["shot"] == "ask")
ev("officer1", officer1["start"], None)
ev("q_land", officer1["start"] + 0.6, "pop", -12)   # the "?" lands beside him
# --- the question
ev("card_admit", S["admit"], "ios_key", -10, lead=0)
ev("cut_admit", S["admit"], "whoosh_soft", -17, lead=1)
ev("admitB", at("admit", "if", 1), "ios_tink", -10)
ev("admitC", at("admit", "if", 2), "ios_tink", -10)
officer2 = next(c for c in tl["clips"] if c["shot"] == "reg")
ev("officer2", officer2["start"], None)
ev("stamp_expired", at("reg", "expired"), "ios_lock", -5)
# --- the clipboard, the choice
t_clip = at("clip", "clipboard")
pens = [(t_clip + 0.05 + i * 0.7, 0.5) for i in range(3)]
for i, (t, d) in enumerate(pens):
    ev(f"pen{i + 1}", t, "pen", -10, lead=0)
ev("five", at("clip", "five"), "ios_key", -6)
ev("explain", at("choice", "explain"), "ios_tink", -6)
ev("explain_hit", at("choice", "explain"), "lowhit", -12)
ev("apologize", at("choice", "apologize"), "ios_tink", -6)
ev("apologize_hit", at("choice", "apologize"), "lowhit", -12)
ev("blackA", at("black", "one"), "impact", -6)
ev("blackB", at("black", "the"), "thump", -4)
ev("end_btn1", at("end", "explain"), "ios_tink", -8)
ev("end_btn2", at("end", "apologize"), "ios_tink", -8)
ev("part2", at("end", "part"), "ios_note", -8)
ev("part2_siren", at("end", "part") + 0.15, "siren", -17, lead=0)      # callback to the opening chirp: the stop isn't over
ev("part2_chip1", at("end", "part") + 0.3, "ios_tink", -14)
ev("part2_chip2", at("end", "part") + 0.45, "ios_tink", -14)

# HUD: CLOCK 60 -> exactly 0:05 on "Five" -> 0:00 at the black frame; fear 0..10 per side
clock = [[S["title"], 60], [at("clip", "five"), 5], [S["black"], 0]]
fear = dict(
    you=[[0, 6], [S["p2"], 6], [at("p2", "badge"), 7.5], [S["disarm"], 7.5], [E["disarm"], 6], [at("approach", "drop"), 5],
         [S["reg"], 5.5], [S["clip"], 7], [at("clip", "five"), 8], [S["choice"], 9], [S["black"], 10]],
    his=[[0, 5], [S["p1"], 6], [at("hispov", "paper"), 6.5], [at("hispov", "loud"), 7], [at("hispov", "tank"), 7.5],
         [at("hispov", "rest"), 8], [S["disarm"], 8], [at("disarm", "hands"), 7], [at("approach", "drop"), 7], [at("approach", "drop") + 0.6, 4]],
)
hud_shots = ["hook", "p1", "hispov", "p2", "slice", "disarm", "approach", "ask", "reg", "clip", "choice"]

# captions, reference style: 2-3 word chunks, broken at punctuation
phrases = []
for clip in tl["clips"]:
    ws = [w for w in W if w["clip"] == clip["id"]]
    cur = []
    for i, w in enumerate(ws):
        cur.append(w)
        punct = w["w"][-1] in ".,?!" or w["w"].endswith("...")
        left = len(ws) - (i + 1)
        if punct or (len(cur) >= 3 and left != 1):
            phrases.append(cur)
            cur = []
    if cur:
        phrases.append(cur)
caps = [dict(shot=p[0]["shot"], speaker=p[0]["speaker"], s=p[0]["s"], e=p[-1]["e"], words=[dict(w=w["w"], s=w["s"], e=w["e"]) for w in p], accent=[])
        for p in phrases]
for a, b in zip(caps, caps[1:]):
    a["out"] = round(min(b["s"], a["e"] + 0.8), 3)
caps[-1]["out"] = round(caps[-1]["e"] + 0.8, 3)

# reading-ball morphs: the ball leaves the caption on the key word and becomes the thing on the page
morphs = []


def mo(shape, t0, t1, color, x, y, size):
    morphs.append(dict(shape=shape, t0=round(t0, 3), t1=round(t1, 3), color=color, x=x, y=y, size=size))


mo("seed", at("danger", "one"), at("danger", "but") - 0.15, "him", 540, 640, 40)   # ball dives into the card and becomes the grid
mo("stopwatch", at("slice", "tenth") - 0.4, at("slice", "what") - 0.05, "white", 250, 1060, 240)
mo("question", officer1["start"] + 0.2, officer1["start"] + officer1["dur"] + 0.25, "him", 830, 470, 170)
mo("stamp", at("reg", "expired") - 0.4, E["reg"] - 0.1, "stakes", 540, 1100, 260)
mo("timer", at("clip", "five") - 0.4, E["clip"] - 0.1, "stakes", 290, 1050, 280)

out = dict(fps=FPS, events=sorted(events, key=lambda e: e["t"]), steps=steps, pens=pens, clock=clock, fear=fear,
           hud_shots=hud_shots, captions=caps, morphs=morphs, hazard=dict(hz=1.5, spans=[]))
(DATA / "cues.json").write_text(json.dumps(out, indent=1))
print(len(events), "events,", len(caps), "caption chunks,", len(morphs), "morphs")
