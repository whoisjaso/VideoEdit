# File-naming manifest (spec §16 item 20)

Pattern: `STP-LWQ-M-<CUT>-<ASPECT>-<RES>-<A4>-<HP|SPK>.<ext>`. STP = Stop Thinking Poor, LWQ = Lead With Questions,
M = men's version, HP = headphone (binaural) mix, SPK = speaker (isochronic) mix.

## Video (`renders/lead-with-questions/`)
| File | What | Audio |
|---|---|---|
| STP-LWQ-M-NIGHT-16x9-1080-432-HP.mp4 | Night master, YouTube | 432 headphone |
| STP-LWQ-M-NIGHT-9x16-1080-432-SPK.mp4 | Night vertical, full length | 432 speaker |
| STP-LWQ-M-MORNING-16x9-1080-432-HP.mp4 | Morning master, YouTube | 432 headphone |
| STP-LWQ-M-MORNING-9x16-1080-432-SPK.mp4 | Morning vertical, full length | 432 speaker |
| STP-LWQ-M-TEASER-9x16-1080-432-SPK.mp4 | 60 s teaser (M3 + The Lot) | 432 speaker |

## Audio only (`renders/lead-with-questions/audio/`)
`STP-LWQ-M-{NIGHT,MORNING}-{432,440}-{HP,SPK}.{mp3,m4a}`: 8 mixes × 2 formats. MP3 is 320 kbps CBR in plain stereo;
M4A is AAC 256 kbps. 432 is the default and 440 the alternate. The WAV 48/24 masters with the same names rebuild with
`lwq_audio.py`; they aren't committed (0.2–0.5 GB each).

## Sound files (`projects/lead-with-questions/deliverables/audio/`)
`question_tone_{night,morning}_{432,440}.wav`, `singing_bowl_F_{432,440}.wav`, `bell_D_{432,440}.wav`

## Paper (`projects/lead-with-questions/deliverables/`)
| File | §16 item |
|---|---|
| script-{night,morning}-locked-tuned.md + PRODUCTION-NOTES.md §1 (change log) | 1 |
| script-{night,morning}-annotated.md | 2 |
| tts-jobs-{night,morning}.jsonl | 3 |
| cuesheet-{night,morning}.csv / .md | 4 |
| captions-{night,morning}.srt | 5 |
| PRODUCTION-NOTES.md §6 | 6 |
| lwq_audio.py `binaural()` / `isochronic()` + PRODUCTION-NOTES §7–8 | 7–8 |
| audio/question_tone_*.wav + PRODUCTION-NOTES §9 | 9 |
| music-*.mid + PRODUCTION-NOTES §10 | 10 |
| PRODUCTION-NOTES §11 | 11 |
| PRODUCTION-NOTES §12 | 12 |
| renders/lead-with-questions/audio/* | 13 |
| LOUDNESS-REPORT.md | 14 |
| lwq_visual.py (V1–V8, CONFIG at the top) | 15 |
| renders/lead-with-questions/*.mp4 | 16 |
| PHOTOSENSITIVITY.md | 17 |
| ../upload/thumbnail-{night,morning}-{16x9,9x16}.jpg | 18 |
| ../upload/youtube-lead-with-questions.md | 19 |
| MANIFEST.md (this file) | 20 |
| QA-REPORT.md | 21 |
