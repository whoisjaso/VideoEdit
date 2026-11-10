# Report: "Your brain is racist. So is mine." (v1)

Built 2026-11-10 for Jason Obawemimo, olaceo. **Nothing is posted. Nothing posts without Jason's OK.**

## 1. Read this first

Four things in this cut are not what the brief asked for. Each is a decision for Jason.

1. **There are no Higgsfield plates and no Higgsfield job ids.** The workspace had 0 credits, the one generation attempted was
   refused ("Out of credits in the selected workspace"), and the free trial cannot be spent from Claude Code ("available in: Claude
   chat, Claude Cowork, ChatGPT"). Every shot is a procedural plate drawn in code. They read as soft, backlit, shallow-focus
   graphics, not as photographs. Generated plates drop into `plates/` and replace them on the next render (`higgsfield-plates.md`).
2. **The voice is a scratch narrator, not Jason.** Offline engine (Kokoro v1.0, voice `am_michael`, speed 0.92). I cannot hear
   audio, so the pick was made on measurements (§4), not on "sounds like he's thinking". Treat it as a timing track until Jason
   reads it. `python3 src/narrate.py align --wav jason.wav` re-times the whole film to his recording.
3. **It runs 7:47, not ~5:30.** The script is 1,116 spoken words. At this read (169 words a minute while speaking, 1.0 s on each
   marked pause) that is 7:38 of narration plus the silent hook and close. 5:30 would need about 200 words a minute, which is not a
   slow read. To hit 5:30, cut roughly 300 words; the script was not cut here.
4. **Three script lines were changed** to keep the brief's own rule (§3).

## 2. Deliverables

| Deliverable | File | Spec |
|---|---|---|
| 16:9 master | `renders/your-brain-is-racist-16x9-v1.mp4` | 1920x1080, 60/1 fps, 28,022 frames, 7:47, H.264 + AAC 320k |
| 9:16 cut | `renders/your-brain-is-racist-9x16-v1.mp4` | 1080x1920 native (re-laid out, not cropped), same length |
| Traffic-stop cut (post 2) | `renders/your-brain-is-racist-cut-traffic-stop-{16x9,9x16}.mp4` | 73 s (brief asked for 60; see promo kit) |
| Code-switching cut (post 3) | `renders/your-brain-is-racist-cut-code-switching-{16x9,9x16}.mp4` | 42 s (brief asked for 45) |
| Narration track | `audio/narration.flac` | voice only, timed to picture, 48 kHz mono |
| Final mix | `audio/master_mix.flac` | 48 kHz stereo, 24-bit |
| Captions | `captions/your-brain-is-racist.en.srt` | 3–5 words a line, every spoken word |
| Thumbnails | `thumbnails/01_hook`, `02_the_script`, `03_two_scripts` | each at 1280x720 and 1080x1350 |
| Promotion kit | `promo/promotion-kit.md` | post text, captions, pinned comment, first-hour rules, posts 2 and 3 |
| Narration as recorded | `narration-as-recorded.txt` (source: `src/script.py`) | |
| Voice auditions | `audio/auditions/*.wav` | three voices on the first four lines and the traffic stop |
| Frame review sheets | `stills/final_16x9.jpg`, `stills/final_9x16.jpg` | 30 frames from each finished file |

## 3. Lines that changed from the brief's script

| Where | Brief | As recorded | Why |
|---|---|---|---|
| The IAT | "…and most people's brains, including people of every race, pair the same faces with the same words faster than the others." | "…and most people's brains pair the same faces with the same words faster than the others. And it shows up in people of every race." | The original says every race shows it as a group. Nosek et al. (2007) report that Black participants show no implicit preference on average. The new wording is true of individuals and of test-takers overall. Checked against the paper this session. |
| Whose fault | "…by ten thousand hours of screens before you were old enough to say no." | "…by thousands of hours of screens before you were old enough to say no." | Brief rule: a number comes from a named study or it is cut. No study stands behind 10,000. |
| The half-second | "The script runs in a quarter of a second." | "Here's a model of it. The script runs in about a quarter of a second." | Brief rule: where it is a model, say "a model". The graphic is also labelled "a model, not a measurement". |

Flagged, not changed: "Here's the thing nobody says out loud" trips the house copy linter as an AI-coded phrase (`lint_copy.py`:
0 blocks, 1 AI-tell). It is Jason's line, so it stays until he says otherwise.

Italics in the script (*You* don't, *its* script, *their* script) are stress marks for the reader. The scratch voice does not
stress them. Jason will.

## 4. Voice audition (measured, not heard)

Same eleven lines, speed 0.96. Lower pitch and a narrower pitch range read as calmer on paper.

| Voice | Median pitch | Pitch range (10th–90th pct) | Pace while speaking |
|---|---|---|---|
| am_michael (used) | 124 Hz | 54 Hz | 180 wpm |
| am_fenrir | 145 Hz | 98 Hz | 211 wpm |
| am_onyx | 93 Hz | 34 Hz | 198 wpm |

`am_onyx` is the lowest and flattest, but it is the engine's lowest-rated voice for quality, so `am_michael` was used and slowed
to 0.92 (169 wpm). Listen to all three in `audio/auditions/`. The Higgsfield narrator set was not auditioned (no credits).

## 5. Faces

No generated plate exists, so none had to be rejected. In the procedural plates no face is drawn anywhere:

- the three characters are backlit outlines, soft-focus, cut at the thigh;
- the street figures are out-of-focus outlines that never sharpen;
- the officer and the driver are points of view (a hood, a mirror, hands on a wheel, a forearm); the one head visible is a
  dark shape through a rear window;
- the child, the boy and the man in the glass room are seen from behind or through reflections;
- the IAT "faces" are identical grey ovals, as the brief asked.

## 6. Where the cut departs from the shot list

- **#8 IAT.** Words are blank chips, not readable words, so no word sits next to a "face". Two lanes ("pairs that match the
  script" / "pairs that don't") with a response bar each; the difference is the amber segment.
- **#13.** The amber card carries the full spoken sentence ("Your brain ran the script and moved your feet…"), word by word.
- **#23.** One waveform that rises and narrows, with a label that changes (home → the interview → the sales call → the meeting).
  The two microphones were dropped as clip art.
- **#27.** The observer is marked at 0.75 s (the half-second after the quarter-second), not at 0.5 s, to match the narration.
- **Added type** so no stretch is a bare caption on black: "keep you alive.", "cultivation / Gerbner & Gross, 1976",
  "Say that's not you.", "dangerous? / safe?", "Not hate. Prediction.", "it's watching you.", "Repetition becomes identity."
- **Sound.** Only the sounds in the brief's §7, all synthesized in `src/mix.py`. The house font-signature sounds were left out
  because the brief rules out whooshes and risers. The low tone on the traffic stop rises and cuts as written.
- **Grain** is added in the encoder (luma noise), not baked into the plates.

## 7. Measurements

| Check | Result | Bar |
|---|---|---|
| Frame rate | 60/1 exactly, both masters | 60/1 |
| Frames | 28,022 read = 467.03 s x 60, both masters | no dropped frame |
| Loudness | QA_LUFS | −14 LUFS |
| True peak (in the MP4, after AAC) | QA_TP | ≤ −4 dBTP |
| Speech through the mix | 98.8% word match, mix vs voice-only (`whisper_check.py`, 1 run) | ≥ 98% |
| Caption / card timing source | 98.7% of words matched by the aligner; the rest interpolated between neighbours | |
| Smoothness | QA_SMOOTH | dup ≤ 0.02, jitter ≤ 0.35 |

`whisper_check.py` prints "pass: false" because its first-three-seconds rule expects speech in the hook. The hook is silent by
design (type only; narration starts at 4.8 s), so that rule does not apply.

Not run: `lint_cuesheet.py` and `word_sync.py` from the house standard. This film was built on its own clock (`timeline.json`,
`scenes.json`, `cues.json`), not on the house cue-sheet schema, so those tools have nothing to read. No 8-sample motion blur
either: every move in this film is slow enough that it was left out.

## 8. Defects found and fixed during the build

- First encode had red and blue swapped (amber came out blue). Caught on the frame sheet, fixed, both formats re-rendered.
- AAC at 256k produced a one-channel peak at −1.9 dBTP on a −5.3 dBTP master. 320k holds −5.3. The masters use 320k.

## 9. What Jason does next

1. Watch the 16:9 master once with sound.
2. Decide: record the narration himself (first choice in the brief), or pick a narrator.
3. Decide: keep 7:47, or cut the script toward 5:30.
4. Decide: procedural plates, or generate the Higgsfield set from Claude chat on the free trial and drop them into `plates/`.
5. Approve or change the three edited lines.
6. Only then: post, using `promo/promotion-kit.md`.
