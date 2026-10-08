"""Reference decoder (methodology §6): visual change events vs audio hit events. Usage: python3 -I scripts/ref_sync.py video.mp4
Prints: visual cuts/motion bursts (frame diff), audio onsets (spectral-flux peaks, with loudness), and nearest pairing offsets."""
import subprocess, sys, numpy as np
f = sys.argv[1]
W, H = 108, 192
raw = subprocess.run(["/usr/bin/ffmpeg", "-v", "error", "-i", f, "-vf", f"fps=30,scale={W}:{H},format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
v = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.float32)
d = np.abs(np.diff(v, axis=0)).mean(axis=(1, 2))
thr = np.median(d) + 4 * (np.percentile(d, 75) - np.median(d) + 0.5)
vis = [i + 1 for i in range(1, len(d) - 1) if d[i] > thr and d[i] >= d[i - 1] and d[i] >= d[i + 1]]
a = np.frombuffer(subprocess.run(["/usr/bin/ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout, np.int16).astype(np.float32)
hop, n = 160, 1024  # 10ms
frames = [a[i:i + n] * np.hanning(n) for i in range(0, len(a) - n, hop)]
S = np.abs(np.fft.rfft(np.array(frames), axis=1))
flux = np.maximum(0, np.diff(np.log1p(S), axis=0)).sum(axis=1)
rms = np.array([10 * np.log10(np.mean(x ** 2) + 1e-9) for x in frames])
ft = np.median(flux) + 3 * np.std(flux)
on = [i + 1 for i in range(2, len(flux) - 2) if flux[i] > ft and flux[i] == flux[i - 2:i + 3].max()]
# spectral centroid tells the SFX family: low = bass/impact, high = click/ui/shimmer
cen = (S * np.arange(S.shape[1])).sum(1) / (S.sum(1) + 1e-9) * (8000 / S.shape[1])
print(f"duration {len(a)/16000:.2f}s  visual events {len(vis)}  audio hits {len(on)}")
print("VISUAL (s):", " ".join(f"{x/30:.2f}" for x in vis))
print("AUDIO  (s, dB, centroid Hz):", " ".join(f"{x/100:.2f}[{rms[x]:.0f},{cen[x]:.0f}]" for x in on))
offs = []
for x in on:
    t = x / 100
    if vis:
        nv = min(vis, key=lambda y: abs(y / 30 - t)); o = t - nv / 30
        if abs(o) < 0.25: offs.append(o)
if offs: print(f"paired {len(offs)}/{len(on)} hits within 250ms of a visual event; median audio-minus-visual {np.median(offs)*1000:.0f} ms")
