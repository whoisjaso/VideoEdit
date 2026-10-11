"""Narrate every scene of scenes.json -> OUT/sNN/vo.wav + lines.json (Kokoro, George/Fable, speed 0.82, sleep pace).
usage: python3 voice.py OUT [scene ...]   (scene 4 = the Bucephalus proof, reused)"""
import sys, os, json, numpy as np, soundfile as sf
from kokoro import KPipeline
SR = 24000; pipe = KPipeline(lang_code="b")
OUT = sys.argv[1]; S = json.load(open(os.path.join(os.path.dirname(__file__), "scenes.json")))
want = [int(x) for x in sys.argv[2:]] or [i for i in range(len(S)) if i != 4]
for si in want:
    d = f"{OUT}/s{si:02d}"; os.makedirs(d, exist_ok=True)
    if os.path.exists(d + "/lines.json"): print("skip", si); continue
    L = S[si]["lines"]; out = [np.zeros(int(SR * 1.8), np.float32)]; t = 1.8; meta = []
    for i, l in enumerate(L):
        a = np.concatenate([x for _, _, x in pipe(l["text"], voice=l["voice"], speed=0.82)]).astype(np.float32)
        meta.append(dict(i=i, voice=l["voice"], text=l["text"], start=round(t, 3), end=round(t + len(a) / SR, 3)))
        out.append(a); t += len(a) / SR
        gap = l["pause"] + (1.0 if i + 1 < len(L) and L[i + 1]["voice"] != l["voice"] else 0)
        out.append(np.zeros(int(SR * gap), np.float32)); t += gap
    sf.write(d + "/vo.wav", np.concatenate(out), SR); json.dump(meta, open(d + "/lines.json", "w"), indent=1)
    print(si, S[si]["title"], round(t, 1), "s", flush=True)
