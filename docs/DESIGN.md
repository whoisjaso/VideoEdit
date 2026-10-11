# Design: the Duolingo teardown

Kairos's front end uses Duolingo's design language. Duolingo makes hard, repetitive work (learning a
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
| `font-family: feather` (proprietary) | A rounded, heavy typeface | **Nunito** 600–900 (open licence), bundled in `web/fonts/` |
| The lesson shell: an X, a top progress bar, the question, the answer, a bottom CHECK/CONTINUE bar that turns green with praise | One task per screen, instant feedback, constant sense of progress | The new-clips Q&A: progress bar, Kai asks in a speech bubble, the bottom bar turns green ("Love it!") on every answer |
| Lesson complete: character + stat cards (XP, time, accuracy) | Celebrate finishing | "Your clips are ready!" with Clips / Minutes read / Top score cards, confetti and a chime |
| The skill path: round 3D nodes with a pulsing current node | Long processes shown as a journey | The processing screen: Reading → Listening → Finding moments → Cutting → Rendering |
| Streaks and XP | Habit loop | Training streak (days in a row you scored edits) and Style XP. They reward the feedback that trains your style |
| Number keys pick answers, Enter continues | Keyboard speed on the web | Same in every Kairos question |

## Feel: sound and haptics

- **Sounds** are synthesized in `web/fx.js` with Web Audio: a soft tap, a select pluck, a two-note
  "that's right", an error buzz and a rising celebration arpeggio. No audio files are copied.
- **Haptics:** `navigator.vibrate` patterns on Android and Chrome. iOS Safari has no vibrate API. On
  iOS 18 and later, toggling a hidden `<input type="checkbox" switch>` fires the system haptic, and
  Kairos uses that.
- Both can be turned off in Settings. Reduced-motion users get no animation.

## What we did not copy

- **Duo the owl.** Kairos has its own mascot: **Kai**, a clapperboard with a face (`kai()` in `fx.js`).
- **The Feather typeface.** It's proprietary, so Kairos uses Nunito.
- **Sound files and illustrations.** All of Kairos's are original.

Colors and layout patterns are design conventions, so we use them. Trademarks, characters, fonts and
recorded assets are Duolingo's, so we don't.
