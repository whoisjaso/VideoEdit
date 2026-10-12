# Motion-graphics brief template (from Jason's 2026-10-09 brief, generalized)
Fill these sections for any standalone piece. Jason's original "one shape" brief is the reference example.

```
<inputs>
8-12 states the element becomes · pure B/W or one accent (gold/green/red = meaning) · a royalty-free song ~120 BPM (Mixkit = free commercial use)
</inputs>

<direction>
Dribbble-level UI motion. One element, never cut: every state is the same element morphing size, radius and colour while its content swaps with a short blur.
A cursor drives every change with real clicks and drags. Light warm-gray canvas (#E8E5E0), black/white components, Inter Variable.
Springs everywhere, a tiny overshoot at most. The camera zooms so each state fills the frame. The last frame = the first frame (loop).
Banned: bouncy easing, particle bursts, glows, gradients on UI chrome, mismatched icon strokes, dead time, template looks.
</direction>

<structure>
BPM, bars (7 bars @120 = 28 beats = 14 s), one event per beat, written as a bar × beat table. The story = Jason's premise.
</structure>

<build>
pure seek(t) · closed-form springs summed per change · two-edge springs on stretchy parts · direct-manipulation drags ·
numpy beat grid, start on a downbeat · SFX by measured peak · Playwright 4 subframes/frame → ffmpeg tmix → 60 fps ·
one still per beat before the full render
</build>

<gotchas>
no will-change on camera-scaled things (blurry text) · swapping text needs its own enter/exit timing · last frame identical to the first (cursor position + speed)
</gotchas>
```

**Our context, always:**
- Vertical 1080×1920.
- The story is Jason's message (e.g. "Just Post": haters are broke, stop caring, post).
- Only his words or neutral UI text on screen.
- Two audio versions (music / SFX-only).
