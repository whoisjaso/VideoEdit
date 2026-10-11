# Kairos

**Long videos in. Clips that hit, out.**

Kairos is an open-source, agent-native video editor. Drop in an hour-long podcast, a vlog or a talk.
Kairos finds the moments worth posting, cuts each one into a vertical short in your house style, and
learns from every score and note you give it. The app is simple, one question per screen. Behind
it, an engine built for AI agents does the editing: Claude reads the transcript, places every cut,
caption, sound and grade, and explains why.

> *Kairos* (καιρός): the right, appointed moment. The whole job is finding it.

## Why it exists

- **No 30 MB wall.** Chat apps cap uploads at about 30 MB (roughly 90 seconds of phone video). Kairos
  takes any length: the browser uploads in resumable 8 MB chunks straight to your Kairos server, or
  you paste a link or a file path. Claude edits it over MCP, so the video never passes through a chat.
- **Editors weren't built for agents.** Premiere, After Effects and CapCut are built around a mouse.
  Kairos is Premiere stripped to the primitives an agent needs (see [docs/TEARDOWN.md](docs/TEARDOWN.md)):
  one JSON EditGraph per clip, every effect addressed by spoken words, and every sound cue tagged
  with the rule that placed it.
- **Your style, not a template.** The default style is the decoded "8.3 standard" from
  `.claude/skills/jason-video-editor` (the playbook built from 22 reference reels). Scores and notes
  tune it, and every lesson is written down and applied to the next edit.

## Run it

```bash
./start.sh                  # one command: venv, install with Whisper, start, open the browser
```

Or by hand:

```bash
pip install -e ".[all]"     # Python 3.10+ and ffmpeg on your PATH; Whisper captions, face reframe, yt-dlp links
python -m kairos serve      # open http://localhost:8787
```

Connect Claude in **Settings** (paste an Anthropic API key) or set `ANTHROPIC_API_KEY`. Without
Claude, everything still works with the built-in editor (heuristic moment picking, offline prompt cleanup).

**Command line:** `python -m kairos run podcast.mp4 --count 5 --length medium --final`

## Use it from Claude (the agent editor)

```bash
claude mcp add kairos -- python -m kairos mcp
```

Then ask: *"Import ~/Videos/episode12.mp4, find the 5 strongest moments, edit them in my style, and
show me stills of each hook."* The MCP server exposes 28 tools: import, analyze, transcript, find
moments, create clip, ripple cut, zoom, shake, SFX, graphics, caption fixes, grade, render, stills,
Premiere export, style rules, feedback learning, idea enhancement and Blender 3D titles.

## How it looks and feels

Three taps from a video to clips: drop it, pick a format, go. Everything else is a default you can
change under "More options".

The mechanics come from a teardown of Duolingo (chunky lip buttons, a feedback bar that turns green,
a celebration with stat cards, streaks). The look is Kairos's own (see [docs/DESIGN.md](docs/DESIGN.md)):
the moment mark (a ring with one slice lifted out), the palette the edits themselves use (gold, mint,
coral) on warm paper by day and ink by night, Outfit type, and an editor's voice. Sounds are
synthesized and haptics work on Android and iOS 18+. Kai, the clapperboard mascot, walks you through it.

## What the app does

| Screen | What you do |
|---|---|
| **New clips** | Drop a video or paste a link, then answer six one-tap questions (about, count, length, style, look, rules). The upload runs while you answer. |
| **Processing** | Watch one ring and five steps: reading, listening, finding moments, editing, rendering. You can leave the page. |
| **Your clips** | A vertical feed. **Adjust**: score 1–10, tap quick fixes, or just say what's wrong, and it re-edits. **Look**: grades previewed on your own footage, with strength and match-to-reference. **Keep**: full-quality MP4, a Premiere XML or SRT captions. |
| **Idea → Prompt** | Ramble (type or talk). You get back a clear vision, hook options, beats and a production-ready prompt for video, image, edit or script. |
| **Library** | Sounds (preview every SFX with the job it does), Looks (add `.cube` LUTs), References (reels to study, your follow-card photo) and Prompts. |
| **What I've learned** | Every lesson and parameter change from your feedback, plus your score trend. |

## The edit (what the engine does to every clip)

1. Cut dead air but keep your pauses (only gaps over 1.4 s are shortened, to 0.75 s).
2. Cold-open on the payoff line when there is one (an open loop), then play the clip in your order.
3. Put the hook title in big type with a bass impact and an impact shake.
4. Captions are raw and word-by-word. Keyword colors carry meaning: gold for the idea, green for money and wins, red for problems. Gold is rationed.
5. Punch zooms with an overshoot spring, and every zoom gets a whoosh.
6. Punchline curses get the 0.5x slow-mo with an octave drop. Slurs are never slowed.
7. Money gets a pop-up (`seven thousand dollars` → **$7,000**) with pop, click and register sounds.
8. A riser ends exactly on the payoff word, followed by a reveal sting.
9. The follow card shows your photo, and the bell rings when Follow flips to Following.
10. Grade (Moody by default), then a -14 LUFS mix with a limiter.

## Layout

| Path | What it is |
|---|---|
| `kairos/` | The engine: `timeline.py` (EditGraph), `autoedit.py` (the recipe), `render.py` + `ass.py` (ffmpeg/libass renderer), `grade.py`, `moments.py`, `learn.py`, `prompts.py`, `blender.py`, `export.py`, `server.py`, `mcp_server.py` |
| `web/` | The app: plain HTML/CSS/JS, no build step. `web/icons/` is the icon set (`node tools/make_icons.mjs` regenerates it from the mark) |
| `site/` | The landing page, standalone and GitHub Pages-ready. Served by the app at `/site/` |
| `docs/TEARDOWN.md` | Premiere Pro, After Effects (via EffectCraft) and Blender mapped to agent primitives |
| `tests/` | `python -m unittest discover -s tests` |
| `.claude/skills/jason-video-editor/` | The editing SOP, the decoded playbook, the scored journal, the SFX packs, and the Remotion recipe for hand-built 8.3-level episodes |
| `renders/`, `raw/` | Finished MP4s and source footage (Git LFS) |
| `data/` | Runtime data (projects, uploads, learned styles). Git-ignored |

## Honest limits (v0.1)

- **Captions need a transcriber.** `faster-whisper` is the default (`small.en` runs at roughly real
  time on a CPU; set `KAIROS_WHISPER=base.en` for about 2x speed). Without one, clips are picked by
  speech energy and have no captions. Words the recognizer isn't sure of are flagged on each clip
  ("2 words to check") so you confirm them before posting.
- **Offline vs Claude.** With no API key, moments come from a heuristic (thesis lines, clean
  sentence starts, cold opens, topic titles). It found the "perceived as nice" core on real footage,
  but Claude picks and titles far better.
- **No text behind the speaker yet.** The fast renderer can't place text behind a person; that
  still needs the skill's Remotion and matte path. Lottie graphics are on the roadmap.
- **Blender is optional.** The 3D templates are written and wired in, but haven't been rendered in
  CI because Blender isn't installed there.
- **Stand-in sounds.** SFX are matched to each job. Drop your exact CapCut exports into the Library
  and they become available by name.

## Rules carried over from the skill

- A render isn't done until it's delivered **and** pushed to `renders/`.
- Raw is the brand: never bleep, mute or asterisk.
- Every choice you approve becomes a written rule.

MIT licensed.
