"""01-alexander.md -> scenes.json: per scene, the spoken lines (voice, text, pause after) and the picture cues.
Pauses: sentence 0.9 s, paragraph 1.4 s, voice change +1.0 s, a [▸ Silence…] cue = 3.2 s, after "What do you do?" 3.2 s."""
import re, json, sys
src = open(sys.argv[1] if len(sys.argv) > 1 else "../scripts/01-alexander.md").read()
body = src.split("\n---\n", 1)[1].split("\n---\n*Build notes", 1)[0]
scenes = []
for blk in re.split(r"\n### ", "\n" + body)[1:]:
    head, *rest = blk.split("\n"); txt = "\n".join(rest)
    sc = {"title": head.strip(), "cues": [], "lines": []}
    voice = None
    for para in re.split(r"\n\s*\n", txt):
        para = para.strip()
        if not para or para == "---": continue
        if para.startswith("[▸"):
            sc["cues"].append(para.strip("[]▸ "))
            if re.search(r"silence", para, re.I) and sc["lines"]: sc["lines"][-1]["pause"] = max(sc["lines"][-1]["pause"], 3.2)
            continue
        m = re.match(r"\*\*(GEORGE|FABLE):\*\*\s*(.*)", para, re.S)
        if m: voice = "bm_george" if m.group(1) == "GEORGE" else "bm_fable"; para = m.group(2)
        if voice is None: continue
        for raw in para.split("\n"):
            raw = re.sub(r"^\s*-\s*", "", raw).replace("**", "").replace("*", "").strip()
            if not raw: continue
            sents = re.findall(r"[^.?!:]+(?:[.?!]+|:(?=\s)|$)", raw)
            sents = [s.strip() for s in sents if s.strip()]
            buf = ""
            for s in sents:   # keep lines 1–2 sentences, ≤ ~22 words
                if buf and len((buf + " " + s).split()) > 22: sc["lines"].append({"voice": voice, "text": buf, "pause": 0.9}); buf = s
                else: buf = (buf + " " + s).strip()
                if buf.endswith(("?", "!")) or len(buf.split()) >= 12: sc["lines"].append({"voice": voice, "text": buf, "pause": 0.9}); buf = ""
            if buf: sc["lines"].append({"voice": voice, "text": buf, "pause": 0.9})
        if sc["lines"]: sc["lines"][-1]["pause"] = max(sc["lines"][-1]["pause"], 1.4)
    for i, l in enumerate(sc["lines"]):
        if l["text"].startswith("What do you do"): l["pause"] = 3.2; sc["lines"][i - 1]["pause"] = max(sc["lines"][i - 1]["pause"], 3.0)
    if sc["lines"]: sc["lines"][-1]["pause"] = 2.4
    scenes.append(sc)
json.dump(scenes, open("scenes.json", "w"), indent=1)
W = 0
for i, s in enumerate(scenes):
    w = sum(len(l["text"].split()) for l in s["lines"]); W += w
    print(f"{i:2d} {s['title'][:42]:42s} lines {len(s['lines']):3d} words {w:4d}")
print("total words", W, "≈", round(W / 105, 1), "min at sleep pace")
