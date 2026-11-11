"""One clock for picture, sound and captions. Everything is keyed to the narration's
word times (timeline.json), so a new read (Jason's) re-times the whole film."""
import json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OFF = 4.8                       # the silent type hook runs before the first spoken word
EXTRA = {"two3": 0.9}           # extra silence after a line (room for the "a traffic stop" card)
FPS = 60

class TL:
    def __init__(self, path=None):
        d = json.load(open(path or f"{ROOT}/timeline.json")); self.meta = d
        self.lines = []; self.by = {}; shift = OFF; self.cuts = []   # cuts: (narration_time, extra) for the audio
        for l in d["lines"]:
            q = dict(id=l["id"], text=l["text"], s=l["s"] + shift, e=l["e"] + shift,
                     words=[dict(w=w["w"], s=w["s"] + shift, e=w["e"] + shift) for w in l["words"]])
            self.lines.append(q); self.by[l["id"]] = q
            if l["id"] in EXTRA:
                self.cuts.append((l["e"] + 0.05, EXTRA[l["id"]])); shift += EXTRA[l["id"]]
        self.narr_end = self.lines[-1]["e"]
        self.end = self.narr_end + 4.4          # olaceo: in at +0.9, hold 2 s, cut, 0.5 s black
    def T(self, i): return self.by[i]["s"]
    def E(self, i): return self.by[i]["e"]
    def W(self, i, k): return self.by[i]["words"][k]["s"]
    def Wn(self, i, word, nth=0):
        """Start of the nth word in line i that matches `word` (letters only)."""
        n = 0
        for w in self.by[i]["words"]:
            if re.sub(r"[^a-z']", "", w["w"].lower()) == word:
                if n == nth: return w["s"]
                n += 1
        raise KeyError((i, word))
    def starts(self, i, a=0, b=None): return [w["s"] for w in self.by[i]["words"][a:b]]
    def frames(self): return int(round(self.end * FPS))

def snap(t): return round(t * FPS) / FPS

def caption_chunks(tl):
    """3 to 5 words per caption line, broken at punctuation where it can be."""
    out = []
    for l in tl.lines:
        ws = l["words"]; i = 0; n = len(ws)
        while i < n:
            rem = n - i
            if rem <= 5: j = n
            else:
                j = None
                for k in range(i + 3, min(i + 5, n - 3) + 1):          # prefer a break after punctuation
                    if re.search(r"[,.:;?!]$", ws[k - 1]["w"]): j = k
                if j is None: j = i + (4 if rem in (6, 7, 8) else 5)
                if n - j < 3: j = n - 3 if n - 3 - i >= 3 else n
            out.append(dict(line=l["id"], words=ws[i:j], s=ws[i]["s"], e=ws[j - 1]["e"]))
            i = j
    for a, b in zip(out, out[1:]): a["out"] = min(a["e"] + 0.35, b["s"])
    out[-1]["out"] = out[-1]["e"] + 0.35
    return out

def srt_time(t):
    ms = int(round(t * 1000)); return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"

def write_srt(tl, path):
    with open(path, "w") as f:
        for n, ch in enumerate(caption_chunks(tl), 1):
            f.write(f"{n}\n{srt_time(ch['s'])} --> {srt_time(max(ch['out'], ch['s'] + 0.3))}\n{' '.join(w['w'] for w in ch['words'])}\n\n")
