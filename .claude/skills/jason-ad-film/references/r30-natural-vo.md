# r30 · NATURAL VO: talk like a person, not an ad (Jason, 2026-11-02)

> "You want to sound like a human being, not a robot... I wouldn't say 'Never fly, always on the go. Eggs, bacon, cheese.'
> It's supposed to be 'You're always fly, and you're always on the go. Whether it's egg, bacon, or cheese.'
> Those little small filler words are what make you human... I want to optimize for just saying, straight to the point, clean."

Applies to every voiceover script (ads, explainers, client demos, motion pieces, chapter films). It sits on top of
the video-editing-standard rule in `docs/preproduction/voiceover-human.md`.

## The rule
Write the VO the way you'd **say it** to someone across the table, not how an advertiser cuts copy.
- **Join every list with connective words.** Use "and", "or", "whether it's", "so", "and that's", "right?", "you know".
  Never use a bare comma list or a stack of noun fragments.
- **Full sentences with a subject and a verb.** "You're always on the go" is right. "Always on the go" is wrong.
  An ad fragment ("Setup. Training. Thirty days of fixes.") becomes a sentence ("That covers setup, training, and thirty days of fixes.").
- **Lead into lines the way people talk:** "So", "And", "Now", "Look", "That's", "Here, ...". Use at least one per two lines.
- **Small words carry the emotion:** "your", "you've got", "already", "honestly", "just", "right?". Spend them on
  feeling and flow. Keep numbers, prices and facts plain, with no hedge before a number.
- **Still clean and straight to the point.** Fillers are connective tissue, not rambling: no "um/uh", no padding sentences.
- A one-word punch is fine **once** per ~20 s (a title slam). Everything else is a spoken sentence.

## Before → after (Royalty explainer v1, Nov 2026: the ad-cut version that Jason flagged)
| Ad-cut (don't) | Spoken (do) |
|---|---|
| That's real business. It comes in through calls, texts, Facebook, people you know. | And that's real business, right? It comes in through phone calls, through texts, through Facebook, and honestly just people you already know. |
| Every customer gets their own link. It's theirs for good, so they can share it anytime. | So every customer you've got gets their own link, and it's theirs for good, so they can share it whenever they want. |
| Start with a free pilot. Fourteen days, a real working version, and no obligation after. | And you can start with a free pilot. That's fourteen days with a real, working version, and there's no obligation after that. |
| Setup, training, and thirty days of fixes. | And that covers your setup, your training, and thirty days of fixes. |
| AWhite Solutions. Systems to find more jobs. | We're AWhite Solutions, and we build the systems that help you find more jobs. |

## Script gate (run before recording)
1. Read every line out loud. If you wouldn't say it that way on a phone call, rewrite it.
2. Look for bare comma lists or noun fragments. Every list needs a connective, and every fragment gets a subject and verb (except the one punch).
3. Check that at least half the lines start with or contain a connective (so / and / that's / whether it's / right?).
4. Check the facts are untouched: same numbers and claims, and no hedge before a number.

## Voice quality (emotion)
- **Kokoro `af_heart` is a flat local TTS, so it's a draft/fallback voice only.** Client-facing and posted VO uses an
  **expressive voice with delivery tags** (ElevenLabs v3 / Higgsfield `generate_audio`, e.g. `[warm, confident]`,
  `[slower, sincere]`, `[little smile]`). Those cost credits, so **ask Jason in the brief** (his custom voice only with his OK).
- If Kokoro is all that's available: write the prosody into the punctuation (commas for breaths, "right?" for lift,
  an ellipsis for a beat), render each line as its own take at speed 0.95–1.0, pick the best take per line, and say in
  the delivery message that it's the fallback voice.
