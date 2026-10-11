---
name: jason-video-editor
description: Jason's default short-form video edit. Use EVERY time Jason drops raw footage (talking head, car/selfie vlogs, motivational, teaching "game", business/AI content, screen recordings) to edit, cut, caption, add SFX/motion graphics, or "make it hit". Turns raw vertical footage into a finished 9:16 reel. It opens with a hook, cuts dead air and stutters, uses raw uncensored captions with gold keywords, and puts slow-mo on curse words. It pairs every event with the right SFX, adds font-combo titles with text behind the speaker, pops up graphics, and ends on an animated follow CTA. Everything follows the decoded creator playbook in references/playbook.md. Also use when Jason sends more "use this for that" reference videos to study; decode them and extend the playbook. NOT for standalone motion-graphics pieces with no footage of him (UI morph loops, kinetic type, animated UI from a brief): use jason-motion-graphics for those.
---

# Jason Video Editor — SOP

> **SKILL UPKEEP (Jason, 2026-10-09):** Jason's claude.ai account copy of this skill is the MASTER; it is what loads in Claude chat, the Claude app and every Claude Code session. Editing the repo (or `~/.claude/skills/synced/`, a read-only download) does NOT update his account. After every approved change: edit the repo skill → run `bash skills-sync.sh <outdir>` at the repo root → send Jason every zip it marks "NEEDS RE-UPLOAD" and tell him to replace that skill at claude.ai (Settings → Capabilities → Skills). Never report a skill as updated until he has re-uploaded it.
>
> **TWO SKILLS (Jason, 2026-10-09):** this skill = edits of his raw footage (cut, captions, SFX, graphic cutaways). Standalone motion pieces with no footage (UI morph loops, kinetic type, animated UI from a brief) → `../jason-motion-graphics/SKILL.md`.

> **THE BAR:** playbook §18 ("My work vs Original"): every sentence gets a designed visual beat, nouns become full-screen editorial cards, giant hero words go behind the speaker, numbers roll, one accent color sits on a moody grade, and there's editorial micro-type. Jason called it the standard he expects. Plan every edit against it.
>
> **Visuals:** for every edit, output an image prompt pack (see `references/image-prompts.md`: style lock + one prompt per picturable noun). Jason generates the images (ChatGPT, or the Higgsfield connector when he approves credits) and they fill the §18 cards.
>
> **MOTION-GRAPHICS LANGUAGE = iOS (Jason, 2026-10-08: "iOS-like UX, soft borderless animations"):** r05 sets the *quality* (bloom, smoothness, depth, micro-detail); iOS sets the *look*: frosted borderless cards, big continuous corner radii, soft layered shadows, no hard outlines, critically-damped springs (no bounce), fade+scale 0.96→1+blur entrances, shared-element morphs (pill → card → full screen, Dynamic-Island style). Hard-lined HUD boxes are out; detail comes from iOS-native micro-UI (status bar, captions, SF-symbol-style glyphs, progress rings, segmented controls).
>
> **MOTION-GRAPHICS QUALITY BAR (Jason, 2026-10-08: "this is the quality I expect"):** reel r05, decoded in `../jason-motion-graphics/references/mg-quality-bar.md`: one navy-blueprint world with bloom and micro-labels, every sentence turned into a literal diagram, spoken-word orange sweep, comets along lines, line-draw everything, full-screen word slams. Every motion graphic is judged against it.
>
> **THE METHODOLOGY (Jason, 2026-10-08):** `references/methodology.md`, decoded from his 12 reference reels (psychology, hook shapes, typography, color, motion, SFX↔animation timing, audio craft, CTA). Plan every edit against it; locked rules below still win where they conflict (the conflicts are listed at the end of that file).
>
> **COOP PRESET (r13, Jason Cooperson, sent 2026-10-09):** `references/cooperson-decode.md`. Lessons: (1) **presets = saved values**: every look is a kit file of fixed constants; beats reuse kit components, never hand-animate from scratch; after every edit, "bake it in" (rule + journal + kit commit). (2) The look kit `template/src/lib/Coop.tsx`: motion graphics on a **12 fps grid** (`useStep`), **glow on every graphic + grain on everything**, near-black stage with a blue→violet light band, full-screen **hard cutaways alternating with his face**, lowercase captions with one **italic-serif accent word** (`CoopCaptions`, Instrument Serif), real assets only. (3) Warm grade on camera footage only. (4) Master speech at **−17 LUFS, SFX ≤ −1 dBTP**. (5) Proof-first psychology: show the claim, exact numbers, objections answered early. Sample: `examples/mg-quality-sample/CoopSample5.tsx` → `renders/mg-coop-sample-v5.mp4`. **LOCKED (Jason, 2026-10-09: v5 "I like this", 7.7/10, best motion-graphics score so far):** the Coop look is the default for motion graphics: **smooth 30 fps motion + motion blur (Jason, same day: the 12 fps stepping "felt laggy"; never step frames)**, no-wobble springs, glow + grain, hard cutaways alternating with his face, a warm camera grade, −17 LUFS. Lowercase captions with the italic-serif accent word come with it (accent colour = our meaning colours). Start every MG beat from `Coop.tsx` + `CoopSample5.tsx`; the iOS components (IosNotify, Glass cards) stay as content *inside* the Coop stage.
>
> **ENGRAVING CUTAWAYS (Jason, 2026-10-09: "I would love this type of motion graphics on my talking heads, for certain portions, with the iOS sound effects"):** the antique-engraving look from `../jason-ad-film` is an approved cutaway style for talking heads. Use it on 2–4 portions per video: the big idea, a definition, a "think about it" turn, or the payoff. Pick public-domain engravings that literally match his words (`../jason-ad-film/tools/metengr.py` → `engrave.py`) on a white stage. One orange accent device travels between them and lands on the key point of each engraving. Bold serif words, one line at a time, are his own words. Cut in and out on his sentence boundaries; his face carries the rest. **Sound for these portions stays iOS** (tink on each accent landing, tri-tone or received for a notification beat, success on the payoff), placed by measured peak. Never music.
>
> **SOUND SPEC + GEARS (Jason, 2026-10-11: "our SFX is decent but not pinpoint; we only use a little portion of the library"):** read `references/r20-editing-masterclass.md` (Inside The Edit pacing, Netflix-style doc sound design, Max McCoy story-first). The short version:
> - **SFX levels sit under his voice:** ticks −30 to −40 dB, textures −28 to −35, whooshes about −24, iOS −16 to −20, bass about −20 across 3 layers. Nothing hotter than −14 except a planned drop.
> - **Layering:** hero sounds use low/mid/high (one whoosh at 60% speed −5 st + texture + 120%). Bass starts 2–4 frames early.
> - **Variety:** alternate variants; the last hit of a sequence is the biggest. Use at least 6 of the 13 jobs, texture and tech included.
> - **Silence and holds:** 0.3–0.8 s of silence before the biggest line. Reverb-end instead of hard stops. Hold 0.5–1.5 s at complex and emotional moments (tag `hold`).
> - **Build order:** sound bed first, graphics placed onto it.
> - **Mix stage (the tool):** never set SFX volumes by guess in Remotion. Write a cue list (`examples/chosen-episode/ep05_cues.py` is the template: `whoosh3`, `bass3`, alternating ticks), render the picture, then `python3 scripts/mix_talk.py work/cut.mp4 cues.json assets/sfx/library.json assets/sfx mix.wav --len_s <total s>` and mux the result over the picture. It levels each sound by role relative to his voice, aligns by the measured peak, layers, adds reverb tails, ducks under him, and masters to −14 LUFS. Check: the SFX stem is about 14–17 dB under the voice.
>
> **DUAL TYPE (Jason, 2026-10-10: "do v2 on that plan, dual fonting"):** every edit uses exactly two families: **Inter** (sans, 700–900, for everything plain) and **Instrument Serif italic** (the accent word, gold). One accent colour: gold (red only for hard "no" words). No Nunito, Bebas, Anton or Montserrat. Captions = `CoopCaptions` (lowercase Inter + serif accent). Hero words, cards and engraving lines use the same pair.
>
> **ENGRAVING CUTAWAYS v2 (2026-10-10):** the plates are dimmed positive prints on a dark stage with a vignette (no white page: v1's white flashes broke the world). Engraving `ins.html` uses Inter + Instrument Serif and a gold device. Every insert gets a 5-frame blur-dissolve in and a 4-frame one out (`Insert` in `examples/chosen-episode/Episode.v2.tsx`), plus a swoosh on the bridge.
>
> **HOOK CARD + CALLBACK (2026-10-10, psychology):** open on a full-screen kinetic-type card of his boldest line over the dimmed footage (open loop). Bring back the SAME card when he says the line at the payoff (closes the loop).
>
> **READING BALL + KINETIC TEXT (LOCKED, Jason 2026-10-11: "the motion graphic ball moving around with these captions and pointing at specific things... beautiful... probably one of the best type of work you've done so far"):** narrated and long-form pieces get word-timed kinetic captions plus ONE gold reading ball. The ball hops word to word as each word is spoken, with a motion-blur streak, then springs off the text in a high arc to whatever the story points at, lands with a squash and a drawn ring, and returns to the words. Hero lines arrive letter by letter with a light sweep and lift away. Every text entrance gets sound. Spec, timings and code: `kinetic/README.md` (reference build `kinetic/proof.html`). The world sound is real public-domain/CC0 recordings (`kinetic/world.py`) placed on the words, and score cues follow the story's emotional turns.

> **SCORECARD (Jason, 2026-10-10: "break the video into categories, psychology included, so we know where to revise"):** before delivery, score the final render on `references/scorecard.md` (10 weighted categories, measured from the 1 fps sheet). Fix any category under 7, and send the scorecard with the video.
>
> **Start here:** read `references/journal.md`. It holds the scored history (current best **8.3/10**, episode #3), what Jason loved (locked), his corrections, and the backlog. Every new edit should beat the best score. After delivery, ask for his score and log it.

The goal is an edit that makes the viewer stay, feel something, and act. It should match Jason's style exactly, with no need for him to ask for any of it.
Every choice below has a *reason*. If a choice has no rule or reason behind it, it doesn't go in the video.
The rules come from `references/playbook.md`, which was decoded frame-by-frame from the creator Jason studies. **Don't invent effects.**

## Jason's non-negotiables
- **Never lose a render (Jason, 2026-10-01).** The moment a final MP4 exists: send it to Jason, then copy it to `renders/epNN-short-title-vN.mp4` (Git LFS) and push, *before* any further work. Raw footage goes to `raw/epNN/` (LFS) and is pushed as soon as it arrives. Sessions are ephemeral; anything unpushed is gone.
- **Raw is the brand.** Never bleep, mute or asterisk anything, n-word included. Captions show every word exactly as spoken. Mention reach risk at most once per project, then drop it.
- **Curse words get the comedic slow-mo:** 0.5x speed with an octave pitch drop, a push-in zoom, and a whoosh. This is Jason's own rule. Do it on the curses that land as punchlines (2–3 per video), not on every one. Never slow-mo a slur.
- **No background music in the render.** Jason adds a trending track in TikTok. Deliver voice + SFX only, and recommend a track from the playbook's music-by-mood list (§5).
- **Follow-card avatar** = Jason's headshot: `assets/avatar.png`. If it's missing, ask for it once.
- Cut dead air and stutters. Keep the retake, not the stumble.

## Jason's vocabulary (spell exactly)
- **ego archetype** (not "architect")
- nigga / niggas (not the hard-r the model outputs)

## THE 8.3 RECIPE: the default pipeline for every talking-head edit
Episode #3 scored **8.3**, the best so far. These are the exact steps that produced it. Follow them in order; every step is there because skipping it cost points in an earlier episode (see "Why each step exists" below). Start from this recipe, not from scratch.
```
bash scripts/setup.sh                                    # ffmpeg, Vosk, MediaPipe (+ DeepFilterNet notes in voice_enhance.py)
# 0. SAVE RAW FIRST: copy every raw part to raw/epNN/ (Git LFS) and push before any editing
# 1. CLEAN VOICE, per part (DeepFilterNet3 -> EQ -> comp -> -14 LUFS)
python3 scripts/voice_enhance.py p1.mov p1_voice.wav
# 2. TRANSCRIBE THE CLEAN VOICE (not the raw file; it fixes many mis-heard words)
PYTHONPATH=/tmp/stub python3 scripts/transcribe.py p1_voice.wav p1c/
# 3. WRITE sections.json BY HAND (see examples/purpose-episode/sections.json): his sections, in his order, exact words
# 4. CUT: keeps his pauses, shortens only dead air > 1.4s (to 0.75s)
python3 scripts/cut_sections.py sections.json work/      # -> work/cut.mp4, edl.json, captions.json
python3 scripts/check_voice.py work/                     # AUDIO GATE: must pass (0 words over silence) before anything else
# 5. PERSON CUTOUT for hero words behind his head
python3 scripts/matte.py work/cut.mp4 work/fg.webm work/edl.json
# 6. PROJECT: the 8.3 build, every asset in place
bash scripts/new_episode.sh proj && cp work/{cut.mp4,fg.webm} proj/public/ep/ && cp work/{captions.json,edl.json} proj/src/ep/
# 7. BEAT SHEET: rewrite proj/src/ep/Episode.tsx (it ships as episode #3's; keep the structure, replace the beats)
# 8. STILLS at every beat -> QA against the reference reels -> fix -> full render
# 9. DELIVER: send the MP4 to Jason -> copy to renders/epNN-title-v1.mp4 -> push -> journal entry -> ask for his score
```
Remotion needs `--browser-executable=/opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell` in the cloud container. Delete `/tmp/remotion-webpack-bundle-*` after each stills run, or the disk fills. **Never delete bundles while a render is running** (it reads assets from its bundle; deleting it killed the iOS v3 render at frame 565). Delete only the bundle a finished still/render made, or clean up after all renders end.
Never `pkill -f` a pattern that matches your own shell command. It kills the tool call; kill by PID instead.

**Step 3, sections.json (where the score is won or lost):**
- One entry per section of his argument, in **his** order: hook → problem → argument → payoff → CTA. Never reorder, never drop a key word.
- Cut only stutters, restarts, unclear asides, and dead air. His pauses are delivery; the script handles dead air.
- The text is his **exact** words. Mark keywords `^gold` (default), `+green` (money/wins), `!red` (problems). Wrap words a graphic will show in `{…}` so captions don't repeat them.
- Add every recognizer mis-hear to `alias` (heard → said) so caption timing still locks to his voice.
- **Word splices only on Jason's explicit request** (see "Never reorder his words"). Cut points still get a 40ms energy check (`snap`), and every changed stretch gets re-transcribed alone to confirm it says what the captions say.
- **Before rendering, send Jason a list of every word you're unsure of** (faith lines especially: a garbled word that could be "God" is asked, never guessed).

**Step 7, the beat sheet (template/src/ep/Episode.tsx):**
- **One designed motion graphic per sentence**, built from `src/lib/Mg.tsx` (Notes, iMessage banners, counters, tiles, Chess, Loop, Doors, Execute, CTA…) and `src/lib/Ios.tsx`. A new idea gets a new component in the same style; add it to `Mg.tsx` in the skill afterward.
- Time everything from his words: `at("section", "WORD", n)`. Never hard-code frames.
- **2–4 hero words behind his head** (`HERO`), colored by meaning. Check stills: the head clips at most 30% of the word.
- `HIDE` every caption window a graphic already says. `TOPS` moves captions clear of the graphic.
- **Sound map:** one line per event. Real iOS sounds 1:1 for UI moments, cinestrike/basscrack on the lines that land, riser into payoffs, shutter only on section changes.
- Real brand logos (`assets/logos/`, from simple-icons) for any app or company he names.

### Why each step exists (what each one fixed)
| Step | Episode that taught it | What went wrong without it |
|---|---|---|
| Clean voice + transcribe the clean audio | #3 | Background noise; mis-heard words ("psycho mcnugget" for "cycle, my nigga") |
| Exact confirmed words, ask before render | #2 v2 (7/10), #3 ("God") | Captions said something he never said |
| Keep his pauses, cut only dead air | #2 (7/10) | Over-cut, choppy; the message stopped making sense |
| His logic order, hook = his boldest first line | #2, #3 | Hook felt staged; argument felt broken |
| Motion graphics, not AI images | #3 (8.3) | #2's photo cards looked generic next to the reference reels |
| Captions always move | #2 (7/10) | Static captions felt dead |
| Real iOS sounds, real logos | #2 (7/10) | Synth chimes sounded fake |
| QA against the references before sending | #3 (8.3) | Weak beats shipped that would have been caught |
| Audio gate (`check_voice.py`) + capped denoise | #4 v1 | Denoise erased his quiet opening; a splice said "Nigerian elephant". Jason heard it before I did |

## Editorial pass (the thinking, done before any code)
1. **Read the whole transcript and name the video's one idea.** Example: "Label people → they commit → they buy."
2. **Find the payoff moment**: the result, the number, the close. **Find the thesis line**: the promise ("I'm going to teach y'all how to…").
3. **Hook = open loop plus pattern interrupt, both in the first 2–4 seconds.** Grade it with playbook §12: the **visual hook** has ≤6 elements, one metric, from→to, and proof. The **verbal hook** speaks to the viewer's want and promises value.
   - **Cold open:** take the payoff line itself, 1.5–3s of it ("It's seven thousand dollars. How would you like to proceed?"). Show the result before the method, which creates a curiosity gap that holds viewers until the payoff. The same seconds play again later: give the cold open its own keep-segment. cut.py maps captions per segment, so reused seconds are safe.
   - **Then the thesis line:** the taboo or direct promise, with a bass impact and a font combo. Something must move within the first 15 frames.
4. **Keep list:**
   - Cut warm-up ("what's up…"), stutters/retakes (keep the clean take), mumbled or garbled lines, and tangents that don't serve the one idea. Dead air: only gaps over ~1.4s, shortened to ~0.75s (his pauses are delivery; 8.3 rule).
   - Keep raw color that carries personality (e.g. the weed line). It's the brand.
   - Length follows the argument, not a percentage. For short-form, aim under ~1:50. Episode #3 kept every section whole and trimmed only dead air.
5. **Correct every caption line by hand from context.** The offline model mishears slang: it writes "nigger" for "nigga", "boys" for "voice", "she and robbers" for "shit and rob us". Write the text as Jason actually said it. Flag low-confidence spots to him.
   **But never "correct" a word the model heard clearly** (high confidence, real word) just because another word seems more likely. Example: the model heard "ego archetype", which is Jason's term; it was wrongly changed to "architect". Jason's own terms: see "Jason's vocabulary" below.
6. **Gold keywords are rationed.** Pick about 1 per idea, and only concept words (the words that, read in sequence, *are* the lesson). Don't gold a word every time it repeats, or viewers stop reading gold. Roughly 8% of words. Specify by `[WORD, occurrence]`.
7. **Beat sheet:** map every section to what fires. Use the table below, and derive every frame from a spoken word with `w("WORD", n)`, never from hard-coded numbers.

## SFX library (Jason: "make SFX library", 2026-10-08)
- **77 sounds sorted by job** in `references/sfx-library.md` (built from `assets/sfx/library.json` by `scripts/build_sfx_library.py`). Jobs: hook · impact · whoosh · shutter · click · typing · ios · win · reveal · build · negative · tech · texture. Every sound has a "use for", default volume and origin (real / lifted from a reference reel / synth stand-in).
- **Sound lands ON the frame.** Use `<Hit at={frame} id="pack6.impact_1" />` (`template/src/lib/sfx.tsx`). It starts the file early by its measured `lead`, so the **peak** (impact, whoosh, reveal, build) or the **onset** (iOS, click, typing, win) lands exactly on the motion. The references hit within 3-45 ms. Starting the file on the frame made CineStrike land ~16 frames late in eps #3/#4.
- **Pick by job, then rotate within the job** (button_1 → button_2 → combo) so repeats don't sound identical; keep the *same job* for the same event every time (conditioned reward).
- New packs: drop the wavs in `assets/sfx/packN/` with a manifest, add each to `CAT` in the build script, run it. The audition reel (`examples/sfx-demo/SfxDemo.tsx`) re-renders from the library.
- **Replace first:** the 6 `synth` stand-ins (pop, click, typing, kaching, ding, riser). The 18 `lifted` sounds are reference-grade; the clean packs come from commenting "SFX" on reels r10/r11.

## What fires when (the rules, with their source)
| Moment | Visual | SFX (his CapCut name → our stand-in) | Why |
|---|---|---|---|
| Hook / thesis line | font combo (Modern or Mozart), **text-behind-you**, zoom punch | **Bass impact** → `deep_bass` | reel 3/9: hooks and statements hit harder |
| A statement that must land | zoom punch | Bass impact | reel 3 "Core" |
| Every zoom-in | punch 1.0 → 1.14, hold, release | **swish_whoosh (large)** → `whoosh` | reels 5/6/9: every zoom gets a whoosh |
| Every cut between clips | zoom transition (incoming clip 1.14 → 1 + blur 10 → 0 over 6f) | **camera shutter (single shot)** → `camera_shutter` at ~0.28 | reel 6/9 transitions, reel 7 zoom transition |
| Across every clip | slow keyframed push 1.02 → 1.055 | — | reel 7: keyframes add smooth movement |
| Anything appears (pop-up, combo, ✓) | pop-up transition: scale spring with overshoot, rounded panel, drop shadow, glow text | **pop! (mouth tap) + Click! mouse single-click** | reels 3/5/6/9, the most-repeated rule |
| New caption line | — | **Keyboard Typing 01** → `typing` at ~0.16 | reel 9 |
| Build-up to a payoff | — | **RISER_01** → `riser`, *ending exactly on* the payoff word | reels 3/6 |
| Reveal (surprise, "you already won", hidden word) | combo or pop-up | **Metallic Riser / Magic reveal** → `riser` + `metallic_hit` / `synth_hit` | reels 3/6/9 |
| Money / numbers | gold pop-up of the number | **Money** → `kaching` | reel 3 |
| Curse punchline | 0.5x slow-mo + push-in, yellow keyword caption | whoosh (it's a zoom) | Jason's rule |
| Fast montage (cuts ≤ 8f) | one shot per beat | **shutter click on every cut** (playbook §16) | reels 1/6/9/18 |
| Title text assembling in chunks | chunk-by-chunk pop | **click per chunk** | reel 18 |
| Numbers counting up | green counter | **Counter** tick (pack3) | reels 10/17 |
| End | the idea's title combo (text-behind), freeze-blur, **animated follow card**: avatar + "FOLLOW FOR MORE" + button flips Follow → ✓ Following | **Bell ding** on the flip | reels 5/9 |

## Never show the same words twice (Jason's rule)
- **Font combo on screen → no captions.** Captions are fully hidden for the combo's window. A combo lives exactly as long as its phrase: from its keyword to the phrase's closing punctuation, 45-frame minimum so it reads (`phraseEnd()` + `hold()`), then captions resume.
- **Pop-up on screen → hide only the caption pages that repeat its words.** Match content words and ignore filler ("the, you, that…"). "$7,000" also matches spoken "seven thousand dollars". Keep an `OVERLAYS` list (from, to, text) that mirrors every pop-up, and pass it as `dedupe`.
- A long-lived title must **clear before a punchline caption** (e.g. the slow-mo curse). If it belongs on the outro, add it again there.
- Check: in every still, one piece of text says one thing once.

## Modes (pick one per video before editing)
- **Talking head / teaching** (default, episode #1): everything below.
- **AI / business how-to**: + recreated tool UIs and result cards (§10), UI/tech SFX (§13), illustrated concept cutaways (§14).
- **Iman × iOS** (§20): clean Avenir-style type, smooth spring motion, frosted-glass iOS UI cards as B-roll, glitch transitions, restraint.
- **Music-led recap** (travel, lifestyle, cars, team): §15. Beat-synced kinetic lyric type, film burns, a grade, editorial corner labels. Grades and light leaks are allowed **only** in this mode.

## Visual system
- **Color psychology system (Jason, 2026-10-08; reference r02, "colors 120° apart"):** two jobs, never mixed up.
  1. **Congruence = meaning** (the locked rule below): a color always means the same thing (green = money/win, red = problem, yellow/orange = the key idea), so viewers read it without thinking. Never use a color just to decorate.
  2. **Contrast = attention** (r02): when two things must pop *against each other*, use a **triadic pair** (~120° apart on the wheel: red + blue, yellow + blue, orange + green, purple + green, yellow + red). Uses: the two sides of a comparison (perceived vs actually), the hero word against its background, thumbnails/first frame, CTA vs scene. Our base is navy/indigo, so the triadic accents that pop hardest on it are **orange/amber** (key idea) and **green** (win); red stays for problems.
  - One dominant accent per scene; a second only to set up a contrast. Check: squint at the still. The accent must be the first thing you see.
- **Font = Inter 4 Variable with optical size** (`@fontsource-variable/inter/opsz.css`, `font-optical-sizing: auto`): the legal SF Pro stand-in. SF Pro's license (developer.apple.com/fonts) only allows UI mock-ups by a registered Apple Developer and forbids artwork/"any other work product" and transfer, so it's never used in renders.
- **Keyword color = meaning (LOCKED, Jason approved 2026-09-27):** yellow `#FFD24A` is the default keyword; **green `#2BE37A` = money, wins, gains, solutions, yes** ($7,000, won, confirmed, fast); **red `#FF3B3B` = problems, pain, threats, no** (against, complaining, problems). Tag each key in edit.json: `["WORD", n, "green"]`. Numbers about money are always green. Never color a word just to decorate it; if it's neither a win nor a problem, it stays yellow.
- **Captions** (reels 2/3/5/7): Montserrat. Two-tier: small white lowercase setup words, then the gold (#FFD24A) UPPERCASE keyword on its own line. Glow on all text, no heavy stroke. 1–3 words per page, word-by-word, placed on the chest (~y 1070 of 1920).
- **Font combos** (reel 8): Mozart = luxury/cinematic, Sugary = elegant, Tempting = lifestyle, Modern = business/tech.
  - Only on significant lines, about one per 5–8s.
  - Entrance is letter-fade: letters in random order, blur → sharp, ~8f; the accent word follows +3f; dead-still hold; blur-out exit 6f.
  - Place them in empty space above the head.
- **Text behind you** (reel 7 masking): do it **preemptively** on the 2–3 biggest title moments (hook, core concept, closing idea).
  - Stack: footage → title → `fg.webm` cutout (same transform as the footage).
  - Size and position so the head clips only the **bottom ~20–30%** of the word. It must stay readable. Check the stills.
- **Pop-ups** (reel 5): dark rounded panel with a thin gold border, drop shadow, and scale-pop entrance. Headlines in Bebas Neue, body in Montserrat. Text = **the speaker's own words only**. ✅ green / ❌ red glowing icons for yes/no, right/wrong.
- **Fonts allowed** (reel 2): hooks Bebas Neue/Archivo/Impact; captions Montserrat; talking-head accents Jost (Futura), Poppins, script. Never Comic Sans/Arial/Papyrus.
- **Grade (updated by §18):** a deliberate moody grade is now standard: desaturate ~30%, darken ~15%, one accent color. Still banned: random grain/vignette for its own sake, progress bars, letterbox bars, "SLOW-MO" labels, screen flashes, record scratches, section labels the speaker never says, invented infographics.

## Subconscious cues (the why behind the rules)
- **Open loop** (cold open on the payoff): the brain wants closure, so viewers stay for the "how".
- **Pattern interrupt** (taboo line + bass impact + motion in the first 15 frames): breaks the scroll reflex.
- **Conditioned reward:** the same pop + click on every new piece of info. The consistent pairing makes each new point feel like a small payoff, which keeps people watching.
- **Gold = important:** gold is rationed, so viewers learn to read it. The gold words in sequence are the lesson.
- **Commitment and consistency:** show ✅ on the viewer-agreeable beats (yes/no both ✓) before the ask.
- **Tension → release:** a riser into the number, then the money sound. The payoff lands physically as well as verbally.
- **Unfinished idea at the end** ("Ego archetype", "part 2"): an open loop that makes following the logical next step. The follow card flipping to Following shows the viewer the action to take.

## Verification checklist (before delivering)
- [ ] Hook: payoff cold open ≤3s, then thesis with bass impact; motion in the first 15 frames
- [ ] No dead air over ~1.4s (his pauses kept); no stutters; frame-exact A/V (video frames = audio length)
- [ ] Captions checked by hand against context; slang and names right; raw words unaltered
- [ ] Gold ≤ ~1 per idea; curse slow-mos only on punchline curses
- [ ] Every zoom → whoosh, every cut → zoom transition + shutter, every pop-up → pop + click, reveals → riser/reveal, money → money, CTA flip → bell
- [ ] Text-behind moments readable (head clips ≤30%)
- [ ] No duplicated text: captions hidden under combos, and caption pages repeating a pop-up hidden
- [ ] Nothing from the "Do not add" list; no invented text
- [ ] Stills checked at every beat; the final encode checked (duration, 1080x1920, loudness peak ≤ 0 dB)
- [ ] Deliver: MP4 in chat (hard limit **30 MB**: two-pass x264 at 1080×1920, video bitrate = 28MB×8 ÷ seconds − 96k audio; ep #4 3:05 → `-b:v 1150k`, text stays crisp), full-quality copy (CRF 23) to `renders/`, music recommendation from the playbook, list of any uncertain caption words

## Extending the playbook
When Jason sends more reference videos: md5-check for duplicates first. Then contact sheet at 2fps, transcript, spectrogram, and zoomed crops to read on-screen labels verbatim. Frame-step any animation at 15fps to measure it. Cross-reference with existing rules (count ×N appearances) and add to `references/playbook.md` with the reel number. Rules seen in 3+ reels are defaults.

## Known limits (tell Jason plainly)
- Sound effects are stand-ins matched by job. Swap in his exact CapCut exports (the names are in the playbook) when he provides them.
- The Vosk small model is weaker than Whisper. HuggingFace is blocked in the cloud env; if it's ever allowed, switch transcription to Whisper for cleaner captions.
- MediaPipe selfie segmentation is ~256px internally, so edges are soft. That's fine for text behind the head, not for fine hair detail.
- Screen-recording "auto-zoom / cursor-follow" animations (the Screen Studio-style look Jason likes): build them in Remotion with keyframed zoom to click points when screen footage is provided.

## Rules from episode #2 feedback (7/10)
- **Coherence over chop:** keep whole sentences.
  - Trim only pauses over 0.55s and real flubs.
  - Transitions and shutter sounds only on section changes; same-thought jump cuts are silent and effect-free.
- **Captions always move:** word pop with overshoot and rotation, active-word lift, keyword slam with shake and glow, line float, blur exit.
- **Real iOS sounds only (1:1):** use `assets/sfx/ios/`, never a synthesized chime.
- **Hook:** open on his cleanest, boldest line, untouched.

## Rules Jason approved (episode #4)
- **Cold open on the boldest quotable line when his first line is soft (Jason: "I like the hook", 2026-10-01).** Pull his single most quotable sentence (episode #4: "A lot of people prioritize being perceived as nice rather than actually being nice.") as a 3–5s cold open, then start the video from his real first line in his order. The line plays again in place later; that repeat is the payoff of the open loop. When his first line is already the boldest line, open on it as-is (episode #3).

- **LOCKED: iOS-coded motion graphics instead of B-roll (Jason, 2026-10-01: "I really appreciated… iOS coded, which I loved, with the iOS sound effects and the animations").** Every explainer beat is an iOS/app UI: Messages, Notes, Calendar, Wallet/Apple Pay, Settings toggles, Activity rings, app notifications, real brand logos. Use real iOS system sounds 1:1 and iOS-style motion (no-bounce springs, blur-in, frosted glass). No stock or AI B-roll unless Jason asks.
- **Never reorder his words on your own (Jason, ep #4 v2: "why would you change that order in a way that doesn't logically make sense").** A self-correction stays where he said it, and "get the female part" means *caption it correctly*. **Only when Jason explicitly asks to replace a word** ("I said a guy on accident… cut that out and make it say a female") do you splice: cut the exact word from a 40ms energy map, set `{"snap": 0}`, and re-transcribe the spliced stretch alone to confirm it's clean. If a stretch is unclear, keep the audio and let a graphic carry the unclear words.
- **The on-screen text must read logically, start to finish (Jason, ep #4).** Before rendering, print the full caption transcript in order (hidden words in [brackets]) and read it as a viewer would. Hidden words must never leave a sentence that doesn't make sense: show the words that carry the logic, and hide only what a graphic shows instead.

## Rules Jason approved (methodology decisions, 2026-10-08)
- **No music in the render. LOCKED, reconfirmed** after seeing every reference carry a music bed ("keep my rule"). Deliver voice + SFX; recommend a track.
- **End on a comment-keyword CTA (default from now on).** Big glowing keyword in quotes ("Comment "EGO""), plus what they get in DM, shown at the end (in offer videos, from the middle onward as a persistent element). The keyword comes from the episode's one idea. **The promise must be real:** ask Jason what he's giving away (guide, course link, list…) before rendering; never invent an offer. The follow card can still play after it.
- **Karaoke captions on screen-led teaching segments** (when a mockup/screen/UI is the star): small white bold, low-center, the phrase builds word by word and clears at the phrase end [r02]. Talking-head segments keep the locked two-tier yellow-keyword captions.

- **iPhone notifications must look exactly real (Jason, 2026-10-08).** Use `template/src/lib/IosNotify.tsx` (`Notification`, `NotificationStack`, `AppIcon`), built to iOS 17/18 metrics (1pt = 2.748px: 8pt margins, radius 23pt, padding 14pt, 38pt superellipse icon, 15pt semibold title, 15pt body, 13pt "now", dark/light system material, iOS drop-in spring). Brand apps use real logos on brand colors (`assets/logos`, from simple-icons); Apple apps (Messages, Phone, Mail, Calendar, Reminders, Wallet, Notes, Photos) are drawn originals in Apple's colors. People texting use the contact-avatar style (initials + app badge). Stacks show blank plates peeking, never text through. Pair with the real iOS sounds. Font: Inter stands in for SF Pro (Apple licenses SF for Apple-platform app UI only). Test sheet: `references/ref-sheets/ios-notifications-test.png`.

## Rules from episode #3 brief
- **Motion graphics > AI images** for explaining ideas (animated UI, counters, diagrams, kinetic type).
- **Respect his pauses:** only cut stutters, restarts and dead air over ~1.5s (leave ~0.7s). Never drop a key word. Never break the logical order: hook → argument → payoff → CTA.
- **QA gate:** before sending, compare stills side by side with the reference reels (v9, v19, v21) and fix any beat that falls short.
