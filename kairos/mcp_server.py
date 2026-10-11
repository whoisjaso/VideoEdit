"""MCP server: the agent's hands on the editor.

Claude (Desktop, Code, or any MCP client) connects here and edits natively: it reads the
transcript, picks moments, patches the EditGraph, places SFX and graphics, grades, renders,
and learns from feedback. The video itself never travels through the chat, so there is no
30 MB limit: the file stays on the machine running Kairos.

    claude mcp add kairos -- python -m kairos mcp
"""
from __future__ import annotations

import json

from mcp.server.mcpserver import MCPServer

from . import autoedit, blender, export, grade, learn, project, prompts, sfx, styles
from .timeline import Graphic, Keyframe, Marker, SfxCue, Shake, Timeline
from .transcribe import sentences

mcp = MCPServer(
    name="kairos",
    instructions=(
        "Kairos is an agent-native video editor. Typical flow: list_projects or import_video -> analyze -> "
        "get_transcript -> find_moments (or pick ranges yourself) -> create_clip -> inspect get_clip -> refine with "
        "cut/add_sfx/add_graphic/add_zoom/set_caption_words/set_grade -> render_clip(preview) -> review -> "
        "render_clip(final) -> record_feedback. All clip times are seconds on the OUTPUT clock unless named src_*. "
        "Captions are raw: never censor or 'correct' the speaker's words. Use list_sfx for sound keys and "
        "get_style for the house rules before editing."),
)


def _tl(project_id: str, clip_id: str) -> Timeline:
    return project.get_clip(project_id, clip_id)


@mcp.tool()
def list_projects() -> list[dict]:
    """All projects with status, duration and clip ids."""
    return project.list_projects()


@mcp.tool()
def import_video(path: str, name: str = "", about: str = "", style: str = "jason") -> dict:
    """Create a project from a video file on this machine (any length; hours are fine). Returns the project."""
    return project.create(path, name, {"about": about, "style": style})


@mcp.tool()
def analyze(project_id: str) -> dict:
    """Probe, extract audio, detect speech and transcribe (cached). Run before get_transcript/find_moments."""
    p = project.analyze(project_id)
    return {"info": p["info"], "words": len(project.get_words(project_id)), "engine": p.get("engine")}


@mcp.tool()
def get_transcript(project_id: str, start: float = 0, end: float = 1e9) -> list[dict]:
    """Timestamped sentences (source seconds) between start and end. Each has i, start, end, text, conf."""
    return [s for s in sentences(project.get_words(project_id)) if s["end"] >= start and s["start"] <= end]


@mcp.tool()
def find_moments(project_id: str, count: int = 5, min_seconds: float = 20, max_seconds: float = 60) -> list[dict]:
    """Rank the best standalone short-form moments (Claude when connected, heuristics otherwise)."""
    return project.find_moments(project_id, count, min_seconds, max_seconds)


@mcp.tool()
def create_clip(project_id: str, src_start: float, src_end: float, title: str = "", hook: str = "",
                keywords: list[str] | None = None, cold_open_start: float | None = None,
                cold_open_end: float | None = None, style: str = "") -> dict:
    """Auto-edit a source range into a full clip with the house style (cuts, captions, zooms, SFX, title, CTA)."""
    m = {"start": src_start, "end": src_end, "title": title, "hook": hook, "keywords": keywords or [], "score": 0,
         "why": "picked by agent", "cold_open": [cold_open_start, cold_open_end] if cold_open_start is not None else None}
    return project.edit_moment(project_id, m, style or None).summary()


@mcp.tool()
def get_clip(project_id: str, clip_id: str) -> dict:
    """The full EditGraph (segments, captions, graphics, sfx, markers) for one clip."""
    return json.loads(_tl(project_id, clip_id).model_dump_json())


@mcp.tool()
def replace_clip(project_id: str, clip_id: str, timeline: dict) -> dict:
    """Overwrite a clip's EditGraph with an edited copy of get_clip's output (validated)."""
    tl = Timeline.model_validate(timeline)
    tl.id = clip_id
    return project.save_clip(project_id, tl).summary()


@mcp.tool()
def cut(project_id: str, clip_id: str, out_start: float, out_end: float) -> dict:
    """Ripple-delete a range of the clip (output seconds). Captions/graphics/sfx after it shift left."""
    tl = _tl(project_id, clip_id)
    acc, segs = 0.0, []
    for s in tl.segments:
        a, b = acc, acc + s.out_dur
        acc = b
        if b <= out_start or a >= out_end:
            segs.append(s)
            continue
        if a < out_start:
            segs.append(s.model_copy(update={"src_out": s.src_in + (out_start - a) * s.speed, "zoom": [], "shake": []}))
        if b > out_end:
            segs.append(s.model_copy(update={"src_in": s.src_in + (out_end - a) * s.speed, "zoom": [], "shake": []}))
    gap = out_end - out_start
    shift = lambda t: t if t < out_start else (None if t < out_end else t - gap)            # starts inside the cut drop
    shift_end = lambda t: t if t <= out_start else (out_start if t < out_end else t - gap)  # ends inside it clamp
    tl.segments = segs
    caps = []
    for c in tl.captions:
        words = [w.model_copy(update={"t0": shift(w.t0), "t1": max(shift(w.t0) + 0.05, shift_end(w.t1))})
                 for w in c.words if shift(w.t0) is not None]
        if words:
            caps.append(c.model_copy(update={"start": words[0].t0, "end": max(words[-1].t1, shift_end(c.end)), "words": words}))
    tl.captions = caps
    tl.graphics = [g.model_copy(update={"start": shift(g.start), "end": shift_end(g.end)}) for g in tl.graphics if shift(g.start) is not None]
    tl.sfx = [c.model_copy(update={"t": shift(c.t)}) for c in tl.sfx if shift(c.t) is not None]
    return project.save_clip(project_id, tl).summary()


@mcp.tool()
def add_sfx(project_id: str, clip_id: str, t: float, name: str, gain: float = 0.8, why: str = "") -> dict:
    """Place a sound (key from list_sfx) at output time t."""
    if not sfx.resolve(name):
        raise ValueError(f"unknown sound '{name}', see list_sfx")
    tl = _tl(project_id, clip_id)
    tl.sfx.append(SfxCue(t=t, name=name, gain=gain, why=why))
    tl.sfx.sort(key=lambda c: c.t)
    return project.save_clip(project_id, tl).summary()


@mcp.tool()
def remove_sfx(project_id: str, clip_id: str, t: float, name: str = "", tolerance: float = 0.15) -> dict:
    """Remove sounds near output time t (optionally only one name)."""
    tl = _tl(project_id, clip_id)
    tl.sfx = [c for c in tl.sfx if not (abs(c.t - t) <= tolerance and (not name or c.name == name))]
    return project.save_clip(project_id, tl).summary()


@mcp.tool()
def add_graphic(project_id: str, clip_id: str, kind: str, start: float, end: float, text: str = "",
                color: str = "gold", position: str = "top", asset: str = "", with_sfx: bool = True) -> dict:
    """Add a title | popup | counter | lower_third | cta | image | blender graphic. Pop-ups get pop+click."""
    tl = _tl(project_id, clip_id)
    tl.graphics.append(Graphic(kind=kind, start=start, end=end, text=text, color=color, position=position, asset=asset))
    if with_sfx and kind in ("popup", "counter", "image", "blender"):
        tl.sfx += [SfxCue(t=start, name="pop", why="pop-up appears"), SfxCue(t=start, name="click", why="pop-up appears")]
    return project.save_clip(project_id, tl).summary()


@mcp.tool()
def add_zoom(project_id: str, clip_id: str, t: float, hold: float = 1.0, scale: float = 1.14, with_whoosh: bool = True) -> dict:
    """Punch-in zoom at output time t (scale up, hold, release). Every zoom gets a whoosh by default."""
    tl = _tl(project_id, clip_id)
    acc = 0.0
    for s in tl.segments:
        if acc <= t < acc + s.out_dur:
            lt = t - acc
            base = [k for k in s.zoom if k.t < lt or k.t > lt + hold + 0.3]
            base += [Keyframe(t=lt, value=1.0), Keyframe(t=lt + 0.16, value=scale, ease="overshoot"),
                     Keyframe(t=min(lt + hold, s.out_dur), value=scale, ease="hold"),
                     Keyframe(t=min(lt + hold + 0.25, s.out_dur), value=1.0)]
            s.zoom = sorted({round(k.t, 3): k for k in base}.values(), key=lambda k: k.t)
            break
        acc += s.out_dur
    if with_whoosh:
        tl.sfx.append(SfxCue(t=max(0, t - 0.06), name="whoosh", why="every zoom gets a whoosh"))
    return project.save_clip(project_id, tl).summary()


@mcp.tool()
def add_shake(project_id: str, clip_id: str, t: float, dur: float = 0.32, amp: float = 12) -> dict:
    """Decaying camera shake (AE wiggle) at output time t, for impact beats. amp in pixels at 1080 wide."""
    tl = _tl(project_id, clip_id)
    acc = 0.0
    for s in tl.segments:
        if acc <= t < acc + s.out_dur:
            s.shake.append(Shake(t=t - acc, dur=dur, amp=amp))
            break
        acc += s.out_dur
    return project.save_clip(project_id, tl).summary()


@mcp.tool()
def set_caption_words(project_id: str, clip_id: str, caption_index: int, words: list[str],
                      colors: list[str] | None = None, hidden: bool | None = None) -> dict:
    """Fix a caption page's words (e.g. a mis-heard word) and colors (white|gold|green|red), keeping timing."""
    tl = _tl(project_id, clip_id)
    c = tl.captions[caption_index]
    old = c.words
    n = len(words)
    span = (c.end - c.start) / max(n, 1)
    c.words = [old[i].model_copy(update={"w": w}) if i < len(old) and n == len(old) else
               old[0].model_copy(update={"w": w, "t0": c.start + i * span, "t1": c.start + (i + 1) * span})
               for i, w in enumerate(words)]
    if colors:
        for w, col in zip(c.words, colors):
            w.color = col
    if hidden is not None:
        c.hidden = hidden
    return project.save_clip(project_id, tl).summary()


@mcp.tool()
def set_grade(project_id: str, clip_id: str, look: str, intensity: float = 1.0) -> dict:
    """Color grade: a look id from list_looks (moody, moody_gold, teal_orange, lut:<file>, custom:<name>)."""
    tl = _tl(project_id, clip_id)
    tl.grade, tl.grade_intensity = look, intensity
    return project.save_clip(project_id, tl).summary()


@mcp.tool()
def list_looks() -> list[dict]:
    """Available color looks, LUTs and matched looks."""
    return grade.catalog()


@mcp.tool()
def add_marker(project_id: str, clip_id: str, t: float, note: str) -> dict:
    """Leave a note on the timeline for the creator or the next agent."""
    tl = _tl(project_id, clip_id)
    tl.markers.append(Marker(t=t, note=note))
    return project.save_clip(project_id, tl).summary()


@mcp.tool()
def render_clip(project_id: str, clip_id: str, final: bool = False) -> dict:
    """Render the clip. Preview = 540x960 fast; final = 1080x1920 high quality. Returns the file path."""
    out = project.render_clip(project_id, clip_id, preview=not final)
    return {"path": str(out), "size_mb": round(out.stat().st_size / 1e6, 2)}


@mcp.tool()
def still(project_id: str, clip_id: str, t: float) -> dict:
    """Write a JPEG of the latest render at output time t, for visual QA. Returns its path."""
    from . import media
    r = project.latest_render(project_id, clip_id)
    if not r:
        raise ValueError("render the clip first")
    out = r.with_name(f"{clip_id}_still_{t:.2f}.jpg")
    media.thumbnail(r, out, t, width=540)
    return {"path": str(out)}


@mcp.tool()
def export_for_premiere(project_id: str, clip_id: str) -> dict:
    """Write a Premiere-importable XML sequence + SRT next to the renders. Returns their paths."""
    p = project.load(project_id)
    tl = _tl(project_id, clip_id)
    d = project.pdir(project_id) / "renders"
    x, s = d / f"{clip_id}.xml", d / f"{clip_id}.srt"
    x.write_text(export.fcpxml7(tl, project.pdir(project_id) / p["source"], p["info"]))
    s.write_text(export.srt(tl))
    return {"xml": str(x), "srt": str(s)}


@mcp.tool()
def list_sfx() -> list[dict]:
    """The sound library: key, pack and the job each sound does (from the playbook)."""
    return sfx.catalog()


@mcp.tool()
def get_style(name: str = "jason") -> dict:
    """A style profile: colors, caption/zoom/cut rules, event->SFX map and learned lessons."""
    return styles.get(name)


@mcp.tool()
def set_style_param(name: str, path: str, value: float | str | bool) -> dict:
    """Change one style rule, e.g. path='zoom.every' value=5. Future edits use it."""
    styles.set_param(name, path, value)
    return {"ok": True}


@mcp.tool()
def record_feedback(project_id: str, clip_id: str, score: float | None = None, chips: list[str] | None = None,
                    note: str = "", rebuild: bool = True) -> dict:
    """Log the creator's score/notes; tunes the style and writes a lesson. Optionally rebuilds the clip."""
    tl = _tl(project_id, clip_id)
    entry = learn.feedback(tl.style, score, chips or [], note, tl.summary())
    if rebuild and tl.moment:
        p = project.load(project_id)
        new = autoedit.build(str(project.pdir(project_id) / p["source"]), p["info"], project.get_words(project_id),
                             project.get_speech(project_id), tl.moment, styles.get(tl.style), tl.style)
        new.id, new.version, new.feedback = tl.id, tl.version, tl.feedback + [entry]
        project.save_clip(project_id, new)
    return entry


@mcp.tool()
def enhance_idea(messy: str, target: str = "video") -> dict:
    """Turn rambling spoken ideation into a clear vision + production prompt (target: video|image|edit|script)."""
    return prompts.enhance(messy, target)


@mcp.tool()
def prompt_library(kind: str = "") -> list[dict]:
    """Saved prompts (hook, edit, image, broll, idea)."""
    return prompts.library(kind or None)


@mcp.tool()
def blender_graphic(project_id: str, clip_id: str, template: str, text: str, start: float, seconds: float = 2.0,
                    value: float = 0, prefix: str = "") -> dict:
    """Render a 3D title/counter in Blender (headless) and place it on the clip. template: title3d | counter."""
    out = project.pdir(project_id) / "renders" / f"{clip_id}_3d_{int(start * 1000)}.mov"
    r = blender.make(template, text, out, seconds, value=value, prefix=prefix)
    if r["ok"]:
        add_graphic(project_id, clip_id, "blender", start, start + seconds, text=text, position="center", asset=r["out"])
    return r


def main() -> None:
    mcp.run("stdio")
