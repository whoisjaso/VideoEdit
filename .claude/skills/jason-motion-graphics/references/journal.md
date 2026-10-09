# Motion-graphics journal (scores from Jason, newest last)
Plain English. After every piece: what shipped, his score, what to fix, rules he approved.

| Piece | Score | Jason said | Lesson / rule |
|---|---|---|---|
| MG v1 blueprint sample (Oct 8) | 6.8 | "the glows, smooth animations, the backgrounds, the infinitesimal details: nowhere near" | Every beat needs bloom, motion blur/parallax, layered background, micro-detail (`mg-quality-bar.md` §8) |
| MG v3 iOS sample | 6.9 | (score only) | Style isn't the gap, execution is: motion in frame 1, a big focal object, a 3D camera, whip transitions |
| MG v4 3D/whip sample | none | "honestly not the best" | More motion alone didn't close it |
| MG v5 Coop look on ep4 | **7.7** | "I like this" | Dark stage, hard cutaways, real proof UI, every graphic on his word with a sound |
| MG v6 smooth | none | "this was a lot better" | **Rule: smooth, never stepped** (the 12 fps look felt laggy) |
| UI morph "Just Post" v1 (Oct 9) | pending | his brief; "the prompt I gave was more motion graphics" | Led to splitting into two skills: footage edits vs standalone motion graphics |

## 2026-10-09 · Skill split
- Jason: "we need to create 2 skills for distinguishing the type of edits." So `jason-video-editor` = his footage; `jason-motion-graphics` = standalone motion pieces from a brief.
- Moved here: the morph engine (`engine/`), `mg-quality-bar.md`, a brief template. The Remotion kits and SFX library stay shared in the editor skill.

## "Just Post" v2: sound pass (Jason: "sfx could be better, there's one sound I don't like"; he hasn't named it yet)
- Replaced the soft "open" swell, which played 5 times, with a different sound per kind of moment:
  - real buttons (pack5) for taps;
  - the iOS lock/card sound for panels opening;
  - lighter whooshes for transitions;
  - one real keystroke per typed letter;
  - silent hovers.
- Transitions dropped 4-6 dB so the interactions lead. Every sound is still placed by its measured peak.
- **Waiting:** which single sound he disliked. When he names it, it's banned for motion pieces (rule here).

## 2026-10-09 · Claude spec ad v1: "Every masterpiece started as a thought." (15 s, 60 fps)
- **Brief:** a fast Claude ad, light mode, an art reimagine, paint on the images, perfect morphs, ends on the logo.
- **Reference video:** it never arrived (the uploads folder was empty). Built from the brief; asked Jason to resend it.
- **Research:** Claude's brand is the clay spark (#D97757), near-black #141413, a Tiempos-style serif, and hand-drawn illustration. Its parchment beige was swapped for pure white, per "no beige".
- **Assets:** 18 public-domain masterpieces from the Met Open Access (CC0); the Art Institute's server blocked bots. Credits in `examples/claude-ad/CREDITS.md`.
- **Music:** Mixkit #623, measured 120.0 BPM, cut so its drop lands on the montage at 4.0 s.
- **Morph chain:**
  - spark draws → its rays open into a marble head → card → circle + pen halo;
  - the spark "thought" pops → dive into it → the orange collapses into the first collage tile;
  - Hokusai grows from a tile → becomes the front card of a 3D carousel → Van Gogh grows from it;
  - match cuts land each face inside one fixed ring → the red-chalk Michelangelo;
  - a ring of works → rays → implode → the spark turns in 3D → "Claude" lockup.
- **Self-QA fixes before delivery:**
  - letter gaps: the "Serif" font name collided with the browser's generic serif;
  - text over the busy sculpture;
  - the underline crossed the word;
  - carousel hand-off maths;
  - faces near a painting's top edge forced absurd zooms;
  - the word sat over the full-frame Hokusai;
  - the orange tile didn't match the first image at the drop;
  - the wave trace appeared early;
  - the rays → logo ghosting (redesigned as an implosion).
