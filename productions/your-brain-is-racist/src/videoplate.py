"""Drop-in photographic plates. If plates/<scene>_<h|v>.mp4 (or .png/.jpg) exists, the film uses it
for that scene instead of the procedural plate. Scene names are the ones in scenes.json
(eye, screens, couch, card_tank, card_hat, card_suit, street1, street2, stop, news, boy, three,
glass, observer, newscript).

Video plates play at half speed with frame blending and ping-pong, so a 4 to 8 second clip covers a
long scene without a visible loop. Every plate gets the same slow push, vignette and (for the
observer) the amber regrade, so one grain and palette holds across the film.
"""
import os, subprocess, json
import numpy as np, skia
from gfx import *

class VideoPlate:
    def __init__(self, path, W, H):
        self.W, self.H = W // 2, H // 2; self.still = path.lower().endswith((".png", ".jpg", ".jpeg"))
        vf = f"scale={self.W}:{self.H}:force_original_aspect_ratio=increase,crop={self.W}:{self.H},format=rgba"
        raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", path] + (["-frames:v", "1"] if self.still else ["-t", "12"]) +
                                      ["-vf", vf, "-f", "rawvideo", "-"])
        self.frames = np.frombuffer(raw, np.uint8).reshape(-1, self.H, self.W, 4)
        self.fps = 24.0
        if not self.still:
            r = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate", "-of", "json", path]))
            a, b = r["streams"][0]["r_frame_rate"].split("/"); self.fps = float(a) / float(b)
    def image(self, i): return skia.Image.fromarray(np.ascontiguousarray(self.frames[i]))
    def draw(self, c, W, H, local_t, dur, amber=0.0, speed=0.5):
        """c is the half-res plate canvas already scaled to full-frame units."""
        n = len(self.frames); r = skia.Rect.MakeWH(W, H); src = skia.Rect.MakeWH(self.W, self.H)
        s = 1.0 + 0.05 * clamp(local_t / max(dur, 1e-6))          # slow push
        c.save(); c.translate(W / 2, H / 2); c.scale(s, s); c.translate(-W / 2, -H / 2)
        if n == 1: c.drawImageRect(self.image(0), src, r, skia.SamplingOptions(skia.FilterMode.kLinear))
        else:
            x = local_t * self.fps * speed; period = 2 * (n - 1); x = x % period
            if x > n - 1: x = period - x                           # ping-pong
            i = int(x); f = x - i; j = min(n - 1, i + 1)
            c.drawImageRect(self.image(i), src, r, skia.SamplingOptions(skia.FilterMode.kLinear))
            if f > 0.01:
                p = skia.Paint(); p.setAlphaf(f); c.drawImageRect(self.image(j), src, r, skia.SamplingOptions(skia.FilterMode.kLinear), p)
        c.restore()
        p = skia.Paint(Color=col((128, 128, 128), 0.22)); p.setBlendMode(skia.BlendMode.kSaturation); c.drawRect(r, p)   # muted palette
        if amber > 0.01:
            p = skia.Paint(Color=col(AMBER, amber * 0.92)); p.setBlendMode(skia.BlendMode.kColor); c.drawRect(r, p)
        c.drawRect(r, skia.Paint(Color=col((0, 0, 0), 0.18)))
        vignette(c, W, H, 0.9, 0.3)

def find(root, scene, aspect):
    for ext in (".mp4", ".mov", ".webm", ".png", ".jpg", ".jpeg"):
        p = os.path.join(root, "plates", f"{scene}_{aspect}{ext}")
        if os.path.exists(p): return p
    return None
