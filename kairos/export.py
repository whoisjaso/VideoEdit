"""Hand-off formats, so a person can finish any clip in a traditional NLE.

- Premiere Pro / Resolve / Final Cut 7: FCP7 XML (xmeml). File > Import in Premiere opens it
  as a 1080x1920 sequence with every cut placed against the original source file.
- SRT captions (the raw, word-accurate text) for any editor or platform.
- The Timeline JSON itself, which is the source of truth.
"""
from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

from .timeline import Timeline


def _tc(t: float) -> str:
    h, rem = divmod(max(0.0, t), 3600)
    m, s = divmod(rem, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s % 1) * 1000)):03d}"


def srt(tl: Timeline) -> str:
    out = []
    for i, c in enumerate(tl.captions, 1):
        out.append(f"{i}\n{_tc(c.start)} --> {_tc(c.end)}\n{c.text}\n")
    return "\n".join(out)


def fcpxml7(tl: Timeline, source: str | Path, info: dict) -> str:
    fps = tl.fps
    src = Path(source).resolve()
    dur_src = int(info["duration"] * fps)
    rate = f"<rate><timebase>{fps}</timebase><ntsc>FALSE</ntsc></rate>"
    file_el = (f'<file id="file-1"><name>{escape(src.name)}</name><pathurl>file://{escape(str(src))}</pathurl>{rate}'
               f"<duration>{dur_src}</duration><media><video><samplecharacteristics><width>{info['width']}</width>"
               f"<height>{info['height']}</height></samplecharacteristics></video><audio><channelcount>2</channelcount></audio></media></file>")
    v_items, a_items, t = [], [], 0
    for i, s in enumerate(tl.segments):
        n = round(s.out_dur * fps)
        name = f"{s.tag or 'seg'} {i + 1}" + (f" ({int(s.speed * 100)}%)" if s.speed != 1 else "")
        common = (f"<name>{escape(name)}</name><duration>{dur_src}</duration>{rate}<start>{t}</start><end>{t + n}</end>"
                  f"<in>{round(s.src_in * fps)}</in><out>{round(s.src_in * fps) + round((s.src_out - s.src_in) * fps)}</out>")
        f_ref = file_el if i == 0 else '<file id="file-1"/>'
        v_items.append(f'<clipitem id="v{i}">{common}{f_ref}</clipitem>')
        a_items.append(f'<clipitem id="a{i}">{common}<file id="file-1"/><sourcetrack><mediatype>audio</mediatype>'
                       f"<trackindex>1</trackindex></sourcetrack></clipitem>")
        t += n
    markers = "".join(f"<marker><name>{escape(g.kind)}: {escape(g.text)}</name><in>{round(g.start * fps)}</in>"
                      f"<out>-1</out></marker>" for g in tl.graphics)
    markers += "".join(f"<marker><name>SFX {escape(c.name)}</name><comment>{escape(c.why)}</comment>"
                       f"<in>{round(c.t * fps)}</in><out>-1</out></marker>" for c in tl.sfx)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xmeml>
<xmeml version="5"><sequence id="seq-1"><name>{escape(tl.title or tl.id)}</name><duration>{t}</duration>{rate}
<media><video><format><samplecharacteristics>{rate}<width>{tl.width}</width><height>{tl.height}</height>
<pixelaspectratio>square</pixelaspectratio></samplecharacteristics></format>
<track>{''.join(v_items)}</track></video>
<audio><track>{''.join(a_items)}</track></audio></media>{markers}</sequence></xmeml>
"""
