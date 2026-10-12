---
name: jason-motion-graphics
description: Jason's standalone motion-graphics pieces. NO raw footage of him. Use when Jason asks for a motion graphic, UI animation, one-shape morph loop, kinetic typography, app/iPhone UI demo, animated explainer or a Dribbble-style motion piece, or pastes a brief with inputs, direction, structure and build sections. Output is a finished, beat-synced, looping MP4 built from code (pure seek(t) HTML engine or Remotion). If Jason sends raw talking-head/vlog footage to cut and caption, use jason-video-editor instead (graphic cutaways inside a footage edit stay in that skill).
---

# Jason Motion Graphics — SOP

> **THE EDITING STANDARD: r21 Netflix film (Jason, 2026-10-12: "this is the video editing standard"):** one continuous camera where every scene morphs into the next (shared elements, push-through blur, slit-scan; no hard cuts, no plain crossfades); one signature transition in the brand colour, used repeatedly; open and close on the same build (callback); ~300 ms of silence before the final drop; real UI, cinematically lit; rack-focus depth; VO of 8 short second-person lines on visual beats; two-line kinetic type with a brand-colour accent word, shimmer and an underline draw; a new idea every 1–1.5 s with one breath before the payoff; exit dot → line → credit. Full decode: `../jason-ad-film/references/r21-netflix-standard.md`.
>
> **STYLE LIBRARY (Jason, 2026-10-12: "label as such so we know the standard and references"):** every approved look has a label: see `STYLES.md`. Always on: **EASING** (r22: entrances ease-out, exits ease-in, moves ease-in-out; **pops, buttons, icons and morph landings get a single ~10% overshoot**, which replaces "no bounce" for pops only; linear only for machines). **HOOK PSYCHOLOGY** (r24: hook → delay → rehook ~midpoint → delay → payoff → end immediately; never answer the hook straight away). **BRAND ASSETS** (r25: any brand named directly or clearly implied gets its real logo, colours and animated UI flow, in the BRAND STORY style; never a generic icon or a fake brand). **VOICE CHAIN** (r26: every voice gets high-pass → expander → de-esser → EQ +3.5 kHz → compressor → limiter, in that order; `voice_enhance.py`). **COLOR TRIAD** (r27: thumbnails, covers and hook frames use one 120°-apart pair picked by emotion). Named looks: NETFLIX/CONTINUOUS, BRAND STORY, DOC-PAPER 3D, ENGRAVING, READING BALL, COOP, iOS, BLUEPRINT.

> **SKILL UPKEEP (Jason, 2026-10-09):** Jason's claude.ai account copy of this skill is the MASTER; it is what loads in Claude chat, the Claude app and every Claude Code session. Editing the repo (or `~/.claude/skills/synced/`, a read-only download) does NOT update his account. After every approved change: edit the repo skill → run `bash skills-sync.sh <outdir>` at the repo root → send Jason every zip it marks "NEEDS RE-UPLOAD" and tell him to replace that skill at claude.ai (Settings → Capabilities → Skills). Never report a skill as updated until he has re-uploaded it.
>
**Which skill?** (Jason, 2026-10-09: "we need 2 skills for distinguishing the type of edits")
| Jason sends… | Skill |
|---|---|
| Raw footage of himself (talking head, car vlog, screen recording with his voice) to cut, caption, add SFX | `jason-video-editor` |
| A brief or idea for a pure motion piece (UI morph, kinetic type, animated UI, explainer graphic, loop), no footage | **this skill** |
| A footage edit that needs graphic cutaways | `jason-video-editor` (its Coop look + kits); borrow this skill's engine only for a standalone insert |

**Start here:** read `references/journal.md` (motion-graphics scores and lessons) and `references/mg-quality-bar.md` (r05 quality bar + iOS language).

## Non-negotiables (Jason's rules for motion)
- **Smooth, never laggy (Jason, 2026-10-09).**
  - 60 fps from 4 blended subframes (180° shutter) for HTML pieces.
  - 30 fps + `CameraMotionBlur` for Remotion pieces.
  - Never step frames (the 12 fps "cinematic" look felt laggy to him).
- **Springs, no wobble.** Closed-form step responses, damping ratio ≈ 0.88-1.0; a tiny overshoot at most. Banned: bouncy easing.
- **iOS-coded language** (Jason loves it):
  - borderless soft cards, big continuous radii, soft shadows;
  - real iOS patterns: Dynamic Island, notifications, toggles, segmented controls, swipe-to-delete, ⌘K/Spotlight;
  - real sounds (`ios_*`).
- **Real assets only.** Real logos and icons (simple-icons or fetched from the web), consistent icon stroke (1.9 on a 24 grid), never placeholder boxes.
- **Colour:**
  - pure black/white plus ONE accent;
  - the accent means something (gold = key idea, green = win, red = problem);
  - banned: glows, gradients on UI chrome, particle bursts, template looks.
- **Text:**
  - Inter Variable (our SF-Pro stand-in);
  - every text that swaps inside a morphing container gets its own enter/exit window with a short blur, so nothing overlaps;
  - only Jason's own words or neutral UI chrome on screen. Any invented number (e.g. a chart stat) is flagged to him before posting.
- **Format:** 1080×1920 vertical unless he asks otherwise. The camera zooms so each state fills the frame.
- **Something happens on every beat.** Measure the song's beat grid with numpy (`engine/bpm.py`, `engine/grid.py`) and start on a downbeat. Place every UI sound by its measured peak (`engine/mixmorph.py`).
- **Loops:** the last frame equals the first, cursor position and speed included. Check frame 0 against t = LEN−ε: the mean pixel difference must be < 0.01. Every spring started near the end must settle before LEN, the camera included.
- **Music:** deliver two files: **with music** (to judge timing) and **SFX-only** (for posting; he adds the trending track in TikTok).
- **Never lose a render:** send it in chat, copy it to `renders/mg-<title>-vN-*.mp4` (Git LFS), commit, and log it in the journal with his score.

## Workflow
1. **Brief.** If Jason pastes a brief, follow it adapted to our context: his premise as the story, his words, vertical, iOS language. If it's just an idea, use `references/brief-template.md`.
2. **Ask for the inputs** (states 8-12, B/W or one accent, a 120-ish BPM royalty-free song). If he says "let's do it" without them, use the defaults (his premise as states, B/W + gold, a Mixkit track measured for BPM) and say so.
3. **Show the state list on the beat grid** (bar × beat table) before writing code. Get his OK.
4. **Build on the engine** (`engine/morph.html`): copy it, replace the state table `S`, the content blocks, `WIN`, the cursor keys `CK` and the interactions. Keep the engine rules:
   - pure `seek(t)`, no CSS transitions or timers;
   - one spring per target change, summed (`track()`);
   - two-edge springs on stretchy elements (leading edge fast, trailing slow);
   - direct-manipulation drags (the value comes from the cursor while held; on release it springs from wherever it was);
   - no `will-change` on anything the camera scales.
5. **QA before the full render:**
   - `node render.js stills beats <one t per beat>` → contact sheet;
   - `node render.js stills tr <transition times>` → check the in-between frames;
   - loop seam check.
   
   Fix anything off-grid, cramped, overlapping or hard to read.
6. **Full render:**
   - `node render.js full sub 6`, then ffmpeg `tmix=frames=4` + select every 4th → 60 fps. Re-render only a time range with `T0=… T1=…` after a fix.
   - Audio: `python3 mixmorph.py song.mp3` (edit `EV` per piece) → `fx_only.wav` + `with_music.wav` at −14 LUFS → mux.
7. **Deliver** both files, commit, add a journal entry, and ask for his score. When he approves a choice, it becomes a rule here immediately.

## Kits you can reuse
- `engine/`: the HTML one-shape morph engine (Playwright render, numpy beat grid, peak-placed SFX). Reference piece: "Just Post" v1.
- Remotion kits in `../jason-video-editor/template/src/lib/`:
  - `IosNotify.tsx`: pixel-accurate iOS notifications;
  - `Glass.tsx`: frosted cards, Stage3D, Whip;
  - `Coop.tsx`: stage, glow, grain, cutaway graphics;
  - `Blueprint2.tsx`: bloom, parallax, HUD.
- SFX library: `../jason-video-editor/assets/sfx/` (`library.json`, 77 sounds; sound leads the picture by 0-2 frames, never trails).
