"""Voice against the world: how far the background sits under the narration while he speaks, and how full it is in the gaps."""
import soundfile as sf, numpy as np, json, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
nar, sr = sf.read(f"{R}/audio/narration.wav"); bg, _ = sf.read(f"{R}/audio/sfx_bed_only.wav"); bg = bg.mean(1)
n = min(len(nar), len(bg)); w = sr // 10; k = n // w
vr = np.sqrt((nar[:k*w].reshape(k, w) ** 2).mean(1)); br = np.sqrt((bg[:k*w].reshape(k, w) ** 2).mean(1))
act = vr > 0.02; quiet = vr < 0.003; d = lambda x: 20 * np.log10(x + 1e-9); vref = np.median(d(vr[act]))
snr = d(vr[act]) - d(br[act])
print(f"voice while speaking {vref:.1f} dBFS | background under voice while speaking: median {np.median(snr):.1f} dB, 10th pct {np.percentile(snr, 10):.1f} dB")
print(f"background in the gaps: median {vref - np.median(d(br[quiet])):.1f} dB under the voice, loudest tenth {vref - np.percentile(d(br[quiet]), 90):.1f} dB under")
for s in json.load(open(f"{R}/scenes.json")):
    i0, i1 = int(s["t0"] * 10), int(s["t1"] * 10); q = quiet[i0:i1]; a = act[i0:i1]
    if q.sum() > 3 and a.sum() > 3: print(f"  {s['name']:11s} under voice {np.median(d(vr[i0:i1][a]) - d(br[i0:i1][a])):5.1f} dB   gaps {vref - np.median(d(br[i0:i1][q])):5.1f} dB under the voice")
