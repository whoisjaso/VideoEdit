"""Render a Timeline to MP4 with one ffmpeg call (the Media Encoder step).

Per segment: fast-seek input -> speed -> 9:16 crop around the face -> keyframed zoom ->
grade. Then concat, burn captions/graphics (ASS), overlay images/avatar, mix SFX under the
voice, normalise to -14 LUFS (TikTok/Reels loudness).
"""
from __future__ import annotations

import json
from pathlib import Path

from . import ass, grade as grading, media, sfx as sfxlib
from .config import FONTS, LIBRARY, SKILL
from .timeline import Keyframe, Timeline


def _ease(k0: Keyframe, k1: Keyframe) -> str:
    """Expression for value between two keyframes (t is segment-local seconds)."""
    if k0.ease == "hold" or abs(k1.value - k0.value) < 1e-6:
        return f"{k0.value:.5f}"
    span = max(k1.t - k0.t, 1e-3)
    x = f"(t-{k0.t:.4f})/{span:.4f}"
    curve = {
        "linear": "X",
        "ease_in": "X*X*X",
        "ease_out": "(1-(1-X)*(1-X)*(1-X))",
        # back-out spring: shoots ~10% past the target, then settles (the pop-in feel)
        "overshoot": "(1+2.70158*(X-1)*(X-1)*(X-1)+1.70158*(X-1)*(X-1))",
    }.get(k1.ease, "X*X*(3-2*X)")
    return f"({k0.value:.5f}+{k1.value - k0.value:.5f}*{curve.replace('X', '(' + x + ')')})"


def shake_expr(shakes, axis: int) -> str:
    """Sum of decaying sines (two incommensurate frequencies per axis): a deterministic wiggle()."""
    if not shakes:
        return "0"
    f1, f2 = (31.0, 47.0) if axis == 0 else (37.0, 53.0)
    terms = []
    for s in shakes:
        terms.append(f"between(t,{s.t:.3f},{s.t + s.dur:.3f})*{s.amp:.2f}*(1-(t-{s.t:.3f})/{s.dur:.3f})"
                     f"*(0.6*sin({f1}*(t-{s.t:.3f}))+0.4*sin({f2}*(t-{s.t:.3f})+1.3))")
    return "+".join(terms)


def zoom_expr(kfs: list[Keyframe]) -> str:
    if not kfs:
        return "1"
    if len(kfs) == 1:
        return f"{kfs[0].value:.5f}"
    expr = f"{kfs[-1].value:.5f}"
    for k0, k1 in reversed(list(zip(kfs, kfs[1:]))):
        expr = f"if(lt(t,{k1.t:.4f}),{_ease(k0, k1)},{expr})"
    return expr


def avatar_path() -> Path | None:
    for p in (LIBRARY / "avatar.png", SKILL / "assets" / "avatar.png"):
        if p.exists():
            return p
    return None


def render(tl: Timeline, src: str, info: dict, style: dict, out: str | Path, preview: bool = False,
           workdir: str | Path | None = None) -> Path:
    out = Path(out)
    work = Path(workdir or out.parent)
    work.mkdir(parents=True, exist_ok=True)
    W, H, FPS = tl.width, tl.height, tl.fps
    RW, RH = (W // 2, H // 2) if preview else (W, H)
    args = ["-v", "error", "-y"]
    fc: list[str] = []

    n_in = 0
    for i, s in enumerate(tl.segments):
        src_d = s.src_out - s.src_in
        N = max(1, round(s.out_dur * FPS))
        T = N / FPS
        args += ["-ss", f"{s.src_in:.3f}", "-t", f"{src_d + 0.5:.3f}", "-i", src]
        z = zoom_expr(s.zoom)
        if s.shake:   # headroom so the shaken frame never shows an edge
            z = f"({z})*(1+0.05*({'+'.join(f'between(t,{k.t:.3f},{k.t + k.dur:.3f})' for k in s.shake)}))"
        sc = RW / W
        sx = f"(iw-ow)/2+({shake_expr(s.shake, 0)})*{sc:.3f}"
        sy = f"(ih-oh)/2+({shake_expr(s.shake, 1)})*{sc:.3f}"
        cx = f"{s.crop_x:.4f}"
        fc.append(
            f"[{n_in}:v]setpts=(PTS-STARTPTS)/{s.speed},fps={FPS},"
            f"crop=w='min(iw,ih*9/16)':h='min(ih,iw*16/9)':x='max(0,min(iw-ow,iw*{cx}-ow/2))':y='(ih-oh)/2',"
            f"scale=w='trunc({RW}*({z})/2)*2':h='trunc({RH}*({z})/2)*2':eval=frame:flags=bicubic,"
            f"crop={RW}:{RH}:x='max(0,min(iw-ow,{sx}))':y='max(0,min(ih-oh,{sy}))',setsar=1,format=yuv420p,"
            f"tpad=stop=15:stop_mode=clone,trim=end_frame={N},setpts=N/{FPS}/TB[v{i}]")
        if info.get("has_audio"):
            speed = (f"aresample=48000,asetrate={int(48000 * s.speed)},aresample=48000," if s.pitch_drop
                     else (f"atempo={s.speed}," if s.speed != 1 else ""))
            fc.append(f"[{n_in}:a]asetpts=PTS-STARTPTS,atrim=0:{src_d:.4f},aresample=48000,{speed}"
                      f"apad,atrim=0:{T:.4f},afade=t=in:d=0.012,afade=t=out:st={max(0, T - 0.025):.4f}:d=0.025,"
                      f"aformat=sample_rates=48000:channel_layouts=stereo[a{i}]")
        else:
            fc.append(f"anullsrc=r=48000:cl=stereo,atrim=0:{T:.4f}[a{i}]")
        n_in += 1

    k = len(tl.segments)
    fc.append("".join(f"[v{i}][a{i}]" for i in range(k)) + f"concat=n={k}:v=1:a=1[vcat][acat]")

    sub = work / f"{tl.id}.ass"
    sub.write_text(ass.build(tl, style))
    fc.append(f"[vcat]{grading.chain(tl.grade, tl.grade_intensity)}ass=filename='{sub}':fontsdir='{FONTS}'[vass]")
    vlast = "vass"

    # Image / Blender overlays (V3+).
    sc = RW / W
    for g in tl.graphics:
        if g.kind in ("image", "blender") and g.asset and Path(g.asset).exists():
            is_img = Path(g.asset).suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")
            args += (["-loop", "1", "-t", f"{g.end:.3f}", "-i", g.asset] if is_img
                     else ["-itsoffset", f"{g.start:.3f}", "-i", g.asset])
            gw = int(g.params.get("width", 900) * sc)
            fc.append(f"[{n_in}:v]scale={gw}:-2,format=rgba[ov{n_in}]")
            y = {"top": int(220 * sc), "center": "(H-h)/2", "bottom": f"H-h-{int(380 * sc)}", "behind": "(H-h)/2"}[g.position]
            fc.append(f"[{vlast}][ov{n_in}]overlay=x=(W-w)/2:y={y}:eof_action=pass:"
                      f"enable='between(t,{g.start:.3f},{g.end:.3f})'[vo{n_in}]")
            vlast = f"vo{n_in}"
            n_in += 1
    cta = next((g for g in tl.graphics if g.kind == "cta"), None)
    av = avatar_path()
    if cta and av:
        d = int(120 * sc)
        args += ["-loop", "1", "-t", f"{cta.end:.3f}", "-i", str(av)]
        fc.append(f"[{n_in}:v]scale={d}:{d},format=rgba,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':"
                  f"a='if(lte(hypot(X-{d / 2},Y-{d / 2}),{d / 2 - 1}),255,0)'[avt]")
        x0, y0 = int((W - 760) / 2 * sc + 40 * sc), int((H - 470) * sc + 40 * sc)
        fc.append(f"[{vlast}][avt]overlay=x={x0}:y={y0}:enable='between(t,{cta.start + 0.1:.3f},{cta.end:.3f})'[vav]")
        vlast = "vav"
        n_in += 1

    # SFX (A2+) under the voice.
    mix = ["[acat]"]
    for j, c in enumerate(tl.sfx):
        p = sfxlib.resolve(c.name)
        if not p or c.t >= tl.duration:
            continue
        args += ["-i", str(p)]
        ms = int(c.t * 1000)
        fc.append(f"[{n_in}:a]aresample=48000,aformat=channel_layouts=stereo,volume={c.gain:.3f},adelay={ms}|{ms}[s{j}]")
        mix.append(f"[s{j}]")
        n_in += 1
    total = tl.duration
    fc.append(f"{''.join(mix)}amix=inputs={len(mix)}:normalize=0:duration=first,"
              f"loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.95,atrim=0:{total:.4f}[aout]")

    script = work / f"{tl.id}.filter"
    script.write_text(";\n".join(fc))
    args += ["-filter_complex_script", str(script), "-map", f"[{vlast}]", "-map", "[aout]",
             "-r", str(FPS), "-c:v", "libx264", "-pix_fmt", "yuv420p",
             "-preset", "veryfast" if preview else "medium", "-crf", "26" if preview else "18",
             "-c:a", "aac", "-b:a", "128k" if preview else "256k", "-movflags", "+faststart",
             "-t", f"{total:.4f}", str(out)]
    media.run([media.FFMPEG, *args])
    (work / f"{tl.id}.render.json").write_text(json.dumps({"out": str(out), "preview": preview, "duration": total}))
    return out
