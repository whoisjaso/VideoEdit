# r25: BRAND STORY. Real brand assets, told as one continuous UI morph (Jason, 2026-10-12: "add this on top of motion graphic skills, and being able to use brand assets when talking about them directly or indirectly, and making the animation style as such")
**Label:** `BRAND STORY`.

**Source:** a 10 s phone recording of an editor (EffectCraft) playing a ~9 s 16:9 Uber Eats spot. End card "visualspaid".

## Beat map (≈ 0.5–1 s per beat, no hard cuts)
1. iMessage on dark: a blue bubble **"Bro i'm starving"** stretches in with motion blur → grey typing dots → **"Try UberEats"** reply. A cursor taps it.
2. The tapped bubble **turns green and morphs into the Uber Eats app icon** (rounded square, brand green, white wordmark). The background flips to light.
3. The icon **morphs into a search pill** ("Search" → typed "Where are we…") with loading dots.
4. The pill **stretches into a green bar**, which splits into **three food tiles** (pizza, burger bowl, ice cream emoji-icons) sliding in on parallax.
5. A tile morphs into a **status card:** "Delivery Requested / Finding drivers nearby" with a **blue progress bar filling** → "Driver Found / Your food will be delivered" with a green bar.
6. The card dissolves into a **map** (light grey streets, green park blocks). A white car drives to the **blue location dot** with motion blur, and the camera follows.
7. **Wordmark resolve:** "Uber Eats" (black "Uber", green "Eats") slides in with motion blur and settles. A soft exit, then the creator credit.

## What makes it work
- **The brand's own world:** its real logo, wordmark, exact brand colours, its app's UI patterns (search pill, status card, map, car), and the platform's real UI (iMessage blue/grey bubbles).
- **A story, not a logo slam:** need → suggestion → app → choose → status → arrival → brand. Each beat is a step the viewer has lived.
- **One object travels:** bubble → icon → pill → bar → tiles → card → map → wordmark. Every screen is born from the last one (shared-element morph, matching r21).
- **Motion:** entrances ease-out with motion blur; pops and landings use a single overshoot (r22); moves ease-in-out; the progress bar is linear.
- **Clean light stage** with soft shadows, no outlines, big continuous radii (the iOS look). Colour comes only from the brand.

## THE RULE: use brand assets whenever a brand is mentioned
- **Named directly** ("Uber Eats", "Cash App", "Chase", "ChatGPT") → show **that brand's real logo, wordmark, colour and UI**, never a generic icon.
- **Referred to indirectly but clearly** ("I texted him", "ordered food", "swiped my card", "googled it", "paid him back") → use the platform the moment implies: iMessage bubbles, a delivery-app flow, a card tap, a Google search bar, a Cash App send screen.
  - If the brand isn't clear, use the most likely category UI built *in the style of* a real app. Never invent a fake brand name.
- **Animate the brand's own flow** (its real screens and steps), using the beat pattern above. Don't just drop a static logo.

### Where assets come from (in order)
1. `../../jason-video-editor/assets/logos/` (simple-icons SVGs, already in the repo).
2. **simple-icons** for any other brand: `https://cdn.jsdelivr.net/npm/simple-icons@13.21.0/icons/<slug>.svg`. The package's `hex` field gives the official brand colour.
3. The brand's official press or media kit for full-colour wordmarks and app icons.

Save every new logo into `assets/logos/` so the library grows.

### Guardrails
- Never distort, recolour or re-letter a logo; scale it uniformly only.
- Commentary and storytelling are fine. Never make it look like the brand sponsored or made the video unless it did. No fake ads with the brand's slogan as if it were official.
- Never put real private data (names, numbers, addresses) in a recreated UI.

### Sound
Real iOS sounds for platform UI (send whoosh, received, tap tink); a soft whoosh under each morph; a success chime on "Driver Found"; a small riser into the wordmark.
