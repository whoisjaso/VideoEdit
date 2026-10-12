---
name: voiceover-pronunciation
description: Pronunciation gate for every generated voice-over (Kokoro, ElevenLabs, Higgsfield, any TTS). Use BEFORE rendering anything Jason will hear: Theta Identity sessions, affirmations, ad reads, narrated shorts, film voice-overs. Catches words spelled one way and said two ways ("Identity lives" said as the plural of life, "Close your eyes" said as nearby), plus names and brands, and fixes them at the phoneme level so the captions keep normal spelling. Also use when Jason says a word "sounded wrong", "she said it weird", or names a mispronunciation.
---

# Voice-over pronunciation gate

> **Why this exists.** In the Theta Identity women's session, the voice said "Identity *lives* for what
> it builds" with the long I of "life" instead of the short I of "gives". Jason heard it while falling
> asleep and it broke the whole state. A wrong vowel in a hypnotic or emotional read is not a nit: it
> pulls the listener out. **No voice-over ships until this gate passes.**

## The rule

Before any TTS render:

1. **Run the checker** on every script that will be spoken:
   ```bash
   python .claude/skills/voiceover-pronunciation/scripts/check_pronunciation.py SCRIPT.md
   # with a build that already has fixes (shows what will actually be said):
   python .claude/skills/voiceover-pronunciation/scripts/check_pronunciation.py --build path/to/build.py SCRIPT.md
   ```
   - `WRONG` means a known heteronym is said the wrong way in this context. It must be fixed, and the
     script exits with code 1.
   - `CHECK` means a heteronym whose context the checker can't read. Read the phonemes yourself.
   - `NAME` means a name or brand. Read the phonemes yourself (American by default).
2. **Fix every WRONG**, and anything off in CHECK or NAME, with a phoneme override. Don't misspell the
   text: captions are built from the same text.
3. **Re-run until it's clean**, then render.
4. When Jason reports a word, add it to the checker's `HETERONYMS` table (or the build's `PRONOUNCE`
   table) so it can never come back, and log it in the table below.

## How to fix it, per engine

| Engine | Fix |
| --- | --- |
| **Kokoro** (Theta Identity) | Phonemize the line, swap the wrong phoneme, synthesize with `is_phonemes=True`. See `PRONOUNCE` and `phonemes()` in `projects/theta-identity/build.py`: each entry is `(pattern in the sentence, wrong phonemes, right phonemes)`. |
| **ElevenLabs** | Use a pronunciation dictionary or an SSML `<phoneme alphabet="ipa" ph="lɪvz">lives</phoneme>` tag (on models that support it). Otherwise reword. |
| **Any engine without phoneme control** | Reword so the word can only be read one way: "Ego *is all about* how it looks"; "Shut your eyes". Never respell it ("livs") if the text is also shown on screen. |

## Fixes already made (keep this log)

| Word / line | Engine said | Correct | Fix |
| --- | --- | --- | --- |
| "Ego **lives** for…", "Identity **lives** for…" | lˈaɪvz (plural of life) | lˈɪvz (verb, rhymes with gives) | `PRONOUNCE` in theta-identity build |
| "**Close** your eyes" | klˈoʊs (near) | klˈoʊz (shut) | `PRONOUNCE` |
| "Mercedes" | mɜːsˈeɪdiːz (British r-less) | mɚsˈeɪdiːz (American) | `PRONOUNCE` |

Checked and correct in Kokoro (en-us): "the rest of their lives" (lˈaɪvz), "does", "closes",
"the wind", "Wim Hof", "Range Rover", "four thirty two hertz", "three, two, one".

## Words that need a look every time

lives/live, close, read, lead, tear, wind, wound, bow, use, present, record, minute, content,
desert, object, produce, refuse, separate, perfect, excuse, row, bass. Also every name, brand,
car model, city and number written as digits. Write numbers out as words, the way they should be
said ("four thirty two hertz", not "432Hz").

## Also listen for

- **Merged words.** "does not" becomes "doesn't". Fine for a casual read, but wrong when the stress
  matters ("it **does not** believe words"). Fix it with a comma or by rewording.
- **Long sentences.** These flatten the read. Split narration into short sentences (the Theta build
  synthesizes one sentence at a time).
- **The same word in the women's and men's versions.** Each version has its own voice, and both use
  the same phonemizer, so a fix applies to both. Run the checker on both scripts.
