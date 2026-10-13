---
name: theta-session
description: Jason's guided identity-installation videos, end to end. Wim Hof breathing with first-person identity statements on the out-breaths, a scene in every empty-lung hold, a vision, and a descent into sleep, for men and women, plus the YouTube upload kit and thumbnails. Use whenever Jason asks for an affirmation, identity, subconscious, sleep, theta, hypnosis, visualization, breathwork or "brainwash myself" video, a new theme or doctrine session ("I AM", "my word is law"), changes to an existing session (timing, SFX, voice, music, intro), or the title, description, tags or thumbnail for one.
---

# Theta Session: the process

Everything lives in `projects/theta-identity/`. The engine is `build.py` and `sounds.py`. Each
session is one script file. Read `README.md` there for the engine details. This file is the
**process and Jason's standards**, learned the hard way across four rounds of feedback. Follow it in
order.

## 0. The standards (non-negotiable)

| Standard | Why (Jason's words / what went wrong) |
| --- | --- |
| **One video**: intro → rounds → bridge → vision → descent | He rejected split night/morning versions ("it's supposed to be all in one") |
| **Intro under 3 minutes**, first breath by ~2:45 | "It took eight minutes to get past the intro… people would churn" |
| **First person, present tense, plain words** | No "future self", no "one day". The past is depression and the future is anxiety. Scenes play *now* and close with "This is me." |
| **Identity, not ego** | Every line is about what I do when nobody's watching |
| **Statements ride the out-breath**, one every ~3 breaths | Affirmations and breathing happen *together* |
| **Explain "let go"** in the intro and on screen | He asked what "let go" means: relax the air out, don't push, don't stop |
| **Countdowns**: "Get ready, 3-2-1" before every round; ticks, a rising swell and a chime into every "go"; LAST BREATHS ticks | "3, 2, 1 with the sound effects impending" |
| **SFX in every scene**: each HOLD and the VISION carry `[sfx]`/`[fx]` cues | "Remember the SFX" (the build fails without them) |
| **Natural breath, no tones**, getting louder as the music falls away | He hated the synthesized "sound effect" breath |
| **Fluid visuals**: a breathing light field, never a contained circle | "Not extremely contained… like lungs" |
| **Music with a reason**: tuned to 432 Hz, plus a binaural theta bed (8 → 6 → 4 Hz), ducked under the voice | State it honestly: the evidence is mixed, so call it a path, not a switch |
| **Pronunciation gate passes** | The verb "lives" said with the "life" vowel broke the state for him |
| **16:9 by default** (1920x1080) | He asked for 16x9 |
| **Men's and women's versions** | Same structure. Her own voice (`af_heart`), her own lines and scenes |
| **His world in the vision** | Gold everything (chain, watch); dark forest green Porsche, brown leather, gold accents; house on the ocean; home gym; the beach at sunset; family taken care of; God thanked |
| **Faith stated precisely** | Quote scripture accurately (Ex 3:14, John 1:1/14, Num 23:19, Ps 138:2, Luke 22:42, Matt 5:37). Don't attribute quotes you can't verify (McAfee "no-bluff": unverified, so keep the rule and drop the name) |

## 1. Intake

Pull out of Jason's message (it's usually a long voice dump):
- **Doctrine.** The beliefs to install, in his own words. Keep his terms ("pump fakes", "my word is law").
- **Identity pillars.** One per round, six rounds. One scene per round, playing in its hold.
- **Vision details.** Car, house, jewelry, places, people.
- **Theme.** Is this a *new* session (new `THEME`, title, look, score) or a revision?
- If the message cuts off mid-sentence, build anyway and say so in one line.

## 2. Write the script

Copy the newest script (`script-iam.md`) as the template. Its blocks are:
`THEME`, `VOICE`, `INTRO`, `ROUND_1..6`, `HOLD_1..6`, `RECOVER_1..6`, `BRIDGE`, `VISION`, `DESCENT`.
The line syntax is `>` statement, `~` narration, `[N]` silence, `[sfx bed]`, `[sfx off]`, `[fx one-shot]`.

- **Intro.** Hook in the first line, one sentence per idea, how it works plus safety in about 5 short lines.
- **Rounds.** 7 or 8 statements each. Scenes run 5–7 sensory lines (touch, temperature, sound, smell) and end with "This is me. Right now."
- **Women's version.** Run the same file through targeted replacements (pronouns, scenes, jewelry, "gentleman" → "lady", plus an "I am beautiful, and I don't need anyone to tell me"-style line). Never just swap the voice.
- **Sounds.** Beds: `morning house office hall gym drive beach lot`. One-shots: `door engine keys clank rack steps phone wave typing laptop pen slide chain watch`. If a scene needs a sound that doesn't exist, add it to `sounds.py`, synthesized and loudness-matched, before using it.

## 3. The gates (run before any render)

```bash
python .claude/skills/voiceover-pronunciation/scripts/check_pronunciation.py --build projects/theta-identity/build.py projects/theta-identity/SCRIPT.md
```

Then build the timeline once (TTS is cached) and read the numbers. `build.py` refuses to render if
any of these fail:
- `audit()`: overlapping voice lines, a statement not on an out-breath, a statement too close to the hold, an unclosed sound bed.
- `pronunciation_problems()`: a known heteronym said wrong. Also eyeball every `NAME` line: "I AM", brands, places.
- `sfx_problems()`: a HOLD or the VISION with no sound.

Also check: the first breath lands before ~2:45, and the total runs about 35–45 min.

## 4. Look before the long render

Render sample frames (`render_frame(segs, t)`) at the title, a mid-round statement, a hold and a
recovery, and *look at them*. Check spectrograms and levels for any new sound. Never render on
untested visuals or sounds.

## 5. Render

```bash
python projects/theta-identity/build.py --script SCRIPT.md --name NAME-vN    # 16:9, parallel chunks, ~25-35 min each
```

Run men's then women's back to back in the background. If Jason changes anything while it renders,
**kill it** (`pkill -f "build.py --script"`), make the change, and restart. Never ship a stale render.
Delete any stale mp4 that a killed run left behind.

## 6. QC and deliver

- `ffprobe` the duration. Pull 6 frames across the timeline into a contact sheet and look at it.
  Measure section loudness from the wav.
- **Chat copy (30 MB upload cap).** Two-pass x264 at 854x480, 15 fps, with the video bitrate set
  from duration: `kbps = 30e6*8/secs/1000 - audio_kbps - 6`. For 37–45 min that's about 32–46k video + 48–56k AAC.
- Send with `SendUserFile` and give the full-quality links:
  `https://github.com/whoisjaso/VideoEdit/raw/theta-identity/renders/NAME.mp4`.
  The full path is always `projects/theta-identity/upload/…` for the kit files; he hit a 404 once on a shortened path.
- Commit renders (Git LFS) and push. Update the PR description.

## 7. The upload kit

Write `projects/theta-identity/upload/youtube-<session>.md` in the same shape as `youtube-iam.md`:
- **Title.** Short, sweet, intentional. Every new session gets a *different* title, hook and wording; the message stays the same.
- **Description:**
  - a one-line hook
  - three lines on what it is
  - the session's "law"
  - a "What you're installing" list
  - "How it sounds"
  - chapters
  - how to use it
  - safety
  - "Original music and sound design. Narration voice is AI-generated."
  - hashtags
- **Chapters** come from the built timeline (`ready` segment starts, then `bridge`, `vision`, `descent`), never guessed. Recompute them after every intro change.
- **Tags:** under 500 characters.
- **Pinned comment:** a call to act ("What's one thing you said you'd do…").
- **Settings:** Education, not for kids, synthetic-content "No".
- Paste the full kit in chat as copy-ready blocks as well.

## 8. Thumbnails

He rejected two text-and-graphics designs. **Use real faces.** No credits means no AI image
generation, so use free Pexels photos (`images.pexels.com/photos/ID/pexels-photo-ID.jpeg`;
Unsplash blocks downloads). Build them with `upload/make_thumbnails.py` (warm gold) or
`make_thumbnails_iam.py` (forest green and gold):
- the face on the right, mirrored so it looks at the text
- a smoothstep fade into black, so there's no seam
- a color grade that matches the theme
- gold dust
- a huge gold gradient word ("HIM", "I AM")
- a one-line subtitle
- a gold pill with the hook
- a small "WIM HOF + THETA · NN MIN" line

Check it at feed size (320x180). A new session gets new faces and a new palette.

## 9. Close out

Commit, push, and update PR #4 (or the session's PR). Write the Supabase digest. Ask Jason to
listen with headphones and report anything off; every fix he names becomes a rule in this file or a gate.
