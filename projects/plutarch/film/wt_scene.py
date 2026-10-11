# word timestamps per known line: transcribe each line's slice, map recognised words onto the script words in order
import json, re, numpy as np, soundfile as sf
from faster_whisper import WhisperModel
import sys, os; D = sys.argv[1]
if os.path.exists(D + "/words.json"): sys.exit(0)
L = json.load(open(D + "/lines.json")); a, sr = sf.read(D + "/vo.wav", dtype="float32")
if a.ndim > 1: a = a.mean(1)
if sr != 16000:
    import scipy.signal as ss; a = ss.resample_poly(a, 16000, sr); sr = 16000
m = WhisperModel("medium.en", device="cpu", compute_type="int8")
norm = lambda s: re.sub(r"[^a-z0-9']", "", s.lower())
out = []
for ln in L:
    s0, s1 = max(0, ln["start"] - 0.15), ln["end"] + 0.25
    seg = a[int(s0 * sr):int(s1 * sr)]
    rec = [w for sg in m.transcribe(seg, language="en", word_timestamps=True, beam_size=5)[0] for w in sg.words]
    toks = ln["text"].split(); res = []; j = 0
    for k, tk in enumerate(toks):
        hit = None
        for q in range(j, min(j + 3, len(rec))):
            if norm(rec[q].word) == norm(tk) or (norm(tk) and norm(rec[q].word)[:3] == norm(tk)[:3]): hit = q; break
        if hit is not None: res.append([tk, s0 + rec[hit].start, s0 + rec[hit].end]); j = hit + 1
        else: res.append([tk, None, None])
    # fill misses by interpolation between neighbours / line bounds
    for k, r in enumerate(res):
        if r[1] is None:
            prv = next((res[i][2] for i in range(k - 1, -1, -1) if res[i][1] is not None), ln["start"])
            nxt = next((res[i][1] for i in range(k + 1, len(res)) if res[i][1] is not None), ln["end"])
            gaps = [i for i in range(len(res)) if res[i][1] is None]
            r[1] = prv + 0.02; r[2] = max(r[1] + 0.12, min(nxt - 0.02, r[1] + 0.35))
    miss = sum(1 for r in res if r[1] is None)
    out.append({"i": ln["i"], "voice": ln["voice"], "start": ln["start"], "end": ln["end"], "w": [[t, round(x, 3), round(y, 3)] for t, x, y in res]})
    pass
json.dump(out, open(D + "/words.json", "w"), indent=0)
