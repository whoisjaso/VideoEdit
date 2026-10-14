# Lead With Questions (men's): production notes

These notes cover spec §16 items 1 (change log), 6 (casting), 7–11 (generators, tone, music, beds) and 12 (mix plan).
Everything here was produced in code, in this repo:

| Step | Command |
|---|---|
| Timeline (TTS + pause tuning) | `python projects/lead-with-questions/lwq_timeline.py night morning` |
| All audio (stems, 8 masters) | `python projects/lead-with-questions/lwq_audio.py night` / `... morning` |
| Visuals (V1–V8) | `python projects/lead-with-questions/lwq_visual.py <cut> <16x9/9x16> --render out.mp4` |
| Paper deliverables | `python projects/lead-with-questions/lwq_deliver.py` |
| Finals, encodes, teaser | `python projects/lead-with-questions/lwq_finish.py` |
| QA gates | `python projects/lead-with-questions/lwq_qa.py` |

Needs: ffmpeg, numpy, scipy, soundfile, pillow, mido, kokoro-onnx (model files v1.0).

---

## 1. Change log (script lock)

- **Spoken words: unchanged.** Every line of §8.2 and §9.2 is rendered word for word; the diff is in QA gate 1.
  `{NAME}` → "Jason". **No pronunciation respellings were needed**: the heteronym gate passed (every "lead" is the
  verb /liːd/, and "read my mind" is present tense). "Obavia" doesn't occur in either script.
- **Pauses:** tuned per unit (a section, or a scene inside N6/M4) with one scale factor, so each unit starts on its
  timestamp. IMPACT pauses (after `[TONE]`) are never shortened. The factors are in `deliverables/script-<cut>-locked-tuned.md`
  (actual pause lengths written into each `[Pn]`) and in the cue sheets. Notable ones:
  - N6.1 *The Lot* is the densest scene. Its non-IMPACT pauses go to 0.35× and it still runs 4.9 s long (within ±10 s).
    N6.2 absorbs the difference, so N6.3 onward starts exactly on target.
  - N9 pauses are stretched 2.5× so the last word ("...sleep now.") ends at **25:40.0**, as §8.2 asks.
  - M7: the voice is fitted to end at 10:03. "ASK FIRST." (4 s) and the end card fill the rest, and the music tail reaches silence at 10:30.
- **Counted breaths** (N1, M1): the count lines are split on "..." and each number lands on a 1-second beat, so
  "in... two... three... four" really takes four seconds.
- **[BR]:** a synthesized relaxed exhale (shaped noise, no tones) at −12 dB relative to speech. The TTS engine has no breath token.

### [DEFAULT] decisions (spec says: choose, label, keep going)
| # | Decision | Why |
|---|---|---|
| D1 | **Voices are local Kokoro TTS, not ElevenLabs:** A = `am_michael` (median F0 ≈ 124 Hz), B = `am_fenrir` (≈ 147 Hz, clearly different timbre) | No ElevenLabs access in this environment. The ElevenLabs job files (item 3) are ready to re-voice in one batch. |
| D2 | No SELF voice; A reads the "I" lines | None supplied (spec default) |
| D3 | Section-wide pitch treatments (−0.5 / −0.75 st) **not applied**; the slower night delivery comes from engine speed (0.84–0.92) | Formant-preserving pitch shift isn't available locally, and plain resampling on a whole section sounds processed. **Embedded suggestions do get** −0.75 st, ~10% slower, +1 dB and less reverb. |
| D4 | Whisper layer = the narrator's own clip turned into a whisper (its spectral envelope on noise, LP 7 kHz, hard de-ess) | No `eleven_v3 [whispers]` available. The content is identical to the spec list. |
| D5 | Masked layer **off** (spec default) | — |
| D6 | Video masters at **1920×1080**, 30 fps, H.264 High, CRF 18 (max 16 Mbps), 8-bit with a **static** 1% (night) / 1.5% (morning) monochrome dither | The spec allows 1080p. 4K procedural renders would take about 4× the time for a near-black picture. With moving (temporal) grain the files ran ~75 Mbps; a static dither prevents banding just as well at ~7 Mbps. |
| D7 | Light rain, birds, wave swells, bowl and bell are **synthesized** (no samples) | No license questions. The rain uses rounded droplet grains (≥3 ms attacks), so it never clicks. |
| D8 | Glue compression skipped; a lookahead peak limiter only | The TTS is already level-consistent per clip (each clip is normalized to the section target). |
| D9 | **Night ducking deepened to 6.5 dB** (attack 80 ms, release 1.2 s): music sits at −33 LUFS-S under the voice (as §11.1 says) but rises to about −26.5 in the long pauses. Morning keeps the spec's 3 dB / 600 ms. | With §11.1's levels and a 2–3 dB duck, the night master measured LRA 11.5 LU, because the long IMPACT pauses drop to the beds alone. §11.10 allows beds to move in the pauses, so they fill the pauses instead. The music never changes level during a spoken line beyond the duck itself. |
| D10 | The 9:16 files carry the **speaker** (isochronic) mix and the 16:9 files the **headphone** (binaural) mix | Phones mostly play vertical video on speakers. All 8 audio-only masters are delivered either way. |
| D11 | ElevenLabs voice picks in the job files: A = **Brian** (`nPczCjzI2devNBz1zQrb`), B = **Eric** (`cjVigY5qzO86Huf0OWal`) | Premade library voices. Check the IDs in your library before batching. |

### Ethics flag (§14)
No line reads as "trick people". The only occurrence of "tricks" is the negation "Never tricks." **No change proposed.**

---

## 6. Voice casting picks

| Role | ElevenLabs candidate | Why | Local render (used) |
|---|---|---|---|
| A | **Brian** (deep, middle-aged American narrator) ← pick | Warm baritone, no radio gloss; holds slow pacing well | `am_michael` |
| A | Bill (older American, documentary) | More gravel, older-brother feel; a little slower | |
| A | Adam (deep American) | Strong low end; can sound announcer-like at high style, so keep style ≤ 0.05 | |
| B | **Eric** (smooth American tenor-baritone) ← pick | Lighter and clearly separable from Brian in the double induction | `am_fenrir` |
| B | Chris (casual American) | Softer and conversational; good for the morning echoes | |
| B (alt) | Sarah / Matilda (warm female alto) | The spec's alternate if two male voices blur on cheap earbuds | |

Presets: exactly §10.4 (copied into every line of `tts-jobs-<cut>.jsonl`). Generate one line per request, 2–3 takes
each, and log the chosen take IDs in the `take_id` field.

---

## 7–8. Binaural + isochronic generators
- Code: `binaural()` (the spec §11.4 reference generator, unchanged) and `isochronic()` (35% raised-cosine AM on the
  same carrier and schedule) in `lwq_audio.py`. The schedule comes from the actual section starts (`beat_points()`).
- Carriers: night F3 = 171.44 Hz (432) / 174.61 Hz (440); morning D4 = 288.33 Hz (432) / 293.66 Hz (440).
- Rendered WAVs (48 kHz/24-bit) are regenerated by `lwq_audio.py` into `/tmp/lwq/<cut>/binaural_<cut>_<432|440>.wav`
  and `isochronic_…wav`. They aren't committed: 0.5 GB each, and they rebuild bit-exact in seconds.
- Levels: binaural −38 (night) / −34 (morning) LUFS-S; isochronic −40 / −36.

## 9. Question tone, bowl, bell
- **Question tone:** synthesized felt piano (8 inharmonic partials, 12 ms soft attack, felt "thump"), two notes a
  perfect fourth up, each about 0.5 s with a release, plus a dark hall tail (3.2 s). Night C4→F4, morning A4→D5. It's the same
  function both times, only transposed. Files: `deliverables/audio/question_tone_<cut>_<432|440>.wav`.
  Night −27 LUFS-M in N6; sleep-tail cues at 26:00, 26:45 and 27:30 at −50 dBFS peak. Morning −22 LUFS-M.
- **Singing bowl:** F3, four bowl partials (1, 2.76, 5.40, 8.93), each a beating pair, 0.35 s raised-cosine attack
  (no metallic transient), about 8 s ring, −28 LUFS-M, under each "Ask." in N7.
- **Bell:** a soft tubular bell on D5 (5 partials), −18 LUFS-M, on "Five", with the D(add9) resolution.

## 10. Music brief + MIDI
**Night:** F major, 60 BPM, rubato feel, then free time from 24:00. Fmaj9 → Dm9 → B♭maj7(♯11) → Csus2, 2 bars each.
It simplifies to Fmaj9 ↔ B♭maj7 from 21:00 and holds Fmaj9 from 24:00. Instruments:
- a warm additive pad (2 s attack, 4 s release, LP 2.5 kHz)
- a sparse felt piano on F pentatonic (F G A C D), with a 6 s / 5 s dark hall
- a cello drone on F2 with slow vibrato
- a sub on F1 at a very low level

The arc follows §11.2 exactly: the motif enters at 03:00, the piano drops out at 06:00, N6 is drone-only, an F swell
sits under each Ask, and a 4-minute fade runs to silence.

**Morning:** D major, 72 BPM, ramping to 96 BPM over 02:40–02:50. D(add9) → A/C♯ → Bm7 → Gmaj9, 2 bars each.
Instruments:
- a pad
- a plucked mallet pulse in eighths from 01:45
- felt-piano answers
- a shaker in 16ths from 02:45
- a soft round kick on 1 and 3 over 04:45–07:45
- a sub on the roots

The riser runs across the whole count over Gmaj9 → Asus4, resolving to D(add9) exactly on "Five", and the tail
reaches silence at 10:30. 1–4 kHz is carved −2 dB under the voice.

**MIDI:** `deliverables/music-night-harmony.mid`, `deliverables/music-morning-harmony-pulse.mid` (harmony + pulse,
tempo map included). Tune your instruments to A = 432 (−31.77 cents) or 440.
**License plan:** all music is original and composed in code in this repo. No third-party stems or samples, so it's
cleared for commercial YouTube use.

## 11. Beds
| Bed | Built from | Level | Window |
|---|---|---|---|
| Night brown noise | integrated white noise, LP 900 Hz, decorrelated L/R | −42 LUFS-S | fades 25:00–28:00 |
| Night rain | pink wash 350 Hz–7 kHz + rounded droplet grains, 90 s loop with 5 s crossfades | −40 LUFS-S | fades 25:30–28:00 |
| Morning pink noise | 1/f noise, LP 6 kHz | −40 LUFS-S | 00:00–02:00 |
| Morning birds | sparse synthesized chirps and trills, LP 6 kHz, distant reverb | −34 LUFS-S | 00:00–03:00 |
| Night wave swells | noise whose low-pass cutoff opens on the inhale and closes on the exhale | −36 LUFS-S | the 3 counted cycles + the free-breathing cycles in N1 |
All of these are generated, so there are no licenses to track.

## 12. Mix plan
**Track order (top to bottom):**
1. VOX A
2. VOX B
3. WHISPER
4. MUSIC (ducked)
5. BINAURAL or ISOCHRONIC
6. NOISE
7. RAIN or BIRDS
8. SFX
9. TONE
10. MASTER

Levels follow §11.1 exactly. Every stem is measured with a BS.1770 meter (`lufs()` in `lwq_audio.py`) and gained to its target.

**Voice chain, per clip:**
1. HP 70 Hz, 12 dB/oct
2. +1.5 dB bell at 150 Hz (Q 1)
3. Night only: −2 dB high shelf above 8 kHz
4. B only: −1.5 dB high shelf above 6 kHz
5. Normalize to −20 (night) / −15 (morning) LUFS
6. B sits −5 dB (N3/N4), −4 dB (N5) or −6 dB (N8) under A; the speaker version takes B down another −2 dB
7. Equal-power pan per §10.3: A L60 / B R60 from "Six" through N4, B R30 in N5, B R60 in N8; morning B R30. The speaker version narrows these to L30 / R30 (R20).
8. Reverb send into a 1.75 s room with 20 ms pre-delay: night 9% wet, morning 4.5% wet, B +4%, embedded suggestions −2%

**Automation:**
- Night VOX A drops 1 dB every 10 s from 24:00, reaching −10 dB by 25:40.
- Music, pad and drone follow the §11.2 arc. All fades use raised-cosine S-curves.

**Master:**
- Gain to the integrated target, measured over 00:00–25:40 at night and over the full cut in the morning.
- A lookahead peak limiter with its ceiling at −2.9 dBFS (night) / −1.9 dBFS (morning), so the true peak stays under −2 / −1 dBTP.
- Then the night sleep-tail tones are added at −50 dBFS peak.

**Exports:**
- WAV 48 kHz/24-bit
- MP3 320 kbps CBR in **plain stereo** (`-joint_stereo 0`, so the binaural L/R difference survives)
- M4A AAC 256 kbps
- Video audio: AAC-LC 320 kbps, 48 kHz, stereo
