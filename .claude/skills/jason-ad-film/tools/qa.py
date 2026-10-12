# qa.py FRAMEDIR N [accentHex] : forensics on rendered frames (thresholds from the cinetic review loop) + 12 fps contact sheets
import sys, numpy as np, os
from PIL import Image, ImageDraw
d, N = sys.argv[1], int(sys.argv[2]); acc = sys.argv[3] if len(sys.argv) > 3 else "D97757"
AR = np.array([int(acc[i:i+2], 16) for i in (0, 2, 4)], float)
def small(i): return np.asarray(Image.open(f"{d}/f{i:04d}.png").convert("RGB").resize((270, 480), Image.BILINEAR), float)
prev = None; D = []; accent = []
for i in range(N):
    a = small(i)
    if prev is not None: D.append(np.abs(a - prev).mean())
    dist = np.sqrt(((a - AR) ** 2).sum(-1)); accent.append(float((dist < 40).mean() * 100))
    prev = a
D = np.array(D); med = np.median(D)
issues = []
for i in range(1, len(D) - 1):
    loc = np.median(D[max(0, i - 6):i + 7])
    if D[i] > 1.0 and D[i] > 2.5 * loc + 0.3 and not (D[i - 1] > loc and D[i + 1] > loc): issues.append(f"spike/pop at f{i+1} (d={D[i]:.2f}, local {loc:.2f})")
    if D[i] < 0.05 and D[i - 1] > 0.5 and D[i + 1] > 0.5: issues.append(f"stall at f{i+1}")
run = 0
for i, v in enumerate(D):
    run = run + 1 if v < 0.1 else 0
    if run == 49: issues.append(f"frozen hold > 48 f ending near f{i+1}")
first = next((i for i, v in enumerate(D) if v > 0.3), None)
if first is None or first > 60: issues.append(f"still opening: first motion at f{first}")
blink = [i for i, a in enumerate(accent) if a < 0.005]
if blink: issues.append(f"device absent (no accent) on {len(blink)} frames, first f{blink[0]}")
over = [i for i, a in enumerate(accent) if a > 8]
print(f"frames {N} | median d {med:.2f} | p90 {np.percentile(D,90):.2f} | near-still {np.mean(D<0.15)*100:.0f}% | accent mean {np.mean(accent):.2f}% max {max(accent):.1f}% (>8% on {len(over)} f)")
print("\n".join(issues) if issues else "no forensics issues")
# 12 fps sheets, 4 s per sheet
os.makedirs(d + "_sheets", exist_ok=True)
for s0 in range(0, N, 240):
    idx = list(range(s0, min(N, s0 + 240), 5)); cols = 12; w, h = 135, 240
    W = Image.new("RGB", (cols * w, ((len(idx) + cols - 1) // cols) * (h + 12)), (140, 140, 140))
    for k, i in enumerate(idx):
        x, y = (k % cols) * w, (k // cols) * (h + 12)
        W.paste(Image.open(f"{d}/f{i:04d}.png").convert("RGB").resize((w, h)), (x, y)); ImageDraw.Draw(W).text((x + 2, y + h), str(i), fill=(0, 0, 0))
    W.save(f"{d}_sheets/sheet_{s0:04d}.png")
