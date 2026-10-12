"""Theta Identity: builds the full guided session as one video.

    python projects/theta-identity/build.py            # -> renders/theta-identity-v2.mp4
    python projects/theta-identity/build.py --preview 90 120   # render only 1:30-3:30 for a check

Introduction -> five Wim Hof rounds (identity statements over the breath, a memory scene in every
hold) -> slow-breath bridge -> descent into sleep. Everything is generated here: the voice (Kokoro,
local), the breath (shaped noise, no tones), the music (composed in code, tuned to A=432 Hz), the
binaural theta bed and every frame. Edit script.md and run it again.
Needs: ffmpeg, numpy, pillow, soundfile, kokoro-onnx (+ model files, see MODELS).
"""
import hashlib
import os
import pickle
import re
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
CACHE = Path(os.environ.get("THETA_CACHE", "/tmp/theta-identity"))
MODELS = Path(os.environ.get("KOKORO_MODELS", CACHE / "models"))
VOICE = os.environ.get("THETA_VOICE", "am_michael")

SR = 48000
FPS = 24
ASPECT = os.environ.get("THETA_ASPECT", "16x9")   # "16x9" (1920x1080) or "9x16" (1080x1920)
if ASPECT == "9x16":
    W, H, CY = 1080, 1920, 880
    TOP1, TOP2, BOT, BOT2, READY1, READY2, TEXTW, SUBW = 260, 320, 1600, 1660, 1330, 1390, 900, 940
else:
    W, H, CY = 1920, 1080, 500
    TOP1, TOP2, BOT, BOT2, READY1, READY2, TEXTW, SUBW = 90, 140, 905, 965, 770, 820, 1500, 1500
LW, LH = W // 4, H // 4    # the breathing field is computed at quarter size, then upscaled
CX = W / 2

T_IN, T_OUT = 1.8, 1.5     # Wim Hof pace: ~3.3 s a breath
BREATHS = 30
HOLDS = [60, 75, 90, 90, 105]
RECOVER_HOLD = 15
A4 = 432.0

FONT_DIR = Path("/usr/share/fonts/opentype/inter")
F_NUM = ImageFont.truetype(str(FONT_DIR / "InterDisplay-Light.otf"), 190)
F_TEXT = ImageFont.truetype(str(FONT_DIR / "InterDisplay-Light.otf"), 62)
F_SUB = ImageFont.truetype(str(FONT_DIR / "InterDisplay-Light.otf"), 50)
F_TITLE = ImageFont.truetype(str(FONT_DIR / "InterDisplay-Light.otf"), 96)
F_LABEL = ImageFont.truetype(str(FONT_DIR / "Inter-Medium.otf"), 32)
F_SMALL = ImageFont.truetype(str(FONT_DIR / "Inter-Light.otf"), 34)


# ================================================================ script

def parse_script():
    blocks, cur = {}, None
    for raw in (HERE / "script.md").read_text().splitlines():
        line = raw.strip()
        if line.startswith("# "):
            name = line[2:].strip()
            cur = blocks.setdefault(name, []) if re.fullmatch(r"[A-Z0-9_]+", name) else None
            continue
        if cur is None or not line:
            continue
        if line.startswith("> "):
            cur.append(("say", line[2:].strip()))
        elif line.startswith("~ "):
            cur.append(("narr", line[2:].strip()))
        elif m := re.fullmatch(r"\[(\d+(?:\.\d+)?)\]", line):
            cur.append(("gap", float(m.group(1))))
    return blocks


def sentences(text):
    parts = re.split(r'(?<=[.!?])\s+(?=[A-Z"])', text)
    return [p.strip() for p in parts if p.strip()]


# ================================================================ DSP helpers

def stft_noise(n, shape_fn, seed, n_fft=1024, hop=256):
    """Noise whose spectrum follows shape_fn(freqs, t01) frame by frame (overlap-add synthesis)."""
    rng = np.random.default_rng(seed)
    frames = n // hop + 4
    f = np.fft.rfftfreq(n_fft, 1 / SR)
    win = np.hanning(n_fft)
    out = np.zeros(frames * hop + n_fft)
    for k in range(frames):
        t01 = min(1.0, k * hop / max(1, n))
        mag = shape_fn(f, t01)
        spec = mag * np.exp(1j * rng.uniform(0, 2 * np.pi, len(f)))
        out[k * hop: k * hop + n_fft] += np.fft.irfft(spec, n_fft) * win
    return out[n_fft // 2: n_fft // 2 + n].astype(np.float32)


def bump(f, center, width):
    return np.exp(-0.5 * ((f - center) / width) ** 2)


def smooth_noise(n, rate_hz, seed):
    rng = np.random.default_rng(seed)
    pts = max(4, int(n / SR * rate_hz) + 4)
    v = rng.standard_normal(pts)
    x = np.linspace(0, pts - 3, n)
    return np.interp(x, np.arange(pts), v).astype(np.float32)


def fft_convolve(x, ir):
    n = len(x) + len(ir) - 1
    nf = 1 << (n - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, nf) * np.fft.rfft(ir, nf), nf)[:n].astype(np.float32)


def ola_convolve(x, ir, block=1 << 20):
    out = np.zeros(len(x) + len(ir), dtype=np.float32)
    for i in range(0, len(x), block):
        y = fft_convolve(x[i:i + block], ir)
        out[i:i + len(y)] += y[: len(out) - i]
    return out[: len(x)]


def reverb_ir(seconds, decay, seed, bright=6000):
    n = int(SR * seconds)
    t = np.arange(n) / SR
    rng = np.random.default_rng(seed)
    ir = rng.standard_normal(n) * np.exp(-t / decay)
    spec = np.fft.rfft(ir)
    f = np.fft.rfftfreq(n, 1 / SR)
    spec *= 1 / (1 + (f / bright) ** 2)
    ir = np.fft.irfft(spec, n)
    ir[: int(SR * 0.012)] *= np.linspace(0, 1, int(SR * 0.012))
    return (ir / np.sqrt(np.sum(ir ** 2))).astype(np.float32)


def resample(x, sr_in, sr_out):
    if sr_in == sr_out:
        return x
    n_out = int(round(len(x) * sr_out / sr_in))
    spec = np.fft.rfft(x)
    out = np.zeros(n_out // 2 + 1, dtype=complex)
    k = min(len(spec), len(out))
    out[:k] = spec[:k]
    return (np.fft.irfft(out, n_out) * (n_out / len(x))).astype(np.float32)


# ================================================================ voice

_kokoro = None
_ROOM = None


def tts(text, speed):
    global _kokoro, _ROOM
    key = hashlib.sha1(f"{VOICE}|{speed}|{text}".encode()).hexdigest()[:16]
    path = CACHE / "tts" / f"{key}.wav"
    if not path.exists():
        if _kokoro is None:
            from kokoro_onnx import Kokoro
            _kokoro = Kokoro(str(MODELS / "kokoro.onnx"), str(MODELS / "voices.bin"))
        samples, sr = _kokoro.create(text, voice=VOICE, speed=speed, lang="en-us")
        path.parent.mkdir(parents=True, exist_ok=True)
        sf.write(path, samples, sr)
    x, sr = sf.read(path, dtype="float32")
    x = resample(x, sr, SR)
    idx = np.flatnonzero(np.abs(x) > 0.01)
    if len(idx):
        x = x[max(0, idx[0] - 800): idx[-1] + 2400]
    if _ROOM is None:
        _ROOM = reverb_ir(1.4, 0.32, 7, bright=3500)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.9
    wet = fft_convolve(x, _ROOM)
    return (np.pad(x, (0, len(_ROOM) - 1)) * 0.9 + wet * 0.2).astype(np.float32)


# ================================================================ breath

def breath(dur, inhale, seed, depth=1.0):
    """A human breath: turbulent air shaped by the throat and mouth. Stereo, no tones.

    Inhale: airy, nasal-throat resonances that tighten and brighten as the lungs fill.
    Exhale: an open-mouth "haah" (relaxed-vowel formants), quick push then a passive release.
    """
    n = int(dur * SR)
    if inhale:
        def shape(f, t):
            pink = 1 / np.sqrt(np.maximum(f, 60) / 300)
            lift = 1 + 0.12 * t
            body = (0.55 * bump(f, 1150 * lift, 420) + 0.7 * bump(f, 2500 * lift, 650)
                    + 0.45 * bump(f, 4300 * lift, 1300) + 0.12 * bump(f, 300, 140))
            air = 0.10 * ((f > 600) & (f < 6000)) * (0.6 + 0.6 * t)
            roll = 1 / (1 + (f / (2600 + 900 * t)) ** 2.5)
            return pink * (body + air) * roll * (f > 90)

        t = np.linspace(0, 1, n)
        env = ease(t / 0.38) ** 1.3 * (0.8 + 0.2 * t) * ease((1 - t) / 0.2)
    else:
        def shape(f, t):
            pink = 1 / np.sqrt(np.maximum(f, 60) / 250)
            close = 1 - 0.1 * t
            vowel = (1.0 * bump(f, 640 * close, 210) + 0.75 * bump(f, 1130 * close, 260)
                     + 0.4 * bump(f, 2450, 420) + 0.18 * bump(f, 3600, 700))
            chest = 0.35 * bump(f, 170, 80)
            air = 0.06 * ((f > 400) & (f < 4500))
            roll = 1 / (1 + (f / 2300) ** 2.5)
            return pink * (vowel + chest + air) * roll * (f > 70)

        t = np.linspace(0, 1, n)
        env = ease(t / 0.12) * np.exp(-2.2 * t) * ease((1 - t) / 0.3)
    a = stft_noise(n, shape, seed)
    b = stft_noise(n, shape, seed + 1000)
    jitter = 1 + 0.16 * smooth_noise(n, 11, seed + 7) + 0.06 * smooth_noise(n, 37, seed + 9)
    env = (env * jitter * depth).astype(np.float32)
    mono = a / (np.max(np.abs(a)) + 1e-9)
    side = b / (np.max(np.abs(b)) + 1e-9)
    return np.stack([(mono + 0.22 * side) * env, (mono - 0.22 * side) * env], axis=1) * 0.5


# ================================================================ music

def note_hz(midi):
    return A4 * 2 ** ((midi - 69) / 12)


# D major, slow and open: Dmaj9 -> Bm11 -> Gmaj7 -> Asus2. The second pass lifts the top voice.
CHORDS = [
    [38, 45, 54, 57, 61, 64],
    [35, 42, 50, 54, 57, 64],
    [31, 38, 50, 54, 59, 61],
    [33, 40, 52, 57, 59, 64],
    [38, 45, 54, 57, 64, 69],
    [35, 42, 50, 57, 62, 66],
    [31, 38, 50, 55, 59, 66],
    [33, 40, 49, 57, 61, 64],
]
CHORD_LEN = 24.0
XFADE = 9.0
PENTA = [62, 64, 66, 69, 71, 74, 76, 78, 81]  # D major pentatonic, upper register


def pad_cycle():
    """One seamless 192 s loop of warm, slowly drifting pad chords, reverb wrapped around the loop."""
    path = CACHE / "pad_cycle_v2.npy"
    if path.exists():
        return np.load(path)
    sr = 24000  # rendered at half rate (pads have nothing above 6 kHz), upsampled after
    L = int(CHORD_LEN * len(CHORDS) * sr)
    out = np.zeros((L, 2), dtype=np.float32)
    seg = int((CHORD_LEN + XFADE) * sr)
    t = np.arange(seg) / sr
    fade = np.minimum(1, np.minimum(t / XFADE, (CHORD_LEN + XFADE - t) / XFADE))
    fade = (0.5 - 0.5 * np.cos(np.pi * np.clip(fade, 0, 1))).astype(np.float32)
    rng = np.random.default_rng(3)
    for ci, chord in enumerate(CHORDS):
        start = int((ci * CHORD_LEN - XFADE / 2) * sr)
        buf = np.zeros((seg, 2), dtype=np.float32)
        for vi, m in enumerate(chord):
            f0 = note_hz(m)
            lvl = 0.9 if m < 45 else (0.55 if m < 60 else 0.32)
            swell = 0.75 + 0.25 * np.sin(2 * np.pi * (0.02 + 0.007 * vi) * t + rng.uniform(0, 6))
            for d, pan in ((-5, 0.25), (0, 0.5), (5, 0.75)):
                drift = 1 + (d + 1.5 * np.sin(2 * np.pi * 0.05 * t + rng.uniform(0, 6))) / 1731
                phase = 2 * np.pi * f0 * np.cumsum(drift) / sr + rng.uniform(0, 6)
                tone = np.zeros(seg)
                for h in range(1, 7):
                    if f0 * h > 5000:
                        break
                    tone += np.sin(h * phase) / h ** 1.9
                tone *= lvl * swell / 3
                buf[:, 0] += (tone * np.sqrt(1 - pan)).astype(np.float32)
                buf[:, 1] += (tone * np.sqrt(pan)).astype(np.float32)
        buf *= fade[:, None]
        idx = (start + np.arange(seg)) % L
        out[idx] += buf
    # circular reverb so the loop point is invisible
    for ch, seed in ((0, 11), (1, 12)):
        ir = reverb_ir(7.0, 2.2, seed, bright=4000)
        ir = resample(ir, SR, sr)
        wet = np.fft.irfft(np.fft.rfft(out[:, ch]) * np.fft.rfft(ir, L), L)
        out[:, ch] = out[:, ch] * 0.45 + wet.astype(np.float32) * 0.9
    out = np.stack([resample(out[:, 0], sr, SR), resample(out[:, 1], sr, SR)], axis=1)
    out /= np.max(np.abs(out))
    path.parent.mkdir(parents=True, exist_ok=True)
    np.save(path, out)
    return out


def bells(total, seed=5):
    """Sparse, soft felt-piano notes from the pentatonic scale, drifting in a large space."""
    n = int(total * SR)
    L = np.zeros(n, dtype=np.float32)
    R = np.zeros(n, dtype=np.float32)
    rng = np.random.default_rng(seed)
    t = 4.0
    dur = 7.0
    tt = np.arange(int(dur * SR)) / SR
    while t < total - dur:
        m = rng.choice(PENTA)
        f = note_hz(m)
        tone = (np.sin(2 * np.pi * f * tt) * np.exp(-tt / 2.4)
                + 0.35 * np.sin(2 * np.pi * 2 * f * tt) * np.exp(-tt / 1.1)
                + 0.12 * np.sin(2 * np.pi * 3.01 * f * tt) * np.exp(-tt / 0.6))
        tone *= np.minimum(1, tt / 0.015) * rng.uniform(0.5, 1.0)
        pan = rng.uniform(0.2, 0.8)
        i = int(t * SR)
        L[i:i + len(tt)] += (tone * np.sqrt(1 - pan)).astype(np.float32)
        R[i:i + len(tt)] += (tone * np.sqrt(pan)).astype(np.float32)
        t += rng.uniform(5.5, 13.0)
    irl, irr = reverb_ir(8.0, 2.6, 21, bright=5000), reverb_ir(8.0, 2.6, 22, bright=5000)
    L = L * 0.35 + ola_convolve(L, irl)
    R = R * 0.35 + ola_convolve(R, irr)
    return np.stack([L, R], axis=1)


def bell_hit(freq, dur=6.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for ratio, amp, tau in ((1, 1, 2.6), (2.76, 0.4, 1.2), (5.4, 0.15, 0.6)):
        x += amp * np.sin(2 * np.pi * freq * ratio * t) * np.exp(-t / tau)
    x *= np.minimum(1, t / 0.004)
    return (x / np.max(np.abs(x))).astype(np.float32)


# ================================================================ timeline

class Builder:
    def __init__(self):
        self.t = 0.0
        self.segs = []
        self.voice = []    # (start, mono)
        self.fx = []       # (start, stereo or mono, gain)
        self.inhales = [breath(T_IN, True, s) for s in range(4)]
        self.exhales = [breath(T_OUT, False, 50 + s) for s in range(4)]

    def seg(self, kind, dur, **kw):
        self.segs.append(dict(kind=kind, start=self.t, end=self.t + dur, **kw))
        self.t += dur

    def say(self, text, at, speed=0.84):
        x = tts(text, speed)
        self.voice.append((at, x))
        return len(x) / SR

    def narrate(self, items, kind, caption=False, speed=0.9):
        for it in items:
            if it[0] == "gap":
                self.seg(kind, it[1], text="")
                continue
            for s in sentences(it[1]):
                d = self.say(s, self.t, speed=speed if it[0] == "narr" else 0.82)
                self.seg(kind, d + (0.45 if it[0] == "narr" else 4.5), text=s if caption or it[0] == "say" else "",
                         stmt=it[0] == "say")

    def round(self, r, statements, scene, anchor, hold):
        n = len(HOLDS)
        self.seg("ready", 2.5, rnd=r, rounds=n)
        self.say(f"Round {['one', 'two', 'three', 'four', 'five'][r]}.", self.t - 2.3)
        start = self.t
        per = T_IN + T_OUT
        for b in range(BREATHS):
            self.fx.append((start + b * per, self.inhales[b % 4], 0.55))
            self.fx.append((start + b * per + T_IN, self.exhales[b % 4], 0.55))
        # statements ride the breath: spread evenly, each starting on an out-breath
        stmts = [s for k, s in statements if k == "say"]
        slots = np.linspace(1, BREATHS - 4, len(stmts)).round().astype(int)
        cues = []
        for b, s in zip(slots, stmts):
            at = start + b * per + T_IN + 0.1
            d = self.say(s, at, speed=0.86)
            cues.append((at, at + max(d + 1.6, 5.5), s))
        self.seg("breath", BREATHS * per, rnd=r, rounds=n, cues=cues)
        # out-breath and hold, the scene plays in the stillness
        self.fx.append((self.t, bell_hit(note_hz(62)), 0.16))
        d = self.say("Let it all out. And hold.", self.t + 0.2)
        at = self.t + d + 2.5
        for it in scene:
            if it[0] == "gap":
                at += it[1]
                continue
            for s in sentences(it[1]):
                at += self.say(s, at, speed=0.86) + 0.7
        hold = max(hold, at - self.t + 4)
        self.fx.append((self.t + hold - 9, bell_hit(note_hz(69), 4), 0.08))
        self.seg("hold", hold, rnd=r, rounds=n, total=hold)
        # recovery breath with an anchor line
        d = self.say("Breathe in. All the way. And hold.", self.t)
        self.fx.append((self.t + 0.3, breath(2.2, True, 900 + r, 1.1), 0.55))
        self.say(anchor, self.t + d + 3.0, speed=0.82)
        self.seg("recover", RECOVER_HOLD + d, rnd=r, rounds=n, total=RECOVER_HOLD + d, delay=d, anchor=anchor)
        self.fx.append((self.t, breath(2.6, False, 950 + r, 1.0), 0.5))
        d = self.say("Let go.", self.t)
        self.seg("release", d + 3.0)


def build():
    blocks = parse_script()
    b = Builder()
    marks = {}
    b.seg("title", 7)
    marks["intro"] = b.t
    b.narrate(blocks["INTRO"], "intro", caption=True)
    marks["rounds"] = b.t
    for r, hold in enumerate(HOLDS):
        anchor = [s for k, s in blocks[f"RECOVER_{r + 1}"] if k == "say"][0]
        b.round(r, blocks[f"ROUND_{r + 1}"], blocks[f"HOLD_{r + 1}"], anchor, hold)
    marks["bridge"] = b.t
    # slow breathing bridge: 4 in, 6 out, natural breath under the voice
    bstart = b.t
    b.narrate(blocks["BRIDGE"], "bridge", speed=0.86)
    for k in range(int((b.t - bstart) / 10)):
        b.fx.append((bstart + k * 10, breath(4.0, True, 300 + k, 0.7), 0.3))
        b.fx.append((bstart + k * 10 + 4.0, breath(6.0, False, 400 + k, 0.7), 0.3))
    marks["descent"] = b.t
    for loop in range(3):
        b.narrate(blocks["DESCENT"], "descent", speed=0.82)
        b.seg("descent", 6, text="")
    for v in range(len(b.voice)):
        st, x = b.voice[v]
        if st >= marks["descent"]:
            k = (st - marks["descent"]) / (b.t - marks["descent"])
            b.voice[v] = (st, x * (1.0 - 0.6 * k))
    marks["fade"] = b.t
    b.seg("fade", 150)
    return b, marks


def mix(b, marks, total):
    n = int(total * SR)
    t = np.arange(n) / SR
    voice = np.zeros(n, dtype=np.float32)
    for st, x in b.voice:
        i = int(st * SR)
        j = min(n, i + len(x))
        voice[i:j] += x[: j - i]
    fx = np.zeros((n, 2), dtype=np.float32)
    for st, x, g in b.fx:
        i = int(st * SR)
        j = min(n, i + len(x))
        if x.ndim == 1:
            x = np.stack([x, x], 1)
        fx[i:j] += x[: j - i] * g
    # breath sits in a small room
    ir = reverb_ir(0.9, 0.18, 33, bright=7000)
    for ch in range(2):
        fx[:, ch] = fx[:, ch] * 0.85 + ola_convolve(fx[:, ch], ir) * 0.25

    music = np.zeros((n, 2), dtype=np.float32)
    pad = pad_cycle()
    for i in range(0, n, len(pad)):
        j = min(n, i + len(pad))
        music[i:j] += pad[: j - i]
    music += bells(total) * 0.32
    # music level: up in the intro, steady under the rounds, slowly settling then out at the end
    lvl = np.interp(t, [0, 4, marks["intro"], marks["rounds"], marks["bridge"], marks["fade"], total - 20, total],
                    [0, 0.30, 0.30, 0.24, 0.26, 0.26, 0.0, 0.0])
    # duck gently under the voice
    env = np.abs(voice)
    k = int(0.25 * SR)
    env = np.convolve(env[::48], np.ones(k // 48) / (k // 48), mode="same")
    env = np.repeat(env, 48)[:n]
    if len(env) < n:
        env = np.pad(env, (0, n - len(env)))
    duck = 1 - 0.35 * np.clip(env / 0.08, 0, 1)
    music *= (lvl * duck)[:, None].astype(np.float32)

    # binaural theta: 216 Hz (= 432 / 2) in the left ear, 216 + beat in the right
    beat = np.interp(t, [0, marks["intro"], marks["rounds"], marks["bridge"], marks["descent"], marks["fade"], total],
                     [8, 8, 6, 6, 5, 4, 4])
    bl = np.interp(t, [0, 6, marks["rounds"] - 30, marks["fade"], total - 10, total],
                   [0, 0.02, 0.025, 0.03, 0, 0]).astype(np.float32)
    left = np.sin(2 * np.pi * 216 * t).astype(np.float32) * bl
    right = np.sin(2 * np.pi * np.cumsum(216 + beat) / SR).astype(np.float32) * bl

    out = music + fx
    out[:, 0] += voice * 0.62 + left
    out[:, 1] += voice * 0.62 + right
    out /= np.max(np.abs(out)) / 0.89
    return out


# ================================================================ visuals

AMBER = np.array([222, 160, 84], dtype=np.float32)
EMBER = np.array([150, 70, 40], dtype=np.float32)
CORE = np.array([255, 236, 205], dtype=np.float32)
BG_TOP = np.array([9, 7, 14], dtype=np.float32)
BG_BOT = np.array([3, 2, 5], dtype=np.float32)


def ease(x):
    x = np.clip(x, 0.0, 1.0)
    return 0.5 - 0.5 * np.cos(np.pi * x)


def seg_at(segs, t):
    lo, hi = 0, len(segs) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if segs[mid]["start"] <= t:
            lo = mid
        else:
            hi = mid - 1
    return segs[lo]


def breath_state(s, t):
    """(lungs 0..1, brightness 0..1, turbulence) for any moment."""
    lt = t - s["start"]
    k = s["kind"]
    slow = 0.5 - 0.5 * np.cos(2 * np.pi * t / 9.0)
    if k == "title":
        return 0.25 + 0.1 * slow, ease(lt / 4) * 0.8, 0.4
    if k == "intro":
        return 0.28 + 0.14 * slow, 0.72, 0.5
    if k == "ready":
        return 0.25, 0.85, 0.5
    if k == "breath":
        per = T_IN + T_OUT
        ph = lt % per
        x = ease(ph / T_IN) if ph < T_IN else 1 - ease((ph - T_IN) / T_OUT)
        return 0.18 + 0.82 * x, 1.0, 1.0
    if k == "hold":
        return 0.12 + 0.03 * slow, 0.62, 0.25
    if k == "recover":
        d = s["delay"]
        if lt < d:
            return 0.15, 0.7, 0.4
        return 0.15 + 0.85 * ease((lt - d) / 2.2), 0.9, 0.35
    if k == "release":
        return 1 - 0.8 * ease(lt / 2.6), 0.85, 0.6
    if k == "bridge":
        ph = lt % 10
        x = ease(ph / 4) if ph < 4 else 1 - ease((ph - 4) / 6)
        return 0.15 + 0.5 * x, 0.6, 0.4
    if k == "descent":
        return 0.15 + 0.3 * (0.5 - 0.5 * np.cos(2 * np.pi * t / 12)), 0.45, 0.3
    if k == "fade":
        return 0.15 + 0.25 * (0.5 - 0.5 * np.cos(2 * np.pi * t / 12)), 0.4 * max(0, 1 - lt / 60), 0.3
    return 0.2, 0.5, 0.5


class Field:
    """A soft, living light that fills and empties like lungs: no edges, no container."""

    def __init__(self):
        y, x = np.mgrid[0:LH, 0:LW].astype(np.float32)
        self.dx = x - CX / 4
        self.dy = (y - CY / 4) * 0.92
        self.r = np.sqrt(self.dx ** 2 + self.dy ** 2) + 1e-3
        self.th = np.arctan2(self.dy, self.dx)
        self.x, self.y = x, y
        g = (y / LH)[..., None]
        self.bg = BG_TOP * (1 - g) + BG_BOT * g
        rng = np.random.default_rng(1)
        self.p_ang = rng.uniform(0, 2 * np.pi, 140)
        self.p_rad = rng.uniform(0.25, 1.9, 140)
        self.p_spd = rng.uniform(-0.05, 0.05, 140)
        self.p_ph = rng.uniform(0, 2 * np.pi, 140)
        self.p_size = rng.uniform(0.5, 1.3, 140)

    def render(self, t, lungs, bright, turb):
        R = 40 + 175 * lungs                      # quarter-res pixels: ~160 px empty, ~860 px full
        wob = (0.05 * np.sin(2 * self.th + 0.45 * t) + 0.04 * np.sin(3 * self.th - 0.31 * t + 1.3)
               + 0.03 * np.sin(5 * self.th + 0.7 * t + 2.1) + 0.02 * np.sin(7 * self.th - 0.9 * t))
        wob *= 0.6 + 0.8 * turb * lungs
        rr = self.r / (R * (1 + wob))
        flow = 1 + 0.10 * np.sin(self.x / 23 + 0.6 * t) * np.sin(self.y / 31 - 0.45 * t) * (0.5 + turb)
        halo = np.exp(-(rr ** 2) * 1.25) * flow
        mid = np.exp(-(rr / 0.6) ** 2 * 1.5)
        core = np.exp(-(rr / 0.28) ** 2 * 1.6)
        # particles drift with the breath: drawn in as the field fills, released as it empties
        pr = R * self.p_rad * (1 + 0.05 * np.sin(t * 0.8 + self.p_ph))
        pa = self.p_ang + self.p_spd * t
        px = CX / 4 + pr * np.cos(pa)
        py = CY / 4 + pr * np.sin(pa) / 0.92
        dots = np.zeros((LH, LW), dtype=np.float32)
        for i in range(len(px)):
            xi, yi = int(px[i]), int(py[i])
            if 1 <= xi < LW - 2 and 1 <= yi < LH - 2:
                a = self.p_size[i] * (0.5 + 0.5 * np.sin(t * 1.3 + self.p_ph[i]))
                dots[yi - 1:yi + 2, xi - 1:xi + 2] += a * np.array([[0.2, 0.5, 0.2], [0.5, 1, 0.5], [0.2, 0.5, 0.2]])
        b = bright
        img = (self.bg
               + EMBER * (halo * 0.38 * b)[..., None]
               + AMBER * (mid * 0.42 * b)[..., None]
               + CORE * (core * (0.12 + 0.30 * lungs) * b)[..., None]
               + AMBER * (dots * 0.35 * b * (0.4 + 0.6 * halo))[..., None])
        return np.clip(img, 0, 255).astype(np.uint8)


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


def text_block(d, text, font, y, fill, alpha, width=None, lh=None):
    width = width or TEXTW
    lines = wrap(text, font, width)
    lh = lh or int(font.size * 1.32)
    y0 = y - (len(lines) - 1) * lh / 2
    col = tuple(int(c) for c in fill) + (int(255 * alpha),)
    shadow = (0, 0, 0, int(160 * alpha))
    for i, ln in enumerate(lines):
        d.text((W / 2 + 2, y0 + i * lh + 3), ln, font=font, fill=shadow, anchor="mm")
        d.text((W / 2, y0 + i * lh), ln, font=font, fill=col, anchor="mm")


def spaced(d, y, text, font, fill, alpha, spacing=7):
    total = sum(font.getlength(ch) for ch in text) + spacing * (len(text) - 1)
    x = W / 2 - total / 2
    col = tuple(int(c) for c in fill) + (int(255 * alpha),)
    for ch in text:
        d.text((x, y), ch, font=font, fill=col, anchor="lm")
        x += font.getlength(ch) + spacing


def fade_alpha(t, a, b, fin=0.6, fout=0.9):
    if t < a or t > b:
        return 0.0
    return float(min(1, (t - a) / fin, (b - t) / fout))


WARM = (240, 228, 210)
GOLD = (226, 170, 96)


def overlay(img, s, t, lungs):
    k = s["kind"]
    lt = t - s["start"]
    d = ImageDraw.Draw(img, "RGBA")
    if k == "title":
        a = fade_alpha(lt, 0.8, 7.0, 1.5, 1.5)
        text_block(d, "THETA IDENTITY", F_TITLE, CY - 20, WARM, a * 0.95)
        spaced(d, CY + 70, "AN INSTALLATION, NOT A MEDITATION", F_LABEL, GOLD, a * 0.85, 6)
    elif k in ("intro", "bridge", "descent") and s.get("text"):
        a = fade_alpha(lt, 0, s["end"] - s["start"], 0.35, 0.45)
        if s.get("stmt"):
            text_block(d, s["text"], F_TEXT, BOT, GOLD, a * 0.85)
        elif k == "intro":
            text_block(d, s["text"], F_SUB, BOT, WARM, a * 0.82, width=SUBW)
    elif k == "ready":
        spaced(d, READY1, f"ROUND {s['rnd'] + 1} OF {s['rounds']}", F_LABEL, GOLD, 0.9)
        spaced(d, READY2, "GET READY", F_LABEL, WARM, 0.55)
    elif k == "breath":
        per = T_IN + T_OUT
        n = int(lt // per) + 1
        d.text((W / 2, CY), str(min(n, BREATHS)), font=F_NUM, fill=WARM + (int(255 * (0.55 + 0.35 * lungs)),), anchor="mm")
        spaced(d, TOP1, f"ROUND {s['rnd'] + 1} OF {s['rounds']}", F_LABEL, WARM, 0.5)
        ph = lt % per
        spaced(d, TOP2, "BREATHE IN" if ph < T_IN else "LET GO", F_LABEL, GOLD, 0.75)
        for a0, a1, txt in s["cues"]:
            a = fade_alpha(t, a0, a1, 0.4, 0.6)
            if a > 0:
                text_block(d, txt, F_TEXT, BOT, GOLD, a * 0.92)
    elif k == "hold":
        left = max(0.0, s["total"] - lt)
        secs = int(np.ceil(left))
        lab = f"{secs // 60}:{secs % 60:02d}"
        d.text((W / 2, CY), lab, font=F_NUM, fill=WARM + (150,), anchor="mm")
        spaced(d, TOP1, f"ROUND {s['rnd'] + 1} OF {s['rounds']}", F_LABEL, WARM, 0.5)
        spaced(d, TOP2, "HOLD · LUNGS EMPTY", F_LABEL, GOLD, 0.75)
        a = fade_alpha(lt, 3, s["total"] - 1, 2, 1)
        spaced(d, BOT, "SEE IT THROUGH YOUR OWN EYES", F_LABEL, WARM, 0.45 * a, 6)
        d.text((W / 2, BOT2), "breathe in when you need to", font=F_SMALL, fill=WARM + (int(80 * a),), anchor="mm")
    elif k == "recover":
        dl = s["delay"]
        left = max(0.0, s["total"] - lt)
        if lt > dl:
            d.text((W / 2, CY), str(int(np.ceil(left))), font=F_NUM, fill=WARM + (170,), anchor="mm")
        spaced(d, TOP1, f"ROUND {s['rnd'] + 1} OF {s['rounds']}", F_LABEL, WARM, 0.5)
        spaced(d, TOP2, "BREATHE IN · HOLD", F_LABEL, GOLD, 0.8)
        a = fade_alpha(lt, dl + 3.0, s["total"] - 0.5, 0.6, 0.8)
        if a > 0:
            text_block(d, s["anchor"], F_TEXT, BOT, GOLD, a * 0.92)
    elif k == "release":
        spaced(d, TOP2, "LET GO", F_LABEL, GOLD, 0.7 * fade_alpha(lt, 0, s["end"] - s["start"], 0.3, 0.8))


_FIELD = None


def render_frame(segs, t):
    global _FIELD
    if _FIELD is None:
        _FIELD = Field()
    s = seg_at(segs, t)
    # smooth the breath state across segment joins (sample a little window)
    vals = [breath_state(seg_at(segs, max(0, t + dt)), max(0, t + dt)) for dt in (-0.12, -0.06, 0, 0.06, 0.12)]
    lungs, bright, turb = (float(np.mean([v[i] for v in vals])) for i in range(3))
    low = _FIELD.render(t, lungs, bright, turb)
    img = Image.fromarray(low).resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(2))
    overlay(img, s, t, lungs)
    return img


def render_chunk(args):
    segs, t0, t1, path = args
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "21",
         "-pix_fmt", "yuv420p", "-g", str(FPS * 4), str(path)], stdin=subprocess.PIPE)
    for i in range(int(round(t0 * FPS)), int(round(t1 * FPS))):
        ff.stdin.write(render_frame(segs, i / FPS).tobytes())
    ff.stdin.close()
    ff.wait()
    return path


def main():
    args = sys.argv[1:]
    preview = None
    if args and args[0] == "--preview":
        preview = (float(args[1]), float(args[2]))
    CACHE.mkdir(parents=True, exist_ok=True)
    b, marks = build()
    total = b.t
    print(f"total {total / 60:.1f} min", {k: f"{v / 60:.2f}" for k, v in marks.items()}, flush=True)
    wav = CACHE / "session.wav"
    if not (preview and wav.exists()):
        sf.write(wav, mix(b, marks, total), SR, subtype="PCM_16")
    print("audio done", flush=True)

    t0, t1 = preview if preview else (0.0, total)
    out = (CACHE / "preview.mp4") if preview else (ROOT / "renders" / f"theta-identity-v2{'' if ASPECT == '9x16' else '-16x9'}.mp4")
    workers = os.cpu_count() or 4
    bounds = np.linspace(t0, t1, workers + 1)
    bounds = [round(x * FPS) / FPS for x in bounds]
    jobs = [(b.segs, bounds[i], bounds[i + 1], CACHE / f"chunk{i}.mp4") for i in range(workers)]
    with ProcessPoolExecutor(workers) as ex:
        parts = list(ex.map(render_chunk, jobs))
    lst = CACHE / "chunks.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                    "-ss", str(t0), "-t", str(t1 - t0), "-i", str(wav), "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", str(out)],
                   check=True)
    print("wrote", out, flush=True)


if __name__ == "__main__":
    main()
