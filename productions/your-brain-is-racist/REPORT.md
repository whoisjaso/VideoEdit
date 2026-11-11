# Report: "Your brain is racist. So is mine." (v3)

Built 2026-11-11 for Jason Obawemimo, olaceo. **Nothing is posted. Nothing posts without Jason's OK.**
v3 changes the voices and adds the short-form parts. Picture, sound design and script are v2's; the v2 and v1 reports follow and are still accurate for what they describe.

## v3 at a glance

| Deliverable | File | Spec |
|---|---|---|
| 16:9 master | `renders/your-brain-is-racist-16x9-v3.mp4` | 1920x1080, 60/1 fps, 26,737 frames, 7:26, H.264 + AAC 320k, -13.8 LUFS, true peak -4.8 dB |
| 9:16 master | `renders/your-brain-is-racist-9x16-v3.mp4` | 1080x1920 native, same length and levels |
| Six 9:16 parts | `renders/parts/your-brain-is-racist-9x16-part{1..6}-*.mp4` | 0:45 to 1:52 each, every one ends with the line becoming the E in OLACEO; -13.7 to -13.9 LUFS, peaks -4.8 dB or lower |
| Follow-up cuts | `renders/your-brain-is-racist-cut-{traffic-stop,code-switching}-{16x9,9x16}.mp4` | re-cut from v3 |
| Audio previews | `audio/preview_v3_mix.mp3`, `audio/preview_v3_voices_only.mp3` | |
| Frame overviews | `stills/final_16x9.jpg`, `stills/final_9x16.jpg`, `stills/parts_sheet.jpg` | from the finished files |

## Voices (ElevenLabs, model `eleven_v4`)

| Role | Voice | Where |
|---|---|---|
| Narrator | Brian | throughout |
| Officer's inner script | Adam, left | 3:06 |
| Driver's inner script | Will, right | 3:22 |
| The kid's brain ("See? Told you. That's us.") | Liam | 5:01 |
| Police radio | Adam (officer), Sarah (dispatch) | from 2:55 |

- The words are unchanged from v2 (`narration-as-recorded.txt`); only who speaks them changed. A recognizer confirmed 99.0% of words.
- Timing comes from ElevenLabs' own word timestamps; picture, captions and sound all re-timed from them.
- Every take is cached in `audio/el_cache/`, so a rebuild costs no characters. Swapping one voice re-records only that role's lines (`src/narrate.py`, `EL_VOICES` and `CAST`).
- Cost: 4,893 of the account's 10,000 monthly characters.
- **Before posting:** the account is on ElevenLabs' free plan, which is non-commercial and requires attribution. Move it to a paid plan first. A paid plan also allows cloning Jason's own voice, which would then be a one-line change here.
- The API key was entered through the secure form and is not in the repository.

## Open for Jason

- Whether each voice is right. They were chosen from descriptions, not by ear.
- Parts 1, 3 and 4 run longer than 60 seconds.
- Thumbnails still show the v1 look, not the new characters.

---

# Report: "Your brain is racist. So is mine." (v2)

Built 2026-11-11 for Jason Obawemimo, olaceo. **Nothing is posted. Nothing posts without Jason's OK.**
v2 answers Jason's notes on v1. The v1 report follows below and is still accurate for what it describes (research, script changes, Higgsfield).

## v2 at a glance

| Deliverable | File | Spec |
|---|---|---|
| 16:9 master | `renders/your-brain-is-racist-16x9-v2.mp4` | 1920x1080, 60/1 fps, 27,784 frames, 7:43, H.264 + AAC 320k |
| 9:16 cut | `renders/your-brain-is-racist-9x16-v2.mp4` | 1080x1920 native, same length |
| Traffic-stop cut | `renders/your-brain-is-racist-cut-traffic-stop-{16x9,9x16}.mp4` | 75 s |
| Code-switching cut | `renders/your-brain-is-racist-cut-code-switching-{16x9,9x16}.mp4` | 39 s |
| Audio previews | `audio/preview_v2_mix.mp3`, `audio/preview_v2_voice_only.mp3` | |
| Frame overviews | `stills/final_16x9.jpg`, `stills/final_9x16.jpg` | 36 frames each, from the finished files |

## What Jason asked for, and what was built

| Note | What v2 does |
|---|---|
| Every title fully capitalized | Every on-screen title, label and card is ALL CAPS with auto-fit. Captions stay sentence case (they are speech). |
| The narrator has no expression | New read with Chatterbox (Resemble AI, MIT, offline), paragraph by paragraph, each paragraph checked word for word and re-taken if it drifted. Slowed 6% without changing pitch. |
| No background sound; it should match what we see | Sound rebuilt scene by scene (`src/mix.py`): sirens, police radio, both engines, his music through the glass, city, footsteps, heartbeat, TV babble, office murmur, a cell door, title impacts, a score that darkens and lifts. |
| One continuum, one line | One unbroken line from first frame to last that becomes each scene's key shape; camera push-through moves replace every cut; one dust field and one floor tone under the whole film. |
| The exit | The OLACEO wordmark, redrawn as vector from Jason's screenshot. The line turns white and locks in as the E's middle bar. |
| Jason is the character and the narrator | His avatar (cut out of its checkerboard) appears on the hook, behind the office glass (splitting in two), and at the close. |
| Stickmen that move for real, dressed, at the highest level | A jointed rig: planted-foot walk, curved tapered limbs, fists, shoes, blinks, expressions that change on the beat. Tank top, chain, earrings, sagging jeans, a cigarette with a drag cycle and smoke; hat, shirt and boots; suit, tie and briefcase. |
| Stickmen should look like the reference | Big white head with a bold outline and a face, solid black body, fists, oval shoes (`brand/stickman-style-reference.png`). |
| Extremely visual, extremely psychological | Brackets and tags lock onto the stranger (TANK TOP, PANTS LOW, BLACK, THREAT / SUIT, CLEAN SHAVEN, WHITE, SAFE). His shadow looms as the prediction while he just walks. The TV figure hangs on strings, then so does the boy. Payoff: the two men walk the one line toward each other, pass, nod; nobody crosses; each step leaves an amber mark. |
| Text masking | Card titles fill the wall behind the figure. PREDICTION., CULTIVATION and A TRAFFIC STOP are windows with picture inside the letters. |

## The traffic stop's sound (added after v2's first pass)

Jason asked for the driver's music to feel real and deep, naming Bloodhound Q50. That artist's recording is **not** in the film:
it is copyrighted, there was no licensed source, and embedding it is what gets a post muted or removed. What is there instead:

- **An original beat** written in `src/mix.py` (`trap_beat`): sliding 808s, a half-time clap, rolling hats, a dark bell line. It is not a recreation of any song.
- **Car and distance.** Heard from the cruiser it is mostly sub, with the trunk and panels rattling on every 808 and almost no highs.
- **Perspective.** The sound follows whose head the picture is in. Officer: music muffled and ahead, his radio and light-bar relay crisp. Driver: the beat is full and loud for a moment, he turns it down, and the police radio becomes the muffled thing behind him.
- **A slot for a real track.** Put a song Jason owns or has licensed at `audio/licensed/car_music.wav` (or .flac/.mp3/.m4a) and the mix uses it automatically, with the same muffling and perspective. That folder is never committed.

## Measurements (v2)

| Check | Result | Bar |
|---|---|---|
| Frame rate and count | 60/1; 27,784 frames = 463.07 s x 60, both masters | exact |
| Loudness | −13.8 LUFS masters; −13.7 on the four cuts | −14 ± 0.5 |
| True peak in the MP4 | −5.2 dBTP masters; −5.4 / −5.5 cuts | ≤ −4 |
| Speech through the new mix | 98.9% word match, mix vs voice-only | ≥ 98% |
| Narration accuracy | 98.2% of words confirmed by the recognizer; the six weakest paragraphs were read back and are word-accurate | |
| Voice vs world | background 11.6 dB under the voice while he speaks (10th percentile 7.8), 5.3 dB under in the pauses | ≥ 12 dB target while speaking |
| Repeated frames | 0 of 3,600 sampled | none |

The voice-over-background figure is 0.4 dB short of the 12 dB target on the median, and the tenth percentile is lower still. The recognizer still gets 98.9% of words, so speech holds, but if any passage feels crowded, `FLOOR` in `src/mix.py` is the one number to raise.

New voice against the old, measured on the full read: pitch range 73 Hz vs 56 Hz, level range 11.3 dB vs 9.9 dB, median pitch 140 Hz vs 123 Hz. It is more animated and a little higher. Whether it sounds right is Jason's call; nobody listened to it during the build.

## What changed from the original brief in v2 (Jason's direction)

- Faces: the stick figures have cartoon faces now. The brief's "no faces" rule was about not casting a real-looking person as a stereotype; stick faces do not do that.
- Palette: the characters carry colour (denim, gold, Jason's green suit). The film is no longer strictly black, white and amber.
- Cuts: none left, including the hard cuts the brief asked for on the three character cards.
- Sound: the brief's "no whooshes, no risers" is superseded. Titles have impacts and scene changes have air.
- The bed no longer drops out completely for the observer: the score does, the floor tone stays.
- On the cards the figure's body covers a letter of each title (the A in BLACK, the E in MEXICAN, the HI in WHITE). That is the text-behind-subject look; titles can be shifted so he stands in a word gap if every letter must show.

## Still open

- **No Higgsfield output.** Nothing changed: 0 credits, and the free trial cannot be spent from Claude Code. Everything on screen and in the mix is made in code. Higgsfield's sound-effects model would give recorded-quality sirens and ambience; the current ones are synthesized.
- **The narrator is still not Jason.** `src/narrate.py align --wav jason.wav` re-times the film to his own read.
- **Runtime 7:43** against the brief's ~5:30. The script was not cut.
- **The OLACEO mark and the avatar** were traced or cut from screenshots. Send the original logo file and a transparent PNG of the character for exact geometry and edges.
- **Thumbnails** are all-caps now but do not yet carry the character or the new stick style.
- **Not posted.** Promotion kit times are updated for v2.

---

# v1 report (2026-11-10)

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
| Loudness | −14.0 LUFS on both masters and the traffic-stop cuts; −13.9 on the code-switching cuts | −14 LUFS |
| True peak (in the MP4, after AAC) | −5.3 dBTP masters, −5.5 and −5.4 on the cuts | ≤ −4 dBTP |
| Speech through the mix | 98.8% word match, mix vs voice-only (`whisper_check.py`, 1 run) | ≥ 98% |
| Caption / card timing source | 98.7% of words matched by the aligner; the rest interpolated between neighbours | |
| Smoothness (`smoothness_check.py`, eight 30 s samples) | jitter 0.08–0.34: pass. dup_ratio 0.02–0.15: tool verdict CHECK | dup ≤ 0.02, jitter ≤ 0.35 |
| Repeated frames (frame hashes, six 20 s samples, both formats) | 0 of 7,200: every frame is distinct | none |

The smoothness tool's duplicate count does not pass its bar, and the reason is measurable: it shrinks each frame to 180x320 grey
and calls a frame a duplicate when it differs from the last by under 0.15 grey levels. Slow drift on a near-black field sits
under that line. Hashing the full-resolution frames finds no repeats, so nothing is held or dropped. Jason's eye is the real
check: if the slow holds read as frozen on a phone, raise the drift amount in `src/film.py` (`drift`, 3.5% now).

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
