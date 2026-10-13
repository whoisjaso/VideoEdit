"""Synthesized scene sounds for the visualizations: background beds that fade in under a scene,
and one-shot effects placed on a line. Everything is generated from noise and oscillators, so there
is nothing to license, and every bed loops without a seam.

Beds:     morning, house, office, hall, gym, drive, beach, lot
One-shots: door, engine, keys, clank, rack, steps, phone, wave, typing, laptop, pen, slide, chain, watch
"""
import numpy as np

SR = 48000


def _filt(x, lo=None, hi=None, order=2):
    spec = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    g = np.ones_like(f)
    if hi:
        g /= 1 + (f / hi) ** (2 * order)
    if lo:
        g /= 1 + (lo / np.maximum(f, 1)) ** (2 * order)
    return np.fft.irfft(spec * g, len(x)).astype(np.float32)


def _norm(x, peak=1.0):
    return (x / (np.max(np.abs(x)) + 1e-9) * peak).astype(np.float32)


def _st(x, pan=0.5):
    return np.stack([x * np.sqrt(1 - pan), x * np.sqrt(pan)], axis=1).astype(np.float32)


def _place(buf, x, at, gain=1.0):
    i = int(at * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(x))
    buf[i:j] += x[: j - i] * gain


# ---------------------------------------------------------------- one-shots

def chirp(rng):
    d = rng.uniform(0.05, 0.14)
    n = int(d * SR)
    t = np.arange(n) / SR
    f0, f1 = rng.uniform(2800, 5200), rng.uniform(2400, 6000)
    f = f0 + (f1 - f0) * (t / d) ** rng.uniform(0.5, 2)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / d) ** 2
    return x.astype(np.float32)


def bird_phrase(rng):
    parts = []
    for _ in range(rng.integers(2, 6)):
        parts.append(chirp(rng))
        parts.append(np.zeros(int(rng.uniform(0.03, 0.12) * SR), np.float32))
    return np.concatenate(parts)


def gull(rng):
    d = rng.uniform(0.5, 0.9)
    n = int(d * SR)
    t = np.arange(n) / SR
    f = 1500 - 500 * (t / d) + 60 * np.sin(2 * np.pi * 9 * t)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.25 * np.sin(3 * ph)
    env = np.minimum(1, t / 0.05) * np.exp(-t / (d * 0.6))
    return _filt((x * env).astype(np.float32), 600, 4500)


def wave(rng, dur=None):
    """One wave: the swell builds, breaks into a wash, then hisses back over the sand."""
    d = dur or rng.uniform(7, 11)
    n = int(d * SR)
    t = np.arange(n) / SR
    noise = rng.standard_normal(n).astype(np.float32)
    low = _filt(noise, 40, 500)
    mid = _filt(noise, 300, 2500)
    hiss = _filt(rng.standard_normal(n).astype(np.float32), 2000, 9000)
    pk = rng.uniform(0.32, 0.42)
    swell = np.where(t < pk * d, (t / (pk * d)) ** 2.2, np.exp(-(t - pk * d) / (d * 0.22)))
    wash = np.clip((t - pk * d * 0.9) / (d * 0.1), 0, 1) * np.exp(-np.maximum(0, t - pk * d) / (d * 0.35))
    retreat = np.clip((t - pk * d * 1.3) / (d * 0.2), 0, 1) * np.exp(-np.maximum(0, t - pk * d * 1.3) / (d * 0.3))
    x = _norm(low) * swell * 0.9 + _norm(mid) * wash * 0.55 + _norm(hiss) * retreat * 0.22
    fade = np.minimum(1, (d - t) / 1.0)
    return (x * fade).astype(np.float32)


def door():
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(2)
    thud = _filt(rng.standard_normal(n).astype(np.float32), 30, 260) * np.exp(-t / 0.07)
    body = np.sin(2 * np.pi * 72 * t) * np.exp(-t / 0.12) * 0.6
    latch = _filt(rng.standard_normal(n).astype(np.float32), 2500, 8000) * np.exp(-np.maximum(0, t - 0.012) / 0.008) * (t > 0.012)
    return _norm(_norm(thud) + body + 0.25 * _norm(latch), 0.9)


def engine(dur=7.0, seed=4):
    """A V8 coming to life: starter, catch, a blip of revs, then a deep idle burble."""
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    rpm = np.interp(t, [0, 0.7, 0.9, 1.4, 2.2, dur], [0, 0, 1100, 2600, 750, 700])
    rpm += 25 * np.sin(2 * np.pi * 0.7 * t)
    f = rpm / 60 * 4  # firing frequency of a V8
    jitter = 1 + 0.08 * _filt(rng.standard_normal(n).astype(np.float32), None, 30) / 0.2
    ph = 2 * np.pi * np.cumsum(f * jitter) / SR
    pulses = sum(np.sin(k * ph) / k ** 0.8 * (1 + 0.3 * np.sin(k * 1.7)) for k in range(1, 9))
    rumble = _filt(pulses.astype(np.float32), 25, 700)
    exhaust = _filt(rng.standard_normal(n).astype(np.float32), 60, 900) * 0.35 * np.clip(rpm / 2600, 0.2, 1)
    starter = (np.sin(2 * np.pi * 180 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 11 * t)) ** 2
               * np.clip((0.85 - t) / 0.1, 0, 1) * np.clip(t / 0.05, 0, 1) * 0.3)
    on = np.clip((t - 0.7) / 0.08, 0, 1)
    loud = 0.45 + 0.55 * np.clip(rpm / 2600, 0, 1)   # louder as it revs
    x = (_norm(rumble) * 0.9 + exhaust) * on * loud + starter
    x *= np.minimum(1, (dur - t) / 1.5)
    return _norm(x.astype(np.float32), 0.95)


def keys():
    rng = np.random.default_rng(9)
    n = int(0.8 * SR)
    out = np.zeros(n, np.float32)
    t = np.arange(int(0.25 * SR)) / SR
    for k in range(7):
        f = rng.uniform(3000, 7500)
        x = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 1.48 * t)) * np.exp(-t / 0.04)
        _place(out, x.astype(np.float32), rng.uniform(0, 0.5), rng.uniform(0.3, 1))
    return _norm(out, 0.6)


def clank(seed=1, heavy=False):
    rng = np.random.default_rng(seed)
    d = 1.6 if heavy else 1.0
    n = int(d * SR)
    t = np.arange(n) / SR
    base = rng.uniform(380, 520) * (0.7 if heavy else 1)
    x = np.zeros(n)
    for ratio, amp, tau in ((1, 1, 0.5), (2.41, 0.6, 0.3), (4.3, 0.4, 0.18), (6.8, 0.25, 0.1)):
        x += amp * np.sin(2 * np.pi * base * ratio * t + rng.uniform(0, 6)) * np.exp(-t / (tau * d))
    hit = _filt(rng.standard_normal(n).astype(np.float32), 200, 5000) * np.exp(-t / 0.012)
    thump = np.sin(2 * np.pi * 60 * t) * np.exp(-t / 0.08) * (1.0 if heavy else 0.4)
    return _norm((x * 0.6 + _norm(hit) * 0.5 + thump).astype(np.float32), 0.9)


def steps(count=4, seed=3):
    rng = np.random.default_rng(seed)
    n = int((count * 0.55 + 0.5) * SR)
    out = np.zeros(n, np.float32)
    m = int(0.25 * SR)
    t = np.arange(m) / SR
    for k in range(count):
        x = _filt(rng.standard_normal(m).astype(np.float32), 50, 400) * np.exp(-t / 0.035)
        x += np.sin(2 * np.pi * 95 * t) * np.exp(-t / 0.05) * 0.5
        _place(out, _norm(x), k * 0.55 + rng.uniform(-0.03, 0.03), rng.uniform(0.6, 1))
    return out


def phone():
    n = int(2.2 * SR)
    t = np.arange(n) / SR
    on = ((t % 1.1) < 0.45).astype(np.float32)
    buzz = np.sign(np.sin(2 * np.pi * 165 * t)) * 0.6 + np.sin(2 * np.pi * 330 * t) * 0.3
    rattle = _filt(np.random.default_rng(5).standard_normal(n).astype(np.float32), 800, 4000) * 0.15
    env = _filt(on, None, 40)
    return _norm(_filt((buzz + rattle).astype(np.float32), 100, 3000) * env, 0.7)


def _clicks(n_clicks, dur, lo, hi, decay, seed, spread=None):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    out = np.zeros(n, np.float32)
    m = int(0.06 * SR)
    t = np.arange(m) / SR
    for k in range(n_clicks):
        at = rng.uniform(0, dur - 0.08) if spread is None else spread[k]
        x = _filt(rng.standard_normal(m).astype(np.float32), lo, hi) * np.exp(-t / decay)
        _place(out, _norm(x), at, rng.uniform(0.4, 1))
    return out


def typing(dur=3.2, seed=21):
    """Keys on a laptop: quick soft clicks in bursts, the odd heavier space bar."""
    rng = np.random.default_rng(seed)
    times, t = [], 0.1
    while t < dur - 0.1:
        times.append(t)
        t += rng.uniform(0.07, 0.18) if rng.random() > 0.12 else rng.uniform(0.35, 0.6)
    x = _clicks(len(times), dur, 1500, 7000, 0.008, seed, times)
    for t in times[::7]:   # space bar: a lower thock
        _place(x, (np.sin(2 * np.pi * 180 * np.arange(int(0.05 * SR)) / SR)
                   * np.exp(-np.arange(int(0.05 * SR)) / SR / 0.012)).astype(np.float32), t, 0.4)
    return _norm(x, 0.6)


def laptop():
    """A laptop lid closing: a soft hinge swish, then a muted clap."""
    n = int(0.8 * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(31)
    swish = _filt(rng.standard_normal(n).astype(np.float32), 800, 4000) * np.exp(-((t - 0.15) / 0.09) ** 2) * 0.3
    clap = _filt(rng.standard_normal(n).astype(np.float32), 120, 1500) * np.exp(-np.maximum(0, t - 0.32) / 0.03) * (t > 0.32)
    return _norm(swish + _norm(clap), 0.7)


def pen(dur=2.4, seed=41):
    """A signature: the nib scratching in quick strokes."""
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    scratch = _filt(rng.standard_normal(n).astype(np.float32), 2500, 8000)
    strokes = np.clip(np.sin(2 * np.pi * rng.uniform(4, 6) * t + 3 * np.sin(2 * np.pi * 1.3 * t)), 0, 1) ** 2
    env = np.minimum(1, t / 0.1) * np.minimum(1, (dur - t) / 0.2)
    return _norm(_norm(scratch) * strokes * env, 0.5)


def slide(seed=51):
    """Paper or keys sliding across a desk."""
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(seed)
    x = _filt(rng.standard_normal(n).astype(np.float32), 600, 5000) * np.sin(np.pi * t / 0.9) ** 2
    return _norm(x, 0.5)


def chain(seed=61):
    """A gold chain: a few small, bright clinks, softer than keys."""
    rng = np.random.default_rng(seed)
    n = int(1.0 * SR)
    out = np.zeros(n, np.float32)
    tt = np.arange(int(0.3 * SR)) / SR
    for k in range(10):
        f = rng.uniform(2200, 5200)
        x = (np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(2 * np.pi * f * 2.3 * tt)) * np.exp(-tt / 0.05)
        _place(out, x.astype(np.float32), rng.uniform(0, 0.7) ** 1.5, rng.uniform(0.2, 0.8))
    return _norm(out, 0.45)


def watch():
    """A watch clasp: two tiny metal clicks."""
    return _norm(_clicks(2, 0.5, 3000, 9000, 0.004, 71, [0.05, 0.22]), 0.5)


def murmur(dur, rng):
    """A room full of people talking quietly: many voices, none of them words."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n, np.float32)
    for v in range(14):
        noise = rng.standard_normal(n).astype(np.float32)
        f1, f2 = rng.uniform(350, 800), rng.uniform(1000, 2400)
        voiced = _filt(noise, f1 * 0.7, f1 * 1.4) + 0.6 * _filt(noise, f2 * 0.8, f2 * 1.2)
        syll = np.clip(np.sin(2 * np.pi * rng.uniform(3, 5.5) * t + rng.uniform(0, 6)), 0, 1)
        phrase = np.clip(np.sin(2 * np.pi * rng.uniform(0.15, 0.35) * t + rng.uniform(0, 6)) + 0.3, 0, 1)
        out += _norm(voiced) * syll * phrase * rng.uniform(0.4, 1)
    return _norm(out)


ONESHOTS = {
    "door": lambda: _st(door()),
    "engine": lambda: _st(engine()),
    "keys": lambda: _st(keys(), 0.6),
    "clank": lambda: _st(clank(1), 0.4),
    "rack": lambda: _st(clank(7, heavy=True), 0.55),
    "steps": lambda: _st(steps(), 0.45),
    "phone": lambda: _st(phone(), 0.55),
    "wave": lambda: _st(wave(np.random.default_rng(11), 9.0)),
    "typing": lambda: _st(typing(), 0.45),
    "laptop": lambda: _st(laptop(), 0.5),
    "pen": lambda: _st(pen(), 0.55),
    "slide": lambda: _st(slide(), 0.5),
    "chain": lambda: _st(chain(), 0.5),
    "watch": lambda: _st(watch(), 0.55),
}


# ---------------------------------------------------------------- beds

def bed(name, dur, seed=0):
    """A stereo ambience of `dur` seconds."""
    rng = np.random.default_rng(seed + sum(map(ord, name)))
    n = int(dur * SR)
    out = np.zeros((n, 2), np.float32)
    room = _filt(rng.standard_normal(n).astype(np.float32), 40, 900)
    room = _norm(room) * 0.05

    def scatter(fn, every, gain, pan_range=(0.15, 0.85)):
        at = rng.uniform(0, every)
        while at < dur:
            x = fn()
            p = rng.uniform(*pan_range)
            _place(out, _st(x, p), at, gain * rng.uniform(0.5, 1))
            at += rng.uniform(every * 0.5, every * 1.5)

    if name in ("morning", "house", "lot"):
        wind = _norm(_filt(rng.standard_normal(n).astype(np.float32), 150, 1200))
        gust = 0.5 + 0.5 * np.interp(np.arange(n), np.linspace(0, n, 12), rng.uniform(0, 1, 12))
        level = {"morning": 0.10, "house": 0.03, "lot": 0.12}[name]
        out += _st(wind * gust * level)
        scatter(lambda: bird_phrase(rng), {"morning": 2.5, "house": 5.0, "lot": 4.0}[name],
                {"morning": 0.22, "house": 0.10, "lot": 0.14}[name])
        if name == "lot":
            traffic = _norm(_filt(rng.standard_normal(n).astype(np.float32), 40, 300))
            out += _st(traffic * 0.08)
        out += _st(room)
    elif name == "office":
        # late, quiet room: air handling, a faint fridge hum, the odd car far away
        hvac = _norm(_filt(rng.standard_normal(n).astype(np.float32), 60, 500)) * 0.08
        hum = np.sin(2 * np.pi * 120 * np.arange(n) / SR).astype(np.float32) * 0.01
        out += _st(hvac + hum + room)
        scatter(lambda: _filt(rng.standard_normal(int(4 * SR)).astype(np.float32), 50, 400)
                * np.sin(np.pi * np.arange(int(4 * SR)) / (4 * SR)) ** 2, 18.0, 0.05)
    elif name == "hall":
        # a full room: people murmuring, settling into silence over the first ten seconds
        t = np.arange(n) / SR
        settle = np.clip(1 - t / 10.0, 0.06, 1) ** 1.5
        out += _st(murmur(dur, rng) * settle * 0.5)
        out += _st(_norm(_filt(rng.standard_normal(n).astype(np.float32), 40, 700)) * 0.05)
    elif name == "gym":
        hum = np.sin(2 * np.pi * 60 * np.arange(n) / SR) * 0.015
        out += _st(room * 1.6 + hum)
        scatter(lambda: clank(int(rng.integers(0, 99)), heavy=rng.random() < 0.3), 4.0, 0.18)
    elif name == "drive":
        road = _norm(_filt(rng.standard_normal(n).astype(np.float32), 30, 350)) * 0.35
        tire = _norm(_filt(rng.standard_normal(n).astype(np.float32), 500, 2200)) * 0.06
        t = np.arange(n) / SR
        f = 68 + 4 * np.sin(2 * np.pi * 0.05 * t)
        ph = 2 * np.pi * np.cumsum(f) / SR
        hum = _filt((np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.25 * np.sin(4 * ph)).astype(np.float32), 30, 400) * 0.12
        out += _st(road + tire + hum)
    elif name == "beach":
        at = 0.0
        while at < dur:
            w = wave(rng)
            _place(out, _st(w, rng.uniform(0.3, 0.7)), at, 0.55)
            at += rng.uniform(5.5, 8.5)
        wind = _norm(_filt(rng.standard_normal(n).astype(np.float32), 200, 2000)) * 0.05
        out += _st(wind)
        scatter(lambda: gull(rng), 14.0, 0.06)
    rms = np.sqrt(np.mean(out ** 2)) + 1e-9
    return (out * (0.05 / rms)).astype(np.float32)   # every bed at the same loudness (-26 dB RMS)
