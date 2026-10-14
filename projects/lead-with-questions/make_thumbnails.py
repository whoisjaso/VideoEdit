"""Thumbnails per spec §12.9: night = lantern glow on near-black + LEAD WITH QUESTIONS / NIGHT;
morning = sun disc on the dawn gradient + ASK FIRST / MORNING. 1280x720 and 1080x1920. No hype words.

    python projects/lead-with-questions/make_thumbnails.py
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE / "upload"
ARCH = str(HERE / "fonts/ArchivoBlack-Regular.ttf")
INTER = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
INTER_L = "/usr/share/fonts/opentype/inter/Inter-Light.otf"


def glow(W, H, x, y, s, col, amp):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    g = np.exp(-((xx - x) ** 2 + (yy - y) ** 2) / (2 * s * s))
    return g[..., None] * np.array(col, np.float32) * amp


def text_center(d, W, y, text, font, fill, track=0.0, x=None):
    widths = [d.textlength(c, font=font) for c in text]
    tw = sum(widths) + font.size * track * (len(text) - 1)
    cx = (W - tw) / 2 if x is None else x
    for c, w in zip(text, widths):
        d.text((cx, y), c, font=font, fill=fill)
        cx += w + font.size * track


def night(W, H):
    yy = np.linspace(0, 1, H)[:, None, None]
    img = np.array([3, 4, 9], np.float32) * (0.7 + 0.3 * yy) + np.zeros((H, W, 3), np.float32)
    vert = H > W
    gx, gy = (W * 0.5, H * 0.36) if vert else (W * 0.72, H * 0.5)
    img += glow(W, H, gx, gy, min(W, H) * 0.30, (156, 107, 60), 0.75)
    img += glow(W, H, gx, gy, min(W, H) * 0.06, (230, 170, 100), 0.6)
    rng = np.random.default_rng(4)
    for _ in range(160):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        img += glow(W, H, x, y, rng.uniform(1, 2.5), (156, 107, 60), rng.uniform(0.1, 0.4)) if rng.random() < 0.0 else 0
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    for _ in range(120):
        x, y, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(1, 2.2)
        a = int(rng.uniform(40, 110))
        d.ellipse((x - r, y - r, x + r, y + r), fill=(156 * a // 255 + 10, 107 * a // 255 + 8, 60 * a // 255 + 6))
    cream = (236, 226, 206)
    if vert:
        f = ImageFont.truetype(ARCH, 150)
        for i, ln in enumerate(["LEAD", "WITH", "QUESTIONS"]):
            text_center(d, W, H * 0.58 + i * 165, ln, f, cream)
        text_center(d, W, H * 0.58 + 3 * 165 + 30, "NIGHT", ImageFont.truetype(INTER_L, 64), (140, 147, 163), track=0.3)
    else:
        f = ImageFont.truetype(ARCH, 104)
        for i, ln in enumerate(["LEAD WITH", "QUESTIONS"]):
            d.text((W * 0.07, H * 0.26 + i * 120), ln, font=f, fill=cream)
        sm = ImageFont.truetype(INTER_L, 44)
        text_center(d, W, H * 0.26 + 2 * 120 + 30, "NIGHT", sm, (140, 147, 163), track=0.3, x=W * 0.072)
    return im


def morning(W, H):
    yy = np.linspace(0, 1, H)[:, None, None]
    top = np.array([58, 74, 92], np.float32) * 1.6
    bot = np.array([242, 181, 68], np.float32)
    img = top * (1 - yy) + bot * yy + np.zeros((H, W, 3), np.float32)
    vert = H > W
    sx, sy = (W * 0.5, H * 0.3) if vert else (W * 0.74, H * 0.55)
    img += glow(W, H, sx, sy, min(W, H) * 0.35, (255, 200, 120), 0.55)
    yy2, xx2 = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt((xx2 - sx) ** 2 + (yy2 - sy) ** 2)
    R = min(W, H) * 0.11
    disc = 1 / (1 + np.exp((r - R) / 2.0))
    img = img * (1 - disc[..., None]) + np.array([250, 243, 227], np.float32) * disc[..., None]
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    ink = (17, 18, 20)
    if vert:
        f = ImageFont.truetype(ARCH, 190)
        text_center(d, W, H * 0.55, "ASK", f, ink)
        text_center(d, W, H * 0.55 + 205, "FIRST", f, ink)
        text_center(d, W, H * 0.55 + 440, "MORNING", ImageFont.truetype(INTER, 60), (58, 74, 92), track=0.3)
    else:
        f = ImageFont.truetype(ARCH, 150)
        d.text((W * 0.07, H * 0.22), "ASK", font=f, fill=ink)
        d.text((W * 0.07, H * 0.22 + 165), "FIRST", font=f, fill=ink)
        text_center(d, W, H * 0.22 + 360, "MORNING", ImageFont.truetype(INTER, 44), (58, 74, 92), track=0.3, x=W * 0.075)
    return im


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    night(1280, 720).save(OUT / "thumbnail-night-16x9.jpg", quality=92)
    night(1080, 1920).save(OUT / "thumbnail-night-9x16.jpg", quality=92)
    morning(1280, 720).save(OUT / "thumbnail-morning-16x9.jpg", quality=92)
    morning(1080, 1920).save(OUT / "thumbnail-morning-9x16.jpg", quality=92)
    print("ok")
