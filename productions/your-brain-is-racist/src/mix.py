"""Sound: narration + one bed + the brief's diegetic layers. Every sound is synthesized here
(no samples, nothing licensed, nothing copyrighted). Cue times come from cues.json, which
film.py writes from the same clock as the picture.

  python3 src/mix.py   -> audio/narration.wav (timed to picture), audio/mix_premaster.wav
"""
import os, sys, json, math
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, sosfiltfilt
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from timing import TL, ROOT, OFF
SR = 48000; rng = np.random.default_rng(12)
tl = TL(); C = json.load(open(f"{ROOT}/cues.json")); N = int(math.ceil(C["end"] * SR))
def db(x): return 10 ** (x / 20)
def bp(x, lo, hi, order=2):
    if lo and hi: sos = butter(order, [lo, hi], "bp", fs=SR, output="sos")
    elif lo: sos = butter(order, lo, "hp", fs=SR, output="sos")
    else: sos = butter(order, hi, "lp", fs=SR, output="sos")
    return sosfilt(sos, x)
def env_seg(a, b, fin=1.0, fout=1.0):
    """Gain envelope: 1 between a and b (seconds), raised-cosine fades."""
    e = np.zeros(N); i0, i1 = int(a * SR), min(N, int(b * SR)); n = i1 - i0
    if n <= 0: return e
    seg = np.ones(n); fi, fo = min(n // 2, int(fin * SR)), min(n // 2, int(fout * SR))
    if fi: seg[:fi] = 0.5 - 0.5 * np.cos(np.pi * np.arange(fi) / fi)
    if fo: seg[-fo:] = 0.5 + 0.5 * np.cos(np.pi * np.arange(fo) / fo)
    e[i0:i1] = seg; return e
def place(buf, x, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N or i < 0: return
    n = min(len(x), N - i); l, r = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
    buf[i:i + n, 0] += x[:n] * gain * l * 1.414; buf[i:i + n, 1] += x[:n] * gain * r * 1.414
def stereo_noise(n): return rng.standard_normal((n, 2))
def brown(n):
    x = np.cumsum(rng.standard_normal(n)); x = bp(x, 20, None); return x / (np.abs(x).max() + 1e-9)
tt = np.arange(N) / SR

# ---------------------------------------------------------------- narration, timed to picture
dry, sr = sf.read(f"{ROOT}/audio/narration_dry.wav"); assert sr == SR
parts = []; last = 0
for at, extra in tl.cuts:                      # the same extra silences the picture clock uses
    i = int(at * SR); parts += [dry[last:i], np.zeros(int(round(extra * SR)))]; last = i
parts.append(dry[last:]); nar = np.concatenate([np.zeros(int(OFF * SR))] + parts)
nar = np.pad(nar, (0, max(0, N - len(nar))))[:N]
sf.write(f"{ROOT}/audio/narration.wav", (nar * db(-3)).astype(np.float32), SR)

# speech envelope for ducking (5 ms attack, 350 ms release)
ab = np.abs(nar); blk = 240; e = ab[:N // blk * blk].reshape(-1, blk).max(1); sm = np.zeros_like(e); v = 0.0
for i, x in enumerate(e):
    v = x if x > v else v * math.exp(-blk / (0.35 * SR)); sm[i] = v
speech = np.clip(np.repeat(sm, blk) / 0.08, 0, 1); speech = np.pad(speech, (0, N - len(speech)))
speech = sosfiltfilt(butter(1, 6, "lp", fs=SR, output="sos"), speech).clip(0, 1)
def duck(depth_db): return db(-depth_db * speech)[:, None]

sfx = np.zeros((N, 2))

# ---------------------------------------------------------------- the bed: low sustained pad, A minor, barely there
bed = np.zeros((N, 2))
for f, a, det in ((55.0, 1.0, 0.07), (82.41, 0.55, 0.05), (110.0, 0.5, 0.11), (130.81, 0.32, 0.09), (164.81, 0.14, 0.13)):
    for ch, sgn in ((0, -1), (1, 1)):
        lfo = 0.75 + 0.25 * np.sin(2 * np.pi * (0.031 + det * 0.2) * tt + f + ch)
        bed[:, ch] += a * lfo * (np.sin(2 * np.pi * (f + sgn * det) * tt) + 0.25 * np.sin(2 * np.pi * 2 * (f + sgn * det) * tt + 1.0))
air = stereo_noise(N); air[:, 0] = bp(air[:, 0], 150, 600); air[:, 1] = bp(air[:, 1], 150, 600); bed += 0.5 * air
benv = sum(env_seg(a, b, 2.5, 2.0) for a, b in C["bed"])
bed *= benv[:, None] * db(-35) * duck(12)               # ducked 12 dB under speech

# ---------------------------------------------------------------- hook: one sub hit under line one. Nothing under line two.
n = int(1.3 * SR); x = np.arange(n) / SR
sub = np.sin(2 * np.pi * (38 * x + (62 - 38) * 0.12 * (1 - np.exp(-x / 0.12)))) * np.exp(-x / 0.33)
sub[:int(0.004 * SR)] *= np.linspace(0, 1, int(0.004 * SR)); sub += 0.25 * bp(rng.standard_normal(n), None, 180) * np.exp(-x / 0.05)
place(sfx, sub, C["sub"], db(-9))

# ---------------------------------------------------------------- broadcast hiss that thickens as the stack grows
for a, b, lv in C["hiss"]:
    hs = stereo_noise(N)
    for ch in (0, 1):
        hs[:, ch] = bp(hs[:, ch], 1800, 7500) + 0.5 * bp(rng.standard_normal(N), 300, 1200) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.21 * tt + ch))
    hs += 0.05 * (np.sin(2 * np.pi * 60 * tt) + 0.5 * np.sin(2 * np.pi * 180 * tt))[:, None]
    grow = np.clip((tt - a) / max(1e-6, (b - a) * 0.8), 0, 1) ** 1.6 if lv == 1.0 else 1.0
    sfx += hs * (env_seg(a, b, 1.0, 1.2) * (0.12 + 0.88 * grow))[:, None] * db(-38) * lv * duck(5)

# ---------------------------------------------------------------- the street: distant traffic, footsteps that change surface, a breath
def step(surface, bright=1.0):
    n = int(0.16 * SR); x = np.arange(n) / SR; w = rng.standard_normal(n)
    if surface == "sidewalk":      # hard, short, a little click
        s = 0.9 * bp(w, 90, 260) * np.exp(-x / 0.035) + 0.55 * bp(w, 1400, 3600) * np.exp(-x / 0.012) * bright
    elif surface == "asphalt":     # duller, grittier, longer
        s = 1.0 * bp(w, 70, 200) * np.exp(-x / 0.05) + 0.5 * bp(w, 500, 1600) * np.exp(-x / 0.045)
    else:                          # leather sole, the other walker
        s = 0.5 * bp(w, 120, 300) * np.exp(-x / 0.03) + 0.9 * bp(w, 2000, 4500) * np.exp(-x / 0.008)
    return s / (np.abs(s).max() + 1e-9)
wk = C["walk"]; per = 2 * math.pi / (5.2 * wk["v"]); c0, c1 = wk["cam"]
def cam_x(t):
    u = min(1, max(0, (t - c0) / (c1 - c0))); u = 4 * u ** 3 if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2
    return -5.4 * u
steps = []
for si, (a, b) in enumerate(C["street"]):
    k = math.ceil((a + 0.5 - wk["t0"] - (1.5 * math.pi) / (5.2 * wk["v"])) / per)
    while True:
        t = wk["t0"] + (1.5 * math.pi) / (5.2 * wk["v"]) + k * per
        if t > b - 0.4: break
        surf = "asphalt" if (si == 0 and -5.0 < cam_x(t) < -0.5) else "sidewalk"
        place(sfx, step(surf), t, db(-25) * (0.9 + 0.2 * rng.random()), pan=0.18 * (1 if k % 2 else -1)); steps.append((round(t, 3), surf)); k += 1
    tr = np.stack([brown(N), brown(N)], 1)
    for ch in (0, 1): tr[:, ch] = bp(tr[:, ch], 40, 420) * (0.65 + 0.35 * np.sin(2 * np.pi * 0.07 * tt + 2 * ch + si))
    sfx += tr * env_seg(a, b, 1.5, 0.6)[:, None] * db(-27) * duck(4)
n = int(1.5 * SR); x = np.arange(n) / SR
br = bp(rng.standard_normal(n), 500, 2600) * (np.exp(-((x - 0.35) / 0.2) ** 2) * 0.8 + np.exp(-((x - 1.0) / 0.26) ** 2))
place(sfx, br / np.abs(br).max(), C["breath"], db(-33))
for j in range(5):                # the second man's steps as he passes on your side
    place(sfx, step("leather"), C["pass2"] - (4 - j) * 0.56, db(-40 + j * 3.0), pan=0.1 + 0.15 * j)

# ---------------------------------------------------------------- the traffic stop: idle, radio very low, a seatbelt, one tone that rises and cuts
a, b = C["stop"]
idle = np.zeros(N); f0 = 31.0
ph = 2 * np.pi * np.cumsum(f0 * (1 + 0.02 * np.sin(2 * np.pi * 0.6 * tt) + 0.01 * np.sin(2 * np.pi * 7.3 * tt))) / SR
for h, am in ((1, 1.0), (2, 0.6), (3, 0.34), (4, 0.2), (6, 0.1)): idle += am * np.sin(h * ph + h)
idle = idle * (0.8 + 0.2 * np.sin(2 * np.pi * 15.5 * tt)) + 0.5 * bp(rng.standard_normal(N), 60, 500)
sfx += np.stack([idle, np.roll(idle, 37)], 1) * env_seg(a, b, 1.2, 0.8)[:, None] * db(-33) * duck(4)
radio = np.zeros(N); t = a + 2.0
while t < b - 3:                  # unintelligible on purpose: shaped noise, squelch, gaps
    d = rng.uniform(0.9, 2.4); i0 = int(t * SR); n = int(d * SR); x = np.arange(n) / SR
    syl = np.clip(np.sin(2 * np.pi * rng.uniform(3.2, 5.0) * x + rng.uniform(0, 6)), 0, 1) ** 0.6 * (0.6 + 0.4 * np.sin(2 * np.pi * 0.9 * x))
    car = np.sign(np.sin(2 * np.pi * np.cumsum(rng.uniform(110, 150) * (1 + 0.15 * np.sin(2 * np.pi * 2.1 * x))) / SR))
    v = bp(car * syl + 0.35 * rng.standard_normal(n) * syl, 500, 2400, 3)
    v[:int(0.03 * SR)] += bp(rng.standard_normal(int(0.03 * SR)), 1500, 4000) * 2; v[-int(0.05 * SR):] += bp(rng.standard_normal(int(0.05 * SR)), 1500, 4000) * 1.5
    radio[i0:i0 + n] += v[:max(0, min(n, N - i0))]; t += d + rng.uniform(3.5, 8.0)
radio /= np.abs(radio).max() + 1e-9
place(sfx, radio, 0, db(-41), pan=-0.45)
sfx *= 1.0
n = int(0.25 * SR); x = np.arange(n) / SR
clk = bp(rng.standard_normal(n), 2500, 7000) * (np.exp(-x / 0.004) + 0.7 * np.exp(-np.maximum(0, x - 0.09) / 0.006) * (x > 0.09)) + 0.4 * np.sin(2 * np.pi * 1900 * x) * np.exp(-x / 0.01)
place(sfx, clk / np.abs(clk).max(), C["belt"], db(-26), pan=0.4)
a, b = C["tone"]; n = int((b - a) * SR); x = np.arange(n) / n
tone = np.sin(2 * np.pi * np.cumsum(58 * (1.72 ** x)) / SR) + 0.3 * np.sin(2 * np.pi * np.cumsum(116 * (1.72 ** x)) / SR)
tone *= x ** 1.5; tone[-int(0.006 * SR):] *= np.linspace(1, 0, int(0.006 * SR))            # rises, then cuts
place(sfx, tone, a, db(-17))

# ---------------------------------------------------------------- the observer: the bed is out. Room tone only.
a, b = C["observer"]; rt = stereo_noise(N)
for ch in (0, 1): rt[:, ch] = bp(rt[:, ch], 60, 700)
sfx += rt * env_seg(a, b, 1.5, 1.5)[:, None] * db(-50)

# ---------------------------------------------------------------- close: one soft settle tone, under 300 ms
n = int(0.28 * SR); x = np.arange(n) / SR
st = (np.sin(2 * np.pi * 220 * x) + 0.5 * np.sin(2 * np.pi * 330 * x)) * np.exp(-((x - 0.07) / 0.075) ** 2) * (x < 0.28)
place(sfx, st, C["settle"], db(-22))

mix = np.stack([nar, nar], 1) * db(-3) + bed + sfx
tail = int(0.4 * SR); mix[-tail:] *= np.linspace(1, 0, tail)[:, None]
print("premaster peak dBFS", round(20 * math.log10(np.abs(mix).max()), 2), "steps", len(steps), "asphalt", sum(1 for s in steps if s[1] == "asphalt"))
sf.write(f"{ROOT}/audio/mix_premaster.wav", mix.astype(np.float32), SR)
sf.write(f"{ROOT}/audio/sfx_bed_only.wav", (bed + sfx).astype(np.float32), SR)
json.dump({"steps": steps}, open(f"{ROOT}/audio/steps.json", "w"))
