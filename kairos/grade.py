"""Color grading: Lumetri, stripped to what an agent can reason about.

A grade = a look (named preset) + intensity (0..1) + optional .cube LUT + optional accent hold.
- Looks are ffmpeg filter chains with every parameter scaled by intensity, so "a little moody" works.
- LUTs: any .cube dropped into data/library/luts (or uploaded in the Library) becomes a look.
- Accent hold (playbook §18): desaturate everything except one color, e.g. the brand gold.
- Match: measure a reference still and the footage, then transfer per-channel mean/contrast
  (a statistical "Color Match", like Premiere's Comparison View match).
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from . import media
from .config import LIBRARY

LUTS = LIBRARY / "luts"
CUSTOM = LIBRARY / "looks.json"
LUTS.mkdir(parents=True, exist_ok=True)

# name: (label, description, params). Params are the look at intensity 1.0.
LOOKS: dict[str, dict] = {
    "none": {"label": "Original", "about": "No grade.", "p": {}},
    "natural": {"label": "Natural", "about": "Auto exposure and white balance, nothing else.",
                "p": {"normalize": 0.6}},
    "moody": {"label": "Moody", "about": "The §18 standard: desaturated, darker, deep blacks.",
              "p": {"sat": -0.30, "bright": -0.045, "contrast": 0.08, "gamma": -0.05}},
    "moody_gold": {"label": "Moody + Gold", "about": "Moody, and only the brand gold keeps its color.",
                   "p": {"sat": -0.15, "bright": -0.04, "contrast": 0.08, "hold": "0xFFD24A"}},
    "teal_orange": {"label": "Teal & Orange", "about": "Blockbuster: warm skin, teal shadows.",
                    "p": {"shadows": (-0.08, 0.0, 0.10), "highlights": (0.08, 0.02, -0.08), "sat": 0.08, "contrast": 0.06}},
    "warm_film": {"label": "Warm Film", "about": "Golden, soft, lifted blacks, light grain.",
                  "p": {"mids": (0.06, 0.02, -0.06), "lift": 0.04, "sat": -0.05, "grain": 6, "vignette": 0.4}},
    "cool_clean": {"label": "Cool Clean", "about": "Crisp tech look, cooler whites.",
                   "p": {"highlights": (-0.03, 0.0, 0.05), "contrast": 0.05, "sat": -0.05, "sharpen": 0.6}},
    "punchy": {"label": "Punchy", "about": "Bright, saturated, social-first.",
               "p": {"sat": 0.18, "contrast": 0.10, "bright": 0.01, "sharpen": 0.5}},
    "golden_hour": {"label": "Golden Hour", "about": "Sunset warmth over everything.",
                    "p": {"mids": (0.09, 0.04, -0.08), "highlights": (0.06, 0.03, -0.04), "sat": 0.05}},
    "noir": {"label": "Noir", "about": "Black and white, hard contrast.",
             "p": {"sat": -1.0, "contrast": 0.22, "gamma": -0.06, "vignette": 0.5}},
    "faded": {"label": "Faded", "about": "Matte blacks, muted color, editorial.",
              "p": {"lift": 0.07, "sat": -0.22, "contrast": -0.06}},
}


def _custom() -> dict:
    return json.loads(CUSTOM.read_text()) if CUSTOM.exists() else {}


def catalog() -> list[dict]:
    out = [{"id": k, "label": v["label"], "about": v["about"], "kind": "look"} for k, v in LOOKS.items()]
    out += [{"id": f"lut:{p.name}", "label": p.stem.replace("_", " ").title(), "about": "Your LUT.", "kind": "lut"}
            for p in sorted(LUTS.glob("*.cube"))]
    out += [{"id": f"custom:{k}", "label": v["label"], "about": v.get("about", "Matched look."), "kind": "custom"}
            for k, v in _custom().items()]
    return out


def chain(look: str, intensity: float = 1.0) -> str:
    """ffmpeg filter chain (ending in ',') for a look at an intensity. '' for none."""
    k = max(0.0, min(1.5, float(intensity)))
    if not look or look == "none" or k == 0:
        return ""
    if look.startswith("lut:"):
        f = LUTS / look[4:]
        if not f.exists():
            return ""
        if k >= 0.999:
            return f"lut3d=file='{f}',"
        # blend LUT with the original by intensity
        return f"split[ga][gb];[gb]lut3d=file='{f}'[gc];[ga][gc]blend=all_mode=normal:all_opacity={k:.3f},"
    if look.startswith("custom:"):
        c = _custom().get(look[7:])
        return _linear(c["gain"], c["offset"], k) if c else ""
    p = LOOKS.get(look, {}).get("p", {})
    f = []
    if "normalize" in p:
        f.append(f"normalize=smoothing=24:independence={1 - p['normalize'] * k:.2f}:strength={min(1, p['normalize'] * k):.2f}")
    for zone, key in (("s", "shadows"), ("m", "mids"), ("h", "highlights")):
        if key in p:
            r, g, b = (x * k for x in p[key])
            f.append(f"colorbalance=r{zone}={r:.3f}:g{zone}={g:.3f}:b{zone}={b:.3f}")
    eq = {"saturation": 1 + p.get("sat", 0) * k, "contrast": 1 + p.get("contrast", 0) * k,
          "brightness": p.get("bright", 0) * k, "gamma": 1 + p.get("gamma", 0) * k}
    if any(abs(v - d) > 1e-4 for v, d in zip(eq.values(), (1, 1, 0, 1))):
        f.append("eq=" + ":".join(f"{n}={v:.3f}" for n, v in eq.items()))
    if "lift" in p:
        lo = p["lift"] * k
        f.append(f"colorlevels=romin={lo:.3f}:gomin={lo:.3f}:bomin={lo:.3f}")
    if "hold" in p:
        f.append(f"colorhold=color={p['hold']}:similarity=0.22:blend=0.15")
    if "sharpen" in p:
        f.append(f"unsharp=5:5:{p['sharpen'] * k:.2f}")
    if "vignette" in p:
        f.append(f"vignette=angle=PI/{max(3, 8 - 4 * p['vignette'] * k):.2f}")
    if "grain" in p:
        f.append(f"noise=alls={int(p['grain'] * k)}:allf=t")
    return ",".join(f) + "," if f else ""


def _linear(gain, offset, k: float) -> str:
    g = [1 + (x - 1) * k for x in gain]
    o = [x * k for x in offset]
    return (f"lutrgb=r='clip(val*{g[0]:.4f}+{o[0]:.2f},0,255)':g='clip(val*{g[1]:.4f}+{o[1]:.2f},0,255)'"
            f":b='clip(val*{g[2]:.4f}+{o[2]:.2f},0,255)',")


def _stats(path: str | Path, t: float | None = None, n: int = 6) -> tuple[list[float], list[float]]:
    """Per-channel mean/std over a few small frames (or one still)."""
    import numpy as np
    frames = []
    times = [None] if t is None else [t + i * 1.5 for i in range(n)]
    for tt in times:
        args = [media.FFMPEG, "-v", "error"] + (["-ss", f"{tt:.2f}"] if tt is not None else []) + [
            "-i", str(path), "-frames:v", "1", "-vf", "scale=96:96", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
        raw = subprocess.run(args, capture_output=True).stdout
        if len(raw) == 96 * 96 * 3:
            frames.append(np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3).astype(float))
    if not frames:
        raise RuntimeError("could not read frames for color match")
    px = np.concatenate(frames)
    return px.mean(0).tolist(), (px.std(0) + 1e-3).tolist()


def match(reference: str | Path, footage: str | Path, at: float, name: str) -> str:
    """Create a custom look that moves the footage's color toward a reference still. Returns its id."""
    mr, sr = _stats(reference)
    ms, ss = _stats(footage, at)
    gain = [max(0.6, min(1.6, r / s)) for r, s in zip(sr, ss)]
    offset = [mr_ - g * ms_ for mr_, g, ms_ in zip(mr, gain, ms)]
    looks = _custom()
    key = "".join(ch for ch in name.lower().replace(" ", "_") if ch.isalnum() or ch == "_") or "match"
    looks[key] = {"label": name, "about": f"Matched to {Path(reference).name}", "gain": gain, "offset": offset}
    CUSTOM.write_text(json.dumps(looks, indent=2))
    return f"custom:{key}"


def still(src: str | Path, at: float, look: str, intensity: float, out: str | Path, width: int = 360) -> Path:
    """One graded frame: powers the look picker, so you choose looks on YOUR footage."""
    vf = (f"crop=w='min(iw,ih*9/16)':h='min(ih,iw*16/9)',scale={width}:-2,"
          + chain(look, intensity) + "format=yuv420p")
    media.run([media.FFMPEG, "-v", "error", "-y", "-ss", f"{at:.2f}", "-i", str(src), "-frames:v", "1",
               "-vf", vf, "-q:v", "3", str(out)])
    return Path(out)
