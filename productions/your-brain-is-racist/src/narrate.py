"""Scratch narration + word timings.

  python3 src/narrate.py audition            -> audio/auditions/*.wav + pitch table
  python3 src/narrate.py build --voice NAME  -> audio/narration.wav + timeline.json
  python3 src/narrate.py align --wav JASON.wav -> timeline.json from Jason's own read

Engine: Kokoro v1.0 (Apache-2.0, runs offline) because the Higgsfield workspace had
no credits. The film is driven only by timeline.json, so a new read re-times everything.
"""
import sys, os, json, argparse, difflib, re
import numpy as np, soundfile as sf
from scipy.signal import resample_poly, butter, sosfilt
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from script import LINES
MODELS = os.environ.get("KOKORO_DIR", "/tmp/claude-0/-home-user-VideoEdit/dea1a155-7f9b-5d5a-9ed6-2efb365ee1a7/scratchpad/models")
SR = 48000
LEAD = 0.0   # narration-local time; the film adds its own offsets

def kokoro():
    from kokoro_onnx import Kokoro
    return Kokoro(f"{MODELS}/kokoro-v1.0.onnx", f"{MODELS}/voices-v1.0.bin")

def say(k, text, voice, speed):
    a, sr = k.create(text, voice=voice, speed=speed, lang="en-us")
    a = resample_poly(a.astype(np.float64), SR, sr)
    # trim engine silence to a consistent 20 ms head / 60 ms tail
    env = np.abs(a); thr = max(1e-3, env.max() * 0.02)
    idx = np.where(env > thr)[0]
    if len(idx):
        a = a[max(0, idx[0] - int(0.02 * SR)): min(len(a), idx[-1] + int(0.06 * SR))]
    f = int(0.012 * SR); a[:f] *= np.linspace(0, 1, f); a[-f:] *= np.linspace(1, 0, f)
    return a

def f0_stats(a):
    """Median pitch + spread by autocorrelation on 40 ms frames."""
    n = int(0.04 * SR); out = []
    for i in range(0, len(a) - n, n // 2):
        fr = a[i:i + n] * np.hanning(n)
        if np.sqrt(np.mean(fr ** 2)) < 0.02: continue
        ac = np.correlate(fr, fr, "full")[n - 1:]
        lo, hi = SR // 300, SR // 60
        p = lo + np.argmax(ac[lo:hi])
        if ac[p] > 0.45 * ac[0]: out.append(SR / p)
    out = np.array(out)
    return float(np.median(out)), float(np.percentile(out, 90) - np.percentile(out, 10))

def norm(w): return re.sub(r"[^a-z0-9']", "", w.lower())

def whisper_words(model, a):
    a16 = resample_poly(a, 16000, SR).astype(np.float32)
    segs, _ = model.transcribe(a16, language="en", word_timestamps=True, beam_size=5,
                               condition_on_previous_text=False, vad_filter=False)
    return [(norm(w.word), w.start, w.end) for s in segs for w in s.words if norm(w.word)]

def align_line(text, ww, dur):
    """Map script words to recognised word times; interpolate anything unmatched."""
    sw = text.split(); keys = [norm(w) for w in sw]
    t0 = [None] * len(sw); t1 = [None] * len(sw)
    sm = difflib.SequenceMatcher(a=keys, b=[w[0] for w in ww], autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1): t0[i1 + k], t1[i1 + k] = ww[j1 + k][1], ww[j1 + k][2]
        elif tag == "replace" and (i2 - i1) == (j2 - j1):
            for k in range(i2 - i1): t0[i1 + k], t1[i1 + k] = ww[j1 + k][1], ww[j1 + k][2]
    # fill gaps by character-weighted interpolation between known neighbours
    i = 0
    while i < len(sw):
        if t0[i] is not None: i += 1; continue
        j = i
        while j < len(sw) and t0[j] is None: j += 1
        a = t1[i - 1] if i > 0 else 0.02
        b = t0[j] if j < len(sw) else dur - 0.06
        wts = np.array([len(k) + 1 for k in keys[i:j]], float); cs = np.concatenate([[0], np.cumsum(wts)]) / wts.sum()
        for k in range(i, j): t0[k] = a + (b - a) * cs[k - i]; t1[k] = a + (b - a) * cs[k - i + 1]
        i = j
    for k in range(len(sw)):   # monotonic, inside the clip
        t0[k] = float(min(max(t0[k], 0.0), dur)); t1[k] = float(min(max(t1[k], t0[k] + 0.04), dur))
        if k and t0[k] < t0[k - 1]: t0[k] = t0[k - 1] + 0.02
    matched = sum(1 for tag, i1, i2, *_ in sm.get_opcodes() if tag == "equal" for _ in range(i2 - i1))
    return [{"w": sw[k], "s": round(t0[k], 3), "e": round(t1[k], 3)} for k in range(len(sw))], matched

def voice_chain(a):
    sos = butter(2, 70, "hp", fs=SR, output="sos"); a = sosfilt(sos, a)
    # gentle 2.5:1 compression above -20 dBFS, 5/120 ms
    env = np.zeros_like(a); e = 0.0; at = np.exp(-1 / (0.005 * SR)); rl = np.exp(-1 / (0.12 * SR))
    ab = np.abs(a)
    for i in range(len(a)):
        e = at * e + (1 - at) * ab[i] if ab[i] > e else rl * e + (1 - rl) * ab[i]; env[i] = e
    thr = 10 ** (-20 / 20); g = np.where(env > thr, (env / thr) ** (1 / 2.5 - 1), 1.0)
    a = a * g
    return a / max(1e-9, np.abs(a).max()) * 10 ** (-3 / 20)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("--voice", default="am_michael")
    ap.add_argument("--speed", type=float, default=0.96); ap.add_argument("--wav"); ap.add_argument("--out")
    A = ap.parse_args(); os.makedirs(f"{ROOT}/audio/auditions", exist_ok=True)
    if A.cmd == "audition":
        k = kokoro(); ids = ["hook1", "hook2", "hook3", "job1"] + [f"ts{i}" for i in range(1, 8)]
        rows = []
        for v in ["am_michael", "am_fenrir", "am_onyx"]:
            parts = []
            for lid, text, gap in LINES:
                if lid in ids: parts += [say(k, text, v, A.speed), np.zeros(int(gap * SR))]
            a = np.concatenate(parts); sf.write(f"{ROOT}/audio/auditions/{v}.wav", (a * 0.8).astype(np.float32), SR)
            med, spread = f0_stats(a); words = sum(len(t.split()) for i, t, _ in LINES if i in ids)
            voiced = sum(len(p) for p in parts[::2]) / SR
            rows.append({"voice": v, "median_f0_hz": round(med, 1), "f0_spread_p10_p90_hz": round(spread, 1), "wpm_speaking": round(words / voiced * 60, 1)})
            print(rows[-1])
        json.dump(rows, open(f"{ROOT}/audio/auditions/audition.json", "w"), indent=1)
        return
    from faster_whisper import WhisperModel
    wm = WhisperModel("small.en", device="cpu", compute_type="int8", cpu_threads=4)
    tl = {"voice": A.voice, "speed": A.speed, "sr": SR, "lines": []}
    if A.cmd == "build":
        k = kokoro(); parts = []; t = LEAD; tot = mat = 0
        for lid, text, gap in LINES:
            a = say(k, text, A.voice, A.speed); dur = len(a) / SR
            words, m = align_line(text, whisper_words(wm, a), dur); tot += len(words); mat += m
            for w in words: w["s"] = round(w["s"] + t, 3); w["e"] = round(w["e"] + t, 3)
            tl["lines"].append({"id": lid, "text": text, "s": round(t, 3), "e": round(t + dur, 3), "gap": gap, "words": words})
            parts += [a, np.zeros(int(round(gap * SR)))]; t += dur + int(round(gap * SR)) / SR
        a = voice_chain(np.concatenate(parts))
        sf.write(f"{ROOT}/audio/narration_dry.wav", a.astype(np.float32), SR)
        tl["duration"] = round(len(a) / SR, 3); tl["word_match"] = round(mat / tot, 4)
        print("duration", tl["duration"], "word match", tl["word_match"])
    if A.cmd == "align":
        # One continuous read (Jason's). Recognise every word, then map the script onto it line by line.
        a, sr = sf.read(A.wav)
        if a.ndim > 1: a = a.mean(1)
        if sr != SR: a = resample_poly(a, SR, sr)
        ww = whisper_words(wm, a); dur = len(a) / SR
        full = " ".join(t for _, t, _ in LINES)
        words, m = align_line(full, ww, dur); k = 0
        for lid, text, gap in LINES:
            n = len(text.split()); seg = words[k:k + n]; k += n
            tl["lines"].append({"id": lid, "text": text, "s": seg[0]["s"], "e": seg[-1]["e"], "gap": gap, "words": seg})
        tl["voice"] = os.path.basename(A.wav); tl["duration"] = round(dur, 3); tl["word_match"] = round(m / len(words), 4)
        if os.path.abspath(A.wav) != os.path.abspath(f"{ROOT}/audio/narration_dry.wav"):
            sf.write(f"{ROOT}/audio/narration_dry.wav", voice_chain(a).astype(np.float32), SR)
        print("duration", tl["duration"], "word match", tl["word_match"])
        out = A.out or f"{ROOT}/timeline.json"
        json.dump(tl, open(out, "w"), indent=0); return
    json.dump(tl, open(f"{ROOT}/timeline.json", "w"), indent=0)

if __name__ == "__main__": main()
