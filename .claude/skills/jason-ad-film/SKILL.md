---
name: jason-ad-film
description: "Jason's system for premium fast-paced brand ads and launch films built from code (the engraving-style Claude ad look), reusable for any brand and for standalone motion pieces. Use when Jason asks for an ad, commercial, brand film, launch teaser or logo sting, says 'an ad like the Claude one', pastes a prompt-motion.com-style brief, or sends a reference ad to match. Pipeline: decode reference, brand research, one ownable concept (idea, device with state, grammar), public-domain or brand assets in one treatment, beat sheet on a whole-frame 120 BPM grid, pure seek(t) HTML engine (kit/), forensics QA, adaptive optical-flow motion blur, picture-computed sound, deliver. Not for edits of Jason's raw footage (jason-video-editor) or simple UI morph loops (jason-motion-graphics)."
---

# Jason Ad Film — SOP

> **SKILL UPKEEP (Jason, 2026-10-09):** Jason's claude.ai account copy of this skill is the MASTER; it is what loads in Claude chat, the Claude app and every Claude Code session. Editing the repo (or `~/.claude/skills/synced/`, a read-only download) does NOT update his account. After every approved change: edit the repo skill → run `bash skills-sync.sh <outdir>` at the repo root → send Jason every zip it marks "NEEDS RE-UPLOAD" and tell him to replace that skill at claude.ai (Settings → Capabilities → Skills). Never report a skill as updated until he has re-uploaded it.
>
**Why this skill exists:**
- Jason scored the first Claude ad 8/10 ("I absolutely adore this… extremely clean").
- He asked for a system to replicate it across ads and motion graphics.
- He set the bar: Leon Lin's "Engraving-style Claude ad" (decoded in `references/decode-engraving-claude-ad.md`).
- The craft numbers come from Leon's MIT `cinetic` skill, summarised in `references/craft-rules.md`. Read both before every film.

**Which skill?**
| Request | Skill |
|---|---|
| Ad, brand film, launch teaser or logo sting for any brand | **this one** |
| Edit Jason's raw footage | `jason-video-editor` |
| A single UI-morph loop or a quick motion piece from a brief | `jason-motion-graphics` |

> **THE EDITING STANDARD: r21 Netflix film (Jason, 2026-10-12: "this is the video editing standard"):** one continuous camera where every scene morphs into the next (shared elements, push-through blur, slit-scan; no hard cuts, no plain crossfades); one signature transition in the brand colour, used repeatedly; open and close on the same build (callback); ~300 ms of silence before the final drop; real UI, cinematically lit; rack-focus depth; VO of 8 short second-person lines on visual beats; two-line kinetic type with a brand-colour accent word, shimmer and an underline draw; a new idea every 1–1.5 s with one breath before the payoff; exit dot → line → credit. Full decode: `references/r21-netflix-standard.md`.
>
> **STYLE LIBRARY (Jason, 2026-10-12: "label as such so we know the standard and references"):** every approved look has a label: see `../jason-motion-graphics/STYLES.md`. Always on: **EASING** (r22: entrances ease-out, exits ease-in, moves ease-in-out; **pops, buttons, icons and morph landings get a single ~10% overshoot**, which replaces "no bounce" for pops only; linear only for machines). **HOOK PSYCHOLOGY** (r24: hook → delay → rehook ~midpoint → delay → payoff → end immediately; never answer the hook straight away). **BRAND ASSETS** (r25: any brand named directly or clearly implied gets its real logo, colours and animated UI flow, in the BRAND STORY style; never a generic icon or a fake brand). **VOICE CHAIN** (r26: every voice gets high-pass → expander → de-esser → EQ +3.5 kHz → compressor → limiter, in that order; `voice_enhance.py`). **COLOR TRIAD** (r27: thumbnails, covers and hook frames use one 120°-apart pair picked by emotion). Named looks: NETFLIX/CONTINUOUS, BRAND STORY, DOC-PAPER 3D, ENGRAVING, READING BALL, COOP, iOS, BLUEPRINT.
>
> **10/10 MOTION GRAPHIC: CLEAN KINETIC (r28, Jason 2026-10-12: "the perfect example of a motion graphic, especially for ads, this is a 10/10"):** the default for ads and motion pieces with no footage. Near-white stage, black SF-style sans, one cool-blue accent; every VO word on screen as spoken (pale blue + blur → black); real brand UI driven by a cursor (type, click, drag); continuous camera with circle wipes, blob→card morphs, mosaic dissolves and scale-to-speck exits; a new visual every 0.3–0.6 s; hook → proof → 3 benefit words → one CTA keyword in ~15 s. Full decode: `references/r28-clean-kinetic-ad.md`.
>
> **TEXT MASKING = THE MOAT (Jason, 2026-10-12: "text masking is the MOAT and pinnacle of real life video, alongside edits and motion graphics, it's a creative mix"):** every footage edit mixes three layers (the cut, motion graphics, and text that lives *inside* the shot), and text masking is the signature. Use at least 3 per video, on the hook and the biggest lines:
> - **behind-subject:** the hero word sits behind his head or body (`matte.py` person cutout);
> - **pass-through reveal:** the word is hidden, then revealed as he or an object moves across it (the matte as a wipe);
> - **object wipe:** a door, car, hand or pole crossing frame masks the word in or out (rotoscope the object with SAM/rembg per frame);
> - **surface-tracked:** the word pinned onto a wall, screen, shirt or road with perspective and the scene's grain and light;
> - **inside-letters:** the footage plays *inside* giant letters (type as a window) on the hook or title.
>
> Masked text follows the r22 easing, the meaning colours and the font combos. Check stills: the edge must be clean (no halo, no flicker; feather 1–2 px and temporal-smooth the matte).
>
> **CHAPTER / TITLE CARD STANDARD (Jason, 2026-10-12: "way better, this is the standard", after rejecting a laurel clip-art title as "ass"):** the subject's real portrait (public-domain bust or engraving, rembg cutout, warm-toned) rising from near-black under one warm pool of light with a slow push; a raking light clipped to the subject only (never a beam on the background); a left type stack: tracked gold small caps → the NAME as the hero in a classic book serif (Cormorant Garamond Light), letters rising through a mask → the film's own device draws a thin rule → the series title in italic → a micro source line; grain over everything. Hierarchy: the chapter name leads, the series title frames it. Banned: clip-art ornaments over type, glowing yellow italics, tiny subtitles. Template: `projects/plutarch/film/title2/title2.html`.

## Non-negotiables (Jason + measured craft)
- **Smooth, never laggy** (Jason).
  - Adaptive motion blur: a sharp pass, then optical-flow speed per frame, then 1–32 samples at a 240° shutter, blended in float.
  - Nothing faster than 60–80 px/f except frame-filling edges.
- **One idea, one device, one grammar** (`craft-rules.md` §1).
  - The device has a *state that changes* and ends as the logo; it never blinks out.
  - A bare travelling dot is not a device.
- **One visual language.** Every asset gets one treatment: grayscale engraving, paper knocked out to the stage white, objects cut out with rembg. No colour photos in rounded cards (the v1 look that capped it at 8/10).
- **One accent with one meaning,** about 1–5% of pixels, at most 8% outside a single flood. Everything else is ink on paper.
- **Type:**
  - one bold serif, one line at a time, at most 5 words, about 124 px statements;
  - masked baseline rise; one shared-letter morph per film;
  - no eyebrow labels, no stacked taglines;
  - only the brand's real words or the film's own callback copy.
- **Motion:**
  - about 3 easing characters (out / in or exit / inOut, plus cam and dolly);
  - zero overshoot (critically damped), except at most 2 true landings;
  - one `hit()` envelope for every punch;
  - velocity is carried across every cut.
- **Energy arc:**
  - something moves at frame 0;
  - an early hook peak;
  - a drop at about 40% (the loudest moment);
  - a lull at about 65%;
  - the biggest visual peak at about 82%;
  - the ending subtracts: the music stops on the bar line, then one soft hit as the name becomes readable.
- **Bookend or callback.** The ending answers the opening, in words and in image.
- **Assets must be legal:**
  - public domain or CC0: the Met Open Access API (v1.1 search), credited in `CREDITS.md`;
  - the brand's own marks (simple-icons);
  - free-licence music (Mixkit) with a measured BPM.
- **Never lose a render:** send it in chat, copy it to `renders/`, commit, and add a journal entry with Jason's score.

## Pipeline
1. **Reference decode** (if Jason sends or names one):
   - Download it. prompt-motion.com pages hold `media.prompt-motion.com/.../video.*.mp4`; YouTube may be bot-blocked, so fall back to the transcript and storyboards.
   - Make 4 fps and 15 fps contact sheets, then run `tools/bpm.py` / `tools/grid.py` on the audio.
   - Write the decode: shots, durations, device, accent use, type, seams, polarity flips, 3D, ending.
2. **Brand research:** marks (simple-icons), colours and type from the brand's own materials and campaigns. Record any brand-supplied exceptions (orange accent, serif) against the bans.
3. **Concept**, in 3 sentences: Idea (8 words or fewer), Device (with state), Grammar. Run the kill tests (ownership, muted, poster, one sentence, specificity). Write the logline.
4. **Assets:**
   - `tools/metpull.py` / `tools/metpick.py` (CC0);
   - `tools/engrave.py` with the rembg venv, for grayscale, paper knockout and cutouts;
   - make a contact sheet;
   - pick anchors on a gridded sheet: the point of each asset where the device lands (an eye, a quill tip, a fingertip, a vanishing point).
5. **Beat sheet** on `K.grid(120)`: beat = 30 f, bar = 120 f. List every shot (asset, anchor, entry seam, exit seam), every device state change, every word (t, text) and every cue. Use 6–8 seam types, each at most twice.
6. **Build** from `kit/kit.js` + `examples/claude-ad-v2/ad2.html`:
   - images are anchored to the device (`K.anchor`), so every cut lands the eye;
   - the device is drawn by one function of the frame;
   - words via `K.maskLine` / `K.morphLine`;
   - pen strokes and compass rings via `K.drawOn`.
7. **QA round** (at least 2 rounds, at most 5):
   - stills at every beat;
   - a sharp pass;
   - `tools/qa.py` forensics (pops, stalls, holds > 48 f, a still opening, device absent, accent %) plus 12 fps sheets;
   - the director pass against `craft-rules.md` §8 (bans) and §11 (rubric).
   - Fix by impact.
8. **Final render:**
   - `tools/blurplan.py` (optical-flow speeds → per-frame samples);
   - `tools/render2.js` for the sample pass;
   - `tools/blend.py` for float averaging with dither;
   - encode with ffmpeg, BT.709-tagged (CRF 14, slow).
9. **Sound:** `tools/mix2.py`.
   - Cue frames come from `window.CUE_LIST()` in the page.
   - Every effect is placed by its measured peak.
   - Same-class sounds share one level (all ticks equal).
   - Master at −14 LUFS, true peak −1.5 dBTP.
   - Deliver two files: with music, and SFX-only.
10. **Deliver:** send both files, then `renders/mg-<brand>-ad-vN-*.mp4`, a journal entry, and ask for his score. Any choice he approves becomes a rule here.

## Kit
- `kit/kit.js`:
  - `K.grid`, `K.E` easing tokens, `K.bez`, `K.lmix` (log-space zoom), `K.hit`, `K.crit`;
  - `K.maskLine`, `K.morphLine` (kerned shared-letter morph);
  - `K.anchor`, `K.svg`, `K.drawOn`.
- `tools/`:
  - `render2.js` (plan-driven Playwright renderer);
  - `blurplan.py`, `blend.py`;
  - `qa.py`;
  - `mix2.py`;
  - `metpick.py`, `engrave.py`;
  - `bpm.py`, `grid.py`.
- `examples/claude-ad-v2/`: the reference build ("the spark, collected one ray at a time").
