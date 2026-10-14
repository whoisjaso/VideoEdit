# Lead With Questions (Stop Thinking Poor), men's version

A sleep/wake programming pair built from `deliverables/SPEC-PROMPT-MEN.md`. **Night Install** runs 28:00 and ends in
silence. **Morning Run** runs 10:30 and ends with a count-up to eyes open. The scripts in `script/` are locked word for
word from the spec; only pause lengths are tuned.

```bash
python projects/lead-with-questions/lwq_timeline.py night morning   # voices + timing  -> /tmp/lwq/<cut>/timeline.json
python projects/lead-with-questions/lwq_audio.py night               # stems + 4 masters (432/440 x HP/SPK)
python projects/lead-with-questions/lwq_audio.py morning
python projects/lead-with-questions/lwq_visual.py night 16x9 --render /tmp/lwq/night/video-16x9.mp4   # x4 (cut x aspect)
python projects/lead-with-questions/lwq_finish.py                    # mp3/m4a, muxes, teaser, share copies
python projects/lead-with-questions/lwq_deliver.py                   # scripts, TTS jobs, cue sheets, SRT, MIDI
python projects/lead-with-questions/make_thumbnails.py
python projects/lead-with-questions/lwq_qa.py                        # the 16 QA gates -> deliverables/QA-REPORT.md
```

Run the heavy steps one at a time: the container's memory limit kills parallel audio and video jobs.
Start with `deliverables/MANIFEST.md`; `deliverables/PRODUCTION-NOTES.md` has the change log and every [DEFAULT].
