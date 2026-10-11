# r20: "10/10 videos to master video editing" (Instagram reel DeWRJ9bi0DA) + the 3 YouTube videos it names

Sent by Jason on 2026-10-11: "our SFX is decent but not top tier, not pinpoint… we have a whole library and only use a little portion of it."

**How it was studied**
- The reel came through a public mirror (Instagram blocks logged-out downloads). I transcribed it with Whisper and made 2 fps contact sheets.
- YouTube bot-blocks video downloads here. For each of the three videos I used the full auto-captions (every word, with timestamps) plus the storyboards (YouTube's low-res thumbnail strips covering the whole video).

## The reel itself (39 s)
- **Format:**
  - The creator is cut out over a backdrop. For 0–10 s the backdrop is his edit suite. From 11 s it switches to the thumbnail of each video as he names it.
  - A persistent title bar sits at the top ("10/10 videos to master video editing", white bold sans).
  - Captions are one word at a time, white bold sans, centred on the lower third.
- **Pacing:** one visual change per topic (about every 9–10 s). The backdrop swap *is* the cut.
- **CTA:** "Comment 'links'": a pill that pops over the last thumbnail. It's a real offer (he DMs the links). The same pattern we use (comment-keyword CTA).

## 1. "How Pacing Controls Emotion in Editing" (Inside The Edit, Paddy Bird, 13:57, id pRpaqx_5jD8)
**Thesis:** edits fail to land not because of weak effects, but because the editor doesn't slow down in two places: when something gets **complex**, and when something gets **emotional**.
- **Complexity:**
  - A dense answer delivered at full speed loses the viewer.
  - Break it into single ideas. Put *space* between them (visual, musical or editorial: B-roll, a music bar) so each idea lands before the next one starts.
  - The editor is the first audience. If it's hard to follow on the 100th watch, it's impossible on the first.
- **Emotion:**
  - People on camera don't know when they've said something important. The editor has to feel it.
  - The short-form reflex (cut straight to the next line) kills the feeling before it registers.
  - Fix: hold the shot a beat longer before and after the line, let the reaction play out, allow a moment of silence instead of filling it.
- **Gears (variation):**
  - Like driving: motorway speed for information, slow down in town for impact.
  - One constant speed = flat and predictable. The audience is "addicted to variation".
  - Great editing isn't making everything faster; it's knowing when not to. Often it's "just a few extra seconds in a few key places".
- **Look:**
  - One dark, moody locked-off A-cam (navy curtain, single key light).
  - Chapter cards: small white bold sans centred on pure black, one pink logo square.
  - A periodic-table graphic for the sponsor plug.
  - Restraint: almost all of it is the face.

## 2. "Documentary Style Sound Design Like Netflix" (luvkilomedia, 17:15, id U6wVF2PMBUw)
**Thesis:** sound is half the experience. The intro "sounds great, but remove the sound and it's instantly boring".

**Music**
- Sits at −5 to −25 dB under the voice.
- Fades in.
- Starts with a hit synced to the title card.

**The "reverb end"** (the most-used music trick):
1. Cut the music about 10 frames before its natural end.
2. Duplicate the last part and extend it.
3. Add reverb (small room, about 4 s tail, 50/50 dry/wet).
4. Pull it down about 5 dB so it doesn't jump.

The track rings out instead of stopping dead.

**Layering = lows + mids + highs**
- Example: a big swish = a low whoosh + a mid fire/lighter flicker + a high whoosh.
- **One whoosh is enough for a whole library.** Slowed to 60% speed and pitched −5 semitones it becomes the deep layer. The same file at 120% speed and pitched up becomes the high layer.

**The five workhorse sounds and their levels**

| Sound | Used for | Level / placement |
|---|---|---|
| Camera shutters / clicks | Image sequences and hard cuts | −25 to −40 dB ("subtle is best"). Alternate 2 different clicks so they don't repeat. The **last** click of a sequence gets a bigger camera-shot impact (−25). |
| Risers | Build-ups, image sequences | About −25 dB, ending exactly on the impact. Layer a second, faster riser for intensity. |
| Whooshes / swishes | Any on-screen movement (scale, rotation, position) | About −25 dB, **peak on the middle of the move**. Pair a film-burn or light-leak transition with a lighter/flicker texture (−20 to −30). |
| Bass | Title cards, emotional impact, release after a build | Starts **a few frames before** the cut so it swells into it. Three basses layered at −25 / −30 / −35. Tiny fade-in, earlier fade-out. |
| Background voice / archival audio | Context (news, the subject's real voice) | Isolated vocals at about −15 to −20 dB, cut into 2 segments. Can work as a sound bridge off a title card. **EQ'd (muffled bands 2 and 4) so it sits inside the mix.** |

**Craft details**
- **Mono to stereo:** a mono SFX plays in one ear only. Fix it.
- **Trial and error is the process.** Swap sounds that don't fit and try again; never settle for the first one.

**Look**
- Netflix-style title cards: a condensed serif title over a grain-textured dark frame, with a small serif list and red tags.
- Photo-wall sequences, red eye glints, film-burn whites.

## 3. "Edit Like a Filmmaker, Not a Videographer" (Max McCoy, 12:54, id XUWjBQiT1Iw)
**Thesis:** cool visuals, music and transitions make you a videographer. Prioritising **story above all** makes you a filmmaker.

**His six steps** (he narrates a real mini-doc edit):
1. **Sort the ingredients:** dialogue bucket and B-roll bucket.
2. **First dialogue scrub:** keep anything usable, trim the fat (20 min → 3 min).
3. **Second, ruthless pass:** 3 min → 1:45. **Label each chunk with its theme** (a title over the clips).
4. **Build the skeleton:** reorder the soundbites into a narrative with three acts. **Setup → conflict → resolution.** These can be felt rather than literal: conflict = what someone aspires to or wrestles with; resolution = how you want to leave the viewer.
5. **Build one: dialogue + music + score + field recordings + SFX + titles, with NO visuals yet.** Treat it as a song: rise and fall, silence, music. "That is editing like a filmmaker."
6. **Visuals and polish last.** Add variety and novelty.

**Mindset**
- Duplicate the project at every stage, so you can go back freely.
- Call the hard structure step "play" to lower the stakes.
- Take breaks and come back with fresh eyes.

**Look: dual type.**
- Bold lowercase sans for titles ("edit like a filmmaker").
- **A small italic serif word over footage ("Rhythm.")**: the same sans + italic-serif pairing we locked in ep05 v2.
- Black chapter cards with thin red progress bars.
- A red-dot "play" graphic.

## What this changes for us (rules)
1. **Gears.**
   - Every edit marks its *complex* and *emotional* moments in `sections.json` (tag `hold`).
   - At those moments we **hold**: 0.5–1.5 s of his face or a reaction before and after the line, no graphic and no SFX, and the room tone stays.
   - Fast sections stay fast. The scorecard's Retention row counts deliberate holds as designed beats, not bare face.
   - (Ep05: the hat-tip smile was exactly this, and it worked.)
2. **Story first, sound second, visuals last.**
   - After `sections.json`, build the **sound bed** (voice + SFX plan on the word grid) before any graphic.
   - Graphics are placed onto the sound, not the other way round.
3. **SFX are seasoning, not salt.** Levels are relative to his voice (voice = 0 dB reference):

   | Sound | Level |
   |---|---|
   | Ticks, clicks, shutters | −30 to −40 dB |
   | Textures (paper, lighter, film, room) | −28 to −35 dB |
   | Whooshes | −22 to −26 dB |
   | Risers | −24 dB |
   | UI / iOS notification sounds | −16 to −20 dB |
   | Bass impacts | −20 dB total across 3 layers |
   | Curse-slow-mo whoosh | −18 dB |

   Nothing louder than −14 dB under the voice except a planned "drop" moment. Ep05 v2 ran everything at −17 to −1.4 dB, which is why it sounded "decent but not pinpoint".
4. **Layer every hero sound (low / mid / high).**
   - Whoosh = low (same file at 60% speed, −5 semitones) + mid texture + high (120% speed).
   - Impact = 3 basses at staggered levels, starting 2–4 frames *before* the frame so the swell lands on it.
5. **Peak on the motion.**
   - Whoosh peak = the middle of the move.
   - Click onset = the cut.
   - Riser end = the impact frame.
   - Bass swell = the title card.

   (`<Hit>` already aligns by measured peak; keep using it.)
6. **Variety, not repetition.**
   - Never the same file twice in a row for the same job: alternate at least 2 variants.
   - The **last** of a sequence gets the bigger sound.
   - Use the whole library. Every edit touches at least 6 of the 13 jobs, **including texture and tech**: film/paper/lighter textures under the engraving cutaways, tech blips under UI.
7. **Silence is a sound.**
   - Before the biggest line, drop everything (no SFX, room tone only) for 0.3–0.8 s.
   - The "reverb end" on any music or hit that would otherwise stop dead.
8. **Background voice as texture.** When he quotes someone (e.g. the insults in ep05), the quote can be EQ'd and pushed back like archival audio.
9. **Dual type is industry standard** (Max McCoy uses the same sans + italic-serif pairing). Keep Inter + Instrument Serif italic.
