"""Cut the 9:16 film into parts for short-form posting. Every part ends the way the film does:
the line travels home and becomes the E in OLACEO.

  python3 src/parts.py <work dir> [--aspect v]     -> renders/parts/your-brain-is-racist-9x16-partN-<name>.mp4
"""
import sys, os, subprocess, math, argparse
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from timing import TL, ROOT
ap = argparse.ArgumentParser(); ap.add_argument("work"); ap.add_argument("--aspect", default="v"); A = ap.parse_args()
tl = TL(); T, E = tl.T, tl.E; R = "9x16" if A.aspect == "v" else "16x9"
master = f"{ROOT}/../../renders/your-brain-is-racist-{R}-v3.mp4"; out = f"{ROOT}/../../renders/parts"; os.makedirs(out, exist_ok=True); os.makedirs(A.work, exist_ok=True)
PARTS = [("the-script", 0.0, E("iat7") + 0.9), ("the-street", T("st1") - 0.35, E("ch8") + 0.9), ("the-traffic-stop", T("two1") - 0.35, E("news2") + 0.9),
         ("the-other-direction", T("od1") - 0.35, E("od23") + 0.9), ("the-switch", T("sw1") - 0.35, E("sw13") + 0.9), ("the-observer", T("wf1") - 0.35, tl.end)]
SR = 48000; n = int(3.5 * SR); x = np.arange(n) / SR                         # the tail's sound: one soft settle as the mark arrives
tone = (np.sin(2 * np.pi * 220 * x) + 0.5 * np.sin(2 * np.pi * 330 * x)) * np.exp(-((x - 0.95) / 0.09) ** 2) * 0.09
floor = 0.012 * np.sin(2 * np.pi * 55 * x) * np.clip(1 - x / 2.5, 0, 1)
sf.write(f"{A.work}/tail.wav", np.stack([tone + floor] * 2, 1).astype(np.float32), SR)
for i, (name, a, b) in enumerate(PARTS, 1):
    dst = f"{out}/your-brain-is-racist-{R}-part{i}-{name}.mp4"; d = b - a
    fin = "" if i == 1 else "fade=in:st=0:d=0.3,"; afin = "" if i == 1 else "afade=in:st=0:d=0.25,"
    enc = ["-c:v", "libx264", "-preset", "medium", "-crf", "19", "-r", "60", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart",
           "-metadata", f"title=Your brain is racist. So is mine. Part {i}", "-metadata", "artist=olaceo"]
    if i == len(PARTS):
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{a:.3f}", "-t", f"{d:.3f}", "-i", master, "-vf", f"{fin}null", "-af", f"{afin}anull"] + enc + [dst], check=True)
    else:
        tail = f"{A.work}/tail_{A.aspect}_{i}.mp4"
        subprocess.run([sys.executable, f"{ROOT}/src/film.py", "tail", "--aspect", A.aspect, "--t", f"{b:.3f}", "--out", tail], check=True, stderr=subprocess.DEVNULL)
        fc = (f"[0:v]{fin}setsar=1[v0];[0:a]{afin}afade=out:st={d - 0.4:.3f}:d=0.4[a0];[1:v]setsar=1[v1];[v0][a0][v1][2:a]concat=n=2:v=1:a=1[v][a]")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{a:.3f}", "-t", f"{d:.3f}", "-i", master, "-i", tail, "-i", f"{A.work}/tail.wav",
                        "-filter_complex", fc, "-map", "[v]", "-map", "[a]"] + enc + [dst], check=True)
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", dst]))
    print(f"part {i} {name:20s} {int(dur // 60)}:{dur % 60:04.1f}  {os.path.getsize(dst) / 1e6:.0f} MB", flush=True)
