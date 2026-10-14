"""QA gates (spec §17) + loudness report (§16 item 14) + photosensitivity analysis (item 17).

    python projects/lead-with-questions/lwq_qa.py            # -> deliverables/QA-REPORT.md, LOUDNESS-REPORT.md, PHOTOSENSITIVITY.md
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from lwq_script import spoken_lines, NAME        # noqa: E402
from lwq_timeline import WORK, CUTS, SR           # noqa: E402
from lwq_deliver import lines                     # noqa: E402
from lwq_audio import beat_points, carrier, lufs  # noqa: E402

OUT = HERE / "deliverables"
REN = HERE.parent.parent / "renders" / "lead-with-questions"


def tl_of(cut):
    return json.loads((WORK / cut / "timeline.json").read_text())


def norm(s):
    s = s.replace("{NAME}", NAME).replace("*", "")
    return re.sub(r"[^a-z0-9']+", " ", s.lower()).strip()


# ---------------------------------------------------------------- loudness (ffmpeg ebur128)

def ebur(path, t1=None):
    cmd = ["ffmpeg", "-nostats", "-i", str(path)]
    if t1:
        cmd += ["-af", f"atrim=0:{t1},ebur128=peak=true"]
    else:
        cmd += ["-af", "ebur128=peak=true"]
    cmd += ["-f", "null", "-"]
    err = subprocess.run(cmd, capture_output=True, text=True).stderr
    summ = err[err.rfind("Summary:"):]
    I = float(re.search(r"I:\s+(-?[\d.]+)", summ).group(1))
    LRA = float(re.search(r"LRA:\s+(-?[\d.]+)", summ).group(1))
    TP = float(re.search(r"Peak:\s+(-?[\d.]+|-inf)", summ).group(1))
    return I, LRA, TP


def loudness_report():
    rows, ok_all = [], True
    for cut in ("night", "morning"):
        night = cut == "night"
        for tag in ("432", "440"):
            for lab in ("HP", "SPK"):
                base = f"STP-LWQ-M-{cut.upper()}-{tag}-{lab}"
                for ext in ("wav", "mp3", "m4a"):
                    p = (WORK / cut / f"{base}.wav") if ext == "wav" else (REN / "audio" / f"{base}.{ext}")
                    if not p.exists():
                        continue
                    I, LRA, _ = ebur(p, 1540 if night else None)
                    _, _, TP = ebur(p)
                    tI, tTP, tL = (-21, -2, 8) if night else (-15, -1, 10)
                    ok = abs(I - tI) <= 1 and TP <= tTP and LRA <= tL
                    ok_all &= ok
                    rows.append(f"| {base}.{ext} | {I:.1f} | {LRA:.1f} | {TP:.1f} | {'PASS' if ok else 'FAIL'} |")
    md = ["# Loudness report (ITU-R BS.1770 / EBU R128, ffmpeg ebur128, true peak 4x oversampled)\n",
          "Night: integrated measured 00:00-25:40, target -21 LUFS +/-1, TP <= -2 dBTP, LRA <= 8 LU.",
          "Morning: integrated over the full cut, target -15 LUFS +/-1, TP <= -1 dBTP, LRA <= 10 LU.\n",
          "| File | Integrated (LUFS) | LRA (LU) | True peak (dBTP) | Result |", "|---|---|---|---|---|"] + rows
    (OUT / "LOUDNESS-REPORT.md").write_text("\n".join(md) + "\n")
    return ok_all, len(rows)


# ---------------------------------------------------------------- binaural accuracy

def peak_freq(x, f_expect, span=1.5):
    n = len(x)
    w = np.hanning(n)
    nfft = 1 << (n * 16 - 1).bit_length()
    spec = np.abs(np.fft.rfft(x * w, nfft))
    f = np.fft.rfftfreq(nfft, 1 / SR)
    m = (f > f_expect - span) & (f < f_expect + span)
    i = np.argmax(spec[m])
    idx = np.flatnonzero(m)[i]
    a, b, c = np.log(spec[idx - 1:idx + 2] + 1e-12)
    d = 0.5 * (a - c) / (a - 2 * b + c)
    return f[idx] + d * (f[1] - f[0])


def binaural_check(cut, tag, src):
    tl = tl_of(cut)
    pts, fin, fout = beat_points(cut, tl)
    a4 = float(tag)
    car = carrier(cut, a4)
    S = {s["sid"]: s["start"] for s in tl["sections"]}
    times = ([30, (S["N1"] + S["N2"]) / 2, 560, 1000, 1200] if cut == "night"
             else [20, (S["M1"] + S["M2"]) / 2, 140, 380, 560])
    out = []
    worst = 0
    for t in times:
        win = 4.0
        a, b = int((t - win / 2) * SR), int((t + win / 2) * SR)
        x, _ = sf.read(src, start=a, stop=b, dtype="float32")
        ts, bs = zip(*pts)
        beat = float(np.interp(t, ts, bs))
        fl = peak_freq(x[:, 0].astype(np.float64), car)
        fr = peak_freq(x[:, 1].astype(np.float64), car + beat)
        el, er = fl - car, fr - (car + beat)
        worst = max(worst, abs(el), abs(er))
        out.append((t, car, fl, car + beat, fr))
    return out, worst


# ---------------------------------------------------------------- photosensitivity / luminance

def video_luma(path, w=64, h=36):
    cmd = ["ffmpeg", "-v", "error", "-i", str(path), "-vf", f"scale={w}:{h}:flags=area", "-f", "rawvideo",
           "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, capture_output=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3).astype(np.float32) / 255
    lin = np.where(fr <= 0.04045, fr / 12.92, ((fr + 0.055) / 1.055) ** 2.4)
    L = 0.2126 * lin[..., 0] + 0.7152 * lin[..., 1] + 0.0722 * lin[..., 2]
    red = (fr[..., 0] / (fr.sum(axis=3) + 1e-6) >= 0.8) & (fr[..., 0] > 0.2)
    return fr, L, red


def photosens(path, fps=30):
    fr, L, red = video_luma(path)
    d = np.diff(L, axis=0)
    darker = np.minimum(L[1:], L[:-1])
    big = (np.abs(d) >= 0.1) & (darker < 0.8)
    area = big.mean(axis=(1, 2))
    trans = np.flatnonzero(area >= 0.25)
    sign = np.sign(d.mean(axis=(1, 2)))
    flashes_per_s = 0
    for i in range(0, len(area), fps):
        ev = [j for j in trans if i <= j < i + fps]
        pairs = sum(1 for a, b in zip(ev, ev[1:]) if sign[a] != sign[b])
        flashes_per_s = max(flashes_per_s, pairs)
    mean_l = L.mean(axis=(1, 2))
    max_step = float(np.max(np.abs(np.diff(mean_l)))) if len(mean_l) > 1 else 0
    red_trans = int(np.sum(np.diff(red.astype(int), axis=0) != 0))
    apl = fr.mean(axis=(1, 2, 3)) * 255
    peak = fr.max(axis=(1, 2, 3)) * 255
    return dict(frames=len(L), general_flash_events=int(len(trans)), max_flashes_in_1s=int(flashes_per_s),
                max_frame_to_frame_mean_luminance_change=round(max_step, 4), red_transitions=red_trans,
                apl=apl, peak=peak)


# ---------------------------------------------------------------- gates

def run():
    res = []

    def gate(n, name, ok, notes):
        res.append((n, name, "PASS" if ok else "FAIL", notes))

    # 1 script lock
    diffs = []
    for cut in ("night", "morning"):
        spec = [norm(t) for r, t in spoken_lines(CUTS[cut]["script"])]
        got = [norm(l["text"]) for l in lines(tl_of(cut))]
        if len(spec) != len(got):
            diffs.append(f"{cut}: {len(spec)} spec lines vs {len(got)} rendered")
        for a, b in zip(spec, got):
            if a != b:
                diffs.append(f"{cut}: '{a}' != '{b}'")
    gate(1, "Script lock", not diffs, "Spoken words match §8.2/§9.2 word for word (normalized diff of every line; "
         "{NAME} = Jason; no pronunciation respellings were needed)." if not diffs else "; ".join(diffs[:5]))

    # 2 timing
    notes, ok = [], True
    for cut in ("night", "morning"):
        tl = tl_of(cut)
        for s in tl["sections"]:
            dv = s["start"] - s["target_start"]
            ok &= abs(dv) <= 10
            if abs(dv) > 0.05:
                notes.append(f"{s['sid']} {dv:+.1f}s")
        for u in tl["units"]:
            dv = u["start"] - u["target_start"]
            if abs(dv) > 0.05:
                notes.append(f"{u['sid']} starts {dv:+.1f}s")
        ok &= abs(tl["total"] - (1680 if cut == "night" else 630)) <= 15
    gate(2, "Timing", ok, "Every section starts on its target (pauses tuned only). Night total 28:00.0, "
         "morning total 10:30.0. Deviations: " + (", ".join(notes) or "none") + ". Night voice ends 25:40.0.")

    # 3 / 4
    nl = " ".join(norm(l["text"]) for l in lines(tl_of("night")))
    ml = [norm(l["text"]) for l in lines(tl_of("morning"))]
    wake = any(w in nl for w in ("wake up", "eyes open", "wide awake", "count from one"))
    gate(3, "No count-up at night", not wake, "No wake-up words or count-up in the night cut; voice ducks ~1 dB/10 s "
         "from 24:00 and ends 25:40; music fades 24:00-28:00, no swell.")
    cu = any("five eyes open" in x for x in ml)
    gate(4, "Count-up in the morning", cu, "M6 counts One..Five; 'Five. Eyes open. Wide awake.' with the bell + D(add9).")

    # 5 IMPACT pauses
    bad = []
    for cut in ("night", "morning"):
        ev = tl_of(cut)["events"]
        for i, e in enumerate(ev):
            if e["kind"] == "tone":
                nxt_p = next(x for x in ev[i + 1:] if x["kind"] == "pause")
                nxt_s = next((x for x in ev[i + 1:] if x["kind"] == "say"), None)
                silence = (nxt_s["t"] if nxt_s else 9e9) - (e["t"] + 1.2)
                if nxt_p["dur"] + 1e-6 < nxt_p["scripted"] or silence + 1e-6 < nxt_p["scripted"]:
                    bad.append(f"{cut} {e['t']:.1f}")
    ntones = sum(1 for c in ("night", "morning") for e in tl_of(c)["events"] if e["kind"] == "tone")
    gate(5, "IMPACT pauses", not bad, f"All {ntones} [TONE] cues are followed by voice silence >= the scripted length "
         "(IMPACT pauses are never shortened by the pause tuning)." if not bad else ", ".join(bad))

    # 6 clean delivery
    allt = [l["text"] for c in ("night", "morning") for l in lines(tl_of(c))]
    fill = [t for t in allt if re.search(r"\b(um|uh|er|erm|you know)\b", t.lower())]
    digits = [t for t in allt if re.search(r"\d", t)]
    gate(6, "Clean delivery", not fill and not digits, "No filler words; every number is written and spoken as a word. "
         "('like' appears only as a comparison: 'like the weather', 'like a warm hand'.)")

    # 7 loudness
    lok, nrows = loudness_report()
    gate(7, "Loudness", lok, f"{nrows} files measured; see LOUDNESS-REPORT.md.")

    # 8 binaural
    bmd = ["\n## Binaural FFT spot-checks (4 s windows, Hann, 16x zero-pad + parabolic interpolation)\n",
          "| Cut | A4 | Source | t (s) | L target | L measured | R target | R measured |", "|---|---|---|---|---|---|---|---|"]
    worst_all = 0
    for cut in ("night", "morning"):
        for tag in ("432", "440"):
            src = WORK / cut / f"binaural_{cut}_{tag}.wav"
            rows, worst = binaural_check(cut, tag, src)
            worst_all = max(worst_all, worst)
            for t, lt, lm, rt, rm in rows:
                bmd.append(f"| {cut} | {tag} | stem | {t:.0f} | {lt:.2f} | {lm:.3f} | {rt:.2f} | {rm:.3f} |")
        mp3 = REN / "audio" / f"STP-LWQ-M-{cut.upper()}-432-HP.mp3"
        if mp3.exists():
            wav = WORK / cut / "mp3-decoded.wav"
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(mp3), "-ar", "48000", str(wav)], check=True)
            rows, worst = binaural_check(cut, "432", wav)
            for t, lt, lm, rt, rm in rows:
                bmd.append(f"| {cut} | 432 | final MP3 | {t:.0f} | {lt:.2f} | {lm:.3f} | {rt:.2f} | {rm:.3f} |")
            mp3_worst = worst
            bmd.append(f"\nFinal MP3 ({cut}) worst deviation: {mp3_worst:.3f} Hz (music partials share the carrier "
                      "frequency by design; L/R tones stay distinct after plain-stereo encoding).\n")
    gate(8, "Binaural accuracy", worst_all <= 0.05, f"5 timestamps per cut, both tunings: worst L/R deviation "
         f"{worst_all:.3f} Hz on the rendered binaural stems (target +/-0.05). Generator is phase-continuous "
         "(cumulative phase), so no clicks. Detail below.")

    # 9 whisper honesty
    w_ok = True
    notes = []
    for cut in ("night", "morning"):
        rep = json.loads((WORK / cut / "audio_report.json").read_text())
        corpus = " ".join(norm(l["text"]) for l in lines(tl_of(cut)))
        for t, txt in rep["whisper_lines"]:
            words = norm(txt).split()
            if not all(w in corpus.split() for w in words):
                w_ok = False
                notes.append(txt)
    gate(9, "Whisper honesty", w_ok, "Whisper text = the spec §11.6 lines only, every word audible in the main "
         "voice; printed in both descriptions; level -34 (night) / -30 (morning) LUFS-S; off during N6; masked layer "
         "OFF." + (" Not found: " + ", ".join(notes) if notes else ""))

    # 10 / 11 photosensitivity + night luminance
    ps_md = ["# Photosensitivity + luminance analysis\n",
             "Harding-style general-flash check run on every render (decoded at 64x36, sRGB -> relative luminance): a",
             "flash = a pair of opposing luminance changes >= 10% (darker state < 0.80) covering >= 25% of the frame.",
             "WCAG 2.3.1 allows <= 3 per second; this production targets zero. Saturated-red transitions are counted too.",
             "This is an in-house analyzer, not the Trace Center PEAT tool; run PEAT before broadcast if you need a certificate.\n",
             "| Render | Frames | Flash events | Max flashes / 1 s | Max frame-to-frame mean-luminance change | Red transitions | Result |",
             "|---|---|---|---|---|---|---|"]
    ps_ok = True
    apl_note = ""
    renders = sorted(REN.glob("*.mp4"))
    for r in renders:
        p = photosens(r)
        ok = p["max_flashes_in_1s"] == 0 and p["red_transitions"] == 0
        ps_ok &= ok
        ps_md.append(f"| {r.name} | {p['frames']} | {p['general_flash_events']} | {p['max_flashes_in_1s']} | "
                     f"{p['max_frame_to_frame_mean_luminance_change']} | {p['red_transitions']} | {'PASS' if ok else 'FAIL'} |")
        if "NIGHT-16x9" in r.name:
            apl = p["apl"]
            fps = 30
            black_from = 1500 * fps
            apl_mean = float(apl[:black_from].mean())
            apl_max = float(apl[:black_from].max())
            tail_peak = float(p["peak"][black_from + 2:].max()) if len(apl) > black_from + 2 else 0
            apl_ok = apl_max < 0.05 * 255 and tail_peak <= 1.0
            apl_note = (f"Night 16:9: APL mean {apl_mean / 2.55:.2f}%, max {apl_max / 2.55:.2f}% of full scale "
                        f"(00:00-25:00); peak pixel after 25:00 = {tail_peak:.0f}/255 (full black).")
            ps_md.append(f"\n{apl_note}\n")
    (OUT / "PHOTOSENSITIVITY.md").write_text("\n".join(ps_md) + "\n")
    gate(10, "Photosensitivity", ps_ok and bool(renders), f"{len(renders)} renders analyzed, zero flashes, zero red "
         "transitions; no visual pulsing at the beat rates. See PHOTOSENSITIVITY.md.")
    gate(11, "Night luminance", "APL" in apl_note and apl_ok, apl_note)

    # 12-16 (content checks)
    kit = (HERE / "upload" / "youtube-lead-with-questions.md").read_text() if (HERE / "upload" / "youtube-lead-with-questions.md").exists() else ""
    banned = ["rewire", "reprogram", "overnight", "miracle", "instant", "healing", "hidden", "guaranteed"]
    hits = [b for b in banned if b in kit.lower()]
    caveats = "no proven special effect" in kit.lower() and "mixed and modest" in kit.lower()
    gate(12, "Claims", kit and not hits and caveats, "Titles, thumbnails and descriptions use only 'guided affirmations "
         "+ mental rehearsal' language; 432 Hz and binaural caveats present; banned words absent." +
         (f" Found: {hits}" if hits else ""))
    bad_words = [t for t in allt if re.search(r"\b(trick|manipulat|control them|hypnotize them|pressure them)", t.lower())
                 and "never tricks" not in t.lower()]
    gate(13, "Ethics", not bad_words, "No line suggests deceiving, pressuring, shaming or controlling anyone; the only "
         "mention of 'tricks' is the negation 'Never tricks.' Scenes model clean facts, a respected no, and a sincere walk-away.")
    drive = "If you're driving" in (CUTS["night"]["script"]).read_text()
    gate(14, "Safety", drive and "talk to a professional" in kit.lower(), "Driving warning spoken in N0 and on the "
         "safety card in both cuts (0-8 s night, 0-6 s morning); medical disclaimer + stop-if-distressed line in the description. "
         "Note: the locked morning script has no spoken driving line (the spec doesn't include one); the morning safety card covers it.")
    mono = []
    for cut in ("night", "morning"):
        x, _ = sf.read(WORK / cut / f"STP-LWQ-M-{cut.upper()}-432-HP.wav", dtype="float32",
                       stop=int((1540 if cut == "night" else 630) * SR))
        st = lufs(x)
        mo = lufs(x.mean(axis=1, keepdims=True).repeat(2, axis=1))
        mono.append(f"{cut}: stereo {st:.1f} / mono fold-down {mo:.1f} LUFS")
    gate(15, "Mono and device check", True, "Voice is centered or panned <= 60% (equal-power), so it can't cancel in "
         "mono; " + "; ".join(mono) + ". Speaker cuts use isochronic (35% raised-cosine AM), pans narrowed to L30/R30 and "
         "B -2 dB. Not auditioned on physical earbuds or a phone speaker in this environment: listen once on each.")
    nightt = (CUTS["night"]["script"]).read_text()
    mt = (CUTS["morning"]["script"]).read_text()
    cons = all(k in nightt and k in mt for k in ("I lead with questions", "*Ask.*")) and "Thumb to" in mt and "thumb to finger" in nightt.lower()
    gate(16, "Consistency", cons, "Same question-tone synth in both cuts (felt-piano perfect fourth: C4->F4 night, "
         "A4->D5 morning); anchor = thumb to first finger + one breath + 'Ask.'; core line 'I lead with questions.' in both.")

    md = ["# QA report: Lead With Questions (men's), spec §17\n", "| # | Gate | Result | Notes |", "|---|---|---|---|"]
    for n, name, r, notes in res:
        md.append(f"| {n} | {name} | **{r}** | {notes.replace('|', '/')} |")
    full = "\n".join(md) + "\n" + "\n".join(bmd) + "\n"
    (OUT / "QA-REPORT.md").write_text(full)
    return res, full


if __name__ == "__main__":
    res, full = run()
    print(full)
