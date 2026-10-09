> Craft reference adapted (summarised in our own words) from the MIT-licensed `cinetic` skill by Leon Lin (github.com/Leonxlnx/cinetic, Copyright (c) 2026 Leonxlnx). The numbers are his measured defaults; the **[us]** notes map them onto our seek(t) HTML pipeline.

# cinetic: craft digest for 9:16 / 60 fps code-built ads

A summary of the MIT `cinetic` skill, in my own words, for our pipeline: a 1080x1920, 60 fps, pure seek(t) HTML engine rendered with Playwright, with 4 blended sub-frames. "f" means a 60 fps frame. The skill measures speeds as px/f at 1080p, and that carries over to a 1080-wide vertical frame. The skill treats every number as a proven default, not a law. Anything marked **[us]** is my note on how a rule applies to our setup.

---

## 0. The bar, and the five laws

- **The target is a film people watch twice.** It has one idea that only this product owns, it is told in pictures, and every frame looks chosen. Substance comes before polish: show the clever, specific thing the product does that a simpler product wouldn't.
- **The five laws:**
  1. **One idea, specific to the product.** You can say it in one sentence.
  2. **One story device.** One object travels through every shot and never blinks out.
  3. **One accent with one meaning.** It covers 8% of pixels or less and floods the frame at most once.
  4. **One house motion system.** A few named curves, and every frame number comes from one timeline file.
  5. **Verify by measurement.** You only know the film works once you have rendered it and measured the pixels and the audio.
- **The brand wins over the skill's taste bans.** If the brand supplies something the bans would catch (Claude's terracotta/orange, a warm paper, a serif wordmark), it stays. Write it down as a brand-supplied exception so critics don't flag it. **[us]** For a Claude ad, record the brand orange, the cream paper and any serif wordmark as exceptions. Every other ban still applies.

## 1. Concept and story

**A concept is three sentences, written before any pixel:**
- **Idea:** what the viewer should believe afterwards, in 8 words or fewer.
- **Device:** the one thing that carries the idea through every shot.
- **Grammar:** the rule the film's form obeys, e.g. "everything fits with no gaps; open and close on the same tick". Grammar is what makes a film ownable. Without it, even a good idea looks like everyone else's film.
- **What a concept is not:** a style ("bold kinetic minimal 3D"), a feature list, a mood, or a format.

**Take inventory before generating ideas:**
- what the name means or evokes; this often hands you the mark and the device;
- the non-obvious behaviour: finish "unlike the obvious version, it…";
- a before/after value sentence in the viewer's words;
- 10 verbs, from literal to abstract;
- the product's own objects and their states;
- the one number that changes (412 → 1);
- the pain scene: time, place, and what is on screen at the worst moment;
- 5 category clichés, which are then banned for this film;
- the sound of the product's world.

**Three lenses, at least 3 raw ideas each.** The first idea in each lens is usually the cliché; the third is usually yours.
- **(a) The product's verb made literal**, built from the product's own objects, never clip art.
- **(b) The pain made visible** as a physical quantity (mass, count, noise) that grows until it breaks the frame. The turn then relieves that same quantity.
- **(c) A formal device:** a relay object, a bookend, one unbroken take, a container that becomes the product, a counter as the spine, split-sync, a rule of the frame, or a scale jump (the same object at 16 px and at full frame).
- **If all nine ideas are weak, try these prompts:** make the invisible visible; follow one unit through its life; show the absence; borrow a physical law; build the logo from the problem's pieces; constrain the film (no cuts, no words before halfway, three objects); do the opposite of the category.

**Kill tests.** A concept that fails ownership or deletion is out, however pretty it is.
- **Ownership:** swap in a competitor's logo. The film must stop working, and at least 2 owned props must remain.
- **Deletion:** remove the demo and the value must still read. Remove the value and the film must stop working; if it still works, it was a feature tour.
- **Muted:** the story reads from pictures alone.
- **Feature word:** a stranger watching muted would use the brief's own word for the feature.
- **Poster:** the last frame, as a still, says who made the film and what the product does.
- **One sentence:** saying the idea needs no "and" and no adjective.
- **Retell:** tomorrow the viewer describes an image, not a style.
- **Specificity:** the film is NOT equally true of a simpler product.
- **Truth:** every frame agrees with the story.

**Scoring and choosing:**
- Score the survivors 0–3 on ownership, muted clarity, device strength, surprise and buildability. Ownership must be at least 2; break ties toward buildability.
- Graft the single best element from each loser onto the winner.
- Write the logline as the film seen, in 15 words or fewer: device + what it does + turn + result.

**Generic props that fail ownership:** rocket, lightbulb, globe with arcs, up-and-right chart, a floating phone or laptop, a glowing orb or sparkle for AI, shield or padlock, puzzle pieces, gears, stopwatch, magnifier, confetti, handshake, bullseye.

**Device design:**
- **Where it comes from, in order of preference:** the product's own object with states → the name's meaning → the key number → a primitive of the mark → the accent colour → a sound (only as a partner to a visual device).
- **A bare dot or line is the lazy default.** Use one only if you give it behaviour only this product has. **[us]** A "travelling accent dot" qualifies only if the dot has a product meaning and changes state (ticks, fills, locks, counts). A dot that merely travels is a logo on a tour.
- **Properties:** one instance at a time; small enough to travel through any shot and able to fill the frame once; a state that changes; ideally it ends as the mark, or as a piece of it.
- **Path rules:**
  - Write the path as a chain of "becomes", with a named seam type per link.
  - Full opacity through every seam. Four missing frames were flagged as a mistake.
  - It changes role at a seam, never style: same size, colour and edge.
  - The eye is already where the device is at every cut.
  - One flood only, usually the turn.
  - Lock the target before the device lands on it.
- **Bookend:** open and close on the same image and sound with exactly one thing changed, e.g. 3:12 → 3:13.

**Beats:**
- **Hook:** inside the problem at frame 0, felt by 1 s, stated by 2 s.
- **Problem:** the pain escalates as a visible quantity.
- **Turn:** the biggest change so far, on a downbeat.
- **Proof:** cause → action → result, with the result held at least 36 f + 6 f per word.
- **Promise:** a callback to the hook's words.
- **Lockup:** the device becomes the mark.
- **Proportions for 30 s:** hook+problem about 20%, turn about 10%, proof 35–40%, promise about 15%, lockup and tail 15–20%.
- **Teaser of 15 s or less:** hook → turn → lockup, 6–10 words, with proof reduced to one glimpse.
- **[us]** "At 15 s, halve the 30 s budgets; don't compress the same film" means 4–5 story beats and about 8–17 words.

## 2. Timing grid

**One grid:**
- Every cue is a frame number computed from bar/beat/16th; none is typed by hand.
- The beat must be a whole number of frames, or the kick and picture drift up to 1 f apart.
- Whole-frame beats at 60 fps: 75 BPM = 48 f, 90 = 40, 100 = 36, **120 = 30 (the default; bar = 120 f = 2.0 s, 8th = 15 f, 16th = 7.5 f)**, 150 = 24, 180 = 20.
- `b(bar, beat, sub) = round(((bar-1)*4 + beat)*BEAT + sub*BEAT/4)`.
- **[us]** 15 s at 120 BPM is 7.5 bars. Use 7 bars + 60 f tail = 900 f, or 100 BPM (36 f beats, 144 f bars).

**Where events land:**

| Event | Lands on |
|---|---|
| Act or section change | a downbeat, with the music's own event (drop, stop, re-entry) |
| Cut inside a section | an 8th, with no sound of its own |
| A move's velocity peak (not its start) | a beat or an 8th; solve the start back from `peak()` |
| Batch of landings | 16ths, first item on the beat, a seeded 0–3 f spread |
| Waves, tile snaps | 32nds (3.75 f) |
| Payoff | the clap (`b(n,2)`); its consequence on the next kick |
| Designed freeze | ≤ 15 f, exactly on a silence |

**Hit-frame rules:**
- Start a picture change at `cue − 1`, because a tween's progress is 0 on its start frame.
- Pulses peak 2 f after their sound, which reads as cause and effect.
- Start springs at `beat − delayTo(cfg, thr)`: thr 0.5 for a pop-in, 0.92–1.0 for an impact.
- A tween's sound goes on its 97% frame, never its last frame.
- Audio leading picture by more than about 45 ms reads as "sound first". Move the picture, not the sound.

**Rolls and ripples:**
- An accelerating roll uses `land_k = start + (k/(N−1))^0.8 · span`. A decelerating schedule drains energy before the drop.
- Ripple delay is 1 f per 60 px of distance from the cause.
- Snap the landing to the grid, not the start.

**Holds:**
- Text that has resolved stays at least **36 f + 6 f/word** (1 word = 42 f, 3 = 54, 5 = 66). Unresolved text never exits.
- Nothing is static for more than **48 f**.
- One designed near-still hold per film of **60–96 f** on the key claim, under a music dropout, followed by the biggest move.
- A URL stays readable at least 1.7 s.
- The tail after the last event is at least 60 f.

**Density:**
- 45–60 discrete events per 30 s (**about 22–30 in 15 s**), so something visibly changes about every 0.5–0.7 s.
- One motion peak per bar, with 30–70 f of calm between peaks.
- The first 6 s are about 2× as dense as the middle.
- **Energy arc:** an early peak at 10–25%; one designed lull of 1–4 s at about 55–85%; the last and biggest peak at about **75–90%** (median 82%), on the music's re-entry; then a calm outro. A film whose last peak comes before 60% sags.
- **Shot length:** median 60–90 f (top-tier median 1.46 s); minimum 24 f, and only without text (shots under 0.45 s carry no copy); maximum 180 f in a cut-driven film. A continuous take may run 300–560 f if a beat lands inside it at least every 72 f.

**Hook norms (measured on top-tier films):**
- First visible change at a median of 0.10 s; nearly half change within 2 f.
- First readable word at about 0.4 s; first hard change at about 1.3 s; premise read by about 2 s.
- Product or name on screen by about 25% of the runtime.

**Repetition speeds up:**
- A second reveal runs about 40% faster (0.6×).
- Word stagger compresses through the film, from 24 f on the title to about 5 f mid-film.
- Ratchet gaps run 26, 14, 12, 8, 8, 4, 4 f.
- Reframe every third repeat.

## 3. Motion tokens

**Easing tokens (cubic-bezier):**

| Token | Bezier | Job |
|---|---|---|
| out | .16,1,.3,1 | arrivals, reveals, word entrances (90% of travel in about 40% of the time) |
| outSoft | .22,1,.36,1 | gentle and secondary settles |
| in | .7,0,.84,0 | implosions, hard snap-outs (too steep for ordinary exits) |
| exit | .55,.055,.675,.19 | exits into a cut: speed grows about ×1.14/f over the last 10–24 f |
| inOut | .87,0,.13,1 | whips, lockup slides, morphs |
| smooth | .65,0,.35,1 | fades (10–14 f), drifts, breath |
| ui | .4,0,.2,1 | small UI changes |
| cam | .48,.1,0,.9 | camera: slow start, peak at about 27%, long settle |
| glide | .47,.2,.15,1 | 150–350 px moves |
| rest | .45,0,.1,1 | moves that end at rest; chaining after another move |
| contact | .55,0,.9,.55 | accelerating into an impact |
| whip | .6,0,.15,1 | feature-to-feature whips, 24–30 f |
| dolly | .35,0,.65,1 | slow push through a hold |
| type | .5,1,.89,1 | eased typewriter character count |

Specialist tokens: split .33,0,.1,1 · close .55,0,.15,1 · pull .5,0,.12,1 · iris .4,0,.7,.92 (applied in log space) · shutter .2,.7,.2,1 · hop .35,0,.7,.85. The measured "large object move" curve is about .8,.05,.07,1.02 over 34–60 f.

**Springs (damping/stiffness/mass → overshoot, frames to 50% / 100%):**
- snap 18/260/0.7 → 6%, 5/10 f
- pop 11/180/0.6 → 14%
- land 14.5/200/1 → 15%
- micro 30/500/0.6 → 0.4%
- firm 24/140/1 → 0%, settles in 38 f
- soft 26/120/1 → 0%, settles in 41 f
- heavy 30/90/1.4 → 0%, settles in 56 f
- Named extras: impact 23/320/1 (7%, the upper limit), detent 24/380/0.6, check 12/220/0.5, tile 15/150/0.7, wordSlide 20/170/0.9 (clamped at the lock).

**Laws:**
- **About 3 easing characters per film** (typically out for arrivals, cam for the camera, in or exit for exits). Linear only for drift, data and luminance ramps.
- **Entrances decay, exits accelerate; only the camera eases both ways.** Never fade out on an expo-out curve: it pops 55% of the change in one frame. Fades run 10–14 f on smooth.
- **Damping:** use an ease or a critically damped spring (ζ ≥ 1). Overshoot of 1–7% is only for a true landing, **at most 2 per film**. Top-tier films measure 0% overshoot in about half of cases. No spring may oscillate more than once.
- **Clamp overshoot** wherever it can collide or drive geometry negative. Snap to rest when |1−s| < 0.01.
- **Duration grows with distance:** 0.35 s + 1.35 ms/px (camera clamped to 0.6–2.4 s), so 150 px = 33 f, 350 px = 49 f. The slowest move is at least 3× the fastest; top films reach about 10×.
- **Duration ladder (60 fps):**
  - popover 8–12 f; toggle 8–10 f; container birth 13 f; chip/button morph 16–20 f; button→panel 23 f;
  - modal 26 f; window/sheet 36–52 f; slow container expansion 62 f;
  - camera push/pull 56–108 f; inertial scroll 76 f.
- **Exit = the entrance reversed, about 30% shorter.**
- **Overlap:** a secondary move starts at 55–75% of the lead move (about 20 f into 60 f), so both settle within 2 f. Otherwise you get stall-then-lurch.
- **Interaction timing:** an interaction leads its effect by 1 f. Colour settles 20–40 f behind the motion that caused it.
- **Budget:** one hero motion plus at most 2 supporting ones. A fast/slow contrast of 10–30× inside a shot (e.g. a 60–70 px/f whip next to 0.3–0.6 px/f stillness).
- **Shape and contact:** shape (w/h/radius) settles 6 f before position. Contact squash is width ×1.08 and height ×0.90, back over 8 f, anchored at the contact edge.
- **Scale and zoom always in log space:** `exp(mix(ln a, ln b, t))`.
- **One settle constant per element class:** all type uses τ ≈ 13–16.5 f, i.e. 95% settled at 40–45 f.
- **Anticipation:** pull 2–4% the opposite way over 6–10 f on smooth, then start on a zero-slope curve. Use it once or twice per film.
- **Weighted moves:**
  - Lift and fly: lift 14 f on out (z 70–130 px), travel on inOut with an arc of sin(πt)·50 px, drop over the last 10 f on in.
  - Shadow of a lifted object: offset (0.1z, 0.22z), blur 3+0.06z, alpha 0.2−0.1·min(1, z/200).
- **hitPulse is the one envelope for every punch and tick:** a quarter-sine attack of 2 f, then exp decay τ 5 f, gone by 32 f.
  - Amplitudes: tick on a small dot +18–30%; whole-mark beat punch +1.5%; lock-in +2.5–3%; payoff camera punch +1.2% (attack 3, τ 7); word lock +1.8% (1, 4).
  - Never use a half-sine: it clunks at both ends and peaks 6–8 f late.
  - Repeating ticks take the max of their pulses; independent causes add.

**Staggers:**
- Statement words 6 f apart, 26 f each (headlines 9/28, quiet descriptors 5/24).
- Burst words 4 f; read-paced words 8–12 f; one word per beat 16–28 f; letters 2–3 f.
- Word exit at half the entry stagger, 16 f on in.
- Grids 4 f per column and 6 f per row; lists 15 f per row (an 8th); a dealt row of cards 5 f.
- A group arrives within 30 f in total. Human gaps run 7, 12, 18 f.
- **Order a stagger by importance, never by DOM order.**

## 4. Transitions catalogue

**Rules:**
- A seam is a designed match: something carries across (the device, a shape, a colour, a direction, a velocity).
- 6–8 seam types per film, each used at most twice. Velocity-matched cuts are exempt.
- One **signature move** derived from the mark, used 3 times: open, middle, close.
- No crossfades. The only blends allowed are 1–2 ghost frames at a motion peak. No dip through black (it costs about 25% luminance).
- **Banned presets:** glitch/RGB split, light leak, film burn, swirl, ripple, dreamy zoom, flash through white.
- **Mix in top films:** about 50% hard cuts, 18% camera moves, 8% morphs, 8% match cuts, 6% floods/wipes, 8% 1–2 f blends. They use 5–10 types; a few films have no visible hard cut at all.

**Seam laws:**
1. Both sides at rest, or the incoming shot starts at the outgoing velocity.
2. Accelerate out about ×1.1–1.2/f over 10–24 f, cut on the fastest frame, then enter at 20–45 px/f and decay ×0.89–0.94/f (τ about 12 f; out over 48–84 f).
3. Match every property across the cut: position, size, radius, colour, shadow, opacity, blur.
4. Show the rest pose once. Never on the last frame of one act AND the first frame of the next.
5. Place shared elements by the same method on both sides. A layout/transform mix shimmers 0.4 px.
6. Never crossfade two copies of one object. Morph one object, or swap its content at the arc apex (p > 0.5).

**Energy table:**
- Calm seams: 30–48 f, sine-like curves, 20–30 px of defocus.
- Medium seams: 18–30 f, glide/whip/ui, 8–15 px.
- High seams: 9–18 f, in/out/contact, 3–6 px.
- Match the seam's energy to the music at that point.

**The best seams, with recipes:**
- **Relay handoff.** The device's state is one function of absolute time, drawn by both shots, so the frames on either side of the cut are consecutive samples of one curve.
- **Velocity-matched cut (the workhorse).**
  - Exit on exit/in over 16–24 f, ending at 25–40 px/f (never above 60).
  - Entry at 30–55 px/f on frame 0 (1.0–1.5× the exit speed), then out over 45–90 f.
  - One screen direction per act.
  - Helpers: `exitSpeed = D·(ease(1)−ease(1−1/T))` and `entryDistance = v/(ease(1/T)−ease(0))`; e.g. 300 px over 24 f exits at 71.7 px/f.
- **Shape match cut.** Outgoing centre and size are recorded; the incoming matching shape sits within ±20 px at 0.57–1.3× the size. Outgoing shrinks 2–4% over its last 4 f on in. Incoming continues with k = lmix(0.57, 1, out over 18 f), no overshoot. Match colour, radius and stroke. Hold 12–30 f.
- **Scale-through cut (signature).** Both objects are centred on one anchor within ±30 px. Outgoing k goes 1 → 0.75 over 16–24 f on in (about −7.8%/f at the cut). Incoming k goes 1.8 → 1 over 30–40 f on out (about −8.4%/f), so the log-scale velocity is continuous. Mark-macro variant: k = 1+(S0−1)·0.84^f from 8–9×. Push variant: swell 1 → 1.22 into the cut, open at 0.8 → 1.
- **Container or shared-element morph.** 46 f on inOut. Each piece is a clip mask with the live next scene drawn inside it at its final transform; pieces overlap 2 px once joined (from about 35%). On the landing frame, swap to one unclipped layer with the identical transform. The Morph primitive: one rounded rect A → B over 40 f on inOut; content A out over the first 35%, content B in over the last 40%.
- **Iris or flood from the device / a glyph.**
  - Radius in log space: about ×1.25–1.29/f, 20 f to the farthest corner. A 14 px seed appears over 6 f and is held 6–10 f first.
  - Flood out: 18 f on out, starting at cue−1 so it is already opening on the drop frame. A flood that ends a shot runs on in.
  - Iris-in from 80× (e.g. 28 px → 2240 px) onto the dot by the first beat (30 f), on the iris curve.
  - A linear radius crawls, then snaps.
- **Implosion → silence → drop.** The world scales 1 → 0 and rotates 0 → −14° on in over 19 f, while the device grows ×1.25 (it never shrinks with the world). Then ≤ 15 f of true silence, then the drop on the downbeat.
- **Shutter collapse.** Height first over 16 f on shutter, starting at cue−1; then width over f13–26 on inOut into a line, and the line becomes the device.
- **Split on a seam.** The product opens along one of its real borders on split over 42 f (a rotateY −12° hinge at perspective 2400, sub-pixel clip insets), then swings shut on close onto the next act's frame 0.
- **Zoom-through.** Exit scale 1 → 1.2 with blur 0 → 10 px (type) or 18–20 px (full frame) on in over 12 f; entry 0.75 → 1 over 30 f on out. Blur goes on one wrapper only, and a full-frame blur uses a sharp/blurred-copy crossfade, never an animated `filter: blur()`.
- **Partial slide cut.** ±230 px with the same distance and duration both sides (e.g. 24 f). The exit is faded out by 25–30% of its travel.
- **Word waterfall.** Line A exits at half its stagger (3–4 f) over 16 f on in, rising 0.6× its entry offset; line B's first word starts once A's last word passes half its exit, on the beat. Only one line is ever readable.
- **Words become the mark.**
  - Underline (never strike-through) at 0.1 em, baseline + 0.07 em, drawn over 16 f on out.
  - It swells into a block (top = baseline − 0.8 em, height 1.04 em) over 12 f while the glyphs fade under it.
  - The blocks accelerate into the mark's pieces over 20 f on contact (shape settling 6 f early), land with the squash, and the device follows 5 f behind.
- **Polarity flip cut.** Mean luma changes by at least 150/255, on a downbeat, carried on a moving shape or a shape held at the same point (inverted, 1–2.5× its size). Optional ghost frames at 0.12 and 0.94. Wait 12–20 f before any small type after a flip to dark. At most 2 per film.
- **Motion-masked swap.** Swap content on the frame of a big secondary motion's peak (a background sweep over 20–24 f centred on the swap, or a card kick of rotateY 12°·hitPulse). Repeat no more than every 48–54 f.
- **Envelope-matched type cut.** A big line cuts to a smaller, longer line whose word gaps start spread so it matches the old width, then close over 36 f on outSoft while a shared 3–4 px/f drift continues.
- **Hide-the-cut tricks:**
  - Cut on the fastest frame.
  - Pass a foreground object through the frame at the camera's peak speed.
  - Leave one blank-ground frame after a hard cut.
  - Hide a 10× scale jump in one frame of horizontal blur.
  - Swap text on the frame of peak background velocity.
  - Whips leave the frame for about 12 f and re-enter at speed.

## 5. Camera

- **One world transform:**
  - Lay the scene out once and move it with one transform on one wrapper (`left:0; top:0; transform-origin:0 0; translate() scale()`).
  - A fractional left/top plus a transform snaps to whole pixels: 1 px stairs every 6–8 f on slow moves.
- **Anchor camera:** a shot is "world point (ax, ay) sits at screen point (sx, sy) at scale k". Blend anchors linearly and k in log space; the subject then travels a straight line at an even zoom rate. Lerping translate and scale separately makes the subject swing.
- **Modifiers multiplied into k:**
  - breath +2.5% across a hold, released by the next move;
  - dip: 1 − 0.18·sin²(πt) during a whip (the operator pulls back to find the next subject);
  - punch: 1 + 0.012·hitPulse(f−cue, 3, 7), one per payoff;
  - dolly: lmix(1, 1.2) on dolly for a logo or statement hold.
- **Holds stay alive:**
  - UI drift 0.5–1.5 px/f plus a 2–3%/s push (scale creep 0.04–0.07%/f).
  - Big display type drifts 1.5–3 px/f.
  - A statement grows ×1.03–1.05 through its hold.
  - Faster than about 9%/s reads as a move, not a hold.
  - A drift that starts at a seam eases in from rest: `(f − 20(1−e^(−f/20)))/300`.
- **Pushes and pulls:**
  - Push 1.5–3.1× over 30–70 f, peak 4–5% scale per frame (never over 10%).
  - Hero push 2–3× over 60–67 f on smooth.
  - Pull-backs 0.43–0.81× over 44–108 f.
  - Captions start in the last 25% of the move so the type and the settle land together.
  - Punch-ins are cuts: a wide of 20–64 f, then 2–2.3× on axis.
  - Every interaction gets a 3–5× close-up of 0.8–2.6 s. A wide of unreadable UI lasts at most about 1.7 s.
- **Speed profile is a U:** enter at 11–85 px/f, cruise at 1.5–8 px/f (≤ 3 under readable text), exit at 15–40 px/f into the cut.
- **Roll** is secondary action: −4° on a push swings back within about 25 f; up to +8° on pull-backs and −14° on whips. Never a fixed dutch angle. Roll ≤ 11°.
- **3D:**
  - Perspective 1800–2600 px. **[us]** On a 1080-wide frame, scale this to about 1000–1450, or use 3–4× the object's width.
  - One rotation axis per act. The same tilted-card angle three times reads as a template.
  - Roll goes OUTSIDE the tilt: `perspective() rotateZ(roll) rotateX(tilt)`, or the type shears into faux italics (about 18° was measured).
  - Total visible shear ≤ 7°.
  - Tilt live components with their own shadow and ground, never floating screenshots.
  - Chromium caps raster scale under perspective, so text goes soft. Lay out at shot scale with CSS `zoom: Z` and use camera `scale3d(k/Z, k/Z, 1/Z)`, switching Z only on a velocity-peak frame.
- **Parallax:** planes at 0.3× / 1.0× / 1.6× of the camera translation. Two planes is usual; three is the maximum. Overscan moving layers 5–8%.
- **Chained moves never stall:** overlap them by about 20 f (40 f for slow ones), with the second on a zero-slope curve (rest or smooth).
- **Rack focus:** never animate `filter: blur()` on a large layer, because Chromium steps it from sharp to soft in one frame. Crossfade a sharp copy with a constant 10–12 px blurred copy, both overscanned 80 px. Veil the defocused background at 80–85% behind type.
- **Framing:**
  - Clamp the camera so the product always covers the frame (no void bands at the edges).
  - Headroom ≥ 24 px at maximum punch.
  - Readable UI ≥ 22 px after camera scale. **[us]** ≥ 32 px in 9:16.

## 6. Copy and typography

**Budget:**
- A 30 s launch film aims for 15–25 words (cap 35).
- A teaser of 15–20 s gets 6–10 words.
- At most 5 words per line (about 24 characters) and 2 lines per shot. Only one statement is readable at a time.
- Viewers read about 3 words/s while watching. Measured dwell is about 0.4 s per word, with a floor of 0.5 s per card.
- The CTA gets at least as long per word as the claim before it.

**Voice:**
- Use the viewer's words at the moment of pain. Nouns, verbs and numbers; no praise adjectives.
- Present tense, active voice. The viewer's world is the subject, not the product.
- Sentence case with a period. No "!", no questions, no ellipses.
- **Six-test line check:** true on its paused frame · a competitor couldn't say it · ≤ 5 words · no praise adjective · sounds spoken · still true in a year.
- Write 15–20 candidate lines per slot.

**Callback copy:**
- Mechanisms: the same words with a new truth; a one-word flip; the digit; the user's own typed words; a grammar rhyme; tautology as proof.
- The payoff reuses at least one content word from the setup, lands on the loudest beat, and is never explained.
- One chain per film, plus at most one echo.

**Stock phrasing to cut:**
- Openers: Meet, Say hello to, Ready to…?, What if…?, Imagine…
- Claims: the future of, reimagined, next-gen, game-changing.
- Verbs: unlock, supercharge, streamline, elevate, empower, transform your, harness.
- Adjectives: seamless, effortless, powerful, smart, AI-powered, all-in-one.
- Nouns: workflow, productivity, solution, experience, journey.
- Structures: a feature name as a headline; "Plan. Track. Win." triplets.

**Type:**
- One family at 2 weights, plus an optional mono, shipped as local variable fonts.
- **Use the variable axis for exact weights** (e.g. 640 display / 450 text).
- **Never animate weight on text that reflows.** The one sanctioned weight move is a front sweeping 400 → 700 across a settled word, with each glyph's advance interpolated so the line stays centred.
- **One token per role.** Near-miss values (600/620/640; −0.04/−0.045) read as "almost matched".
- Tabular figures on anything that counts.
- **Tracking tightens with size:**
  - ≥ 160 px: −0.05 to −0.06 em, leading 0.95
  - 88–160 px: −0.04 to −0.05 em
  - 44–88 px: −0.015 to −0.03 em
  - 22–44 px: −0.01 to 0 em
  - all caps: +0.04 to +0.08 em
- **Kerning:**
  - Per-glyph animation must place glyphs at their kerned positions: `x_i = measure(prefix incl. i) − measure(glyph i)`.
  - Chromium's measured width includes trailing letter-spacing, so with negative tracking the last glyph overhangs by up to |track|×size (about 9 px at 176 px). Pad covering boxes by about 8 px.
  - Align ink, not boxes: side bearings can be 13 px at 176 px.
- **Scale at 9:16:**
  - statement 110–140 px, ≤ 3 words per line, ≤ 2 lines;
  - emphasis/payoff 1.3–1.5× the statement, fitted to the safe width;
  - slam fitted to about 83% of the width;
  - secondary/URL 60–72 px; UI ≥ 32 px.
  - At 16:9, statements are 88–128 px. Keep a headline:secondary ratio ≥ 2:1; a flat scale reads as a slide.
  - Hero words span 11–48% of frame height (median about 21%).
- **Contrast:** statements ≥ 7:1, secondary ≥ 3:1 at ≥ 44 px, small text ≥ 4.5:1.
- **Hierarchy from colour OR weight, not both.** Either one weight with active words white, inactive at about 30% luma and one accent word, or light vs semibold in one colour with 30–50% of the words bold.

**Kinetic recipes (one per role, about 4 roles per film):**
- **Word reveal (default).**
  - Per word: 26 f on out, 6–9 f stagger; opacity 0 → 1; translateY 0.32 em → 0.
  - Blur 8 → 0 px (4–6 px on body lines), cleared by 60% of the eased move.
  - Exit at half the stagger over 16 f: position on in, opacity on smooth.
  - Measured norm: words start at 40% opacity or 50% grey, not 0, rise about 25 px, and settle in 12–24 f.
- **Slam** (problem headline, 1–2 per film): from cue−1 over 15 f on out; scale 1.2 → 1 and blur 22 → 0; then grow 1 → 1.05 through the hold.
- **Locking words** (payoff, 1 per film): two words enter from opposite edges on wordSlide, launched delayTo = 19 f before the cue, each clamped at its lock, with a +1.8% punch and a push 1 → 1.03 through the hold.
- **Tracking collapse** (hero word, once): per glyph +0.6–0.8 em → 0 over 24 f on out; colour accent → ink over 20 f.
- **Underline → block** (a word that becomes a shape or the mark): see §4.
- **Label roll:** old label to −0.6 em over 10 f on in; new label from +0.6 em over 14 f on out, overlapping 4 f; digits roll 6–8 f each.
- **Mask slide-up / masked baseline rise:**
  - Each word rises out of its clip, translateY 110% → 0 over 10–14 f on out, 6 f stagger; opacity over the first 3 f.
  - It needs motion blur, because frame 1 moves about 57 px/f.
  - Optional ink resolve mute → ink over 10 f.
- **Typing:** humans type at about 30 cps. Product prompts are time-boxed to about 68 f on an eased count, then a 72–120 f read hold. Headlines type at 15–22 cps with hard per-letter pops.
- **Reveals never spell another word.** A sweep passes through every prefix, and a half-drawn glyph reads as another letter (half an n is an r; half an h is an l). Reveal names whole-word or by mask, and check every intermediate frame.
- **Blur is only for entry.** Text never stays readable-but-blurred for more than 6 f. Chromium blur radii are quantised in about 0.5 px steps (under about 0.75 px renders fully sharp), so a blur that eases out with the move snaps sharp late.
- **Text being read moves ≤ 3 px/f** (median about 2). Fast type is allowed only when nobody needs to read it, and it must be under about 15–20 px/f and sharp within 10 f.
- **Vertical text snaps to whole pixels** in the headless shell (horizontal stays sub-pixel). End rises early with `arrive(p) = clamp(p/0.94)` so the move stops from about 1 px/f instead of ticking. For slow vertical drifts of text, drift sideways, scale it, or use outlined SVG text.

## 7. Brand and colour

- **One accent token, with its meaning written next to it** ("now", "yours", "set aside").
  - About 5% of pixels on average (top films: 1–6%, peak about 12%). The skill caps it at ≤ 8% outside the single flood, which lasts about 1.2 s.
  - The most restrained films keep 80% of frames under 1%.
  - The accent must still visibly carry the key beats: a mid-film frame at 480 px with no brand colour means the film has no identity.
- **"Just happened" colour.** New things arrive in the accent and relax to ink/neutral over 10–30 f (typed letters 12 f; median about 24 f). Applied to every word on every card, it becomes a tic by the third card.
- **Colour changes on cut or impact frames, never through slow fades.**
  - Accent floods rise in 10–12 f and release over 20–26 f.
  - Mix colours in OKLab, not sRGB: the sRGB midpoint goes muddy and shifts hue.
  - Slow global ramps step at 8 bits (#101010 → #141414 has 5 values), so hide them inside motion.
- **Saturation lives off the product:** at most about 30% of the runtime is saturated (open, close, one hero beat). The UI stays under 3% saturated pixels.
- **Polarity is structure:**
  - Change stage luminance or colour world 2–6 times per film, on act boundaries, each time carried on a moving shape.
  - Never a hard cut to a different luminance on a static frame; at most one flip per bar.
  - A single inversion at about 40% of runtime, inside a music hole, is the strongest attention reset.
  - Luma swings of 10 → 250 on every cut read as harsh on dark phones.
- **Light leads, geometry follows:**
  - Tie luminance to scale: dark when huge, full brightness on the landing frame. Brightness follows p³ of a log-scale slam.
  - Reveal from light values: build +50% over 14 f, dip −25% over 12 f, pop over 7–12 f with about 2% overshoot.
- **Ink:** OKLCH L 0.15–0.18, chroma 0.003–0.008, never #000. On ink, raised surfaces sit at L 0.21–0.23.
- **Paper:** L 0.96–0.99, chroma ≤ 0.004. Neutrals are tinted 0.003–0.010 toward the accent's hue, except next to a red or yellow accent, where they stay ≤ 0.004.
- **Accent lightness and chroma:**
  - light stage: L 0.50–0.65, C 0.10–0.20;
  - dark stage: L 0.70–0.82, C 0.08–0.16;
  - below 0.08 chroma the accent reads as grey;
  - graphics contrast ≥ 3:1.
- **Surfaces:**
  - On paper, one soft key shadow `0 20–40px 60–120px rgba(0,0,0,.12–.22)` (e.g. `0 28px 90px rgba(0,0,0,.16)`), with an optional `0 1px 2px .06` contact shadow.
  - On ink, a luminance step plus a 1 px top hairline at 8–12% white.
  - One card radius; a nested radius is the outer radius minus the padding.
- **Lockup:**
  - Mark height = cap height (1.0× for a solid mark, up to 1.15× for an open one).
  - Gap 0.25–0.4× the mark height, on a shared baseline.
  - Name stems within about 15% of the mark's stroke.
  - The resolved lockup spans **28–45% of frame width**, sits slightly above centre, and is centred on its optical mass.
  - Render three settings side by side (tight/balanced/airy) and pick the one that reads as one object at small size.
- **Defaults to avoid:** framework blue (#3B82F6/#2563EB), flat chroma-0 greys, pure black and white, the GitHub-style blue-grey dark (#0D1117), and haze or radial washes behind the hero.

## 8. Taste and slop: hard bans and generated-look tells

**Hard bans** (when inventing a look; the brand overrides each one):
- **HB1** Eyebrow or kicker labels above a headline ("NEW FEATURE", "01 / SPEED").
- **HB2** Stacked taglines (a second statement under the first), and any "Introducing…".
- **HB3** Text walls (two statements readable at once, bullets, paragraphs) and filler text: decorative mono captions, fake metrics, version strings, coordinates, labels naming the obvious, lorem.
- **HB4** Serif, italic or oblique type, including a skew that fakes one.
- **HB5** Orange, amber, beige, cream, tan or sand as an accent, paper or glow. As OKLCH: orange h 31–96 with C ≥ 0.05; beige h 31–118, L ≥ 0.70, C 0.007–0.10.
- **HB6** Neon (C ≥ 0.27, or L ≥ 0.85 with C ≥ 0.15, or L ≥ 0.80 with C ≥ 0.18), glow, bloom, halos.
- **HB7** Purple, violet or indigo (h 270–340, C ≥ 0.02); purple-to-blue or any multi-hue gradient; gradient text.
- **HB8** Glassmorphism: backdrop blur, a 10–20% white fill, a 1 px white border.
- **HB9** Emoji and stock icons.
- **HB10** Effects standing in for ideas: AI sparkles, particles, confetti, lens flares, code rain.
- **HB11** Bouncy overshoot on anything that isn't a true landing.

**Tells by group:**
- **Concept:** a feature tour; opening on the logo, a question or "Introducing"; borrowed props; a style posing as an idea; a demo with no cause, or a result shown 11 f before a whip; the device dropping out; frames contradicting the promise (a strike-through on your own tagline); a dead or recycled end card; an oversimplified feature; an anonymous product (never named, no chrome); the brief's fact missing from the end card.
- **Copy:** landing-page grammar; all-caps micro labels; stock phrases; a feature name as a headline; over budget; 14–16 px microcopy asked to carry meaning; proofing bugs ("1 clashes", straight quotes, "Acme", "John Doe").
- **Type:**
  - condensed display faces for "impact"; an unchosen UI-default family or a visible fallback;
  - near-miss tokens; a flat 48–64 px scale; faux italics from 3D shear;
  - glyph collisions (overshoot closing a word space: "Everythingfits");
  - blur-dissolve on every word; width-jittering numbers; mono timestamps in consumer UI;
  - letter gimmicks (typewriter headlines, per-letter bounce, scramble/decode, wide-tracked titles at rest);
  - reveals that misspell.
- **Colour:** generated gradients; neon on black; the beige default; glass and glow; an accent with no meaning or two near-identical reds; filler decoration (bokeh, ghost text at 3–8%, per-scene grain); muddy washes; pure-black holes; house-style convergence; the default palette; a colourless film; a mark that misreads at 64 px (minus, plus, menu, padlock, play, ±); haze behind the hero; the stock tech palette (cool grey + navy + teal).
- **Layout:** "text left, UI card right"; small centred floating cards (under about 40% of the width); voids and edge bands; margins < 96 px at the sides or < 64 px top/bottom; crops slicing glyphs; social versions cropped from 16:9; a lockup lost in a void; **an empty vertical frame (a strip in the middle, the bottom 40% bare, 16:9 type sizes)**.
- **Motion:**
  - the default entrance (everything fades in, or y:30 + opacity 0); uniform 0.4–0.5 s timing;
  - bounce everywhere; easing the wrong way (ease-in entrances, expo-out fade-outs); half-sine punches;
  - linear zooms; stall-then-lurch; everything moving at once (idle bobbing, ambient zoom on every scene);
  - 6–7 objects landing on one frame; shape snaps in the last 1–2 frames.
- **Transitions:** crossfade by default; presets; the same iris 3 times; a 2 f pop where a move was meant; a velocity mismatch at a cut; a duplicated rest pose (stop-hold-go); a crossfade through black.
- **Camera:** floating screenshot cards or device mockups orbiting in a void; locked-off shots (mean frame difference about 0.1 for > 1.5 s); an invisible drift (1 → 1.05 over 2 s on a logo reads as dead); strobing unblurred moves over 20 px/f; elements faster than 60–80 px/f.
- **UI:** fake KPIs and charts; data that disagrees (weekdays, counts); a counter frozen, then flipping in one frame; z-order bugs; a caret floating away from its text; animated chip weight; a robotic cursor (straight, constant speed, parked); a cursor present after the product acts alone; text covered by a moving element.
- **Pacing:** a weak or soft first second; dead holds > 48 f; cramming (17 scenes in 32 s, 3 features in 5 s); flat energy; off-grid timing.
- **Cheap vs expensive.** Cheap: the same template twice in a row; per-letter re-centring jitter; animating on twos; a stall between an accelerating exit and the next shot; ambient motion on everything. Expensive: zero overshoot, velocity carried across every cut, one settle constant for all type, early peaks with long exponential tails, crisp settled type, 10–30× speed contrast, exits mirroring entrances, stillness spent once.

## 9. Sound

**Sync norms:**
- **Where each sound goes:**
  - impact: the contact frame (the motion must arrive with velocity);
  - pop-in: the 50% travel frame;
  - tween settle: the 97% frame;
  - text or wordmark: the frame it becomes readable, never the tween's end or the next bar;
  - whoosh: onset **100–450 ms ahead**, apex on the velocity peak (±45 ms), length = the move;
  - typing: per key up to 25 chars/s, one blip per word above that.
- **Measured offsets:** designed accents land about +8 ms after their trigger (range −45 to +75; the tightest films −16 to +27). Clicks come 10–30 ms before the visible press. Word sounds land +40–90 ms after the word first appears, on the full-opacity frame. Hits land 0 to +75 ms after their cut (median +20 ms); after a riser, +100–116 ms.
- **Gate:** every event within ±1 f (±2 f in the audit). A systematic lag of more than 1 f is a defect.
- **Compute sync points from the picture code.** Hand-typed ones landed 8–11 f off.
- **[us]** Mux with ffmpeg, not an encoder that adds AAC priming. Priming of 2048 samples is 42.7 ms, about 2.6 f late. Gate the A/V lag at ≤ 48 samples (1 ms).

**Density:**
- About **5 designed effects per 10 s**, clustered where the music is sparse (cold open 10–28 per 10 s, typing, logo build) and nearly none once the full groove plays (0–1 per 10 s).
- About 85% of hard cuts get no sound of their own and under 5% get a whoosh: about 2 whooshes and about 2 structural hits per film.
- **Sounded:** only discrete state changes (a press, an insert, a lock, a counter landing, the logo assembling).
- **Silent:** scrolls, streaming text, progress bars, rolling counters, hovers, most zooms, URLs typing on.
- **Coverage is all or nothing.** Once a class of action has a sound, every instance gets it at the same level.
- **Scale each sound to its cause:** a caret or tick sits 12–18 dB under a landing; the drop is the loudest.

**Levels:**
- **Master:** −14 LUFS integrated (−16 only for a sting of 8 s or less that heads someone else's video). True peak ≤ −1.5 dBTP on the WAV and ≤ −1 dBTP after AAC (the limiter ceiling is 0.77 linear, −2.3 dBFS). PLR 12–16 dB. High-pass below about 25 Hz. Mono below 120–150 Hz.
- **Arc:** LRA 5–8 LU for films of 20 s or more (4–6 for short pieces). The loudest moment is +4.4 LU over integrated (+2–3 LU over the median momentary), at about 30–60% of the runtime (median 41%), on the drop at the hero reveal.
- **Intro:** 5–12 LU under the body for 2–3 s, with no sub or drums. It enters with intent on frame 0 (a drone or a 150–450 ms entry, never a fade across the first bar). The first 0.5 s sits within 12 dB of the median.
- **Effects vs music:**
  - key click: +4 dB (music ducked 10–16 dB under typing);
  - UI click: −3 dB broadband, but +12–20 dB above 3 kHz; centroid about 3.3 kHz; −20 dB in 6–10 ms; release about 85 ms after the press;
  - pop or word blip: +7 dB, 330–1400 Hz;
  - tick: −8 dB;
  - whoosh: +6 dB over the bed, 120–800 ms long;
  - hit: +21 dB over the bed;
  - chime: +14 dB over a quiet end pad;
  - every effect at least +6 dB over the music in its own band; duck the music 3 dB for 150 ms around key hits;
  - every effect's centroid ≤ 6.5 kHz (9–14 kHz pings are fatiguing).
- **Placement:** effects are dry, mono and centred (pan ±0.1–0.15). Width goes only on whooshes, risers and the music.

**Score approach:**
- Tune everything to the film's key and the chord under it. Kick and sub on the root at 39–62 Hz.
- One chord per bar, changing on downbeats. A V chord ends at bar + 0.08 s, before its resolution.
- A tuned tick/tock signature plus a 3–4 note motif bookends the film.
- A **progress motif** gives one scale step per story step and resolves to the tonic on the payoff.
- Silence before the drop: 30–250 ms gaps (median 150 ms) and sucks of 0.2 s. Risers end in a hard stop, a filter drop or a gap, never a crash.
- One or two breakdowns about 5 LU down at 40–80% of the runtime, with the re-entry on a picture beat.
- Music holes: cut a statement card 3–12 f into a 12–24 f hole and bring the beat back about 17 f later; or a 2–4 beat dropout, with the next visual on the return downbeat.
- **The ending subtracts:**
  - As the logo forms (0–80 ms after its move starts), the music stops on a bar line or filters down.
  - Then 0.2–0.7 s of near-silence, then one soft resolved element (a sub boom peaking around −7.5 dBFS, a bell, the motif) on the frame the wordmark becomes readable.
  - Then a tail of 0.5–2.5 s to below −60 dBFS. The end card sits 8–20 dB under the film's peak.
  - The logo is never the loudest moment, except in a sting.
- **Match the personality.** A calm or literary brand gets soft mallets, felt keys, one bell, narrow dynamics, no sucks, booms or risers. A precise or expensive brand gets sparse piano-like tones, a low strings pad and one warm low chord. Drops onto silence with sub booms are only for energetic launches.

## 10. Finishing

**Motion blur:**
- Average sub-frames in float outside the browser and quantise once. In-browser 8-bit stacking posterises gradients and tints greys cyan or pink.
- 240° shutter, centred on the frame (f ± 1/3).
- Sample count adapts to speed: n = clamp(ceil((240/360)·speed / 3 px), 4, 48); 1 sample under 2 px/f.
  - Table: 2–18 px/f → 4 samples; 30 → 7; 60 → 14; 80 → 18; 120 → 27; ≥ 144 → 32 (cap).
  - Above the cap, shorten the shutter so samples stay 3 px apart.
- **Clamp samples inside the act.** Every hard cut must be an act boundary, or its frame becomes a 50/50 double exposure.
- Discrete state (typed counts, carets, counters, labels, layout switches, grain tiles) reads `Math.round(frame)`, so all of one frame's samples agree.
- **When blur is needed:** anything over 12 px/f needs it; unblurred motion over about 20 px/f strobes. Measured top films read clean unblurred up to about 40 px/f at native 60 fps, and nearly half use no blur at all.
- **Ceiling:** no element faster than about 60–80 px/f. Blur can't save it: it smears into a streak with stepped copies, so redesign the move as a cut, a match cut, a mask wipe or a shorter distance. Frame-filling edges (wipes, floods, irises, zoom-throughs) may peak at 150–300 px/f for a few frames.
- **[us] Our fixed 4 sub-frames is the weakest part of the pipeline.** The skill measured a uniform 4× (3 samples, 0.25 f apart) as clean only to about 12–18 px/f. At 27 px/f the samples separate into three distinct copies. Either keep every element under about 18 px/f, or move to adaptive sampling: about 3 px between samples, up to 32–48 on the fastest frames, with optical-flow speed measured on a sharp pass.

**Banding:**
- CSS gradients render at 8 bits, so any ramp spanning fewer than about 30 code values bands (on ink, 11 → 29 showed about 18 rings).
- Bake gradients as PNGs: compute in float, add ±1 LSB TPDF dither, quantise once.
- Dither only smooth ramps; flat fields get plain rounding to one code value, or x264 smears them into frame-varying blotches.
- Check with a ×12 contrast stretch.

**Grain:** either none, or global at 1.5–2% (σ about 1–2 code levels), keyed to the frame index (a new tile every 2 f). Same strength for the whole film. Measured top films keep flat stages clean and put grain only inside gradients.

**Colour:** BT.709 limited range, tagged on every file (`-colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv`, converting with `scale=out_color_matrix=bt709:out_range=tv:flags=accurate_rnd+full_chroma_int`). Untagged BT.601 previews mislead colour and banding judgements.

**Encode:**
- frame capture: JPEG q95, or PNG for dark gradients;
- previews: CRF 20 veryfast;
- sharp master: x264 CRF 14 slow, yuv420p;
- sub-frame intermediates: yuv444p CRF 6;
- 10-bit master only for grading; ship 8-bit to the web;
- audio: AAC 320k, 48 kHz, `-af apad -t <exact length>`, `+faststart`;
- the poster is rendered as a lossless still, not decoded from the H.264 master.

**Chromium traps (each one was hit on a real film):**
- fractional left/top plus a transform → pixel stairs;
- `will-change` on a layer whose blur animates → ghost frames;
- a negative SVG `rx` or `width` → stale shape (clamp ≥ 0);
- gaps under 8 units or strokes under 1.5 px → crawling dashes;
- overflow/opacity/filter flattening `preserve-3d` → paint in z order yourself;
- no CSS animations, Math.random or Date.now;
- gate rendering on font load.

## 11. Review loop and ship gate

**Rounds:**
- At least 2 rounds for launch films; stop after 5.
- Critique runs on fast previews. The blurred master is rendered once at the end and gets a check, not a round.

**Per round:**
1. Render.
2. Run the scripts.
3. Make contact sheets: 12 fps sheets of 4 s chunks, plus a legibility sheet at 480 px wide, 1 frame per second.
4. Look at the sheets before opening any code.
5. Run the lenses.
6. Verify.
7. Fix by impact per minute.
8. Write down each fix with the frames that prove it.

**Lenses:**
- **Director:**
  - First run the hard-ban checklist on the sheets.
  - Name the weakest 3 seconds; anything cheap, templated, slow or dead.
  - Specificity (true of a simpler product?); its own look (vs. a generic minimal template); colour at thumbnail size; the mark at 64 px.
  - Does each act land in under 1 s? Does the story read muted, with the device never blinking?
  - The hook (frame 0 moving, problem by 1–2 s); can a stranger name the product?
  - The end (lockup 1.5–2 s and building, URL ≥ 1.7 s, final frame = poster).
  - Covered text; a vertical frame with a bare bottom 40%.
  - Pacing (one peak per bar, first 6 s 2× dense); transitions (6–8 types, signature ×3, no duplicate rest pose); the fastest frames at full size.
  - At most 12 changes, each concrete and code-level.
- **Forensics:** pops, seam pops, stalls, frozen holds over 48 f, ghosts, border slivers, judder, sharpness steps, banding, smear; checked at full resolution.
- **Sound/sync:** onsets vs cues per stem; the 3 biggest picture changes each have an audio onset within ±3 f; masking; LUFS/LRA/payoff; head and tail; personality fit.
- **Art/copy/UI:** spelling and plurals; reveals; word budget; tokens; tabular numbers; collisions; brand personality; lockup typography; one accent with one meaning ≤ 8%; composition and safe zones; data truth.
- **Verifier:** tries to refute every P0 and P1 at real speed. It rejects claims that are wrong, invisible at speed off key beats, already fixed, or whose fix would hurt the film.
- **Critic prompt rules:** say what changed; "do not re-report fixed issues"; "don't propose adding text" (the fix is the picture); rank by impact per minute.

**Severity:**
- **P0:** visible on a key beat (hook, payoff, logo, end card), breaks the story, a typo, audio ≥ 3 f late, the device blinking, or any hard ban.
- **P1:** noticeable on a normal viewing.
- **P2:** visible only on pause.

**Rubric:** 11 dimensions scored 1–5: idea & device, hook, copy & type, colour & brand, composition, motion, transitions, pacing, product truth, sound & sync, finish. **Ship gate:**
- every dimension ≥ 3;
- Finish = 5 and Sound & sync = 5;
- mean ≥ 4.2;
- no open P0;
- all scripts pass.

**Design-off.** If an act stays at ≤ 2 for two rounds, three parallel redesigns (story, camera and rhythm biases) are judged on cinema, clarity, restraint and risk, and the best ideas are grafted onto the winner.

**Recurring issues, most common first:** seam pops and duplicate frames → sound on the settle instead of the contact → dead holds → overshoot collisions → Chromium artifacts → half-sine envelopes and expo-out fades → UI truth → masked or out-of-key sound → templated layouts → house-style convergence and oversimplified features → moves too fast to blur.

**Thresholds worth copying into our QA** (d = mean |ΔRGB| at 480×270):
- spike: d > 1.0 and > 2.5× the local median + 0.3;
- stall: d < 0.05 between moving frames;
- frozen hold: d < 0.1 for > 48 f;
- quiet: a 60 f mean < 0.15;
- still opening: the first moving 0.5 s window starting after 1.0 s warns, after 2.5 s fails;
- loop seam ≤ max(0.4, 1.5× the median step).
- Top-film reference: median frame difference 1.4, p90 6.0, 27% near-still frames.

## 12. Techniques for an editorial/engraving brand ad

The ad uses photos and illustrations, kinetic type, a travelling accent dot, morphing text, clean 3D and zooms. These are the entries from the 273-entry library that fit it best. The skill draws about one technique per 2.5 s (**6 for a 15 s film**) at random, weighted by format and energy, so films don't converge. Use the list as a menu, retold in our own objects.

1. **Travelling thread object (signature).**
   - Build: one accent object, head 2–3% of frame height, with a tapered tail of length clamp(v·1.5, 0, 240) px and no halo.
   - It travels on paths at 20–60 px/f with true blur: contact into impacts, out into the distance.
   - Across a cut it re-enters from the same side at the same angle, and hands off by becoming the next element (a check, a pin, a period), with squash on contact and a hitPulse bump on the struck element.
   - Timing: 3–5 appearances of 20–60 f each, at the same size every time.
2. **Velocity-stretch dot.**
   - Build: the dot stretches into a capsule along its motion. Tail = an exponential follow of the head (weights 0.8^i over 30 f, a lag of about 4 f), drawn as a round-cap line at the dot's diameter.
   - Hop: 54 px over 22 f on smooth every 54 f, with the label colour flipping over 8 f around the midpoint.
   - Exit: stretch to a dash of about 4× the dot's length over 17 f, then off on in.
3. **Collapse to a dot relay (signature).**
   - Build: the hero collapses to a 24–52 px dot (4 f on in into a cut, or 16 f on out to snap and hold). The world scales lmix(1, 0.03) over 24 f on contact about the dot.
   - The dot stays at full opacity through the seam, then opens into the next object over 8–12 f.
4. **Story object becomes the mark.**
   - Build: compute the mark's rect first; the last object lands exactly on it.
   - Then either a hard cut at 0.57 of the size, growing lmix(0.57, 1) over 18 f on out, or an in-place darkening over 12 f.
   - Hold about 20 f before the name follows.
5. **Device keeps time inside the lockup.**
   - Build: only the device piece pulses, 1 + 0.12·hitPulse(f−beat, 2, 6), 1–2 times on downbeats at least 30 f apart, none in the last 30 f. It flashes to the accent and relaxes over 12 f.
6. **Shared-letter morph** (the text morph).
   - Build: shared glyphs keep their element and slide to their new kerned x over 24 f on out; unshared old glyphs fade over 6 f; spaces collapse over 8 f.
   - New glyphs fly in from ±150/±120 px, rotated 90–180°, over 24 f on out, with opacity over 12 f (faint while faster than 20 px/f). Starts are spread over 56 f.
   - Hold ≥ 36 f. Needs at least 2 shared letters and words of 8 letters or fewer. Check every frame for accidental words.
7. **Travelling front restyles a word** (variable font).
   - Build: after the word lands (+10 f), a front 0.6 em wide sweeps over 32 f on dolly. Each glyph goes mute → accent → ink in OKLab, or wght 400 → 700, with advances interpolated so the line stays centred.
   - Use colour or weight, not both, in one film.
8. **Masked baseline rise** (editorial headlines).
   - Build: per word, translateY 110% → 0 over 12 f on out inside an overflow-hidden box (padding-bottom 0.15 em), 6 f stagger, opacity over 3 f, optional ink resolve over 10 f. Exit back into the mask over 10 f on in.
9. **Ink resolve on arrival.**
   - Build: words arrive pale (opacity 0.3–0.4, colour mixed 65% toward the paper) and darken to ink over 12–16 f on out (a headline may take 40 f), with a ≤ 60 px masked rise over 20 f and an 8 f stagger.
   - Connector words reach 50% in 2 f, so the nouns read first. Good over textured or engraved plates.
10. **Phrase clamp at a junction (signature).**
    - Build: the halves meet at about 48% of the width. The first half rises +64 px → 0 and the second drops −40 → 0 over 18 f on out, 2 f word stagger.
    - Or a horizontal snap: 35 px per side to 0.75 of the gap over 10 f, then back over 18 f on outSoft.
    - A +1.5% punch on the beat; hold ≥ 54 f with a 0.3 px/f drift. Once per film.
11. **Words part for an inserted object** (a photo or illustration inside the headline).
    - Build: a slot opens over 16 f on glide while the groups translate apart. The object pops in on the micro spring once the gap is 70% open. Hold 14–60 f.
    - To make it the next shot: the words fly apart over 16 f on in while the image scales up into the next hero (measured: words accelerating ×1.22/f).
12. **Cut in mid-sentence, pull back to the line.**
    - Build: open at k = 3.2 on the key word with its first glyph about 40% cropped; settle 12 f, hold 36 f at 0.3 px/f drift.
    - Pull back to k = 1 over 56 f on dolly (log zoom).
13. **Pull out from inside the object (signature).**
    - Build: open on what reads as a full-bleed field or a statement, which is really the face of an object (an engraved plate, an illustration, the mark) at k0 = 8–14.
    - Pull to k = 1 over N = 25.7·ln(k0) frames on dolly (about 53 f from 8×). The log rate peaks near 6%/f, so frame-corner speed stays under 66 px/f.
    - Opening copy scales by (k/k0)^0.46 and fades over 8–14 f. Vector content only; a bitmap falls apart at 8–14×.
14. **Scale-through cut (signature).**
    - Build: outgoing shrinks 1 → 0.75 over 16–24 f on in; cut on the downbeat; incoming goes 1.8 → 1 over 30–40 f on out, on the same anchor (±30 px).
    - Ideal for photo → illustration → UI medium changes.
15. **Shape match cut.**
    - Build: centre within ±20 px, scale 0.57–1.3×, incoming settles over 18 f on out, outgoing shrinks 2–4% over its last 4 f. Hold 12–30 f.
    - E.g. a round photo crop → the dot → a circle in the mark.
16. **Iris from a glyph.**
    - Build: a 14 px seed on a word (6 f in, held 6–10 f) balloons ×1.25–1.29/f over 20 f to the farthest corner, revealing the next scene inside it. The centre drifts to the frame centre on smooth. The disc fills the frame on the downbeat.
17. **Velocity handoff cut** (the workhorse; exempt from the 2-use limit). Exit 16–24 f on exit ending at 25–40 px/f; entry at 30–55 px/f decaying over 45–90 f; one screen vector per act.
18. **Pacing pair: the one long hold + music hole, then slam.**
    - One claim near-still for 60–90 f (breath 1.5–2%, under 0.3 px/f), leaving on a +6% in-creep over 18 f. Every other near-still run stays ≤ 30 f.
    - Pair it with a 12–24 f music hole and a re-entry on the next picture event, ±1 f.
19. **Monochrome world, one accent / one grade across mixed media** (photos plus illustrations plus UI).
    - Normalise every medium to one value range: photos grayscale, brightness about 0.65, every medium's mean luma 8–25%. Nothing but the accent exceeds chroma 0.03.
    - The accent goes on exactly one thing per shot and swaps on cue frames, never via fades.
    - Media swap on beats every 48–90 f. **[us]** On a light editorial stage, apply the same discipline the other way round: one paper tone, ink-only illustration, the accent only on the hero.
20. **Halftone or stipple shading** (engraving texture done honestly).
    - Halftone: a 12 px pitch dot grid clipped to the shape, dot radius 5.5·smooth(dist/R) px from a light point drifting under 0.5 px/f; dots under 0.8 px are dropped. Revealed as a 36 f diagonal wave.
    - Stipple: seeded noise masked to the lit ramps only, overlay at 0.08–0.12; the flat stage stays clean.
    - Keep halftone shapes ≥ 200 px. Engraved hairlines need ≥ 1.5 px at final scale and fade out on pull-backs.
21. **Low-luma photo plate** (dark acts).
    - A sharp plate with grayscale, brightness 0.25, contrast 1.15, at 5–8% mean luma; or a pre-blurred plate (40 px offline) at 0.3× parallax. Overscan 6%.
    - Plates may hard-cut every 15–30 f under a locked foreground. Never fade a plate.
22. **Hero push with a 3D turn / tilted object on a spotlit ground** (clean 3D).
    - Push: 1 → 2.56× over 60 f on smooth with yaw 24–30° and pitch about 5°; caption at 75% of the move; then breath +2.5%. Once per film.
    - Spotlit object: perspective with roll outside the tilt (rotateZ 4°, rotateX 8°, rotateY −12°), a dithered PNG light pool, a contact shadow (blur 36 px, alpha 0.35), drift −0.5 px/f and yaw 0.03°/f.
23. **Living hold creep + lockup keeps building.**
    - Every hold over about 30 f creeps 0.04–0.07%/f, or drifts 0.3–0.5 px/f (1.5–3 px/f for big type).
    - The end card pushes 10–20% on dolly over its 90–120 f hold, while tracking tightens +0.03–0.06 em → the token value over 46 f.
    - Never fade to black: the last frame is the poster, with mark + name + at most one CTA at the secondary size, readable ≥ 1.7 s.
24. **Vertical clear-band stack** (9:16 layout).
    - The safe band at 1080×1920 runs y 270–1500 (896 px wide, centre y ≈ 885). Feed zones: top 270, right 120, bottom 420, left 64 (a strict preset uses bottom 672).
    - The caption sits on top (≤ 2 lines), a 48 px gap, then the subject at 0.86 of the band width. The combined mass is centred on the band's centre; the action happens around y 900–1100.
    - The subject rises 120 px over 40 f on glide; the caption follows 8 f later; scenes exit upward over 16 f on in.
    - No bare bottom 40%: the caption zone carries stage or product texture.

---

## Files read

- `SKILL.md`
- `references/`: `concept-and-story.md`, `timing-grid.md`, `motion-tokens.md`, `transitions.md`, `camera.md`, `craft-rules.md`, `copy-and-type.md`, `brand-and-color.md`, `taste-and-slop.md`, `sound.md`, `finishing.md`, `review-loop.md`, `worked-example.md`, `formats.md`, `chromium-rendering.md`, `product-ui.md` (most sections).
- `references/technique-library.md`: the category intros plus about 60 selected entries.
- Headings and selected sections only: `hyperframes-engine.md` (§11.7–11.8 on motion blur), `remotion-engine.md`.
- `assets/critics/`: `director.md`, `art-copy-ui.md`, `sound-sync.md`, `forensics.md`, `verifier.md`.
- `assets/TREATMENT.md` (header); `assets/remotion-starter/src/lib/anim.ts` (SPR, arrive, blurIn, blurOut, squash, inertia, stagger).
- `scripts/pick.py` (docstring and weights).
- File listing of `scripts/` and `assets/`.

All paths are under `/tmp/claude-0/-home-user-ApoheniaQuest/a7864f3b-0e94-5f00-94a5-59ce23b410f7/scratchpad/leon/cinetic/skills/cinetic/`.
