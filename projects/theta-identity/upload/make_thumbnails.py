"""Theta Identity thumbnails: a gold-graded face (eyes closed, chin up) on the right, the type on the left.

    python projects/theta-identity/upload/make_thumbnails.py PHOTO_DIR

PHOTO_DIR holds the two free Pexels photos (Pexels License: free for commercial use, no attribution):
  pexels-3031397.jpg   man in profile, eyes closed   https://www.pexels.com/photo/3031397/
  pexels-11582029.jpg  woman in golden light         https://www.pexels.com/photo/11582029/
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
W, H = 1280, 720
K = ROOT / "kairos/assets/fonts"
F_HUGE = ImageFont.truetype(str(K / "Montserrat-ExtraBold.ttf"), 240)
F_BIG = ImageFont.truetype(str(K / "Montserrat-ExtraBold.ttf"), 104)
F_PILL = ImageFont.truetype(str(K / "Montserrat-ExtraBold.ttf"), 48)
F_BADGE = ImageFont.truetype(str(K / "Montserrat-SemiBold.ttf"), 28)


def duotone(im):
    """Black-and-white photo -> black, ember, gold, warm white."""
    g = np.asarray(ImageOps.autocontrast(im.convert("L"), cutoff=1)).astype(np.float32) / 255
    g = g ** 1.15
    stops = [(0, (4, 2, 2)), (0.35, (90, 40, 8)), (0.7, (235, 150, 50)), (1, (255, 240, 210))]
    out = np.zeros(g.shape + (3,), np.float32)
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        m = (g >= a) & (g <= b)
        t = ((g - a) / (b - a))[..., None]
        out = np.where(m[..., None], np.array(ca) * (1 - t) + np.array(cb) * t, out)
    return Image.fromarray(out.astype(np.uint8))


def warm(im):
    a = np.asarray(im.convert("RGB")).astype(np.float32)
    a = (a - 20) * 1.15
    a[..., 2] *= 0.85
    a[..., 0] *= 1.05
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def place(photo):
    """Mirror so the face looks toward the text, fill the right side, and melt its left edge into black."""
    photo = ImageOps.mirror(photo)
    s = H / photo.height * 1.08
    photo = photo.resize((int(photo.width * s), int(photo.height * s)), Image.LANCZOS)
    canvas = np.zeros((H, W, 3), np.float32) + np.array([4, 2, 3])
    x0, y0 = W - photo.width, (H - photo.height) // 2
    p = np.asarray(photo).astype(np.float32)
    xs = np.arange(photo.width)[None, :, None] / photo.width
    fade = np.clip((xs - 0.04) / 0.5, 0, 1)
    fade = fade * fade * (3 - 2 * fade)   # smoothstep: no visible seam
    ys, xs0 = max(0, -y0), max(0, -x0)
    region = p[ys:ys + H, xs0:xs0 + W] * fade[:, xs0:xs0 + W]
    cy, cx = max(0, y0), max(0, x0)
    canvas[cy:cy + region.shape[0], cx:cx + region.shape[1]] = (
        canvas[cy:cy + region.shape[0], cx:cx + region.shape[1]] * (1 - fade[:, xs0:xs0 + W]) + region)
    return canvas


def finish(a, who, mins, out, glow_xy=(900, 300)):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    gx, gy = glow_xy
    r = np.hypot(x - gx, y - gy)
    a = a + np.array([255, 150, 40]) * (np.exp(-(r / 380) ** 1.5) * 0.35)[..., None]
    rng = np.random.default_rng(7)
    for _ in range(260):   # drifting gold dust
        px, py = rng.uniform(300, W), rng.uniform(0, H)
        s = rng.uniform(1, 3)
        b = rng.uniform(80, 255) * np.exp(-np.hypot(px - gx, py - gy) / 600)
        y0, y1, x0, x1 = int(max(0, py - 6)), int(min(H, py + 7)), int(max(0, px - 6)), int(min(W, px + 7))
        yy, xx = np.mgrid[y0:y1, x0:x1]
        a[y0:y1, x0:x1] += (np.exp(-((xx - px) ** 2 + (yy - py) ** 2) / (s * s)) * b)[..., None] * np.array([1, .75, .4])
    a *= (1 - 0.7 * np.clip((0.48 - x / W) / 0.48, 0, 1) ** 1.1)[..., None]
    a *= (1 - 0.5 * np.clip((np.hypot(x / W - 0.6, y / H - 0.5) - 0.45) / 0.45, 0, 1))[..., None]
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im, "RGBA")
    d.text((64, 82), "BECOME", font=F_BIG, fill=(0, 0, 0, 210))
    d.text((58, 76), "BECOME", font=F_BIG, fill=(255, 250, 240))
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).text((44, 160), who, font=F_HUGE, fill=255)
    im.paste(Image.new("RGB", (W, H), (255, 140, 20)), (0, 0),
             mask.filter(ImageFilter.GaussianBlur(20)).point(lambda v: int(v * 0.75)))
    im.paste(Image.new("RGB", (W, H), (0, 0, 0)), (6, 8), mask.point(lambda v: int(v * 0.85)))
    bb = mask.getbbox()
    t = np.clip((np.arange(H) - bb[1]) / (bb[3] - bb[1]), 0, 1)[:, None, None]
    grad = (np.array([255, 238, 175]) * (1 - t) + np.array([235, 135, 25]) * t) * np.ones((1, W, 1))
    im.paste(Image.fromarray(grad.astype(np.uint8)), (0, 0), mask)
    d = ImageDraw.Draw(im, "RGBA")
    txt = "IN YOUR SLEEP"
    tw = F_PILL.getlength(txt)
    px, py = 60, 450
    d.rounded_rectangle((px, py, px + tw + 52, py + 80), radius=16, fill=(255, 198, 92))
    d.text((px + 26, py + 40), txt, font=F_PILL, fill=(14, 8, 4), anchor="lm")
    d.text((64, 570), f"WIM HOF  +  THETA  ·  {mins}", font=F_BADGE, fill=(255, 230, 200, 235))
    im.save(out, quality=93)
    return im


if __name__ == "__main__":
    photos = Path(sys.argv[1])
    finish(place(duotone(Image.open(photos / "pexels-3031397.jpg"))), "HIM", "45 MIN", OUT / "thumbnail-men.jpg")
    finish(place(warm(Image.open(photos / "pexels-11582029.jpg"))), "HER", "44 MIN", OUT / "thumbnail-women.jpg")
