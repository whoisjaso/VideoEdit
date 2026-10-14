"""Parse the locked Lead With Questions scripts (spec §7 notation) into timed-ready events.

The script files are copied verbatim from the spec (§8.2 and §9.2). Nothing here rewrites a spoken
word. The only spoken-text change is {NAME} -> Jason, plus the pronunciation spellings in
PRON_SPELLINGS (logged in deliverables/CHANGELOG.md).
"""
import re
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
NAME = "Jason"

# spoken-text spelling fixes for the voice engine only (pronunciation, never wording)
PRON_SPELLINGS = {}


def tc(s):
    m, sec = s.split(":")
    return int(m) * 60 + float(sec)


@dataclass
class Item:
    kind: str                 # say | pause | tone | br
    text: str = ""
    role: str = "A"           # A | B | SELF
    embedded: bool = False
    secs: float = 0.0
    after_tone: bool = False  # an IMPACT pause (never shortened)
    line: int = 0             # index of the script line this came from


@dataclass
class Unit:
    """A block with its own target window: a section, or a scene inside N6 / M4."""
    sid: str
    title: str
    start: float
    end: float
    items: list = field(default_factory=list)
    label: str = ""           # scene label for the screen (N6/M4)


@dataclass
class Section:
    sid: str
    title: str
    start: float
    end: float
    units: list = field(default_factory=list)


TOKEN = re.compile(r"\[P([\d.]+)\]|\[BR\]|\[TONE\]|\*([^*]+)\*|([^\[*]+)")


def tokens(body):
    out = []
    for m in TOKEN.finditer(body):
        if m.group(1):
            out.append(("pause", float(m.group(1))))
        elif m.group(0) == "[BR]":
            out.append(("br", None))
        elif m.group(0) == "[TONE]":
            out.append(("tone", None))
        elif m.group(2) is not None:
            out.append(("emb", m.group(2).strip()))
        else:
            t = m.group(3).strip()
            if t:
                out.append(("text", t))
    return out


def spoken(text):
    text = text.replace("{NAME}", NAME)
    for a, b in PRON_SPELLINGS.items():
        text = text.replace(a, b)
    return text


def parse(path):
    sections = []
    line_no = 0
    for raw in Path(path).read_text().splitlines():
        s = raw.strip()
        m = re.match(r"\*\*([NM]\d) · (.+?) · (\d\d:\d\d)–(\d\d:\d\d)\*\*", s)
        if m:
            sec = Section(m.group(1), m.group(2).title(), tc(m.group(3)), tc(m.group(4)))
            sec.units.append(Unit(sec.sid, sec.title, sec.start, sec.end))
            sections.append(sec)
            continue
        m = re.match(r"\*Scene (\d) · (.+?) · (\d\d:\d\d)–(\d\d:\d\d)\*", s)
        if m:
            sec = sections[-1]
            u = Unit(f"{sec.sid}.{m.group(1)}", m.group(2).title(), tc(m.group(3)), tc(m.group(4)),
                     label=m.group(2).replace("THE ", ""))
            prev = sec.units[-1]
            prev.end = u.start
            sec.units.append(u)
            continue
        m = re.match(r"(A|B|SELF/A):\s*(.*)", s)
        if not m:
            continue
        role = {"A": "A", "B": "B", "SELF/A": "SELF"}[m.group(1)]
        unit = sections[-1].units[-1]
        line_no += 1
        prev = None
        for kind, val in tokens(m.group(2)):
            if kind == "pause":
                unit.items.append(Item("pause", secs=val, after_tone=(prev == "tone"), line=line_no))
            elif kind == "br":
                unit.items.append(Item("br", line=line_no))
            elif kind == "tone":
                unit.items.append(Item("tone", line=line_no))
            else:
                text = spoken(val)
                # "*...you hold the light...*": keep the ellipses (they shape the delivery)
                unit.items.append(Item("say", text=text, role=role, embedded=(kind == "emb"), line=line_no))
            prev = kind
    # the last unit of each section ends with the section
    for sec in sections:
        sec.units[-1].end = sec.end
    return sections


def spoken_lines(path):
    """Every spoken line as one string (for the lock diff, captions and the pronunciation gate)."""
    out = []
    for raw in Path(path).read_text().splitlines():
        m = re.match(r"(A|B|SELF/A):\s*(.*)", raw.strip())
        if m:
            body = re.sub(r"\[P[\d.]+\]|\[BR\]|\[TONE\]", " ", m.group(2))
            body = body.replace("*", "")
            out.append((m.group(1), re.sub(r"\s+", " ", body).strip()))
    return out


if __name__ == "__main__":
    import sys
    for p in sys.argv[1:]:
        for sec in parse(p):
            n = sum(len(u.items) for u in sec.units)
            print(sec.sid, sec.title, sec.start, sec.end, [(u.sid, u.start, u.end) for u in sec.units], n)
