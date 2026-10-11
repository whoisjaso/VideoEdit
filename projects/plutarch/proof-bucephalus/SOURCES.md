# Bucephalus proof: sources and licences
All the media is public domain or CC0. The narration is Kokoro TTS (Apache-2.0), voices bm_george and bm_fable.

**Plates.** Metropolitan Museum Open Access (CC0): 337380, 341836, 397661, 410826, 410807, 670266, 355663.

**Score.** Musopen recordings, Public Domain Mark (archive.org `MusopenCollectionAsFlac`):
| Timeline | Recording |
|---|---|
| 0–79 s | Brahms, Symphony No. 1 in C minor, I (Un poco sostenuto), from 0:00 |
| 84.6–130.8 s | Grieg, *Peer Gynt* Suite No. 1, I "Morning", from 0:24. The climax lands on "and you let him run" |
| 130.6–181.6 s | Brahms, Symphony No. 3, III (Poco allegretto), from 0:00 |

**Field recordings.** archive.org, CC0 1.0:
- `horse-sound-effects`: neighs, whinnies, snorts, gallops, hooves, breathing.
- `SSE_Library_CROWDS`: men talking, a group laughing, men cheering.
- `SSE_Library_AMBIENCE`: murmur outside a palace, crunchy dirt footsteps.
- `SSE_Library_WIND`: prairie wind.

**Rebuild.**
1. `python3 world.py` makes `music.wav` and `amb.wav` from `../pd/`.
2. `mix_talk.py` with `cues_v2.json`.
3. Run the amix + loudnorm step (see the journal).
