"""Finals: audio-only encodes, video muxes, the 9:16 teaser, short sound files, share copies.

    python projects/lead-with-questions/lwq_finish.py [audio] [video] [teaser] [share]
"""
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
WORK = Path("/tmp/lwq")
REN = HERE.parent.parent / "renders" / "lead-with-questions"
AUD = REN / "audio"


def ff(*args):
    subprocess.run(["ffmpeg", "-y", "-v", "error", *args], check=True)


def audio():
    AUD.mkdir(parents=True, exist_ok=True)
    for cut in ("night", "morning"):
        for tag in ("432", "440"):
            for lab in ("HP", "SPK"):
                base = f"STP-LWQ-M-{cut.upper()}-{tag}-{lab}"
                wav = WORK / cut / f"{base}.wav"
                ff("-i", str(wav), "-c:a", "libmp3lame", "-b:a", "320k", "-joint_stereo", "0", "-ar", "48000",
                   str(AUD / f"{base}.mp3"))
                ff("-i", str(wav), "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2", str(AUD / f"{base}.m4a"))
                print("audio", base, flush=True)
    sd = HERE / "deliverables" / "audio"
    sd.mkdir(parents=True, exist_ok=True)
    for p in list((WORK / "night").glob("question_tone_*.wav")) + list((WORK / "morning").glob("question_tone_*.wav")) \
            + list((WORK / "night").glob("singing_bowl_*.wav")) + list((WORK / "morning").glob("bell_*.wav")):
        shutil.copy(p, sd / p.name)


def video():
    for cut in ("night", "morning"):
        for aspect, lab in (("16x9", "HP"), ("9x16", "SPK")):
            v = WORK / cut / f"video-{aspect}.mp4"
            a = WORK / cut / f"STP-LWQ-M-{cut.upper()}-432-{lab}.wav"
            out = REN / f"STP-LWQ-M-{cut.upper()}-{aspect}-1080-432-{lab}.mp4"
            ff("-i", str(v), "-i", str(a), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k",
               "-ar", "48000", "-ac", "2", "-shortest", "-movflags", "+faststart", str(out))
            print("video", out.name, flush=True)


def teaser():
    """60 s from the morning cut: part of M3 + scene 1 of M4, with the session line and the safety line."""
    v = WORK / "morning" / "video-9x16.mp4"
    a = WORK / "morning" / "STP-LWQ-M-MORNING-432-SPK.wav"
    W, H = 1080, 1920
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f1 = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-SemiBold.otf", 46)
    f2 = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-SemiBold.otf", 30)
    for text, f, y in (("Full night + morning sessions on YouTube", f1, int(H * 0.165)),
                       ("Lead With Questions  ·  Stop Thinking Poor", f2, int(H * 0.165) + 64),
                       ("Don't listen while driving. Not medical advice.", f2, int(H * 0.69))):
        w = d.textlength(text, font=f)
        d.rounded_rectangle(((W - w) / 2 - 22, y - 12, (W + w) / 2 + 22, y + f.size + 16), 18, fill=(17, 18, 20, 150))
        d.text(((W - w) / 2, y), text, font=f, fill=(250, 243, 227, 255))
    ov = WORK / "teaser-overlay.png"
    img.save(ov)
    segs = [(165.0, 190.0), (290.0, 324.0)]
    fc = []
    for i, (s, e) in enumerate(segs):
        fc.append(f"[0:v]trim={s}:{e},setpts=PTS-STARTPTS[v{i}]")
        fc.append(f"[1:a]atrim={s}:{e},asetpts=PTS-STARTPTS,afade=t=in:d=0.3,afade=t=out:st={e - s - 0.6}:d=0.6[a{i}]")
    fc.append("[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]")
    fc.append("[v][2:v]overlay=0:0[vo]")
    out = REN / "STP-LWQ-M-TEASER-9x16-1080-432-SPK.mp4"
    ff("-i", str(v), "-i", str(a), "-i", str(ov), "-filter_complex", ";".join(fc), "-map", "[vo]", "-map", "[a]",
       "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "320k",
       "-movflags", "+faststart", str(out))
    print("teaser", out.name)


def share():
    """Copies under 30 MB for chat."""
    sh = WORK / "share"
    sh.mkdir(exist_ok=True)
    for name, secs in (("STP-LWQ-M-NIGHT-16x9-1080-432-HP.mp4", 1680), ("STP-LWQ-M-MORNING-16x9-1080-432-HP.mp4", 630)):
        src = REN / name
        akbps = 64
        vk = int(29e6 * 8 / secs / 1000 - akbps - 6)
        out = sh / name.replace("-1080-", "-share-")
        for p in (1, 2):
            args = ["-i", str(src), "-vf", "scale=854:480,fps=15", "-c:v", "libx264", "-b:v", f"{vk}k", "-pass", str(p),
                    "-passlogfile", str(sh / "pl")]
            if p == 1:
                ff(*args, "-an", "-f", "mp4", "/dev/null")
            else:
                ff(*args, "-c:a", "aac", "-b:a", f"{akbps}k", "-movflags", "+faststart", str(out))
        print("share", out, out.stat().st_size / 1e6, "MB")
    shutil.copy(REN / "STP-LWQ-M-TEASER-9x16-1080-432-SPK.mp4", sh / "STP-LWQ-M-TEASER-9x16.mp4")


if __name__ == "__main__":
    REN.mkdir(parents=True, exist_ok=True)
    steps = sys.argv[1:] or ["audio", "video", "teaser", "share"]
    for s in steps:
        globals()[s]()
