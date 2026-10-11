"""World sound: public-domain score (Musopen recordings) + CC0 field recordings (archive.org SSE/BSB/mixkit libraries).
Everything is levelled against the narration and ducked under it. -> music.wav, amb.wav (48k stereo)"""
import subprocess, json, numpy as np
SR = 48000; L = int(184 * SR); PD = "../pd/"
def load(f, ss=0, dur=None):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(ss), "-i", PD + f] + (["-t", str(dur)] if dur else []) + ["-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.float32).reshape(-1, 2).copy()
db = lambda x: 10 ** (x / 20)
rms = lambda a: np.sqrt(np.mean(a ** 2) + 1e-12)
def fade(a, fi, fo):
    n = len(a); i = np.ones(n)
    if fi: k = min(n, int(fi * SR)); i[:k] = np.sin(np.linspace(0, np.pi / 2, k)) ** 2
    if fo: k = min(n, int(fo * SR)); i[n - k:] *= np.cos(np.linspace(0, np.pi / 2, k)) ** 2
    return a * i[:, None]
def put(bus, a, t, gain_db, pan=0.0):
    s = int(t * SR); a = a[: max(0, L - s)] * db(gain_db)
    a = a * np.array([np.sqrt(0.5 - pan / 2) * 1.414, np.sqrt(0.5 + pan / 2) * 1.414])[None, :]
    bus[s:s + len(a)] += a
def norm(a, target_db): return a / rms(a) * db(target_db)  # set clip RMS (dBFS)
# voice envelope for ducking (narration RMS sets every level)
v = load("../proof/vo.wav")[:, 0]; v = np.pad(v, (0, max(0, L - len(v))))[:L]
VR = 20 * np.log10(rms(v[np.abs(v) > 0.01]))
win = int(0.05 * SR); env = np.sqrt(np.convolve(v ** 2, np.ones(win) / win, "same"))
act = (env > db(VR - 18)).astype(float)
k = int(0.35 * SR); act = np.convolve(act, np.ones(k) / k, "same"); act = np.clip(act * 3, 0, 1)  # smooth, hold
sm = int(0.25 * SR); act = np.convolve(act, np.ones(sm) / sm, "same")
print("voice speech RMS", round(VR, 1), "dBFS")
music = np.zeros((L, 2), np.float32); amb = np.zeros((L, 2), np.float32)
# ── score ── (levels: under speech ≈ voice −21 dB; between lines it breathes up ~8 dB)
m1 = fade(load("brahms1_intro.ogg", 0, 79.2), 2.5, 1.6); put(music, norm(m1, VR - 15), 0.0, 0)          # tension: pounding timpani pedal
m2 = fade(load("grieg_morning.ogg", 24.1, 130.8 - 84.6), 3.0, 1.4); put(music, norm(m2, VR - 15), 84.6, 0)  # sunrise: climax lands on "let him run"
m3 = fade(load("brahms3_iii.ogg", 0, 51.0), 2.5, 3.5); put(music, norm(m3, VR - 14), 130.6, 0)          # the mirror
music *= (db(-7) + (1 - db(-7)) * (1 - act))[:, None] * 1.0
# ── world (story section only, 0–130) ──
def loop(f, dur, ss=0, seg=None):
    a = load(f, ss, seg); out = np.zeros((int(dur * SR), 2), np.float32); x = 0; xf = int(0.8 * SR)
    while x < len(out):
        b = fade(a.copy(), 0.8 if x else 0, 0.8); n = min(len(b), len(out) - x); out[x:x + n] += b[:n]; x += len(b) - xf
    return out
crowd = loop("men_murmur.wav", 79.0); crowd = fade(crowd, 3.0, 2.5)
put(amb, norm(crowd, VR - 30), 0.0, 0, -0.2)                                    # the men around the yard
put(amb, fade(norm(loop("men_murmur.wav", 44.0, 12), VR - 33), 2.5, 4.0), 84.6, 0, -0.2)
yard = loop("palace_murmur.wav", 79.0); put(amb, fade(norm(yard, VR - 31), 3, 2.5), 0.0, 0, 0.25)   # dirt, footsteps, court
put(amb, fade(norm(loop("palace_murmur.wav", 45.0), VR - 33), 2.5, 4), 84.6, 0, 0.25)
wind = loop("wind_prairie.wav", 131.0, 5); put(amb, fade(norm(wind, VR - 34), 4, 4), 0.0, 0)
put(amb, fade(norm(load("wind_prairie.wav", 30, 52), VR - 40), 4, 6), 129.5, 0)          # a ghost of wind into the mirror
# horse: every sound placed on the word that names it (peak-aligned)
H = [  # (file, src start, dur, at, dB vs voice RMS (peak-ish), pan)
 ("neigh_053889.mp3", 0.3, 3.2, 0.6, -14, 0.5),        # far off, before the first word
 ("scared_stallion.wav", 0.0, 6.0, 12.1, -8, -0.15),   # "a black horse is screaming and rearing"
 ("neigh3.mp3", 0.1, 2.0, 16.4, -11, 0.3),
 ("hoof_clatter.mp3", 1.6, 5.5, 24.6, -12, 0.1),       # the riders try him
 ("big_snort.wav", 0.15, 1.2, 27.9, -10, -0.2),         # "thrown"
 ("neigh2.mp3", 6.4, 2.2, 30.0, -12, 0.35),             # "backed away"
 ("walk_dirt.wav", 0.4, 8.0, 37.0, -17, 0.3),           # "take the horse away"
 ("big_snort.wav", 0.15, 1.2, 53.6, -10, 0.1),          # "lunges"
 ("stallion_neigh.wav", 0.0, 2.9, 55.2, -11, -0.1),     # "jumping away"
 ("walk_dirt.wav", 9.0, 4.0, 61.0, -15, 0.0),           # hooves stamping at the shadow
 ("neigh2.mp3", 0.2, 1.8, 68.9, -15, 0.4),              # restless under the laughter
 ("walk_dirt.wav", 2.0, 3.0, 85.0, -18, 0.0),           # you walk forward
 ("big_snort.wav", 0.15, 1.2, 91.0, -12, -0.1),         # head turned to the sun
 ("breathing.mp3", 40.0, 8.0, 98.0, -14, 0.0),          # "you speak low", trembling under your palm
 ("big_snort.wav", 0.15, 1.2, 106.8, -11, 0.0),         # "in one motion"
 ("gallop_single.mp3", 0.0, 7.0, 110.6, -9, -0.3),      # "and you let him run"
 ("gallop_dirt.wav", 0.5, 6.0, 110.9, -14, 0.3),
 ("stallion_neigh.wav", 0.0, 2.9, 112.6, -11, 0.2),
 ("walk_dirt.wav", 4.0, 5.0, 115.2, -17, 0.0),          # riding back
]
for f, ss, d, at, g, pan in H:
    a = fade(load(f, ss, d), 0.03, min(0.8, d / 3)); pk = np.max(np.abs(a)) + 1e-9
    put(amb, a / pk * db(VR + 8 + g), at, 0, pan)       # peak relative to the voice
# the men
put(amb, fade(norm(load("laugh_group.wav", 1.0, 5.5), VR - 16), 0.2, 2.0), 66.3, 0, -0.3)      # "the men are laughing at you"
put(amb, fade(norm(load("men_cheer.wav", 0.5, 7.0), VR - 19), 0.6, 3.0), 115.3, 0, 0.2)        # the ride back
# the held breath: the world drops out for "What do you do?" (bed carries the heartbeat)
g = np.ones(L); a0, a1 = int(78.6 * SR), int(84.4 * SR); g[a0:a1] = 0.06
g = np.convolve(g, np.ones(int(0.6 * SR)) / int(0.6 * SR), "same"); amb *= g[:, None]
amb *= (db(-3) + (1 - db(-3)) * (1 - act))[:, None]
for n, a in (("music.wav", music), ("amb.wav", amb)):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", n], input=np.clip(a, -1, 1).astype(np.float32).tobytes())
print("ok")
