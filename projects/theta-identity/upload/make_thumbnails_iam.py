"""I AM thumbnails: forest green and gold. A face that means it on the right, I AM on the left.

    python projects/theta-identity/upload/make_thumbnails_iam.py PHOTO_DIR

PHOTO_DIR holds two free Pexels photos (Pexels License: free for commercial use, no attribution):
  pexels-7974957.jpg   man with a gold chain, eyes on camera   https://www.pexels.com/photo/7974957/
  pexels-7615245.jpg   woman in profile, gold chain           https://www.pexels.com/photo/7615245/
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
W, H = 1280, 720
K = ROOT / "kairos/assets/fonts"
F_IAM = ImageFont.truetype(str(K / "Montserrat-ExtraBold.ttf"), 250)
F_SUB = ImageFont.truetype(str(K / "Montserrat-ExtraBold.ttf"), 66)
F_PILL = ImageFont.truetype(str(K / "Montserrat-ExtraBold.ttf"), 44)
F_BADGE = ImageFont.truetype(str(K / "Montserrat-SemiBold.ttf"), 28)
GREEN_DEEP = np.array([4, 16, 10], np.float32)


def grade(im):
    """Split-tone: shadows sink into forest green, highlights and the gold stay warm."""
    a = np.asarray(im.convert("RGB")).astype(np.float32) / 255
    lum = (a * [0.3, 0.59, 0.11]).sum(-1, keepdims=True)
    shadow = np.array([0.05, 0.22, 0.13]) * (1 - lum) ** 2
    warm = np.array([1.06, 0.98, 0.82])
    out = (a * warm) * (0.35 + 0.85 * lum) + shadow
    out = np.clip((out - 0.03) * 1.18, 0, 1)
    return Image.fromarray((out * 255).astype(np.uint8))


def place(photo, mirror, zoom=1.12, shift_y=0.0):
    if mirror:
        photo = ImageOps.mirror(photo)
    s = H / photo.height * zoom
    photo = photo.resize((int(photo.width * s), int(photo.height * s)), Image.LANCZOS)
    canvas = np.zeros((H, W, 3), np.float32) + GREEN_DEEP
    x0 = W - photo.width + int(photo.width * 0.05)
    y0 = int((H - photo.height) / 2 + shift_y * H)
    p = np.asarray(photo).astype(np.float32)
    xs = np.arange(photo.width)[None, :, None] / photo.width
    fade = np.clip((xs - 0.02) / 0.45, 0, 1)
    fade = fade * fade * (3 - 2 * fade)
    ys0, xs0 = max(0, -y0), max(0, -x0)
    cy, cx = max(0, y0), max(0, x0)
    hh = min(H - cy, photo.height - ys0)
    ww = min(W - cx, photo.width - xs0)
    f = fade[:, xs0:xs0 + ww]
    canvas[cy:cy + hh, cx:cx + ww] = canvas[cy:cy + hh, cx:cx + ww] * (1 - f) + p[ys0:ys0 + hh, xs0:xs0 + ww] * f
    return canvas


def finish(a, mins, out):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.hypot(x - 880, y - 360)
    a = a + np.array([40, 120, 70]) * (np.exp(-(r / 520) ** 1.4) * 0.18)[..., None]   # green aura
    rng = np.random.default_rng(11)
    for _ in range(180):   # gold dust
        px, py = rng.uniform(250, W), rng.uniform(0, H)
        s, b = rng.uniform(1, 2.6), rng.uniform(60, 220)
        y0, y1, x0, x1 = int(max(0, py - 5)), int(min(H, py + 6)), int(max(0, px - 5)), int(min(W, px + 6))
        yy, xx = np.mgrid[y0:y1, x0:x1]
        a[y0:y1, x0:x1] += (np.exp(-((xx - px) ** 2 + (yy - py) ** 2) / (s * s)) * b)[..., None] * np.array([1, .78, .35])
    a *= (1 - 0.72 * np.clip((0.5 - x / W) / 0.5, 0, 1) ** 1.1)[..., None]
    a *= (1 - 0.55 * np.clip((0.32 - y / H) / 0.32, 0, 1) ** 1.3)[..., None]   # sink the bright sky behind him
    a *= (1 - 0.45 * np.clip((np.hypot(x / W - 0.6, y / H - 0.5) - 0.45) / 0.45, 0, 1))[..., None]
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

    # I AM in gold, with glow and a hard shadow
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).text((48, 70), "I AM", font=F_IAM, fill=255)
    im.paste(Image.new("RGB", (W, H), (230, 160, 40)), (0, 0),
             mask.filter(ImageFilter.GaussianBlur(22)).point(lambda v: int(v * 0.7)))
    im.paste(Image.new("RGB", (W, H), (0, 0, 0)), (6, 8), mask.point(lambda v: int(v * 0.85)))
    bb = mask.getbbox()
    t = np.clip((np.arange(H) - bb[1]) / (bb[3] - bb[1]), 0, 1)[:, None, None]
    grad = (np.array([255, 236, 170]) * (1 - t) + np.array([214, 150, 40]) * t) * np.ones((1, W, 1))
    im.paste(Image.fromarray(grad.astype(np.uint8)), (0, 0), mask)

    d = ImageDraw.Draw(im, "RGBA")
    d.text((60, 352), "MY WORD IS LAW", font=F_SUB, fill=(0, 0, 0, 200))
    d.text((56, 346), "MY WORD IS LAW", font=F_SUB, fill=(250, 246, 236))
    txt = "NO PUMP FAKES"
    tw = F_PILL.getlength(txt)
    px, py = 58, 456
    d.rounded_rectangle((px, py, px + tw + 48, py + 74), radius=14, fill=(232, 186, 96))
    d.text((px + 24, py + 37), txt, font=F_PILL, fill=(6, 22, 14), anchor="lm")
    d.text((62, 568), f"WIM HOF  +  THETA  ·  {mins}", font=F_BADGE, fill=(230, 240, 228, 235))
    im.save(out, quality=93)
    return im


if __name__ == "__main__":
    photos = Path(sys.argv[1])
    finish(place(grade(Image.open(photos / "pexels-7974957.jpg")), mirror=False, zoom=1.05),
           "38 MIN", OUT / "thumbnail-iam-men.jpg")
    finish(place(grade(Image.open(photos / "pexels-7615245.jpg")), mirror=True, zoom=1.1),
           "37 MIN", OUT / "thumbnail-iam-women.jpg")
