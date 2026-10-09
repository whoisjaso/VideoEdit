# blend.py SAMPLEDIR PLAN.json OUTDIR : float average per frame, TPDF dither, quantise once
import sys, json, numpy as np, os
from PIL import Image
d, plan, out = sys.argv[1], sys.argv[2], sys.argv[3]; os.makedirs(out, exist_ok=True)
P = json.load(open(plan)); by = {}
for p in P: by.setdefault(p["f"], []).append(p["o"])
rng = np.random.default_rng(7)
for f, outs in sorted(by.items()):
    acc = None
    for o in outs:
        a = np.asarray(Image.open(f"{d}/{o}").convert("RGB"), dtype=np.float32)
        acc = a if acc is None else acc + a
    acc /= len(outs)
    if len(outs) > 1: acc += rng.random(acc.shape, dtype=np.float32) - rng.random(acc.shape, dtype=np.float32)
    Image.fromarray(np.clip(np.rint(acc), 0, 255).astype(np.uint8)).save(f"{out}/f{f:04d}.png")
print("blended", len(by))
