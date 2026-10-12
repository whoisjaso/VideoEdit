# Design

Two layers. The **mechanics** come from a teardown of Duolingo (below): one task per screen, chunky
lip buttons, a feedback bar that turns green, a celebration when you finish, sounds and haptics.
The **look** is Kairos's own.

## The Kairos identity

**The angle.** *Kairos* is the Greek word for the right moment, as opposed to *chronos*, clock
time. An hour of footage is chronos. The 40 seconds worth posting are kairos. Everything in the
brand says that one thing: the hour, and the moment lifted out of it.

**The mark.** A ring (the hour of footage) with one slice lifted out (the clip you keep). Ink ring,
gold slice. It is `logo()` in `web/fx.js`, the favicon, and the first thing on the welcome screen.
The icon set in `web/icons/` (iOS, Android maskable, PWA, favicon, wordmarks) is rendered from one
SVG master by `tools/make_icons.mjs`; the landing page in `site/` is built on it too.
Kai, the mascot, is a clapperboard with a face in the same gold; Kai asks, the mark signs.

**The palette is the edit's palette.** The app wears the same colours the clips do, so what you see
in the app is what you get on screen:

| Token | Light | Dark | Job |
|---|---|---|---|
| `--gold` | `#ffc21a` | `#ffd24a` | The primary action, selection, scores. The keyword colour in the edits. |
| `--mint` | `#2be37a` | `#3df08a` | Done, success, uploads. The money/wins colour in the edits. |
| `--coral` | `#ff3b3b` | `#ff5c5c` | Errors. The problem colour in the edits. |
| `--ember` | `#ff7a1a` | `#ffa04a` | Streaks, words to check. |
| `--violet` | `#8b5cf6` | `#a78bfa` | Ideas and prompts. |
| `--ink` / `--paper` | `#14131a` / `#fffdf7` | `#f4f2ec` / `#0f0f16` | Text and background. Warm paper by day, ink by night. |

One accent per screen. Gold is for the thing you should press; mint only appears when something
is finished. Blue, the colour most apps use for "tap here", does not exist in Kairos.

**Type.** Outfit (OFL, bundled in `web/fonts/`): geometric, a little sharper than a rounded face,
weights 500 to 800. Buttons stay uppercase with tracking (a mechanic kept from the teardown).

**Voice.** Kairos talks like an editor, in short lines: *Clean take. Locked. Making the cut. Printing
your clips. That's a wrap.* Feedback trains "taste", not "XP". The welcome line is the brand in one
sentence: *Give me the hour, I'll find the moment.*

## The landing page

`site/index.html`, one theme (paper), one accent (gold), no eyebrows, no mock UI. The hero is a
real auto-edited clip playing in a phone with Kai beside it; the results row is three real clips
with their real durations and the editor's own scores; every screenshot is the app over real
footage. One CTA label everywhere: **Get Kairos**. Radius rule: controls 14px, media 20px, the
phone 44px. Motion is one entrance in the hero and one reveal per section; Kai blinks and nothing
else loops.

## The Duolingo teardown

Kairos's mechanics use Duolingo's design language. Duolingo makes hard, repetitive work (learning a
language) feel light, one small win at a time. Editing your own videos is the same kind of work.

## Method

This follows the [REA](https://github.com/morluto/rea) approach of evidence first, conclusions
second. Nothing below is guessed from screenshots. Every token was read from Duolingo's public web
app on 2026-10-11:

```
https://www.duolingo.com/                                   page shell
https://d35aaqx5ub95lt.cloudfront.net/css/app-*.css         brotli-compressed CSS (86 KB decompressed)
https://d35aaqx5ub95lt.cloudfront.net/js/app-*.js           palette table, component logic
```

## Evidence → Kairos

| Evidence (from their code) | What it means | In Kairos |
|---|---|---|
| Palette table in JS, `name: [light, dark]`: `owl #58cc02 / #93d333`, `tree-frog #58a700`, `macaw #1cb0f6 / #49c0f8`, `whale #1899d6`, `cardinal #ff4b4b`, `bee #ffc800`, `fox #ff9600`, `beetle #ce82ff`, `eel #4b4b4b`, `wolf #777`, `hare #afafaf`, `swan #e5e5e5`, `polar #f7f7f7`, `snow #fff / #131f24` | Color tokens are named after animals, with a paired dark-mode value | `web/app.css` `:root` uses the same names and values, light and dark |
| CSS usage counts: `snow` 147, `macaw` 64, `swan` 67, `hare` 40, `eel` 32, `owl` 32 | Mostly white space and grey lines. Blue marks selection, green marks progress and success | Blue = selected, green = continue/success, gold = scores and XP |
| `transform: translateY(var(--__internal__lip-width))` on `:active`, with the `::before` box-shadow removed | Buttons sit on a solid "lip" and physically drop onto it when pressed | `.btn`: `box-shadow: 0 4px 0 <darker>`; `:active` moves down 4px and drops the shadow |
| `border-width: 2px 2px 4px` | Cards have a thick bottom edge | `.choice`, `.clip`, `.tile`, `.chip`, `.score button` |
| `border-radius: 12px` ×13, `16px` ×11 | Friendly rounded corners | `--r: 16px`, small controls 12px |
| `letter-spacing: var(--web-ui_button-letter-spacing, 0.04em)`, `text-transform: uppercase` | Button labels are spaced capitals | `.btn` uppercase, 0.06em |
| `font-family: feather` (proprietary) | A rounded, heavy typeface | Not copied. Kairos uses **Outfit** (open licence), see the identity section |
| The lesson shell: an X, a top progress bar, the question, the answer, a bottom CHECK/CONTINUE bar that turns green with praise | One task per screen, instant feedback, constant sense of progress | The three-step new-clips flow: progress bar, one question, the bottom bar turns mint ("Clean take.") on every answer |
| Lesson complete: character + stat cards (XP, time, accuracy) | Celebrate finishing | "That's a wrap." with Clips / Minutes / Top score cards, confetti and a chime |
| The skill path: round 3D nodes with a pulsing current node | Long processes shown as a journey | The processing screen: Reading → Listening → Finding moments → Cutting → Rendering |
| Streaks and XP | Habit loop | A streak (days in a row you scored edits) and Taste points. They reward the feedback that trains the editor |
| Number keys pick answers, Enter continues | Keyboard speed on the web | Same in every Kairos question |

## Feel: sound and haptics

- **Sounds** are synthesized in `web/fx.js` with Web Audio: a soft tap, a select pluck, a two-note
  "that's right", an error buzz and a rising celebration arpeggio. No audio files are copied.
- **Haptics:** `navigator.vibrate` patterns on Android and Chrome. iOS Safari has no vibrate API. On
  iOS 18 and later, toggling a hidden `<input type="checkbox" switch>` fires the system haptic, and
  Kairos uses that.
- Both can be turned off in Settings. Reduced-motion users get no animation.

## What we did not copy

- **Duo the owl.** Kairos has its own mascot, **Kai**, and its own mark.
- **The Feather typeface.** It's proprietary, so Kairos uses Outfit.
- **The green-and-blue palette.** Kairos uses its own: the colours from the edits themselves.
- **Sound files and illustrations.** All of Kairos's are original.

Colors and layout patterns are design conventions, so we use them. Trademarks, characters, fonts and
recorded assets are Duolingo's, so we don't.
