"""Scene sound world: public-domain score + CC0 field recordings, placed on words, ducked under the voice.
usage: world_scene.py SCENE WORKDIR PD_DIR -> WORKDIR/sNN/{music.wav,amb.wav}"""
import subprocess, json, sys, re, numpy as np
import importlib as _il, os as _os
_CH = _os.environ.get("CH"); C = _il.import_module("ch_" + _CH) if _CH else None
si = int(sys.argv[1]); WD = sys.argv[2]; PD = sys.argv[3].rstrip("/") + "/"; D = f"{WD}/s{si:02d}"
SR = 48000
W = json.load(open(D + "/words.json"))
LEN = float(re.search(r"const LEN=([\d.]+)", open(D + "/scene.js").read()).group(1))
HOLD = json.loads(re.search(r"const HOLD=(.*);", open(D + "/scene.js").read()).group(1))
L = int((LEN + 0.5) * SR)
# music: (file, offset s, level vs voice, start-anchor word or None) ; beds: (file, level, pan, from-word|None, to-word|None) ; hits: (file, ss, dur, word, level, pan)
S_ALL = {
 0: dict(music=[("dvorak_lento.ogg", 0, -15, None)], beds=[("fire_rumble.wav", -38, 0, None, None)]),
 1: dict(music=[("haydn_lark_adagio.ogg", 0, -15, None)], beds=[("birds_wings.wav", -40, 0.3, None, None)]),
 2: dict(music=[("mendel_scottish_i.ogg", 0, -15, None)], beds=[("wind_prairie.wav", -40, 0, None, None)],
         hits=[("thunder_clap.wav", 0, 7, "thunderbolt", -10, -0.2), ("lion_growl.wav", 0.5, 5, "lion", -13, 0.2), ("fire_crackle.wav", 0, 7, "burned", -16, 0)]),
 3: dict(music=[("mendel_italian_ii.ogg", 0, -15, None)], beds=[("court_murmur.wav", -36, -0.2, "envoys", None)]),
 5: dict(music=[("beet_q6_adagio.ogg", 0, -15, None)], beds=[("fire_rumble.wav", -40, 0, "night", None)], hits=[("sword_draw.wav", 0, 2.5, "dagger", -18, 0.3)]),
 6: dict(music=[("coriolan.ogg", 0, -14, None)], beds=[("court_murmur.wav", -34, 0, None, "Stop")], hits=[("horrified.wav", 0, 6, "murdered", -14, 0)]),
 7: dict(music=[("brahms2_ii.ogg", 0, -15, None)], beds=[("market.wav", -34, -0.2, None, "Except"), ("birds_wings.wav", -40, 0.3, None, None)],
         hits=[("laugh_group.wav", 1, 4, "laugh", -18, -0.3)]),
 8: dict(music=[("eroica_i.ogg", 0, -15, None)], beds=[("river_rapids.wav", -28, 0.2, "Granicus", None), ("battle.wav", -24, 0, "chaos", None)],
         hits=[("gallop_single.mp3", 0, 6, "ride", -12, -0.3), ("sword_draw.wav", 0, 2.5, "blade", -12, 0.2)]),
 9: dict(music=[("brahms_tragic.ogg", 0, -16, None)], beds=[("fire_rumble.wav", -40, 0, None, None)]),
 10: dict(music=[("dvorak_dumka.ogg", 0, -15, None)], beds=[("wind_prairie.wav", -38, 0, None, None)]),
 11: dict(music=[("mendel_scottish_iii.ogg", 0, -15, None)], beds=[("wind_prairie.wav", -30, 0, "desert", None)], hits=[("eagle.wav", 2, 5, "Siwa", -22, 0.4)]),
 12: dict(music=[("brahms4_ii.ogg", 0, -15, None)], beds=[("fire_crackle.wav", -32, 0.2, "campfires", "dawn"), ("wind_prairie.wav", -36, 0, None, None)],
          hits=[("neigh_053889.mp3", 0.3, 3, "Persian", -24, 0.6), ("battle.wav", 10, 9, "broke", -22, 0)]),
 13: dict(music=[("brahms4_i.ogg", 0, -16, None)], beds=[("serious_chamber.wav", -34, 0, None, None)]),
 14: dict(music=[("eroica_funebre.ogg", 0, -14, "collapse")], beds=[("party_crowd.wav", -26, 0, None, "Cleitus"), ("court_murmur.wav", -32, 0, "Cleitus", "kill")],
          hits=[("men_drunk_laugh.wav", 0, 6, "praising", -18, 0.2), ("horrified.wav", 0, 6, "kill", -16, 0)]),
 15: dict(music=[("grieg_ase.ogg", 0, -15, None)], beds=[("wind_prairie.wav", -30, 0, "desert", None)],
          hits=[("lion_elephant.wav", 8, 8, "India", -20, 0.3), ("thunder_roll.wav", 0, 8, "Porus", -22, 0), ("river_gentle.wav", 0, 8, "river", -26, -0.2)]),
 16: dict(music=[("eroica_funebre.ogg", 0, -15, None)], beds=[("court_murmur.wav", -40, 0, None, None)]),
 17: dict(music=[("brahms3_iii.ogg", 0, -15, None)], beds=[]),
 18: dict(music=[("mendel_scottish_iii.ogg", 0, -15, None)], beds=[("fire_rumble.wav", -42, 0, None, None)]),
}
S = (C.WORLD if C else S_ALL)[si]
def load(f, ss=0, dur=None):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(ss), "-i", PD + f] + (["-t", str(dur)] if dur else []) + ["-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.float32).reshape(-1, 2).copy()
db = lambda x: 10 ** (x / 20); rms = lambda a: np.sqrt(np.mean(a ** 2) + 1e-12)
def fade(a, fi, fo):
    n = len(a); g = np.ones(n)
    if fi: k = min(n, int(fi * SR)); g[:k] = np.sin(np.linspace(0, np.pi / 2, k)) ** 2
    if fo: k = min(n, int(fo * SR)); g[n - k:] *= np.cos(np.linspace(0, np.pi / 2, k)) ** 2
    return a * g[:, None]
def put(bus, a, t, pan=0.0):
    s = max(0, int(t * SR)); a = a[: max(0, L - s)]
    bus[s:s + len(a)] += a * np.array([np.sqrt(1 - pan), np.sqrt(1 + pan)])[None, :]
def word_t(w):
    for ln in W:
        for x in ln["w"]:
            if re.sub(r"[^a-z]", "", x[0].lower()).startswith(re.sub(r"[^a-z]", "", w.lower())): return x[1]
    print("anchor not found:", w); return None
def loop(f, dur, ss=0):
    a = load(f, ss); out = np.zeros((int(dur * SR), 2), np.float32); x = 0; xf = int(0.8 * SR)
    if len(a) < 2 * xf: return out
    while x < len(out):
        b = fade(a.copy(), 0.8 if x else 0, 0.8); n = min(len(b), len(out) - x); out[x:x + n] += b[:n]; x += len(b) - xf
    return out
v = load("../film-work/s%02d/vo.wav" % si) if False else None
vv = subprocess.run(["ffmpeg", "-v", "error", "-i", D + "/vo.wav", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
v = np.frombuffer(vv, np.float32); v = np.pad(v, (0, max(0, L - len(v))))[:L]
VR = 20 * np.log10(rms(v[np.abs(v) > 0.01]))
win = int(0.05 * SR); env = np.sqrt(np.convolve(v ** 2, np.ones(win) / win, "same"))
act = (env > db(VR - 18)).astype(float); k = int(0.35 * SR); act = np.clip(np.convolve(act, np.ones(k) / k, "same") * 3, 0, 1)
sm = int(0.25 * SR); act = np.convolve(act, np.ones(sm) / sm, "same")
music = np.zeros((L, 2), np.float32); amb = np.zeros((L, 2), np.float32)
for f, off, lvl, anc in S.get("music", []):
    t0 = (word_t(anc) - 0.5) if anc else 0.0
    m = load(f, off, LEN - t0 + 0.5); m = m / rms(m[: int(20 * SR)] if len(m) > 20 * SR else m) * db(VR + lvl)
    put(music, fade(m, 2.5 if t0 == 0 else 4.0, 3.5), t0)
music *= (db(-7) + (1 - db(-7)) * (1 - act))[:, None]
for f, lvl, pan, a, b in S.get("beds", []):
    t0 = (word_t(a) - 0.6) if a else 0.0; t1 = (word_t(b) - 0.3) if b else LEN
    if t0 is None or t1 is None or t1 - t0 < 2: continue
    put(amb, fade(loop(f, t1 - t0) / max(1e-6, rms(load(f)[: 30 * SR])) * db(VR + lvl), 2.5, 2.5), t0, pan)
for f, ss, dur, w, lvl, pan in S.get("hits", []):
    t = word_t(w)
    if t is None: continue
    a = fade(load(f, ss, dur), 0.03, min(1.0, dur / 3)); pk = np.max(np.abs(a)) + 1e-9
    put(amb, a / pk * db(VR + 8 + lvl), t - 0.05, pan)
amb *= (db(-3) + (1 - db(-3)) * (1 - act))[:, None]
g = np.ones(L)
for h0, h1 in HOLD: g[int(max(0, h0 + 0.3) * SR):int(h1 * SR)] = 0.08     # the held breath
g = np.convolve(g, np.ones(int(0.6 * SR)) / int(0.6 * SR), "same"); music *= g[:, None]; amb *= g[:, None]
for n, a in (("music.wav", music), ("amb.wav", amb)):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", D + "/" + n], input=np.clip(a, -1, 1).astype(np.float32).tobytes())
print("scene", si, "world ok; voice RMS", round(VR, 1))
