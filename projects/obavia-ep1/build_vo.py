"""VO + single source of truth for Obavia Ep1.

    python projects/obavia-ep1/build_vo.py   # -> public/vo/*.wav, src/data/timeline.json, src/data/cues.json

Every time in the film (visual or audio) comes from these two files.
"""
import difflib
import hashlib
import json
import re
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "theta-identity"))
import build  # noqa: E402  (phonemes with the PRONOUNCE fixes, resample)

SR = 48000
FPS = 30
CACHE = Path("/tmp/obavia-ep1")
MODELS = Path("/tmp/theta-identity/models")
VOICES = {"N": ("am_michael", 1.13), "O": ("am_onyx", 0.98)}   # narrator: low, warm; officer: deeper, flat

# (shot, speaker, text). Clips in one shot follow each other with 300-450 ms gaps.
SCRIPT = [
    ("hook", "N", "You just got pulled over. Red and blue in the mirror."),
    ("hook", "N", "And before either of you says a word... you've already judged each other."),
    ("title", "N", "Because a traffic stop is two scared people. One window between you."),
    ("p1", "N", "Problem one. He's scared too."),
    ("hispov", "N", "From his seat, he's reading your car. Paper tags. Loud music. Tank top."),
    ("hispov", "N", "Every movie he's seen fills in the rest."),
    ("danger", "N", "His training says any stop could turn deadly."),
    ("danger", "N", "One big Florida study put it at about one in six and a half million stops."),
    ("danger", "N", "But fear doesn't read data."),
    ("p2", "N", "Problem two. You're labeling him back. Power trip. Quota. The badge."),
    ("bias", "N", "Here's what you don't know. In a famous study, split-second threat decisions followed cultural stereotypes."),
    ("bias", "N", "Even in people with no personal prejudice."),
    ("slice", "N", "A face gets judged in a tenth of a second. What he sees lands before what you say."),
    ("rule", "N", "Rule one. Disarm the fear before you speak."),
    ("disarm", "N", "Hazards on. Dome light on. Window down. Hands on the wheel."),
    ("disarm", "N", "Driver handbooks say it plainly. Let him see you."),
    ("approach", "N", "Footsteps. Flashlight. He sees your hands, and his shoulders drop."),
    ("ask", "O", "Do you know why I stopped you?"),
    ("admit", "N", "That question invites an admission."),
    ("admit", "N", "If you honestly don't know, say, no officer, could you tell me?"),
    ("admit", "N", "If you do know, don't lie. Keep it short and honest."),
    ("reg", "O", "Your registration expired last month."),
    ("clip", "N", "He goes quiet. Clipboard. Five seconds left."),
    ("choice", "N", "One sentence. Do you explain why it lapsed... or just apologize?"),
    ("black", "N", "One drops his guard. The other raises it."),
    ("end", "N", "Comment explain or apologize. Part two follows what you pick."),
]
PRE_REVEAL = {"title": 0.3, "rule": 0.3, "admit": 0.4, "choice": 0.3, "black": 0.5, "end": 0.4}   # silence on the outgoing shot
GAP_CLIP = 0.28
GAP_SHOT = 0.2
LEAD_IN = 0.12
TAIL_END = 3.4   # end card hold after the last word

_k = None


def tts(text, speaker):
    global _k
    voice, speed = VOICES[speaker]
    ph = build.phonemes(text)
    key = hashlib.sha1(f"{voice}|{speed}|{ph}".encode()).hexdigest()[:16]
    p = CACHE / "tts" / f"{key}.wav"
    if not p.exists():
        if _k is None:
            from kokoro_onnx import Kokoro
            _k = Kokoro(str(MODELS / "kokoro.onnx"), str(MODELS / "voices.bin"))
        s, sr = _k.create(ph, voice=voice, speed=speed, lang="en-us", is_phonemes=True)
        p.parent.mkdir(parents=True, exist_ok=True)
        sf.write(p, s, sr)
    x, sr = sf.read(p, dtype="float32")
    x = build.resample(x, sr, SR)
    idx = np.flatnonzero(np.abs(x) > 0.01)
    x = x[max(0, idx[0] - 240): idx[-1] + 1200]
    return x / (np.max(np.abs(x)) + 1e-9) * 0.89


def norm(w):
    return re.sub(r"[^a-z0-9']", "", w.lower().replace("’", "'"))


_wm = None


def word_times(path, text):
    """Whisper word timestamps mapped onto the script's own words (script spelling wins)."""
    global _wm
    if _wm is None:
        from faster_whisper import WhisperModel
        _wm = WhisperModel("small.en", device="cpu", compute_type="int8")
    a16 = build.resample(sf.read(path, dtype="float32")[0], SR, 16000)
    segs, _ = _wm.transcribe(a16, word_timestamps=True, initial_prompt=text, language="en")
    hw = [(w.word.strip(), w.start, w.end) for s in segs for w in s.words]
    sw = text.replace("...", " ").split()
    a = [norm(w) for w in sw]
    b = [norm(w[0]) for w in hw]
    out = [None] * len(sw)
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag == "equal" or (tag == "replace" and i2 - i1 == j2 - j1):
            for k in range(i2 - i1):
                out[i1 + k] = (hw[j1 + k][1], hw[j1 + k][2])
        elif tag == "replace":
            t0, t1 = hw[j1][1], hw[j2 - 1][2]
            for k in range(i2 - i1):
                out[i1 + k] = (t0 + (t1 - t0) * k / (i2 - i1), t0 + (t1 - t0) * (k + 1) / (i2 - i1))
    # fill gaps by interpolation
    for i in range(len(out)):
        if out[i] is None:
            prev = next((out[j][1] for j in range(i - 1, -1, -1) if out[j]), 0.0)
            nxt = next((out[j][0] for j in range(i + 1, len(out)) if out[j]), prev + 0.3)
            out[i] = (prev, max(prev + 0.08, nxt - 0.02))
    return [dict(w=w, s=round(s, 3), e=round(e, 3)) for w, (s, e) in zip(sw, out)]


def rms_frames(x):
    hop = SR // FPS
    n = len(x) // hop + 1
    r = np.array([np.sqrt(np.mean(x[i * hop:(i + 1) * hop] ** 2) + 1e-12) for i in range(n)])
    return [round(float(v), 3) for v in np.clip(r / (r.max() + 1e-9), 0, 1)]


def main():
    vo_dir = HERE / "public" / "vo"
    vo_dir.mkdir(parents=True, exist_ok=True)
    data = HERE / "src" / "data"
    data.mkdir(parents=True, exist_ok=True)
    t = LEAD_IN
    shots, clips, words = [], [], []
    order = []
    for sh, _, _ in SCRIPT:
        if sh not in order:
            order.append(sh)
    for si, sh in enumerate(order):
        start = 0.0 if si == 0 else t
        if si:
            t += 0.1
        for ci, (s2, spk, text) in enumerate([c for c in SCRIPT if c[0] == sh]):
            x = tts(text, spk)
            name = f"{sh}-{ci}.wav"
            sf.write(vo_dir / name, x, SR, subtype="PCM_16")
            wt = word_times(vo_dir / name, text)
            clip = dict(id=f"{sh}-{ci}", shot=sh, speaker=spk, text=text, file=f"vo/{name}", start=round(t, 3),
                        dur=round(len(x) / SR, 3))
            if spk == "O":
                clip["rms"] = rms_frames(x)
            clips.append(clip)
            for wi, w in enumerate(wt):
                words.append(dict(clip=clip["id"], shot=sh, speaker=spk, i=wi, w=w["w"],
                                  s=round(t + w["s"], 3), e=round(t + w["e"], 3)))
            t += len(x) / SR + GAP_CLIP
        t -= GAP_CLIP
        nxt = order[si + 1] if si + 1 < len(order) else None
        t += (PRE_REVEAL.get(nxt, 0.0) + GAP_SHOT) if nxt else TAIL_END
        shots.append(dict(id=sh, start=round(start, 3), end=round(t, 3)))
    total = round(t, 3)
    tl = dict(fps=FPS, sr=SR, duration=total, frames=int(np.ceil(total * FPS)), shots=shots, clips=clips, words=words)
    (data / "timeline.json").write_text(json.dumps(tl, indent=1))
    print(f"total {total:.2f}s  ({len(words)} words, {sum(len(c[2].split()) for c in SCRIPT) / total * 60:.0f} wpm)")
    for s in shots:
        print(f"  {s['id']:8s} {s['start']:6.2f} - {s['end']:6.2f}")


if __name__ == "__main__":
    main()
