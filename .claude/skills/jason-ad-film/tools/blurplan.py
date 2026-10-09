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
# hard cuts: a frame whose mean change spikes vs its neighbours. Flow there is meaningless and samples
# must never straddle the cut (that blends two shots into a ghost frame), so clamp the shutter inside the act.
dif = [0.0] + [float(np.abs(load(i).astype(int) - load(i - 1).astype(int)).mean()) for i in range(1, N)]
cuts = set(i for i in range(1, N - 1) if dif[i] > 6 and dif[i] > 3 * max(np.median(dif[max(1, i - 6):i]), np.median(dif[i + 1:i + 7]), 0.5))
for c in cuts:                                   # speed at a cut = its neighbour inside the same act
    speeds[c] = speeds[c + 1] if c + 1 < N else 0
    if c >= 2: speeds[c - 1] = speeds[c - 2]
P = []
for i in range(N):
    n = 1 if speeds[i] < 2 else max(4, min(32, math.ceil(SH * speeds[i] / 3)))
    lo, hi = -SH / 2, SH / 2
    if i in cuts: lo = 0.0                        # first frame of a shot: the shutter opens at the cut
    for j in range(n):
        off = (lo + (hi - lo) * (j + 0.5) / n) if n > 1 else 0.0
        P.append({"o": f"s{i:04d}_n{n:02d}_{j:02d}.png", "t": max(0, (i + off) / FPS), "f": i})
print("cuts", sorted(cuts))
json.dump(P, open(plan, "w")); json.dump(speeds, open(sp, "w"))
print("frames", N, "samples", len(P), "max px/f", round(max(speeds), 1), "frames>18px/f", sum(s > 18 for s in speeds), "frames>80px/f", sum(s > 80 for s in speeds))
