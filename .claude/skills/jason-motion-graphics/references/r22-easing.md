# r22: EASING. Ease in/out and overshoot (Jason, 2026-10-12: "we want to shoot for these animation styles always for these type of things")
**Source:** an easing cheat-sheet reel showing curves next to the motion each one makes.

## The rule: pick the curve by the job
| Job | Curve | Kit name (`kit.js`) |
|---|---|---|
| Something **enters** (card, word, icon arrives) | ease-out: fast start, soft landing | `K.out` / `K.expoOut` |
| Something **exits** | ease-in: soft start, fast leave | `K.in` / `backIn` (a small wind-up, then gone) |
| Something **moves** on screen (A → B, camera push) | ease-in-out | `K.inOut` |
| **Pop-ups, buttons, icons, badges, morph landings** | **overshoot:** it passes the target by about 10% and settles back **once** | `back` = bez(0.34,1.56,0.64,1); `backSoft` = bez(0.25,1.32,0.5,1) for big objects |
| Mechanical motion only (progress bar, clock hand, scrolling ticker) | linear | `t` |
| Elastic / bounce (several wobbles) | rarely: a playful, comedic hit at most once per piece | — |

- **Overshoot = one settle.** Never a wobble chain. Scale pops run 0 → 1.08 → 1, about 280–420 ms.
- **Nothing moves linearly** unless it's a machine.
- **Exits are shorter than entrances** (about 60%).

**This updates older rules:**
- iOS "critically-damped springs (no bounce)" and Coop "no-wobble springs" still hold for **camera moves, cards sliding and text lines**.
- **Pops, buttons, icons, badges and morph landings now get the single overshoot.**
