"""Audio QA gate (ep #4: the cleaned voice silently lost his opening words and nobody noticed until Jason did).
Usage: python3 check_voice.py WORKDIR [max_pause_s=1.0]
  WORKDIR holds cut.mp4 + captions.json (from cut_sections.py).
Fails (exit 1) when any captioned word plays over near-silence (= words on screen, no voice), and lists every
silent stretch longer than max_pause_s inside the cut so long dead spots are seen, not heard by Jason first."""
import json, subprocess, sys
import numpy as np
work = sys.argv[1]; MAXP = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
a = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", f"{work}/cut.mp4", "-ac", "1", "-ar", "8000", "-f", "s16le", "-"],
                                 capture_output=True, check=True).stdout, dtype=np.int16).astype(np.float32)
db = lambda x: 10 * np.log10(np.mean(x ** 2) + 1e-9) if len(x) else -90
caps = [c for c in json.load(open(f"{work}/captions.json")) if not c.get("hide")]
lv = [db(a[int(c["f0"] / 30 * 8000):int(max(c["f1"], c["f0"] + 4) / 30 * 8000)]) for c in caps]
med = float(np.median(lv))
silent = [(c["tag"], c["t"], c["f0"], round(l)) for c, l in zip(caps, lv) if l < med - 30]
win = [db(a[i:i + 800]) for i in range(0, len(a), 800)]  # 0.1s windows
quiet, run, pauses = med - 25, 0, []
for k, l in enumerate(win + [99]):
    if l < quiet: run += 1
    else:
        if run * 0.1 > MAXP: pauses.append((round((k - run) * 0.1, 1), round(run * 0.1, 1)))
        run = 0
print(f"median word level {med:.0f} dB; words with no voice under them: {len(silent)}")
for s in silent: print("  SILENT", s)
print(f"pauses > {MAXP}s (start s, length s):", pauses)
sys.exit(1 if silent else 0)
