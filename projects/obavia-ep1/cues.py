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
ev("title_hit", S["title"], "lowhit", -10, lead=0)
# --- problem one: his side
ev("p1_tag", S["p1"] + 0.05, "ios_tink", -10)
for i, w in enumerate(["paper", "loud", "tank"]):
    ev(f"tagH{i + 1}", at("hispov", w), "pop", -8)
ev("tagH4", at("hispov", "rest"), "thump", -6)
ev("card_danger", S["danger"], "ios_key", -10, lead=0)
ev("dangerB", at("danger", "one"), None)
ev("dot", at("danger", "one", 2), "ios_tink", -8)
ev("dangerC", at("danger", "but"), "lowhit", -6)
# --- problem two: your side
ev("p2_tag", S["p2"] + 0.05, "ios_tink", -10)
for i, w in enumerate(["power", "quota", "badge"]):
    ev(f"tagY{i + 1}", at("p2", w), "pop", -8)
ev("card_bias", S["bias"], "ios_key", -10, lead=0)
ev("biasB", at("bias", "even"), None)
ev("stamp_bias", at("bias", "prejudice"), "ios_lock", -6)
ev("tenth", at("slice", "tenth"), "shutter", -6, lead=0)
ev("sliceB", at("slice", "what"), None)
# --- rule one: disarm
ev("rule", S["rule"], "ios_note", -8, lead=0)
for i, w in enumerate(["hazards", "dome", "window", "hands"]):
    ev(f"toggle{i + 1}", at("disarm", w), "ios_tink", -8)
ev("handbook", at("disarm", "driver"), "ios_key", -12, lead=0)
ev("letsee", at("disarm", "let"), "ios_success", -8)
# --- the approach
t_steps = at("approach", "footsteps")
steps = [t_steps + 0.06 + i * 0.4 for i in range(4)]
for i, t in enumerate(steps):
    ev(f"step{i + 1}", t, "step", -8, lead=0)
ev("flashlight", at("approach", "flashlight") + 0.1, "click", -6, lead=0)
ev("drop", at("approach", "drop"), "whoosh_soft", -12)
officer1 = next(c for c in tl["clips"] if c["shot"] == "ask")
ev("officer1", officer1["start"], None)
# --- the question
ev("card_admit", S["admit"], "ios_key", -10, lead=0)
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


mo("dot", at("danger", "one", 2), at("danger", "but") - 0.1, "pink", 540, 860, 40)
mo("stopwatch", at("slice", "tenth") - 0.3, at("slice", "what") - 0.05, "white", 250, 1060, 240)
mo("question", officer1["start"] + 0.2, officer1["start"] + officer1["dur"] + 0.25, "pink", 830, 470, 170)
mo("stamp", at("reg", "expired"), E["reg"] - 0.1, "pink", 540, 1100, 260)
mo("timer", at("clip", "five"), E["clip"] - 0.1, "pink", 290, 1050, 280)

out = dict(fps=FPS, events=sorted(events, key=lambda e: e["t"]), steps=steps, pens=pens, clock=clock, fear=fear,
           hud_shots=hud_shots, captions=caps, morphs=morphs, hazard=dict(hz=1.5, spans=[]))
(DATA / "cues.json").write_text(json.dumps(out, indent=1))
print(len(events), "events,", len(caps), "caption chunks,", len(morphs), "morphs")
