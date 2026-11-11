"""Scratch narration + word timings.

  python3 src/narrate.py audition            -> audio/auditions/*.wav + pitch table
  python3 src/narrate.py build --voice NAME  -> audio/narration.wav + timeline.json
  python3 src/narrate.py align --wav JASON.wav -> timeline.json from Jason's own read

Engine: Kokoro v1.0 (Apache-2.0, runs offline) because the Higgsfield workspace had
no credits. The film is driven only by timeline.json, so a new read re-times everything.
"""
import sys, os, json, argparse, difflib, re, math
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

# ------------------------------------------------------------------ ElevenLabs v4: a narrator and a cast
EL_VOICES = {"narrator": ("Brian", "nPczCjzI2devNBz1zQrb"), "officer": ("Adam", "pNInz6obpgDQGcFmaJgB"), "driver": ("Will", "bIHbv24MWmeRgasZH58o"),
             "kid": ("Liam", "TX3LPaxmHKxFdv7VOQHJ"), "dispatch": ("Sarah", "EXAVITQu4vr4xnSDxMaL")}
CAST = {**{i: "officer" for i in ("ts4", "ts5", "ts6", "ts17")}, **{i: "driver" for i in ("ts9", "ts10", "ts11", "ts12", "ts19")}, "od17": "kid"}
EL_CACHE = f"{ROOT}/audio/el_cache"

def el_say(text, role, speed=1.0, prev=None, nxt=None, seed=7, model="eleven_v4"):
    """One ElevenLabs request with character timestamps. Cached on disk by content, so a rebuild never spends quota twice.
    The API key is injected by the session's network proxy; it is never in this code or in the repo."""
    import hashlib, subprocess, base64, tempfile
    os.makedirs(EL_CACHE, exist_ok=True); vid = EL_VOICES[role][1]
    key = hashlib.md5(f"{model}|{vid}|{speed}|{seed}|{text}".encode()).hexdigest()[:14]; fn = f"{EL_CACHE}/{key}.json"
    if not os.path.exists(fn):
        body = {"text": text, "model_id": model, "seed": seed, "voice_settings": {"stability": 0.5, "speed": speed}}
        if prev: body["previous_text"] = prev[-300:]
        if nxt: body["next_text"] = nxt[:300]
        for attempt in range(3):
            with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tf: json.dump(body, tf); bf = tf.name
            r = subprocess.run(["curl", "-sS", "--max-time", "180", "-X", "POST", f"https://api.elevenlabs.io/v1/text-to-speech/{vid}/with-timestamps?output_format=mp3_44100_128",
                                "-H", "Content-Type: application/json", "-d", f"@{bf}"], capture_output=True, text=True); os.unlink(bf)
            try: d = json.loads(r.stdout)
            except Exception: d = {"detail": r.stdout[:200] or r.stderr[:200]}
            if "audio_base64" in d: break
            msg = json.dumps(d.get("detail", d))[:240]; print("  ElevenLabs:", msg, flush=True)
            if "previous_text" in msg or "next_text" in msg: body.pop("previous_text", None); body.pop("next_text", None); continue
            if "speed" in msg or "voice_settings" in msg: body.pop("voice_settings", None); continue
            raise SystemExit("ElevenLabs refused the request: " + msg)
        json.dump({"text": text, "role": role, "voice": EL_VOICES[role][0], "audio_base64": d["audio_base64"], "alignment": d.get("alignment") or d.get("normalized_alignment")}, open(fn, "w"))
    d = json.load(open(fn)); import base64 as b64, subprocess as sp
    raw = sp.run(["ffmpeg", "-v", "error", "-i", "pipe:0", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], input=b64.b64decode(d["audio_base64"]), capture_output=True).stdout
    a = np.frombuffer(raw, np.float32).astype(np.float64); al = d["alignment"]; words = []; cur = ""; s0 = e0 = 0.0
    for ch, cs, ce in zip(al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]):
        if ch.isspace():
            if cur: words.append((cur, s0, e0)); cur = ""
        else:
            if not cur: s0 = cs
            cur += ch; e0 = ce
    if cur: words.append((cur, s0, e0))
    return a, words

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("--voice", default="am_michael")
    ap.add_argument("--speed", type=float, default=0.96); ap.add_argument("--wav"); ap.add_argument("--out")
    ap.add_argument("--ref", default=f"{ROOT}/audio/auditions/am_michael.wav"); ap.add_argument("--exag", type=float, default=0.7); ap.add_argument("--cfg", type=float, default=0.25); ap.add_argument("--elspeed", type=float, default=0.95)
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
    from scipy.signal import butter, sosfilt
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
    if A.cmd == "build_cb":
        # Expressive read: Chatterbox (Resemble AI, MIT), run offline on CPU. Lines are read in paragraph groups so the
        # voice carries a thought across sentences; each group is checked word-for-word and re-taken if it drifts.
        import torch, hashlib
        torch.set_num_threads(4)
        from chatterbox.tts import ChatterboxTTS
        cb = ChatterboxTTS.from_pretrained(device="cpu")
        cache = os.environ.get("CB_CACHE", "/tmp/claude-0/-home-user-VideoEdit/dea1a155-7f9b-5d5a-9ed6-2efb365ee1a7/scratchpad/cb_groups"); os.makedirs(cache, exist_ok=True)
        groups = [[]]; wc = 0
        for L in LINES:
            groups[-1].append(L); wc += len(L[1].split())
            if L[2] >= 0.6 or wc >= 42: groups.append([]); wc = 0
        groups = [g for g in groups if g]
        parts = []; t = 0.0; tot = mat = 0; log = []
        for gi, g in enumerate(groups):
            text = " ".join(x[1] for x in g); nw = len(text.split())
            key = hashlib.md5(f"{text}|{A.ref}|{A.exag}|{A.cfg}".encode()).hexdigest()[:10]; fn = f"{cache}/{gi:03d}_{key}.npy"
            if os.path.exists(fn): a = np.load(fn)
            else:
                best = None
                for seed in (11, 23, 37, 53):
                    torch.manual_seed(seed)
                    w = cb.generate(text, audio_prompt_path=A.ref, exaggeration=A.exag, cfg_weight=A.cfg, temperature=0.8).squeeze().numpy()
                    w = resample_poly(w.astype(np.float64), SR, cb.sr)
                    idx = np.where(np.abs(w) > max(1e-3, np.abs(w).max() * 0.02))[0]
                    w = w[max(0, idx[0] - int(0.02 * SR)): min(len(w), idx[-1] + int(0.08 * SR))]
                    _, m_ = align_line(text, whisper_words(wm, w), len(w) / SR); score = m_ / nw; wpm = nw / (len(w) / SR) * 60
                    ok = score >= 0.93 and 105 <= wpm <= 235
                    if best is None or score > best[0]: best = (score, w, seed, wpm)
                    if ok: break
                a = best[1]; np.save(fn, a); log.append((gi, best[2], round(best[0], 2), round(best[3])))
                print("group", gi, "/", len(groups), "seed", best[2], "match", round(best[0], 2), "wpm", round(best[3]), flush=True)
            f = int(0.012 * SR); a = a.copy(); a[:f] *= np.linspace(0, 1, f); a[-f:] *= np.linspace(1, 0, f)
            a = a / (np.sqrt(np.mean(a[np.abs(a) > 0.01] ** 2)) + 1e-9) * 0.09            # same loudness for every group
            dur = len(a) / SR; words, m_ = align_line(text, whisper_words(wm, a), dur); tot += len(words); mat += m_; k = 0
            for lid, ltext, gap in g:
                n = len(ltext.split()); seg = words[k:k + n]; k += n
                for w_ in seg: w_["s"] = round(w_["s"] + t, 3); w_["e"] = round(w_["e"] + t, 3)
                tl["lines"].append({"id": lid, "text": ltext, "s": seg[0]["s"], "e": seg[-1]["e"], "gap": gap, "words": seg})
            gap = g[-1][2]; parts += [a, np.zeros(int(round(gap * SR)))]; t += dur + int(round(gap * SR)) / SR
        a = voice_chain(np.concatenate(parts))
        sf.write(f"{ROOT}/audio/narration_dry.wav", a.astype(np.float32), SR)
        tl["voice"] = f"chatterbox ref={os.path.basename(A.ref)} exag={A.exag} cfg={A.cfg}"; tl["duration"] = round(len(a) / SR, 3); tl["word_match"] = round(mat / tot, 4)
        print("duration", tl["duration"], "word match", tl["word_match"], "groups", len(groups))
        json.dump(tl, open(f"{ROOT}/timeline.json", "w"), indent=0); return
    if A.cmd == "build_el":
        # ElevenLabs v4. Paragraph groups for the narrator; the people inside the film speak in their own voices.
        from scipy.signal import fftconvolve
        groups = [[]]; wc = 0
        for L in LINES:
            groups[-1].append(L); wc += len(L[1].split())
            if L[2] >= 0.6 or wc >= 42: groups.append([]); wc = 0
        runs = []                                             # a run = consecutive lines in one voice inside one group
        for g in [g for g in groups if g]:
            cur = []
            for L in g:
                role = CAST.get(L[0], "narrator")
                if cur and cur[0][0] != role: runs.append(cur); cur = []
                cur.append((role, L))
            runs.append(cur)
        texts = [" ".join(L[1] for _, L in r) for r in runs]; print("requests", len(runs), "characters", sum(len(x) for x in texts), flush=True)
        nar_parts, chr_parts = [], []; t = 0.0; used = 0; bad = 0
        PAN = {"officer": -0.55, "driver": 0.55, "kid": 0.0}
        def inner(x):                                         # a voice inside a head: closer, narrower, a little room behind it
            x = sosfilt(butter(2, [170, 5200], "bp", fs=SR, output="sos"), x); n_ = int(0.5 * SR); ir = np.random.default_rng(3).standard_normal(n_) * np.exp(-np.arange(n_) / (0.07 * SR)); ir[:int(0.012 * SR)] = 0
            w = fftconvolve(x, ir / np.sqrt(np.sum(ir ** 2)))[:len(x)]; return x * 0.9 + w * 0.22
        for ri, (r, text) in enumerate(zip(runs, texts)):
            role = r[0][0]; sp = A.elspeed if role == "narrator" else 1.0
            a, words = el_say(text, role, sp, prev=texts[ri - 1] if ri else None, nxt=texts[ri + 1] if ri + 1 < len(texts) else None); used += len(text)
            nw = len(text.split())
            if len(words) != nw:                               # timestamps did not line up word for word: fall back to the recognizer
                words_, _ = align_line(text, whisper_words(wm, a), len(a) / SR); words = [(w["w"], w["s"], w["e"]) for w in words_]; bad += 1
            idx = np.where(np.abs(a) > max(1e-3, np.abs(a).max() * 0.02))[0]; i0 = max(0, idx[0] - int(0.02 * SR)); i1 = min(len(a), idx[-1] + int(0.08 * SR)); a = a[i0:i1].copy(); off = i0 / SR
            f = int(0.012 * SR); a[:f] *= np.linspace(0, 1, f); a[-f:] *= np.linspace(1, 0, f)
            a = a / (np.sqrt(np.mean(a[np.abs(a) > 0.01] ** 2)) + 1e-9) * 0.09; dur = len(a) / SR; k = 0
            for _, (lid, ltext, gap) in r:
                n = len(ltext.split()); seg = words[k:k + n]; k += n
                ws = [{"w": w_, "s": round(max(0.0, s_ - off) + t, 3), "e": round(min(dur, e_ - off) + t, 3)} for (w_, s_, e_), w_ in zip(seg, ltext.split())]
                tl["lines"].append({"id": lid, "text": ltext, "voice": EL_VOICES[role][0], "s": ws[0]["s"], "e": ws[-1]["e"], "gap": gap, "words": ws})
            gap = r[-1][1][2]; z = np.zeros(int(round(gap * SR))); st = np.zeros((len(a) + len(z), 2))
            if role == "narrator": nar_parts += [a, z]; chr_parts.append(st)
            else:
                x = inner(a) * 0.95; p_ = PAN[role]; st[:len(a), 0] = x * math.cos((p_ + 1) * math.pi / 4) * 1.414; st[:len(a), 1] = x * math.sin((p_ + 1) * math.pi / 4) * 1.414
                nar_parts += [np.zeros(len(a)), z]; chr_parts.append(st)
            t += dur + len(z) / SR
            if ri % 10 == 0: print("  run", ri, "/", len(runs), role, round(nw / dur * 60), "wpm", flush=True)
        nar = np.concatenate(nar_parts); ch = np.concatenate(chr_parts); g_ = 10 ** (-3 / 20) / max(1e-9, np.abs(nar).max())
        nar_c = voice_chain(nar); k_ = np.abs(nar_c).max() / max(1e-9, np.abs(nar).max())
        sf.write(f"{ROOT}/audio/narration_dry.wav", nar_c.astype(np.float32), SR); sf.write(f"{ROOT}/audio/characters_dry.wav", (ch * k_ * 0.9).astype(np.float32), SR)
        act = np.abs(nar) > 0.01; spoken = sum(len(l["words"]) for l in tl["lines"] if l["voice"] == "Brian")
        tl["voice"] = "ElevenLabs eleven_v4: " + ", ".join(f"{k}={v[0]}" for k, v in EL_VOICES.items()); tl["duration"] = round(len(nar) / SR, 3); tl["characters"] = used; tl["fallback_runs"] = bad
        print("duration", tl["duration"], "characters sent", used, "runs needing the recognizer", bad)
        json.dump(tl, open(f"{ROOT}/timeline.json", "w"), indent=0); return
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
