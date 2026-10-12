# Theta Identity

One video for the window when the mind is most open: falling asleep. It explains the method,
then runs five rounds of Wim Hof breathing with identity statements riding the breath and a
first-person memory scene playing in every hold. Then it slows the body down and lets you fall
asleep with the words still playing.

| File | What it is |
| --- | --- |
| `script.md` | Every word that gets spoken. Edit this, re-run, and the video rebuilds. |
| `build.py` | Generates the voice, breath, music, theta bed and frames, then renders. |
| `renders/theta-identity-v3-16x9.mp4` | Men's session (44 min, 1920x1080). |
| `script-women.md` | The women's script: own voice (`af_heart`), statements and scenes. |
| `renders/theta-identity-women-v1-16x9.mp4` | Women's session (43 min, 1920x1080). |
| `sounds.py` | Synthesized scene sounds: beds (house, gym, drive, beach, lot) and one-shots (door, engine, keys, plates, steps, phone, waves). |

## Running order

1. **Introduction (~7 min).** What theta is and why the door opens at sleep. Ego vs identity, with the
   family example. The observer that believes actions, not words. Why scenes are filed as memories.
   How the rounds work, why the music is there, and safety.
2. **Five rounds.** 30 breaths at ~3.3 s each, with 7–8 identity statements spoken on the out-breaths.
   Then a breath out and a hold, with the memory scene playing in the stillness. The hold
   stretches to fit the scene. Then a recovery breath held for 15 seconds, with one anchor line.
   | Round | Identity | Scene in the hold |
   | --- | --- | --- |
   | 1 | God as the only audience; saying no | Saying "not right now" to family, with no guilt |
   | 2 | Kind, not looking kind | Paying a stranger's bill in secret |
   | 3 | The long game: build now, carry them later | Handing my mother the paid-off house |
   | 4 | Calm, decisive, first mover | Holding the silence until they say yes |
   | 5 | Owner, wealth already done | My name on the building at sunrise |
3. **Bridge.** Slow breathing (4 in, 6 out) to switch the body off after the rounds.
4. **Descent.** The anchor lines loop three times, quieter and slower each pass, then the music fades.

## Timing

`audit()` runs before every render and fails the build if two voice lines overlap, if a
statement doesn't start on an out-breath, or if a statement lands within 3 s of the hold. In the
recovery, the inhale starts on the word "in", the 15-second count starts on "hold", and the exhale
lands on "Let go".

## Sound design

- **Breath.** Turbulent air shaped the way a throat and mouth shape it, with no tones. The inhale
  brightens as the lungs fill; the exhale is an open-mouth "haah" that pushes, then releases.
  Every breath varies a little, and the stereo is wide.
- **Music.** Composed in code and tuned to A = 432 Hz. Slow, open D-major pad chords
  (Dmaj9, Bm11, Gmaj7, Asus2) cross-fade every 24 s in a large reverb, with sparse soft piano
  notes from the pentatonic scale. Nothing repeats in a way you'd notice. It ducks under the voice.
- **Theta bed.** A binaural pair (216 Hz, half of 432, in the left ear; 216 + beat in the right)
  starts at 8 Hz in the intro, sits at 6 Hz through the rounds and slows to 4 Hz for sleep.
  It needs headphones. The evidence that binaural beats change brain waves is mixed, so treat it as a
  cue to slow down, not a switch. The breathing and the repetition do the heavy lifting.

## Visuals

There's no container. A soft field of warm light fills most of the screen on the inhale and shrinks
to an ember on the exhale, with drifting particles and a slowly flowing surface. It goes nearly dark
in the hold and dims away during the descent. The breath count, countdowns and statements sit on top.

## Protocol

- Lie down in bed, headphones in, phone on low brightness. Watch the intro and the breath count;
  close your eyes in the holds and once the bridge starts.
- Every night for 30 days. Keep the script stable for at least a week at a time.
- Upgrade: record `script.md` in **your own voice** and swap it in.

**Safety:** breathe lying down. Never in water, never driving or standing. Tingling and
light-headedness are normal. Stop if anything feels wrong. Talk to a doctor first if you're pregnant
or have epilepsy, heart problems or high blood pressure.

## Rebuild

```bash
pip install numpy pillow soundfile kokoro-onnx
# model files -> $KOKORO_MODELS (default /tmp/theta-identity/models): kokoro.onnx + voices.bin from
# https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0
python projects/theta-identity/build.py                    # full render
python projects/theta-identity/build.py --preview 420 520  # just 7:00-8:40, for a quick check
```

`THETA_VOICE` picks the Kokoro voice (default `am_michael`).
