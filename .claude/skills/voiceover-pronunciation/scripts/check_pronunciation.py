"""Pronunciation gate for generated voice-overs.

    python .claude/skills/voiceover-pronunciation/scripts/check_pronunciation.py SCRIPT [SCRIPT ...]
    python .../check_pronunciation.py --build projects/theta-identity/build.py SCRIPT ...

With --build, the phonemes come from that module's phonemes(text), so its PRONOUNCE fixes count
and the check shows what will actually be said.

It reads plain text or a Theta-style script (lines starting with "> " or "~ "). Each sentence goes
through the same phonemizer Kokoro uses, and the script prints:

  WRONG   a known heteronym said the wrong way in this context (exit code 1)
  CHECK   a heteronym whose reading depends on context; confirm the phonemes by eye
  NAME    a capitalised word mid-sentence (names, brands); confirm the phonemes by eye

Every WRONG needs a PRONOUNCE entry in the build script, or a rewording, before you render.
"""
import re
import sys
from pathlib import Path

# word -> list of (context regex, phoneme the context needs, what it means)
HETERONYMS = {
    "lives": [(r"\b(\w+) lives (for|in|with|by|on|to|at|like|inside|through)\b", "lˈɪvz", "verb: rhymes with gives"),
              (r"\b(their|our|your|my|his|her|whose|many|two|three|saved|changed) lives\b", "lˈaɪvz", "noun: plural of life")],
    "live": [(r"\b(to|I|we|you|they|can|will|must|should|would|never) live\b", "lˈɪv", "verb"),
             (r"\b(a|the|go|went|is|was|are|were) live\b", "lˈaɪv", "adjective: live show")],
    "close": [(r"\b[Cc]lose (your|my|the|his|her|their|it|them|up|down|out)\b", "klˈoʊz", "verb: shut"),
              (r"\b(so|too|very|is|was|am|are|be|get|got|come|came) close\b", "klˈoʊs", "adjective: near")],
    "read": [(r"\b(I|we|you|they|to|will|can|must|should) read\b", "ɹˈiːd", "present tense"),
             (r"\b(had|have|has|was|were|been|already) read\b", "ɹˈɛd", "past participle")],
    "lead": [(r"\b(to|will|I|we|you|they|can|must) lead\b", "lˈiːd", "verb: guide"),
             (r"\b(of|like|heavy as) lead\b", "lˈɛd", "metal")],
    "tear": [(r"\b(a|one|single|the) tear\b", "tˈɪɹ", "noun: crying"),
             (r"\b(to|will|I|we|you|they|can) tear\b", "tˈɛɹ", "verb: rip")],
    "wind": [(r"\b(the|a|cold|warm|in the) wind\b", "wˈɪnd", "noun: air"),
             (r"\b(to|I|we|you|they|will|can|must) wind\b", "wˈaɪnd", "verb: turn")],
    "wound": [(r"\b(a|the|old|deep|open) wound\b", "wˈuːnd", "noun: injury"),
              (r"\b(was|were|is|got|had|have|has) wound\b", "wˈaʊnd", "past of wind")],
    "bow": [(r"\b(to|I|we|you|they|will|can|must) bow\b", "bˈaʊ", "verb: bend"),
            (r"\b(a|the|with a) bow\b", "bˈoʊ", "noun: ribbon or weapon")],
    "use": [(r"\b(the|a|no|any|good|its) use\b", "jˈuːs", "noun"),
            (r"\b(to|I|we|you|they|will|can|must) use\b", "jˈuːz", "verb")],
    "present": [(r"\b(the|this|a) present\b", "pɹˈɛzənt", "noun or adjective"),
                (r"\b(to|will|I|we|they|can) present\b", "pɹᵻzˈɛnt", "verb")],
    "record": [(r"\b(a|the|my|world|new) record\b", "ɹˈɛkɚd", "noun"),
               (r"\b(to|I|we|you|they|will|can) record\b", "ɹᵻkˈɔːɹd", "verb")],
    "minute": [(r"\b(a|one|the|each|every|last|first) minute\b", "mˈɪnɪt", "noun: 60 seconds")],
    "content": [(r"\b(I am|I'm|feel|be|is|am) content\b", "kəntˈɛnt", "adjective: satisfied")],
    "does": [(r"\b(it|he|she|that|this|what|who) does\b", "dˈʌz", "verb")],
    "desert": [(r"\b(the|a) desert\b", "dˈɛzɚt", "noun: sand")],
    "object": [(r"\b(to|I|we|they) object\b", "əbdʒˈɛkt", "verb")],
    "produce": [(r"\b(to|I|we|they|will|can) produce\b", "pɹədˈuːs", "verb")],
    "refuse": [(r"\b(to|I|we|they|will) refuse\b", "ɹᵻfjˈuːz", "verb")],
    "separate": [(r"\b(to|I|we|they|will) separate\b", "sˈɛpɚɹeɪt", "verb")],
    "perfect": [(r"\b(to|I|we|they|will) perfect\b", "pɚfˈɛkt", "verb")],
    "excuse": [(r"\b(an|no|the|any) excuse\b", "ɛkskjˈuːs", "noun")],
    "row": [(r"\b(a|in a|in|the) row\b", "ɹˈoʊ", "noun: line")],
    "bass": [(r"\b(the|deep|heavy) bass\b", "bˈeɪs", "noun: low sound")],
}


def sentences(path):
    out = []
    lines = [raw.strip() for raw in Path(path).read_text().splitlines()]
    spoken_only = any(line.startswith(("> ", "~ ")) for line in lines)   # a Theta-style script
    for line in lines:
        if line.startswith(("> ", "~ ")):
            line = line[2:]
        elif spoken_only or line.startswith(("#", "[", "|", "`", "-")) or not line:
            continue
        out += [s.strip() for s in re.split(r'(?<=[.!?])\s+(?=[A-Z"])', line) if s.strip()]
    return out


def main(args):
    from kokoro_onnx.tokenizer import Tokenizer
    tok = Tokenizer()
    say = lambda s: tok.phonemize(s, "en-us")  # noqa: E731
    paths = list(args)
    if paths[:1] == ["--build"]:
        import importlib.util
        build_path = Path(paths[1]).resolve()
        sys.path.insert(0, str(build_path.parent))
        spec = importlib.util.spec_from_file_location("voice_build", build_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        say = mod.phonemes
        paths = paths[2:]
    wrong = 0
    seen = set()
    for path in paths:
        for s in sentences(path):
            if s in seen:
                continue
            seen.add(s)
            ph = None
            for word, rules in HETERONYMS.items():
                if not re.search(rf"\b{word}\b", s, re.I):
                    continue
                ph = ph or say(s)
                matched = False
                for ctx, need, meaning in rules:
                    if re.search(ctx, s):
                        matched = True
                        if need.replace("ˈ", "").replace("ˌ", "") not in ph.replace("ˈ", "").replace("ˌ", ""):
                            wrong += 1
                            print(f"WRONG  [{word}: {meaning}, needs /{need}/]  {s}\n       engine: {ph}")
                if not matched:
                    print(f"CHECK  [{word}]  {s}\n       engine: {ph}")
            for name in re.findall(r"(?<=[a-z,] )([A-Z][a-zA-Z]+)", s):
                if name not in ("I", "God"):
                    print(f"NAME   [{name}]  {s}\n       engine: {say(s)}")
    print(f"\n{wrong} wrong pronunciation(s)." if wrong else "\nNo known mispronunciations.")
    return 1 if wrong else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
