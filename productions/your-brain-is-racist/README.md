# Your brain is racist. So is mine.

One narrated motion-graphic film for olaceo, in 16:9 and 9:16. Start with `REPORT.md`.

| What | Where |
|---|---|
| Masters and cuts (Git LFS) | `../../renders/your-brain-is-racist-*-v2.mp4` (v1 kept for comparison) |
| Narration track, final mix | `audio/narration.flac`, `audio/master_mix.flac` |
| Captions | `captions/your-brain-is-racist.en.srt` |
| Thumbnails | `thumbnails/` (three designs, 1280x720 and 1080x1350) |
| Promotion kit | `promo/promotion-kit.md` |
| Narration as recorded | `narration-as-recorded.txt`, source of truth `src/script.py` |
| Research behind each claim | `SOURCES.md` |
| Higgsfield prompt list (not run) | `higgsfield-plates.md` |

## Rebuild

Needs Python 3.10+, ffmpeg, Inter and JetBrains Mono installed, and `pip install skia-python numpy scipy soundfile faster-whisper kokoro-onnx`.

```bash
python3 src/narrate.py build_cb                                # expressive narrator (Chatterbox) -> audio/narration_dry.wav + timeline.json
                                                                # then ease the tempo 6%: see REPORT.md
python3 src/film.py cues                                        # scene clock -> cues.json, scenes.json, captions/*.srt
src/master.sh                                                   # sound design + master -> audio/master_mix.wav
src/render.sh h /tmp/work && src/render.sh v /tmp/work          # picture, 60 fps, both aspects
src/finish.sh /tmp/work                                         # mux, cuts, QA numbers
python3 src/thumbs.py
```

## Put Jason's voice on it

Record the script in `narration-as-recorded.txt` as one continuous read and save it as a WAV. Leave about four seconds
of silence before the last line ("Now you know whose job it is…"): the hook card returns in that gap. Then:

```bash
python3 src/narrate.py align --wav /path/to/jason.wav    # his word times -> timeline.json, his voice -> audio/narration_dry.wav
```

and rerun the steps above from `film.py cues`. Every cut, card, caption and sound cue follows the words, so the film
re-times itself to his pace. If a pause needs to be longer somewhere, add it to `EXTRA` in `src/timing.py` (seconds of
silence after a line id) instead of re-recording.
