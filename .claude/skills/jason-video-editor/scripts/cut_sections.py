"""The 8.3 cut (episode #3 method), generalised: cut that respects Jason's pauses.
Usage: python3 cut_sections.py sections.json OUTDIR
  -> OUTDIR/cut.mp4 (1080x1920, 30fps), OUTDIR/edl.json, OUTDIR/captions.json   (FORCE=1 re-renders cached pieces)

sections.json (paths relative to the json file):
  {"sources": {"p1": {"video": "p1.mov", "audio": "p1_voice.wav", "words": "p1c/words.json"}},
   "gap_max": 1.4, "gap_keep": 0.75,          # only dead air > gap_max is shortened, to gap_keep (his pauses stay)
   "alias": {"psycho": "cycle"},              # recognizer mis-hear -> confirmed word (aligns captions to timing)
   "snap": 0.08,                              # cut points snap to the quietest spot within +/-80ms (0 = off)
   "keep": [["p1", 0.62, 10.45, "Exact confirmed words ...", "hook"], ...]}   # in HIS order; tag = section name
                                              # optional 6th field {"snap": 0}: keep this piece's cut points exact (word splices)
Caption markup inside the text: ^gold  +green  !red   {words} = caption hidden (a graphic carries those words).
Video comes from the phone clip, audio from the enhanced voice track (scripts/voice_enhance.py)."""
import json, os, re, subprocess, sys, difflib
from itertools import groupby

cfg_path, OUT = sys.argv[1], sys.argv[2]
BASE = os.path.dirname(os.path.abspath(cfg_path))
cfg = json.load(open(cfg_path))
P = lambda x: x if os.path.isabs(x) else os.path.join(BASE, x)
SRC = {k: (P(v["video"]), P(v["audio"])) for k, v in cfg["sources"].items()}
WORDS = {k: json.load(open(P(v["words"]))) for k, v in cfg["sources"].items()}
GAP_MAX, GAP_KEEP = cfg.get("gap_max", 1.4), cfg.get("gap_keep", 0.75)
ALIAS = cfg.get("alias", {})
KEEP = [tuple(x) for x in cfg["keep"]]
FPS = 30
os.makedirs(f"{OUT}/pieces", exist_ok=True)

def spans(p, a, b):
    ws = [x for x in WORDS[p] if x["start"] >= a - 0.05 and x["end"] <= b + 0.05]
    out, t = [], a
    for x, y in zip(ws, ws[1:]):
        if y["start"] - x["end"] > GAP_MAX:
            h = GAP_KEEP / 2; out.append((t, x["end"] + h)); t = y["start"] - h
    out.append((t, b)); return out

OPTS = {k: (row[5] if len(row) > 5 else {}) for k, row in enumerate(KEEP)}   # optional 6th field, e.g. {"snap": 0} for an exact word splice
KEEP = [row[:5] for row in KEEP]
pieces = [(p, a, b, tag, k) for k, (p, a0, b0, txt, tag) in enumerate(KEEP) for a, b in spans(p, a0, b0)]

# snap every cut point to the quietest 10ms within +/-SNAP s, so a splice never clips a word (ep #4 word-level splices)
SNAP = cfg.get("snap", 0.08)
if SNAP:
    import numpy as np
    def load(path):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", "8000", "-f", "s16le", "-"], capture_output=True, check=True).stdout
        return np.frombuffer(raw, dtype=np.int16).astype(np.float32)
    AUD = {k: load(v[1]) for k, v in SRC.items()}
    def quiet(p, t):
        x, sr, w = AUD[p], 8000, 80
        best, bt = None, t
        for d in np.arange(-SNAP, SNAP + 1e-9, 0.005):
            i = int((t + d) * sr)
            if i - w < 0 or i + w > len(x): continue
            e = float(np.mean(x[i - w:i + w] ** 2))
            if best is None or e < best - 1e-6 or (abs(e - best) <= 1e-6 and abs(d) < abs(bt - t)): best, bt = e, t + d
        return max(0.0, bt)
    pieces = [(p, a, b, tag, k) if OPTS[k].get("snap", 1) == 0 else (p, quiet(p, a), quiet(p, b), tag, k) for p, a, b, tag, k in pieces]
edl, f = [], 0
for i, (p, a, b, tag, k) in enumerate(pieces):
    out = f"{OUT}/pieces/q{i:03d}.mp4"; d = b - a; N = round(d * FPS); T = N / FPS; vsrc, asrc = SRC[p]
    if not os.path.exists(out) or os.environ.get("FORCE"):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a), "-t", str(d + 0.5), "-i", vsrc, "-ss", str(a), "-t", str(d + 0.5), "-i", asrc,
            "-filter_complex", f"[0:v]scale=1080:1920:flags=lanczos,setpts=PTS-STARTPTS,fps={FPS},tpad=stop=10:stop_mode=clone,trim=end_frame={N},setpts=N/{FPS}/TB[v];"
            f"[1:a]atrim=0:{d},asetpts=PTS-STARTPTS,apad,atrim=0:{T},afade=t=in:d=0.015,afade=t=out:st={T-0.03}:d=0.03[a]",
            "-map", "[v]", "-map", "[a]", "-r", str(FPS), "-c:v", "libx264", "-crf", "15", "-preset", "fast", "-pix_fmt", "yuv420p",
            "-c:a", "pcm_s16le", "-ar", "48000", out], check=True, timeout=300)
    edl.append({"p": p, "a": a, "b": b, "speed": 1, "tag": tag, "k": k, "f0": f, "f1": f + N}); f += N

ins, fc = [], ""
for i in range(len(pieces)): ins += ["-i", f"{OUT}/pieces/q{i:03d}.mp4"]; fc += f"[{i}:v][{i}:a]"
subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", fc + f"concat=n={len(pieces)}:v=1:a=1[v][a]", "-map", "[v]", "-map", "[a]", "-r", str(FPS),
    "-c:v", "libx264", "-crf", "15", "-preset", "fast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", f"{OUT}/cut.mp4"], check=True)
json.dump(edl, open(f"{OUT}/edl.json", "w"), indent=0)

def mapt(t, k):
    for e in edl:
        if e["k"] == k and e["a"] - 1e-6 <= t <= e["b"] + 1e-6: return e["f0"] + (t - e["a"]) * FPS
    for e in edl:
        if e["k"] == k and e["a"] >= t: return e["f0"]
    return [e for e in edl if e["k"] == k][-1]["f1"]

norm = lambda s: re.sub(r"[^a-z0-9']", "", s.lower())
TONE = {"!": "red", "+": "green", "^": "gold"}
caps = []
for k, (p, a, b, txt, tag) in enumerate(KEEP):
    vw = [x for x in WORDS[p] if x["start"] >= a - 0.05 and x["end"] <= b + 0.05]
    hidden, toks = set(), []
    for m in re.finditer(r"\{([^}]*)\}|(\S+)", txt):
        if m.group(1) is not None:
            for wd in m.group(1).split(): hidden.add(len(toks)); toks.append(wd)
        else: toks.append(m.group(2))
    vn = [norm(x["word"]) for x in vw]; cn = [norm(c.lstrip("!+^")) for c in toks]
    vn2 = [ALIAS.get(v, v) if v not in cn else v for v in vn]
    tim = [None] * len(toks)
    for blk in difflib.SequenceMatcher(None, cn, vn2, autojunk=False).get_matching_blocks():
        for j in range(blk.size): tim[blk.a + j] = (vw[blk.b + j]["start"], vw[blk.b + j]["end"])
    known = [(i, t) for i, t in enumerate(tim) if t]
    starts = []
    for i in range(len(toks)):  # unmatched words: spread evenly between their matched neighbours
        if tim[i]: starts.append(max(a, tim[i][0])); continue
        pv = max([q for q in known if q[0] < i], default=None, key=lambda z: z[0]); nx = min([q for q in known if q[0] > i], default=None, key=lambda z: z[0])
        s0 = pv[1][1] if pv else a; s1 = nx[1][0] if nx else b; n0 = pv[0] if pv else -1; n1 = nx[0] if nx else len(toks)
        starts.append(s0 + (s1 - s0) * (i - n0) / (n1 - n0))
    for i, c in enumerate(toks):
        s = min(max(starts[i], a), b - 0.01); e = starts[i + 1] if i + 1 < len(toks) else b
        mark = c[0] if c[0] in TONE else ""; word = c.lstrip("!+^")
        caps.append({"k": k, "t": word.upper(), "f0": round(mapt(s, k)), "f1": round(mapt(min(max(e, s + 0.05), b), k)),
                     "emph": bool(mark), "tone": TONE.get(mark, "gold"), "curse": False, "hide": i in hidden, "tag": tag, "end": i == len(toks) - 1})
for k, grp in groupby(range(len(caps)), key=lambda i: caps[i]["k"]):  # no two words pop on the same frame
    idx = list(grp)
    for j in range(1, len(idx) - 1):
        a_, b_, n_ = caps[idx[j - 1]], caps[idx[j]], caps[idx[j + 1]]
        if (b_["f0"] - a_["f0"] >= 8 and n_["f0"] - b_["f0"] <= 1) or (b_["f0"] - a_["f0"] <= 0 and n_["f0"] - b_["f0"] >= 8):
            b_["f0"] = round((a_["f0"] + n_["f0"]) / 2)
    for j in range(len(idx) - 1): caps[idx[j]]["f1"] = max(caps[idx[j]]["f0"] + 2, min(caps[idx[j]]["f1"], caps[idx[j + 1]]["f0"] + 6))
json.dump(caps, open(f"{OUT}/captions.json", "w"), indent=0)
print("frames", f, round(f / FPS, 1), "pieces", len(pieces), "words", len(caps))
