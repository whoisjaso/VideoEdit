# Kinetic text + reading ball (LOCKED, Jason 2026-10-11: "one of the best type of work you've done so far")
Reference build: the Plutarch Bucephalus proof v2 (`proof.html`, `renders/plutarch-alexander-proof-bucephalus-v2.mp4`).

## Pipeline
1. **Word times.** `wt.py`: faster-whisper medium.en with word timestamps on the voice, mapped onto the known script words → `words.json`.
2. **Phrases and heroes.** `caps.py`:
   - Clauses split at punctuation; anything over 7 words is split into balanced halves; one-word orphans are glued to a neighbour.
   - HERO lines get their own window.
   - Writes `caps.js` (PH, HERO), plus the text SFX cues: an airy whoosh at −9 under every phrase, and a whoosh + texture + shine + sub stack on every hero.
3. **Render.** `proof.html`, functions `text(t)` and `ball(t)`, pure seek(t).

## Captions
- Each word writes in **on its spoken time**: opacity 0→1, blur 10→0 px, rise 0.42 em, over 0.42 s.
- Key words switch to Instrument Serif italic gold, start at 1.14× and settle, with a glow that decays.
- The line drifts up 3.2 px/s, and its tracking opens by 0.018 em.
- **Exit** starts 0.3 s before the next phrase: lift 78 px + blur over 0.4 s. Two alternating slots, so the outgoing line clears above while the next one writes in below.
- Heroes:
  - per-letter stagger (blur 16→0, rise), a light sweep across the letters, tracking slowly opening, a gold hairline drawn beneath;
  - exit: the hero lifts 150 px away while the caption continues.

## The reading ball
- **Reading.** One gold dot hops word to word, landing on each word **as it is spoken**, in an arc of 18 px + 7% of the distance.
- **Pointing.** When the story points at something (KEYS), it springs off the current word in a high arc (180 px + 25% of the distance, 1.6 s, inOut) and lands on the target with a squash. A drawOn ring follows. Then it returns to the words.
- **Look.**
  - Motion blur is a streak of 16 past positions (11 ms apart) drawn as round segments that taper and fade.
  - Gold glow (shadowBlur 22) plus a hot cream core.
  - Pure function of t, so every frame is deterministic.
- **Use it on every narrated / long-form piece and on any captioned motion piece.** Keep exactly one ball: it is the viewer's eye.
