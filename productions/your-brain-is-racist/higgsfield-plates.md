# Higgsfield plates: not generated (workspace out of credits)

On 2026-11-10 the Higgsfield workspace (plan: plus) held **0 credits** and no unlimited allowance. The one generation attempted
was refused: "Out of credits in the selected workspace." **No Higgsfield job ids exist for this film.**
Quoted costs that day: image 0.25 credits (gpt_image_2_6), 4 s video 28 credits (seedance_2_5, 720p), narration line 0.9 credits (seed_audio).
A full plate set as the brief lists it is 13 video prompts x 2 aspect ratios, roughly 1,000 credits at those rates.

Every shot below is currently a procedural plate drawn in `src/plates.py`. To swap one for a Higgsfield plate, generate it,
save it under `plates/<slot>_<h|v>.mp4`, and replace that slot's draw call in `src/film.py` with a video-frame read. The scene
clock, type, captions and sound do not change.

Rules from the brief: every prompt ends with "no text, no logos, no readable signage". Reject any output where a face is clear
enough to be a person. Keep one grain and palette; regrade in the edit, do not re-prompt.

| Slot | Shot | Type | Prompt |
|---|---|---|---|
| eye | 2, 26 | video 4 s | Extreme macro of a human eye in low light, pupil contracting, cinematic, 35mm, shallow depth, muted palette, photoreal, no text, no logos, no readable signage |
| screens | 3, 19, 28 | video 6 s | Hundreds of translucent television and phone screens receding into darkness, faint glow, dust in the air, cinematic, photoreal, no readable content, no text, no logos, no readable signage |
| couch | 4 | image, then 5 s motion | Small child seen from behind sitting on a couch in a dark living room, lit only by a television glow, 1990s, cinematic, photoreal, no face visible, no text, no logos, no readable signage |
| card_tank | 5 | image | Silhouette of a man in a tank top against a concrete wall, backlit, no facial features, cinematic, no text, no logos, no readable signage |
| card_hat | 6 | image | Silhouette of a man, wide-brimmed hat, backlit, no face, no text, no logos, no readable signage |
| card_suit | 7 | image | Silhouette of a man in a suit holding a briefcase, office window, backlit, no face, no text, no logos, no readable signage |
| street1, street2 | 9–12 | video 8 s, two variants | First-person POV walking on a city sidewalk at night, streetlights, a distant figure approaching out of focus, cinematic, anamorphic, photoreal, no text, no logos, no readable signage |
| cruiser | 14–18 left | video 6 s | Interior of a police cruiser at night, POV of the officer, hand resting near the belt, red and blue light reflecting, cinematic, photoreal, no face, no text, no logos, no readable signage |
| sedan | 14–18 right | video 6 s | Interior of an older sedan at night, POV of the driver, rearview mirror filled with red and blue lights, hands on the wheel, cinematic, photoreal, no face, no text, no logos, no readable signage |
| boy | 20–22 | video 6 s | Teenage boy seen from behind watching television in a dark room, the screen shows a backlit silhouette, cinematic, photoreal, no faces, no text, no logos, no readable signage |
| glass | 24 | video 5 s | A man in a suit speaking in a glass-walled meeting room seen from the hallway, reflections on the glass, face softened by reflection, cinematic, photoreal, no text, no logos, no readable signage |

Narrator audition, if Jason does not record: Higgsfield preset male voices to try on the first four lines and the traffic stop
are Marcus, Callum and Bram (seed_audio). They were not auditioned; no credits.
