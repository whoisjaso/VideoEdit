# One-shape UI morph ("Just Post") — Jason's brief, 2026-10-09
One element, never cut: Post button → loader → check → Dynamic Island → notification → comment card (swipe-to-delete) → Apple Pay → "Care what others think" toggle (drag past max, rubber stretch, flips off on the beat) → the knob becomes the liquid tab indicator → chart draws itself + hover tooltip → ⌘K, type "who's talking" → one row "every single person that talks · broke" → toast "They're broke." → back to Post. 120 BPM, 7 bars, 28 beats, 14 s, loops.

**Engine rules (morph.html):**
- Everything is computed from time inside `seek(t)`; no CSS transitions, no timers, no stored state.
- Springs are closed-form step responses. A value that changes target many times is the sum of one spring per change (`track()`).
- The toggle knob and the tab indicator are ONE element. The two edges ride different springs, so the leading edge stretches ahead of the trailing one.
- Drags are direct manipulation: while held, the value comes from the cursor position (swipe, knob). On release it springs from wherever it was.
- Text inside a morphing container has its own enter/exit window (`WIN`) with a blur, so swaps never overlap.
- Loop check: frame 0 vs t=13.999 must match (mean pixel difference < 0.01). Every spring started near the end must be stiff enough to settle before 14 s, the camera included.

**Pipeline:**
```
python3 bpm.py music/*.mp3            # tempo of candidate tracks (numpy, spectral-flux autocorrelation)
python3 grid.py track.mp3             # exact period, phase, downbeats -> pick a 14 s window starting on a downbeat
node render.js stills beats <t...>    # one frame per beat -> QA sheet before the full render
node render.js full sub 6             # 60 fps x 4 subframes (180° shutter) with 6 parallel pages
ffmpeg -framerate 240 -i sub/s%05d.png -vf "tmix=frames=4,select='eq(mod(n\,4)\,3)',setpts=N/(60*TB)" -r 60 ...
python3 mixmorph.py track.mp3         # every UI sound placed by its measured peak; fx_only.wav + with_music.wav at -14 LUFS
```
Song used: Mixkit track #802 (Mixkit Stock Music Free License, free for commercial use), measured at 120.0 BPM, window 8.468-22.468 s.
