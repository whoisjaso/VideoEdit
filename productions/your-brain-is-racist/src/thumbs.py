"""Three thumbnails, each at 1280x720 and 1080x1350. System face only. No arrows, circles or red."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import skia
from gfx import *; import plates as P
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def base(W, H, plate=None, **kw):
    out = skia.Surface(W, H); c = out.getCanvas(); c.clear(col(BLACK))
    if plate:
        s = skia.Surface(W // 2, H // 2); pc = s.getCanvas(); pc.scale(0.5, 0.5); plate(pc, W, H, **kw)
        c.drawImageRect(s.makeImageSnapshot(), skia.Rect.MakeWH(W // 2, H // 2), skia.Rect.MakeWH(W, H), skia.SamplingOptions(skia.CubicResampler.Mitchell()))
    return out, c
def done(out, c, W, H, name):
    Grain(W, H).draw(c, 0); out.makeImageSnapshot().save(f"{ROOT}/thumbnails/{name}_{W}x{H}.png", skia.kPNG)
for W, H in ((1280, 720), (1080, 1350)):
    tall = H > W; u = W / 1280 if not tall else W / 1080
    out, c = base(W, H); sz = (98 if not tall else 92) * u                       # 1: the hook, no image
    draw_text(c, "Your brain is racist.", W / 2, H / 2 - sz * 0.2, sz, 600); draw_text(c, "So is mine.", W / 2, H / 2 + sz * 1.08, sz, 600)
    done(out, c, W, H, "01_hook")
    out, c = base(W, H, P.eye, t=1.0, pupil=0.4, amber=1.0, push=0.3)             # 2: the amber eye
    sz = (96 if not tall else 110) * u; y = H * (0.9 if not tall else 0.9)
    linear(c, skia.Rect.MakeLTRB(0, H * 0.62, W, H), (0, H * 0.62), (0, H), [col((0, 0, 0), 0), col((0, 0, 0), 0.82)])
    draw_text(c, "the script.", W * 0.06, y, sz, 600, WHITE, align="left")
    done(out, c, W, H, "02_the_script")
    out, c = base(W, H, P.stop_split, t=0.12)                                     # 3: two points of view, no faces
    p0, p1 = ((W / 2, 0), (W / 2, H)) if not tall else ((0, H / 2), (W, H / 2))
    c.drawLine(*p0, *p1, paint(AMBER, 0.5, stroke=26 * u, blur=16 * u, blend=skia.BlendMode.kPlus)); c.drawLine(*p0, *p1, paint(AMBER, 1, stroke=5 * u, cap=False))
    sz = (104 if not tall else 118) * u
    if not tall:
        linear(c, skia.Rect.MakeLTRB(0, 0, W, H * 0.4), (0, 0), (0, H * 0.4), [col((0, 0, 0), 0.8), col((0, 0, 0), 0)])
        draw_text(c, "two scripts.", W * 0.05, H * 0.2, sz, 600, WHITE, align="left")
    else:
        draw_text(c, "two scripts.", W / 2, H * 0.455, sz, 600, (0, 0, 0), 0.7, blur=14); draw_text(c, "two scripts.", W / 2, H * 0.455, sz, 600, WHITE)
    done(out, c, W, H, "03_two_scripts")
print("ok")
