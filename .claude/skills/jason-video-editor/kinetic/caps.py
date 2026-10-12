# words.json -> caps.js: caption phrases (word-timed) + hero titles. Also writes text SFX cues -> cues_text.json
import json, re
W = json.load(open("words.json"))
KEY = {"twelve", "screaming", "bucephalus", "watching", "eyes", "shadow", "pounding", "sun", "trembling", "tears",
       "applause", "quieter", "missed", "observer", "do", "evidence", "belief"}
# hero = (line, first word, last word, out time, y, size)
HERO = [(3, 3, 3, 22.2, 840, 120), (12, 0, 3, 83.9, 520, 128), (19, 11, 14, 129.9, 850, 104),
        (22, 0, 4, 146.05, 850, 92), (22, 5, 10, 149.7, 850, 92), (23, 0, 2, 151.6, 850, 112), (25, 4, 8, 172.7, 850, 100)]
hmap = {(h[0], i) for h in HERO for i in range(h[1], h[2] + 1)}
norm = lambda s: re.sub(r"[^a-z']", "", s.lower())
PH, HE = [], []
for ln in W:
    fable = ln["voice"] == "bm_fable"
    # clauses: split at punctuation and at heroes; long clauses split into balanced halves (no orphan words)
    cl, cur = [], []
    for i, (t, s, e) in enumerate(ln["w"]):
        if (ln["i"], i) in hmap:
            if cur: cl.append(cur); cur = []
            continue
        cur.append((t, s, e))
        if re.search(r"[.?!]$", t) or (t.endswith(",") and len(cur) >= 3): cl.append(cur); cur = []
    if cur: cl.append(cur)
    merged = []
    for c in cl:  # glue 1-word clauses onto the previous clause when it stays short
        if merged and (len(c) == 1 or len(merged[-1]) == 1) and len(merged[-1]) + len(c) <= 7: merged[-1] = merged[-1] + c
        else: merged.append(c)
    for c in merged:
        parts = [c] if len(c) <= 7 else [c[:(len(c) + 1) // 2], c[(len(c) + 1) // 2:]]
        for p in parts: PH.append({"f": fable, "w": [[t, s, e, int(norm(t) in KEY and norm(t) != "do")] for t, s, e in p]})
for li, a, b, out, y, size in HERO:
    ws = W[li]["w"][a:b + 1]
    HE.append({"t": ws[0][1], "out": out, "y": y, "size": size, "txt": " ".join(w[0] for w in ws)})
# phrase out: next item's start (phrase or hero) or a 1.8 s hold after its last word; last phrase holds to the end
starts = sorted([p["w"][0][1] for p in PH] + [h["t"] for h in HE])
for p in PH:
    nxt = [s for s in starts if s > p["w"][0][1] + 1e-3]
    end = p["w"][-1][2]
    p["out"] = round(min(nxt[0] - 0.3, end + 1.8) if nxt else 181.5, 3)
    if nxt and nxt[0] - end > 2.4: p["out"] = round(end + 1.8, 3)
PH[-1]["out"] = 181.5
pst = sorted(p["w"][0][1] for p in PH)
for h in HE:
    nx = [x for x in pst if x > h["t"] + 0.1]
    if nx: h["out"] = round(min(h["out"], nx[0] - 0.3), 3)
open("caps.js", "w").write("const PH=" + json.dumps(PH) + ";\nconst HERO=" + json.dumps(HE) + ";\n")
print(len(PH), "phrases;", len(HE), "heroes"); [print(round(p["w"][0][1], 2), p["out"], " ".join(w[0] for w in p["w"])) for p in PH]
# text SFX: a whisper of air on every phrase, a full designed hit on every hero
C = []
for i, p in enumerate(PH):
    C.append(dict(f=round(p["w"][0][1] * 30) - 2, id=["whoosh", "swoosh"][i % 2], role="texture", speed=0.5, db=-9))
for h in HE:
    f = round(h["t"] * 30)
    C += [dict(f=f, id="whoosh", role="whoosh", speed=0.55, db=-3), dict(f=f, id="pack4.ripple_textures", role="texture", db=-4),
          dict(f=f + 16, id="pack3.shine", role="accent", db=-4, tail=True), dict(f=f, id="deep_bass", role="sub", pre=3, db=-8)]
json.dump(C, open("cues_text.json", "w"))
