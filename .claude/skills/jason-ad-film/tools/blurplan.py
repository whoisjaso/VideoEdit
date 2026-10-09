# blurplan.py SHARPDIR N_FRAMES PLAN.json SPEEDS.json  -> per-frame sample counts from optical flow (240° shutter, ~3 px between samples)
import sys, json, cv2, numpy as np, math
d, N, plan, sp = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
FPS = 60; SH = 240/360
def load(i):
    im = cv2.imread(f"{d}/f{i:04d}.png", cv2.IMREAD_GRAYSCALE); return cv2.resize(im, (270, 480), interpolation=cv2.INTER_AREA)
speeds = [0.0]*N; prev = load(0)
for i in range(1, N):
    cur = load(i)
    fl = cv2.calcOpticalFlowFarneback(prev, cur, None, 0.5, 4, 21, 3, 5, 1.1, 0)
    mag = np.hypot(fl[...,0], fl[...,1]) * 4          # back to 1080-wide px
    diff = np.abs(cur.astype(int) - prev.astype(int)) > 6
    v = float(np.percentile(mag[diff], 99)) if diff.sum() > 50 else 0.0
    speeds[i] = max(speeds[i], v); speeds[i-1] = max(speeds[i-1], v)   # a frame's shutter straddles both neighbours
    prev = cur
P = []
for i in range(N):
    n = 1 if speeds[i] < 2 else max(4, min(32, math.ceil(SH * speeds[i] / 3)))
    for j in range(n):
        t = (i + (SH * ((j + 0.5) / n - 0.5) if n > 1 else 0)) / FPS
        P.append({"o": f"s{i:04d}_{j:02d}.png", "t": max(0, t), "f": i})
json.dump(P, open(plan, "w")); json.dump(speeds, open(sp, "w"))
print("frames", N, "samples", len(P), "max px/f", round(max(speeds), 1), "frames>18px/f", sum(s > 18 for s in speeds), "frames>80px/f", sum(s > 80 for s in speeds))
