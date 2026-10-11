"""Captions and graphics as an ASS subtitle script, burned in by libass.

ASS is the cheapest motion-graphics engine that ships with ffmpeg: per-word color, size, scale
springs, fades, rotation and vector shapes (rounded panels), all resolution-independent.
Heavier designs (text behind the speaker, 3D) go through Remotion or Blender instead.
"""
from __future__ import annotations

from .timeline import Timeline

W, H = 1080, 1920


def _ts(t: float) -> str:
    t = max(0.0, t)
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def _bgr(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    return f"&H{h[4:6]}{h[2:4]}{h[0:2]}&".upper()


def _esc(s: str) -> str:
    return s.replace("\\", "").replace("{", "(").replace("}", ")").replace("\n", " ")


def _wrap(text: str, width: int) -> str:
    text = _esc(text)
    lines, cur = [], ""
    for w in text.split():
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return r"\N".join(lines)


def _panel(w: int, h: int, r: int = 36) -> str:
    """Rounded rectangle as an ASS vector drawing, origin at its top-left."""
    return (f"m {r} 0 l {w - r} 0 b {w} 0 {w} 0 {w} {r} l {w} {h - r} b {w} {h} {w} {h} {w - r} {h} "
            f"l {r} {h} b 0 {h} 0 {h} 0 {h - r} l 0 {r} b 0 0 0 0 {r} 0")


def build(tl: Timeline, style: dict) -> str:
    col = style["colors"]
    cap = style["caption"]
    cfont, tfont = cap["font"], style["title"]["font"]
    glow = r"\bord5\blur7\3c&H000000&\shad0" if cap.get("glow") else r"\bord3\3c&H000000&\shad2"
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{cfont},{cap['size']},&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,4,0,5,60,60,0,1
Style: Title,{tfont},{style['title']['size']},&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,2,0,1,0,0,8,40,40,0,1
Style: Box,{cfont},60,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev: list[str] = []
    y = int(cap["y"] * H)

    def line(layer, a, b, sty, text):
        if b - a > 0.01:
            ev.append(f"Dialogue: {layer},{_ts(a)},{_ts(b)},{sty},,0,0,0,,{text}")

    # Graphics windows push captions out of the way (never the same words twice, never overlapping).
    busy_center = [(g.start, g.end) for g in tl.graphics if g.kind == "popup"]

    for c in tl.captions:
        if c.hidden:
            continue
        cy = y - 260 if any(a < c.end and b > c.start for a, b in busy_center) else y
        cy = min(cy, H - 520) if any(g.kind == "cta" and g.start < c.end for g in tl.graphics) else cy
        kw = [w for w in c.words if w.color != "white"]
        # Word-by-word: one event per word, the page grows as he says it.
        for i, w in enumerate(c.words):
            a = w.t0 if i else c.start
            b = c.words[i + 1].t0 if i + 1 < len(c.words) else c.end
            parts = []
            for j, x in enumerate(c.words[: i + 1]):
                t = _esc(x.w)
                if x.color != "white":
                    t = t.upper() if cap.get("uppercase_keywords") else t
                    parts.append(r"{\c" + _bgr(col[x.color]) + r"\fs" + str(int(cap["size"] * 1.32)) + "}" + t + r"{\r}")
                else:
                    parts.append(t.lower() if kw and cap.get("uppercase_keywords") else t)
            sep = r"\N" if kw and len(c.words) > 1 else " "
            text = sep.join(parts) if kw else " ".join(parts)
            anim = ""
            if i == 0:   # page entrance: spring pop with overshoot
                anim = r"\fscx72\fscy72\t(0,90,\fscx108\fscy108)\t(90,170,\fscx100\fscy100)"
            if w.color != "white" and i > 0:   # keyword slam
                anim = r"\fscx125\fscy125\frz-2\t(0,120,\fscx100\fscy100\frz0)"
            line(2, a, b, "Cap", "{\\an5\\pos(540," + str(cy) + ")" + glow + anim + "}" + text)

    for g in tl.graphics:
        a, b = g.start, g.end
        if g.kind == "title":
            gy = 300 if g.position == "top" else 860
            color = _bgr(col.get(g.color, col["gold"]))
            text = _wrap(g.text, 14)
            line(5, a, b, "Title", "{\\an8\\pos(540," + str(gy) + r")\c" + color +
                 r"\bord0\blur0\shad0\fad(80,160)\fscx130\fscy130\blur12\t(0,160,\fscx100\fscy100\blur0)\3c&H000000&}"
                 + text)
            line(4, a, b, "Title", "{\\an8\\pos(540," + str(gy + 6) + r")\c&H000000&\alpha&H70&\blur14\fad(80,160)}" + text)
        elif g.kind == "popup":
            pw, ph = 860, 260
            x0, y0 = (W - pw) // 2, int(H * 0.36)
            color = _bgr(col.get(g.color, col["gold"]))
            pop = r"\fscx40\fscy40\t(0,110,\fscx106\fscy106)\t(110,200,\fscx100\fscy100)"
            line(6, a, b, "Box", "{\\an7\\pos(" + f"{x0},{y0}" + r")\org(540," + str(y0 + ph // 2) + r")\p1\1c&H141414&\1a&H18&\3c"
                 + color + r"\bord4\shad0\blur1" + pop + r"\fad(0,160)}" + _panel(pw, ph))
            line(7, a, b, "Title", "{\\an5\\pos(540," + str(y0 + ph // 2) + r")\org(540," + str(y0 + ph // 2) + r")\c" + color
                 + r"\fs150\bord0" + pop + r"\fad(0,160)}" + _wrap(g.text, 16))
        elif g.kind == "counter":
            line(6, a, b, "Title", "{\\an5\\pos(540,700)\\c" + _bgr(col["green"]) + "\\fad(60,120)}" + _esc(g.text))
        elif g.kind == "lower_third":
            line(6, a, b, "Box", "{\\an1\\pos(70,1560)\\fs54\\bord3\\3c&H000000&\\fad(150,150)}" + _esc(g.text))
        elif g.kind == "cta":
            pw, ph = 760, 200
            x0, y0 = (W - pw) // 2, H - 470
            flip = a + 1.0
            panel = "{\\an7\\pos(" + f"{x0},{y0}" + r")\org(540," + str(y0 + 100) + r")\p1\1c&H141414&\1a&H10&\3c&H333333&\bord2"
            line(8, a, b, "Box", panel + r"\fscx60\fscy60\t(0,140,\fscx100\fscy100)\fad(80,0)}" + _panel(pw, ph, 100))
            line(9, a, b, "Box", "{\\an4\\pos(" + str(x0 + 200) + "," + str(y0 + 64) + r")\fs40\c&HFFFFFF&\fad(120,0)}"
                 + _esc(g.text))
            btn = "{\\an7\\pos(" + str(x0 + 200) + "," + str(y0 + 108) + r")\p1\bord0"
            line(9, a, flip, "Box", btn + r"\1c&H4A3BFF&\fad(120,0)}" + _panel(230, 64, 32))
            line(9, flip, b, "Box", btn + r"\1c&H3A3A3A&\fscx115\fscy115\t(0,120,\fscx100\fscy100)}" + _panel(300, 64, 32))
            line(10, a, flip, "Box", "{\\an5\\pos(" + str(x0 + 315) + "," + str(y0 + 140) + r")\fs36\c&HFFFFFF&\fad(120,0)}Follow")
            line(10, flip, b, "Box", "{\\an5\\pos(" + str(x0 + 350) + "," + str(y0 + 140) + r")\fs36\c&HFFFFFF&}Following")
    return head + "\n".join(ev) + "\n"
