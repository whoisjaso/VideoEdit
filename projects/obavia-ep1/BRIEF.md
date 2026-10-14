# PROMPT: Build "Obavia Ep1 — Two Scared People" as a code-only animated short

You are an expert motion designer + React/Remotion engineer + sound designer. Build a polished ~100-second vertical animated short entirely in code (no AI image/video generation, no stock footage). Deliver a working Remotion project and a rendered MP4. Read everything below before writing code.

## 1. What this is
A short-form interactive explainer series for **Obavia** (live sales-call intelligence — the psychology of conversations). Episode 1 premise, told in second person ("you"): you just got pulled over at night. A traffic stop is two scared humans labeling each other before a word is said. He fears for his safety and wears the weight of the badge; you feel judged and judge him back. The episode teaches how to disarm fear on both sides through calm, honest, visible behavior, then ends on a cliffhanger choice that the audience votes on in comments.

Tone: brisk, conspiratorial, game-like, a little dark but never preachy. Responsible: honest compliance, no advice to lie/evade/argue, no legal-advice claims, stereotypes shown as *perceptions in both directions*, never endorsed.

## 2. Technical stack (required)
- Remotion 4 (React + TypeScript), composition 1080×1920, 30 fps, H.264 + AAC, CRF ≈18.
- All visuals = SVG/HTML/CSS in React. Fonts: **Anton** (headlines/captions), **JetBrains Mono** (HUD, sources). Load them locally (@remotion/google-fonts or local files).
- Audio: one pre-mixed WAV (VO + music + SFX) placed with `<Audio>`, OR separate `<Audio>` layers — either way every SFX time must come from the same cue data the visuals use.
- VO: generate with the best TTS available (ElevenLabs if available; otherwise a neural TTS such as Edge/Azure neural or Piper). Must provide **word-level timestamps** (e.g. edge-tts `boundary="WordBoundary"`, ElevenLabs `with_timestamps`, or forced alignment via whisperx/aeneas).
- Single source of truth: write `timeline.json` (shots with start/end, VO clips, words with times) and `cues.json` (named event times derived from words). Visuals AND the audio mixer both read these. Never hand-type a time in two places.

## 3. Script (VO, natural pace)
Narrator: male, low, warm, slightly conspiratorial, **natural speed (0 to +5%)**, ~150–165 wpm. Officer: deeper, calm, flat. "You" lines (if any): younger, neutral.
Pacing rules: 300–450 ms between sentences/clips; 250 ms between shots; an extra 0.4–0.8 s of silence *before* key reveals (the admission card, the choice split, the black frame, the end card). The silence sits on the outgoing shot so the cut lands on the reveal.
## Full VO
- **hook** — You just got pulled over. And before either of you says a word... you've already judged each other.
- **two** — Two scared people. One window between you.
- **hispov** — From his seat, he's reading your car. Paper tags. Loud music. Tank top. Every movie he's seen fills in the rest.
- **danger** — His training says any stop could turn deadly. One big Florida study put killings at about one in six and a half million stops. / But fear doesn't read data.
- **yourpov** — Meanwhile, you're labeling him. Power trip. Quota. The badge, the ego, the idea that he's supposed to be fair. You feel all of it.
- **bias** — And it's not just you two. In a famous study, split-second threat decisions followed cultural stereotypes, even in people with no personal prejudice.
- **slice** — A face gets judged in a tenth of a second. What he sees lands before what you say.
- **disarm** — So disarm the fear. Hazards on. Dome light on. Window down. Hands on the wheel. Driver handbooks say it plainly. Let him see you.
- **window** — Footsteps. Flashlight. He sees your hands, and his shoulders drop. / OFFICER: "Do you know why I stopped you?"
- **admit** — That question invites an admission. If you honestly don't know, say, no officer, could you tell me? / If you do know, don't lie. Keep it short and honest.
- **twoshot** — OFFICER: "Your registration expired last month."
- **clip** — He goes quiet. Clipboard. Five seconds left.
- **split** — One sentence. Do you explain why it lapsed... or just apologize?
- **black** — One drops his guard. The other raises it.
- **end** — Comment one word. Majority writes Part 2.


## 4. Shot list (target timings — re-derive from your VO; keep order and content)
## Shot list (timings from actual VO)
| Time | Shot | Visual | VO | HUD | SFX/Music | On-screen text |
|---|---|---|---|---|---|---|
| 0:00.00–0:05.74 | hook | Car interior, YOU (round head, tank top) behind wheel, red/blue siren light pulsing through rear window, slow push-in 1.12→1.28. Mood scared→worried, sweat drop. | You just got pulled over. And before either of you says a word... you've already judged each other. | CLOCK 0:60 · YOUR FEAR 6 · HIS FEAR 5 | Siren double-chirp @0.05s; whoosh into each caption | 'BEFORE A WORD IS SAID' → swaps (no overlap) to 'YOU'VE ALREADY JUDGED EACH OTHER' on word "judged" |
| 0:05.74–0:08.66 | two | Split screen: YOU in car (top) / OFFICER in cruiser lit by cyan laptop glow (bottom), both scared; halves slide in. | Two scared people. One window between you. | CLOCK starts 60→ · both fear 6 | Low double heartbeat | 'TWO SCARED PEOPLE' (bottom pill) |
| 0:08.66–0:16.84 | hispov | Officer POV through windshield: your beat-up car (dent, mismatched panel, paper TEMP tag), muffled bass + bouncing ♪, officer's eyes in rear-view mirror narrowing. Thought-tags pop on each word. | From his seat, he's reading your car. Paper tags. Loud music. Tank top. Every movie he's seen fills in the rest. | HIS FEAR 6→8 | Muffled boom-bap car stereo; pop per tag; thump on DANGER? | Tags: PAPER TAGS? · LOUD MUSIC · TANK TOP · DANGER? (red) — at their words |
| 0:16.84–0:27.38 | danger | Beige card, officer worried→calm. | His training says any stop could turn deadly. One big Florida study put killings at about one in six and a half million stops. / But fear doesn't read data. | HUD hidden | Whoosh in; ding on number; low hit on 'fear' | Title HIS TRAINING SAYS; one content block at a time: ANY STOP COULD TURN DEADLY → 1 IN 6.5M (routine stops where an officer was killed) → BUT FEAR DOESN'T READ DATA |
| 0:27.38–0:36.45 | yourpov | YOU in car glancing at side mirror (officer reflected, hands on hips). Mood worried→suspicious. | Meanwhile, you're labeling him. Power trip. Quota. The badge, the ego, the idea that he's supposed to be fair. You feel all of it. | YOUR FEAR 6→7.5 | Pop per tag | Tags: POWER TRIP? · QUOTA? · THE BADGE · 'IMPARTIAL'? (red) |
| 0:36.45–0:45.86 | bias | Beige card, two heads eyeing each other, dashed cyan line between. | And it's not just you two. In a famous study, split-second threat decisions followed cultural stereotypes, even in people with no personal prejudice. | hidden | Whoosh; click on 'even' | SPLIT-SECOND THREAT CALLS FOLLOWED CULTURAL STEREOTYPES → EVEN IN PEOPLE WITH NO PERSONAL PREJUDICE |
| 0:45.86–0:51.09 | slice | Beige card, stopwatch sweeps 36° on 'tenth'. | A face gets judged in a tenth of a second. What he sees lands before what you say. | hidden | Shutter double-click on 'tenth' | 0.1 SEC → WHAT HE SEES LANDS BEFORE WHAT YOU SAY |
| 0:51.09–1:00.10 | disarm | Beige card, 2×2 icons pop on their words (hazard triangle blinks). | So disarm the fear. Hazards on. Dome light on. Window down. Hands on the wheel. Driver handbooks say it plainly. Let him see you. | hidden | Hazard ticks on 'Hazards'; switch click 'Dome'; window motor 'Window'; grip thump 'Hands'; riser+ding into 'Let' | Icon labels; caption LET HIM SEE YOU. |
| 1:00.10–1:08.28 | window | YOUR POV out lowered driver window, dome light warm, hazards blinking amber (synced to ticks). Officer walks in with stepped bob per footstep, flashlight clicks on, beam moves to your hands, shoulders drop + face softens on 'drop'. Lip flaps from VO amplitude. | Footsteps. Flashlight. He sees your hands, and his shoulders drop. / OFFICER: "Do you know why I stopped you?" | HIS FEAR 8→4 on 'drop' | Footstep per visual step; flashlight click; whoosh-down on 'drop'; hazard ticks | Tag DANGER? over him fades on 'drop'; then bubble "Do you know why I stopped you?" |
| 1:08.28–1:18.34 | admit | Beige card, big speech bubble with cyan '?'. | That question invites an admission. If you honestly don't know, say, no officer, could you tell me? / If you do know, don't lie. Keep it short and honest. | hidden | Riser, whoosh, pop on each 'If' | IT INVITES AN ADMISSION → HONESTLY DON'T KNOW? "No, officer — could you tell me?" → DO KNOW? DON'T LIE. SHORT & HONEST. |
| 1:18.34–1:22.13 | twoshot | Two-shot: YOU at wheel (left), officer at window (right), relaxed, lip-synced. | OFFICER: "Your registration expired last month." | YOUR FEAR 5 · HIS 4 | Hazard ticks | Bubble "Your registration expired last month." |
| 1:22.13–1:26.34 | clip | Officer writing; pen strokes animate only during scratch SFX windows; inset circle of YOU sweating; red pulsing vignette; push-in. | He goes quiet. Clipboard. Five seconds left. | CLOCK hits 0:05 on 'Five', flashes red; YOUR FEAR 7→8 | Pen scratches ×3 (matched to strokes); fast heartbeat | 5 SECONDS LEFT |
| 1:26.34–1:31.42 | split | EXPLAIN panel slams down on 'explain', APOLOGIZE up on 'apologize', VS badge. | One sentence. Do you explain why it lapsed... or just apologize? | CLOCK →0:00 · YOUR FEAR 9 | Riser + impact on each word; heartbeat | ONE SENTENCE. (cleared before panels) → panel labels |
| 1:31.42–1:34.69 | black | Black. | One drops his guard. The other raises it. | hidden | Impact on 'One', thump on 'The'; music silent | ONE DROPS HIS GUARD. → THE OTHER RAISES IT. |
| 1:34.69–1:40.24 | end | Beige end card, buttons spring in. | Comment one word. Majority writes Part 2. | hidden | Impact + ding; music outro | COMMENT ONE WORD · EXPLAIN / APOLOGIZE · MAJORITY WRITES PART 2 · @obavia — the psychology behind every conversation · Not legal advice |


## 5. Style guide (match the reference reel)
**Characters** — faceless-style round-head stickmen:
- Head: big circle (r≈112 at 1×), off-white #F6F2EA (YOU) or navy #2c3a5e (OFFICER, with flat-brim cap + small cyan diamond badge), 9px near-black outline #121418, soft top-left highlight.
- Eyes: two black ovals with a white catch-light; size/height drive emotion; blinks every ~3.3 s (cosine squash, ~7 frames), small saccades (sum of slow sines).
- Brows: single thick strokes; angle encodes mood (worried = inner ends up, stern/suspicious = inner ends down).
- Mouth: curve whose bend = mood; when that character speaks, replace with an ellipse whose height follows **VO amplitude per frame** (RMS of that speaker's audio at 30 fps) = lip flaps. Narrator never moves anyone's mouth.
- Body: rounded hoodie/tank-top shape; YOU wears a light tank top (skin-colored arms), OFFICER navy uniform.
- Arms: thick outlined quadratic curves with round hands; named poses (down, wheel, gesture, write, bow, hips, flash) blended with eased interpolation.
- Motion: "puppet-limited" but smooth — breathing (±5 px, ~0.75 Hz), head lags body by ~6 frames (secondary motion), slow body sway, arm wobble, spring pops. Moods blend over 10–20 frames (never snap). Shoulders drop visibly when the officer relaxes.
- Mood presets: neutral, scared, worried, calm, relieved, stern, suspicious, sad, focused (each = eye scale, brow angle, smile, lid).
**Thought-tags** (the "labels" each person puts on the other): cream pill (#F6F2EA, 5 px ink border, Anton ~58 px, hard drop shadow) with two trailing "thought bubble" dots toward the head; spring-pop in on the exact spoken word, gentle bob, red (#E63946, white text) for the loaded label (DANGER?, 'IMPARTIAL'?). Fade out when the fear is disarmed.
**Night scenes**: deep navy/black gradients (#04060c → #0c1222), red/blue siren light as smooth alternating radial glows (screen blend, ~1.4 Hz), amber hazard glow that blinks in sync with hazard ticks, warm dome-light cone after "Dome light on", flashlight beam (soft cone + hot spot) from the officer's hand, bokeh, film grain (6%), vignette. Slow push-ins on every night shot (scale 1.00→1.06–1.28, ease-in-out sine).
**Fact cards**: flat beige #EFE6D2 with faint scanlines, ink #1A1A1A, exactly ONE neon accent: cyan #00E5FF (use a darker teal #0097a8 only for accent text legibility on beige). Title zone at top with a cyan underline that draws in; one content block in the middle that *replaces* itself (never stacks); source line in mono at the bottom. Cards slide in from the left with a spring.
**HUD** (top, night shots only): three dark translucent panels — CLOCK (mono 0:SS; counts 60 → hits exactly 0:05 on "Five seconds left" → 0:00 at the choice; flashes red ≤5), YOUR FEAR and HIS FEAR (10 segments each, partial fill, cyan → amber → red with glow at ≥7, border turns red at ≥7). Fear keyframes follow the story (his rises with each label, drops sharply on "his shoulders drop"; yours climbs to 10 at the black frame). No fake percentages.
**Kinetic captions**: Anton, white with dark stroke + shadow on night scenes, ink on cards; words spring up staggered 2 frames; one accent word in cyan.

## 6. Strict layout rules (zero tolerance)
- **Only one text block on screen at a time** in each region; when a new caption/block arrives, the previous fades out over the 5 frames *before* it. Card title + one content block + source footer are allowed together because they live in fixed, non-overlapping zones.
- Safe zones (1080×1920): HUD y 64–234 · bubbles/tags y 290–620 (or explicitly placed tags elsewhere that never intersect another text element) · card title y 250–400 · content y 470–1600 · captions y 1400–1680 · source footer y 1790–1840 · side margins ≥ 60 px.
- Text auto-fits: font size = min(max, width·lines / (chars·0.52), width / (longestWord·0.56)). Never let text touch the frame edge.
- Text/tags/bubbles are rendered **outside** the push-in scale layer so camera moves never push them off-screen or into the HUD.
- Never put a caption on screen while a speech bubble is up.

## 7. Sound design
- Music (synthesize or use a royalty-free track): dark D-minor synth bed ~92 BPM — detuned saw pad (Dm–B♭–Gm–A, low-passed ~700 Hz), sub-bass 8ths, kick + off-beat hats only in tension sections, reverbed plucked arpeggio in build-ups. Side-chain duck ~-5 dB under VO. Near-silence under the officer's first line, building heartbeat-driven tension through clipboard → choice, total silence on the black frame, short sting on the end card.
- SFX must be **frame-matched to on-screen events**, generated from cues.json:
## SFX / visual cue sheet (reference timings from a prior build — recompute from YOUR VO word timestamps)
| Time | Frame | Event |
|---|---|---|
| 0.05s | 2 | siren double-chirp (lights already pulsing) |
| 10.95s | 329 | tag pop tag1 |
| 12.07s | 362 | tag pop tag2 |
| 13.07s | 392 | tag pop tag3 |
| 14.15s | 425 | tag pop tag4 |
| 22.03s | 661 | ding — 1 IN 6.5M appears |
| 25.46s | 764 | low hit — BUT FEAR card |
| 29.29s | 879 | tag pop tag1 |
| 30.24s | 907 | tag pop tag2 |
| 31.02s | 931 | tag pop tag3 |
| 33.95s | 1019 | tag pop tag4 |
| 42.70s | 1281 | click — "even…" block |
| 47.09s | 1413 | shutter — 0.1 SEC + stopwatch sweep |
| 52.57s | 1577 | icon i1 + matched SFX |
| 53.51s | 1605 | icon i2 + matched SFX |
| 54.50s | 1635 | icon i3 + matched SFX |
| 55.48s | 1664 | icon i4 + matched SFX |
| 58.43s | 1753 | ding — LET HIM SEE YOU |
| 60.25s | 1807 | footstep (officer bob dips) |
| 60.67s | 1820 | footstep (officer bob dips) |
| 61.09s | 1833 | footstep (officer bob dips) |
| 61.18s | 1835 | flashlight click — beam on |
| 61.51s | 1845 | footstep (officer bob dips) |
| 63.95s | 1919 | whoosh-down — shoulders drop, DANGER? fades |
| 65.11s | 1953 | officer line + bubble |
| 70.25s | 2108 | pop — admit block swap |
| 74.69s | 2241 | pop — admit block swap |
| 83.41s | 2502 | pen scratch 0.6s (stroke draws) |
| 84.23s | 2527 | CLOCK = 0:05, caption |
| 84.31s | 2529 | pen scratch 0.6s (stroke draws) |
| 85.21s | 2556 | pen scratch 0.6s (stroke draws) |
| 87.66s | 2630 | impact — EXPLAIN panel |
| 89.31s | 2679 | impact — APOLOGIZE panel + VS |
| 91.53s | 2746 | impact — ONE DROPS HIS GUARD |
| 92.79s | 2784 | thump — THE OTHER RAISES IT |
| 94.69s | 2841 | impact + ding — end card |


- Footsteps: the officer's walk is computed from the same step list — each footstep = a body dip in the animation.
- Pen scratches only while the pen line is visibly drawing; hazard ticks only when the hazard glow is on.

## 8. Facts (use exactly; cite on cards)
## Sources
1. BJS, *Contacts Between Police and the Public, 2022* — traffic stops are the most common police contact (context only). https://bjs.ojp.gov/document/cbpp22.pdf
2. Woods, J.B. (2019). *Policing, Danger Narratives, and Routine Traffic Stops.* Michigan Law Review 117(4). Danger narrative "permeates police training"; conservative estimate: felonious killing of an officer 1 in every 6.5 million routine stops (10 yrs, 200+ Florida agencies). https://michiganlawreview.org/journal/policing-danger-narratives-and-routine-traffic-stops/
3. Correll, Park, Judd & Wittenbrink (2002). *The police officer's dilemma.* JPSP 83(6). Shoot/don't-shoot bias tracked awareness of cultural stereotypes, not personal prejudice; seen in Black and White participants. https://pubmed.ncbi.nlm.nih.gov/12500813/
4. Willis & Todorov (2006). First impressions after a 100-ms exposure to a face. *Psychological Science* 17(7). (Also: Ambady & Rosenthal 1992 thin-slices meta-analysis, https://doi.org/10.1037/0033-2909.111.2.256)
5. AAMVA — What to do when stopped: engine off, interior lights on at night, hands visible, stay in vehicle. https://www.aamva.org/law-enforcement/what-to-do-when-stopped-by-law-enforcement
6. Texas DPS Driver Handbook — hazard lights on, dome light at night, lower window if safe, hands on wheel. https://www.dps.texas.gov/sites/default/files/documents/docs/dlhandbook.pdf
7. Jack Rice Defense / Cardon Stuart Law — "Do you know why I stopped you?" seeks an admission; "No, officer" if you don't know. https://www.jackricelaw.com/blog/what-do-i-say-when-the-cop-says-do-you-know-why-i-stopped-you · https://cardonstuartlaw.com/what-to-say-pulled-over

Dropped as unverifiable: "officers watch the same how-to-act videos" (replaced with "driver handbooks say it plainly"); media-shapes-labels kept as narration ("every movie he's seen") without a stat; "window ALL the way down" softened to "window down" (handbook: lower window if safe). Admission nuance (honestly admit if you know) is honesty framing, not legal advice.


## 9. End card
Beige: "YOUR MOVE" · "COMMENT ONE WORD" · two big buttons EXPLAIN (cyan) / APOLOGIZE (white) · "MAJORITY WRITES PART 2" · small "@obavia — the psychology behind every conversation" · tiny "Not legal advice. Stay calm, honest, respectful." No sales pitch.

## 10. QA checklist (do all before delivering)
1. Render stills at 15%, 50%, 85% of EVERY shot; inspect each: no overlapping text, nothing clipped, nothing under the HUD, ≥60 px margins.
2. Additionally sample at every cue time ±3 frames (text swaps) to catch two blocks visible at once.
3. Print a cue table (time, frame, event) and confirm each SFX lands within ±1 frame of its visual.
4. Lip flaps only during that character's audio; mouths closed during narrator lines.
5. CLOCK reads 0:05 on the word "Five"; 0:00 at the black frame.
6. Listen through: VO intelligible over music everywhere; no clipping (peak ≤ -1 dBFS); pauses feel natural.
7. Confirm runtime 95–105 s, 1080×1920, 30 fps, audio present.
8. Check every on-screen fact against Section 8; nothing invented.
9. Deliver: project folder, MP4, 4 PNG stills (hook, a fact card, clock-at-5 moment, choice screen), and the cue table.
