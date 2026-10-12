# r29: KENYSET TEXT. A kinetic-caption preset pack, rebuilt in our engine (Jason, 2026-10-12: shared the "Kenyset preset pack" Drive folder)
**Label:** `KENYSET TEXT #NN`. Ask for it like "captions in KENYSET #21".

**Source:** 42 After Effects text-animator presets (`.ffx`) by @kenyset.
- Decoded with `ffx.py`, a RIFX walker: it reads match names, static values, keyframe headers and expressions.
- The original `.ffx` files are **not** stored in the repo (they're the creator's pack); only our re-implementation is.
- Audition reel: `renders/kenyset-text-presets-reel-v1.mp4`.

## How every preset works
1. **A from-state.** Each unit starts here and travels to rest. The pack's values:
   - opacity 0;
   - blur 10–59;
   - offsets: x ±94–122 (slide), y −111…+71 (drop/rise);
   - scale 0 / 50 / 78–80 / 150% / a stretch-flip (−36 × 291%);
   - rotation −62…+54°;
   - tracking ±37–100.
2. **Unit:** per **char / word / line**, staggered across the text.
   - In AE this is a Range Selector: shape Ramp Up, smoothness 100, Offset keyed −100 → 100.
   - Ease High 50 = smooth; −100 = snap start; Ease Low 100 = long soft landing.
3. **Spring (presets #01–#31).** An expression selector gives each unit an elastic settle:
   - `amount = 1.5·cos(2π·2.5·τ)·e^(−7·τ)`, with a 0.08 s delay per unit (#16 is only that delay slider);
   - the shape: a 0.1 s snap, one clear ~37% overshoot, then a ~9% echo;
   - this is the pack's signature; it fits r22 overshoot for pops.
4. **Typewriters (#38–#42).** A square shape with Start keyed.
   - #39 / #40: plain reveal by character or by word.
   - #38 / #41 / #42: tracking collapse or expand as the letters arrive.

## Families (numbers = preset IDs)
- **Stretch-flip pop, by line/word/char:** #01–#03.
- **Slide from left + blur:** #04–#06.
- **Slide from right:** #07–#10.
- **Drop from above with spin:** #11, #12, #17.
- **Fall/shrink from above:** #13–#15, #18, #19.
- **Rise and spin from below:** #20, #21.
- **Scale pops:** #22–#24, #28, #29.
- **Rise + blur, by char/word/line:** #25–#27, #30–#34.
- **Blur-zoom from 150%:** #35–#37.
- **Typewriters / tracking:** #38–#42.

## Use (engine)
`kit/textfx.js` + `kit/kenyset-presets.json`:

```js
const T = TextFX.make(el, "Build the self\nno one claps for.", PRESETS[n], {size: 96});
// then every frame:
T.seek(t - t0);
```

`T.length` gives the full in-time.

Pair with the SFX rule: a pop or whoosh on the first unit, and a soft tick per word for the typewriters.
