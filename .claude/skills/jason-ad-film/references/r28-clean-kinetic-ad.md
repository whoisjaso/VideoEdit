# r28: CLEAN KINETIC AD. The 10/10 motion-graphics benchmark, especially for ads (Jason, 2026-10-12: "this is the perfect example of a motion graphic, especially for ads, this is a 10/10")
**Label:** `CLEAN KINETIC`.

**Source:** a 15 s 9:16 promo for a sound-effects pack (CTA: comment "Pack").
**VO:**
> Video editor. Still wasting hours searching for the perfect sound effects? Not anymore. I've created my all-premium sound effects pack. Use it in your videos and upgrade your edits: premium, professional, and cinematic. Want the sound effects pack? Comment pack.

## Beat map (one new visual every 0.3–0.6 s, one continuous camera)
| t (s) | Picture |
|---|---|
| 0.0–1.6 | "Video Editors": words fade in with blur from pale blue, settle to black, slight scale drift |
| 1.6–2.6 | "Still Wasting": a typing caret; "Wasting" slides as a thin blue arc sweeps in |
| 2.6–3.2 | A cyan circle wipe reveals the **Safari icon**; the camera pushes into it |
| 3.2–5.3 | **Google logo** + search bar; "Perfect Sound Effects?" types; the camera pans with the caret; the cursor clicks the search icon |
| 5.3–6.3 | "Not Anymore": a staggered word drop, light → bold |
| 6.3–7.4 | "I've Created My All Premium": the line slides through the frame word by word (a ticker with the camera tracking) |
| 7.4–8.0 | A **blue blob morphs into a Google Drive card:** folders Whoosh 124MB, Riser, Impact, Pop, Click, Gear |
| 8.0–9.2 | The cursor **drags "Whoosh"** out onto a cyan content card (a "Lazy → ambitious" panda thumbnail): the product being *used* |
| 9.2–10.0 | The file drags back onto a Google card, which **pixelates/mosaics away** |
| 10.0–12.2 | "Premium" → a blue dashed vertical line wipes → "Professional" → "Cinematic". Each word shrinks to tiny and the next one punches in |
| 12.2–13.6 | "Want This Sound Effects Pack" builds word by word, then the whole line **shrinks to a speck** |
| 13.6–14.9 | `Comment "Pack"` punches in, breathes, then fades |

## Why it's 10/10 (the rules)
1. **Near-white stage** (#F4F5FA / pure white), black SF-style sans, one **cool blue accent** (cyan #A5E3FB, blue #3B82F6). Nothing else competes, and the brand colours of the real logos pop.
2. **Every spoken word is on screen as it's spoken** (kinetic VO-sync). Incoming words arrive pale blue and blurred, then settle to black. This is a "now reading" colour state, no captions needed.
3. **Real brand UI tells the story** (r25): Safari → Google search → Drive folders → drag a file into a video. The viewer *lives* the pain and the fix.
4. **A cursor is the actor:** it types, clicks and drags. Each action is one UI tick sound.
5. **No hard cuts:** circle wipe, push-through zoom, blob → card morph, mosaic dissolve, a dashed-line wipe, scale-to-speck exits. Motion blur on every move.
6. **Scale contrast as rhythm:** words snap between huge and tiny. Shrink-to-speck is the exit; punch-in with a single overshoot (r22) is the entrance.
7. **Hook to CTA in 15 s:** pain (wasting hours) → loop (search) → "Not anymore" → proof (the real files and sizes) → three benefit words → one CTA keyword.
8. **Sound:** VO on top, a soft modern bed, a tick on each type/click, a whoosh on each camera move, a pop on each word punch. Quiet ~250 ms gaps after "sound effects?" and before the CTA (onsets: 0.1, 4.25, 5.4, 5.95, 6.75, 7.3, 14.05 s).

## Build notes (our engine)
- `kit.js` already has the blur fade, `back` overshoot and camera push.
- New pieces to build:
  - a word-state colouring (incoming blue → current black → past fade);
  - a cursor actor (path + click squash);
  - a mosaic dissolve (pixelate by downscale steps);
  - a blob → card morph (SDF/rounded-rect radius tween);
  - a dashed-line wipe.

  Add each to the kit after first use.
- **Default ad format when there's no footage:** 9:16, 12–20 s, VO-driven.
