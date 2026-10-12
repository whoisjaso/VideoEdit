"""Theta Identity: builds the guided breathing + identity-installation videos.

    python projects/theta-identity/build.py night     # Wim Hof rounds -> slow-breath bridge -> identity -> sleep
    python projects/theta-identity/build.py morning   # identity on waking -> Wim Hof rounds -> get up

Everything is generated here: the voice (Kokoro, local), the breath pacing sounds, the bells,
the drone and the binaural theta bed, and every frame. Edit script.md and run it again.
Needs: ffmpeg, numpy, pillow, soundfile, kokoro-onnx (+ its model files, see MODELS below).
"""
import hashlib
import os
import re
import subprocess
import sys
from collections import OrderedDict
from pathlib import Path

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
CACHE = Path(os.environ.get("THETA_CACHE", "/tmp/theta-identity"))
MODELS = Path(os.environ.get("KOKORO_MODELS", CACHE / "models"))
VOICE = os.environ.get("THETA_VOICE", "am_michael")

SR = 48000
FPS = 15
W, H = 1080, 1920
CX, CY = W // 2, 860

# Wim Hof pacing (beginner): 30 breaths a round, ~3.3 s a breath.
T_IN, T_OUT = 1.8, 1.5
BREATHS = 30
RECOVER_HOLD = 15

FONT_DIR = Path("/usr/share/fonts/opentype/inter")
F_NUM = ImageFont.truetype(str(FONT_DIR / "InterDisplay-Light.otf"), 210)
F_NUM_S = ImageFont.truetype(str(FONT_DIR / "InterDisplay-Light.otf"), 170)
F_TEXT = ImageFont.truetype(str(FONT_DIR / "InterDisplay-Light.otf"), 66)
F_TITLE = ImageFont.truetype(str(FONT_DIR / "InterDisplay-Light.otf"), 92)
F_LABEL = ImageFont.truetype(str(FONT_DIR / "Inter-Medium.otf"), 34)
F_SMALL = ImageFont.truetype(str(FONT_DIR / "Inter-Light.otf"), 34)


# ---------------------------------------------------------------- script

def parse_script():
    """Returns {block: [items]} where an item is ('say'|'narr', text) or ('gap', secs) or ('break',)."""
    blocks, cur = {}, None
    for raw in (HERE / "script.md").read_text().splitlines():
        line = raw.strip()
        if line.startswith("# "):
            name = line[2:].strip()
            cur = blocks.setdefault(name, []) if re.fullmatch(r"[A-Z_]+", name) else None
            continue
        if cur is None:
            continue
        if not line:
            if cur and cur[-1] != ("break",):
                cur.append(("break",))
        elif line.startswith("> "):
            cur.append(("say", line[2:].strip()))
        elif line.startswith("~ "):
            cur.append(("narr", line[2:].strip()))
        elif m := re.fullmatch(r"\[(\d+(?:\.\d+)?)\]", line):
            cur.append(("gap", float(m.group(1))))
    return blocks


def split_scenes(items):
    scenes, cur = [], []
    for it in items:
        if it == ("break",):
            if cur:
                scenes.append(cur)
            cur = []
        else:
            cur.append(it)
    if cur:
        scenes.append(cur)
    return scenes


# ---------------------------------------------------------------- audio

_kokoro = None


def tts(text, speed):
    key = hashlib.sha1(f"{VOICE}|{speed}|{text}".encode()).hexdigest()[:16]
    path = CACHE / "tts" / f"{key}.wav"
    if not path.exists():
        global _kokoro
        if _kokoro is None:
            from kokoro_onnx import Kokoro
            _kokoro = Kokoro(str(MODELS / "kokoro.onnx"), str(MODELS / "voices.bin"))
        samples, sr = _kokoro.create(text, voice=VOICE, speed=speed, lang="en-us")
        path.parent.mkdir(parents=True, exist_ok=True)
        sf.write(path, samples, sr)
    x, sr = sf.read(path, dtype="float32")
    x = resample(x, sr, SR)
    # trim silence the model leaves at the ends
    idx = np.flatnonzero(np.abs(x) > 0.01)
    if len(idx):
        x = x[max(0, idx[0] - 800): idx[-1] + 2400]
    return voice_fx(x)


def resample(x, sr_in, sr_out):
    if sr_in == sr_out:
        return x
    n_out = int(round(len(x) * sr_out / sr_in))
    spec = np.fft.rfft(x)
    out = np.zeros(n_out // 2 + 1, dtype=complex)
    k = min(len(spec), len(out))
    out[:k] = spec[:k]
    return (np.fft.irfft(out, n_out) * (n_out / len(x))).astype(np.float32)


_IR = None


def voice_fx(x):
    """Warm it up a touch and put it in a soft room."""
    global _IR
    if _IR is None:
        rng = np.random.default_rng(7)
        n = int(SR * 1.6)
        t = np.arange(n) / SR
        _IR = (rng.standard_normal(n) * np.exp(-t / 0.35)).astype(np.float32)
        _IR = lowpass(_IR, 3500)
        _IR /= np.sqrt(np.sum(_IR ** 2))
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.9
    n = len(x) + len(_IR) - 1
    wet = np.fft.irfft(np.fft.rfft(x, n) * np.fft.rfft(_IR, n), n)[:n].astype(np.float32)
    dry = np.pad(x, (0, len(_IR) - 1))
    return dry * 0.88 + wet * 0.22


def shape(x, lo, hi):
    spec = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    spec *= ((f >= lo) & (f <= hi)) * 1.0 / np.sqrt(np.maximum(f, 20) / 200)
    return np.fft.irfft(spec, len(x)).astype(np.float32)


def lowpass(x, hi):
    spec = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    spec *= 1 / (1 + (f / hi) ** 4)
    return np.fft.irfft(spec, len(x)).astype(np.float32)


def breath_sound(dur, inhale, seed):
    """Air through the nose plus a soft gliding tone: rises on the way in, falls on the way out."""
    n = int(dur * SR)
    t = np.linspace(0, 1, n, endpoint=False)
    noise = np.random.default_rng(seed).standard_normal(n).astype(np.float32)
    if inhale:
        air = shape(noise, 400, 3200)
        env = np.sin(np.pi * t ** 0.8) ** 1.5
        f0, f1 = 196.0, 293.7
    else:
        air = shape(noise, 150, 1400)
        env = np.sin(np.pi * t ** 1.35) ** 1.5
        f0, f1 = 293.7, 196.0
    air = air / (np.max(np.abs(air)) + 1e-9)
    freq = f0 + (f1 - f0) * (0.5 - 0.5 * np.cos(np.pi * t))
    tone = np.sin(2 * np.pi * np.cumsum(freq) / SR) + 0.3 * np.sin(4 * np.pi * np.cumsum(freq) / SR)
    return (air * 0.32 + tone * 0.12) * env


def bell(freq=528.0, dur=6.0, gain=0.25):
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n, dtype=np.float32)
    for ratio, amp, tau in ((1, 1, 2.6), (2.76, 0.45, 1.3), (5.4, 0.2, 0.7), (8.93, 0.08, 0.35)):
        out += amp * np.sin(2 * np.pi * freq * ratio * t) * np.exp(-t / tau)
    out *= np.minimum(1, t / 0.004)
    return out / np.max(np.abs(out)) * gain


class Mix:
    def __init__(self):
        self.events = []  # (start_sec, mono array, gain)

    def add(self, start, x, gain=1.0):
        self.events.append((start, x, gain))

    def render(self, total, beat_curve, drone_curve):
        n = int(total * SR) + SR
        L = np.zeros(n, dtype=np.float32)
        R = np.zeros(n, dtype=np.float32)
        for start, x, g in self.events:
            i = int(start * SR)
            j = min(n, i + len(x))
            L[i:j] += x[: j - i] * g
            R[i:j] += x[: j - i] * g
        t = np.arange(n) / SR
        # drone: low open fifths that breathe slowly
        dg = np.interp(t, *drone_curve).astype(np.float32)
        drone = np.zeros(n, dtype=np.float32)
        for k, (f, a) in enumerate(((55.0, 1.0), (82.41, 0.6), (110.0, 0.45), (164.81, 0.22), (220.0, 0.12))):
            lfo = 0.65 + 0.35 * np.sin(2 * np.pi * (0.031 + 0.013 * k) * t + k)
            drone += (a * lfo * np.sin(2 * np.pi * f * t)).astype(np.float32)
        drone *= dg * 0.05
        L += drone
        R += drone
        # binaural bed: carrier in the left ear, carrier + beat in the right (headphones)
        beat = np.interp(t, *beat_curve[:2]).astype(np.float64)
        bg = np.interp(t, beat_curve[0], beat_curve[2]).astype(np.float32)
        carrier = 150.0
        L += (np.sin(2 * np.pi * carrier * t) * bg * 0.035).astype(np.float32)
        R += (np.sin(2 * np.pi * np.cumsum(carrier + beat) / SR) * bg * 0.035).astype(np.float32)
        peak = max(np.max(np.abs(L)), np.max(np.abs(R)))
        st = np.stack([L, R], axis=1) / peak * 0.89
        return st[: int(total * SR)]


# ---------------------------------------------------------------- timeline

class Builder:
    def __init__(self, mode):
        self.mode = mode
        self.t = 0.0
        self.segs = []  # dicts with start, end, kind
        self.mix = Mix()
        self.gap_say = 7.0 if mode == "night" else 5.0
        self.inhale = [breath_sound(T_IN, True, s) for s in range(3)]
        self.exhale = [breath_sound(T_OUT, False, s + 10) for s in range(3)]

    def seg(self, kind, dur, **kw):
        self.segs.append(dict(kind=kind, start=self.t, end=self.t + dur, **kw))
        self.t += dur

    def voice(self, text, speed=0.85, gain=1.0, at=None):
        x = tts(text, speed)
        self.mix.add(self.t if at is None else at, x, gain)
        return len(x) / SR

    def card(self, lines, dur, voice=None):
        if voice:
            d = self.voice(voice, at=self.t + 2.0)
            dur = max(dur, d + 4.0)
        self.seg("card", dur, lines=lines)

    def narr(self, text, gap=2.2, kind="narr", gain=1.0, speed=0.85, **kw):
        d = self.voice(text, speed=speed, gain=gain)
        self.seg(kind, d + gap, text=text, **kw)

    def items(self, items, gap_scale=1.0, gain=1.0, show=True):
        for it in items:
            if it[0] == "say":
                d = self.voice(it[1], speed=0.8, gain=gain)
                self.seg("say" if show else "narr", d + self.gap_say * gap_scale, text=it[1])
            elif it[0] == "narr":
                self.narr(it[1], gain=gain)
            elif it[0] == "gap":
                self.seg("narr", it[1] * gap_scale, text="")

    def wim_hof(self, holds, intro):
        self.narr(intro, gap=2.0, kind="card", lines=["WIM HOF BREATHING", f"{len(holds)} rounds · {BREATHS} breaths"])
        words = ["one", "two", "three", "four", "five"]
        for r, hold in enumerate(holds):
            self.narr(f"Round {words[r]}.", gap=1.2, kind="breath_ready", rnd=r, rounds=len(holds))
            start = self.t
            for b in range(BREATHS):
                self.mix.add(start + b * (T_IN + T_OUT), self.inhale[b % 3], 0.9)
                self.mix.add(start + b * (T_IN + T_OUT) + T_IN, self.exhale[b % 3], 0.9)
            self.seg("breath", BREATHS * (T_IN + T_OUT), rnd=r, rounds=len(holds))
            self.mix.add(self.t, bell(396, 6, 0.22))
            self.voice("Let it all out. And hold.", at=self.t + 0.3)
            if hold > 20:
                self.mix.add(self.t + hold - 10, bell(528, 4, 0.10))
            self.seg("hold", hold, rnd=r, rounds=len(holds), total=hold)
            d = self.voice("Breathe in. All the way. And hold.")
            self.seg("recover", max(RECOVER_HOLD, d + 1), rnd=r, rounds=len(holds), total=max(RECOVER_HOLD, d + 1))
            d = self.voice("Let go.")
            self.seg("rest", d + 3.0)
        self.narr("Breathe normally now.", gap=4.0, kind="rest")


def build(mode):
    blocks = parse_script()
    scenes = split_scenes(blocks["SCENES"])
    b = Builder(mode)
    safety = ("Do this lying down. Never in water, and never while driving. "
              "Tingling and light-headedness are normal. If anything feels wrong, stop and breathe normally.")
    marks = {}
    if mode == "night":
        b.card(["THETA IDENTITY", "night"], 6)
        b.card(["Lie down. Headphones in.", "Never in water. Never driving."], 6, voice=safety)
        marks["whm"] = b.t
        b.wim_hof([60, 75, 90, 105], "Four rounds. Thirty deep breaths each. Follow the sound. "
                  "In through the belly, then the chest. Let it go, no force.")
        marks["bridge"] = b.t
        b.items(blocks["BRIDGE"])
        marks["identity"] = b.t
        for name in ("WHO_I_AM", "THE_NO", "REAL_KIND", "THE_LONG_GAME", "THE_MAN", "DOMINION"):
            b.items(blocks[name])
            b.seg("narr", 4, text="")
        for sc in scenes:
            b.items(sc)
        marks["descent"] = b.t
        for gain, scale in ((1.0, 1.0), (0.7, 1.5), (0.45, 2.0)):
            b.items(blocks["DESCENT"], gap_scale=scale, gain=gain, show=False)
        marks["fade"] = b.t
        b.seg("black", 150)
        end = b.t
        # (times, beat Hz, level): silent through the breathwork, then alpha -> theta -> deep theta
        beat = ([0, marks["bridge"] - 1, marks["bridge"] + 20, marks["identity"], marks["descent"], marks["fade"], end],
                [10, 10, 9, 7, 5, 4, 3.5],
                [0, 0, 1, 1, 1, 0.9, 0])
        drone = ([0, 8, marks["whm"], marks["bridge"], marks["fade"], end], [0, 0.6, 0.35, 1, 1, 0])
    else:
        b.card(["THETA IDENTITY", "morning"], 5)
        b.items(blocks["MORNING_OPEN"])
        marks["identity"] = b.t
        for name in ("WHO_I_AM", "THE_NO", "THE_LONG_GAME", "THE_MAN"):
            b.items(blocks[name])
            b.seg("narr", 3, text="")
        for sc in scenes[:2]:
            b.items(sc)
        marks["whm"] = b.t
        b.card(["Now wake the body up.", "Lie down. Never in water."], 5, voice="Now I wake the body up. " + safety)
        b.wim_hof([60, 75, 90], "Three rounds. Thirty deep breaths each. Follow the sound. "
                  "In through the belly, then the chest. Let it go, no force.")
        b.items(blocks["MORNING_CLOSE"])
        b.seg("black", 8)
        end = b.t
        beat = ([0, 5, marks["whm"] - 10, marks["whm"], end], [5, 5, 9, 10, 10], [0, 1, 1, 0, 0])
        drone = ([0, 5, marks["whm"], marks["whm"] + 20, end - 8, end], [0, 1, 1, 0.35, 0.35, 0])
    return b, end, beat, drone, marks


# ---------------------------------------------------------------- video

AMBER = (214, 162, 92)
WARM = (236, 226, 210)


def gradient(top, bottom):
    t = np.linspace(0, 1, H)[:, None, None]
    g = (np.array(top) * (1 - t) + np.array(bottom) * t) * np.ones((1, W, 1))
    return Image.fromarray(g.astype(np.uint8), "RGB")


def ease(x):
    return 0.5 - 0.5 * np.cos(np.pi * min(max(x, 0.0), 1.0))


def dim(c, a):
    return tuple(int(v * a) for v in c)


def wrap(text, font, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if font.getlength(trial) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


class Frames:
    def __init__(self, mode):
        self.bg = gradient((10, 8, 16), (4, 3, 6)) if mode == "night" else gradient((12, 13, 22), (22, 15, 10))
        self.cache = OrderedDict()

    def centered(self, d, y, text, font, fill, spacing=0):
        if spacing:
            total = sum(font.getlength(ch) for ch in text) + spacing * (len(text) - 1)
            x = CX - total / 2
            for ch in text:
                d.text((x, y), ch, font=font, fill=fill, anchor="lm")
                x += font.getlength(ch) + spacing
        else:
            d.text((CX, y), text, font=font, fill=fill, anchor="mm")

    def orb(self, d, r, a):
        base = self.bg.getpixel((CX, CY))

        def glow(x):  # amber added on top of the background, never darker than it
            return tuple(min(255, int(b0 + c * x)) for b0, c in zip(base, AMBER))
        for k in range(10, 0, -1):
            rr = r + k * 9
            d.ellipse((CX - rr, CY - rr, CX + rr, CY + rr), fill=glow(a * 0.05 * (11 - k) / 10))
        d.ellipse((CX - r, CY - r, CX + r, CY + r), fill=glow(a * 0.2), outline=dim(AMBER, a * 0.9), width=3)

    def round_label(self, d, s, a=0.55):
        self.centered(d, 1520, f"ROUND {s['rnd'] + 1} / {s['rounds']}", F_LABEL, dim(WARM, a), spacing=6)

    def key_and_draw(self, s, t):
        """Return (key, draw_fn). The key decides whether the frame can be reused."""
        lt = t - s["start"]
        dur = s["end"] - s["start"]
        fade = min(1.0, lt / 0.8, (dur - lt) / 1.0)
        fq = round(max(fade, 0) * 24) / 24
        k = s["kind"]

        if k == "card":
            def draw(d):
                self.centered(d, 900, s["lines"][0], F_TITLE if len(s["lines"][0]) < 18 else F_TEXT, dim(WARM, fq * 0.85))
                self.centered(d, 1010, s["lines"][1], F_SMALL, dim(AMBER, fq * 0.8))
            return ("card", s["start"], fq), draw

        if k == "breath":
            per = T_IN + T_OUT
            n = int(lt // per)
            ph = lt - n * per
            x = ease(ph / T_IN) if ph < T_IN else 1 - ease((ph - T_IN) / T_OUT)
            r = int(170 + 190 * x) // 3 * 3
            word = "BREATHE IN" if ph < T_IN else "LET GO"

            def draw(d):
                self.orb(d, r, 0.8)
                self.centered(d, CY, str(min(n + 1, BREATHS)), F_NUM, dim(WARM, 0.92))
                self.centered(d, 1330, word, F_LABEL, dim(AMBER, 0.85), spacing=8)
                self.round_label(d, s)
            return ("breath", s["rnd"], n, r, word), draw

        if k in ("hold", "recover"):
            left = max(0.0, s["total"] - lt)
            secs = int(np.ceil(left))
            prog = round(lt / s["total"] * 360 / 1.5) * 1.5
            big = k == "recover"

            def draw(d):
                r = 360 if big else 170
                self.orb(d, r, 0.55 if big else 0.6)
                rr = r + 70
                d.arc((CX - rr, CY - rr, CX + rr, CY + rr), 0, 360, fill=dim(AMBER, 0.18), width=6)
                d.arc((CX - rr, CY - rr, CX + rr, CY + rr), -90, -90 + prog, fill=dim(AMBER, 0.9), width=6)
                label = f"{secs // 60}:{secs % 60:02d}" if secs >= 60 else str(secs)
                self.centered(d, CY, label, F_NUM_S, dim(WARM, 0.92))
                if big:
                    self.centered(d, 1330, "BREATHE IN · HOLD", F_LABEL, dim(AMBER, 0.85), spacing=8)
                else:
                    self.centered(d, 1330, "HOLD · LUNGS EMPTY", F_LABEL, dim(AMBER, 0.85), spacing=8)
                    self.centered(d, 1400, "breathe in when you need to", F_SMALL, dim(WARM, 0.4))
                self.round_label(d, s)
            return (k, s["start"], secs, prog), draw

        if k == "breath_ready":
            def draw(d):
                self.orb(d, 170, 0.8 * fq)
                self.centered(d, CY, "0", F_NUM, dim(WARM, 0.5 * fq))
                self.centered(d, 1330, "GET READY", F_LABEL, dim(AMBER, 0.85 * fq), spacing=8)
                self.round_label(d, s, 0.55 * fq)
            return ("ready", s["start"], fq), draw

        if k == "rest":
            def draw(d):
                self.orb(d, 170, 0.5 * fq)
                self.centered(d, 1330, "BREATHE NORMALLY", F_LABEL, dim(AMBER, 0.7 * fq), spacing=8)
            return ("rest", s["start"], fq), draw

        if k == "say":
            def draw(d):
                lines = wrap(s["text"], F_TEXT, 860)
                y0 = 960 - (len(lines) - 1) * 46
                for i, ln in enumerate(lines):
                    self.centered(d, y0 + i * 92, ln, F_TEXT, dim(AMBER, fq * 0.75))
            return ("say", s["start"], fq), draw

        if k == "narr":
            # near-dark, a slow ember so the screen is never dead
            p = 0.5 + 0.5 * np.sin(2 * np.pi * t / 10)
            a = round((0.12 + 0.10 * p) * 30) / 30

            def draw(d):
                r = 6
                d.ellipse((CX - r, 960 - r, CX + r, 960 + r), fill=dim(AMBER, a * 1.6))
                for k2 in range(1, 6):
                    rr = r + k2 * 8
                    d.ellipse((CX - rr, 960 - rr, CX + rr, 960 + rr), outline=dim(AMBER, a * 0.5 / k2), width=2)
            return ("narr", a), draw

        return ("black",), None

    def frame(self, s, t):
        key, draw = self.key_and_draw(s, t)
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        img = self.bg.copy() if draw or s["kind"] != "black" else Image.new("RGB", (W, H), (0, 0, 0))
        if draw:
            draw(ImageDraw.Draw(img))
        data = img.tobytes()
        self.cache[key] = data
        if len(self.cache) > 48:
            self.cache.popitem(last=False)
        return data


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "night"
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "renders" / f"theta-identity-{mode}-v1.mp4"
    CACHE.mkdir(parents=True, exist_ok=True)
    b, end, beat, drone, marks = build(mode)
    print(f"{mode}: {end / 60:.1f} min", {k: f"{v / 60:.1f}" for k, v in marks.items()}, flush=True)
    wav = CACHE / f"{mode}.wav"
    sf.write(wav, b.mix.render(end, beat, drone), SR, subtype="PCM_16")
    print("audio done", flush=True)

    fr = Frames(mode)
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", "-i", str(wav), "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
         "-tune", "stillimage", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart", "-shortest", str(out)],
        stdin=subprocess.PIPE)
    segs = b.segs
    si = 0
    nframes = int(end * FPS)
    for i in range(nframes):
        t = i / FPS
        while si < len(segs) - 1 and t >= segs[si]["end"]:
            si += 1
        ff.stdin.write(fr.frame(segs[si], t))
        if i % (FPS * 120) == 0:
            print(f"  {t / 60:.0f} min", flush=True)
    ff.stdin.close()
    ff.wait()
    print("wrote", out)


if __name__ == "__main__":
    main()
