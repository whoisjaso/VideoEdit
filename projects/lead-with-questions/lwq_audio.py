"""Audio for Lead With Questions: voices, score, binaural/isochronic beds, noise, rain, birds, SFX, mix, master.

    python projects/lead-with-questions/lwq_audio.py night|morning      # needs timeline.json (lwq_timeline.py)

Writes /tmp/lwq/<cut>/STP-LWQ-M-<CUT>-<432|440>-<HP|SPK>.wav (48 kHz / 24-bit) plus stems.
Every level follows spec §11.1, measured with the BS.1770 meter below.
"""
import json
import os
import sys
from pathlib import Path

import numpy as np
import scipy.signal as ss
import soundfile as sf
from scipy.ndimage import maximum_filter1d, minimum_filter1d, uniform_filter1d

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "theta-identity"))
import build                                                   # noqa: E402
from lwq_timeline import SR, WORK, VOICE_A, VOICE_B, tts, emb_shift, CUTS   # noqa: E402

# ================================================================ metering (ITU-R BS.1770-4)

KB1 = ([1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585])
KB2 = ([1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621])


def _blocks(x, t0=0.0, t1=None, win=0.4, step=0.1):
    if x.ndim == 1:
        x = x[:, None]
    a = int(t0 * SR)
    b = len(x) if t1 is None else min(len(x), int(t1 * SR))
    y = ss.lfilter(*KB2, ss.lfilter(*KB1, x[a:b], axis=0), axis=0)
    p = np.sum(y.astype(np.float64) ** 2, axis=1)
    c = np.concatenate([[0], np.cumsum(p)])
    w, s = int(win * SR), int(step * SR)
    starts = np.arange(0, max(1, len(p) - w + 1), s)
    if len(p) < w:
        return np.array([c[-1] / max(1, len(p))])
    return (c[starts + w] - c[starts]) / w


def lufs(x, t0=0.0, t1=None):
    """Integrated (gated) loudness."""
    z = _blocks(x, t0, t1)
    lk = -0.691 + 10 * np.log10(z + 1e-20)
    z = z[lk > -70]
    if not len(z):
        return -120.0
    rel = -0.691 + 10 * np.log10(np.mean(z)) - 10
    z2 = z[-0.691 + 10 * np.log10(z) > rel]
    return float(-0.691 + 10 * np.log10(np.mean(z2)))


def lufs_m_max(x, t0=0.0, t1=None):
    z = _blocks(x, t0, t1)
    return float(-0.691 + 10 * np.log10(np.max(z) + 1e-20))


def db(v):
    return 10 ** (v / 20)


# ================================================================ small DSP

def butter(x, fc, kind="low", order=2):
    sos = ss.butter(order, fc, kind, fs=SR, output="sos")
    return ss.sosfilt(sos, x, axis=0).astype(np.float32)


def peaking(x, f0, gain_db, q=1.0):
    A = 10 ** (gain_db / 40)
    w = 2 * np.pi * f0 / SR
    al = np.sin(w) / (2 * q)
    b = [1 + al * A, -2 * np.cos(w), 1 - al * A]
    a = [1 + al / A, -2 * np.cos(w), 1 - al / A]
    return ss.lfilter(np.array(b) / a[0], np.array(a) / a[0], x, axis=0).astype(np.float32)


def shelf(x, f0, gain_db, high=True):
    A = 10 ** (gain_db / 40)
    w = 2 * np.pi * f0 / SR
    al = np.sin(w) / 2 * np.sqrt(2)
    c = np.cos(w)
    if high:
        b = [A * ((A + 1) + (A - 1) * c + 2 * np.sqrt(A) * al), -2 * A * ((A - 1) + (A + 1) * c),
             A * ((A + 1) + (A - 1) * c - 2 * np.sqrt(A) * al)]
        a = [(A + 1) - (A - 1) * c + 2 * np.sqrt(A) * al, 2 * ((A - 1) - (A + 1) * c),
             (A + 1) - (A - 1) * c - 2 * np.sqrt(A) * al]
    else:
        b = [A * ((A + 1) - (A - 1) * c + 2 * np.sqrt(A) * al), 2 * A * ((A - 1) - (A + 1) * c),
             A * ((A + 1) - (A - 1) * c - 2 * np.sqrt(A) * al)]
        a = [(A + 1) + (A - 1) * c + 2 * np.sqrt(A) * al, -2 * ((A - 1) + (A + 1) * c),
             (A + 1) + (A - 1) * c - 2 * np.sqrt(A) * al]
    return ss.lfilter(np.array(b) / a[0], np.array(a) / a[0], x, axis=0).astype(np.float32)


def pan_gains(p):
    """p in [-1, 1] (-0.6 = 60% left). Equal power."""
    th = (p + 1) * np.pi / 4
    return np.cos(th), np.sin(th)


def add(buf, x, t, gain=1.0):
    i = int(round(t * SR))
    if i >= len(buf):
        return
    if i < 0:
        x = x[-i:]
        i = 0
    n = min(len(x), len(buf) - i)
    if x.ndim == 1 and buf.ndim == 2:
        buf[i:i + n] += (x[:n, None] * gain)
    else:
        buf[i:i + n] += x[:n] * gain


def cos_fade(n_total, segments):
    """Gain curve from (t, gain) points with raised-cosine interpolation."""
    t = np.arange(n_total) / SR
    g = np.ones(n_total, dtype=np.float32) * segments[0][1]
    for (ta, ga), (tb, gb) in zip(segments, segments[1:]):
        a, b = int(ta * SR), int(tb * SR)
        if b > a:
            x = np.linspace(0, 1, b - a)
            g[a:b] = ga + (gb - ga) * (0.5 - 0.5 * np.cos(np.pi * x))
        g[b:] = gb
    return g


def stereo_ir(sec, t60, seeds=(11, 12), bright=4500, predelay=0.02):
    irs = []
    for s in seeds:
        ir = build.reverb_ir(sec, t60 / 6.9, s, bright=bright)
        irs.append(np.concatenate([np.zeros(int(predelay * SR), np.float32), ir]))
    return irs


def reverb(x, irs, wet):
    """x stereo -> wet signal only."""
    out = np.zeros_like(x)
    for ch in range(2):
        out[:, ch] = build.ola_convolve(x[:, ch].copy(), irs[ch])
    return out * wet


def note(m, a4):
    return a4 * 2 ** ((m - 69) / 12)


# ================================================================ instruments

def pad_chord(freqs, dur, seed, attack=2.0, release=4.0, lp=2500, detune=(-5, 0, 5)):
    n = int((dur + release) * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(seed)
    out = np.zeros((n, 2), np.float32)
    for f in freqs:
        for j, cents in enumerate(detune):
            ff = f * 2 ** (cents / 1200)
            pl, pr = pan_gains([-0.5, 0.0, 0.5][j] * 0.8)
            sig = np.zeros(n, np.float32)
            for k in range(1, 9):
                fk = ff * k
                if fk > 9000:
                    break
                amp = (1 / k) / (1 + (fk / lp) ** 2)
                sig += (amp * np.sin(2 * np.pi * fk * t + rng.uniform(0, 6.28))).astype(np.float32)
            out[:, 0] += sig * pl
            out[:, 1] += sig * pr
    env = np.minimum(1, t / attack) ** 2
    rel = np.clip((t - dur) / release, 0, 1)
    env = env * (0.5 + 0.5 * np.cos(np.pi * rel))
    env[t < attack] = (0.5 - 0.5 * np.cos(np.pi * t[t < attack] / attack))
    return out * env[:, None].astype(np.float32) / (len(freqs) * 3)


def felt_piano(f, dur=5.0, vel=1.0, bright=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    B = 0.0004
    sig = np.zeros(n, np.float32)
    for k in range(1, 9):
        fk = k * f * np.sqrt(1 + B * k * k)
        if fk > 8000:
            break
        amp = (1 / k ** (1.9 - 0.4 * bright)) * np.exp(-t * (0.7 + 0.55 * k))
        sig += (amp * np.sin(2 * np.pi * fk * t)).astype(np.float32)
    att = np.minimum(1, t / 0.012)
    thump = np.random.default_rng(int(f)).standard_normal(n).astype(np.float32) * np.exp(-t / 0.015) * 0.04
    thump = butter(thump, 700)
    sig = (sig * att + thump) * vel
    return sig / (np.max(np.abs(sig)) + 1e-9)


def mallet(f, dur=0.9):
    n = int(dur * SR)
    t = np.arange(n) / SR
    sig = (np.sin(2 * np.pi * f * t) * np.exp(-t / 0.22) + 0.25 * np.sin(2 * np.pi * f * 3.93 * t) * np.exp(-t / 0.05)
           + 0.12 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t / 0.1))
    sig *= np.minimum(1, t / 0.004)
    return (sig / np.max(np.abs(sig))).astype(np.float32)


def bowl(f, dur=9.0, seed=3):
    n = int(dur * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(seed)
    sig = np.zeros(n, np.float32)
    for r, a, tau in [(1, 1.0, 3.2), (2.76, 0.5, 2.4), (5.40, 0.22, 1.6), (8.93, 0.08, 1.0)]:
        for d in (-0.35, 0.35):
            sig += (a * np.exp(-t / tau) * np.sin(2 * np.pi * (f * r + d) * t + rng.uniform(0, 6.28))).astype(np.float32)
    att = 0.5 - 0.5 * np.cos(np.pi * np.minimum(1, t / 0.35))      # no metallic transient
    return (sig * att / np.max(np.abs(sig))).astype(np.float32)


def tubular_bell(f, dur=7.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    sig = np.zeros(n, np.float32)
    for r, a, tau in [(1.0, 1.0, 2.6), (2.0, 0.45, 1.8), (3.01, 0.3, 1.2), (4.17, 0.18, 0.8), (5.43, 0.1, 0.5)]:
        sig += (a * np.exp(-t / tau) * np.sin(2 * np.pi * f * r * t)).astype(np.float32)
    sig *= np.minimum(1, t / 0.006)
    return sig / np.max(np.abs(sig))


def question_tone(lo_m, a4, irs):
    """The paired cue: felt-piano perfect fourth up (lo -> lo+5), ~1.2 s, dark hall tail. Same synth always."""
    n = int(3.6 * SR)
    x = np.zeros(n, np.float32)
    a = felt_piano(note(lo_m, a4), 3.0, bright=0.6)
    b = felt_piano(note(lo_m + 5, a4), 3.0, bright=0.6)
    env = np.ones(len(a), np.float32)
    env[int(0.55 * SR):int(0.8 * SR)] = np.linspace(1, 0, int(0.25 * SR))
    env[int(0.8 * SR):] = 0
    x[:len(a)] += a * env
    env2 = np.ones(len(b), np.float32)
    env2[int(0.7 * SR):int(1.1 * SR)] = np.linspace(1, 0, int(0.4 * SR))
    env2[int(1.1 * SR):] = 0
    x[int(0.5 * SR):int(0.5 * SR) + len(b)] += b * env2
    st = np.stack([x, x], 1)
    st = st * 0.8 + reverb(st, irs, 0.35)[:n]
    return st.astype(np.float32)


def whisper(x):
    """A whisper made from the narrator's own clip: its spectral envelope (cepstrally smoothed) on noise."""
    n_fft, hop = 1024, 256
    win = np.hanning(n_fft).astype(np.float32)
    frames = 1 + (len(x) - n_fft) // hop if len(x) > n_fft else 1
    x = np.pad(x, (0, max(0, n_fft - len(x))))
    rng = np.random.default_rng(len(x))
    out = np.zeros(frames * hop + n_fft, np.float32)
    for i in range(frames):
        seg = x[i * hop: i * hop + n_fft] * win
        if len(seg) < n_fft:
            break
        mag = np.abs(np.fft.rfft(seg)) + 1e-6
        cep = np.fft.irfft(np.log(mag))
        cep[40:-40] = 0
        env = np.exp(np.fft.rfft(cep).real)
        noise = np.fft.rfft(rng.standard_normal(n_fft) * win)
        out[i * hop: i * hop + n_fft] += np.fft.irfft(noise / (np.abs(noise) + 1e-9) * env, n_fft).astype(np.float32) * win
    out = butter(out, 7000)
    out = butter(out, 300, "high")
    out = shelf(out, 5000, -4.0)                                     # hard de-ess
    return out / (np.max(np.abs(out)) + 1e-9)


def noise_riser(dur, seed=21):
    n = int(dur * SR)
    t01 = np.linspace(0, 1, n)

    def shape(f, u):
        fc = 250 * (5500 / 250) ** u
        return 1 / (1 + (f / fc) ** 4) * (f > 80) / np.sqrt(np.maximum(f, 50) / 200)
    a = build.stft_noise(n, shape, seed)
    b = build.stft_noise(n, shape, seed + 1)
    env = (t01 ** 2.2).astype(np.float32)
    st = np.stack([a, b], 1) * env[:, None]
    return st / (np.max(np.abs(st)) + 1e-9)


def whoosh(dur=1.5, seed=31):
    n = int(dur * SR)

    def shape(f, u):
        fc = 500 + 2200 * np.sin(np.pi * u)
        return np.exp(-0.5 * ((f - fc) / (fc * 0.6)) ** 2) * (f < 5000)
    a = build.stft_noise(n, shape, seed)
    b = build.stft_noise(n, shape, seed + 1)
    env = np.sin(np.pi * np.linspace(0, 1, n)) ** 1.5
    st = np.stack([a * env, b * env], 1)
    return (st / np.max(np.abs(st))).astype(np.float32)


def wave_swell(rise, fall, seed):
    """Ocean wash: rises across the inhale, falls across the exhale."""
    n = int((rise + fall + 1.5) * SR)
    tt = np.arange(n) / SR
    env = np.where(tt < rise, 0.5 - 0.5 * np.cos(np.pi * tt / rise),
                   0.5 + 0.5 * np.cos(np.pi * np.clip((tt - rise) / fall, 0, 1)))
    env[tt > rise + fall] = 0

    def shape(f, u):
        uu = u * (rise + fall + 1.5)
        e = np.interp(uu, tt[::480], env[::480])
        fc = 300 + 2300 * e
        return 1 / (1 + (f / fc) ** 2) / np.sqrt(np.maximum(f, 40) / 100) * (f > 40)
    a = build.stft_noise(n, shape, seed)
    b = build.stft_noise(n, shape, seed + 1)
    st = np.stack([a, b], 1) * env[:, None].astype(np.float32)
    return st / (np.max(np.abs(st)) + 1e-9)


def brown(n, seed):
    rng = np.random.default_rng(seed)
    out = np.zeros((n, 2), np.float32)
    for ch in range(2):
        w = rng.standard_normal(n).astype(np.float32)
        out[:, ch] = ss.lfilter([1], [1, -0.997], w)
    out = butter(out, 900)
    out = butter(out, 25, "high")
    return out / np.max(np.abs(out))


def pink(n, seed):
    rng = np.random.default_rng(seed)
    out = np.zeros((n, 2), np.float32)
    for ch in range(2):
        spec = np.fft.rfft(rng.standard_normal(n))
        f = np.fft.rfftfreq(n, 1 / SR)
        spec /= np.sqrt(np.maximum(f, 20))
        out[:, ch] = np.fft.irfft(spec, n).astype(np.float32)
    return out / np.max(np.abs(out))


def rain(dur, seed=41):
    """Light rain on a window: soft broadband wash + rounded droplet grains (3 ms+ attacks: no clicks)."""
    loop = 90.0
    n = int(loop * SR)
    rng = np.random.default_rng(seed)
    base = pink(n, seed)
    base = butter(butter(base, 7000), 350, "high") * 0.5
    am = 1 + 0.2 * build.smooth_noise(n, 0.15, seed)
    base *= am[:, None]
    grains = np.zeros((n, 2), np.float32)
    count = int(loop * 55)
    for i in range(count):
        L = int(rng.uniform(0.006, 0.022) * SR)
        g = rng.standard_normal(L).astype(np.float32)
        fc = rng.uniform(1500, 6000)
        g = ss.lfilter(*ss.butter(2, [fc * 0.7, min(fc * 1.3, 20000)], "band", fs=SR), g).astype(np.float32)
        env = np.sin(np.pi * np.linspace(0, 1, L)) ** 2
        amp = rng.lognormal(-1.2, 0.6) * 0.5
        pl, pr = pan_gains(rng.uniform(-0.9, 0.9))
        s = int(rng.uniform(0, n - L))
        grains[s:s + L, 0] += g * env * amp * pl
        grains[s:s + L, 1] += g * env * amp * pr
    one = base + butter(grains, 8000) * 1.2
    xf = int(5 * SR)
    total = int(dur * SR)
    out = np.zeros((total + n, 2), np.float32)
    pos = 0
    fade = np.linspace(0, 1, xf)[:, None]
    while pos < total:
        seg = one.copy()
        seg[:xf] *= fade
        seg[-xf:] *= 1 - fade
        out[pos:pos + n] += seg
        pos += n - xf
    return out[:total] / np.max(np.abs(out[:total]))


def birds(dur, seed=51):
    n = int(dur * SR)
    rng = np.random.default_rng(seed)
    out = np.zeros((n, 2), np.float32)
    t = 0.5
    while t < dur - 2:
        notes = rng.integers(1, 6)
        f0 = rng.uniform(2600, 4200)
        pl, pr = pan_gains(rng.uniform(-0.8, 0.8))
        amp = rng.uniform(0.3, 1.0)
        tt = t
        for _ in range(notes):
            L = rng.uniform(0.05, 0.14)
            m = int(L * SR)
            u = np.linspace(0, 1, m)
            f = f0 * (1 + rng.uniform(-0.25, 0.35) * u + 0.05 * np.sin(2 * np.pi * rng.uniform(20, 40) * u * L))
            ph = 2 * np.pi * np.cumsum(f) / SR
            s = (np.sin(ph) + 0.15 * np.sin(2 * ph)) * np.sin(np.pi * u) ** 2 * amp
            i = int(tt * SR)
            out[i:i + m, 0] += s * pl
            out[i:i + m, 1] += s * pr
            tt += L + rng.uniform(0.03, 0.12)
        t += rng.uniform(1.5, 5.0)
    out = butter(out, 6000)
    irs = stereo_ir(2.0, 1.4, (61, 62), bright=5000)
    out = out * 0.6 + reverb(out, irs, 0.5)
    return out / np.max(np.abs(out))


def normalize(x, target, t0=0.0, t1=None, momentary=False):
    cur = lufs_m_max(x, t0, t1) if momentary else lufs(x, t0, t1)
    return (x * db(target - cur)).astype(np.float32)


# ================================================================ timeline helpers

def load_tl(cut):
    return json.loads((WORK / cut / "timeline.json").read_text())


def sec_start(tl, sid):
    return next(s["start"] for s in tl["sections"] if s["sid"] == sid)


def unit_by(tl, sid):
    return next(u for u in tl["units"] if u["sid"] == sid)


def says(tl):
    return [e for e in tl["events"] if e["kind"] == "say"]


# ================================================================ voice

def pan_for(cut, tl, e, speaker):
    sec = e["unit"].split(".")[0]
    role = e["role"]
    p = 0.0
    if cut == "night":
        six = next(x["t"] for x in says(tl) if x["unit"] == "N3" and x["text"].startswith("Six."))
        if sec == "N3" and e["t"] >= six - 0.01:
            p = 0.6 if role == "B" else -0.6
        elif sec == "N4":
            p = 0.6 if role == "B" else -0.6
        elif sec == "N5" and role == "B":
            p = 0.3
        elif sec == "N8" and role == "B":
            p = 0.6
    elif role == "B":
        p = 0.3
    if speaker:
        p = {0.6: 0.3, -0.6: -0.3, 0.3: 0.2}.get(p, p)
    return p


def b_offset(cut, sec):
    if cut == "morning":
        return -5.0
    return {"N5": -4.0, "N8": -6.0}.get(sec, -5.0)


def voice_stems(cut, tl, speaker):
    """Returns (stereo voice mix incl. reverb, mono A envelope source)."""
    night = cut == "night"
    total = tl["total"]
    n = int(total * SR)
    dry = np.zeros((n, 2), np.float32)
    send = np.zeros((n, 2), np.float32)
    a_only = np.zeros(n, np.float32)
    target = -20.0 if night else -15.0
    for e in says(tl):
        voice = VOICE_B if e["role"] == "B" else VOICE_A
        x, sr0 = sf.read(WORK / "tts" / e["key"], dtype="float32")
        x = build.resample(x, sr0, SR)
        idx = np.flatnonzero(np.abs(x) > 0.008)
        if len(idx):
            x = x[max(0, idx[0] - 480): idx[-1] + 1440]
        if e["emb"]:
            x = emb_shift(x)
        x = butter(x, 70, "high")
        x = peaking(x, 150, 1.5, 1.0)
        if night:
            x = shelf(x, 8000, -2.0)
        if e["role"] == "B":
            x = shelf(x, 6000, -1.5)
        lv = lufs(np.pad(x, (0, max(0, int(0.45 * SR) - len(x)))))
        g_db = target - lv
        sec = e["unit"].split(".")[0]
        if e["role"] == "B":
            g_db += b_offset(cut, sec) - (2.0 if speaker else 0.0)
        if e["emb"]:
            g_db += 1.0
        if night and e["t"] >= 1440:
            g_db -= min(10.0, (e["t"] - 1440) / 10.0)                 # ~1 dB / 10 s from 24:00
        x = x * db(g_db)
        pl, pr = pan_gains(pan_for(cut, tl, e, speaker))
        st = np.stack([x * pl, x * pr], 1)
        add(dry, st, e["t"])
        wet = (0.09 if night else 0.045) + (0.04 if e["role"] == "B" else 0) - (0.02 if e["emb"] else 0)
        add(send, st, e["t"], wet / 0.1)
        if e["role"] != "B":
            add(a_only, x, e["t"])
    # audible exhales [BR]: -12 dB relative to speech
    for e in tl["events"]:
        if e["kind"] == "br":
            b = build.breath(1.6, False, 77)
            b = b * db(target - 12 - lufs(b))
            add(dry, b, e["t"])
    irs = stereo_ir(2.2, 1.75, (71, 72), bright=5000)
    out = dry + reverb(send, irs, 0.1)
    return out, a_only


def duck_env(a_only, depth_db, release=0.6):
    env = np.abs(a_only)
    env = maximum_filter1d(env, int(0.02 * SR))
    att, rel = np.exp(-1 / (0.08 * SR)), np.exp(-1 / (release * SR))
    # one-pole with separate attack/release, done on a decimated envelope then upsampled
    dec = 240
    e = env[::dec]
    out = np.zeros_like(e)
    a1, r1 = att ** dec, rel ** dec
    prev = 0.0
    for i, v in enumerate(e):
        c = a1 if v > prev else r1
        prev = c * prev + (1 - c) * v
        out[i] = prev
    out = np.interp(np.arange(len(env)) / dec, np.arange(len(out)), out)
    thr = np.percentile(out[out > 1e-4], 50) if np.any(out > 1e-4) else 1
    return db(-depth_db * np.clip(out / thr, 0, 1)).astype(np.float32)


def whisper_stem(cut, tl, a4=None):
    night = cut == "night"
    lines = (["I lead with questions.", "Ask, and let it land.", "My facts are clean.", "One question at a time.",
              "The silence is working.", "Honest questions only.", "Thumb to finger. Ask."] if night else
             ["Ask first.", "Say it clean.", "Let them say it.", "One next step."])
    if night:
        windows = [(sec_start(tl, "N4"), sec_start(tl, "N6")), (sec_start(tl, "N7"), sec_start(tl, "N9"))]
    else:
        windows = [(sec_start(tl, "M3"), sec_start(tl, "M6"))]
    n = int(tl["total"] * SR)
    mono = np.zeros(n, np.float32)
    rng = np.random.default_rng(5)
    clips = [whisper(tts(l, VOICE_A, 0.9)[0]) for l in lines]
    placed = []
    k = 0
    for a, b in windows:
        t = a + 4
        while True:
            c = clips[k % len(clips)]
            if t + len(c) / SR > b - 2:
                break
            add(mono, c, t)
            placed.append((round(t, 2), lines[k % len(clips)]))
            t += len(c) / SR + rng.uniform(6, 10)
            k += 1
    rate = 0.03 if night else 0.05
    tt = np.arange(n) / SR
    p = 0.4 * np.sin(2 * np.pi * rate * tt)
    th = (p + 1) * np.pi / 4
    st = np.stack([mono * np.cos(th), mono * np.sin(th)], 1).astype(np.float32)
    tgt = -34.0 if night else -30.0
    act = [(a, b) for a, b in windows]
    cur = lufs(np.concatenate([st[int(a * SR):int(b * SR)] for a, b in act]))
    return (st * db(tgt - cur)).astype(np.float32), placed


# ================================================================ binaural / isochronic

def beat_points(cut, tl):
    s = {x["sid"]: x["start"] for x in tl["sections"]}
    if cut == "night":
        return [(0, 10), (s["N1"], 10), (s["N2"], 8), (s["N3"], 6), (s["N4"], 5), (s["N5"], 5), (s["N6"], 6),
                (s["N7"], 6), (s["N8"], 5), (s["N9"], 4.5), (1530, 4.0), (1680, 4.0)], 20.0, (1530, 1620)
    return [(0, 6), (s["M1"], 6), (s["M2"], 8), (s["M3"], 8), (s["M4"], 10), (s["M5"], 10), (s["M6"], 12),
            (630, 12)], 10.0, (585, 615)


def carrier(cut, a4):
    return note(53, a4) if cut == "night" else note(62, a4)   # F3 / D4


def binaural(duration_s, carrier_hz, beat_pts, level_dbfs=-40.0, fade_in_s=20.0, fade_out=(None, None)):
    """Spec §11.4 reference generator (phase-continuous, linear glides)."""
    n = int(duration_s * SR)
    t = np.arange(n) / SR
    times, beats = zip(*beat_pts)
    beat = np.interp(t, times, beats)
    left_phase = 2 * np.pi * carrier_hz * t
    right_phase = 2 * np.pi * np.cumsum(carrier_hz + beat) / SR
    amp = 10 ** (level_dbfs / 20)
    env = np.ones(n)
    fi = int(fade_in_s * SR)
    env[:fi] = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, fi))
    if fade_out[0] is not None:
        a, b = int(fade_out[0] * SR), int(fade_out[1] * SR)
        env[a:b] *= 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, b - a))
        env[b:] = 0
    return np.stack([amp * env * np.sin(left_phase), amp * env * np.sin(right_phase)], 1).astype(np.float32)


def isochronic(duration_s, carrier_hz, beat_pts, depth=0.35, fade_in_s=20.0, fade_out=(None, None)):
    """Speaker version: the carrier, smoothly amplitude-modulated (raised cosine, 35% depth) at the beat schedule."""
    n = int(duration_s * SR)
    t = np.arange(n) / SR
    times, beats = zip(*beat_pts)
    beat = np.interp(t, times, beats)
    mod_phase = 2 * np.pi * np.cumsum(beat) / SR
    am = 1 - depth * (0.5 - 0.5 * np.cos(mod_phase))
    env = np.ones(n)
    fi = int(fade_in_s * SR)
    env[:fi] = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, fi))
    if fade_out[0] is not None:
        a, b = int(fade_out[0] * SR), int(fade_out[1] * SR)
        env[a:b] *= 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, b - a))
        env[b:] = 0
    x = (np.sin(2 * np.pi * carrier_hz * t) * am * env).astype(np.float32)
    return np.stack([x, x], 1)


# ================================================================ score

NIGHT_CHORDS = {"Fmaj9": [53, 60, 64, 67, 69], "Dm9": [50, 57, 60, 64, 65], "Bbmaj7#11": [46, 53, 57, 62, 64],
                "Csus2": [48, 55, 60, 62, 67]}
F_PENTA = [65, 67, 69, 72, 74]


def night_score(tl, a4):
    total = tl["total"]
    n = int(total * SR)
    s = {x["sid"]: x["start"] for x in tl["sections"]}
    pad = np.zeros((n, 2), np.float32)
    cache = {}
    t = 0.0
    seq = ["Fmaj9", "Dm9", "Bbmaj7#11", "Csus2"]
    i = 0
    while t < s["N9"]:
        name = seq[i % 4] if t < s["N7"] else ["Fmaj9", "Bbmaj7#11"][i % 2]
        if name not in cache:
            cache[name] = pad_chord([note(m, a4) for m in NIGHT_CHORDS[name]], 8.0, hash(name) % 1000)
        add(pad, cache[name], t)
        t += 8.0
        i += 1
    hold = pad_chord([note(m, a4) for m in NIGHT_CHORDS["Fmaj9"]], total - t, 9, attack=4.0, release=1.0)
    add(pad, hold, t - 2.0)
    asks = [e["t"] for e in says(tl) if e["unit"] == "N7" and e["text"].strip(" .*") == "Ask"]
    g = cos_fade(n, [(0, 0), (8, 1), (s["N6"], 1), (s["N6"] + 8, 0.5), (s["N7"] - 6, 0.5), (s["N7"] + 2, 1),
                     (1440, 1), (1680, 0)])
    tt = np.arange(n) / SR
    for a in asks:                                   # soft F major swell under each anchor
        g *= (1 + 0.4 * np.exp(-0.5 * ((tt - a - 1.0) / 2.0) ** 2)).astype(np.float32)
    pad *= g[:, None]

    # felt piano: N2 motif at 03:00, sparse after; out at 06:00; a few notes in N4; sparse N5
    rng = np.random.default_rng(8)
    piano = np.zeros((n, 2), np.float32)
    notes = [(s["N2"], 65), (s["N2"] + 1.5, 69), (s["N2"] + 3.0, 72)]
    for a, b, lo, hi in [(s["N2"] + 8, s["N3"] - 4, 4, 8), (s["N4"] + 6, s["N5"], 8, 12), (s["N5"] + 4, s["N6"] - 4, 5, 8)]:
        t = a
        idx = 2
        while t < b:
            idx = int(np.clip(idx + rng.integers(-2, 3), 0, 4))
            notes.append((t, F_PENTA[idx]))
            t += rng.uniform(lo, hi)
    for t, m in notes:
        x = felt_piano(note(m, a4), 5.0, vel=rng.uniform(0.6, 0.9), bright=0.5)
        pl, pr = pan_gains(rng.uniform(-0.3, 0.3))
        add(piano, np.stack([x * pl, x * pr], 1), t)
    hall = stereo_ir(6.0, 5.0, (81, 82), bright=3000)
    piano = piano * 0.6 + reverb(piano, hall, 0.55)

    # cello drone F2 (+ soft fifth) from 06:00 through N7, out across N8; sub F1 throughout
    tt32 = tt.astype(np.float64)
    vib = 1 + 0.0025 * np.sin(2 * np.pi * 4.8 * tt32) * build.smooth_noise(n, 0.2, 4)
    f2 = note(41, a4)
    ph = 2 * np.pi * np.cumsum(f2 * vib) / SR
    cello = np.zeros(n, np.float32)
    for k in range(1, 13):
        cello += (np.sin(k * ph) / k * (1 / (1 + (k * f2 / 900) ** 2))).astype(np.float32)
    cello = butter(cello, 1200) * (1 + 0.25 * build.smooth_noise(n, 0.1, 5))
    cg = cos_fade(n, [(0, 0), (s["N3"], 0), (s["N3"] + 6, 1), (s["N8"], 1), (s["N8"] + 50, 0)])
    cello = cello * cg / np.max(np.abs(cello))
    sub = (np.sin(2 * np.pi * note(29, a4) * tt32)).astype(np.float32)
    sub = butter(sub, 35, "high") * cos_fade(n, [(0, 0), (12, 1), (1440, 1), (1680, 0)])

    mix = pad * 1.0 + piano * 0.55 + np.stack([cello, cello], 1) * 0.35 + np.stack([sub, sub], 1) * 0.06
    mix = mix * 0.85 + reverb(mix, stereo_ir(4.0, 3.5, (91, 92), bright=3500), 0.25)
    mix = peaking(mix, 2000, -2.0, 0.7)                                # carve 1-4 kHz under the voice
    return mix.astype(np.float32)


MORNING_CHORDS = {"Dadd9": [50, 57, 62, 64, 66], "A/C#": [49, 52, 57, 61, 64], "Bm7": [47, 54, 57, 62, 66],
                  "Gmaj9": [43, 50, 54, 57, 59], "Asus4": [45, 52, 57, 62, 64]}
ROOT = {"Dadd9": 38, "A/C#": 37, "Bm7": 35, "Gmaj9": 31, "Asus4": 33}


def beat_times(t_end, ramp=(160, 170), bpm=(72, 96)):
    dt = 0.001
    t = np.arange(0, t_end, dt)
    b = np.interp(t, ramp, bpm)
    ph = np.cumsum(b / 60 * dt)
    k = np.arange(1, int(ph[-1]))
    return np.interp(k, ph, t)


def morning_score(tl, a4):
    total = tl["total"]
    n = int(total * SR)
    s = {x["sid"]: x["start"] for x in tl["sections"]}
    five = next(e["t"] for e in says(tl) if e["unit"] == "M6" and e["text"].startswith("Five"))
    beats = beat_times(s["M7"])
    rng = np.random.default_rng(12)
    pad = np.zeros((n, 2), np.float32)
    plucks = np.zeros((n, 2), np.float32)
    shaker = np.zeros((n, 2), np.float32)
    kick = np.zeros(n, np.float32)
    bass = np.zeros(n, np.float32)
    keys = np.zeros((n, 2), np.float32)
    cache = {}
    seq = ["Dadd9", "A/C#", "Bm7", "Gmaj9"]
    # chord grid: every 8 beats until M6; then Gmaj9 -> Asus4 -> Dadd9 on "Five"
    grid = []
    bi = 0
    ci = 0
    while bi + 8 < len(beats) and beats[bi] < s["M6"] - 1:
        grid.append((beats[bi], beats[min(bi + 8, len(beats) - 1)], seq[ci % 4]))
        bi += 8
        ci += 1
    m6 = grid[-1][1] if grid else s["M6"]
    mid = (m6 + five) / 2
    grid += [(m6, mid, "Gmaj9"), (mid, five, "Asus4")]
    for a, b, name in grid:
        key = (name, round(b - a, 1))
        if key not in cache:
            cache[key] = pad_chord([note(m, a4) for m in MORNING_CHORDS[name]], b - a, len(cache), attack=1.2,
                                   release=2.5, lp=3000)
        add(pad, cache[key], a)
        if a >= s["M3"] - 0.5 and b <= five + 0.1:
            r = note(ROOT[name], a4)
            L = int((b - a) * SR)
            tt = np.arange(L) / SR
            env = np.minimum(1, tt / 0.05) * np.minimum(1, (b - a - tt) / 0.3)
            add(bass, (np.sin(2 * np.pi * r * tt) + 0.2 * np.sin(4 * np.pi * r * tt)) * env * 0.8, a)
    final = pad_chord([note(m, a4) for m in MORNING_CHORDS["Dadd9"]], total - five - 6.5, 99, attack=0.4,
                      release=6.0, lp=3500)
    add(pad, final * 1.4, five)

    def chord_at(t):
        for a, b, name in grid:
            if a <= t < b:
                return name
        return "Dadd9"
    mcache = {}
    pattern = [0, 2, 3, 4, 2, 3, 1, 4]
    eighth = 0
    for i, bt in enumerate(beats[:-1]):
        nb = beats[i + 1]
        for half in (0, 1):
            t = bt + half * (nb - bt) / 2
            if s["M2"] <= t < five - 0.2:
                ch = MORNING_CHORDS[chord_at(t)]
                m = ch[pattern[eighth % 8]] + 12
                if m not in mcache:
                    mcache[m] = mallet(note(m, a4))
                pl, pr = pan_gains(0.35 if eighth % 2 else -0.35)
                v = 0.8 if half == 0 else 0.55
                add(plucks, np.stack([mcache[m] * pl, mcache[m] * pr], 1) * v, t)
                eighth += 1
        if s["M3"] <= bt < s["M5"]:                                     # 16th shaker
            for q in range(4):
                t = bt + q * (nb - bt) / 4
                L = int(0.05 * SR)
                g = rng.standard_normal(L).astype(np.float32) * np.exp(-np.arange(L) / (0.012 * SR))
                v = [0.9, 0.4, 0.65, 0.4][q]
                add(shaker, np.stack([g * v * 0.7, g * v], 1), t)
        if s["M4"] <= bt < s["M5"] and (i % 4) in (0, 2):              # soft round kick on 1 and 3
            L = int(0.35 * SR)
            tt = np.arange(L) / SR
            f = 45 + 50 * np.exp(-tt / 0.04)
            k = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.12) * np.minimum(1, tt / 0.003)
            add(kick, k.astype(np.float32), bt)
        if s["M2"] <= bt < s["M5"] and i % 16 == 4 and rng.random() < 0.8:   # felt-piano answers
            ch = MORNING_CHORDS[chord_at(bt)]
            for j, m in enumerate(rng.choice(ch[2:], 2, replace=False)):
                x = felt_piano(note(int(m) + 12, a4), 3.0, vel=0.6)
                add(keys, np.stack([x, x], 1), bt + j * (nb - bt))
    shaker = butter(shaker, 5000, "high")
    mix = (pad * 0.9 + plucks * 0.32 + shaker * 0.05 + np.stack([kick, kick], 1) * 0.22
           + np.stack([bass, bass], 1) * 0.22 + keys * 0.18)
    mix = mix * 0.85 + reverb(mix, stereo_ir(3.0, 2.2, (93, 94), bright=5000), 0.22)
    mix = peaking(mix, 2000, -2.0, 0.7)
    mix *= cos_fade(n, [(0, 0), (6, 1), (total - 6, 1), (total, 0)])[:, None]
    return mix.astype(np.float32), five


def sectioned(x, segs, total):
    """Normalize a stem section by section (integrated LUFS), with 2 s cosine gain ramps between."""
    pts = []
    for a, b, tgt in segs:
        g = tgt - lufs(x, a, b)
        pts += [(a + 1.0, g), (b - 1.0, g)]
    pts = [(0, pts[0][1])] + pts + [(total, pts[-1][1])]
    gdb = np.interp(np.arange(len(x)) / SR, [p[0] for p in pts], [p[1] for p in pts])
    return (x * db(gdb)[:, None]).astype(np.float32)


# ================================================================ master

def limit(x, ceiling_db):
    c = db(ceiling_db)
    a = np.max(np.abs(x), axis=1)
    la = int(0.002 * SR)
    pk = maximum_filter1d(a, 2 * la + 1)
    g = np.minimum(1.0, c / np.maximum(pk, 1e-9))
    g = minimum_filter1d(g, 8 * la + 1)
    g = uniform_filter1d(g, 4 * la + 1)
    return (x * g[:, None]).astype(np.float32)


def glue(x, t1, ratio=1.5, max_gr=1.5, above=1.5):
    """Spec §11.1 master glue: 1.5:1 on the slow (3 s) level above (integrated + 1.5 dB), at most 1.5 dB of reduction."""
    integ = lufs(x, 0, t1)
    m = ss.lfilter(*KB2, ss.lfilter(*KB1, x, axis=0), axis=0)
    p = uniform_filter1d(np.sum(m.astype(np.float32) ** 2, axis=1), 3 * SR)
    lev = -0.691 + 10 * np.log10(p + 1e-12)
    gr = np.clip((lev - (integ + above)) * (1 - 1 / ratio), 0, max_gr)
    gr = uniform_filter1d(gr, SR)
    return (x * db(-gr)[:, None]).astype(np.float32)


def post_glue(cut):
    """Apply glue + re-master to existing masters (night only); the sleep tail after 25:45 is left untouched."""
    for p in sorted((WORK / cut).glob(f"STP-LWQ-M-{cut.upper()}-*.wav")):
        x, _ = sf.read(p, dtype="float32")
        y = glue(x, 1540)
        g = db(-21.0 - lufs(y, 0, 1540))
        ramp_ = np.ones(len(y), np.float32) * g
        a, b = int(1545 * SR), int(1550 * SR)
        ramp_[a:b] = np.linspace(g, 1.0, b - a)
        ramp_[b:] = 1.0
        y = y * ramp_[:, None]
        y[:b] = limit(y[:b], -2.9)
        sf.write(p, y, SR, subtype="PCM_24")
        print("glued", p.name, round(lufs(y, 0, 1540), 2), flush=True)


def stem_path(cut, name):
    p = WORK / cut / "stems" / f"{name}.npy"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def cached(cut, name, fn):
    p = stem_path(cut, name)
    if p.exists():
        return np.load(p, mmap_mode="r")
    x = fn()
    np.save(p, x)
    return np.load(p, mmap_mode="r")


def render(cut):
    tl = load_tl(cut)
    total = tl["total"]
    n = int(total * SR)
    night = cut == "night"
    s = {x["sid"]: x["start"] for x in tl["sections"]}
    report = {}

    vox = {}
    for spk in (False, True):
        v, a_only = voice_stems(cut, tl, spk)
        np.save(stem_path(cut, f"vox-{'spk' if spk else 'hp'}"), v)
        del v
        if not spk:
            duck = duck_env(a_only, 6.5, 1.2) if night else duck_env(a_only, 3.0)
            np.save(stem_path(cut, "aonly"), a_only)
    whisp, placed = whisper_stem(cut, tl)
    report["whisper_lines"] = placed
    np.save(stem_path(cut, "whisper"), whisp)
    del whisp

    # beds
    if night:
        nz = brown(n, 1)
        nz = normalize(nz, -42.0, 30, 600) * cos_fade(n, [(0, 0), (8, 1), (1500, 1), (1680, 0)])[:, None]
        rn = rain(total)
        rn = normalize(rn, -40.0, 30, 600) * cos_fade(n, [(0, 0), (8, 1), (1530, 1), (1680, 0)])[:, None]
        beds = nz + rn
    else:
        pk = pink(int(130 * SR), 2)
        pk = butter(pk, 6000)
        pk = normalize(pk, -40.0, 10, 100)
        pkf = np.zeros((n, 2), np.float32)
        pkf[:len(pk)] = pk[:n]
        pkf *= cos_fade(n, [(0, 0), (6, 1), (s["M2"], 1), (120, 0)])[:, None]
        bd = birds(200)
        bd = normalize(bd, -34.0, 10, 140)
        bdf = np.zeros((n, 2), np.float32)
        bdf[:len(bd)] = bd[:n]
        bdf *= cos_fade(n, [(0, 0), (6, 1), (150, 1), (180, 0)])[:, None]
        beds = pkf + bdf

    # SFX (tuning independent)
    sfx = np.zeros((n, 2), np.float32)
    if night:
        br = [e for e in tl["events"] if e["kind"] == "breath" and e["unit"] == "N1"]
        cycles = []
        for a, b in zip(br, br[1:]):
            if a["phase"] == "in" and b["phase"] == "out":
                cycles.append((a["t"], a["end"] - a["t"], b["end"] - b["t"]))
        free = next(e for e in tl["events"] if e["kind"] == "pause" and e["unit"] == "N1" and e["scripted"] == 20)
        t = free["t"] + 0.5
        while t + 10 <= free["t"] + free["dur"] + 0.5:
            cycles.append((t, 4.0, 6.0))
            t += 10
        waves = np.zeros((n, 2), np.float32)
        for i, (t, r, f) in enumerate(cycles):
            add(waves, wave_swell(r, f, 100 + i), t)
        win = (cycles[0][0], cycles[-1][0] + 10)
        waves = normalize(waves, -36.0, *win)
        sfx += waves
        report["wave_swells"] = [round(c[0], 2) for c in cycles]
        report["breath_cycles"] = cycles
    else:
        w = whoosh()
        wh = np.zeros((n, 2), np.float32)
        for t in (s["M3"], s["M4"]):
            add(wh, w, t - 0.9)
        sfx += normalize(wh, -26.0, s["M3"] - 2, s["M3"] + 2, momentary=True)
        five = next(e["t"] for e in says(tl) if e["unit"] == "M6" and e["text"].startswith("Five"))
        r = noise_riser(five - s["M6"])
        rz = np.zeros((n, 2), np.float32)
        add(rz, r, s["M6"])
        sfx += normalize(rz, -22.0, five - 3, five)
        report["riser"] = (round(s["M6"], 2), round(five, 2))

    np.save(stem_path(cut, "beds"), beds)
    np.save(stem_path(cut, "sfx"), sfx)
    del beds, sfx
    np.save(stem_path(cut, "duck"), duck)
    del duck
    import gc
    gc.collect()
    mixes = {}
    for a4 in (432.0, 440.0):
        tag = str(int(a4))
        if night:
            music = night_score(tl, a4)
            music = normalize(music, -26.5, 45, 1440)   # free level in pauses; ducked 6.5 dB -> -33 under the voice
            five = None
        else:
            music, five = morning_score(tl, a4)
            music = sectioned(music, [(0, s["M3"], -27.0), (s["M3"], s["M6"], -24.0), (five - 3, five + 1, -21.0)],
                              total)
        music = music * np.load(stem_path(cut, "duck"), mmap_mode="r")[:, None]
        np.save(stem_path(cut, f"music-{tag}"), music)
        del music
        gc.collect()
        pts, fin, fout = beat_points(cut, tl)
        bina = binaural(total, carrier(cut, a4), pts, -40, fin, fout)
        bina = normalize(bina, -38.0 if night else -34.0, 30, 600 if night else 580)
        iso = isochronic(total, carrier(cut, a4), pts, 0.35, fin, fout)
        iso = normalize(iso, -40.0 if night else -36.0, 30, 600 if night else 580)
        np.save(stem_path(cut, f"binaural-{tag}"), bina)
        np.save(stem_path(cut, f"iso-{tag}"), iso)
        sf.write(WORK / cut / f"binaural_{cut}_{tag}.wav", bina, SR, subtype="PCM_24")
        sf.write(WORK / cut / f"isochronic_{cut}_{tag}.wav", iso, SR, subtype="PCM_24")
        del bina, iso
        gc.collect()
        # tuned one-shots
        irs = stereo_ir(3.0, 3.2, (95, 96), bright=3200)
        tone = question_tone(60 if night else 69, a4, irs)
        sf.write(WORK / cut / f"question_tone_{cut}_{tag}.wav", tone, SR, subtype="PCM_24")
        tones = np.zeros((n, 2), np.float32)
        for e in tl["events"]:
            if e["kind"] == "tone":
                add(tones, tone, e["t"])
        first = next(e["t"] for e in tl["events"] if e["kind"] == "tone")
        tone_lvl = lufs_m_max(tone)
        tones *= db((-27.0 if night else -22.0) - tone_lvl)
        np.save(stem_path(cut, f"tones-{tag}"), tones)
        del tones
        tsfx = np.zeros((n, 2), np.float32)
        if night:
            b = bowl(note(53, a4))
            b = np.stack([b, b], 1)
            b = b * db(-28.0 - lufs_m_max(b))
            asks = [e["t"] for e in says(tl) if e["unit"] == "N7" and e["text"].strip(" .*") == "Ask"]
            for t in asks:
                add(tsfx, b, t - 0.3)
            report["bowls"] = asks
            sf.write(WORK / cut / f"singing_bowl_F_{tag}.wav", b, SR, subtype="PCM_24")
        else:
            bl = tubular_bell(note(74, a4))
            bl = np.stack([bl, bl], 1)
            bl = bl * db(-18.0 - lufs_m_max(bl))
            add(tsfx, bl, five)
            sf.write(WORK / cut / f"bell_D_{tag}.wav", bl, SR, subtype="PCM_24")
        for spk in (False, True):
            label = "SPK" if spk else "HP"
            mix = np.array(tsfx, copy=True)
            parts = [f"vox-{'spk' if spk else 'hp'}", "whisper", f"music-{tag}", f"iso-{tag}" if spk else f"binaural-{tag}",
                     "beds", "sfx", f"tones-{tag}"]
            for nm in parts:
                st = np.load(stem_path(cut, nm), mmap_mode="r")
                for i0 in range(0, n, SR * 60):
                    mix[i0:i0 + SR * 60] += st[i0:i0 + SR * 60]
                del st
            meas = (0, 1540) if night else (0, total)
            target = -21.0 if night else -15.0
            ceiling = -2.9 if night else -1.9
            if night:
                mix = glue(mix, 1540)
            for it in range(3):
                g = target - lufs(mix, *meas)
                mix *= db(g)
                mix = limit(mix, ceiling)
            if night:                                            # experimental sleep-tail cues, after mastering
                for t in (1560.0, 1605.0, 1650.0):
                    add(mix, tone * (db(-50.0) / np.max(np.abs(tone))), t)
            mix[int((total - 0.05) * SR):] = 0
            out = WORK / cut / f"STP-LWQ-M-{cut.upper()}-{tag}-{label}.wav"
            sf.write(out, mix, SR, subtype="PCM_24")
            mixes[(tag, label)] = str(out)
            print("wrote", out, round(lufs(mix, *meas), 2), flush=True)
            del mix
    report["mixes"] = {f"{k[0]}-{k[1]}": v for k, v in mixes.items()}
    (WORK / cut / "audio_report.json").write_text(json.dumps(report, indent=1, default=float))


if __name__ == "__main__":
    if sys.argv[1] == "--glue":
        post_glue(sys.argv[2])
    else:
        for cut in sys.argv[1:]:
            render(cut)
