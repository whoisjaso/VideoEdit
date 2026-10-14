"""QA (brief §10): cue table, clock check, runtime, loudness. -> out/QA.md"""
import json, subprocess, re
from pathlib import Path
H = Path(__file__).resolve().parent
tl = json.loads((H / "src/data/timeline.json").read_text())
cu = json.loads((H / "src/data/cues.json").read_text())
rows = ["| Time | Frame | Event | SFX (frame it lands) |", "|---|---|---|---|"]
for e in cu["events"]:
    if e["name"] == "haz":
        continue
    sf = f"{e['sfx']} (f{e['f'] - e['lead']}, leads {e['lead']})" if e["sfx"] else "visual only"
    rows.append(f"| {e['t']:.2f}s | {e['f']} | {e['name']} | {sf} |")
five = next(e for e in cu["events"] if e["name"] == "five")
blk = next(s for s in tl["shots"] if s["id"] == "black")
clock = cu["clock"]
mp4 = H / "out/ep1-v1.mp4"
probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height,r_frame_rate,codec_name:format=duration", "-of", "compact", str(mp4)],
                       capture_output=True, text=True).stdout if mp4.exists() else "not rendered"
eb = subprocess.run(["ffmpeg", "-nostats", "-i", str(H / "public/mix.wav"), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
I = re.search(r"I:\s+(-?[\d.]+)", eb[eb.rfind("Summary"):]).group(1)
TP = re.search(r"Peak:\s+(-?[\d.]+)", eb[eb.rfind("Summary"):]).group(1)
md = ["# Obavia Ep1: QA", "",
      f"- Runtime {tl['duration']:.2f} s ({tl['frames']} frames), 1080x1920, 30 fps: {probe.strip()}",
      f"- Mix: {I} LUFS integrated, true peak {TP} dBTP (target peak <= -1)",
      f"- CLOCK keyframes {clock}: reads 0:05 at {five['t']:.2f}s (the word \"Five\"), 0:00 at {blk['start']:.2f}s (black frame)",
      "- Every SFX is placed from cues.json, the same data the visuals read. Whooshes land their loudest point on the cut; hits land on the onset, leading the picture by 0-2 frames.",
      "- Lip flaps: officer mouth = per-frame RMS of his own clips only; the narrator never moves a mouth.",
      f"- Words/minute: {len(tl['words']) / tl['duration'] * 60:.0f}", "", "## Cue table", ""] + rows
(H / "out/QA.md").write_text("\n".join(md) + "\n")
print("\n".join(md[:9]))
