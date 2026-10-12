# r26: THE VOICE CHAIN. Done to Jason's voice every time (Jason, 2026-10-12: "what we need to do EVERYTIME to our voice to make it sound legible, clear and powerful")
**Source:** a 100 s reel (Patch app). The same mic is heard with nothing on it, then with the six processors radio stations put on microphones.

## The six stages, always in this order
| # | Stage | What it does | Our setting (`voice_enhance.py`) |
|---|---|---|---|
| 1 | **High-pass filter** | Cuts everything below ~100 Hz. Almost none of the voice lives there, only room rumble. | `highpass=f=100` |
| 2 | **Downward expander** | Turns the gaps quieter (fan, keyboard, breaths) when the voice drops. | `agate` ratio 2:1, at most −12 dB. **Gentle on purpose:** the ep #4 denoise erased his soft opening. |
| 3 | **De-esser** | Tames sharp "s" hiss. | `deesser` |
| 4 | **EQ** | Boost around **3.5 kHz**, the range that makes words clear. We also cut 2 dB of mud at 250 Hz and add light air at 9 kHz. | +4 dB @ 3.5 kHz |
| 5 | **Compressor** | Shrinks the gap between quiet and loud words. Steady volume; the voice sits at the **front of the mix**, closest and clearest. | 3.5:1 @ −22 dB, 8 ms attack / 120 ms release |
| 6 | **Limiter** | A ceiling: laughs and shouts can't distort. | −14 LUFS, true peak ≤ −1.5 dB |

Before the chain: DeepFilterNet3 denoise (capped at 15 dB). After: `check_voice.py` (the audio gate).

**Applies to every voice we ship:** Jason's talking heads, his voice-overs, and the Kokoro narration (TTS needs stages 3–6; skip the denoise). Music and SFX always sit *behind* the voice (duck ≥ 8 dB under speech).
