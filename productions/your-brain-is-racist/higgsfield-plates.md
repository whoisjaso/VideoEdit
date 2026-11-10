# Higgsfield plates: not generated (workspace out of credits)

On 2026-11-10 the Higgsfield workspace (plan: plus) held **0 credits** and no unlimited allowance. The one generation attempted
was refused: "Out of credits in the selected workspace." **No Higgsfield job ids exist for this film.**
Quoted costs that day: image 0.25 credits (gpt_image_2_6), 4 s video 28 credits (seedance_2_5, 720p), narration line 0.9 credits (seed_audio).
A full plate set as the brief lists it is 13 video prompts x 2 aspect ratios, roughly 1,000 credits at those rates.

"Free trial" was also tried (use_unlim). Higgsfield's answer: "You are using Higgsfield from Claude Code, where unlimited
generations are not available. They are available in: Claude chat, Claude Cowork, ChatGPT." So the free-trial allowance has to be
spent from one of those, or credits added for this workspace.

## How to get the plates in

1. In Claude chat (claude.ai) with the Higgsfield connector, paste the table below and say "generate each of these in 16:9 and 9:16
   on my free trial". Download the results.
2. Name each file after its slot and aspect and put it in `plates/`: `eye_h.mp4`, `eye_v.mp4`, `couch_h.png`, `street1_v.mp4` …
   (`h` = 16:9, `v` = 9:16; mp4, mov, webm, png or jpg).
3. Re-render (`src/render.sh h <work>`, `src/render.sh v <work>`, `src/finish.sh <work>`). Any scene with a file in `plates/` uses it;
   scenes without one keep the procedural plate. Type, captions, timing and sound do not change. Tested with a stand-in image.

Each dropped-in plate gets the same slow push, muted saturation and vignette, and `observer_*` gets the amber regrade, so the film
keeps one palette. Video plates play at half speed, blended and ping-ponged, so a 4 to 8 second clip covers a long scene.

What a dropped-in plate cannot do that the procedural one does: the pupil contracting on "one job", the camera drifting across the
road on "cross the street", the screen's outline settling onto the boy on "repetition becomes identity", and each half of the
traffic stop dimming while the other man's script runs. For `stop`, supply one clip that already has both points of view side by
side (stacked for 9:16). If those moves matter more than photoreal texture, keep the procedural plate for that scene.

Rules from the brief: every prompt ends with "no text, no logos, no readable signage". Reject any output where a face is clear
enough to be a person. Keep one grain and palette; regrade in the edit, do not re-prompt.

| Slot | Shot | Type | Prompt |
|---|---|---|---|
| eye (and observer) | 2, 26 | video 4 s | Extreme macro of a human eye in low light, pupil contracting, cinematic, 35mm, shallow depth, muted palette, photoreal, no text, no logos, no readable signage |
| screens, news, newscript | 3, 19, 28 | video 6 s | Hundreds of translucent television and phone screens receding into darkness, faint glow, dust in the air, cinematic, photoreal, no readable content, no text, no logos, no readable signage |
| couch | 4 | image, then 5 s motion | Small child seen from behind sitting on a couch in a dark living room, lit only by a television glow, 1990s, cinematic, photoreal, no face visible, no text, no logos, no readable signage |
| card_tank | 5 | image | Silhouette of a man in a tank top against a concrete wall, backlit, no facial features, cinematic, no text, no logos, no readable signage |
| card_hat | 6 | image | Silhouette of a man, wide-brimmed hat, backlit, no face, no text, no logos, no readable signage |
| card_suit | 7 | image | Silhouette of a man in a suit holding a briefcase, office window, backlit, no face, no text, no logos, no readable signage |
| street1, street2 | 9–12 | video 8 s, two variants | First-person POV walking on a city sidewalk at night, streetlights, a distant figure approaching out of focus, cinematic, anamorphic, photoreal, no text, no logos, no readable signage |
| stop (left / top half) | 14–18 | video 6 s | Interior of a police cruiser at night, POV of the officer, hand resting near the belt, red and blue light reflecting, cinematic, photoreal, no face, no text, no logos, no readable signage |
| stop (right / bottom half) | 14–18 | video 6 s | Interior of an older sedan at night, POV of the driver, rearview mirror filled with red and blue lights, hands on the wheel, cinematic, photoreal, no face, no text, no logos, no readable signage |
| boy, three | 20–22 | video 6 s | Teenage boy seen from behind watching television in a dark room, the screen shows a backlit silhouette, cinematic, photoreal, no faces, no text, no logos, no readable signage |
| glass | 24 | video 5 s | A man in a suit speaking in a glass-walled meeting room seen from the hallway, reflections on the glass, face softened by reflection, cinematic, photoreal, no text, no logos, no readable signage |

Narrator audition, if Jason does not record: Higgsfield preset male voices to try on the first four lines and the traffic stop
are Marcus, Callum and Bram (seed_audio). They were not auditioned; no credits.
