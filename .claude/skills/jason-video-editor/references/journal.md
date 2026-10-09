# Edit Journal — scores, what landed, what to beat

Every delivered video gets an entry: Jason's score, what he called out, what's locked, and the backlog.
**Read this before starting any new edit.** The goal of each new video is to beat the best score here.

---

## #1 · "Ego / Label" (car, green blazer) · 2026-09-27 · **7.7 / 10** (baseline)
**Raw → final:** 3 uploads (3:36 raw) → 1:47 final. Cold open on the $7,000 close, then "how to MANIPULATE".

**Jason loved (LOCKED, never change without him asking):**
- **Two-tier captions with the yellow keyword**: small white lowercase setup, then the BOLD YELLOW UPPERCASE keyword on its own line. "The yellow part within the captions to colorify and bold it — I love it."
- Overall direction, the psychology-driven structure, and the raw captions.

**Corrections Jason made during this edit (now rules):**
- Captions must never duplicate on-screen text (combos/pop-ups): captions step aside.
- Transcript terms are his: "ego **archetype**" (the model was right; don't override a clearly heard word).
- Follow card uses his headshot, not a video frame.
- No music in the render; he adds it in TikTok.
- Follow the reference creator's rules to the tee; invent nothing (no grain/vignette/progress bar/flashes/letterbox).
- Text behind him is expected by default on the biggest title moments.

**Why it's 7.7 and not 10 (backlog to close):**
1. The SFX are synthesized stand-ins. Swap in his exact CapCut sounds (names are in the playbook) as soon as he exports them.
2. Transcription uses the small offline model, so some captions were hand-guessed. Push for Whisper (the HuggingFace network allowance).
3. Visual layer is only captions, combos and pop-ups. No B-roll, images or screen visuals yet. **Spec now exists (playbook §10):** recreated tool UIs with typed prompts, staggered result cards, green counters, brand-logo stickers, split screens, and face↔B-roll every 3–6s.
4. Text-behind edges are soft (256px matte). Fine on the hat; weak on hair or hands.
5. A camera shutter on every jump cut may be too much at 40+ cuts. Confirm with Jason or with a reference example.
6. The pop-up look is one style. Build variety from his future examples.

**Next iteration protocol:** Jason will send examples (edits, captions, cues, SFX). For each: decode it (frames at 15fps, labels, audio), add the rule to `playbook.md` with its source, apply it on the next video, then log the new score here.

**DECIDED 2026-09-27 (Jason: yes):** keyword color = meaning. Yellow is the default, green = money/wins, red = problems/pain. It's layered on the locked yellow two-tier style. Applies from episode #2.

**2026-09-30: The standard defined.** Jason pointed to reel 22 ("My work vs Original") as *the* standard. The gap from 7.7 is now concrete:
- episode #1 had captions, combos and small pop-ups;
- the standard has a **full designed scene per sentence** (image collages, editorial cards, rolling numbers, cinematic B-roll), a **moody grade with one accent**, and **callbacks**.
- Next edit: plan a beat sheet with one visual per sentence *before* rendering.
- Needs from Jason: images/B-roll for his nouns (or approval to use stock/AI-generated images, e.g. via Higgsfield), and his logo/brand assets.

## Episode #2: "You ARE disciplined" (Iman Gadzhi × iOS). Cut 2026-09-30
- **Source:** 5 parts, 4:31 raw → **1:41** cut, 40 keep segments, 5 slow-mo curse punchlines (bitch ×2, bullshit, fuck, nigga, loser).
- **Confirmed words:** Jason corrected 3 spots the transcription got wrong. Always ask for unclear words before cutting; never guess captions.
  - "get slutted the fuck out, you stupid bitch"
  - "created in the image of God"
  - "because I'm not a bitch and I'm not weak and my dick is big as fuck"
- **10 in-depth AI images:** all 9+/10 on the first try. The in-depth prompt rule works.
- **Image color system across the set:**
  - Gold = the way out: 01, 03, 07, 08, 10.
  - Red = the trap: 12.
  - Green = the win: 11, 15.
- **iOS layer:**
  - Dynamic-Island notification on the hook.
  - Collapsing notification stack (newest in front; never stack cards over the face).
  - Screen Time toggle flip, Fitness rings closing.
- **Text-behind hero words:** ARE (yellow, behind the hat), AUTHORITY, REDIRECT (green).
- **Rules learned:**
  - Hero words on this footage sit at top ≤ 170, where the hat starts at ~340.
  - 8–9-letter words max out at a Nunito 900 size of ~160–175.
  - Caption position follows the image card's reserved text zone (the `tops` prop).
- **Code:** `examples/discipline-episode/`.
- **Score:** pending Jason.

### Episode #2 v1 score: **7/10** (Jason). His notes are now rules:
1. **Captions need more motion.**
   - Every word pops with overshoot and a slight rotation, and blurs in.
   - The spoken word lifts; keywords slam in from 2× with a shake and a glow pulse.
   - The line floats gently and exits upward with a blur.
2. **iOS sounds must be 1:1 real.**
   - Never synthesize. Use Apple's own system sounds (`assets/sfx/ios/`): Tri-tone (sms-received1) for notifications, iMessage received, Tink (toggle), Activity goal attained (rings), Apple Pay success.
   - Source: github extratone/iOSSystemSounds and macOSsystemsounds. Git clone works where websites are blocked.
3. **Too many cuts hurt coherency. Cleaner is better.**
   - Keep whole sentences.
   - Only trim pauses over 0.55s (down to 0.3s) and cut true flubs or unclear words.
   - Same-thought jump cuts get no transition and no SFX, just alternating framing.
   - Zoom transitions and shutter sounds only on section changes.
   - Image cards crossfade, never hit-zoom.
4. **Hook = the cleanest, boldest line, as-is.**
   - This episode opens on "I'm black as fuck, and my dick is big as fuck." (Jason's wording for part 04 ~0:21–22.)
   - No notification or graphic on the hook when the line carries itself.

### Episode #2 v2 score: **7/10**. Note: the caption wasn't his exact words.
- He confirmed "I'm not weak, and my dick is big as fuck." v2 wrongly captioned "I'm black as fuck", from his loose paraphrase of the hook request.
- **Rule:** captions follow the **confirmed words**. When a new message paraphrases a line that was already confirmed, keep the confirmed wording and flag the difference; never overwrite it.
- **Rule:** align confirmed words to recognizer mis-hears with an alias map ("week"→weak, "pick"→dick, "biggest"→big as, "work"→fuck). Then spread merged tokens, so no two words pop on the same frame.

## Episode #3 brief ("what to do with your life"). Jason's direction, 2026-09-30
- **Motion graphics over AI images.** Use designed, animated explainers that *show* what he's saying (v9-style UI/card takeovers, v19-style clean kinetic type), not photo B-roll.
- **Pauses are part of the delivery.**
  - His silences are often intentional, for impact. Do NOT auto-trim every gap.
  - Only cut stutters, restarts and true dead air (roughly >1.5s with no dramatic intent), and even then leave ~0.6–0.8s.
- **Never drop key words**, and never reorder or break his logic.
  - The sequence must flow hook → argument → payoff → CTA exactly as he builds it.
  - The hook is the first line when the first line is already a hook.
- **iOS notification sounds:** he is bullish on them, so use them generously and 1:1 real.
- **QA against references before sending.**
  - Compare the render frame by frame with v9 (motion-graphics talking head), v19 (kinetic iOS type) and v21 (the "My work vs Original" standard).
  - Fix anything below them first.

## Episode #3 "Find your purpose": build notes
- **Audio:** Jason asked for the background cut and the voice louder.
  - Chain: `scripts/voice_enhance.py` (DeepFilterNet3 → EQ → comp → −14 LUFS). Re-transcribing the clean audio fixed many words.
  - Examples: "taste of fucking psycho mcnugget" → "change the fucking cycle, my nigga"; "that gets you into the doors".
- **Cut:**
  - Sections are contiguous, so his natural pauses stay.
  - Only dead air over 1.4s is shortened (to 0.75s).
  - The unclear 0:55–1:18 aside in part 2 was removed; "never ever…" joins "…you will never find your purpose by being still".
- **Motion graphics (no AI images):**
  - iOS Notes hook; iMessage stack; Reminders grade ticks with a rolling ordinal; grad cap; goldfish bowl → ocean; path network → one destination; green counter; "you can sell" tiles → flood.
  - Overwhelm notification rain → grey freeze; Chase card → Safari tabs → "0% started".
  - Notes questions; thinking-spinner → "doing" bar; Chess.com board + streak → gold king PURPOSE; same-week calendar; loop ring (paradigm/script/cycle).
  - Hero CHANGE; Activity walk ring 5:00; iMessage from a stranger; doors of light; DOING ×3; plans ✓ actions ✓ EXECUTE.
  - CTA: comment PURPOSE → DM "AI guide + course link".
- **Real brand logos:** from simple-icons (`assets/logos/`), rendered as masks.
- **Hero words behind the head:** top ≈ 570–610 on this framing (the durag starts ~760).
- **Ops:** remotion stills bundles copy `public/` into /tmp every run. Delete `/tmp/remotion-webpack-bundle-*` after each run, or the disk allowance fills.

### Episode #3 score: **8.3/10**. NEW HIGH ("probably one of the best you've done so far")
- **What won it:**
  - Motion graphics instead of AI images: every sentence visualised with iOS/brand UI.
  - Clean loud voice (DeepFilterNet3 chain).
  - His pauses kept, with only dead air trimmed.
  - Logic intact from hook → CTA.
  - Real iOS sounds and real brand logos.
  - Reference QA pass before sending.
- **Correction:** the closing line is "**Commit all your plans and actions onto God, then execute.**" I had guessed "Come up with…".
  - **Rule:** faith lines are his signature. When a garbled word could be "God", ask, never guess.
- **This episode is now the baseline:** the purpose-episode format (`examples/purpose-episode/`) is the default for talking-head motivational content.

---

## 2026-10-01 · New session, repo rebuilt as **VideoEdit**
- **What happened:** the old session was lost. The episode #3 raw clips lived only in that container and were never pushed. Jason still has the final 8.3 render on his side. If he uploads it, it goes to `renders/ep03-find-your-purpose-v1.mp4` as the reference to beat.
- **What survived:** everything that *teaches* the edit. That's the playbook (19 reels), this journal, the episode #3 code (`examples/purpose-episode/`) and all the assets. **8.3 stays the bar.** Episode #4 must beat it using the same recipe.
- **What changed so it can't happen again:**
  - The repo is now dedicated to video editing. The old game is deleted and the repo is renamed VideoEdit.
  - Videos go through Git LFS.
  - Every final MP4 → sent to Jason → `renders/` → pushed, before anything else (SKILL.md non-negotiable).
  - Raw footage → `raw/epNN/` → pushed as soon as it arrives.
- **Lesson for the craft:** the rules are the asset, not the files. A new session reproduces an 8.3 from `SKILL.md`, `playbook.md`, this journal and the example code alone.

### Plan to beat 8.3 on episode #4 (from the backlog, highest impact first)
1. **Real CapCut SFX** in place of the synthesized stand-ins (backlog #1 since episode #1). These need Jason's exports.
2. **Text-behind-you on every hero word**, checked so the head clips at most 30%. This was the weakest-looking element in episode #3 stills.
3. **A callback in the last 10s:** replay the hook's graphic as the payoff closes the loop (§18 calls for callbacks; episode #3 didn't have one).
4. **Caption accuracy:** ask Jason about every low-confidence word *before* rendering, not after. Episode #3 lost points on the "God" line.

## 2026-10-01 · Skill rebuilt around the 8.3 recipe (no new video; this is about the system)
**Jason's ask:** "I want to know how Claude got the 8.3, so the skill starts there. The next video should land at 8.0–8.3 automatically, not drop back to 6.7 or 7.7."

**What I found (plain English):**
- The 8.3 method was in the repo, but scattered. The main instructions (`SKILL.md`) still described the **episode #1 way** (the 7.7 way): chop every pause over 0.45s, old caption code, no voice cleanup. A fresh session follows `SKILL.md`, so it would have started from 7.7.
- Worse, two of the files the 8.3 build needed were **never saved**: the newer video layer (it added the freeze-frame) and the newer timeline (it looks up words by section). Even with the raw clips, episode #3 couldn't have been rebuilt from the repo.

**What I changed:**
1. **`SKILL.md` now opens with "THE 8.3 RECIPE"**: the exact 10 steps that made episode #3, in order, with a table showing which mistake each step prevents. Rules that contradicted it (e.g. "cut pauses over 0.45s") were updated.
2. **The template IS the 8.3 build now.** The motion-graphics library, moving captions, iOS cards, video layer and timeline all sit in `template/src/lib/`. `Episode.tsx` ships as episode #3's beat sheet, ported 1:1, so a new session sees a real 8.3 edit and replaces the beats.
3. **The two lost files were rebuilt** from how the 8.3 code uses them (freeze-frame = hold one frame in black and white; timeline = find any spoken word by section).
4. **`scripts/cut_sections.py`**: the episode #3 cut as a reusable tool. You give it a `sections.json` (his sections, his exact words, colored keywords); it keeps his pauses and only trims dead air. Episode #3's own `sections.json` is saved in `examples/purpose-episode/`.
5. **`scripts/new_episode.sh`** builds a ready project in one command, with every sound (real iOS, packs), logo and the avatar in the right place. Episode #3 had done this by hand.

**Why this should lift the floor:** before, each session re-learned the method and lost points on the same mistakes (over-cutting, wrong words, fake sounds). Now the 8.3 decisions are the starting point. The next score depends on the new video's beats, not on rebuilding the machine.

**Honest limit:** the rebuilt video layer and timeline are faithful reconstructions, tested end-to-end on dummy footage. They aren't byte-for-byte the files from the lost session. The visible difference to watch is the "still" freeze-frame look on episode #4.

**Test result (2026-10-01):** passed. Dummy footage was run through every step with episode #3's exact sections and words: cut (9 pieces, 515 words, 2:36) → new project → typecheck clean → 11 stills.
- Every graphic rendered: Notes hook, grade ticks, $1,000,000 counter, sell tiles, PROBLEM/CHANGE/EXECUTE hero words, Chess streak, the black-and-white freeze on "STILL", the PURPOSE CTA and the follow card with Jason's avatar.
- Text-behind-you works: the cutout layer clips the bottom of the hero word.
- Not yet proven on real footage: the person cutout's edges, and caption timing on a real transcript. Episode #4 is the first real check.

## Episode #4: "Perceived as nice" (car, white durag + polo) · 2026-10-01 · v1 · score: pending Jason
**Raw → final:** 3 parts (3:30 raw) → 3:01 cut + 4s outro. Part order was confirmed by the words: part 2 ends "not because you're nice but because…" and part 3 continues "…they don't know that you're a nice person."

**The one idea:** you care what broke people think because your ego wants to be *perceived* as nice. Let it go and just post.

**What I did (the 8.3 recipe, step by step):**
1. **Raw saved first** to `raw/ep04/`. The push is still blocked: the environment needs `lfs.github.com` allowed.
2. **Voice cleaned** (DeepFilterNet3 chain), then re-transcribed. The cleaned part 1 lost its first 5 seconds of words, so part 1's timings come from the raw transcript. Lesson: always check that the clean transcript starts where the raw one does.
3. **Asked before cutting.** I sent Jason 9 unclear spots. He answered 6:
   - "see you guys as, like, you can be influential"
   - "why are you giving a fuck"
   - "if a **female**…" (he corrected himself on camera; keep only the female version)
   - "**stop** giving a fuck"
   - his boy "**Khamani**"
   - the closer: "Just fucking post. Fuck everybody that talks shit. They're broke. They're broke, nigga."
   The 3 he didn't answer were short unclear bits, and I cut them instead of guessing.
4. **Hook (Jason approved: "I like the hook"):** cold open on "A lot of people prioritize being perceived as nice rather than actually being nice." Then the video starts at his real first line. Now a rule in SKILL.md.
5. **Word-level splice:** the female line joins four moments ("If" + "a female" + "came up to me… your dick small" + "I'ma laugh"). To keep a word from being clipped, `cut_sections.py` now **snaps every cut to the quietest spot within ±80ms** (new `snap` setting).
   - The middle phrase couldn't be transcribed exactly, so its caption is hidden and an iMessage from "Her: your dick small 😂" carries it. **Never guess a caption; let a graphic say it.**
6. **One designed beat per sentence** (13 graphics). 8 new components were added to the library (`template/src/lib/Mg.tsx`) for future episodes:
   - **NiceSplit** (🎭 perceived vs 💛 actually): used in the cold open and again as a **callback** when he says the line in place. That callback is new; §18 asked for callbacks, and episode #3 had none.
   - **Meter** (potential bar → "✓ Influential")
   - **CommentRain** (opinions pour in → freeze → "0 people actually care"). It dissolves before reaching his face.
   - **SettingToggle** ("Care what others think" flips OFF on "rewire")
   - **BrokeHater** (hater comment → their Chase balance drops to $4.12)
   - **HeightTag** (6'5" with a ruler)
   - **Tiles** (Influential / Know how to speak / Funny as fuck)
   - **NewCity** (route to a new-city pin)
   - **PostUpload** ("Posting…" → "Shared ✓")
   - **LetGo** (the words float up and dissolve)
   Existing components reused: Notes, Banner, BannerStack, SameWeek.
7. **Hero words behind his head:** BROKE (red), BELIEF (yellow), SCRIPT (yellow), EGO (red).
   - **Placement rule for this framing** (head top ≈ y 735–865): word top ≈ 615–690.
   - The first try put them fully *above* the head (top 545). The stills check caught it, and they were moved down until the durag clips ~25%.
   - BELIEF needed 50px less overlap than the others, because the head was higher in that shot. Check each hero still, not just one.
8. **Captions** sit on the chest (y 1440) all video. At the default 1070 they'd cover his mouth on this framing.
9. **Motion in the first 15 frames:** a zoom punch + hit on frame 3. The split only lands at 2s, so without it the open would be still.

**Mistakes I made and caught (so the next session doesn't repeat them):**
- A wait loop used `pgrep -f matte.py` while its own command contained "matte.py", so it waited forever. The SKILL.md warning is about `pkill`; it applies to `pgrep` too. Wait on the output file instead.
- `setup.sh` was missing vosk's runtime packages (tqdm etc.). Fixed in setup.sh.
- `download.pytorch.org` is blocked here; installing torch from PyPI works (slower). Then `pip install --ignore-installed packaging deepfilternet`.

**Guesses to confirm** (captions I couldn't verify 100%): "you short ass nigga" (the 6'5" joke), "oh, he just, he be yapping", "telling your sister…", "Hey, can you do this for me?"

### Episode #4 v1 → v2: Jason: "the audio comes out so fucked up. 'Nigerian elephant' is misplaced, some places stop talking"
**What was wrong (both my fault, both now caught by tools):**
1. **"Some places stop talking":** the voice cleanup (DeepFilterNet) decided his quieter first 5 seconds were background noise and **erased them**. "It's really a shame, because a lot of y'all…" played silent under the captions. 14 captioned words had no voice under them.
2. **"Nigerian elephant":** to splice "a female" I used the recognizer's word times. That piece really held "a [nigga] [female]" run together, so it sounded like "a Nigerian elephant".

**Fixes:**
- `voice_enhance.py` now **caps how much it can remove (15 dB)** and adds a **leveler** that lifts quiet stretches before compression. His opening went from silent (−90 to 15 dB) to 70–77 dB, the same as the rest of the video.
- New **`check_voice.py` audio gate**: it fails if any captioned word plays over silence, and lists every pause over 1s. v1 would have failed it with 14 words. v2 passes with 0 words and no pause over 1s.
- The splice was rebuilt from a 40ms energy map: "If a" + **"female" (62.10–62.64s exactly, before he says "nigga" again)** + "came up to me…". Snapping is off for those pieces, and the spliced stretch was re-transcribed alone to check it.
- Both are now rules in SKILL.md (the recipe's audio-gate step + the word-splice rule).

**Craft lesson:** sound problems are the fastest way to lose a viewer and the hardest for me to notice, because I can't hear. So every audio decision now gets a measurement: levels per half-second, words-over-silence, and re-transcribing every splice.

### Episode #4 v2 → v3: Jason: "the 'Nigerian elephant' part should come after the dick small part… why would you change that order?"
**What I did wrong:** he said "make sure you get the female part". I read that as *splice "a female" to the front of the line*. He meant *make sure the caption says "female"* (the transcriber heard "elephant"). So in v1 and v2 I moved his words out of the order he said them. That broke his logic: in the original, he says the "dick small" line first and *then* corrects himself with "a female, nigga".
**Fix (v3):** the whole line plays exactly as recorded (55.85–70.1s, no splice). Captions: "If a nigga came up to me and said… a female, nigga, I'ma laugh, because I know who I am." Visual: a text from "Some guy: your dick small 😂", then when he says "a female", a second text from "Her" says the same. That shows his point (man or woman, he laughs) instead of hiding it.
**Also asked by Jason this round, now locked rules in SKILL.md:**
1. iOS-coded motion graphics over B-roll, with iOS sounds and iOS animation (what he loved in the 8.3).
2. The on-screen text must read logically start to finish. I now print and read the full caption transcript before every render.
**Craft lesson:** when an instruction could mean "fix the caption" or "change the edit", it almost always means the caption. The order of his words is his argument; touching it is never a small change.

### Episode #4 v3: Jason: "I said a guy on accident. I'd rather it be a female… cut that out and make it say a female. Let the female text me with a girl emoji"
- Now **his** explicit request, so the splice is right this time: "If a" + "female" (62.10–62.64s exact) + "came up to me and said…" + "I'ma laugh, because I know who I am". "Nigga", "never" and the trailing "a female, nigga" are gone. Re-transcribed alone: the spliced audio has no stray words.
- One text only: **"Her 👩🏾": "your dick small 😂"**. The "Some guy" text is removed.
- Rule refined: never reorder his words *on my own*; splice only when he explicitly asks to replace a word.
- **Lesson:** I should have asked one question at v2 ("keep both, or female only?") instead of guessing twice. When two readings change the edit, ask.

## 2026-10-08 · SFX library built (Jason: "make SFX library")
- **What:** every sound we own (60) plus 17 new ones, cut from Jason's new reference reels r10 (Zenix: Button 1-3, Combo, Sparkle, Deep Whoosh, Typing) and r11 (vishu: Hook 1-2, Impact 1-2, Blade, Camera action, Tension, UI+SFX, Shutter, Click+SFX). That's **77 sounds sorted into 13 jobs**, each with when to use it, a default volume and where it came from. Sounds were cut per on-screen label window (label changes detected at 30fps). r11 has no music bed under the effects (silence between them), so the cuts are clean.
- **The big finding:** I measured where each sound actually *hits*. CineStrike peaks 0.53s in, the camera click 0.54s, Digital Text 1.34s, Tension 3.7s. In episodes #3-#4 I started files a frame before the word, so heavy hits landed up to ~16 frames late. The reference reels land the sound within 3-45 ms of the motion. New `<Hit>` helper: it lines up the peak (impacts, whooshes) or the onset (iOS/UI/clicks) with the frame automatically.
- **Audition reel** (reference style, playhead over waveforms, job-colored): every sound plays with its name and job. The source is in `examples/sfx-demo/`.
- **Honest limits:** 6 sounds are still my synthesized stand-ins (pop, click, typing, kaching, ding, riser), and 18 are lifted from reels (reference-grade). Biggest upgrade available: Jason comments "SFX" on reels r01/r10/r11 and sends the clean packs.

## 2026-10-08 · Methodology from 12 reference reels (Jason: "this must be our methodology… understand the psychology, hooks, typography, SFX timing, everything")
- **All 12 analyzed** (r07 was a photo carousel; only its cover was reachable without login): frame-stepped, transcribed, plus a new audio-vs-visual sync analyzer. Written up as `references/methodology.md`. SKILL.md now points to it first.
- **Key findings in plain English:**
  1. **Sound leads the picture by up to 2 frames, never trails it.** Measured on 7 reels (−83 to +28 ms). Our old habit landed heavy hits up to 16 frames late; `<Hit>` fixes that.
  2. **Five hook shapes:** a question they can't answer yet, a contrast (okay vs scroll-stopping), "what if I told you", calling out their pain, want + offer.
  3. **Typography:** a sandwich title (small / BIG glowing word / small), one word at a time synced to speech, words growing on the key phrase, a highlight box on the keyword, karaoke captions when the screen is the star.
  4. **Color:** one accent per video; triadic pairs (120° apart) for maximum contrast; flip the background light↔dark when a new idea starts; one full-screen color slam on the punchline.
  5. **Psychology:** value first; show the result before the method; prove by pattern (3 examples); name the concept; "the answer is simple" before the payoff; a comment-keyword CTA.
  6. **Audio craft:** add an echo/reverb tail where the voice is cut, so nothing stops dead.
- **Duplicate spotted:** r04 is the same reel as our `pack3` source (sound names and timings match).
- **Conflicts with Jason's locked rules** (music bed, comment-CTA vs follow card, karaoke vs two-tier captions) are flagged in the file, not applied. Waiting on Jason.
- **Jason's decisions (same day):** keep no-music · comment-keyword CTA becomes the default close (the offer must be real, so ask him) · karaoke captions yes, on screen-led teaching segments. All three are written as rules in SKILL.md.

## 2026-10-08 · Motion-graphics quality bar set (Jason: r05 "this is the quality I expect for motion graphics")
- Decoded r05 frame by frame (4 × 24-frame screen crops). Spec in `references/mg-quality-bar.md`; SKILL.md points to it at the top.
- **Honest gap vs our 8.3 graphics:** ours are good iOS cards on top of footage. r05 builds a **whole technical world** (navy blueprint grid, bloom, micro-labels) and turns **every sentence into a literal diagram** that animates on the spoken words (strike-through timelines, node chains with travelling sparks, typing prompt boxes, code + live artboard, paper forms with hand-drawn strikes, dictionary entries, full-screen word slams). That's the level to reach.
- **Built the r05 kit** (`template/src/lib/Blueprint.tsx`): Stage (navy blueprint world, grid, bloom, vignette, grain, optional 3D floor or light paper), Micro labels, KLine (spoken-word orange sweep, ghost words), Node (line-drawn box, hot/dead states), Wire (line-draw + travelling comet), Strike (corner-to-corner strike with sparks), Prompt (mono typewriter + underline marks), WireCube, Slam (full-screen orange one-word-per-beat), Finale, Form (paper form + hand-drawn strike + stamp).
- **Quality sample v1** (18s, over ep #4's cold open + first lines; `examples/mg-quality-sample/BpSample.tsx`, `renders/mg-quality-sample-v1.mp4`): perceived-vs-actually node diagram with a strike, a crowd of dots lighting into POTENTIAL, a paper FORM 4-A with "NOT ONLY" stamped, a slam "YOU / CAN BE / INFLUENTIAL." The first stills failed my own check (Title Case, diagrams too small, empty lower half, the finale clipping) and were fixed before the render. Waiting on Jason's verdict vs r05.

### MG quality sample v1 score: **6.8 / 10** (Jason): "the glows, smooth animations, graphics etc, you're nowhere near yet. The backgrounds. The infinitesimal details."
**Why it fell short of r05 (my own diagnosis, frame vs frame):**
1. **Glow:** mine is a thin text-shadow. r05 has real **bloom**: light spills from every bright thing into the air around it, sparks have cross/anamorphic flares, hot elements tint the background around them.
2. **Smoothness:** mine pops elements in with short springs and a flat scale-dolly. r05 has **motion blur** on everything that moves, eased camera moves with parallax depth, RGB-split smears on transitions, nothing ever static.
3. **Backgrounds:** mine is one flat grid. r05 is **layered depth**: a far blurred grid + a sharp near grid, light pools, drifting dust, scanlines, animated grain, a vignette, a perspective floor.
4. **Infinitesimal details:** mine has a handful of labels. r05 has a **HUD layer** everywhere: corner brackets, rulers with ticks, coordinates on anchors, crosshairs, dashed construction lines, live readouts, tiny tables, reference numbers.
**Rule from this:** a motion-graphics beat isn't done until it has all four layers: bloom, motion blur/parallax, layered background, HUD micro-detail. Check stills side by side with an r05 frame before rendering.
- **Jason (same day): "iOS-like UX, soft borderless animations etc."** Direction: keep the r05 quality layers, swap the look to iOS (frosted borderless cards, soft shadows, no-bounce springs, morphs). The v2 render with hard outlined HUD boxes was stopped; the iOS kit (`Glass.tsx`) gets built instead.

## 2026-10-08 · Font research + color psychology rule
- **SF Pro (Jason: "find a way to actually use these fonts"):** researched Apple's own license page. It allows SF only for UI mock-ups by a registered Apple Developer, and forbids "artwork… or any other work product" and transfer. So it can't be used in captions or titles, and it can't be installed in this cloud container. **Best legal move:** Inter 4 Variable with the optical-size axis, which works like SF's Text/Display split and is the top-ranked free match to SF Pro Display. Swapped into the notifications + iOS kit; comparison sheet in `ref-sheets/font-inter-opsz-vs-static.png`.
- **Color psychology** from r02 (Jason re-raised it) is now a SKILL rule: congruence = meaning (locked), contrast = attention (triadic 120° pairs for comparisons, hero words, first frame).
- **MG sample v3 (iOS language) delivered** (`renders/mg-ios-sample-v3.mp4`): frosted borderless cards on a mesh wallpaper; swipe-to-delete on "perceived as nice"; island → avatar grid lighting up on "potential"; a Reminders list with a "Not only." capsule and a 1-of-2 ring; a soft orange word moment; bloom + parallax + motion blur kept. Rendered before the Inter-variable font swap. Waiting on Jason's score (v1 was 6.8).
### MG sample v3 score: **6.9 / 10** (Jason). Only +0.1 over v1. Rebuilding the look (blueprint → iOS) didn't move the score, so the gap isn't the style; it's execution quality.
**Diagnosis (side-by-side, 1 second at 15fps vs r05):** the gap is not style:
1. **Motion density:** v3's first second = words fading on an empty wallpaper; r05's first second = the whole set swinging in 3D with motion blur + several elements reacting.
2. **Scale/composition:** v3 = small headline top-left, ~2/3 of the frame empty; r05 = a big focal object always in frame.
3. **Camera:** v3 = flat 2D drift; r05 = a real 3D camera (tilt, dolly, whip).
4. **Transitions:** v3 = soft fades; r05 = whip pans with heavy blur smears.
**Rule:** frame 1 must already move; a big focal object in the center third at all times; a new element every ~0.5s; a 3D camera move on every scene; whip transitions between scenes.
