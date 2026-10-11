"""Blender bridge: 3D motion graphics rendered headless and dropped on the timeline.

Blender is open source with a full Python API (bpy), so instead of reverse engineering it we drive it:
Kairos writes a bpy script, runs `blender -b -P script.py`, and gets back a transparent
ProRes 4444 .mov the renderer overlays like any other graphic. If Blender isn't installed, the
script is still written so you (or an agent) can run it anywhere Blender is.

Templates:
  title3d  extruded, beveled hero word, gold metal, camera push-in, soft studio light
  counter  a number rolling up in 3D (money, stats)
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

BLENDER = shutil.which("blender")

SCRIPT = r'''
import bpy, math, json, sys
cfg = json.loads(r"""{cfg}""")
scn = bpy.context.scene
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
fps = 30; frames = int(cfg["seconds"] * fps)
scn.render.fps = fps; scn.frame_start = 1; scn.frame_end = frames
scn.render.resolution_x, scn.render.resolution_y = 1080, 1080
scn.render.film_transparent = True
scn.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in {{e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items}} else "BLENDER_EEVEE"
scn.render.image_settings.file_format = "FFMPEG"
scn.render.ffmpeg.format = "QUICKTIME"; scn.render.ffmpeg.codec = "PRORES"
if hasattr(scn.render.ffmpeg, "ffmpeg_prores_profile"): scn.render.ffmpeg.ffmpeg_prores_profile = "4444"
scn.render.image_settings.color_mode = "RGBA"
scn.render.filepath = cfg["out"]

def gold():
    m = bpy.data.materials.new("Gold"); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    r, g, bl = [int(cfg["color"][i:i+2], 16) / 255 for i in (1, 3, 5)]
    b.inputs["Base Color"].default_value = (r, g, bl, 1); b.inputs["Metallic"].default_value = 0.9
    b.inputs["Roughness"].default_value = 0.28
    return m

bpy.ops.object.text_add(location=(0, 0, 0))
t = bpy.context.object; t.data.body = cfg["text"]; t.data.align_x = "CENTER"; t.data.align_y = "CENTER"
t.data.extrude = 0.12; t.data.bevel_depth = 0.02; t.data.bevel_resolution = 3
t.data.materials.append(gold()); t.rotation_euler = (math.radians(90), 0, 0)
dims = max(t.dimensions.x, 0.1); s = 4.2 / dims; t.scale = (s, s, s)

if cfg["template"] == "counter":
    target = float(cfg.get("value", 0))
    def roll(scene):
        k = min(1, (scene.frame_current - 1) / max(1, frames * 0.7)); k = 1 - (1 - k) ** 3
        t.data.body = cfg.get("prefix", "") + f"{{int(target * k):,}}"
    bpy.app.handlers.frame_change_pre.append(roll)

t.keyframe_insert("rotation_euler", frame=1)
t.rotation_euler[2] = math.radians(cfg.get("spin", 12)); t.keyframe_insert("rotation_euler", frame=frames)
bpy.ops.object.camera_add(location=(0, -9, 0), rotation=(math.radians(90), 0, 0))
cam = bpy.context.object; scn.camera = cam
cam.keyframe_insert("location", frame=1); cam.location.y = -7.2; cam.keyframe_insert("location", frame=frames)
for loc, e in (((4, -6, 4), 900), ((-5, -4, 2), 500), ((0, 4, 5), 700)):
    bpy.ops.object.light_add(type="AREA", location=loc); L = bpy.context.object; L.data.energy = e; L.data.size = 5
    L.rotation_euler = (math.radians(60), 0, math.atan2(loc[0], -loc[1]))
bpy.ops.render.render(animation=True)
'''


def available() -> bool:
    return BLENDER is not None


def make(template: str, text: str, out: str | Path, seconds: float = 2.0, color: str = "#FFD24A", **extra) -> dict:
    out = Path(out)
    cfg = {"template": template, "text": text, "out": str(out), "seconds": seconds, "color": color, **extra}
    script = out.with_suffix(".py")
    script.write_text(SCRIPT.replace("{{", "{").replace("}}", "}").replace("{cfg}", json.dumps(cfg)))
    if not BLENDER:
        return {"ok": False, "script": str(script),
                "message": "Blender isn't installed here. Install it (blender.org) or run: blender -b -P " + str(script)}
    p = subprocess.run([BLENDER, "-b", "-P", str(script)], capture_output=True, text=True, timeout=900)
    ok = p.returncode == 0 and out.exists()
    return {"ok": ok, "script": str(script), "out": str(out) if ok else None,
            "message": "" if ok else p.stderr[-1200:] or p.stdout[-1200:]}
