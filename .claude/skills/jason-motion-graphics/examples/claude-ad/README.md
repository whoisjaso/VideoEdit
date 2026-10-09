# Claude spec ad: "Every masterpiece started as a thought." (15 s, 1080×1920, 60 fps)
Jason's brief (2026-10-09): a fast-paced Claude ad, light mode, an art reimagine, paint on top of the images, perfect morphs, ends on the Claude logo.

**Concept:** public-domain masterpieces from the Met, painted over with Claude's clay-orange pen and spark. Black serif type on pure white (no beige, no eyebrow labels).

**Shots (120 BPM; the music's drop lands on 4.0):**
| t | Shot |
|---|---|
| 0.0 | The spark draws itself |
| 0.5 | Its rays open into a marble head |
| 1.0 | "Every / masterpiece" |
| 2.0 | Card → circle + pen halo, "started as" |
| 3.0 | "a thought." + the spark pops above the head |
| 3.5 | Dive into the spark |
| 4.0 | DROP: the orange collapses into a collage tile; Vermeer / Rembrandt / Aristotle slam in; "think → write → paint → build"; the tiles re-size on the beat; pen marks |
| 6.0 | Hokusai takes the frame, the pen traces the crest |
| 6.45 | It becomes the front card of a 3D carousel; one turn; "code → learn" |
| 8.0 | Van Gogh grows from the front card; match cuts every half-beat, each face landing inside one fixed orange ring |
| 10.0 | Michelangelo's red-chalk study; "What's / yours?"; the pen finishes the study |
| 12.0 | A ring of 12 works |
| 12.75 | Their thumbnails morph into rays |
| 13.5 | The Claude spark turns once in 3D (an extruded stack) |
| 14.05 | "Claude" writes in, centred lockup |

**Engine:** same rules as `../../engine` (pure `seek(t)`, springs, 4-subframe motion blur). Extras:
- `word()`: morphing text; letters that stay, stay; the rest blur out and rise in.
- `stroke()`: pen marks that draw on and lift off.
- `place()`: an exact focal-point crop, so match cuts land faces on the same spot.
- A spark-shaped clipPath mask.
- Exact carousel front-card maths (`FRONT`), so the flat → 3D hand-offs are seamless.

**Build:** put the images in `img/` (see CREDITS.md / metpull.py), then:
```
node render.js stills st <times>
node render.js full sub 6
ffmpeg -framerate 240 -i sub/s%05d.png -vf "tmix=frames=4,select='eq(mod(n\,4)\,3)',setpts=N/(60*TB),format=yuv420p" -r 60 -c:v libx264 -crf 16 video.mp4
python3 mixad.py music/623.mp3
```
Then mux the video with `ad_music.wav` and with `ad_fx.wav`.
