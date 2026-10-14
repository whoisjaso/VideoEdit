"""Paper deliverables (spec §16 items 1-6, 10, 12): locked + annotated scripts, TTS jobs, cue sheets, SRT, MIDI.

    python projects/lead-with-questions/lwq_deliver.py      # -> projects/lead-with-questions/deliverables/
"""
import csv
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from lwq_script import parse, NAME                          # noqa: E402
from lwq_timeline import WORK, VOICE_A, VOICE_B, CUTS        # noqa: E402

OUT = HERE / "deliverables"
ROLE = re.compile(r"^(A|B|SELF/A):\s*(.*)$")


def tc(t, srt=False):
    h, r = divmod(t, 3600)
    m, s = divmod(r, 60)
    if srt:
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s - int(s)) * 1000)) % 1000:03d}"
    return f"{int(m):02d}:{s:05.2f}" if h == 0 else f"{int(h)}:{int(m):02d}:{s:05.2f}"


def load(cut):
    return json.loads((WORK / cut / "timeline.json").read_text())


# ---------------------------------------------------------------- source tags (§5 traceability)

SECTION_TAGS = {
    "N0": "[§13 Safety][§3 honest framing]", "N1": "[§4 row 16 slow breathing][§3.7 induction]",
    "N2": "[§3.7 progressive relaxation]", "N3": "[§3.7 countdown deepener][§10.3 double induction]",
    "N4": "[§3.7 Ericksonian metaphor][§5.3 frame rule: who asks holds the light]",
    "N7": "[§3.6 anchor][§6.6 anchor phrase]", "N8": "[§3.3 implementation intentions][§4 row 10 sleep consolidation]",
    "N9": "[§3.5 sleep-onset timing][§6.6 core line]", "M0": "[§4 row 17 sleep inertia][§15 protocol]",
    "M1": "[§4 row 16 cyclic sighing + paced breath]", "M2": "[§3.6 anchor][§6.6]",
    "M5": "[§3.3 implementation intentions][§5.4 IMPACT pause]", "M6": "[§3.7 count-up][§4 row 17 sleep inertia]",
    "M7": "[§6.6 anchor][§5.2 laws 1, 3, 4]",
}
KEYWORDS = [
    ("thumb", "[§6.6 anchor]"), ("Sounds like", "[§5.4 Disarm][§5.5 affirm before you probe]"),
    ("got you looking", "[§5.4 Intent: tangible]"), ("going on with the one", "[§5.4 Intent: experience]"),
    ("How long", "[§5.4 Duration]"), ("doing to your week", "[§5.4 Impact → IMPACT PAUSE]"),
    ("costing you", "[§5.4 Impact → IMPACT PAUSE]"), ("worth to you", "[§5.4 Impact → IMPACT PAUSE]"),
    ("go cold", "[§5.4 Impact][§6.2]"), ("comes in at nine", "[§5.4 Process][§6.2]"),
    ("If the numbers", "[§5.4 objection → hypothetical][§5.4 Self-conviction]"),
    ("clear yes", "[§5.4 Intent: tangible][§6.3]"), ("go wrong", "[§5.4 Pre-handling][§6.3]"),
    ("worries you most", "[§5.4 Doubt (soft)][§5.5 the Skeptic][§6.3 IMPACT PAUSE]"),
    ("priority now", "[§5.4 Rationale][§6.4]"), ("Walk me through", "[§5.4 Process]"),
    ("Who else weighs in", "[§5.4 Commitment: whose call][§6.4 partner/committee]"),
    ("ninety days", "[§5.4 Intent: tangible][§6.5]"), ("hardest part", "[§5.4 Intent: experience][§6.5 IMPACT PAUSE]"),
    ("gives you pause", "[§5.4 Doubt][§6.5 PAUSE]"), ("answer it straight", "[§6.5 answer first, then ask][§5.2 law 1]"),
    ("price", "[§5.2 law 1 clean facts][§5.8 price as signal]"), ("number", "[§5.2 law 1 clean facts][§5.8]"),
    ("terms", "[§5.2 law 1][§6.3 exact numbers]"), ("say it back", "[§5.4 Gap reflection]"),
    ("So you need", "[§5.4 Gap reflection]"), ("stop talking", "[§5.2 law 3 let them say it][§5.4 IMPACT pause]"),
    ("silence", "[§5.2 law 3][§5.4 IMPACT pause]"), ("quiet", "[§5.2 law 3][§5.4 IMPACT pause]"),
    ("wait", "[§5.2 law 3][§5.4 IMPACT pause]"), ("fine if she walked", "[§5.4 sincere walk-away][§5.9 ethics test]"),
    ("Want to drive", "[§5.4 Next step: two options][§5.2 law 4]"), ("or Monday", "[§5.4 Next step: two options]"),
    ("Tuesday at ten", "[§5.4 Next step: two options][§6.4]"), ("Thursday or Friday", "[§5.4 Next step][§6.3]"),
    ("bring them", "[§5.4 objection: invite the partner][§6.4]"), ("not auditioning", "[§5.3 frame rule][§6.5]"),
    ("lead with questions", "[§5.3 core frame][§6.6 core line]"), ("Talking isn't leading", "[§5.3 frame rule]"),
    ("Nobody's coming", "[§5.3 frame: you set the agenda]"), ("don't chase", "[§5.2 law 2 never add pressure][§5.3]"),
    ("Overthinking", "[§5.6 L1 importance turned down]"), ("perfect line", "[§5.6 L4 one question][§6.6]"),
    ("Thinking poor", "[§5.3 frame rule][brand: Stop Thinking Poor]"), ("give before", "[§5.7 give:ask ratio]"),
    ("One conversation", "[§5.2 law 4 one lane][§5.8]"), ("guilt", "[§5.9 hard bounds][§14]"),
    ("is information", "[§5.4 objections: respect a no][§5.9]"), ("hear my thoughts", "[§5.9 the transcript test]"),
    ("Jason", "[§4 row 8 distanced self-talk]"), ("urge to explain", "[§3.3 when-then][§5.2 law 3]"),
    ("three questions", "[§3.3 when-then][§5.3 answer one, return with a question]"),
    ("too much", "[§3.3 when-then][§5.4 objections → comparison]"), ("count to five", "[§3.3 when-then][§5.4 IMPACT pause]"),
    ("first question", "[§3.3 implementation intention][§15 pair with real reps]"),
]
SCENE_TAGS = {"1": "[§3.2 rehearsal][§6.1 the lot]", "2": "[§3.2 rehearsal][§6.2 AI sale]", "3": "[§3.2 rehearsal][§6.3 investor]",
              "4": "[§3.2 rehearsal][§6.4 B2B]", "5": "[§3.2 rehearsal][§6.5 interview]"}


def tags_for(sec, scene, block_tag, text):
    out = []
    if block_tag:
        out.append(block_tag)
    if scene:
        out.append(SCENE_TAGS[scene])
    for kw, tg in KEYWORDS:
        if kw.lower() in text.lower() and tg not in out:
            out.append(tg)
    if not out:
        out.append(SECTION_TAGS.get(sec, "[§3 mechanism]"))
    return "".join(out[:3])


# ---------------------------------------------------------------- locked + annotated scripts

def scripts(cut):
    tl = load(cut)
    pauses = [e for e in tl["events"] if e["kind"] == "pause"]
    pi = 0
    locked, annotated = [], []
    sec, scene, block_tag = None, None, None
    for raw in (CUTS[cut]["script"]).read_text().splitlines():
        s = raw.strip()
        m = re.match(r"\*\*([NM]\d) ·", s)
        if m:
            sec, scene, block_tag = m.group(1), None, None
        m = re.match(r"\*Scene (\d)", s)
        if m:
            scene = m.group(1)
        m = re.match(r"\*Block.*?(\[§[^\]]+\])\*|\*Name lines.*?(\[§[^\]]+\])\*", s)
        if m:
            block_tag = m.group(1) or m.group(2)
        rm = ROLE.match(s)
        if not rm:
            locked.append(raw)
            annotated.append(raw)
            continue

        def sub(mm):
            nonlocal pi
            e = pauses[pi]
            pi += 1
            return f"[P{e['dur']:.1f}]"
        tuned = re.sub(r"\[P[\d.]+\]", sub, s)
        locked.append(tuned)
        plain = re.sub(r"\[P[\d.]+\]|\[BR\]|\[TONE\]|\*", "", rm.group(2))
        annotated.append(f"{s}   {tags_for(sec, scene, block_tag, plain)}")
    assert pi == len(pauses), (pi, len(pauses))
    head = f"# Lead With Questions: {cut.upper()} script (locked, pauses tuned to the timeline)\n\n"
    (OUT / f"script-{cut}-locked-tuned.md").write_text(head + "\n".join(locked) + "\n")
    (OUT / f"script-{cut}-annotated.md").write_text(
        f"# Lead With Questions: {cut.upper()} script, annotated with §5 source tags (tags are never spoken)\n\n"
        + "\n".join(annotated) + "\n")


# ---------------------------------------------------------------- lines (grouped say events)

def lines(tl):
    groups = {}
    for e in tl["events"]:
        if e["kind"] == "say":
            groups.setdefault((e["unit"], e["line"]), []).append(e)
    out = []
    for (u, ln), evs in sorted(groups.items(), key=lambda kv: kv[1][0]["t"]):
        txt = " ".join(x["text"] for x in evs)
        if evs[0].get("counted"):
            txt = "... ".join(x["text"] for x in evs) + "."
        out.append(dict(unit=u, line=ln, role=evs[0]["role"], start=evs[0]["t"], end=evs[-1]["t"] + evs[-1]["dur"],
                        text=re.sub(r"\s+", " ", txt).strip(), emb=any(x["emb"] for x in evs)))
    return out


def srt(cut):
    tl = load(cut)
    rows = []
    for i, l in enumerate(lines(tl), 1):
        if l["role"] == "B" and cut == "night" and l["unit"].startswith(("N3", "N4")):
            text = f"({l['text']})"
        else:
            text = l["text"]
        rows.append(f"{i}\n{tc(l['start'], True)} --> {tc(l['end'] + 0.3, True)}\n{text}\n")
    (OUT / f"captions-{cut}.srt").write_text("\n".join(rows))


# ---------------------------------------------------------------- TTS jobs (ElevenLabs)

PRESETS = {
    ("night", "A", "N0-N2"): dict(stability=0.70, similarity_boost=0.80, style=0.05, use_speaker_boost=True, speed=0.88),
    ("night", "A", "N3-N8"): dict(stability=0.75, similarity_boost=0.80, style=0.03, use_speaker_boost=True, speed=0.82),
    ("night", "A", "N9"): dict(stability=0.80, similarity_boost=0.80, style=0.00, use_speaker_boost=True, speed=0.76),
    ("night", "B", "*"): dict(stability=0.65, similarity_boost=0.75, style=0.08, use_speaker_boost=True, speed=0.80),
    ("morning", "A", "M0-M2"): dict(stability=0.60, similarity_boost=0.80, style=0.12, use_speaker_boost=True, speed=0.95),
    ("morning", "A", "M3-M7"): dict(stability=0.50, similarity_boost=0.80, style=0.22, use_speaker_boost=True, speed=1.05),
    ("morning", "B", "*"): dict(stability=0.60, similarity_boost=0.75, style=0.10, use_speaker_boost=True, speed=1.00),
}
EL_VOICE = {"A": "nPczCjzI2devNBz1zQrb", "B": "cjVigY5qzO86Huf0OWal"}   # [DEFAULT] Brian / Eric (premade library)


def preset(cut, role, sec):
    if role == "B":
        return PRESETS[(cut, "B", "*")]
    if cut == "night":
        k = "N9" if sec == "N9" else ("N0-N2" if sec in ("N0", "N1", "N2") else "N3-N8")
    else:
        k = "M0-M2" if sec in ("M0", "M1", "M2") else "M3-M7"
    return PRESETS[(cut, "A", k)]


def pan_name(cut, role, sec, t, tl):
    sys.path.insert(0, str(HERE))
    from lwq_audio import pan_for
    p = pan_for(cut, tl, dict(unit=sec, role=role, t=t), False)
    return "C" if p == 0 else (f"L{int(abs(p) * 100)}" if p < 0 else f"R{int(p * 100)}")


def tts_jobs(cut):
    tl = load(cut)
    rows = []
    for i, l in enumerate(lines(tl), 1):
        sec = l["unit"].split(".")[0]
        role = "SELF/A" if l["role"] == "SELF" else l["role"]
        post = dict(pitch_st=-0.75 if l["emb"] else 0.0, gain_db=1.0 if l["emb"] else 0.0,
                    reverb_wet=(0.09 if cut == "night" else 0.045) + (0.04 if l["role"] == "B" else 0),
                    level_rel_A_db=0 if l["role"] != "B" else (-4 if sec == "N5" else -6 if sec == "N8" else -5),
                    embedded=l["emb"])
        rows.append(dict(id=f"{cut[0].upper()}{i:03d}", section=l["unit"], start_target=round(l["start"], 2),
                         voice_role=role, voice_id=EL_VOICE["B" if l["role"] == "B" else "A"],
                         model_id="eleven_multilingual_v2", voice_settings=preset(cut, l["role"], sec),
                         text=l["text"], pan=pan_name(cut, l["role"], l["unit"], l["start"], tl), post_fx=post,
                         local_render=dict(engine="kokoro-onnx v1.0", voice=VOICE_B if l["role"] == "B" else VOICE_A)))
    rep = json.loads((WORK / cut / "audio_report.json").read_text())
    for j, (t, txt) in enumerate(rep["whisper_lines"], 1):
        rows.append(dict(id=f"{cut[0].upper()}W{j:03d}", section="whisper", start_target=t, voice_role="A (whisper)",
                         voice_id=EL_VOICE["A"], model_id="eleven_v3",
                         voice_settings=dict(stability=0.5, similarity_boost=0.75, use_speaker_boost=True),
                         text=f"[whispers] {txt}", pan="autopan L40-R40", post_fx=dict(lowpass_hz=7000, deess="hard"),
                         local_render=dict(engine="kokoro + spectral-envelope whisper", voice=VOICE_A)))
    (OUT / f"tts-jobs-{cut}.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n")


# ---------------------------------------------------------------- cue sheet

def cues(cut):
    tl = load(cut)
    rep = json.loads((WORK / cut / "audio_report.json").read_text())
    S = {s["sid"]: s["start"] for s in tl["sections"]}
    rows = []
    for s in tl["sections"]:
        rows.append((s["start"], s["end"], "SECTION", s["sid"], s["title"]))
    for l in lines(tl):
        rows.append((l["start"], l["end"], f"VOX {l['role']}", l["unit"], l["text"]))
    for e in tl["events"]:
        if e["kind"] == "pause":
            rows.append((e["t"], e["t"] + e["dur"], "PAUSE", e["unit"],
                         f"{'IMPACT ' if e['impact'] else ''}scripted {e['scripted']}s -> {e['dur']:.1f}s"))
        elif e["kind"] == "tone":
            rows.append((e["t"], e["t"] + 1.2, "TONE", e["unit"], "question tone"))
        elif e["kind"] == "br":
            rows.append((e["t"], e["t"] + 1.6, "VOX A", e["unit"], "[BR] audible exhale"))
        elif e["kind"] == "breath":
            rows.append((e["t"], e["end"], "BREATH", e["unit"], f"guided {e['phase']}-breath"))
    sys.path.insert(0, str(HERE))
    from lwq_audio import beat_points
    pts, fin, fout = beat_points(cut, tl)
    for t, b in pts:
        rows.append((t, t, "BINAURAL", "", f"beat target {b} Hz"))
    rows.append((fout[0], fout[1], "BINAURAL", "", "fade out"))
    for t, txt in rep["whisper_lines"]:
        rows.append((t, t + 2, "WHISPER", "", txt))
    if cut == "night":
        for t in rep["wave_swells"]:
            rows.append((t, t + 10, "SFX", "N1", "wave swell (rise on inhale, fall on exhale)"))
        for t in rep["bowls"]:
            rows.append((t - 0.3, t + 8, "SFX", "N7", "singing bowl, F"))
        for t in (1560, 1605, 1650):
            rows.append((t, t + 3, "TONE", "N9", "sleep-tail cue, -50 dBFS peak (experimental)"))
        music = [(0, "pad fades in 8 s; rain + brown noise in"), (S["N2"], "felt-piano motif enters (F-A-C)"),
                 (S["N3"], "piano out (6 s), cello drone in"), (S["N4"], "drone + sparse piano"),
                 (S["N5"], "sparse piano"), (S["N6"], "pad thins to drone only"),
                 (S["N7"], "pad back; F major swell under each Ask; harmony Fmaj9 <-> Bbmaj7"),
                 (S["N8"], "pad only; drone fades"), (1440, "music 4-min fade begins; Fmaj9 held, free time"),
                 (1500, "brown-noise fade begins; picture full black"), (1530, "rain + binaural fades begin"),
                 (1680, "digital silence")]
    else:
        five = rep["riser"][1]
        for t in (S["M3"], S["M4"]):
            rows.append((t - 0.9, t + 0.6, "SFX", "", "soft whoosh"))
        rows.append((S["M6"], five, "SFX", "M6", "riser (filtered noise)"))
        rows.append((five, five + 7, "SFX", "M6", "tubular bell, D + D(add9) resolution"))
        music = [(0, "pad + birds + pink noise in (6 s)"), (S["M2"], "plucked eighth-note pulse enters (72 BPM)"),
                 (160, "tempo ramp 72 -> 96 BPM (160-170 s)"), (S["M3"], "shaker 16ths, sub bass"),
                 (S["M4"], "soft kick on 1 and 3"), (S["M5"], "groove thins to pad + pulse"),
                 (S["M6"], "Gmaj9 -> Asus4 under the riser"), (five, "D(add9) resolution"),
                 (624, "tail to silence at 10:30")]
    for t, txt in music:
        rows.append((t, t, "MUSIC", "", txt))
    vis = visual_events(cut)
    rows += vis
    rows.sort(key=lambda r: (r[0], r[2]))
    with open(OUT / f"cuesheet-{cut}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["start", "end", "start_s", "track", "unit", "event"])
        for a, b, tr, u, ev in rows:
            w.writerow([tc(a), tc(b), round(a, 2), tr, u, ev])
    md = [f"# Cue sheet: {cut.upper()} (human-readable; full EDL in cuesheet-{cut}.csv)\n",
          "| Start | End | Track | Unit | Event |", "|---|---|---|---|---|"]
    for a, b, tr, u, ev in rows:
        if tr in ("PAUSE", "BREATH"):
            continue
        md.append(f"| {tc(a)} | {tc(b)} | {tr} | {u} | {ev.replace('|', '/')} |")
    (OUT / f"cuesheet-{cut}.md").write_text("\n".join(md) + "\n")


def visual_events(cut):
    from lwq_visual import make_plan
    p = make_plan(cut)
    S = p["S"]
    rows = []
    if cut == "night":
        rows += [(0, 8, "VISUAL", "N0", "safety card"), (8, 16, "VISUAL", "N0", "title card LEAD WITH QUESTIONS / Night Install"),
                 (16, 45, "VISUAL", "N0", "V2 particles fade in"), (S["N1"], S["N3"], "VISUAL", "N1-N2", "V1 breathing circle (synced 4/6), then resting pulse"),
                 (S["N3"], S["N4"], "VISUAL", "N3", "V4 ten light bands; V3 fractal 20%"),
                 (S["N4"], S["N5"], "VISUAL", "N4", "V5 lantern glow turns left -> right; V3 25%"),
                 (S["N5"], S["N6"], "VISUAL", "N5", "V5 steady; V3 fades to 0"),
                 (S["N6"], S["N7"], "VISUAL", "N6", "near-black, small dim glow; eases right on each tone"),
                 (S["N7"], S["N8"], "VISUAL", "N7", "glow +3% at each Ask"), (S["N8"], S["N9"], "VISUAL", "N8", "glow dims"),
                 (S["N9"], 1500, "VISUAL", "N9", "last particles fade"), (1500, 1680, "VISUAL", "N9", "full black")]
        for i, t in enumerate(p["counts"]):
            rows.append((t, t + 1.5, "VISUAL", "N3", f"band {i + 1} fades"))
        for t, lab in p["labels"]:
            rows.append((t, t + 4, "VISUAL", "N6", f"label {lab} (10% opacity)"))
    else:
        rows += [(0, 6, "VISUAL", "M0", "small safety card"), (6, 30, "VISUAL", "M0", "title card LEAD WITH QUESTIONS / Morning Run"),
                 (S["M1"], S["M2"], "VISUAL", "M1", "V1 breathing circle 4/4"),
                 (S["M2"], S["M3"], "VISUAL", "M2", "circle condenses into the sun disc; warms on steady / sharp")]
        for a, b, txt in p["cards"]:
            rows.append((a, b, "VISUAL", "", f"card: {txt}"))
        for a, b, img, q in p["scenes"]:
            rows.append((a, b, "VISUAL", "M4", f"V7 {img}: {q}"))
        for t, d in p["numbers"]:
            rows.append((t, t + 3, "VISUAL", "M6", f"number {d}"))
        rows += [(p["five"], p["five"] + 1.5, "VISUAL", "M6", "smooth brightening to daylight (no flash)"),
                 (p["askfirst"], p["askfirst"] + 4, "VISUAL", "M7", "ASK FIRST."),
                 (p["askfirst"] + 4, 628, "VISUAL", "M7", "STOP THINKING POOR end card"), (628, 630, "VISUAL", "M7", "fade to black")]
    return rows


# ---------------------------------------------------------------- MIDI (harmony + pulse)

def midi():
    import mido
    from lwq_audio import NIGHT_CHORDS, MORNING_CHORDS, beat_times
    # night: 60 BPM, 2 bars per chord
    mf = mido.MidiFile(ticks_per_beat=480)
    tr = mido.MidiTrack()
    mf.tracks.append(tr)
    tr += [mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(60)), mido.MetaMessage("track_name", name="NIGHT harmony (F major, A=432 tune your synth -31.77 c)")]
    seq = ["Fmaj9", "Dm9", "Bbmaj7#11", "Csus2"]
    t = 0
    i = 0
    while t < 1440:
        name = seq[i % 4] if t < 1260 else ["Fmaj9", "Bbmaj7#11"][i % 2]
        notes = NIGHT_CHORDS[name]
        for k, m in enumerate(notes):
            tr.append(mido.Message("note_on", note=m, velocity=50, time=0))
        for k, m in enumerate(notes):
            tr.append(mido.Message("note_off", note=m, velocity=0, time=480 * 8 if k == 0 else 0))
        t += 8
        i += 1
    for m in NIGHT_CHORDS["Fmaj9"]:
        tr.append(mido.Message("note_on", note=m, velocity=40, time=0))
    for k, m in enumerate(NIGHT_CHORDS["Fmaj9"]):
        tr.append(mido.Message("note_off", note=m, velocity=0, time=480 * 240 if k == 0 else 0))
    mf.save(OUT / "music-night-harmony.mid")
    # morning: chords every 2 bars + eighth-note pulse, tempo 72 -> 96
    mf = mido.MidiFile(ticks_per_beat=480)
    h, p = mido.MidiTrack(), mido.MidiTrack()
    mf.tracks += [h, p]
    h.append(mido.MetaMessage("track_name", name="MORNING harmony (D major)"))
    p.append(mido.MetaMessage("track_name", name="MORNING pulse (plucked eighths)"))
    beats = beat_times(580)
    seq = ["Dadd9", "A/C#", "Bm7", "Gmaj9"]
    for b in range(0, len(beats) - 1):
        if b % 4 == 0:
            bpm = 60 / (beats[b + 1] - beats[b])
            h.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm), time=0))
        if b % 8 == 0:
            name = seq[(b // 8) % 4]
            notes = MORNING_CHORDS[name]
            for m in notes:
                h.append(mido.Message("note_on", note=m, velocity=55, time=0))
            for k, m in enumerate(notes):
                h.append(mido.Message("note_off", note=m, velocity=0, time=480 * 8 if k == 0 else 0))
        if beats[b] >= 105:
            name = seq[(b // 8) % 4]
            ch = MORNING_CHORDS[name]
            for half in range(2):
                m = ch[[0, 2, 3, 4, 2, 3, 1, 4][(b * 2 + half) % 8]] + 12
                p.append(mido.Message("note_on", note=m, velocity=70 if half == 0 else 50, time=0))
                p.append(mido.Message("note_off", note=m, velocity=0, time=240))
        else:
            p.append(mido.Message("note_off", note=0, velocity=0, time=480))
    mf.save(OUT / "music-morning-harmony-pulse.mid")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for cut in ("night", "morning"):
        scripts(cut)
        srt(cut)
        tts_jobs(cut)
        cues(cut)
        print("done", cut)
    midi()
