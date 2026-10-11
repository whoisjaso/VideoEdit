# The teardown: Premiere Pro, After Effects and Blender, rebuilt for an agent

Kairos started from one question: if you strip Premiere Pro down to what an AI editor actually
needs, what is left? This document is that teardown. Every row maps a feature of a professional
tool to the agent primitive that replaces it, and says what was cut on purpose.

## How it was done (and why not by decompiling)

The brief was to run [REA](https://github.com/morluto/rea) ("Reverse Engineer Anything") on Premiere.
REA is an MCP server that inspects binaries (through Hopper, Ghidra or IDA), Electron/JS apps, .NET
assemblies and websites, and builds an evidence trail for how a feature works. Its method has four
steps: name the feature, gather evidence of its behaviour, reduce it to a primitive, then rebuild it.

That method is what this document applies. Running REA on Premiere's actual binaries wasn't
possible or useful here, for three reasons:
- Premiere is a native Windows/macOS application, and Kairos is built in a Linux container where
  Premiere can't be installed.
- Adobe's licence forbids decompiling it, and Kairos is meant to be open source. A clean-room
  design from documented behaviour is the safe foundation.
- The value is in *what each feature does for an edit*, which is fully observable and documented.
  The decompiled internals of Adobe's C++ renderer wouldn't change one design decision.

Blender is open source with a complete Python API, so there was nothing to reverse: Kairos drives
Blender directly. [EffectCraft](https://github.com/storytold/effectcraft) (an open-source After
Effects rebuild in Rust) was the third reference. Its JSON project format, its AE keyframe semantics
and its "every command over MCP/CLI" design all carried over.

## Premiere Pro → Kairos

| Premiere feature | What it does for an edit | Kairos primitive | Where |
|---|---|---|---|
| Project panel, media import | Holds sources | `project.create`, resumable chunked upload, link/path import | `project.py`, `server.py` |
| Proxies | Fast scrubbing of huge files | Fast-seek per segment, so the source is never re-encoded. Analysis audio is 16 kHz mono | `media.py`, `render.py` |
| Sequence / timeline | Ordered clips on tracks | **EditGraph** `Timeline`: segments (V1/A1), captions, graphics (V2+), sfx (A2+), markers | `timeline.py` |
| Razor, ripple delete, trim | Remove ranges, close the gap | `cut(out_start, out_end)`: a ripple delete that shifts every later event | `mcp_server.py` |
| Speed/Duration, Time Remapping | Slow-mo | `Segment.speed` + `pitch_drop` (the curse-word punchline) | `render.py` |
| Motion > Scale/Position keyframes | Punch-ins, pushes | `Segment.zoom` keyframes with AE easing (linear, ease, ease in/out, hold, overshoot) | `render.py` |
| Auto Reframe | 16:9 → 9:16 around the subject | Face-centre crop (`crop_x`), median over the range | `media.face_center_x` |
| Speech to Text, text-based editing | Edit by transcript | Word-timed transcript; moments and edits are addressed by spoken words | `transcribe.py`, `moments.py` |
| Captions track | Burned-in subtitles | Word-by-word pages, keyword colors by meaning, spring pop, keyword slam | `ass.py` |
| Essential Graphics, MOGRTs | Titles, lower thirds | `Graphic` kinds: title, popup, counter, lower_third, cta, image, blender | `ass.py`, `blender.py` |
| Lumetri Color | Grade | Looks with intensity, `.cube` LUTs, accent-color hold, reference color match | `grade.py` |
| Comparison View / Color Match | Match a shot to a reference | Per-channel mean/contrast transfer from a still | `grade.match` |
| Essential Sound, loudness | Mix to platform loudness | SFX bus under the voice, `loudnorm` to -14 LUFS, limiter | `render.py` |
| Enhance Speech | Clean dialogue | The skill's `voice_enhance.py` (DeepFilterNet → EQ → comp), used in the 8.3 recipe | skill |
| Scene Edit Detection | Find cuts in a source | `scdet` scene cuts | `media.scene_cuts` |
| Markers | Notes | `Marker`, exported to Premiere as sequence markers | `timeline.py`, `export.py` |
| Media Encoder / render queue | Export | Preview (540×960, fast) and final (1080×1920) renders, backgrounded | `render.py`, `server.py` |
| XML / EDL interchange | Hand-off between NLEs | FCP7 XML that Premiere imports, plus SRT | `export.py` |

**Cut on purpose:** multicam, nested sequences, adjustment layers, audio track mixer automation,
dynamic link, Productions, Morph Cut, multi-format delivery. None of them change a short-form edit
an agent makes, and every one adds surface an agent would have to learn.

## After Effects (via EffectCraft) → Kairos

| AE / EffectCraft idea | Kairos |
|---|---|
| Keyframe interpolation (linear, Bezier, hold, auto) | `Keyframe.ease`: linear, ease, ease_in, ease_out, hold, overshoot |
| `wiggle()` expression | `Segment.shake`: a decaying, deterministic two-frequency wiggle, placed on bass hits and reveal stings |
| Versioned JSON project (`.ecproj`) that diffs in git | `Timeline` carries `"schema": "kairos.timeline/1"`, one JSON file per clip |
| MCP server + CLI exposing every command | `python -m kairos mcp` (28 tools) and `python -m kairos run` |
| Shape and text layers with spring animation | ASS vector shapes (rounded panels) + `\t` transforms for pops and slams |
| Lottie import/export | Roadmap: Lottie graphics as a `Graphic` kind |

## Blender → Kairos

| Blender | Use in Kairos |
|---|---|
| Text objects with extrude and bevel | `title3d`: gold metal hero word, camera push-in, three-point studio light |
| Frame-change handlers | `counter`: a number rolling up in 3D (money, stats) |
| EEVEE, film transparency, ProRes 4444 | Transparent `.mov` overlaid like any graphic |
| `blender -b -P script.py` | Headless and scriptable. Without Blender installed, the script is still written for you to run |

Not used: Blender's Video Sequence Editor (the EditGraph replaces it) and the compositor (`grade.py` replaces it).

## Why an agent-native editor looks like this

1. **Everything is addressable by words.** Agents think in transcript, not frames. Every edit is
   placed from a spoken word, and only the renderer turns that into frames.
2. **Every effect carries its reason.** `SfxCue.why` names the playbook rule that placed it, so an
   agent can audit an edit and a person can see why a sound is there.
3. **One JSON document per clip.** An agent can read it, patch it, validate it and diff it. The
   renderer is a pure function of that document plus the source file.
4. **Feedback is a first-class input.** Scores and notes change bounded style parameters and leave a
   written lesson that steers the next edit and the next video's moment picking.
5. **The 30 MB wall disappears.** Video never travels through a chat. It goes to Kairos (chunked,
   resumable, any size) and the agent works on it through MCP.
