"""mix_talk.py — the offline SOUND STAGE for talking-head edits (Jason, 2026-10-11: "SFX decent but not pinpoint").
Replaces per-clip <Audio volume> guesses with a real mix, per references/r20-editing-masterclass.md:
  * every SFX is levelled RELATIVE TO HIS VOICE by role (ticks way under, impacts closer), measured, not guessed
  * placed by the library's measured lead, so the peak/onset lands exactly on the cue frame
  * layers: one cue can expand to low/mid/high (same file at 0.6x and 1.2x speed + a texture) or a 3-bass stack
  * reverb tails on cues marked "tail" (no dead stops), soft ducking of the SFX bus under his voice
  * master: voice + SFX bus, -14 LUFS / -1.5 dBTP; also writes the SFX stem so levels can be checked
Usage: python3 mix_talk.py VOICE(.mp4|.wav) CUES.json LIBRARY.json SFX_ROOT OUT.wav [--fps 30] [--len_s N]
CUES.json: [{"f": frame, "id": "lib id", "role": "tick|texture|typing|whoosh|riser|ui|accent|notif|impact|sub", "db": +/-trim, "speed": 1.0, "tail": false, "pre": 0}]
"""
import json, os, subprocess, sys, argparse
import numpy as np

SR = 48000
# level of each role relative to his voice's speech punch (dB). Ticks sit far under, impacts closest. (r20 sound spec)
ROLE_DB = {"tick": -24, "typing": -26, "texture": -20, "whoosh": -16, "riser": -17, "ui": -13, "accent": -14,
           "notif": -12, "impact": -9, "sub": -10, "slowmo": -13}
DUCK = {"tick": 0, "typing": 0, "texture": 4, "whoosh": 3, "riser": 4, "ui": 2, "accent": 1, "notif": 2, "impact": 0, "sub": 0, "slowmo": 0}

ap = argparse.ArgumentParser()
ap.add_argument("voice"); ap.add_argument("cues"); ap.add_argument("lib"); ap.add_argument("root"); ap.add_argument("out")
ap.add_argument("--fps", type=float, default=30); ap.add_argument("--len_s", type=float, default=0)
A = ap.parse_args()

def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).copy()

def punch_db(x, win=0.05):
    """loudness of the loudest 50 ms of a sound (how loud it 'hits')"""
    m = x.mean(1); n = int(win * SR)
    if len(m) < n: n = max(1, len(m))
    e = np.convolve(m ** 2, np.ones(n) / n, mode="valid")
    return 10 * np.log10(e.max() + 1e-12)

def speed(x, s):
    if abs(s - 1) < 1e-3: return x
    n = int(len(x) / s); t = np.arange(n) * s
    return np.stack([np.interp(t, np.arange(len(x)), x[:, c]) for c in range(2)], 1).astype(np.float32)

rng = np.random.default_rng(5)
def reverb(x, secs=2.6, wet=0.32):
    n = int(secs * SR); t = np.arange(n) / SR
    ir = (rng.standard_normal(n) * np.exp(-t / 0.75)).astype(np.float32)
    ir = np.convolve(ir, np.ones(24) / 24, mode="same")            # darker tail
    ir /= np.sqrt((ir ** 2).sum())
    pad = np.zeros((len(x) + n, 2), np.float32); pad[:len(x)] = x
    out = np.zeros_like(pad)
    for c in range(2):
        L = len(pad); F = 1 << (L + n - 1).bit_length()
        y = np.fft.irfft(np.fft.rfft(pad[:, c], F) * np.fft.rfft(ir, F), F)[:L]
        out[:, c] = y
    return (1 - wet) * pad + wet * out * 0.9

voice = load(A.voice)
L = max(len(voice), int(A.len_s * SR))
V = np.zeros((L, 2), np.float32); V[:len(voice)] = voice
mono = V.mean(1)
# voice reference = 90th percentile of 50 ms punch while he talks
n = int(0.05 * SR); env = np.sqrt(np.convolve(mono ** 2, np.ones(n) / n, mode="same") + 1e-12)
talk = env[env > env.max() * 0.05]
VREF = 20 * np.log10(np.percentile(talk, 90))
# ducking envelope (smoothed voice presence 0..1)
k = int(0.15 * SR); pres = np.convolve((env > env.max() * 0.06).astype(np.float32), np.ones(k) / k, mode="same")

lib = json.load(open(A.lib)); lib = {i["id"]: i for i in (lib if isinstance(lib, list) else lib["sounds"])}
cache = {}
bus = np.zeros((L, 2), np.float32)
log = []
for c in json.load(open(A.cues)):
    it = lib[c["id"]]
    if it["file"] not in cache: cache[it["file"]] = load(os.path.join(A.root, it["file"].replace("sfx/", "", 1)))
    x = speed(cache[it["file"]], c.get("speed", 1.0))
    lead = it.get("lead", 0) / c.get("speed", 1.0)
    if c.get("tail"): x = reverb(x)
    g_db = VREF + ROLE_DB[c["role"]] + c.get("db", 0) - punch_db(x)
    x = x * (10 ** (g_db / 20))
    st = int((c["f"] / A.fps - lead - c.get("pre", 0) / A.fps) * SR)
    if st < 0: x = x[-st:]; st = 0
    e = min(L, st + len(x)); x = x[: e - st]
    # short fades so nothing clicks
    fi = min(len(x), int(0.004 * SR)); x[:fi] *= np.linspace(0, 1, fi)[:, None]
    if DUCK[c["role"]]:   # beds and moves dip under his voice; ticks and impacts stay on the frame
        x = x * (10 ** (-DUCK[c["role"]] * pres[st:e] / 20))[:, None]
    bus[st:e] += x
    log.append((c["f"], c["id"], c["role"], round(g_db, 1)))
sfx = bus
# gentle bus limiter so stacked hits never clip into the voice
pk = np.abs(sfx).max()
if pk > 0.7: sfx = np.tanh(sfx / 0.7) * 0.7
mix = V + sfx
base = os.path.splitext(A.out)[0]
def wav(p, x):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "pcm_s24le", p], input=x.astype(np.float32).tobytes(), check=True)
wav(base + "_sfx.wav", sfx); wav(base + "_raw.wav", mix)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", base + "_raw.wav", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", str(SR), "-c:a", "pcm_s24le", A.out], check=True)
print(f"voice ref {VREF:.1f} dBFS punch; {len(log)} cues; sfx stem peak {20*np.log10(np.abs(sfx).max()+1e-9):.1f} dBFS")
json.dump(log, open(base + "_log.json", "w"))
