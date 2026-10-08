# MOTION-GRAPHICS QUALITY BAR: reel r05 (Jason, 2026-10-08: "this is the quality I expect for motion graphics")
Source: Mohamed Ahmed, instagram.com/p/DeH8OIzMton (92s; a laptop screen filmed while it plays motion graphics that Claude wrote as code). Contact sheet: `ref-sheets/r05.jpg`. Every motion graphic we ship is judged against this. If a beat looks plainer than this, it isn't done.

## 1. One world, held for the whole video
- **Stage:** deep navy (#141a3c → #1d2554 radial), a **blueprint grid** (fine 1px lines at ~8% white plus a stronger line every 5th cell), soft **bloom/glow** on anything bright, a vignette, light film grain. For "prompt/terminal" scenes the grid tilts into a **3D perspective floor** receding to a horizon.
- **Palette:** white text, **one hot accent: orange-red #FF5A2A** (with a warmer #FFB347 for gradients/glow), dim blue-grey for secondary lines. Nothing else.
- **Micro-type everywhere** (the "expensive" detail): tiny monospace labels on every panel: `fig. 1 — the model`, `t = 0.000`, `CONTEXT 012 / 200000`, `keyframes to move by hand: 0`, `REF 26-0002`, corner ticks, axis ticks. 14-18px, 40-60% opacity.

## 2. Kinetic headline (every spoken line)
- Top-left, bold grotesk (Inter/Archivo 800), white, 1-2 lines, set in place for the whole beat.
- **Spoken-word sweep:** words not yet said are dim **outline/ghost**; the word being said flashes **orange**, then settles to white. One or two **concept words stay orange** ("**code**", "**keyframes**", "**procedural**").
- Entrance per word: blur 10→0 + slight y-rise, ~5 frames, on the word's spoken frame.

## 3. Every sentence becomes a literal diagram (the core of the quality)
Build a small, labelled technical diagram that *does* what the sentence says, timed to the words:
| Sentence idea | Diagram (r05) |
|---|---|
| "without even opening X" | the X tool's UI (timeline panel with bars) appears, then two **orange strike lines draw corner to corner** with sparks at the tips |
| "not A → B → C" | **node chain**: labelled boxes linked by lines; a **glowing comet** travels the line; the middle node glitches / gets crossed out |
| "instead of controlling X" | X's signature UI (graph-editor curve); a red slash cuts it; it smears out |
| "you just tell it what you want" | **prompt box**: mono typewriter text + block cursor; key words get a **red underline sweep** as they're typed; a tiny token table ticks beside it |
| "3D elements" | **wireframe** cube / octahedron / sphere draw themselves (line-draw) and slowly rotate |
| "it doesn't do A directly" | `A ──✗──▶ output.mp4` (✗ sparks), then the route re-draws through a glowing `{ code }` node |
| "writes it as code" | split panel: **code on the left typing**, **live artboard on the right** building the result; floating labels pop around it ("The text, transitions, particles, positions, shapes, easing") + a formula `x(t) = x₀ + (x₁ − x₀)·e(t)` |
| "frame by frame → video" | a **film strip** of the artboard scrolls, then collapses into a ▶ player |
| process comparison | **paper form** scene (light): `FORM 2-B · PRODUCTION PIPELINE`, mono boxes with arrows, a **hand-drawn orange strikethrough** over the old process, the new process boxes typing in, a red **"NO KEYFRAMES"** stamp |
| a definition | **dictionary entry** in serif: `pro·ce·dur·al (adj.)` + numbered meanings, revealed letter by letter |
| "you can just ask it to change X" | live preview + **chat edits as code diffs** (− red / + green lines, "applied · keyframes touched: 0") that change the preview |
| "hundreds of keyframes" | a **particle field** of hundreds of tiny diamonds in rows, then it smears away |
| "from idea to result" | an **arc** draws from a glowing `idea` node to a result panel, with "without touching a timeline" on the axis |
| question / verdict | **questionnaire form** (FORM 9): checkboxes YES / NO / ✗ NOT REALLY, a checklist ticking in orange |

## 4. Punctuation beats
- **Full-screen word slam:** a solid orange (#FF6B35) frame, a huge black condensed heavy word, **one word per beat, hard cut every ~6-10 frames**: "AND" → "GETS" → "CRAZY." (a tiny timecode in the corner). Use 1-2 times per video on the hype line.
- **Finale title:** a two-line giant headline with heavy bloom: line 1 white, line 2 orange ("PRETTY / INSANE.").

## 5. Motion language
- **Light is the connector:** comets/sparks travel along every line that links two things; elements "light up" when the spark arrives.
- **Line-draw everything:** boxes, arcs, wireframes, underlines draw on (stroke-dashoffset), never just appear.
- **Camera always moving:** a slow dolly/zoom on every scene; scene changes **push through** (zoom + motion blur) or **RGB-split glitch smear** (3-6 frames).
- Scene length 2-4s, cut on the sentence boundary; inside a scene, a new sub-element every ~0.5-1s, each on a spoken word.

## 6. Sound for this style (from the library)
Typewriter / `pack5.typing_2` per typed word in prompts · `ui.data_loading` under code typing · `pack6.blade` on strike lines · `pack5.sparkle` / `pack3.shine` when a comet arrives · `pack6.impact_1` on slams (one per word) · `pack5.deep_whoosh` on push-through transitions · `ui.glitch_transition` on RGB smears. All via `<Hit>` (lands on the frame).

## 7. Self-check before shipping a motion-graphics beat
1. Is it in the one world (navy grid, bloom, one accent, micro-labels)?
2. Does the diagram literally *do* what the sentence says?
3. Does every sub-element arrive on a spoken word, with a sound?
4. Is something drawing, travelling or moving on every frame?
5. Would it look at home in r05? If not, it's not done.
