"""One scene -> scene.js for film.html.  usage: build_scene.py SCENE_INDEX WORKDIR
Needs WORKDIR/sNN/{lines.json,words.json,vo.wav}, WORKDIR/picks.json, WORKDIR/plates/<id>.jpg (+ ar in plates.json)."""
import json, re, sys, os, subprocess
si = int(sys.argv[1]); WD = sys.argv[2]; D = f"{WD}/s{si:02d}"
W = json.load(open(D + "/words.json")); picks = json.load(open(WD + "/picks.json"))[str(si)]
AR = json.load(open(WD + "/plates.json"))
LEN = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", D + "/vo.wav"], capture_output=True, text=True).stdout) + 1.2
ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII"]
TITLE = json.load(open(os.path.join(os.path.dirname(__file__), "scenes.json")))[si]["title"]
PLACE = {0: "Corsica  ·  1780s", 1: "Chaeronea  ·  c. AD 100", 2: "Pella, Macedonia  ·  356 BC", 3: "Pella  ·  c. 345 BC", 5: "Mieza  ·  c. 343 BC",
 6: "Aegae  ·  336 BC", 7: "Corinth  ·  336 BC", 8: "The Granicus  ·  334 BC", 9: "Tarsus  ·  333 BC", 10: "Issus  ·  333 BC", 11: "Siwa, the Libyan desert  ·  331 BC",
 12: "Gaugamela  ·  331 BC", 13: "Babylon  ·  330 BC", 14: "Maracanda  ·  328 BC", 15: "India  ·  326 BC", 16: "Babylon  ·  323 BC", 17: ""}
HEROES = {0: ["Plutarch's Lives.", "As him."], 1: ["He's writing lives."], 2: ["You're the smart one.", "You're the strong one."],
 3: ["My father will leave me nothing great to do."], 5: ["one day, they'll tell stories about me.", "What did you fall asleep next to?"],
 6: ["who are we, here?", "we are the king.", "Who are you when no one has told you?"], 7: ["You're blocking my sun.", "If I were not Alexander, I would be Diogenes."],
 8: ["Remember his face."], 9: ["What do you do?", "You get well."], 10: ["What do you do?", "In front of God, and yourself."],
 11: ["son of Zeus.", "One letter, and a new identity."], 12: ["What do you do?", "I will not steal my victory.", "Identity sleeps."],
 13: ["Then it feels normal."], 14: ["This is the hand that saved you.", "You kill him."], 15: ["What do you do?", "as if every man had drunk."],
 16: ["Alexander died at thirty-two."], 17: ["What did you see me do today?", "Sleep well."]}
DUSTS = {7, 11, 15}
norm = lambda s: re.sub(r"[^a-z0-9']", "", s.lower())
# ── heroes: locate phrase in the word stream
HERO = []
for ph in HEROES.get(si, []):
    toks = [norm(x) for x in ph.split()]
    for ln in W:
        ws = [norm(w[0]) for w in ln["w"]]
        for k in range(len(ws) - len(toks) + 1):
            if ws[k:k + len(toks)] == toks: HERO.append((ln["i"], k, k + len(toks) - 1)); break
        else: continue
        break
    else: print("hero not found:", ph)
# ── captions (same rules as the locked proof)
KEY = {"observer", "evidence", "belief", "identity", "ego", "mask", "god", "achilles", "diogenes", "lives", "lion", "thunderbolt", "king", "sun", "cup", "letter", "truth",
       "applause", "trust", "honour", "shadow", "water", "helmet", "fever", "dagger", "pillow", "candle", "zeus", "cleitus", "porus", "bucephalus", "victory", "significance"}
hmap = {(h[0], i) for h in HERO for i in range(h[1], h[2] + 1)}
PH, HE = [], []
for ln in W:
    fable = ln["voice"] == "bm_fable"; cl, cur = [], []
    for i, (t, s, e) in enumerate(ln["w"]):
        if (ln["i"], i) in hmap:
            if cur: cl.append(cur); cur = []
            continue
        cur.append((t, s, e))
        if re.search(r"[.?!:]$", t) or (t.endswith(",") and len(cur) >= 3): cl.append(cur); cur = []
    if cur: cl.append(cur)
    mg = []
    for c in cl:
        if mg and (len(c) == 1 or len(mg[-1]) == 1) and len(mg[-1]) + len(c) <= 7: mg[-1] = mg[-1] + c
        else: mg.append(c)
    for c in mg:
        parts = [c] if len(c) <= 7 else [c[:(len(c) + 1) // 2], c[(len(c) + 1) // 2:]]
        for p in parts: PH.append({"f": fable, "w": [[t, s, e, int(norm(t).rstrip("'s") in KEY or norm(t) in KEY)] for t, s, e in p]})
for li, a, b in HERO:
    ws = W[li]["w"][a:b + 1]; txt = " ".join(w[0] for w in ws); n = len(txt)
    size = 120 if n < 16 else 104 if n < 26 else 88 if n < 36 else 74
    HE.append({"t": ws[0][1], "out": W[li]["w"][b][2] + 2.2, "y": 520 if txt.startswith("What do you do") else 850, "size": size, "txt": txt})
starts = sorted([p["w"][0][1] for p in PH] + [h["t"] for h in HE])
for p in PH:
    nxt = [s for s in starts if s > p["w"][0][1] + 1e-3]; end = p["w"][-1][2]
    p["out"] = round(min(nxt[0] - 0.3, end + 1.8) if nxt else LEN - 1.6, 3)
pst = sorted(p["w"][0][1] for p in PH)
for h in HE:
    nx = [x for x in pst if x > h["t"] + 0.1]
    h["out"] = round(min(h["out"], nx[0] - 0.3) if nx else min(h["out"] + 3, LEN - 1.6), 3)
# ── shots: plates spread over the scene, cut on line starts, 1.2 s dissolves, alternating push-in / pull-back
lstarts = [ln["start"] for ln in json.load(open(D + "/lines.json"))]
n = len(picks); SH = []; bounds = [0.0]
for k in range(1, n):
    target = LEN * k / n; bounds.append(min(lstarts, key=lambda s: abs(s - target)))
bounds.append(LEN + 0.6); bounds = sorted(set(bounds))
for k in range(len(bounds) - 1):
    p = picks[k % n]; ar = AR[str(p["id"])]; fx, fy = p.get("cfx", p["fx"]), p.get("cfy", p["fy"])
    fx = min(max(fx, 0.12), 0.88); fy = min(max(fy, 0.12), 0.88)
    w = max(2100, 960 / fx, 960 / (1 - fx), 540 / (fy * ar), 540 / ((1 - fy) * ar)) * 1.05
    z0, z1 = (1.0, 1.14) if k % 2 == 0 else (1.12, 1.0)
    SH.append({"img": str(p["id"]), "t0": round(max(0, bounds[k] - 0.6), 3), "t1": round(bounds[k + 1] + 0.6, 3), "x": 960, "y": 540, "w": round(min(w, 4400)),
               "fx": round(fx, 4), "fy": round(fy, 4), "z0": z0, "z1": z1, "pfx": p["fx"], "pfy": p["fy"], "role": p.get("role", "")})
# ── the ball points at each plate's focal point once, landing on a spoken word ~45% into the shot (not the opening establishing plate)
KEYS = []
allw = [(w[1], w[0]) for ln in W for w in ln["w"]]
for k, s in enumerate(SH):
    if k == 0 and len(SH) > 2: continue
    tgt = s["t0"] + 0.45 * (s["t1"] - s["t0"])
    cand = [t for t, _ in allw if s["t0"] + 2.5 < t < s["t1"] - 3.0 and not any(h["t"] - 1.8 < t < h["out"] + 0.6 for h in HE)]
    if not cand: continue
    t = min(cand, key=lambda x: abs(x - tgt))
    if KEYS and t - KEYS[-1]["t"] < 6: continue
    KEYS.append({"t": round(t, 3), "shot": k, "fx": s["pfx"], "fy": s["pfy"], "r": 72})
# ── holds / heartbeat for "What do you do?", the ball goes dark in the banquet
HOLD, BEATS, DARK = [], [], []
for ln in W:
    if ln["w"] and norm(ln["w"][0][0]) == "what" and " ".join(x[0] for x in ln["w"]).startswith("What do you do"):
        HOLD.append([ln["start"] - 2.8, ln["end"] + 3.0]); BEATS.append([ln["start"] - 2.8, ln["start"] - 0.2])
if si == 14:
    t0 = next(ln["start"] for ln in W if "pause to choose" in " ".join(x[0] for x in ln["w"])); DARK.append([t0 - 0.5, LEN + 5])
MICRO = []
if ROMAN[si] if si < len(ROMAN) else "": pass
lab = ("Plutarch's Lives  ·  Alexander" if si == 0 else f"{ROMAN[si]}  ·  " + re.sub(r"^\d+\.\s*|\s*\(IMMERSE\)", "", TITLE)) if si else "Plutarch's Lives  ·  Alexander"
MICRO.append(["A", lab, 0.8, 9.5])
if PLACE.get(si): MICRO.append(["B", PLACE[si], 1.4, 9.5])
fl = [ln for ln in W if ln["voice"] == "bm_fable"]
if fl and si not in (0, 17): MICRO.append(["A", "The Mirror", fl[0]["start"] - 0.4, fl[0]["start"] + 6.5])
DUST = [[0, LEN]] if si in DUSTS else []
js = "const LEN=%s;\nconst SH=%s;\nconst KEYS=%s;\nconst PH=%s;\nconst HERO=%s;\nconst MICRO=%s;\nconst HOLD=%s;\nconst BEATS=%s;\nconst DARK=%s;\nconst DUST=%s;\n" % tuple(
    json.dumps(x) for x in (round(LEN, 3), SH, KEYS, PH, HE, MICRO, HOLD, BEATS, DARK, DUST))
open(D + "/scene.js", "w").write(js)
# text SFX cues for this scene (the locked kinetic-text sound)
C = []
for i, p in enumerate(PH): C.append(dict(f=round(p["w"][0][1] * 30) - 2, id=["whoosh", "swoosh"][i % 2], role="texture", speed=0.5, db=-9))
for h in HE:
    f = round(h["t"] * 30)
    C += [dict(f=f, id="whoosh", role="whoosh", speed=0.55, db=-3), dict(f=f, id="pack4.ripple_textures", role="texture", db=-4),
          dict(f=f + 16, id="pack3.shine", role="accent", db=-4, tail=True), dict(f=f, id="deep_bass", role="sub", pre=3, db=-8)]
for k in KEYS: C.append(dict(f=round(k["t"] * 30), id="ios.ios_tink", role="accent", db=-3))
json.dump(sorted(C, key=lambda c: c["f"]), open(D + "/cues.json", "w"))
print(f"scene {si}: LEN {LEN:.1f}s, {len(SH)} shots, {len(KEYS)} keys, {len(PH)} phrases, {len(HE)} heroes")
