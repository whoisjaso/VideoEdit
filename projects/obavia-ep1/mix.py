"""Sound for Obavia Ep1: VO + D-minor 92 BPM score + SFX, every time read from timeline.json / cues.json.

    python projects/obavia-ep1/mix.py      # -> public/mix.wav (48 kHz, -14 LUFS, peak <= -1 dBFS)
"""
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "projects/lead-with-questions"))
sys.path.insert(0, str(ROOT / "projects/theta-identity"))
import build                                                                     # noqa: E402
from lwq_audio import (butter, lufs, limit, reverb, stereo_ir, pad_chord, felt_piano,  # noqa: E402
                       note, db, add, cos_fade, shelf, peaking)

SR = 48000
LIB = ROOT / ".claude/skills/jason-video-editor/assets/sfx"
tl = json.loads((HERE / "src/data/timeline.json").read_text())
cues = json.loads((HERE / "src/data/cues.json").read_text())
T = tl["duration"]
N = int(T * SR) + SR
S = {s["id"]: s["start"] for s in tl["shots"]}
E = {s["id"]: s["end"] for s in tl["shots"]}
rng = np.random.default_rng(7)


def lib(name):
    x, sr = sf.read(LIB / name, dtype="float32", always_2d=True)
    x = np.stack([build.resample(x[:, c].copy(), sr, SR) for c in range(x.shape[1])], 1)
    if x.shape[1] == 1:
        x = np.repeat(x, 2, 1)
    return x / (np.max(np.abs(x)) + 1e-9)


def env_t(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)


def st(x, w=0.0):
    return np.stack([x * (1 - w), x * (1 + w)], 1).astype(np.float32)


# ---------------------------------------------------------------- synthesized SFX

def siren_chirp():
    out = np.zeros(int(0.9 * SR), np.float32)
    for k, t0 in enumerate((0.0, 0.32)):
        n = int(0.24 * SR)
        t = np.arange(n) / SR
        f = 650 + 900 * (t / 0.24) ** 0.7
        ph = 2 * np.pi * np.cumsum(f) / SR
        s = np.sign(np.sin(ph)) * 0.35 + np.sin(ph) * 0.65
        s = s * np.minimum(1, t / 0.01) * np.minimum(1, (0.24 - t) / 0.03)
        i = int(t0 * SR)
        out[i:i + n] += s.astype(np.float32)
    out = butter(out, 3500)
    return st(out / np.max(np.abs(out)))


def heartbeat(n_beats=2, bpm=64, gap=0.28):
    L = int((60 / bpm * n_beats + 0.6) * SR)
    out = np.zeros(L, np.float32)
    for b in range(n_beats):
        for k, (dt, a) in enumerate(((0, 1.0), (gap, 0.7))):
            t0 = b * 60 / bpm + dt
            n = int(0.25 * SR)
            t = np.arange(n) / SR
            f = 55 + 35 * np.exp(-t / 0.03)
            s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.07) * np.minimum(1, t / 0.004) * a
            i = int(t0 * SR)
            out[i:i + n] += s.astype(np.float32)
    return st(out / np.max(np.abs(out)))


def step():
    n = int(0.22 * SR)
    t = np.arange(n) / SR
    thud = np.sin(2 * np.pi * (70 + 40 * np.exp(-t / 0.02)) * t) * np.exp(-t / 0.05)
    grit = butter(rng.standard_normal(n).astype(np.float32), 2500) * np.exp(-t / 0.03) * 0.5
    grit = butter(grit, 300, "high")
    s = (thud + grit) * np.minimum(1, t / 0.002)
    return st(s / np.max(np.abs(s)))


def motor(d=1.1):
    n = int(d * SR)
    t = np.arange(n) / SR
    f = 120 + 25 * t / d
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.4 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    s += 0.3 * butter(rng.standard_normal(n).astype(np.float32), 1800)
    s *= np.minimum(1, t / 0.05) * np.minimum(1, (d - t) / 0.08) * (1 + 0.15 * np.sin(2 * np.pi * 31 * t))
    s = butter(s.astype(np.float32), 2500)
    return st(s / np.max(np.abs(s)))


def pen(d=0.6):
    n = int(d * SR)
    t = np.arange(n) / SR
    s = rng.standard_normal(n).astype(np.float32)
    s = butter(butter(s, 6000), 1800, "high")
    strokes = 0.55 + 0.45 * np.abs(np.sin(2 * np.pi * 7.5 * t))
    s *= strokes * np.minimum(1, t / 0.02) * np.minimum(1, (d - t) / 0.05)
    return st(s / np.max(np.abs(s)), 0.1)


def relay(hi=False):
    n = int(0.06 * SR)
    t = np.arange(n) / SR
    s = rng.standard_normal(n).astype(np.float32) * np.exp(-t / 0.006)
    s = butter(butter(s, 4500 if not hi else 7000), 900, "high")
    s += (np.sin(2 * np.pi * (1800 if hi else 900) * t) * np.exp(-t / 0.01) * 0.6).astype(np.float32)
    return st(s / np.max(np.abs(s)))


def grip():
    n = int(0.3 * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * (90 + 60 * np.exp(-t / 0.015)) * t) * np.exp(-t / 0.06)
    s += butter(rng.standard_normal(n).astype(np.float32), 1200) * np.exp(-t / 0.02) * 0.4
    return st((s / np.max(np.abs(s))).astype(np.float32))


def pitch_down(x, semis=-7):
    out = np.stack([build.resample(x[:, c].copy(), SR, int(SR * 2 ** (-semis / 12))) for c in range(2)], 1)
    return out / np.max(np.abs(out))


KIT = {
    "swoosh": lib("swoosh.wav"), "whoosh_soft": lib("pack3/woosh.wav"), "pop": lib("pop.wav"), "ding": lib("ding.wav"),
    "thump": lib("deep_bass.wav"), "lowhit": lib("pack4/basscrack.wav"), "click": lib("click.wav"),
    "shutter": lib("camera_shutter.wav"), "switch": lib("ui/switch.wav"), "riser": lib("pack3/riser.wav"),
    "riser_short": lib("riser.wav"), "impact": lib("pack4/cinestrike.wav"),
    "whoosh_down": pitch_down(lib("pack3/cinematic_woosh.wav")),
    "siren": siren_chirp(), "heartbeat2": heartbeat(2), "step": step(), "motor": motor(), "pen": pen(),
    "tick": relay(), "tick_hi": relay(True), "grip": grip(),
}
def paper_slide():
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    s = rng.standard_normal(n).astype(np.float32)
    s = butter(butter(s, 3200), 400, "high") * np.sin(np.pi * t / 0.45) ** 1.5
    return st(s / np.max(np.abs(s)), 0.15)


def marker(d=0.55):
    n = int(d * SR)
    t = np.arange(n) / SR
    s = rng.standard_normal(n).astype(np.float32)
    s = butter(butter(s, 5200), 2600, "high")
    tone = np.sin(2 * np.pi * np.cumsum(1900 + 500 * t / d) / SR) * 0.25
    s = (s + tone) * (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 9 * t))) * np.minimum(1, t / 0.03) * np.minimum(1, (d - t) / 0.06)
    return st((s / np.max(np.abs(s))).astype(np.float32))


def stamp():
    th = lib("deep_bass.wav")[: int(0.6 * SR)]
    n = int(0.08 * SR)
    t = np.arange(n) / SR
    smack = butter(rng.standard_normal(n).astype(np.float32), 2500) * np.exp(-t / 0.012)
    th[:n] += st(smack / np.max(np.abs(smack))) * 0.8
    return th / np.max(np.abs(th))


def siren_wipe():
    w = lib("pack3/cinematic_woosh.wav").copy()
    ch = siren_chirp()[: int(0.6 * SR)] * 0.35
    o = int(np.argmax(np.convolve(np.abs(w).max(1), np.ones(480) / 480, "same"))) - int(0.15 * SR)
    w[o:o + len(ch)] += ch[: len(w) - o]
    return w / np.max(np.abs(w))


for nm in ["ios_tink", "ios_key", "ios_lock", "ios_note", "ios_success", "ios_received", "ios_tritone"]:
    KIT[nm] = lib(f"ios/{nm}.wav")
KIT.update({"paper": paper_slide(), "marker": marker(), "stamp": stamp(), "toggle": lib("ui/switch.wav"),
            "morph": lib("ui/open_ui.wav"), "shine": lib("pack3/shine.wav")})
KIT["tick_soft"] = KIT["ios_key"] * 0.7
KIT["siren_wipe"] = siren_wipe()
KIT["impact_ding"] = KIT["impact"].copy()
KIT["impact_ding"][:len(KIT["ding"])] += KIT["ding"] * 0.6
PEAK_ALIGNED = {"swoosh", "whoosh_soft", "whoosh_down", "siren_wipe"}   # these land their loudest point on the cut


def peak_offset(x):
    e = np.convolve(np.abs(x).max(1), np.ones(480) / 480, "same")
    return np.argmax(e) / SR


# melodic / multi-note sounds land their first note; everything percussive lands its peak (files carry 0-535 ms of pre-roll)
ONSET_ALIGNED = {"ios_success", "ios_received", "ios_tritone", "shine", "siren", "heartbeat2", "pen", "step"}


def hit_offset(name, x):
    if name in PEAK_ALIGNED:
        return peak_offset(x)
    a = np.convolve(np.abs(x).max(1), np.ones(48) / 48, "same")
    if name in ONSET_ALIGNED:
        return np.argmax(a > a.max() * 0.0316) / SR
    head = a[: int(0.8 * SR)]
    return np.argmax(head > head.max() * 0.5) / SR      # perceived attack: where the hit reaches half its peak


# ---------------------------------------------------------------- score (D minor, 92 BPM)

BPM = 92
BEAT = 60 / BPM
CH = [[50, 57, 62, 65, 69], [46, 53, 58, 62, 65], [43, 50, 55, 58, 62], [45, 52, 57, 61, 64]]   # Dm Bb Gm A
ROOTS = [38, 34, 31, 33]
A4 = 440.0


def saw_pad(freqs, dur, seed):
    return pad_chord(freqs, dur, seed, attack=0.6, release=1.8, lp=700, detune=(-9, 0, 9))


def score():
    out = np.zeros((N, 2), np.float32)
    bar = 4 * BEAT
    t, i = 0.0, 0
    cache = {}
    end_music = S["black"]
    while t < end_music:
        c = i % 4
        if c not in cache:
            cache[c] = saw_pad([note(m, A4) for m in CH[c]], bar * 2, c)
        add(out, cache[c], t)
        t += bar * 2
        i += 1
    pad = out
    # sub-bass 8ths
    sub = np.zeros(N, np.float32)
    kick = np.zeros(N, np.float32)
    hats = np.zeros(N, np.float32)
    arp = np.zeros((N, 2), np.float32)
    tension = [(S["hispov"], E["hispov"]), (S["p2"], E["p2"]), (S["clip"], S["black"])]
    build_up = [(S["disarm"], S["approach"]), (S["admit"], S["reg"])]
    k = 0
    while k * BEAT / 2 < end_music:
        tb = k * BEAT / 2
        c = int(tb // (bar * 2)) % 4
        n_ = int(0.18 * SR)
        tt = np.arange(n_) / SR
        r = note(ROOTS[c], A4)
        s = np.sin(2 * np.pi * r * tt) * np.minimum(1, tt / 0.004) * np.exp(-tt / 0.12)
        add(sub, s.astype(np.float32) * (1.0 if k % 2 == 0 else 0.6), tb)
        if any(a <= tb < b for a, b in tension):
            if k % 2 == 0 and (k // 2) % 2 == 0:
                L = int(0.3 * SR)
                t3 = np.arange(L) / SR
                kk = np.sin(2 * np.pi * np.cumsum(45 + 70 * np.exp(-t3 / 0.03)) / SR) * np.exp(-t3 / 0.11)
                add(kick, kk.astype(np.float32), tb)
            if k % 2 == 1:
                L = int(0.05 * SR)
                h = rng.standard_normal(L).astype(np.float32) * np.exp(-np.arange(L) / (0.008 * SR))
                add(hats, h, tb)
        if any(a <= tb < b for a, b in build_up):
            m = CH[c][(k % 4) + 1] + 12
            x = felt_piano(note(m, A4), 1.2, vel=0.7, bright=0.9)
            pl = 0.3 * np.sin(k)
            add(arp, np.stack([x * (1 - pl), x * (1 + pl)], 1), tb)
        k += 1
    hats = butter(hats, 6000, "high")
    arp = arp * 0.7 + reverb(arp, stereo_ir(2.5, 2.2, (5, 6)), 0.5)
    mix = pad * 0.9 + st(sub) * 0.5 + st(kick) * 0.55 + st(hats) * 0.12 + arp * 0.35
    # arc: near-silent under the officer's first line, heartbeat tension clip->split, silence on black
    o1 = next(c for c in tl["clips"] if c["shot"] == "ask")
    g = cos_fade(N, [(0, 0), (0.6, 0.8), (S["approach"], 0.8), (S["approach"] + 1.0, 0.45), (o1["start"] - 0.3, 0.45),
                     (o1["start"], 0.08), (o1["start"] + o1["dur"], 0.08), (o1["start"] + o1["dur"] + 0.8, 0.7),
                     (S["clip"], 0.75), (S["choice"], 1.0), (S["black"] - 0.15, 1.0), (S["black"], 0.0)])
    mix = mix * g[:, None]
    # end sting: Dm add9 stab with a tail
    sting = pad_chord([note(m, A4) for m in [50, 57, 62, 64, 69, 74]], 1.2, 9, attack=0.02, release=3.0, lp=2400)
    add(mix, sting * 2.2, S["end"])
    mix = mix * 0.85 + reverb(mix, stereo_ir(3.0, 2.6, (7, 8), bright=3000), 0.25)
    return mix.astype(np.float32)


def heartbeat_track():
    """Fast heartbeat from the clipboard through the choice (stops on the black frame)."""
    out = np.zeros((N, 2), np.float32)
    t = S["clip"] + 0.2
    bpm = 96
    while t < S["black"] - 0.3:
        add(out, heartbeat(1, bpm, 0.24), t)
        t += 60 / bpm
        bpm = min(132, bpm + 3)
    return out


def stereo_bass():
    """Muffled boom-bap from your car while he reads it (behind glass: low-passed, thumping)."""
    out = np.zeros((N, 2), np.float32)
    a, b = S["hispov"], next(e["t"] for e in cues["events"] if e["name"] == "tagH4") + 0.8
    beat = 60 / 88
    t = a
    k = 0
    while t < b:
        L = int(0.35 * SR)
        tt = np.arange(L) / SR
        if k % 4 in (0, 2) or k % 8 == 7:
            kk = np.sin(2 * np.pi * np.cumsum(50 + 60 * np.exp(-tt / 0.03)) / SR) * np.exp(-tt / 0.15)
            add(out, st(kk.astype(np.float32)), t)
        if k % 4 in (1, 3):
            sn = rng.standard_normal(L).astype(np.float32) * np.exp(-tt / 0.06)
            add(out, st(butter(sn, 900) * 0.8), t)
        t += beat
        k += 1
    out = butter(out, 260)
    env = cos_fade(N, [(0, 0), (a, 0), (a + 0.5, 1), (b - 1.0, 1), (b, 0)])
    return out * env[:, None]


# ---------------------------------------------------------------- mix

def main():
    vo = np.zeros((N, 2), np.float32)
    vo_env = np.zeros(N, np.float32)
    for c in tl["clips"]:
        x, sr = sf.read(HERE / "public" / c["file"], dtype="float32")
        x = butter(x, 80, "high")
        x = peaking(x, 3500, 2.5, 0.8)
        x = x * db(-18 - lufs(x))
        if c["speaker"] == "O":
            x = shelf(x, 6000, -2.0)
        add(vo, st(x), c["start"])
        add(vo_env, np.abs(x), c["start"])
    vo = vo * 0.92 + reverb(vo, stereo_ir(0.8, 0.45, (3, 4), bright=6000), 0.08)

    sfx = np.zeros((N, 2), np.float32)
    for e in cues["events"]:
        if not e["sfx"]:
            continue
        x = KIT[e["sfx"]]
        t = e["t"] - e["lead"] / 30 - hit_offset(e["sfx"], x)   # the audible hit, not the file start, lands on the frame
        x = x * db(-24 - lufs(np.pad(x, ((0, max(0, int(0.45 * SR) - len(x))), (0, 0))))) * db(e["gain"] + 8)
        add(sfx, x, t)
    sfx += heartbeat_track() * db(-26 - lufs(heartbeat(1))) * 1.0
    sfx += stereo_bass() * 0.25

    music = score()
    music = music * db(-26 - lufs(music, 0, S["black"]))
    # side-chain duck ~5 dB under the VO
    env = np.convolve(vo_env, np.ones(int(0.12 * SR)) / int(0.12 * SR), "same")
    env = env / (np.percentile(env[env > 1e-4], 70) + 1e-9)
    duck = db(-5 * np.clip(env, 0, 1))
    duck = np.convolve(duck, np.ones(int(0.25 * SR)) / int(0.25 * SR), "same")
    music *= duck[:, None]

    mix = vo + music + sfx
    sf.write(HERE / "public/sfx_only.wav", np.clip(sfx[: int(T * SR)], -1, 1), SR, subtype="PCM_16")   # for the sync audit
    mix = mix[: int(T * SR)]
    mix *= db(-14 - lufs(mix))
    mix = limit(mix, -2.0)
    mix[-int(0.05 * SR):] *= np.linspace(1, 0, int(0.05 * SR))[:, None]
    sf.write(HERE / "public/mix.wav", mix, SR, subtype="PCM_16")
    sf.write(HERE / "public/mix_vo_only.wav", vo[: int(T * SR)] * db(-14 - lufs(vo[: int(T * SR)])), SR, subtype="PCM_16")
    print("mix", round(lufs(mix), 2), "LUFS, peak", round(20 * np.log10(np.max(np.abs(mix))), 2), "dBFS,", round(T, 2), "s")


if __name__ == "__main__":
    main()
