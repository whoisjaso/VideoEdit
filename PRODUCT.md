# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Creators who record long talking-head footage (podcasts, car vlogs, talks, teaching content) and
want short vertical clips for TikTok, Reels and Shorts without editing by hand. The primary user is
Jason, the project owner: a creator and operator who wants to drop an hour of footage, get clips in
his established edit style, and give one-tap feedback. Secondary users (inferred from the open-source
positioning, not yet confirmed): other creators and the AI agents (Claude over MCP) that edit on a
creator's behalf.

## Product Purpose

Kairos turns long videos into short clips cut in the owner's house style, and learns from every
score and note. Success is a clip the creator would post as-is, with less time spent than any manual
editor, and a style that gets closer to their taste with each round of feedback.

## Positioning

Agent-native: Premiere's sequence model stripped to primitives an AI agent can drive (one JSON
timeline per clip, every edit addressed by spoken words, 28 MCP tools). The video never passes
through a chat window, so the 30 MB chat-upload limit does not apply. Open source (MIT).

## Operating Context

- Runs locally: `python -m kairos serve` on a machine with Python 3.10+ and ffmpeg. Whisper
  transcribes on CPU at roughly real time.
- Works offline with a built-in heuristic editor; connecting an Anthropic API key makes moment
  picking and titling sharper.
- Agents connect with `claude mcp add kairos -- python -m kairos mcp`.
- The edit recipe comes from `.claude/skills/jason-video-editor` (a playbook decoded from reference
  reels; the best hand-built episode scored 8.3/10).

## Capabilities and Constraints

- Resumable chunked upload, link or path import, any length.
- Auto-edit: dead-air cuts that keep pauses, cold open, hook title, raw word-level captions with
  meaning-colored keywords (gold idea, mint money/wins, coral problems), punch zooms, curse slow-mo,
  money pop-ups, riser into the payoff, follow CTA, color grade, -14 LUFS.
- Color looks, LUTs, match-to-reference. Premiere XML and SRT export.
- Feedback loop: 1-10 score, quick-fix chips, free text; bounded style parameter changes; lessons.
- Captions are raw and never censored. Low-confidence words are flagged, never guessed.
- Limits: text-behind-speaker needs the separate Remotion path; Blender 3D titles are optional.
- Undecided: hosted/cloud version; domain name; pricing (none today; open source).

## Brand Commitments

- Name: Kairos. Angle: *kairos* (the right moment) versus *chronos* (clock time). The hour, and
  the moment lifted out of it.
- The moment mark: a ring with one slice lifted out, ink ring and gold slice (`web/icons/`).
- Kai: the clapperboard mascot (`kai()` in `web/fx.js`).
- Palette is the edit's palette: gold `#ffc21a`, mint `#2be37a`, coral `#ff3b3b`, ink `#14131a`,
  paper `#fffdf7`. One accent per screen, no blue.
- Type: Outfit (OFL, bundled). Voice: short editor's lines ("Clean take", "That's a wrap").
- Mechanics borrowed from Duolingo (lip buttons, feedback bar, celebrations, streaks); Duolingo's
  trademarks, typeface and assets are not used.

## Evidence on Hand

- Real app screenshots over real footage: `site/img/home.png`, `format.png`, `wrap.png`,
  `clips-dark.png`.
- Real auto-edited clips from raw episode 4 (3.5 min car vlog): `site/img/hero.mp4` (11 s loop),
  `site/img/clip-1..3.jpg` (poster frames). Titles and durations are real output.
- No testimonials, customer logos, user counts or benchmarks exist. Do not invent any.
- Jason's own scores: none recorded yet for auto clips (the hand-built best is 8.3/10).

## Product Principles

1. Three taps from a video to clips; everything else is a remembered default.
2. The owner's style is the product. Feedback is the main input, and it must feel rewarding.
3. Raw is the brand. Never soften the creator's words.
4. Built for agents first; the human UI is the simplest possible face on the same engine.
5. Show real output. No mockups, no invented numbers.
