"""Word-level transcription, best engine available: faster-whisper > Vosk > none.

Output format (same as the skill's words.json): [{"word", "start", "end", "conf"}].
A one-hour video is ~9k words; the engine streams the audio so memory stays flat.
"""
from __future__ import annotations

import json
import os
import wave
from pathlib import Path

VOSK_MODEL = Path(os.path.expanduser("~/.vosk-model"))


def available() -> list[str]:
    out = []
    try:
        import faster_whisper  # noqa: F401
        out.append("whisper")
    except ImportError:
        pass
    try:
        import vosk  # noqa: F401
        if VOSK_MODEL.exists():
            out.append("vosk")
    except ImportError:
        pass
    return out


def transcribe(wav16k: str | Path, engine: str = "auto", progress=None) -> list[dict]:
    engines = available()
    if engine == "auto":
        engine = engines[0] if engines else "none"
    if engine == "whisper" and "whisper" in engines:
        return _whisper(wav16k, progress)
    if engine == "vosk" and "vosk" in engines:
        return _vosk(wav16k, progress)
    return []


def _whisper(path, progress) -> list[dict]:
    from faster_whisper import WhisperModel
    model = WhisperModel(os.environ.get("KAIROS_WHISPER", "small.en"), compute_type="int8")
    segments, info = model.transcribe(str(path), word_timestamps=True, vad_filter=True)
    words = []
    for seg in segments:
        for w in seg.words or []:
            words.append({"word": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3),
                          "conf": round(w.probability, 3)})
        if progress and info.duration:
            progress(min(1.0, seg.end / info.duration))
    return words


def _vosk(path, progress) -> list[dict]:
    import sys
    stub = Path("/tmp/stub")                       # vosk imports `srt`, which we never use
    stub.mkdir(exist_ok=True)
    (stub / "srt.py").touch()
    sys.path.append(str(stub))
    from vosk import KaldiRecognizer, Model, SetLogLevel
    SetLogLevel(-1)
    wf = wave.open(str(path), "rb")
    total = wf.getnframes() or 1
    rec = KaldiRecognizer(Model(str(VOSK_MODEL)), wf.getframerate())
    rec.SetWords(True)
    words, read = [], 0
    while True:
        data = wf.readframes(8000)
        if not data:
            break
        read += 8000
        if rec.AcceptWaveform(data):
            words += json.loads(rec.Result()).get("result", [])
        if progress and read % 160000 == 0:
            progress(min(1.0, read / total))
    words += json.loads(rec.FinalResult()).get("result", [])
    return [{"word": w["word"], "start": w["start"], "end": w["end"], "conf": w.get("conf", 1.0)} for w in words]


def sentences(words: list[dict], gap: float = 0.6, max_words: int = 40) -> list[dict]:
    """Group words into sentence-ish units by pauses (recognizers give no punctuation)."""
    out, cur = [], []
    for w in words:
        if cur and (w["start"] - cur[-1]["end"] > gap or len(cur) >= max_words or cur[-1]["word"].endswith((".", "?", "!"))):
            out.append(cur)
            cur = []
        cur.append(w)
    if cur:
        out.append(cur)
    return [{"i": i, "start": s[0]["start"], "end": s[-1]["end"], "text": " ".join(x["word"] for x in s),
             "conf": round(sum(x.get("conf", 1) for x in s) / len(s), 3)} for i, s in enumerate(out)]
