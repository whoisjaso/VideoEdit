# r13: Jason Cooperson, "I Finally Solved AI Video Editing (Full Guide + FREE Setup)" (youtu.be/sGt1ACELN4k, 21:19, posted 2026-10-08)
Sent by Jason on 2026-10-09: "watch it, listen to it, understand the premise and the angle… colors, typography, animations, SFX, all of it, and implement it."
**How it was read:** YouTube blocks downloads from the cloud box (bot check), so the decode uses:
- his full auto-transcript (4,815 words, word-timed);
- YouTube's frame storyboards (150 frames, one every ~8.5s);
- the chapter list and description;
- the free blueprint he links (a public Claude artifact; pipeline numbers below).

A scene-by-scene AI visual analysis was also queued. Frame-stepping the real file at 10-15fps still needs the MP4: if Jason drops it in chat, re-run the usual analyzers on it.

## 1. Premise and angle (why it works)
**The video IS the proof.** Line one: "This entire video was edited by Claude." The viewer spends 21 minutes inside the evidence, so the claim never has to be argued. It is the strongest hook shape there is: *the medium proves the message*.

**Hook stack, first 110 seconds (every beat is a separate psychological lever):**
| t | Line | Lever |
|---|---|---|
| 0:00 | "This entire video was edited by Claude. Not just the intro…" | Meta-proof + pre-empting the obvious doubt ("just the intro") |
| 0:08 | "When I say fully automated, I mean I *fully* automated" | Repetition = conviction; it signals he is not exaggerating |
| 0:14 | "send a prompt, raw footage, wait a couple hours…" | The process made concrete and small; the dream looks effortless |
| 0:28 | "while I work, sleep, play video games" | The lifestyle payoff, which is the real desire, not the tool |
| 0:42 | "the **last** video you will ever need on AI video editing" | Finality and authority claim (caption accent on "last", in red) |
| 0:51 | "works on any agent, any model, any app, in the future" | Removes the risk of it going out of date |
| 0:56 | "I have **real proof**… customers… outliers" (shows their videos) | Social proof by named people plus visible numbers |
| 1:24 | "my life's work for 3 months, 86,000 lines, 335 commits" | Effort = value; precise numbers = credibility |
| 1:34 | "in this video I'm giving it all away" | Reciprocity: give before asking |
| 1:39 | "editor, creator, or posting your first video" | Widens the room; every viewer is named |
| 1:47 | "let's get **straight** into it" | Pace promise, then he delivers on it |

**Body structure:**
1. Free value (how it works) at 1:51.
2. The paid offer early (2:56): one honest pitch, never repeated in the middle.
3. Objections answered in advance:
   - "CapCut works, but you'll have to step away";
   - "token cost? ~$5 per edit, it's inside your plan".
4. Live demo as proof, with an on-screen clock: "started 12:20, it's 22 minutes later".
5. Customer testimonials last: other people say the big claims, not him ("30 videos done overnight", "doubled my views first week").
6. A soft close with both doors open: paid or free.

**The tone:** casual, unpolished, honest. He admits the limits ("CapCut is the worst", "it didn't go crazy because I told it to be fast"). The admissions are what make the strong claims believable.

## 2. The core lesson for OUR system: PRESETS (he calls it "the secret sauce")
> "Out of the box Claude has the tools but no taste, so you get generic AI slop. I hand-built my animations and graphics, dialed them in by hand, then had Claude **save the values**. So it doesn't creatively come up with these things from scratch every time; it's just following the recipe." … "after every edit tell it: take everything we learned this session and **bake it into the preset**, so next time you get it right first try."

- That is exactly what this skill is (rules + journal + kit). His point, though, is **values, not descriptions**: exact numbers saved as code. That is why our kits live as `.tsx` files with fixed constants (`Coop.tsx`, `Glass.tsx`), and why a beat must reuse a kit component instead of hand-animating a new one.
- **One preset per format** (his: YouTube default, short-form, vlog). Ours: the 8.3 recipe = talking-head short; Coop look = graphics-cutaway short.
- He starts every session **inside the project folder** so CLAUDE.md and the 20+ skills load. Ours: the skill lives in the repo, same principle.

## 3. Look (from the storyboard frames + his own words)
- **Glow layer over everything**, **grain on the background**, and **all motion graphics move at 12 fps** ("a very cinematic style for motion graphics"). That is held frames on a 30fps timeline (3-2-3-2), not smooth 30fps tweening. → `Coop.tsx`: `useStep()`, `Glow`, `Grain`.
- **Captions:**
  - lowercase;
  - 2-4 words per chunk;
  - bold white sans + ONE accent word in **italic serif**, slightly larger: "the *last* video you ever need", "i have real *proof*", "let's get *straight* into", "*baked* it", "no official *MCP*", "edit the video almost *perfectly*", "in your *business*";
  - placed lower-middle, no box, soft shadow;
  - the accent is sometimes coloured (red on "last").
  
  → `CoopCaptions` with Instrument Serif italic (free, OFL).
- **Graphics = full-screen hard cutaways** on a near-black stage with a soft **blue→violet light band** low in the frame. Then back to the face. They alternate; it is never all graphics or all face.
- **Real assets, never placeholders:**
  - real app icons (CapCut, Resolve, FCP, Premiere);
  - real YouTube thumbnails grid;
  - a real YouTube **Comments** card ("the token cost is so expensive");
  - the real Grokbot icon (Claude fetched it from the web itself);
  - a real Claude "Pro $20" plan card;
  - a real Zoom grid for testimonials.
- **Graphic types seen:**
  - a big glowing red **✗** + "Don't Do This";
  - an equation of tiles ("$20/month ÷ ▢▢▢▢ = 4 edits", rounded colour tiles);
  - a **green pixel-grid** "Claude is Editing" timeline;
  - app-icon rows;
  - pricing cards;
  - a comment card;
  - a big title with icon ("GROKBOT");
  - screen recordings with a **circular face-cam** bottom-right.
- **Camera footage grade:** "Autumn Rec709 at 80% intensity, 120% saturation", a warm look, applied **only to camera footage, never to screen recordings or graphics**.
- **Layouts rotate** (explainer): split, tight, wide, full, card.

## 4. Pipeline numbers (from his free blueprint)
- **Intake:**
  - copy the raw untouched;
  - name the job;
  - read the format from the footage;
  - keep a resumable run file and a list of content that must never show on screen.
- **Rough cut:** transcribe once; remove filler and false starts; produce an EDL and a finished script; check the cut against the script.
- **Audio:** speech at **−17 LUFS** into a −6 dBFS limiter; a second voice is lifted when it sits more than 3 dB under; stacked SFX are held under **−1 dBTP**; an opt-in music bed at −20 dB with a 2s tail.
- **Graphics:** storyboard → build → review: an automated QA pass first, then **max 3 review rounds**. SFX are **planned from the placed graphics** (every graphic gets its sound).
- **Export:** vertical 1080×1920, CBR 14 Mbps, AAC 320k, bt709.
- **Review is for taste only.** Mechanics are already handled by the preset.

## 5. What we take, mapped to our rules
| His | Ours (decision) |
|---|---|
| The video is the proof | Hook rule: when Jason's claim can be *shown* (money, results, the edit itself), the first frame shows it, not tells it |
| Repetition, exact numbers, lifestyle payoff, "last video you'll need", "giving it all away", objections answered early, testimonials last | Added to methodology §psychology as the **long-form proof stack**; for shorts, use the first 4 levers in ≤ 6s |
| Presets = saved values | Every look is a kit file of constants; beats reuse kit components; "bake it in" = rule + journal + kit commit (already our loop) |
| 12fps MG + glow + grain | `Coop.tsx`: `useStep`, `Glow`, `Grain` (MG v5) |
| lowercase + italic-serif accent captions | `CoopCaptions` (MG v5). **Not yet a rule:** our locked caption style is two-tier gold keywords; Jason decides after v5 |
| Hard cutaway ↔ face alternation | MG v5 structure: face, cutaway, face… never > ~2.6s of graphics without his face unless the graphics carry the sentence |
| Real assets only | Already our rule (IosNotify, simple-icons). Extend: fetch real logos/thumbnails from the web when a brand is named |
| Autumn grade on camera only | `Video look=` warm grade (sat 1.2, sepia .12, warm soft-light wash) + grain; graphics keep their own colours |
| −17 LUFS speech, SFX ≤ −1 dBTP | Final master: `loudnorm I=-17:TP=-1:LRA=11` on the mix (was −14 per part) |
| Max 3 review rounds, QA first | Our stills QA = his automated pass; aim to land in ≤ 3 rounds with Jason |
| Colour meaning | Unchanged and locked: gold = key idea, green = win, red = problem. His blue/violet band is the *stage*, never a meaning colour |
