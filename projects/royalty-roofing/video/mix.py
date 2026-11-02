import json, subprocess, numpy as np, soundfile as sf
SR = 48000; A = "/home/user/ApoheniaQuest/.claude/skills/jason-video-editor/assets/"
LIB = {s["id"]: s for s in json.load(open(A + "sfx/library.json"))["sounds"]}
vo, sr = sf.read("vo.wav", dtype="float32"); vo = vo if vo.ndim == 1 else vo.mean(1); assert sr == SR
L = len(vo); T = L / SR; t = np.arange(L) / SR
db = lambda x: 10 ** (x / 20)
def load(f):
    y = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(y, np.float32).reshape(-1, 2).copy()
# voice activity envelope (for ducking)
win = int(0.05 * SR); env = np.sqrt(np.convolve(vo ** 2, np.ones(win) / win, "same")); act = (env > db(-38)).astype(float)
k = int(0.25 * SR); act = np.clip(np.convolve(act, np.ones(k) / k, "same") * 2, 0, 1)
vpk = np.max(np.abs(vo))
# ---- synthesized bed: warm pad, Cmaj9 - Am9 - Fmaj7#11 - G6/9, 4 s per chord, soft sub pulse
CH = [[48, 55, 59, 62, 64], [45, 52, 55, 59, 60], [41, 48, 52, 55, 59], [43, 50, 55, 57, 62]]
hz = lambda m: 440 * 2 ** ((m - 69) / 12)
bed = np.zeros((L, 2), np.float32); seg = 4.0
for c in range(int(T / seg) + 2):
    notes = CH[c % 4]; t0 = c * seg; i0 = int(t0 * SR); n = int((seg + 1.5) * SR)
    if i0 >= L: break
    n = min(n, L - i0); tt = np.arange(n) / SR
    envc = np.minimum(1, tt / 1.2) * np.minimum(1, np.maximum(0, (seg + 1.5 - tt) / 1.5))
    for j, m in enumerate(notes):
        f = hz(m + 12 if j > 2 else m)
        for det, pan in ((-0.12, 0.3), (0.12, 0.7)):
            w = np.sin(2 * np.pi * f * (1 + det / 100) * tt + j) * 0.6 + np.sin(2 * np.pi * 2 * f * tt) * 0.12
            bed[i0:i0 + n, 0] += (w * envc * (1 - pan)).astype(np.float32); bed[i0:i0 + n, 1] += (w * envc * pan).astype(np.float32)
    sub = np.sin(2 * np.pi * hz(notes[0] - 12) * tt) * np.exp(-tt * 2.2) * 0.9
    bed[i0:i0 + n] += (sub[:, None] * np.array([0.5, 0.5])).astype(np.float32)
# gentle low-pass (one-pole) for warmth
a = np.exp(-2 * np.pi * 2200 / SR)
for ch in range(2):
    y = bed[:, ch]; out = np.zeros_like(y); z = 0.0
    for i0 in range(0, L, 4800):
        blk = y[i0:i0 + 4800]; o = np.empty_like(blk)
        for i, v in enumerate(blk): z = (1 - a) * v + a * z; o[i] = z
        out[i0:i0 + 4800] = o
    bed[:, ch] = out
rms = lambda x: np.sqrt(np.mean(x ** 2) + 1e-12)
vrms = rms(vo[env > db(-38)]); bed *= (vrms * db(-19)) / rms(bed)
g = 1 - (1 - db(-4)) * act                       # 4 dB duck under speech
drop = json.load(open("cues.json")); tdrop = [c["t"] for c in drop if c["role"] == "drop"][0]
gate = np.ones(L); gate[int((tdrop - 0.32) * SR):int(tdrop * SR)] = 0.0   # ~300 ms of silence before the drop
gate = np.convolve(gate, np.ones(int(0.04 * SR)) / int(0.04 * SR), "same")
fade = np.minimum(1, t / 1.5) * np.minimum(1, np.maximum(0, (T - t) / 2.5))
bed *= (g * gate * fade)[:, None]
# ---- SFX by peak
sfx = np.zeros((L, 2), np.float32)
for c in drop:
    s = LIB[c["id"]]; x = load(A + s["file"]); pk = np.max(np.abs(x)) + 1e-9
    x = x / pk * vpk * db(c["db"]); st = int((c["t"] - s.get("lead", 0)) * SR)
    if st < 0: x = x[-st:]; st = 0
    n = min(len(x), L - st); sfx[st:st + n] += x[:n]
sfx *= (1 - (1 - db(-3)) * act)[:, None]          # light sidechain under the voice
mix = np.stack([vo, vo], 1) + bed + sfx
sf.write("mix_pre.wav", mix, SR, subtype="FLOAT")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "mix_pre.wav", "-af", "loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000", "-ar", "48000", "mix.wav"], check=True)
print("mix ok", round(T, 2))
