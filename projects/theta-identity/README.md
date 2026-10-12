# Theta Identity

A self-programming session for the two windows when the mind is most open: falling asleep
(hypnagogic) and waking up (hypnopompic). It pairs Wim Hof breathing with first-person identity
statements and memory-style scenes, all in my own words.

| File | What it is |
| --- | --- |
| `script.md` | Every word that gets spoken. Edit this, re-run, and the video rebuilds. |
| `build.py` | Generates the voice, breath pacing, bells, drone, binaural bed and frames, then renders. |
| `renders/theta-identity-night-v1.mp4` | Night: 4 Wim Hof rounds, slow-breath bridge, identity, scenes, fade to sleep (~40 min). |
| `renders/theta-identity-morning-v1.mp4` | Morning: identity and two scenes on waking, then 3 Wim Hof rounds, then get up. |

## Why it's built this way

- **Wim Hof first, then a bridge.** Wim Hof breathing switches the body on (adrenaline, alkaline
  blood). That's perfect in the morning and the wrong state for sleep. So the night version follows the
  rounds with a slow countdown and long out-breaths to tip the nervous system into rest before a single
  identity line plays. In the morning, the breathing comes last, so it launches me out of bed.
- **Identity, not ego.** Every line is about what I do when nobody is watching. The Observer believes
  actions, not words. Ego is an identity rented from other people's eyes.
- **Scenes are filed as memories.** Each opens with "I remember this," plays in first person in the
  present tense with sensory detail (cold air, hot coffee, a dry handshake), and closes with "That
  happened. I was there." Vivid, sensory, first-person, emotional, repeated: those are what make the
  brain treat an imagined event like a lived one.
- **Silence after every statement.** 7 seconds at night (5 in the morning) so I can say it back
  in my head and see it. The repetition I do myself is what installs it.
- **Theta bed.** A binaural beat (150 Hz carrier) slides from 10 Hz down to 3.5 Hz across the night
  session. It only works with headphones. Treat it as atmosphere: the evidence that it drives brain
  waves is thin. The breathing and the repetition do the real work.
- **Dim, warm screen.** Amber on near-black so the screen doesn't fight sleep.

## Protocol

1. Night: lie in bed with headphones in, phone on low brightness. Watch the screen for the breathing
   rounds, then close your eyes when the bridge starts. Let yourself fall asleep anywhere after that.
2. Morning: start it before you sit up. Eyes closed for the identity part, eyes open for the rounds.
3. Every night for 30 days. Change the script as the identity grows, but keep it stable for at least
   a week at a time. Repetition beats novelty.
4. Upgrade: record `script.md` in **your own voice** and swap it in. Your own voice saying "I" is
   the strongest version of this.

**Safety:** do the breathing lying down. Never in water, never driving or standing. Tingling and
light-headedness are normal. Stop if anything feels wrong. Talk to a doctor first if you're pregnant
or have epilepsy, heart problems or high blood pressure.

## Rebuild

```bash
pip install numpy pillow soundfile kokoro-onnx
# model files -> $KOKORO_MODELS (default /tmp/theta-identity/models): kokoro.onnx + voices.bin from
# https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0
python projects/theta-identity/build.py night
python projects/theta-identity/build.py morning
```

`THETA_VOICE` picks the Kokoro voice (default `am_michael`).
