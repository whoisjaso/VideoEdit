"""Sound design v2: every scene has its own world, and titles land with weight.

Everything is made here: synthesis for tones, impacts, sirens, engines, weather and footsteps, and the
offline voice engine (Kokoro) for the things that are voices in real life: police radio, TV babble, office murmur.
No samples, nothing licensed, nothing copyrighted. Times come from the narration clock (timing.py) and scenes.json.

  python3 src/mix.py   -> audio/narration.wav (timed to picture), audio/mix_premaster.wav, audio/stems/*.wav
"""
import os, sys, json, math
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, sosfiltfilt, fftconvolve, resample_poly
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from timing import TL, ROOT, OFF
SR = 48000; rng = np.random.default_rng(12)
tl = TL(); T, E, Wn = tl.T, tl.E, tl.Wn
SC = {s["name"]: (s["t0"], s["t1"]) for s in json.load(open(f"{ROOT}/scenes.json"))}
END = tl.end; N = int(math.ceil(END * SR)); tt = np.arange(N) / SR
VERT_SAFE = True

# ------------------------------------------------------------------ small tools
def db(x): return 10 ** (x / 20)
def bp(x, lo=None, hi=None, order=2):
    if lo and hi: sos = butter(order, [lo, hi], "bp", fs=SR, output="sos")
    elif lo: sos = butter(order, lo, "hp", fs=SR, output="sos")
    else: sos = butter(order, hi, "lp", fs=SR, output="sos")
    return sosfilt(sos, x, axis=0)
def norm(x, peak_db=-1.0): return x / (np.abs(x).max() + 1e-12) * db(peak_db)
def rms_to(x, target_db):
    r = np.sqrt(np.mean(x ** 2) + 1e-20); return x * db(target_db) / r
def secs(d): return int(round(d * SR))
def fade(x, fi=0.01, fo=0.01):
    x = x.copy(); a, b = min(len(x) // 2, secs(fi)), min(len(x) // 2, secs(fo))
    if a: x[:a] *= (0.5 - 0.5 * np.cos(np.pi * np.arange(a) / a))[(...,) + (None,) * (x.ndim - 1)]
    if b: x[-b:] *= (0.5 + 0.5 * np.cos(np.pi * np.arange(b) / b))[(...,) + (None,) * (x.ndim - 1)]
    return x
def env(a, b, fi=1.0, fo=1.0):
    e = np.zeros(N); i0, i1 = max(0, secs(a)), min(N, secs(b))
    if i1 > i0: e[i0:i1] = fade(np.ones(i1 - i0), fi, fo)
    return e
def noise(n): return rng.standard_normal(n)
def pink(n):
    x = np.fft.rfft(noise(n)); f = np.arange(len(x)); f[0] = 1; return norm(np.fft.irfft(x / np.sqrt(f), n), -3)
def brown(n):
    x = np.fft.rfft(noise(n)); f = np.arange(len(x)); f[0] = 1; return norm(np.fft.irfft(x / f, n), -3)
_IR = {}
def reverb(x, decay=1.2, wet=0.3, lp=5000):
    """Cheap room: convolve with decaying filtered noise."""
    k = (decay, lp)
    if k not in _IR:
        n = secs(decay * 1.6); ir = noise(n) * np.exp(-np.arange(n) / (decay * SR / 6.9)); ir = bp(ir, 120, lp); ir[:secs(0.004)] = 0
        _IR[k] = ir / np.sqrt(np.sum(ir ** 2))
    w = fftconvolve(x, _IR[k])[:len(x) + secs(decay)]
    out = np.zeros(len(w)); out[:len(x)] = x; return out * (1 - wet * 0.3) + w * wet
def pan2(x, p=0.0):
    l, r = math.cos((p + 1) * math.pi / 4), math.sin((p + 1) * math.pi / 4); return np.stack([x * l, x * r], 1) * 1.414
BUS = {k: np.zeros((N, 2)) for k in ("amb", "fx", "hits", "music")}
def put(bus, x, t, gain_db=0.0, pan=0.0):
    if x.ndim == 1: x = pan2(x, pan)
    i = secs(t)
    if i < 0: x = x[-i:]; i = 0
    n = min(len(x), N - i)
    if n > 0: BUS[bus][i:i + n] += x[:n] * db(gain_db)
def loop_to(x, n, xf=0.5):
    """Loop a clip to n samples with crossfades."""
    k = secs(xf); out = np.zeros(n + len(x)); pos = 0; body = fade(x, xf, xf)
    while pos < n: out[pos:pos + len(body)] += body; pos += len(body) - k
    return out[:n]

# ------------------------------------------------------------------ narration, timed to picture
dry, sr = sf.read(f"{ROOT}/audio/narration_dry.wav"); assert sr == SR
parts = []; last = 0
for at, extra in tl.cuts:
    i = secs(at); parts += [dry[last:i], np.zeros(secs(extra))]; last = i
parts.append(dry[last:]); nar = np.concatenate([np.zeros(secs(OFF))] + parts); nar = np.pad(nar, (0, max(0, N - len(nar))))[:N]
sf.write(f"{ROOT}/audio/narration.wav", (nar * db(-3)).astype(np.float32), SR)
ab = np.abs(nar); blk = 240; e = ab[:N // blk * blk].reshape(-1, blk).max(1); sm = np.zeros_like(e); v = 0.0
for i, x in enumerate(e):
    v = x if x > v else v * math.exp(-blk / (0.14 * SR)); sm[i] = v
speech = np.clip(np.repeat(sm, blk) / 0.06, 0, 1); speech = np.pad(speech, (0, N - len(speech)))
speech = sosfiltfilt(butter(1, 5, "lp", fs=SR, output="sos"), speech).clip(0, 1)
def duck(depth_db): return db(-depth_db * speech)[:, None]

# ------------------------------------------------------------------ voices that are voices: radio, TV babble, office murmur
_k = None
def tts(text, voice, speed=1.0):
    global _k
    if _k is None:
        from kokoro_onnx import Kokoro
        md = os.environ.get("KOKORO_DIR", "/tmp/claude-0/-home-user-VideoEdit/dea1a155-7f9b-5d5a-9ed6-2efb365ee1a7/scratchpad/models")
        _k = Kokoro(f"{md}/kokoro-v1.0.onnx", f"{md}/voices-v1.0.bin")
    a, r = _k.create(text, voice=voice, speed=speed, lang="en-us"); return resample_poly(a.astype(np.float64), SR, r)
FILLER = ["and that brings us to the top of the hour, with more after the break, so stay right where you are",
          "you won't believe what happened next, he walked right in, looked around, and said nothing at all",
          "coming up tonight, the story everyone is talking about, and the weather for the rest of your week",
          "I told you once and I'm not going to tell you again, get in the car, we are leaving right now",
          "the numbers are in and they are bigger than anyone expected, analysts say this changes everything",
          "previously, on the last episode, nobody saw it coming, and nothing would ever be the same again"]
VOICES = ["am_michael", "af_bella", "am_fenrir", "af_sarah", "bm_george", "af_nicole"]
def babble(dur, layers=6, lo=300, hi=2600, seed=0):
    """Many voices at once, filtered until no single word survives. TV wall, office, crowd."""
    r = np.random.default_rng(seed); n = secs(dur); out = np.zeros((n, 2))
    for j in range(layers):
        clip = CLIPS[(j + seed) % len(CLIPS)]; ps = r.choice([0.92, 1.0, 1.08, 1.15])
        c = resample_poly(clip, 100, int(100 * ps)); c = np.roll(c, r.integers(0, len(c)))
        out += pan2(loop_to(c, n, 0.3), r.uniform(-0.8, 0.8))
    out = bp(out, lo, hi, 2); return out / (np.abs(out).max() + 1e-9)
def radio(text, voice="am_onyx", speed=1.12):
    v = norm(tts(text, voice, speed)); v = np.tanh(bp(v, 450, 2900, 3) * 6) * 0.6; v = bp(v, 400, 3200, 2)
    sq = bp(noise(secs(0.09)), 1200, 4500) * 0.5; beep = np.sin(2 * np.pi * 1050 * np.arange(secs(0.07)) / SR) * 0.25
    hissy = v + bp(noise(len(v)), 900, 3500) * 0.05
    return np.concatenate([fade(sq, 0.002, 0.02), hissy, fade(beep, 0.003, 0.01), fade(sq * 0.7, 0.002, 0.03)])
print("voices…"); CLIPS = [norm(tts(t, v, 1.05)) for t, v in zip(FILLER, VOICES)]

# ------------------------------------------------------------------ instruments
def hit(big=1.0, f0=64, f1=34, dur=1.6):
    n = secs(dur); x = np.arange(n) / SR
    s = np.sin(2 * np.pi * (f1 * x + (f0 - f1) * 0.1 * (1 - np.exp(-x / 0.1)))) * np.exp(-x / (0.28 + 0.25 * big))
    s += 0.5 * bp(noise(n), 40, 220) * np.exp(-x / 0.06) + 0.12 * big * bp(noise(n), 1500, 6000) * np.exp(-x / 0.012)
    return fade(reverb(np.tanh(s * 1.6), 1.4, 0.22 * big, 900), 0.002, 0.3)
def whoosh(dur=0.7, lo=300, hi=3200, rise=0.6):
    n = secs(dur); x = np.arange(n) / n
    e = np.where(x < rise, (x / rise) ** 2.2, ((1 - x) / (1 - rise)) ** 1.5)
    a = bp(noise(n), lo, (lo * hi) ** 0.5); b = bp(noise(n), (lo * hi) ** 0.5, hi)
    return (a * (1 - x) + b * x) * e
def tick(f=3200, d=0.03):
    n = secs(d); x = np.arange(n) / SR; return (np.sin(2 * np.pi * f * x) * 0.6 + bp(noise(n), 2000, 7000) * 0.5) * np.exp(-x / (d / 5))
def tone(f, dur, a=0.02, r=0.4, harm=(1, 0.3, 0.1)):
    n = secs(dur); x = np.arange(n) / SR; s = sum(h * np.sin(2 * np.pi * f * (i + 1) * x) for i, h in enumerate(harm))
    return s * np.minimum(1, x / a) * np.exp(-np.maximum(0, x - a) / r)
def heartbeat(t0, t1, bpm0, bpm1, g0, g1):
    t = t0
    while t < t1:
        u = (t - t0) / (t1 - t0); bpm = bpm0 + (bpm1 - bpm0) * u; g = g0 + (g1 - g0) * u
        for off, amp, f in ((0.0, 1.0, 52), (0.27 * 72 / bpm, 0.7, 62)):
            n = secs(0.2); x = np.arange(n) / SR
            put("fx", np.sin(2 * np.pi * (f - 12 * x / 0.2) * x) * np.exp(-x / 0.05) * amp, t + off, g)
        t += 60 / bpm
def siren(dur, mode="wail", f_lo=640, f_hi=1480):
    n = secs(dur); x = np.arange(n) / SR
    if mode == "wail": ph = 0.5 - 0.5 * np.cos(2 * np.pi * x / 4.6)
    elif mode == "yelp": ph = (x / 0.34) % 1.0; ph = np.where(ph < 0.85, ph / 0.85, (1 - ph) / 0.15)
    else: ph = np.clip(x / dur, 0, 1) ** 0.7                                   # one whoop
    f = f_lo * (f_hi / f_lo) ** ph; p = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(p) + 0.5 * np.sin(2 * p) + 0.33 * np.sin(3 * p) + 0.2 * np.sin(4 * p)
    return bp(np.tanh(s * 1.4), 350, 4200)
def car_pass(dur=3.2, left_to_right=True):
    n = secs(dur); x = np.linspace(-1, 1, n); e = np.exp(-(x / 0.33) ** 2)
    s = bp(pink(n), 70, 1800) * e + 0.25 * np.sin(2 * np.pi * np.cumsum(118 * (1 - 0.07 * np.tanh(x * 3))) / SR) * e
    p = np.clip(x * 1.2, -1, 1) * (1 if left_to_right else -1)
    l, r = np.cos((p + 1) * np.pi / 4), np.sin((p + 1) * np.pi / 4); return np.stack([s * l, s * r], 1)
def crickets(dur):
    n = secs(dur); x = np.arange(n) / SR; out = np.zeros((n, 2))
    for f, rate, ph, p in ((4300, 17, 0.0, -0.6), (4650, 15, 1.3, 0.5), (4050, 19, 2.1, 0.1)):
        chirp = (np.sin(2 * np.pi * rate * x + ph) > 0.2) * (np.sin(2 * np.pi * 0.42 * x + ph * 2) > -0.2)
        out += pan2(np.sin(2 * np.pi * f * x) * sosfilt(butter(1, 60, "lp", fs=SR, output="sos"), chirp.astype(float)), p)
    return out
def step(surface):
    n = secs(0.18); x = np.arange(n) / SR; w = noise(n)
    if surface == "sidewalk": s = 0.9 * bp(w, 90, 260) * np.exp(-x / 0.035) + 0.6 * bp(w, 1400, 3600) * np.exp(-x / 0.012)
    elif surface == "asphalt": s = 1.0 * bp(w, 70, 200) * np.exp(-x / 0.05) + 0.6 * bp(w, 500, 1600) * np.exp(-x / 0.05)
    else: s = 0.5 * bp(w, 120, 300) * np.exp(-x / 0.03) + 0.9 * bp(w, 2000, 4500) * np.exp(-x / 0.008)
    return norm(s, -3)
def engine(dur, f0=31.0):
    n = secs(dur); x = np.arange(n) / SR
    ph = 2 * np.pi * np.cumsum(f0 * (1 + 0.02 * np.sin(2 * np.pi * 0.6 * x) + 0.01 * np.sin(2 * np.pi * 7.3 * x))) / SR
    s = sum(am * np.sin(h * ph + h) for h, am in ((1, 1.0), (2, 0.7), (3, 0.45), (4, 0.3), (6, 0.18), (8, 0.1)))
    return s * (0.8 + 0.2 * np.sin(2 * np.pi * f0 / 2 * x)) + 0.6 * bp(noise(n), 60, 600)
def car_music(dur, bpm=88):
    """Loud music heard through a closed car: kick, sub bass, a rattle. Nothing melodic enough to be a song."""
    n = secs(dur); out = np.zeros(n); beat = 60 / bpm; t = 0.0; k = 0; notes = [41.2, 41.2, 49.0, 36.7]
    while t < dur:
        for off, amp in ((0, 1.0), (0.75, 0.6), (1.5, 0.9), (2.5, 0.8)):
            i = secs(t + off * beat); m = secs(0.35); x = np.arange(m) / SR
            kick = np.sin(2 * np.pi * (48 * x + 60 * 0.03 * (1 - np.exp(-x / 0.03)))) * np.exp(-x / 0.12) * amp
            if i + m < n: out[i:i + m] += kick
        f = notes[k % 4]; i = secs(t); m = min(secs(beat * 4), n - i); x = np.arange(m) / SR
        out[i:i + m] += 0.7 * np.sin(2 * np.pi * f * x) * (0.6 + 0.4 * np.sin(2 * np.pi * x / (beat * 0.5)) ** 2) * fade(np.ones(m), 0.02, 0.1)
        for h in np.arange(0, 4, 0.5):
            i = secs(t + h * beat); m = secs(0.05)
            if i + m < n: out[i:i + m] += 0.1 * bp(noise(m), 2500, 6000) * np.exp(-np.arange(m) / (0.008 * SR))
        t += beat * 4; k += 1
    return bp(np.tanh(out * 1.5), None, 240, 3) + 0.15 * bp(out, 240, 900)
def trap_beat(dur, bpm=140):
    """An original beat in the lane of what he would be playing: sliding 808s, a half-time clap, rolling hats, a dark bell line.
    Written here from scratch. It is not a recreation of any song."""
    n = secs(dur) + SR; out = np.zeros(n); beat = 60 / bpm; bar = beat * 4; r = np.random.default_rng(5)
    roots = [43.65, 43.65, 51.91, 38.89]; mel = [349.23, 415.30, 523.25, 415.30, 622.25, 523.25, 415.30, 311.13]
    def add(x, t):
        i = secs(t)
        if 0 <= i < n: k_ = min(len(x), n - i); out[i:i + k_] += x[:k_]
    nb = int(dur / bar) + 1
    for bi in range(nb):
        t0 = bi * bar; f = roots[bi % 4]
        for k_, (off_, ln, gl) in enumerate(((0.0, 2.2, 0), (2.5, 1.2, 0), (3.75, 0.25, 1 if bi % 2 else 0))):       # 808: long, saturated, sometimes sliding up
            m = secs(ln * beat); x = np.arange(m) / SR; fr = f * (1 + (0.5 * gl) * np.clip(x / (ln * beat), 0, 1) ** 2)
            s8 = np.tanh(np.sin(2 * np.pi * np.cumsum(fr) / SR + 0.6 * np.sin(2 * np.pi * np.cumsum(fr) / SR)) * 2.2) * np.exp(-x / (0.55 * ln * beat + 0.1)); s8[:secs(0.004)] *= np.linspace(0, 1, secs(0.004))
            add(s8 * 0.9, t0 + off_ * beat)
            mk = secs(0.2); xk = np.arange(mk) / SR; add(np.sin(2 * np.pi * (52 * xk + 90 * 0.02 * (1 - np.exp(-xk / 0.02)))) * np.exp(-xk / 0.07) * 0.8, t0 + off_ * beat)   # kick on top of it
        mc = secs(0.22); xc = np.arange(mc) / SR
        add((bp(r.standard_normal(mc), 900, 5200) * np.exp(-xc / 0.045) + 0.5 * bp(r.standard_normal(mc), 900, 5200) * np.exp(-np.maximum(0, xc - 0.012) / 0.03) * (xc > 0.012)) * 0.5, t0 + 2 * beat)   # clap on three
        for h in range(8):                                                    # hats, with a roll at the end of every other bar
            subs = 3 if (bi % 2 == 1 and h == 7) else (2 if h in (3,) else 1)
            for q in range(subs):
                mh = secs(0.05); xh = np.arange(mh) / SR; add(bp(r.standard_normal(mh), 6500, 12000) * np.exp(-xh / 0.012) * (0.2 if q else 0.26), t0 + (h + q / subs) * beat / 2)
        for h in range(8):                                                    # the bell line
            if (bi + h) % 3 == 2: continue
            fm = mel[(h + bi * 3) % 8]; mm = secs(0.5); xm = np.arange(mm) / SR
            add((np.sin(2 * np.pi * fm * xm) + 0.5 * np.sin(2 * np.pi * fm * 2.76 * xm) * np.exp(-xm / 0.08) + 0.3 * np.sin(2 * np.pi * fm * 0.5 * xm)) * np.exp(-xm / 0.16) * 0.13, t0 + h * beat / 2)
    return out[:secs(dur)]

def licensed(name):
    """A track Jason owns or has licensed, dropped into audio/licensed/. Never committed. None if there isn't one."""
    import subprocess
    for ext in ("wav", "flac", "mp3", "m4a", "aiff"):
        f = f"{ROOT}/audio/licensed/{name}.{ext}"
        if os.path.exists(f):
            raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]); print("using licensed track:", f)
            return np.frombuffer(raw, np.float32).astype(np.float64)
    return None

def muffled(x, cut=170):
    """Music through a wall, a window or a TV speaker in the next room."""
    return bp(x, None, cut, 4) + 0.15 * bp(x, cut, 520, 2)

def clang():
    n = secs(2.2); x = np.arange(n) / SR
    s = sum(a * np.sin(2 * np.pi * f * x + p) * np.exp(-x / d) for f, a, d, p in
            ((168, 1.0, 0.5, 0), (301, 0.8, 0.4, 1), (447, 0.7, 0.35, 2), (633, 0.5, 0.3, 3), (912, 0.4, 0.22, 4), (1370, 0.3, 0.15, 5), (2140, 0.2, 0.1, 6)))
    s += bp(noise(n), 200, 3000) * np.exp(-x / 0.03) * 1.5
    lock = np.zeros(n); i = secs(0.28); m = secs(0.08); lock[i:i + m] = bp(noise(m), 1500, 5000) * np.exp(-np.arange(m) / (0.01 * SR)) * 1.2
    return reverb(s + lock, 2.2, 0.5, 3500)
def phone_ring(reps=2):
    out = []
    for _ in range(reps):
        n = secs(1.0); x = np.arange(n) / SR
        out += [fade((np.sin(2 * np.pi * 440 * x) + np.sin(2 * np.pi * 480 * x)) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 20 * x))), 0.01, 0.02), np.zeros(secs(1.6))]
    return np.concatenate(out)
def keys(dur, rate=6.0, seed=1):
    r = np.random.default_rng(seed); n = secs(dur); out = np.zeros(n); t = 0.0
    while t < dur - 0.1:
        c = tick(r.uniform(1800, 3200), 0.025) * r.uniform(0.4, 1.0); i = secs(t); out[i:i + len(c)] += c[:n - i]
        t += r.exponential(1 / rate) + (r.uniform(0.6, 2.0) if r.random() < 0.08 else 0)
    return out
def cheer(dur=2.6):
    n = secs(dur); x = np.arange(n) / n
    return bp(pink(n), 500, 3600) * np.sin(np.pi * x) ** 1.3 * (0.8 + 0.2 * np.sin(2 * np.pi * 5.5 * x * dur))
def wind(dur, seed=3):
    n = secs(dur); r = np.random.default_rng(seed); g = sosfiltfilt(butter(1, 0.35, "lp", fs=SR, output="sos"), r.standard_normal(n)); g = (g - g.min()) / (np.ptp(g) + 1e-9)
    return bp(pink(n), 180, 900) * (0.25 + 0.75 * g) + 0.4 * bp(pink(n), 900, 2600) * g ** 2
def pad(freqs, dur, bright=0.25):
    n = secs(dur); x = np.arange(n) / SR; out = np.zeros((n, 2))
    for f, a, det in freqs:
        for ch, sg in ((0, -1), (1, 1)):
            lfo = 0.72 + 0.28 * np.sin(2 * np.pi * (0.03 + det * 0.2) * x + f + ch)
            out[:, ch] += a * lfo * (np.sin(2 * np.pi * (f + sg * det) * x) + bright * np.sin(2 * np.pi * 2 * (f + sg * det) * x + 1) + bright * 0.4 * np.sin(2 * np.pi * 3 * (f + sg * det) * x))
    return out
def title(t, big=0.6, gain=-12.0, sweep=True):
    """A title landing: a short intake of air, then weight."""
    if sweep: put("hits", whoosh(0.45, 200, 1800, 0.85), t - 0.42, gain - 9)
    put("hits", hit(big), t, gain)
def typing(t0, n_chars, dur, gain=-27.0, pan=0.0):
    for i in range(n_chars): put("fx", tick(2400 + 600 * rng.random(), 0.02), t0 + dur * i / n_chars, gain - 3 * rng.random(), pan)

# ================================================================== the score (bed)
AMIN = ((55.0, 1.0, 0.07), (82.41, 0.55, 0.05), (110.0, 0.5, 0.11), (130.81, 0.34, 0.09), (164.81, 0.16, 0.13))
AMAJ = ((55.0, 0.8, 0.06), (110.0, 0.5, 0.08), (138.59, 0.42, 0.1), (164.81, 0.36, 0.09), (220.0, 0.2, 0.12), (277.18, 0.1, 0.1))
DARK = ((43.65, 1.0, 0.09), (55.0, 0.6, 0.07), (87.31, 0.45, 0.12), (103.83, 0.3, 0.15))        # F / A / G#: unease for the stop
bed_min = rms_to(pad(AMIN, END), -29); bed_dark = rms_to(pad(DARK, END, 0.4), -28); bed_maj = rms_to(pad(AMAJ, END, 0.35), -27)
t_obs0, t_obs1 = SC["observer"]; t_new0, t_new1 = SC["newscript"]; t_stop0, t_stop1 = SC["stop"]
e_min = env(T("job1") - 0.4, SC["two"][0], 3.0, 2.5) + env(SC["news"][0], t_obs0 - 0.2, 2.5, 1.2) + env(SC["halfsecond"][0], t_new0 + 4, 2.0, 4.0)
e_dark = env(SC["street1"][0] + 6, SC["street1"][1], 6.0, 2.0) * 0.6 + env(SC["two"][0], t_stop1 + 0.5, 3.0, 1.0)
e_maj = env(T("ns2") - 1.0, t_new1 + 0.4, 6.0, 1.6)
BUS["music"] += (bed_min * e_min[:, None] + bed_dark * e_dark[:, None] + bed_maj * e_maj[:, None]) * duck(5)
# one tone that never stops, first frame to last: the film is one continuum, and so is its floor
BUS["music"] += rms_to(pad(((36.71, 1.0, 0.05), (55.0, 0.55, 0.07), (73.42, 0.2, 0.09)), END, 0.12), -35) * env(0.5, END - 0.6, 3.0, 2.5)[:, None]
# a slow pulse under the two tense stretches: the street and the stop
for a, b, g in ((T("st4"), T("st11") - 0.3, -24), (T("ts3"), E("ts22") + 0.3, -22)):
    t = a
    while t < b:
        put("music", fade(tone(55, 0.9, 0.03, 0.22, (1, 0.4, 0.15)), 0.005, 0.2), t, g + 4 * (t - a) / (b - a) - 4, 0); t += 1.0

# ================================================================== scene by scene
# ---- hook: silence, then weight. A lighter second hit so line two lands too.
title(0.6, 1.0, -8, sweep=False); title(2.4, 0.5, -15, sweep=False)

# ---- one job: the eye. A heartbeat, and the pupil closing.
heartbeat(SC["eye"][0] + 0.4, SC["eye"][1] - 0.6, 62, 66, -19, -17)
put("fx", whoosh(1.3, 80, 500, 0.5), T("job2") - 0.1, -20)
for lid, w in (("job3", "fair"), ("job4", "moral"), ("job5", "a")): put("fx", tick(1700, 0.04), Wn(lid, w) + 0.35, -24, -0.5)
title(Wn("job6", "keep"), 0.7, -12)

# ---- pattern-match: a wall of screens. Voices pile up, static thickens.
a, b = SC["screens"]; n = secs(b - a)
wall = babble(b - a, 6, 350, 3000, seed=1) * (0.15 + 0.85 * np.clip(np.arange(n) / (0.75 * n), 0, 1) ** 1.5)[:, None]
put("amb", fade(rms_to(wall, -27), 1.0, 0.8) * 1.0, a)
st = np.stack([bp(noise(n), 1800, 7500), bp(noise(n), 1800, 7500)], 1) * (0.1 + 0.9 * np.clip(np.arange(n) / (0.8 * n), 0, 1) ** 1.6)[:, None]
put("amb", fade(rms_to(st, -37), 1.0, 0.8), a)
for i in range(22):                                              # sets switching on
    tt_ = a + (b - a) * 0.75 * (i / 22) ** 0.8 + rng.uniform(0, 0.3); put("fx", tick(900 + 2600 * rng.random(), 0.05), tt_, -27, rng.uniform(-0.9, 0.9))
title(Wn("pat4", "when"), 0.4, -17); title(Wn("pat4", "expect"), 0.6, -14, sweep=False)

# ---- cultivation: one living-room TV, a clock, a house at night
a, b = SC["couch"]
tvr = bp(babble(b - a, 2, 250, 1500, seed=4), None, 1400); put("amb", fade(rms_to(tvr, -29), 1.2, 0.05), a)
put("amb", fade(rms_to(pan2(np.sin(2 * np.pi * 60 * np.arange(secs(b - a)) / SR) + 0.4 * bp(pink(secs(b - a)), 80, 400)), -42), 1, 0.05), a)
t = a + 0.7
while t < b - 0.2: put("fx", tick(1400, 0.03), t, -29, 0.6); put("fx", tick(1100, 0.03), t + 0.5, -31, 0.6); t += 1.0
title(Wn("cul4", "cultivation"), 0.8, -11)

# ---- the three characters: hard cuts, each with the world the screen always gave him
cuts = json.load(open(f"{ROOT}/cues.json"))["cuts"]; ends = cuts[1:] + [SC["iat"][0]]
for i, (c0, c1) in enumerate(zip(cuts, ends)):
    put("hits", hit(0.9), c0, -9); put("fx", tick(600, 0.06), c0, -14)
    typing(c0 + 0.04, 12, 0.32, -24); d = c1 - c0; n = secs(d)
    if i == 0:      # a block at night: a far siren, a dog-less street, bass from somewhere
        put("amb", fade(pan2(rms_to(reverb(siren(d, "wail"), 2.0, 0.6, 2500)[:n], -30), -0.5), 0.3, 0.02), c0)
        put("amb", fade(pan2(rms_to(muffled(trap_beat(d)), -25), 0.4), 0.2, 0.02), c0)
        put("amb", fade(rms_to(np.stack([bp(brown(n), 40, 400)] * 2, 1), -30), 0.2, 0.02), c0)
    elif i == 1:    # heat and wind
        put("amb", fade(pan2(rms_to(wind(d, 5), -25)), 0.2, 0.02), c0); put("amb", fade(rms_to(crickets(d), -38), 0.2, 0.02), c0)
    else:           # an office: a phone, keys, murmur, air handling
        put("amb", fade(rms_to(babble(d, 4, 300, 2200, seed=7), -31), 0.2, 0.02), c0)
        put("amb", pan2(rms_to(bp(phone_ring(2), 300, 3000)[:n], -27), 0.5), c0 + 0.5); put("amb", pan2(rms_to(keys(d, 7, 2), -33), -0.5), c0)
        put("amb", fade(rms_to(np.stack([bp(pink(n), 100, 700)] * 2, 1), -38), 0.2, 0.02), c0)

# ---- the IAT: a quiet lab. Each trial is a soft click and a tone; the slow lane answers lower and later.
a, b = SC["iat"]; put("amb", fade(rms_to(np.stack([bp(pink(secs(b - a)), 90, 500)] * 2, 1), -41), 0.3, 0.5), a)
title(Wn("iat3", "your"), 0.6, -14)
tb = T("iat4"); per = 1.55
for i, rt in enumerate((0.40, 0.78)):
    t = tb + 0.5 + i * 0.22
    while t < T("iat6"):
        put("fx", tick(2600, 0.02), t, -26, -0.6); put("fx", tone(880 if i == 0 else 587, 0.25, 0.005, 0.08), t + rt, -27, 0.5 if i == 0 else 0.2); t += per
put("fx", fade(tone(220, 1.6, 0.4, 0.6, (1, 0.5, 0.2)), 0.05, 0.4), Wn("iat5", "faster"), -18)
title(T("iat7") + 0.25, 0.7, -13)

# ---- the street: a city at night, your own feet, a pulse that climbs as he gets closer
wk = json.load(open(f"{ROOT}/cues.json"))["walk"]; per = 2 * math.pi / (5.2 * wk["v"]); c0, c1 = wk["cam"]
def cam_x(t):
    u = min(1, max(0, (t - c0) / (c1 - c0))); u = 4 * u ** 3 if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2; return -5.4 * u
steps = []
for si, key in enumerate(("street1", "street2")):
    a, b = SC[key]; n = secs(b - a)
    city = np.stack([bp(brown(n), 35, 500), bp(brown(n), 35, 500)], 1) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.07 * np.arange(n) / SR + si))[:, None]
    put("amb", fade(rms_to(city, -25), 1.5, 0.6), a)
    put("amb", fade(rms_to(crickets(b - a), -41), 2.0, 0.6), a)
    put("amb", fade(pan2(rms_to(reverb(siren(b - a, "wail", 560, 1200), 2.5, 0.75, 1800)[:n], -38), 0.6 if si == 0 else -0.6), 3, 2), a)   # far away, someone else's night
    k = math.ceil((a + 0.5 - wk["t0"] - (1.5 * math.pi) / (5.2 * wk["v"])) / per)
    while True:
        t = wk["t0"] + (1.5 * math.pi) / (5.2 * wk["v"]) + k * per
        if t > b - 0.4: break
        surf = "asphalt" if (si == 0 and -5.0 < cam_x(t) < -0.5) else "sidewalk"
        put("fx", step(surf), t, -17 + rng.uniform(-1.5, 1.0), 0.2 * (1 if k % 2 else -1)); steps.append((round(t, 3), surf)); k += 1
for t_, lr in ((SC["street1"][0] + 3.0, True), (T("st9") + 0.9, False), (SC["street2"][0] + 9.0, True), (T("ch3"), False)):
    put("amb", car_pass(3.4, lr), t_, -19)
for w in ("phone", "watch", "keys"): put("fx", tone(1568 if w == "phone" else 2093 if w == "watch" else 2637, 0.3, 0.003, 0.07), Wn("st3", w), -27, {"phone": 0.6, "watch": -0.6, "keys": 0.0}[w])
put("fx", reverb(tick(3800, 0.05) + np.pad(tick(4400, 0.05), (secs(0.05), 0))[:secs(0.05)], 0.4, 0.3), Wn("st3", "keys") + 0.12, -25)
heartbeat(T("st4"), T("st10") + 1.2, 70, 104, -18, -11)
n = secs(1.5); x = np.arange(n) / SR
br = bp(noise(n), 500, 2600) * (np.exp(-((x - 0.35) / 0.2) ** 2) * 0.8 + np.exp(-((x - 1.0) / 0.26) ** 2)); put("fx", norm(br), T("st4") + 0.9, -24)
put("fx", whoosh(2.6, 120, 900, 0.5), T("st9") + 0.3, -16)                      # the drift across the road
title(T("st11") - 0.25, 0.9, -9)
for i, s0 in enumerate(tl.starts("st11")): put("fx", tick(1500, 0.03), s0, -27, (i % 3 - 1) * 0.3)
p2 = json.load(open(f"{ROOT}/cues.json"))["pass2"]
for j in range(7): put("fx", step("leather"), p2 - (6 - j) * 0.55, -30 + j * 2.4, -0.2 + 0.12 * j)
for w_, lid, p in (("dangerous", "ch1", -0.5), ("safe", "ch2", 0.5)): title(Wn(lid, w_), 0.4, -17), put("fx", tone(196, 0.5, 0.01, 0.15), Wn(lid, w_), -22, p)

# ---- your brain tagging him: a lock tone, a tick for every item, a verdict
put("fx", tone(1320, 0.18, 0.004, 0.05, (1, 0.3)), T("st4") + 0.25, -25, 0.3)
for lid in ("st5", "st6", "st7"): put("fx", tick(2900, 0.03), T(lid), -22, 0.3)
vb = np.concatenate([tone(196, 0.16, 0.004, 0.06, (1, 0.6, 0.4)), np.zeros(secs(0.05)), tone(196, 0.3, 0.004, 0.12, (1, 0.6, 0.4))]); put("fx", vb, T("st8") + 0.2, -18, 0.3)   # THREAT: low, twice
put("fx", tone(1320, 0.18, 0.004, 0.05, (1, 0.3)), T("sx3") - 0.5, -25, 0.3)
for lid in ("sx3", "sx4", "sx5"): put("fx", tick(2900, 0.03), T(lid), -22, 0.3)
put("fx", tone(784, 0.5, 0.004, 0.18, (1, 0.3)) + np.pad(tone(988, 0.42, 0.004, 0.18, (1, 0.3)), (secs(0.08), 0))[:secs(0.5)], T("sx6"), -21, 0.3)                              # SAFE: a small bright chime

# ---- not hate. prediction.
title(T("ch7"), 0.5, -14); title(T("ch8"), 1.0, -7)

# ---- two heads: one tone left, one tone right, a beat apart
put("fx", tone(330, 1.2, 0.01, 0.4), Wn("two2", "one"), -19, -0.8); put("fx", tone(392, 1.4, 0.01, 0.5), Wn("two3", "both"), -18, 0.8)

# ---- the traffic stop
card = E("two3") + 0.45
put("hits", hit(1.0), card, -8)
put("fx", pan2(reverb(np.concatenate([siren(0.55, "whoop"), np.zeros(secs(0.12)), siren(0.7, "whoop")]), 1.6, 0.45, 3000), -0.2), card + 0.05, -15)
a, b = t_stop0, t_stop1; d = b - a; n = secs(d)
# ---- whose head are we in? 0 = the officer's (outside his car, behind it), 1 = the driver's (inside it). The sound follows the picture.
pov = (env(T("ts8") - 0.2, T("ts14") - 0.2, 0.5, 0.6) + 0.5 * env(T("ts14") - 0.2, T("ts16"), 0.6, 0.4) + 0.15 * env(T("ts16"), T("ts18"), 0.4, 0.4)
       + 0.85 * env(T("ts18"), T("ts20"), 0.4, 0.4) + 0.5 * env(T("ts20"), E("ts22") + 0.45, 0.4, 0.01)).clip(0, 1)
# ---- his music. From the cruiser it is what a car does to a song: sub and trunk rattle. From his seat it is the song.
m0 = card; m1 = E("ts22") + 0.45; mn = secs(m1 - m0)
src = licensed("car_music"); full = loop_to(norm(src), mn, 0.05) if src is not None else norm(trap_beat(m1 - m0))
gate = sosfiltfilt(butter(1, 14, "lp", fs=SR, output="sos"), np.abs(bp(full, None, 120, 3))); gate = gate / (gate.max() + 1e-9)
outside = bp(full, None, 150, 4) * 1.0 + bp(full, 150, 520, 2) * 0.16 + bp(noise(mn), 1700, 4600) * gate ** 1.5 * 0.05 + bp(noise(mn), 240, 420) * gate * 0.06   # panels and plate buzzing on every 808
outside = reverb(outside, 0.7, 0.18, 900)[:mn]
inside = np.tanh(full * 1.3) * 0.8 + bp(full, None, 110, 3) * 0.5
pv = pov[secs(m0):secs(m0) + mn]; tloc = np.arange(mn) / SR + m0
arrive = np.clip((tloc - m0) / (T("ts2") - m0), 0, 1) ** 1.6                                  # the cruiser rolls up behind him: it gets louder
knob = 1 - 0.8 * np.clip((tloc - (T("ts8") + 0.9)) / 0.7, 0, 1)                               # he hears the door, and turns it down
mus_out = rms_to(outside, -17) * arrive * (1 - pv) * (0.35 + 0.65 * knob); mus_in = rms_to(inside, -15) * pv * knob
cutf = np.ones(mn); cutf[-secs(0.006):] = np.linspace(1, 0, secs(0.006))
put("amb", pan2((mus_out + mus_in) * cutf, 0.35), m0)
# ---- the officer's world: his idle, the relay of the light bar, dispatch. Crisp in his head, a murmur through glass in the driver's.
off = np.zeros(N)
def puto(x, t, g):
    i = secs(t); k_ = min(len(x), N - i)
    if k_ > 0: off[i:i + k_] += x[:k_] * db(g)
puto(fade(rms_to(engine(d, 31), -24), 1.0, 0.6), a, 0)
t = a + 0.3
while t < b - 0.3:
    for o in (0, 0.16): puto(tick(950, 0.03), t + o, -27)
    t += 1 / 1.55 / 2
for txt, when, vc in (("Dispatch, twelve. Traffic stop, Elm and Fourth.", T("ts1") + 0.6, "am_onyx"), ("Ten four, twelve.", T("ts2") + 1.4, "af_sarah"),
                      ("Twelve, status check.", T("ts7") + 2.2, "af_sarah"), ("Twelve, do you copy.", T("ts10") + 0.4, "af_sarah"),
                      ("All units, stand by.", T("ts13") + 3.0, "af_sarah"), ("Twelve, respond.", T("ts16") + 0.2, "af_sarah")):
    puto(radio(txt, vc), when, -19)
off_far = bp(off, None, 620, 3) * 0.45
BUS["amb"] += pan2(off * (1 - pov) + off_far * pov, -0.5)
# ---- the driver's world: his own engine under him, louder when we are in his seat
drv = np.zeros(N); i0 = secs(a); e2 = fade(rms_to(engine(d, 38), -27), 1.0, 0.6); drv[i0:i0 + len(e2)] += e2[:N - i0]
BUS["amb"] += pan2(drv * (0.55 + 0.9 * pov), 0.5)
put("amb", fade(rms_to(np.stack([bp(brown(n), 35, 400)] * 2, 1), -30), 1.0, 0.6), a)
put("fx", whoosh(0.9, 300, 1400, 0.5) * 0.6 + np.pad(np.sin(2 * np.pi * 140 * np.arange(secs(0.9)) / SR) * 0.15, (0, 0)), T("ts8") + 0.2, -19, 0.55)   # window motor
n2 = secs(0.25); x = np.arange(n2) / SR
clk = bp(noise(n2), 2500, 7000) * (np.exp(-x / 0.004) + 0.7 * np.exp(-np.maximum(0, x - 0.09) / 0.006) * (x > 0.09)) + 0.4 * np.sin(2 * np.pi * 1900 * x) * np.exp(-x / 0.01)
put("fx", norm(clk), T("ts8") + 1.3, -15, 0.5)                                                # seatbelt
put("fx", reverb(tick(500, 0.08) * 1.5, 0.5, 0.3), T("ts7") + 0.4, -17, -0.6)                  # leather: a hand settling on a belt
heartbeat(T("ts3"), T("ts8") - 0.3, 78, 96, -17, -13); heartbeat(T("ts8"), T("ts14"), 84, 108, -16, -12); heartbeat(T("ts14"), E("ts22") + 0.3, 100, 124, -13, -8)
for lid in ("ts4", "ts5", "ts6"): put("hits", hit(0.35), T(lid), -17); put("fx", tone(196, 0.5, 0.005, 0.15), T(lid), -22, -0.6)
for lid in ("ts9", "ts10", "ts11", "ts12"): put("hits", hit(0.35), T(lid), -17); put("fx", tone(233, 0.5, 0.005, 0.15), T(lid), -22, 0.6)
for lid, p in (("ts17", -0.6), ("ts19", 0.6)): title(T(lid), 0.6, -12); put("fx", tone(147, 0.9, 0.005, 0.3), T(lid), -18, p)
ta, tb_ = T("ts20"), E("ts22") + 0.45; n3 = secs(tb_ - ta); x = np.arange(n3) / n3
rise = (np.sin(2 * np.pi * np.cumsum(58 * (1.9 ** x)) / SR) + 0.4 * np.sin(2 * np.pi * np.cumsum(116 * (1.9 ** x)) / SR) + 0.15 * bp(noise(n3), 400, 3000) * x ** 3) * x ** 1.4
rise[-secs(0.006):] *= np.linspace(1, 0, secs(0.006)); put("hits", rise, ta, -9)                # one tone rises, and cuts
put("amb", fade(pan2(rms_to(siren(tb_ - ta, "yelp")[:n3] * x ** 2, -30), 0.0), 0.5, 0.004), ta)   # a second unit, closing, cut with the tone

# ---- news: the same thing, as television
a, b = SC["news"]; put("amb", fade(rms_to(babble(b - a, 5, 350, 3000, seed=9), -27), 0.6, 1.0), a)
put("amb", fade(rms_to(np.stack([bp(noise(secs(b - a)), 1800, 7500)] * 2, 1), -39), 0.6, 1.0), a)
put("fx", tone(880, 0.35, 0.004, 0.09) * 0.8 + np.pad(tone(1175, 0.3, 0.004, 0.09), (secs(0.16), 0))[:secs(0.35)], a + 0.5, -22)   # a bulletin sting
put("hits", hit(0.8), T("news2") + 0.05, -12)

# ---- the other direction: quieter, as he says
put("fx", whoosh(1.4, 200, 1800, 0.5)[::-1].copy(), T("od1") - 0.2, -18); title(Wn("od4", "watching"), 0.5, -15)

# ---- the boy and the screen: what the set gives him, one at a time
a, b = SC["boy"]; put("amb", fade(rms_to(bp(babble(b - a, 2, 250, 1600, seed=11), None, 1500), -31), 1.0, 1.0), a)
put("amb", fade(rms_to(pan2(np.sin(2 * np.pi * 60 * np.arange(secs(b - a)) / SR) + 0.4 * bp(pink(secs(b - a)), 80, 400)), -43), 1, 1), a)
put("fx", pan2(fade(rms_to(bp(trap_beat(E("od7") - T("od7") + 0.5), 140, 3200), -21) + rms_to(muffled(trap_beat(E("od7") - T("od7") + 0.5)), -24), 0.05, 0.25)), T("od7"), 0)       # the rapper: a beat
put("fx", pan2(rms_to(cheer(E("od8") - T("od8") + 1.0), -22)), T("od8") - 0.1, 0); put("fx", tone(2800, 0.5, 0.002, 0.2, (1,)), T("od8"), -26)   # the athlete: a crowd, a whistle
put("fx", norm(keys(0.7, 14, 5)) , T("od9"), -22); put("fx", tick(700, 0.07), T("od9") + 0.5, -20)          # the dealer: quick hands, a zip
put("fx", norm(clang()), T("od10") + 0.35, -11)                                                             # the one in the cell: a door
for lid in ("od7", "od8", "od9", "od10"): put("fx", tick(1200, 0.04), T(lid), -22)
title(T("od17"), 0.4, -17)
for i, dt in enumerate((0.0, 0.25, 0.5)): put("fx", reverb(tone((392, 330, 262)[i], 0.9, 0.003, 0.25, (1, 0.5, 0.25)), 1.2, 0.4, 3500), T("od14") + 0.3 + dt, -21, (-0.3, 0.0, 0.3)[i])
put("fx", fade(tone(110, 2.4, 0.9, 0.9, (1, 0.5, 0.25)), 0.05, 0.6), T("od18") - 0.1, -15); title(T("od18"), 0.8, -11); title(T("od19"), 0.9, -10)

# ---- three rooms, three sets
a, b = SC["three"]
for i, (p, s0) in enumerate(((-0.8, a), (0.0, Wn("od20", "mexican") - 0.15), (0.8, Wn("od21", "white") - 0.15))):
    w = bp(babble(b - s0, 2, 250, 1500, seed=20 + i), None, 1400); m = (w[:, 0] + w[:, 1]) / 2
    put("amb", fade(pan2(rms_to(m, -32), p), 0.6, 0.5), s0)
    if i: put("fx", tick(900, 0.06), s0 + 0.15, -18, p); put("fx", tone(60, 0.5, 0.01, 0.2), s0 + 0.15, -18, p)   # a set switching on
put("hits", hit(0.7), T("od22"), -13)

# ---- the switch: a voice changing shape. A hum that climbs and tightens with the waveform.
a, b = SC["wave"]; n = secs(b - a); x = np.arange(n) / SR + a
def rr(u, a0, a1): return np.clip((u - a0) / max(1e-6, a1 - a0), 0, 1)
m = 0.45 * rr(x, T("sw3"), E("sw3")) + 0.55 * rr(x, T("sw4"), E("sw4"))
f0 = 104 * (1.42 ** m) * (1 + 0.012 * np.sin(2 * np.pi * 5.2 * x)); ph = 2 * np.pi * np.cumsum(f0) / SR
buzz = sum(np.sin(k * ph) / k for k in range(1, 14))
vow = bp(buzz, 500, 900) * (1 - 0.6 * m) + bp(buzz, 900, 1500) * 0.6 + bp(buzz, 2200, 3000) * (0.15 + 0.5 * m)
syl = 0.45 + 0.55 * np.abs(sosfiltfilt(butter(1, 3.0, "lp", fs=SR, output="sos"), noise(n))) * 6
wake = rr(x, T("sw2") - 0.1, T("sw2") + 0.9)
put("fx", fade(pan2(rms_to(vow * np.clip(syl, 0, 1.6) * wake, -24)), 0.3, 0.5), a)
for w_ in ("interview", "sales", "meeting"): put("fx", tick(2000, 0.03), Wn("sw3", w_), -24)

# ---- code-switching: an office heard through glass
a, b = SC["glass"]; d = b - a; n = secs(d)
put("amb", fade(rms_to(bp(babble(d, 5, 250, 1400, seed=30), None, 1100), -29), 1.0, 0.8), a)
put("amb", fade(rms_to(np.stack([bp(pink(n), 90, 600)] * 2, 1), -36), 1.0, 0.8), a)
put("amb", pan2(rms_to(bp(phone_ring(1), 300, 1800), -33), -0.6), a + 5.5); put("amb", pan2(rms_to(bp(phone_ring(1), 300, 1800), -34), 0.7), a + 17.0)
put("amb", fade(pan2(rms_to(bp(keys(d, 8, 9), None, 2500), -36), 0.4), 1, 1), a)
for lid in ("sw5", "sw6", "sw7"): title(T(lid), 0.5, -14)
put("fx", fade(tone(98, 3.0, 1.0, 1.0, (1, 0.6, 0.3)) + tone(103.8, 3.0, 1.0, 1.0, (1, 0.6, 0.3)), 0.05, 0.8), Wn("sw12", "two") - 0.1, -17)   # two notes that do not agree

# ---- whose fault
title(T("wf2"), 0.7, -12); title(T("wf3"), 1.0, -8)

# ---- the observer: the score is gone. A room, and one warm note when it is named.
a, b = SC["observer"]; put("amb", fade(rms_to(np.stack([bp(pink(secs(b - a)), 60, 700), bp(pink(secs(b - a)), 60, 700)], 1), -40), 1.5, 1.5), a)
obs = fade(tone(220, 4.5, 0.6, 2.2, (1, 0.35, 0.12)) + 0.6 * tone(329.63, 4.5, 0.9, 2.0, (1, 0.25)) + 0.4 * tone(440, 4.5, 1.2, 1.8, (1, 0.2)), 0.05, 1.0)
put("music", pan2(reverb(obs, 2.6, 0.5, 4000)), Wn("ob5", "the") - 0.1, -13)

# ---- the half-second: a clock, a mark, and the space after it
a, b = SC["halfsecond"]
t = a + 0.4
while t < b - 0.3: put("fx", tick(1800, 0.025), t, -30, 0.0); t += 0.5
put("fx", tick(2600, 0.05), Wn("hs1", "script"), -16, -0.4); put("hits", hit(0.4), Wn("hs1", "script"), -16)
sw = fade(tone(220, 2.6, 0.8, 1.2, (1, 0.4, 0.15)) + 0.5 * tone(330, 2.6, 1.0, 1.0, (1, 0.3)), 0.05, 0.6); put("music", pan2(reverb(sw, 2.0, 0.4, 4000)), Wn("hs2", "catches"), -15)
put("music", pan2(reverb(fade(tone(277.18, 3.4, 1.0, 1.6, (1, 0.3)) + tone(220, 3.4, 1.0, 1.6, (1, 0.3)), 0.05, 0.8), 2.4, 0.5, 4000)), T("hs3"), -15)

# ---- the new script: sets going dark one by one, a pencil for every line you write
a, b = t_new0, t_new1; d = b - a
wallx = babble(d, 6, 350, 3000, seed=40); dk = np.clip((np.arange(secs(d)) / SR + a - T("ns1")) / max(1e-6, E("ns4") - T("ns1")), 0, 1)
put("amb", fade(rms_to(wallx, -28) * (1 - dk[:, None]) ** 1.4, 0.8, 0.3), a)
for i in range(26):
    t_ = T("ns1") + (E("ns4") - T("ns1")) * (i + rng.random()) / 26; n4 = secs(0.22); x = np.arange(n4) / SR
    put("fx", np.sin(2 * np.pi * np.cumsum(900 * np.exp(-x / 0.05) + 60) / SR) * np.exp(-x / 0.07), t_, -27, rng.uniform(-0.9, 0.9))   # a set powering down
for j, s0 in enumerate((Wn("ns2", "feet"), Wn("ns2", "voice"), Wn("ns2", "shoulders"), Wn("ns3", "one"))):
    n5 = secs(0.6); x = np.arange(n5) / n5
    put("fx", bp(noise(n5), 1800, 5200) * np.sin(np.pi * x) ** 0.5 * (0.7 + 0.3 * np.sin(2 * np.pi * 23 * x)), s0, -24 if j < 3 else -20, -0.3 + 0.2 * j)   # pencil
    put("music", pan2(reverb(tone((277.18, 329.63, 369.99, 440.0)[j], 2.2, 0.02, 0.8, (1, 0.3, 0.1)), 2.2, 0.45, 4500)), s0, -17 if j < 3 else -13)

# ---- the payoff: two people walking the same line toward each other, and a nod
CU = json.load(open(f"{ROOT}/cues.json")); tm = CU.get("pass3", T("ns3"))
ta_, tb2 = T("ns1") + 0.2, E("ns4") + 0.5; stp = 0.37 * 226.8 / (1.2 * 1920 / (tb2 - ta_)); t = ta_ + 0.3; k = 0
while t < tb2 - 0.3:
    u = (t - ta_) / (tb2 - ta_); put("fx", step("sidewalk"), t, -24, -0.9 + 1.8 * u); put("fx", step("leather"), t + stp * 0.5 + 0.9, -29, 0.9 - 1.8 * u); t += stp; k += 1
put("music", pan2(reverb(tone(329.63, 2.4, 0.03, 0.9, (1, 0.3, 0.1)) + np.pad(tone(440.0, 2.2, 0.03, 0.9, (1, 0.3)), (secs(0.22), 0))[:secs(2.4)], 2.4, 0.5, 4500)), tm - 0.1, -14)

# ---- close
tc0 = E("ns4") + 1.0; title(tc0, 1.0, -8, sweep=False); title(tc0 + 1.4, 0.6, -13, sweep=False)
zt = E("cl1") + 0.9; n6 = secs(0.28); x = np.arange(n6) / SR
put("hits", (np.sin(2 * np.pi * 220 * x) + 0.5 * np.sin(2 * np.pi * 330 * x)) * np.exp(-((x - 0.07) / 0.075) ** 2), zt, -15)

# ---- a breath of air on each crossfade between plates
for name in ("eye", "screens", "couch", "street1", "street2", "stop", "news", "boy", "three", "glass", "observer", "newscript"):
    put("fx", pan2(whoosh(0.8, 250, 2400, 0.55)), SC[name][0] - 0.25, -25)

# ================================================================== mix
TRIM = 1.0                                   # everything that is not the voice, as one fader
amb = BUS["amb"] * duck(3) * db(TRIM); fx = BUS["fx"] * duck(1.5) * db(TRIM); hits = BUS["hits"] * db(TRIM); music = BUS["music"] * db(TRIM)
# Voice-keyed ceiling: while he is speaking, the world may not come closer than FLOOR dB under him. In the gaps it is free.
FLOOR = 13.0; bl = secs(0.05); k = N // bl
voice = nar * db(-3); bgsum = (amb + fx + hits + music).mean(1)
vr = np.sqrt((voice[:k * bl].reshape(k, bl) ** 2).mean(1)); br = np.sqrt((bgsum[:k * bl].reshape(k, bl) ** 2).mean(1))
vs = np.maximum.reduce([vr, np.roll(vr, 1), np.roll(vr, -1), np.roll(vr, 2), np.roll(vr, -2), np.roll(vr, 3)])       # hold across syllables
g = np.where(vs > 0.012, np.minimum(1.0, vs * db(-FLOOR) / (br + 1e-9)), 1.0)
g = np.minimum.reduce([g, np.roll(g, 1), np.roll(g, -1)])
g = np.pad(np.repeat(g, bl), (0, N - k * bl), constant_values=1.0)
g = sosfiltfilt(butter(1, 9, "lp", fs=SR, output="sos"), g).clip(0.05, 1.0)[:, None]
amb, fx, hits, music = amb * g, fx * g, hits * g, music * g
# And a ceiling for the gaps: the world can fill a pause, but it does not get louder than the man talking.
vref = np.median(vr[vr > 0.02]); bl2 = secs(0.2); k2 = N // bl2; bg2 = (amb + fx + hits + music).mean(1)
b2 = np.sqrt((bg2[:k2 * bl2].reshape(k2, bl2) ** 2).mean(1)); g2 = np.minimum(1.0, vref * db(-2.5) / (b2 + 1e-9))
g2 = np.minimum.reduce([g2, np.roll(g2, 1), np.roll(g2, -1)]); g2 = np.pad(np.repeat(g2, bl2), (0, N - k2 * bl2), constant_values=1.0)
g2 = sosfiltfilt(butter(1, 3, "lp", fs=SR, output="sos"), g2).clip(0.05, 1.0)[:, None]
amb, fx, music = amb * g2, fx * g2, music * g2          # title impacts keep their weight
mix = np.stack([nar, nar], 1) * db(-3) + amb + fx + hits + music
tail = secs(0.4); mix[-tail:] *= np.linspace(1, 0, tail)[:, None]
def r(x): return round(20 * math.log10(np.sqrt(np.mean(x ** 2)) + 1e-12), 1)
print("rms dBFS  voice", r(nar * db(-3)), " amb", r(amb), " fx", r(fx), " hits", r(hits), " music", r(music), " | premaster peak", round(20 * math.log10(np.abs(mix).max()), 2))
os.makedirs(f"{ROOT}/audio/stems", exist_ok=True)
sf.write(f"{ROOT}/audio/mix_premaster.wav", mix.astype(np.float32), SR)
sf.write(f"{ROOT}/audio/sfx_bed_only.wav", (amb + fx + hits + music).astype(np.float32), SR)
json.dump({"steps": steps}, open(f"{ROOT}/audio/steps.json", "w"))
