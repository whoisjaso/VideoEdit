"""Short-form clips (9:16) that sell a Theta session, in Jason's house style.

    python projects/theta-identity/shorts.py shorts-iam.md [name ...]

For each `## name` block in the script:
  1. The hook: a full-screen text slam over the first line, a bass hit on frame 0, shake, motion in the first 15 frames.
  2. Word-by-word captions (Montserrat), 1-3 words a page. Keywords are UPPERCASE on their own line: gold ^,
     green + (wins), red ! (problems). A zoom punch and whoosh on every keyword.
  3. An end card that points to the full session, with a riser into it and a ding.
Voice is generated fresh (fast, dry) through build.py's phoneme pipeline, so the pronunciation gate covers it.
No music in the render: Jason adds a trending track in-app.
"""
import os
import re
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

os.environ.setdefault("THETA_ASPECT", "9x16")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build  # noqa: E402
import numpy as np  # noqa: E402
import soundfile as sf  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

ROOT = HERE.parent.parent
SFX = ROOT / ".claude/skills/jason-video-editor/assets/sfx"
FONTS = ROOT / "kairos/assets/fonts"
SR, FPS, W, H = build.SR, 30, 1080, 1920
F_HOOK = ImageFont.truetype(str(FONTS / "BebasNeue-Regular.ttf"), 185)
F_CAP = ImageFont.truetype(str(FONTS / "Montserrat-ExtraBold.ttf"), 78)
F_KEY = ImageFont.truetype(str(FONTS / "Montserrat-ExtraBold.ttf"), 124)
F_CTA_BIG = ImageFont.truetype(str(FONTS / "BebasNeue-Regular.ttf"), 120)
F_CTA = ImageFont.truetype(str(FONTS / "Montserrat-SemiBold.ttf"), 44)
COLORS = {"^": (255, 210, 74), "+": (43, 227, 122), "!": (255, 59, 59)}
WHITE = (255, 255, 255)
CAP_Y = 1150
LINE_GAP = 0.28


# ---------------------------------------------------------------- script

def parse(path):
    shorts, cur = [], None
    for raw in Path(path).read_text().splitlines():
        line = raw.strip()
        if line.startswith("## "):
            cur = dict(name=line[3:].strip(), voice="am_michael", speed=1.05, hook="", lines=[], cta="")
            shorts.append(cur)
        elif cur is None:
            continue
        elif line.startswith("> "):
            cur["lines"].append(line[2:].strip())
        elif m := re.match(r"(voice|speed|hook|cta):\s*(.*)", line):
            cur[m.group(1)] = float(m.group(2)) if m.group(1) == "speed" else m.group(2).strip()
    return shorts


def words_of(text):
    """[(word, mark)] where mark is '^', '+', '!' or ''."""
    out = []
    for tok in text.split():
        mark = tok[0] if tok[0] in COLORS else ""
        out.append((tok[1:] if mark else tok, mark))
    return out


def plain(text):
    return " ".join(w for w, _ in words_of(text))


# ---------------------------------------------------------------- audio

def load_sfx(name, gain=1.0):
    x, sr = sf.read(SFX / name, dtype="float32")
    if x.ndim > 1:
        x = x.mean(1)
    x = build.resample(x, sr, SR)
    return x / (np.max(np.abs(x)) + 1e-9) * gain


def voice_line(text, speed):
    """Dry, punchy read: build's phoneme TTS with the room reverb trimmed off."""
    x = build.tts(text, speed)
    x = x[: max(1, len(x) - int((build.ROOM_TAIL - 0.25) * SR))]
    fade = np.minimum(1, (len(x) - np.arange(len(x))) / (0.2 * SR))
    return (x * fade).astype(np.float32)


def timeline(short):
    """Voice clips, word timings, keyword hits and the end card time."""
    build.VOICE = short["voice"]
    t = 0.15
    clips, words, keys = [], [], []
    for i, line in enumerate(short["lines"]):
        x = voice_line(plain(line), short["speed"])
        dur = len(x) / SR
        clips.append((t, x))
        ws = words_of(line)
        speech = dur - 0.3
        weights = np.array([len(w) + 2 for w, _ in ws], dtype=float)
        starts = t + 0.04 + np.concatenate([[0], np.cumsum(weights)[:-1]]) / weights.sum() * speech
        for (w, mark), st in zip(ws, starts):
            words.append(dict(t=float(st), w=w, mark=mark, line=i))
            if mark:
                keys.append(float(st))
        t += dur + LINE_GAP
    hook_end = clips[0][0] + len(clips[0][1]) / SR + LINE_GAP * 0.5
    cta_at = t + 0.2
    total = cta_at + 3.2
    return dict(clips=clips, words=words, keys=keys, hook_end=hook_end, cta_at=cta_at, total=total)


def mix(tl):
    n = int(tl["total"] * SR)
    out = np.zeros(n, np.float32)

    def put(x, at, g):
        i = int(at * SR)
        j = min(n, i + len(x))
        if i < n:
            out[i:j] += x[: j - i] * g

    for at, x in tl["clips"]:
        put(x, at, 1.0)
    put(load_sfx("deep_bass.wav"), 0.0, 0.55)              # the hook hits on frame 0
    put(load_sfx("whoosh.wav"), tl["hook_end"] - 0.15, 0.3)
    whoosh = load_sfx("whoosh.wav")
    for k in tl["keys"]:
        put(whoosh, k - 0.12, 0.22)                         # every zoom punch gets a whoosh
    put(load_sfx("riser.wav"), max(0, tl["cta_at"] - 1.6), 0.25)
    put(load_sfx("ding.wav"), tl["cta_at"], 0.35)
    out /= max(1.0, np.max(np.abs(out)) / 0.95)
    return np.stack([out, out], 1)


# ---------------------------------------------------------------- visuals

def pages(words):
    """Group words into caption pages: 1-3 words, a keyword always alone on its own page."""
    out, cur = [], []
    for w in words:
        if w["mark"]:
            if cur:
                out.append(cur)
            out.append([w])
            cur = []
            continue
        if cur and (len(cur) == 3 or cur[-1]["line"] != w["line"] or cur[-1]["w"][-1] in ".?,"):
            out.append(cur)
            cur = []
        cur.append(w)
    if cur:
        out.append(cur)
    return out


def pop(age, dur=0.22):
    """Scale for a word popping in: overshoot then settle."""
    if age < 0:
        return 0.0
    x = min(1.0, age / dur)
    return 1.0 + 0.18 * np.sin(np.pi * x) * (1 - x) + (0.6 * (1 - x) ** 3) * -1


def draw_text(img, xy, text, font, fill, scale=1.0, rot=0.0, glow=True, alpha=1.0):
    if scale <= 0.05 or alpha <= 0.01:
        return
    w = int(font.getlength(text)) + 60
    h = font.size + 60
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    if glow:
        for r in (6, 3):
            d.text((30, 30), text, font=font, fill=(0, 0, 0, int(140 * alpha)), stroke_width=r, stroke_fill=(0, 0, 0, int(90 * alpha)))
    d.text((30, 30), text, font=font, fill=fill + (int(255 * alpha),))
    if scale != 1.0 or rot:
        layer = layer.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.BICUBIC)
        if rot:
            layer = layer.rotate(rot, resample=Image.BICUBIC, expand=True)
    img.alpha_composite(layer, (int(xy[0] - layer.width / 2), int(xy[1] - layer.height / 2)))


def wrap_hook(text, font, width=960):
    toks = words_of(text)
    lines, cur = [], []
    for w, m in toks:
        trial = " ".join(x for x, _ in cur + [(w, m)])
        if cur and font.getlength(trial) > width:
            lines.append(cur)
            cur = []
        cur.append((w, m))
    if cur:
        lines.append(cur)
    return lines


class Renderer:
    def __init__(self, short, tl):
        build.apply_theme("iam")
        self.field = build.Field()
        self.s, self.tl = short, tl
        self.pages = pages(tl["words"])
        self.hook_lines = wrap_hook(short["hook"], F_HOOK)

    def zoom(self, t):
        z = 1.0
        for k in self.tl["keys"]:
            a = t - k
            if 0 <= a < 0.5:
                z = max(z, 1.0 + 0.09 * (np.exp(-a / 0.12) if a > 0.06 else a / 0.06))
        if t < 0.5:
            z = max(z, 1.12 - 0.12 * t / 0.5)   # the hook opens pushed in and settles
        return z

    def frame(self, t):
        tl = self.tl
        lungs = 0.35 + 0.25 * np.sin(2 * np.pi * t / 4.0)
        bright = 0.8
        for k in tl["keys"]:
            if 0 <= t - k < 0.4:
                bright = max(bright, 1.15 - (t - k))
        low = self.field.render(t, lungs, bright, 0.8)
        bg = Image.fromarray(low).resize((W, H), Image.BICUBIC)
        z = self.zoom(t)
        if z > 1.001:
            cw, ch = int(W / z), int(H / z)
            bg = bg.crop(((W - cw) // 2, (H - ch) // 2, (W - cw) // 2 + cw, (H - ch) // 2 + ch)).resize((W, H), Image.BILINEAR)
        img = bg.convert("RGBA")

        # progress bar: a thin gold line across the top
        d = ImageDraw.Draw(img)
        d.rectangle((0, 0, int(W * min(1, t / tl["total"])), 10), fill=(255, 210, 74, 255))

        if t < tl["hook_end"]:
            self.draw_hook(img, t)
        elif t < tl["cta_at"]:
            self.draw_caption(img, t)
        else:
            self.draw_cta(img, t - tl["cta_at"])
        return img.convert("RGB")

    def draw_hook(self, img, t):
        """Each hook line is drawn whole (colored words and all), then slammed in as one piece."""
        shake = 12 * np.exp(-t / 0.18) * np.sin(t * 90)
        n = len(self.hook_lines)
        lh = 178
        y0 = 820 - (n - 1) * lh / 2
        for i, line in enumerate(self.hook_lines):
            age = t - i * 0.12
            if age < 0:
                continue
            sc = 1.35 - 0.35 * min(1, age / 0.18)
            sp = F_HOOK.getlength(" ")
            widths = [F_HOOK.getlength(w) for w, _ in line]
            lw = int(sum(widths) + sp * (len(line) - 1)) + 40
            layer = Image.new("RGBA", (lw, F_HOOK.size + 50), (0, 0, 0, 0))
            d = ImageDraw.Draw(layer)
            x = 20
            for (w, m), wl in zip(line, widths):
                d.text((x, 20), w, font=F_HOOK, fill=(0, 0, 0, 150), stroke_width=7, stroke_fill=(0, 0, 0, 110))
                d.text((x, 20), w, font=F_HOOK, fill=COLORS.get(m, WHITE) + (255,))
                x += wl + sp
            if sc != 1.0:
                layer = layer.resize((int(layer.width * sc), int(layer.height * sc)), Image.BICUBIC)
            img.alpha_composite(layer, (int(W / 2 - layer.width / 2 + shake), int(y0 + i * lh - layer.height / 2)))

    def draw_caption(self, img, t):
        page = None
        for p in self.pages:
            if p[0]["t"] <= t:
                page = p
            else:
                break
        if not page or page[0]["line"] == 0:
            return
        if len(page) == 1 and page[0]["mark"]:
            w = page[0]
            age = t - w["t"]
            sc = pop(age)
            rot = 4 * np.exp(-age / 0.1) * np.sin(age * 60)
            draw_text(img, (W / 2, CAP_Y), w["w"].upper().strip(".,?!"), F_KEY, COLORS[w["mark"]], scale=sc, rot=rot)
            return
        shown = [w for w in page if w["t"] <= t]
        text = " ".join(w["w"] for w in shown)
        total = F_CAP.getlength(" ".join(w["w"] for w in page))
        x = W / 2 - total / 2
        for w in shown:
            wl = F_CAP.getlength(w["w"])
            draw_text(img, (x + wl / 2, CAP_Y), w["w"], F_CAP, WHITE, scale=pop(t - w["t"]))
            x += wl + F_CAP.getlength(" ")
        _ = text

    def draw_cta(self, img, age):
        a = min(1, age / 0.25)
        draw_text(img, (W / 2, 800), "FULL SESSION", F_CTA_BIG, WHITE, scale=pop(age), alpha=a)
        draw_text(img, (W / 2, 920), "ON THE CHANNEL", F_CTA_BIG, (255, 210, 74), scale=pop(age - 0.1), alpha=a)
        draw_text(img, (W / 2, 1060), self.s["cta"], F_CTA, (235, 240, 230), alpha=min(1, max(0, (age - 0.3) / 0.3)), glow=True)


def render_short(args):
    short, out_dir = args
    tl = timeline(short)
    wav = out_dir / f"{short['name']}.wav"
    sf.write(wav, mix(tl), SR, subtype="PCM_16")
    r = Renderer(short, tl)
    out = out_dir / f"short-{short['name']}.mp4"
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
         "-i", "-", "-i", str(wav), "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", str(out)],
        stdin=subprocess.PIPE)
    for i in range(int(tl["total"] * FPS)):
        ff.stdin.write(r.frame(i / FPS).tobytes())
    ff.stdin.close()
    ff.wait()
    return str(out), tl["total"]


def main():
    script = HERE / sys.argv[1]
    only = set(sys.argv[2:])
    shorts = [s for s in parse(script) if not only or s["name"] in only]
    out_dir = ROOT / "renders" / "shorts"
    out_dir.mkdir(parents=True, exist_ok=True)
    for s in shorts:   # voice first, serially (one TTS model), then render in parallel
        timeline(s)
    with ProcessPoolExecutor(min(4, len(shorts))) as ex:
        for out, total in ex.map(render_short, [(s, out_dir) for s in shorts]):
            print(f"wrote {out} ({total:.1f}s)", flush=True)


if __name__ == "__main__":
    main()
