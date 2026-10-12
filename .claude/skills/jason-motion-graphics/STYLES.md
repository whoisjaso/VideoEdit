# STYLE LIBRARY: ask for any look by its label
Every approved editing type has a **label**, its **reference** and its **rules**. Say "make this DOC-PAPER 3D" or "BRAND STORY this part" and the rules below apply.
Paths are relative to `.claude/skills/`.

## Editing styles (pick one per piece or section)
| Label | What it is | Reference / rules |
|---|---|---|
| **NETFLIX / CONTINUOUS** | THE editing standard: one continuous camera, every scene morphs into the next, a signature brand-colour transition, callback ending | `jason-ad-film/references/r21-netflix-standard.md` |
| **BRAND STORY** | Real brand assets told as one travelling UI morph (iMessage → app icon → search → tiles → status → map → wordmark) | `jason-motion-graphics/references/r25-brand-story.md` |
| **DOC-PAPER 3D** | Documentary paper explainer: B&W photo cutouts in 2.5D parallax, case files on a lit desk, red highlighter, timeline scrub | `jason-motion-graphics/references/r23-doc-paper-3d.md` |
| **ENGRAVING** | Antique public-domain engravings on paper, one orange accent device, bold serif lines (Claude ad, *The Ego of the Greats*) | `jason-ad-film/references/decode-engraving-claude-ad.md` |
| **READING BALL** | A sleep-pace film with a reading orb that follows the words and shape-shifts into symbols (crown, scales, ?, laurel) | `jason-video-editor/kinetic/README.md` |
| **COOP** | Near-black stage, glow + grain, hard cutaways alternating with the face, lowercase captions with an italic-serif accent | `jason-video-editor/references/cooperson-decode.md` |
| **iOS** | Frosted borderless cards, soft shadows, shared-element morphs, real iOS sounds | `jason-video-editor/SKILL.md` (iOS rule), `Ios.tsx` |
| **BLUEPRINT (r05)** | Navy blueprint world, bloom, line-draw diagrams, orange spoken-word sweep | `jason-motion-graphics/references/mg-quality-bar.md` |

## Standards that apply to everything
| Label | Rule | Reference |
|---|---|---|
| **EASING** | Entrances ease-out, exits ease-in, moves ease-in-out; pops, buttons, icons and landings get a single ~10% overshoot; linear only for machines | `jason-motion-graphics/references/r22-easing.md` |
| **HOOK PSYCHOLOGY** | Hook → delay 1 → rehook (~midpoint) → delay 2 → payoff → end immediately; never answer the hook straight away | `jason-motion-graphics/references/r24-hook-psychology.md` |
| **BRAND ASSETS** | Any brand named directly or clearly implied gets its real logo, colour and UI flow | `jason-motion-graphics/references/r25-brand-story.md` |
| **VOICE CHAIN** | Every voice: high-pass → expander → de-esser → EQ (+3.5 kHz) → compressor → limiter, −14 LUFS | `jason-motion-graphics/references/r26-voice-chain.md`, `jason-video-editor/scripts/voice_enhance.py` |
| **COLOR TRIAD** | Thumbnails, covers and hook frames use one triad pair (red+blue, yellow+blue, yellow+red, orange+green, purple+green) | `jason-motion-graphics/references/r27-color-triad.md` |

**Adding a style:** decode the reference → write `rNN-<label>.md` → add a row here → add one rule line to each SKILL.md.
