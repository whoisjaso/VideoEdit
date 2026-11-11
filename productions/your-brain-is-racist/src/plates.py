"""Procedural plates. Every plate is drawn at half resolution and scaled up, which gives
the soft, shallow-focus look of a lens instead of the hard edge of an illustration.

No plate contains a face. People are backlit outlines, seen from behind, or out of focus.
Each function takes the canvas already scaled so it can draw in full-frame pixels.
"""
import math, random
import skia
from gfx import *
import stick as K

PLUS = skia.BlendMode.kPlus
import os as _os
AVATAR = skia.Image.open(_os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), 'brand', 'jason-avatar.png'))   # Jason: the character and the narrator

# ------------------------------------------------------------------ the eye (#2, #26)
def eye(c, W, H, t, pupil=0.36, push=0.0, amber=0.0, lum=1.0):
    m = min(W, H); Ri = 0.43 * m
    ex = W / 2 + noise1(t * 0.9, 3) * 5; ey = H / 2 + noise1(t * 0.7, 4) * 4
    s = 1.0 + 0.09 * push
    c.save(); c.translate(W / 2, H / 2); c.scale(s, s); c.translate(-W / 2, -H / 2)
    # skin
    sh = skia.GradientShader.MakeRadial((ex, ey), 1.5 * m, [col((58, 44, 38)), col((26, 20, 18)), col((7, 6, 6))], [0, 0.45, 1])
    c.drawRect(skia.Rect.MakeLTRB(-W, -H, 2 * W, 2 * H), skia.Paint(Shader=sh))
    # the opening between the lids
    lid = skia.Path(); L = ex - 2.5 * Ri; Rr = ex + 2.5 * Ri
    lid.moveTo(L, ey + 0.16 * Ri)
    lid.cubicTo(ex - 1.3 * Ri, ey - 1.02 * Ri, ex + 0.9 * Ri, ey - 1.12 * Ri, Rr, ey - 0.02 * Ri)
    lid.cubicTo(ex + 1.1 * Ri, ey + 1.02 * Ri, ex - 1.0 * Ri, ey + 1.08 * Ri, L, ey + 0.16 * Ri)
    c.save(); c.clipPath(lid, True)
    sh = skia.GradientShader.MakeRadial((ex, ey), 2.4 * Ri, [col((150, 138, 128)), col((96, 84, 78)), col((40, 32, 30))], [0, 0.55, 1])
    c.drawRect(skia.Rect.MakeLTRB(-W, -H, 2 * W, 2 * H), skia.Paint(Shader=sh))
    # iris
    sh = skia.GradientShader.MakeRadial((ex, ey), Ri,
        [col((122, 104, 78)), col((92, 92, 82)), col((58, 70, 72)), col((30, 38, 42)), col((10, 12, 14))], [0, 0.34, 0.66, 0.9, 1.0])
    c.drawCircle(ex, ey, Ri, skia.Paint(AntiAlias=True, Shader=sh))
    rp = pupil * Ri * (1 + 0.012 * noise1(t * 2.3, 9))
    rng = random.Random(11)
    for i in range(260):                               # radial fibres
        a = rng.uniform(0, math.tau); r0 = rp * rng.uniform(1.0, 1.25); r1 = Ri * rng.uniform(0.55, 0.97)
        if r1 <= r0: continue
        wob = rng.uniform(-0.05, 0.05); light = rng.random() < 0.62
        p = skia.Path(); p.moveTo(ex + math.cos(a) * r0, ey + math.sin(a) * r0)
        mid = (r0 + r1) / 2
        p.quadTo(ex + math.cos(a + wob) * mid, ey + math.sin(a + wob) * mid, ex + math.cos(a) * r1, ey + math.sin(a) * r1)
        c.drawPath(p, paint((214, 206, 186) if light else (12, 14, 16), rng.uniform(0.05, 0.2) if light else rng.uniform(0.1, 0.3),
                            blur=1.2, stroke=rng.uniform(1.2, 3.6)))
    c.drawCircle(ex, ey, rp * 1.5, paint((150, 120, 70), 0.16, blur=rp * 0.3, stroke=rp * 0.35))   # collarette
    c.drawCircle(ex, ey, Ri, paint((6, 8, 10), 0.75, blur=6, stroke=Ri * 0.07))                    # limbal ring
    c.drawCircle(ex, ey, rp, paint((2, 2, 3), 1.0, blur=3.5))                                       # pupil
    # shadow of the upper lid across the iris
    linear(c, skia.Rect.MakeLTRB(-W, -H, 2 * W, ey), (0, ey - 1.15 * Ri), (0, ey - 0.25 * Ri), [col((0, 0, 0), 0.85), col((0, 0, 0), 0)])
    # window reflection
    c.save(); c.translate(ex - 0.36 * Ri, ey - 0.34 * Ri); c.rotate(-9)
    hl = mix((236, 240, 244), AMBER, amber)
    rrect(c, -0.13 * Ri, -0.17 * Ri, 0.26 * Ri, 0.3 * Ri, 0.03 * Ri, paint(hl, 0.82 * lum, blur=2.4))
    c.drawLine(0, -0.17 * Ri, 0, 0.13 * Ri, paint((20, 22, 26), 0.55, stroke=0.016 * Ri))
    c.restore()
    glow(c, ex + 0.3 * Ri, ey + 0.36 * Ri, 0.2 * Ri, hl, 0.16 * lum)
    c.restore()
    # lashes, soft
    rng = random.Random(5)
    for i in range(54):
        u = i / 53; bx = lerp(L + 0.4 * Ri, Rr - 0.5 * Ri, u)
        by = ey - (1.0 - (2 * u - 1) ** 2 * 0.9) * 0.83 * Ri - 0.03 * Ri
        ln = Ri * rng.uniform(0.14, 0.3); ang = math.radians(lerp(-125, -55, u) + rng.uniform(-8, 8))
        p = skia.Path(); p.moveTo(bx, by + 0.06 * Ri)
        p.quadTo(bx + math.cos(ang) * ln * 0.5, by + math.sin(ang) * ln * 0.2, bx + math.cos(ang) * ln, by + math.sin(ang) * ln)
        c.drawPath(p, paint((8, 6, 6), 0.5, blur=4.5, stroke=rng.uniform(4, 8)))
    c.drawPath(lid, paint((6, 5, 5), 0.6, blur=10, stroke=0.1 * Ri))
    c.restore()
    if amber > 0.01:                                    # regrade: amber is the only light
        p = skia.Paint(Color=col(AMBER, amber * 0.92)); p.setBlendMode(skia.BlendMode.kColor); c.drawRect(skia.Rect.MakeWH(W, H), p)
        p = skia.Paint(Color=col((255, 214, 150), amber * 0.10)); p.setBlendMode(skia.BlendMode.kOverlay); c.drawRect(skia.Rect.MakeWH(W, H), p)
    vignette(c, W, H, 0.92, 0.22)
    if lum < 1: c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Color=col((0, 0, 0), 1 - lum)))

# ------------------------------------------------------------------ stacked screens (#3, #19, #28)
_SCR = None
def _screens(n=150):
    global _SCR
    if _SCR is None:
        rng = random.Random(21); _SCR = []
        for i in range(n):
            ph = rng.random() < 0.34
            _SCR.append(dict(x=rng.uniform(-1, 1) * (1.6 + 3.4 * rng.random()), y=rng.uniform(-1, 1) * 2.4, z=rng.uniform(2.0, 26.0),
                             phone=ph, w=rng.uniform(0.5, 0.85) if not ph else rng.uniform(0.2, 0.28),
                             tint=rng.choice([(150, 172, 200), (176, 186, 198), (198, 180, 156), (140, 160, 186), (190, 190, 196)]),
                             born=rng.random(), die=rng.random(), ph=rng.uniform(0, 100), rot=rng.uniform(-5, 5),
                             blobs=[(rng.uniform(-0.3, 0.3), rng.uniform(-0.25, 0.25), rng.uniform(0.25, 0.5)) for _ in range(2)]))
        _SCR.sort(key=lambda s: -s["z"])
    return _SCR

def screens(c, W, H, t, grow=1.0, dolly=0.0, dark=0.0, warm=0.0, lum=1.0):
    """grow 0..1: how much of the stack exists. dark 0..1: screens switching off. warm: the one light."""
    c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Color=col((4, 4, 6))))
    f = 0.9 * max(W, H) if W > H else 1.25 * W
    zc = -0.5 - 5.0 * dolly; cx, cy = W / 2, H / 2
    ysq = 1.0 if W > H else 1.9
    for i, s in enumerate(_screens()):
        b = ramp(grow, s["born"] * 0.92, s["born"] * 0.92 + 0.08)
        if b <= 0: continue
        off = ramp(dark, s["die"] * 0.9, s["die"] * 0.9 + 0.1)
        d = s["z"] - zc
        if d < 1.2: continue
        k = f / d; x = cx + s["x"] * k * 1.15; y = cy + s["y"] * k * 0.62 * ysq
        w = s["w"] * k; h = w * (0.6 if not s["phone"] else 2.05)
        if x + w < 0 or x - w > W or y + h < 0 or y - h > H: continue
        fl = 0.72 + 0.28 * noise1(t * 5.5 + s["ph"], i)
        depth = clamp(1.3 - d / 32.0) ** 1.3
        a = b * depth * fl * (1 - off) * lum
        tint = s["tint"]
        c.save(); c.translate(x, y); c.rotate(s["rot"])
        if a > 0.01:
            glow(c, 0, 0, w * 1.25, tint, 0.20 * a, sx=1.0, sy=max(0.6, h / w))
            rrect(c, -w / 2, -h / 2, w, h, w * 0.035, paint(tint, 0.34 * a, blur=max(0.6, 26.0 / d)))
            for bx, by, br in s["blobs"]:
                glow(c, bx * w + noise1(t * 0.4 + s["ph"], 5) * w * 0.12, by * h, br * w, (236, 238, 244), 0.22 * a, sy=0.7)
        rrect(c, -w / 2, -h / 2, w, h, w * 0.035, paint((30, 32, 38), 0.45 * b * depth * (0.25 + 0.75 * off) + 0.05 * b * depth, stroke=max(0.8, w * 0.012)))
        c.restore()
    rng = random.Random(3)                               # dust in the beam
    for i in range(70):
        dx = (rng.random() + t * 0.004 * rng.uniform(-1, 1)) % 1.0; dy = (rng.random() + t * 0.003 * rng.uniform(0.2, 1)) % 1.0
        c.drawCircle(dx * W, dy * H, rng.uniform(1.2, 3.2), paint((220, 224, 232), rng.uniform(0.04, 0.16) * lum * (1 - 0.7 * dark), blur=1.5))
    if warm > 0.005:
        glow(c, cx, cy, lerp(0.05, 0.42, warm) * max(W, H), AMBER, 0.55 * warm)
        glow(c, cx, cy, lerp(0.012, 0.07, warm) * max(W, H), (255, 226, 178), 0.9 * warm)
    vignette(c, W, H, 0.9, 0.3)

# ------------------------------------------------------------------ the room with the TV (#4, #20-22)
def tv_light(t, seed=0):
    k = 0.5 + 0.5 * noise1(t * 0.55, 40 + seed)
    base = mix((150, 176, 214), (214, 190, 160), k)
    lv = 0.74 + 0.2 * noise1(t * 6.5, 41 + seed) + 0.06 * noise1(t * 19, 42 + seed)
    return base, clamp(lv, 0.35, 1.0)

DARK_FIG = (7, 7, 9)
def _performer(act, at, t):
    """What the screen shows him. Returns pose, optional ball, bars flag."""
    if act == "rapper": return K.rapper(at), None, False
    if act == "athlete": p, ball = K.athlete(at); return p, ball, False
    if act == "dealer": return K.dealer(at), None, False
    if act == "cell": return K.cell(at), None, True
    return K.stand(t, 1.0), None, False

def room(c, W, H, t, viewer=0.15, tv="abstract", tv_scale=1.0, seed=0, act=None, act_t=0.0, prev=None, act_k=1.0, grow=0.0, mimic=0.0, echo=0.0, strings=0.0, **_):
    """A stick figure seen from behind, lit only by a screen. With tv="sil" the screen shows a stick figure performing."""
    vert = H > W
    c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Color=col((5, 5, 7))))
    tint, lv = tv_light(t, seed)
    tw = (0.36 if not vert else 0.66) * W * tv_scale; th = tw * 0.6
    tx = W * (0.5 if vert else 0.52); ty = H * 0.36
    glow(c, tx, ty, tw * 1.7, tint, 0.34 * lv); glow(c, tx, ty + th, tw * 1.3, tint, 0.12 * lv, sy=0.5)
    c.save(); c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(tx - tw / 2, ty - th / 2, tw, th), tw * 0.02, tw * 0.02), True)
    c.drawRect(skia.Rect.MakeXYWH(tx - tw / 2, ty - th / 2, tw, th), skia.Paint(Color=col(mix(tint, (255, 255, 255), 0.25), 0.9 * lv)))
    perf = None; ph = th * 0.84; pyf = ty + th / 2 - th * 0.05
    if tv == "abstract":
        for i in range(4):
            glow(c, tx + noise1(t * 0.5 + i * 7, 60 + i) * tw * 0.4, ty + noise1(t * 0.45 + i * 3, 70 + i) * th * 0.35, tw * 0.3,
                 [(255, 255, 255), (60, 80, 120), (40, 30, 30), (240, 220, 190)][i], 0.5, blend=skia.BlendMode.kSrcOver)
    else:
        glow(c, tx, ty - th * 0.05, tw * 0.55, (255, 255, 255), 0.55 * lv, blend=skia.BlendMode.kSrcOver)
        perf, ball, bars = _performer(act, act_t, t)
        if prev is not None and act_k < 1: perf = K.blend(_performer(prev, act_t + 1.0, t)[0], perf, io_cubic(act_k))
        for jn in ("head", "ha_l", "ha_r", "kn_l", "kn_r"):          # he is on strings. Everything the screen shows him is.
            jx, jy = tx + perf[jn][0] * ph, pyf - perf[jn][1] * ph
            c.drawLine(jx, jy, tx + (jx - tx) * 0.55, ty - th / 2, paint(DARK_FIG, 0.5, stroke=max(1.2, ph * 0.006)))
        K.draw(c, perf, tx, pyf, ph, a=0.98, soft=0.5, outfit="tank", t=t, dim=0.9, toon=True,
               face={"rapper": "tough", "athlete": "focus", "dealer": "shifty", "cell": "sad"}.get(act, "neutral"), look=0.2 * math.sin(t * 1.3))
        if ball is not None and act_k > 0.5: c.drawCircle(tx + ball[0] * ph, pyf - ball[1] * ph, ph * 0.045, paint(DARK_FIG, 0.95, stroke=max(2.0, ph * 0.03)))
        if bars:
            for i in range(7): bx = tx - tw * 0.36 + tw * 0.12 * i; c.drawLine(bx, ty - th / 2, bx, ty + th / 2, paint(DARK_FIG, 0.9 * io_cubic(act_k), stroke=max(2.5, tw * 0.012)))
    c.restore()
    rrect(c, tx - tw / 2, ty - th / 2, tw, th, tw * 0.02, paint((2, 2, 3), 0.9, stroke=tw * 0.012))
    linear(c, skia.Rect.MakeLTRB(0, ty + th / 2, W, H), (0, ty + th / 2), (0, H), [col(tint, 0.10 * lv), col(tint, 0.0)], blend=PLUS)
    # the couch and the one watching
    cy0 = H * (0.70 if not vert else 0.66)
    couch = skia.Path(); couch.moveTo(-40, H + 40); couch.lineTo(-40, cy0 + 30)
    couch.cubicTo(W * 0.06, cy0 - 14, W * 0.2, cy0 - 20, W * 0.5, cy0 - 20)
    couch.cubicTo(W * 0.8, cy0 - 20, W * 0.94, cy0 - 14, W + 40, cy0 + 30); couch.lineTo(W + 40, H + 40); couch.close()
    vx = W * (0.5 if vert else 0.47); vh = min(W, H) * (0.56 + (viewer - 0.13) * 2.0)
    g = io_cubic(grow)
    pose = K.blend(K.sit(t, seed), K.stand(t, seed + 2), g)
    if mimic > 0 and perf is not None: pose = K.blend(pose, perf, io_cubic(mimic))
    vy = cy0 + lerp(0.50, 0.40, g) * vh                     # where his feet would be, behind the couch
    if strings > 0.003:                                    # and now so is he: lines from the screen to his head and his hands
        for jn, sx_ in (("head", 0.0), ("ha_l", -0.34), ("ha_r", 0.34)):
            jx, jy = vx + pose[jn][0] * vh, vy - pose[jn][1] * vh
            c.drawLine(jx, jy, tx + sx_ * tw, ty + th / 2, paint((236, 234, 228), 0.55 * strings, stroke=2.2, blur=0.6))
    K.draw(c, pose, vx, vy, vh, tint, 0.6 * lv, weight=0.055, soft=3.5, glow=False)        # rim light from the screen
    K.draw(c, pose, vx, vy, vh, a=1.0, soft=0.5, toon=True, face=None, edge=None, dim=lerp(0.55, 0.95, lv))          # the back of his head, lit by the screen
    c.drawPath(couch, paint(tint, 0.3 * lv, blur=6, stroke=4))
    c.drawPath(couch, paint((9, 9, 11), 1.0, blur=1.5))
    if echo > 0.001 and perf is not None:                  # the figure on the screen steps out of it and settles onto him
        e = io_cubic(echo)
        K.draw(c, perf, lerp(tx, vx, e), lerp(pyf, vy, e), lerp(ph, vh, e), WHITE, 0.95 * min(1, echo * 4), weight=0.03, soft=0.4)
    vignette(c, W, H, 0.9, 0.3)

# ------------------------------------------------------------------ three backlit figures (#5-7)
CARD_LIGHT = {"tank": (206, 196, 176), "hat": (218, 176, 124), "suit": (172, 192, 214)}
def card_geo(W, H):
    vert = H > W; return W * 0.5, H * (0.95 if not vert else 0.86), H * (0.76 if not vert else 0.52)

def card_fig(c, W, H, t, kind, tin, push=0.0, rim=True):
    """The figure on a character card, on its own, so the film can stand him in front of the title."""
    fx, base, fh = card_geo(W, H); light = CARD_LIGHT[kind]; s = 1 + 0.03 * push
    c.save(); c.translate(W / 2, H / 2); c.scale(s, s); c.translate(-W / 2, -H / 2)
    sd = {"tank": 0.0, "hat": 2.1, "suit": 4.3}[kind]
    idle = K.stand(t, sd, pockets=False, carry=(kind == "suit"), smoke=(kind == "tank"))
    if kind == "tank": idle["el_l"], idle["ha_l"] = K._limb(idle["sh_l"], -14, K.UARM, 16, K.FARM)        # one hand in a pocket
    far = 0.95 * (1 - out_quint(ramp(tin, 0.0, 1.5)))                  # how far he still has to walk, in body heights
    pose = K.blend(K.walk_ik(-far, 1, energy=0.9), idle, io_cubic(ramp(tin, 1.0, 1.6)))
    ox = fx - far * fh
    if rim: K.draw(c, pose, ox, base, fh, light, 0.35, weight=0.07, soft=9, glow=False)
    dg = K.drag(t + sd) if kind == "tank" else 0.0
    fc_ = {"tank": K.face_blend("cool", "drag", dg * 1.4), "hat": "neutral", "suit": "smile"}[kind]
    K.draw(c, pose, ox, base, fh, a=1.0, soft=0.6 if rim else 0.0, case=(kind == "suit"), outfit=kind, t=t, smoke=(kind == "tank"), dim=0.86,
           toon=True, face=fc_, look=0.25 * math.sin(t * 0.5 + sd), edge=K.EDGE)
    c.restore()

def figure_wall(c, W, H, t, kind="tank", push=0.0, tin=9.0):
    vert = H > W
    s = 1 + 0.03 * push
    c.save(); c.translate(W / 2, H / 2); c.scale(s, s); c.translate(-W / 2, -H / 2)
    fx, base, fh = card_geo(W, H)
    light = CARD_LIGHT[kind]
    c.drawRect(skia.Rect.MakeLTRB(-W, -H, 2 * W, 2 * H), skia.Paint(Color=col((16, 15, 15))))
    rng = random.Random({"tank": 1, "hat": 2, "suit": 3}[kind])
    for i in range(26):                                   # concrete: uneven tone
        glow(c, rng.uniform(0, W), rng.uniform(0, H), rng.uniform(0.1, 0.35) * W, (58, 56, 54), rng.uniform(0.05, 0.16), blend=skia.BlendMode.kSrcOver)
    for i in range(3):                                    # form lines
        y = H * (0.2 + 0.27 * i) + rng.uniform(-20, 20)
        c.drawLine(-W, y, 2 * W, y, paint((0, 0, 0), 0.22, blur=1.5, stroke=3))
    fl = 0.94 + 0.06 * noise1(t * 3.0, 80)
    if kind == "suit":                                    # an office window behind him
        wx, wy, ww, wh = fx - fh * 0.36, base - fh * 1.08, fh * 0.72, fh * 0.8
        glow(c, fx, base - fh * 0.55, fh * 0.95, light, 0.5 * fl)
        rrect(c, wx, wy, ww, wh, 4, paint(light, 0.72 * fl, blur=5))
        for i in range(1, 3): c.drawLine(wx + ww * i / 3, wy, wx + ww * i / 3, wy + wh, paint((14, 15, 18), 0.9, blur=1.5, stroke=fh * 0.02))
        c.drawLine(wx, wy + wh * 0.45, wx + ww, wy + wh * 0.45, paint((14, 15, 18), 0.9, blur=1.5, stroke=fh * 0.02))
    else:
        glow(c, fx, base - fh * 0.58, fh * 0.9, light, 0.5 * fl)
        glow(c, fx, base - fh * 0.62, fh * 0.42, (255, 246, 228), 0.26 * fl)
    c.restore(); card_fig(c, W, H, t, kind, tin, push); c.save(); c.translate(W / 2, H / 2); c.scale(s, s); c.translate(-W / 2, -H / 2)
    linear(c, skia.Rect.MakeLTRB(-W, base - fh * 0.02, 2 * W, 2 * H), (0, base - fh * 0.02), (0, base + fh * 0.16), [col((4, 4, 5), 0), col((4, 4, 5), 0.85)])
    c.drawOval(skia.Rect.MakeLTRB(fx - fh * 0.22, base - fh * 0.012, fx + fh * 0.22, base + fh * 0.03), paint((0, 0, 0), 0.5, blur=8))
    c.restore()
    vignette(c, W, H, 0.92, 0.28)

# ------------------------------------------------------------------ the street (#9-12)
def street_geo(W, H, walk, cam_x, z, fig_x):
    """Where the walking figure is on screen (feet x, feet y, height). The film uses this to lock its brackets onto him."""
    vert = H > W; bob = math.sin(walk * 5.2) * 5.0; sway = math.sin(walk * 2.6) * 4.0
    yh = H * (0.45 if not vert else 0.44) + bob; k = (0.40 if not vert else 0.62) * W
    return W * 0.5 + sway + (fig_x - cam_x) * k / z, yh + (H - yh) / z - 0.02 * (H - yh) / z, 1.72 * k / z

def street(c, W, H, t, walk, cam_x=0.0, fig_z=None, fig_kind="tank", fig_x=0.25, props=(0, 0, 0), lum=1.0, menace=0.0, react=0.0):
    """POV at night. walk = distance walked (z units). cam_x = lateral position (0 = our sidewalk,
    about -5.4 = the far sidewalk). The approaching figure is never in focus."""
    vert = H > W
    bob = math.sin(walk * 5.2) * 5.0; sway = math.sin(walk * 2.6) * 4.0
    yh = H * (0.45 if not vert else 0.44) + bob; vx = W * 0.5 + sway
    k = (0.40 if not vert else 0.62) * W; gh = H - yh
    def px(X, z): return vx + (X - cam_x) * k / z
    def py(z): return yh + gh / z
    linear(c, skia.Rect.MakeWH(W, H), (0, 0), (0, yh), [col((4, 5, 9)), col((12, 13, 20))])
    rng = random.Random(77)
    for i in range(34):                                   # far city, out of focus
        bx = vx + (rng.uniform(-1.3, 1.3) - cam_x * 0.02) * W * 0.5; by = yh - rng.uniform(4, 0.22 * H)
        cc = rng.choice([(255, 196, 130), (255, 232, 200), (190, 210, 255), (255, 120, 90), (150, 230, 170)])
        tw = 0.75 + 0.25 * noise1(t * 1.3 + i, i)
        r = rng.uniform(5, 15)
        c.drawOval(skia.Rect.MakeLTRB(bx - r * 1.5, by - r, bx + r * 1.5, by + r), paint(cc, rng.uniform(0.1, 0.34) * tw, blur=1.6))
    # ground: road (left), our sidewalk, building line (right)
    c.drawRect(skia.Rect.MakeLTRB(0, yh, W, H), skia.Paint(Color=col((9, 9, 11))))
    def strip(X0, X1, color, a=1.0):
        p = skia.Path(); p.moveTo(px(X0, 60), py(60)); p.lineTo(px(X1, 60), py(60)); p.lineTo(px(X1, 0.55), py(0.55)); p.lineTo(px(X0, 0.55), py(0.55)); p.close()
        c.drawPath(p, paint(color, a))
    strip(-1.0, 1.7, (30, 29, 28)); strip(-7.2, -4.6, (27, 26, 26))
    strip(-1.12, -1.0, (52, 50, 47)); strip(-4.6, -4.48, (46, 44, 42))          # curbs
    strip(-2.85, -2.75, (70, 64, 44), 0.35)                                      # lane paint
    for j in range(26):                                   # slab joints coming toward us
        z = ((j * 1.15 - walk) % 30.0) + 0.6
        a = 0.26 * clamp(1.4 - z / 22)
        c.drawLine(px(-1.0, z), py(z), px(1.7, z), py(z), paint((0, 0, 0), a, stroke=max(1.0, 5.0 / z)))
        c.drawLine(px(-7.2, z), py(z), px(-4.6, z), py(z), paint((0, 0, 0), a * 0.8, stroke=max(1.0, 5.0 / z)))
    # buildings
    for side, X in ((1, 1.7), (-1, -7.2)):
        p = skia.Path(); p.moveTo(px(X, 60), py(60)); p.lineTo(px(X, 0.5), py(0.5)); p.lineTo(px(X + side * 6, 0.5), py(0.5))
        p.lineTo(px(X + side * 6, 0.5), -H); p.lineTo(px(X, 0.5), yh - 3.2 * k / 0.5); p.lineTo(px(X, 60), yh - 3.2 * k / 60); p.close()
        c.drawPath(p, paint((11, 11, 14), 1.0))
        for j in range(10):
            z = ((j * 4.3 + (3 if side < 0 else 0) - walk) % 43.0) + 1.3
            if rng.random() < 0.5: continue
            wy = yh - 1.25 * k / z; wx = px(X, z)
            c.drawOval(skia.Rect.MakeLTRB(wx - 0.3 * k / z, wy - 0.42 * k / z, wx + 0.3 * k / z, wy + 0.42 * k / z),
                       paint((224, 170, 104), 0.2 * clamp(1.6 - z / 20), blur=max(1.5, 9 / z)))
    # streetlights along both curbs
    lights = []
    for j in range(8):
        for X in (-1.25, -4.35):
            z = ((j * 6.0 + (0 if X > -2 else 3.0) - walk) % 48.0) + 0.9
            lights.append((z, X))
    for z, X in sorted(lights, reverse=True):
        lx = px(X, z); ly = yh - 2.3 * k / z; a = clamp(1.5 - z / 30) * lum
        ell = skia.Rect.MakeLTRB(px(X + 0.9, z) - 1.6 * k / z, py(z) - 0.16 * gh / z, px(X + 0.9, z) + 1.6 * k / z, py(z) + 0.16 * gh / z)
        c.drawOval(ell, paint((255, 190, 120), 0.15 * a, blur=max(3, 30 / z), blend=PLUS))
        c.drawLine(lx, ly, lx, py(z), paint((8, 8, 10), 0.9 * a, stroke=max(1.2, 0.06 * k / z)))
        r = max(4.0, 0.16 * k / z)
        glow(c, lx, ly, r * 5.5, (255, 180, 104), 0.34 * a, sx=1.7)
        c.drawOval(skia.Rect.MakeLTRB(lx - r * 1.5, ly - r, lx + r * 1.5, ly + r), paint((255, 214, 160), 0.86 * a, blur=max(1.2, r * 0.16)))
    # the other person: out of focus, an outline only
    if fig_z is not None and fig_z > 0.55:
        z = fig_z; fx = px(fig_x, z); fy = py(z) - 0.02 * gh / z; fh = 1.72 * k / z
        a = clamp(1.3 - z / 26) * lum
        suit = fig_kind == "suit"                         # two gaits: one slouched and slow, one upright and brisk
        pose = K.walk_front(t * (0.98 if suit else 0.8), energy=1.0 if suit else 0.7, slouch=0.0 if suit else 1.0, carry=suit, smoke=not suit)
        if not suit: pose["el_l"], pose["ha_l"] = K._limb(pose["sh_l"], -14, K.UARM, 16, K.FARM)
        # His shadow, thrown toward you. With menace it is not his: it is the one your script predicted. Taller, hunched, arms wide.
        sp = pose if menace <= 0.01 else K.blend(pose, K.front(arm_l=(-62, -18), arm_r=(62, 18), leg_l=(-12, -6), leg_r=(12, 6), drop=0.05, head=(0, -0.05), sh_tilt=0.0), io_cubic(menace))
        c.save(); c.translate(fx, fy); c.skew(-0.18, 0); c.scale(1.0 + 0.55 * menace, -(1.15 + 1.55 * menace))
        K.draw(c, sp, 0, 0, fh, (0, 0, 0), (0.5 + 0.3 * menace) * a, weight=0.05 + 0.03 * menace, soft=max(2.5, fh * 0.03), glow=False)
        c.restore()
        K.draw(c, pose, fx, fy, fh, (255, 196, 140), 0.45 * a, weight=0.06, soft=max(2.0, fh * 0.012), glow=False)
        fc_ = "smile" if suit else K.face_blend("cool", "hurt", react)          # he sees you cross. It lands.
        K.draw(c, pose, fx, fy, fh, a=a, soft=max(0.4, fh * 0.002), case=suit, outfit="suit" if suit else "tank", t=t, smoke=not suit, dim=0.92,
               toon=True, face=fc_, look=-0.75 * react, edge=K.EDGE)
    # what you are carrying: phone, watch, keys
    if max(props) > 0.002:
        pb = H * (1.0 if not vert else 0.90)
        ph, wa, ke = props
        hx = W * (0.80 if not vert else 0.74); hy = pb - (0.10 if not vert else 0.035) * H + bob * 1.4
        c.save(); c.translate(hx, hy); c.rotate(-13 + noise1(t * 1.4, 90) * 2)
        glow(c, 0, 0, 0.12 * W * (1 if not vert else 1.6), (170, 196, 236), 0.42 * ph)
        rrect(c, -0.032 * H, -0.068 * H, 0.064 * H, 0.136 * H, 0.008 * H, paint((6, 6, 8), ph))
        rrect(c, -0.027 * H, -0.060 * H, 0.054 * H, 0.120 * H, 0.005 * H, paint((176, 198, 232), 0.84 * ph, blur=1.2))
        c.restore()
        wx = W * (0.19 if not vert else 0.24); wy = pb - (0.075 if not vert else 0.03) * H - bob * 1.2
        glow(c, wx, wy, 0.05 * H, (220, 226, 236), 0.4 * wa)
        c.drawCircle(wx, wy, 0.024 * H, paint((10, 10, 12), wa)); c.drawCircle(wx, wy, 0.024 * H, paint((206, 210, 220), 0.75 * wa, stroke=0.004 * H))
        c.drawCircle(wx, wy, 0.012 * H, paint((150, 220, 190), 0.6 * wa, blur=1.5))
        kx = W * (0.5 if not vert else 0.5); ky = pb - (0.055 if not vert else 0.02) * H + bob
        for i in range(3):
            ang = math.radians(78 + i * 14 + math.sin(walk * 5.2 + i) * 9)
            x2 = kx + math.cos(ang) * 0.05 * H; y2 = ky + math.sin(ang) * 0.05 * H
            c.drawLine(kx, ky, x2, y2, paint((214, 204, 176), 0.8 * ke, stroke=0.006 * H, blur=0.8))
            glow(c, x2, y2, 0.02 * H, (255, 236, 200), 0.5 * ke)
        c.drawCircle(kx, ky, 0.012 * H, paint((214, 204, 176), 0.8 * ke, stroke=0.004 * H))
    vignette(c, W, H, 0.9, 0.3)
    linear(c, skia.Rect.MakeWH(W, H), (0, 0), (W, 0), [col((90, 140, 255), 0.05), col((0, 0, 0), 0), col((255, 170, 90), 0.045)], blend=PLUS)
    if lum < 1: c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Color=col((0, 0, 0), 1 - lum)))

# ------------------------------------------------------------------ the traffic stop (#14-18)
def flash(t):
    """Red and blue light bar: two quick blinks each, alternating."""
    ph = (t * 1.55) % 1.0
    def bl(p): return max(0.0, math.sin(p * math.tau * 2)) ** 1.5 if 0 <= p < 0.5 else 0.0
    return 0.18 + 0.82 * bl(ph), 0.18 + 0.82 * bl((ph + 0.5) % 1.0)

RED, BLUE = (255, 44, 40), (52, 96, 255)

def cruiser(c, pw, ph, t, tense=0.0):
    """Officer's view: a stopped sedan through the windshield. No face anywhere."""
    r, b = flash(t)
    c.drawRect(skia.Rect.MakeWH(pw, ph), skia.Paint(Color=col((5, 6, 9))))
    hz = ph * 0.47
    linear(c, skia.Rect.MakeLTRB(0, hz, pw, ph), (0, hz), (0, ph), [col((14, 14, 17)), col((26, 25, 27))])
    for i, (x, a) in enumerate(((0.12, 0.3), (0.9, 0.22), (0.72, 0.16))):
        glow(c, pw * x, hz - ph * 0.07, pw * 0.05, (255, 196, 130), a, sx=1.6)
    cw = pw * 0.44; chh = cw * 0.5; cx = pw * 0.5; cy = hz + ph * 0.06
    glow(c, cx - cw * 0.5, cy + chh * 0.5, cw * 0.9, RED, 0.36 * r); glow(c, cx + cw * 0.5, cy + chh * 0.5, cw * 0.9, BLUE, 0.4 * b)
    body = skia.Path(); body.addRoundRect(skia.Rect.MakeXYWH(cx - cw / 2, cy - chh * 0.2, cw, chh * 0.7), cw * 0.05, cw * 0.05)
    roof = skia.Path(); roof.moveTo(cx - cw * 0.36, cy - chh * 0.18); roof.lineTo(cx - cw * 0.27, cy - chh * 0.62)
    roof.lineTo(cx + cw * 0.27, cy - chh * 0.62); roof.lineTo(cx + cw * 0.36, cy - chh * 0.18); roof.close()
    c.drawPath(roof, paint((10, 11, 14), 1, blur=1.5)); c.drawPath(body, paint((13, 14, 17), 1, blur=1.5))
    win = skia.Path(); win.moveTo(cx - cw * 0.31, cy - chh * 0.22); win.lineTo(cx - cw * 0.24, cy - chh * 0.55)
    win.lineTo(cx + cw * 0.24, cy - chh * 0.55); win.lineTo(cx + cw * 0.31, cy - chh * 0.22); win.close()
    c.drawPath(win, paint(mix(RED, BLUE, 0.5), 0.08 + 0.1 * max(r, b), blur=2))
    c.drawPath(bust_path(cx - cw * 0.13, cy - chh * 0.2, cw * 0.17), paint((3, 3, 4), 0.95, blur=3))     # a head rest and a head: outline only
    for sx in (-1, 1):
        lx = cx + sx * cw * 0.39; ly = cy + chh * 0.02
        glow(c, lx, ly, cw * 0.2, (255, 30, 24), 0.75); rrect(c, lx - cw * 0.07, ly - chh * 0.07, cw * 0.14, chh * 0.14, 4, paint((255, 80, 60), 0.95, blur=2.5))
    linear(c, skia.Rect.MakeLTRB(0, cy + chh * 0.5, pw, ph), (0, cy + chh * 0.5), (0, ph), [col(RED, 0.12 * r), col(RED, 0)], blend=PLUS)
    # hood, dash, pillar, mirror
    hood = skia.Path(); hood.moveTo(-20, ph + 20); hood.lineTo(-20, ph * 0.78)
    hood.cubicTo(pw * 0.3, ph * 0.71, pw * 0.7, ph * 0.71, pw + 20, ph * 0.78); hood.lineTo(pw + 20, ph + 20); hood.close()
    c.drawPath(hood, paint(mix(RED, BLUE, b / (r + b + 1e-6)), 0.4 * max(r, b), blur=10, stroke=8))
    c.drawPath(hood, paint((8, 8, 10), 1, blur=2))
    dash = skia.Path(); dash.moveTo(-20, ph + 20); dash.lineTo(-20, ph * 0.87)
    dash.cubicTo(pw * 0.3, ph * 0.83, pw * 0.7, ph * 0.84, pw + 20, ph * 0.88); dash.lineTo(pw + 20, ph + 20); dash.close()
    c.drawPath(dash, paint((3, 3, 4), 1, blur=2))
    for i, (x, cc) in enumerate(((0.3, (120, 230, 160)), (0.34, (255, 180, 80)), (0.38, (120, 230, 160)), (0.62, (200, 220, 255)))):
        glow(c, pw * x, ph * 0.925, pw * 0.012, cc, 0.5 + 0.2 * noise1(t * 3 + i, i))
    pil = skia.Path(); pil.moveTo(-20, -20); pil.lineTo(pw * 0.10, -20); pil.lineTo(pw * 0.02, ph + 20); pil.lineTo(-20, ph + 20); pil.close()
    c.drawPath(pil, paint((2, 2, 3), 1, blur=5))
    rrect(c, pw * 0.4, -ph * 0.02, pw * 0.2, ph * 0.075, 10, paint((2, 2, 3), 1, blur=3))
    # forearm and hand resting low, toward the belt
    arm = skia.Path(); arm.moveTo(pw * 1.06, ph * 1.04); arm.quadTo(pw * 0.9, ph * 0.985, pw * (0.80 - 0.012 * tense), ph * (0.955 + 0.01 * tense))
    c.drawPath(arm, paint(mix(RED, BLUE, b / (r + b + 1e-6)), 0.24 * max(r, b) + 0.2 * tense, blur=7, stroke=ph * 0.085))
    c.drawPath(arm, paint((12, 11, 12), 1, blur=3, stroke=ph * 0.075))
    vignette(c, pw, ph, 0.9, 0.3)

def sedan(c, pw, ph, t, tense=0.0):
    """Driver's view: mirror full of red and blue, hands on the wheel. No face anywhere."""
    r, b = flash(t + 0.21)
    c.drawRect(skia.Rect.MakeWH(pw, ph), skia.Paint(Color=col((6, 6, 8))))
    hz = ph * 0.5
    linear(c, skia.Rect.MakeLTRB(0, hz, pw, ph), (0, hz), (0, ph), [col((12, 12, 14)), col((22, 21, 23))])
    for i, (x, a) in enumerate(((0.2, 0.26), (0.66, 0.2), (0.86, 0.3))):
        glow(c, pw * x, hz - ph * 0.06, pw * 0.045, (255, 196, 130), a, sx=1.6)
    glow(c, pw * 0.08, ph * 0.1, pw * 0.5, RED, 0.2 * r); glow(c, pw * 0.92, ph * 0.1, pw * 0.5, BLUE, 0.24 * b)
    # the mirror
    mw = pw * 0.5; mh = mw * 0.3; mx = pw * 0.5; my = ph * 0.2
    c.drawLine(mx, -10, mx, my - mh / 2, paint((2, 2, 3), 1, stroke=mw * 0.07))
    rrect(c, mx - mw / 2 - 8, my - mh / 2 - 8, mw + 16, mh + 16, mh * 0.34, paint((2, 2, 3), 1, blur=2))
    c.save(); c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(mx - mw / 2, my - mh / 2, mw, mh), mh * 0.3, mh * 0.3), True)
    c.drawRect(skia.Rect.MakeXYWH(mx - mw / 2, my - mh / 2, mw, mh), skia.Paint(Color=col((10, 10, 14))))
    for i in range(5):
        fx = mx + (i - 2) * mw * 0.13
        glow(c, fx, my - mh * 0.12, mh * 0.5, RED if i % 2 == 0 else BLUE, 0.95 * (r if i % 2 == 0 else b))
    glow(c, mx - mw * 0.2, my + mh * 0.2, mh * 0.34, (255, 250, 236), 0.8); glow(c, mx + mw * 0.2, my + mh * 0.2, mh * 0.34, (255, 250, 236), 0.8)
    c.restore()
    glow(c, mx, my, mw * 0.8, RED, 0.16 * r); glow(c, mx, my, mw * 0.8, BLUE, 0.2 * b)
    # dash and wheel
    dash = skia.Path(); dash.moveTo(-20, ph + 20); dash.lineTo(-20, ph * 0.74)
    dash.cubicTo(pw * 0.3, ph * 0.69, pw * 0.7, ph * 0.69, pw + 20, ph * 0.74); dash.lineTo(pw + 20, ph + 20); dash.close()
    c.drawPath(dash, paint(mix(RED, BLUE, b / (r + b + 1e-6)), 0.3 * max(r, b), blur=10, stroke=7))
    c.drawPath(dash, paint((5, 5, 6), 1, blur=2))
    wr = pw * 0.36; wx = pw * 0.5; wy = ph * 0.74 + wr * 0.72
    c.drawCircle(wx, wy, wr, paint(mix(RED, BLUE, b / (r + b + 1e-6)), 0.34 * max(r, b), blur=8, stroke=wr * 0.17))
    c.drawCircle(wx, wy, wr, paint((24, 24, 28), 1, blur=2, stroke=wr * 0.15))
    for sgn, seed in ((-1, 1), (1, 2)):                    # hands at ten and two; they fidget as he tenses
        fid = tense * (noise1(t * 3.1, seed) * 0.12 + noise1(t * 7.3, seed + 5) * 0.05)
        ang = math.radians(-90 + sgn * (47 + fid * 60))
        hx = wx + math.cos(ang) * wr; hy = wy + math.sin(ang) * wr - tense * wr * 0.03
        c.save(); c.translate(hx, hy); c.rotate(math.degrees(ang) + 90)
        ov = skia.Rect.MakeLTRB(-wr * 0.17, -wr * 0.135, wr * 0.17, wr * 0.135)
        c.drawOval(ov, paint(mix(RED, BLUE, b / (r + b + 1e-6)), 0.3 * max(r, b), blur=7, stroke=6))
        c.drawOval(ov, paint((44, 36, 32), 1, blur=3))
        c.restore()
        arm = skia.Path(); arm.moveTo(hx, hy); arm.quadTo(hx + sgn * wr * 0.2, hy + wr * 0.5, wx + sgn * wr * 1.05, ph + 30)
        c.drawPath(arm, paint((9, 9, 10), 1, blur=4, stroke=wr * 0.3))
    for sx in (-1, 1):
        pil = skia.Path(); x0 = pw * (0.5 + sx * 0.5)
        pil.moveTo(x0 + sx * 20, -20); pil.lineTo(x0 - sx * pw * 0.1, -20); pil.lineTo(x0 - sx * pw * 0.02, ph * 0.74); pil.lineTo(x0 + sx * 20, ph * 0.74); pil.close()
        c.drawPath(pil, paint((2, 2, 3), 1, blur=5))
    vignette(c, pw, ph, 0.9, 0.3)

def stop_split(c, W, H, t, lum_a=1.0, lum_b=1.0, tense_a=0.0, tense_b=0.0, pull=0.0):
    """Officer on the left / top, driver on the right / bottom."""
    vert = H > W
    c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Color=col((0, 0, 0))))
    if not vert:
        pw, ph = W / 2, H; pos = ((0, 0), (W / 2, 0)); d = (pull * 0.03 * W, 0)
    else:
        pw, ph = W, H / 2; pos = ((0, 0), (0, H / 2)); d = (0, pull * 0.02 * H)
    for i, (fn, lum, tense) in enumerate(((cruiser, lum_a, tense_a), (sedan, lum_b, tense_b))):
        c.save(); c.translate(*pos[i]); c.clipRect(skia.Rect.MakeWH(pw, ph), True)
        sg = 1 if i == 0 else -1
        c.translate(sg * d[0], sg * d[1]); c.translate(pw / 2, ph / 2); c.scale(1.05 + 0.02 * pull, 1.05 + 0.02 * pull); c.translate(-pw / 2, -ph / 2)
        fn(c, pw, ph, t, tense)
        c.restore()
        if lum < 1:
            c.drawRect(skia.Rect.MakeXYWH(pos[i][0], pos[i][1], pw, ph), skia.Paint(Color=col((0, 0, 0), 1 - lum)))

# ------------------------------------------------------------------ three screens, three viewers (#22b)
def three_rooms(c, W, H, t, lit=(1, 0, 0)):
    vert = H > W
    c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Color=col((5, 5, 7))))
    kinds = ("plain", "hat", "wide")
    for i in range(3):
        a = lit[i]
        if not vert: cx = W * (0.2 + 0.3 * i); cy = H * 0.4; tw = W * 0.24
        else: cx = W * 0.5; cy = H * (0.17 + 0.235 * i); tw = W * 0.5
        th = tw * 0.6; tint, lv = tv_light(t, i * 3); lv *= a
        glow(c, cx, cy, tw * 1.25, tint, 0.3 * lv)
        c.save(); c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(cx - tw / 2, cy - th / 2, tw, th), tw * 0.025, tw * 0.025), True)
        c.drawRect(skia.Rect.MakeXYWH(cx - tw / 2, cy - th / 2, tw, th), skia.Paint(Color=col(mix((16, 16, 20), mix(tint, (255, 255, 255), 0.25), lv))))
        glow(c, cx, cy - th * 0.05, tw * 0.5, (255, 255, 255), 0.5 * lv, blend=skia.BlendMode.kSrcOver)
        K.draw(c, K.stand(t, i * 1.7, pockets=(i == 0), carry=(i == 2)), cx, cy + th / 2 - th * 0.05, th * 0.84, a=0.3 + 0.67 * a, soft=0.5,
               case=(i == 2), outfit=("tank", "hat", "suit")[i], t=t, dim=0.9, toon=True, face=("cool", "neutral", "smile")[i])
        c.restore()
        rrect(c, cx - tw / 2, cy - th / 2, tw, th, tw * 0.025, paint((2, 2, 3), 0.9, stroke=tw * 0.014))
        vw = tw * (0.36 if not vert else 0.26); vb = cy + th / 2 + vw * (0.95 if not vert else 0.5)
        vh = tw * 0.6; ps = K.sit(t, i * 2.3); vb = cy + th / 2 + vh * 0.6
        K.draw(c, ps, cx, vb + vh * 0.02, vh, tint, 0.6 * lv + 0.12, weight=0.06, soft=3, glow=False, legs=False); K.draw(c, ps, cx, vb + vh * 0.02, vh, a=1, soft=0.5, legs=False, toon=True, face=None, dim=0.75)
    vignette(c, W, H, 0.9, 0.34)

# ------------------------------------------------------------------ the glass room (#24)
def glass_room(c, W, H, t, refl=0.35, ghost=0.0):
    vert = H > W
    c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Color=col((8, 9, 11))))
    rx, ry, rw, rh = W * 0.06, H * (0.16 if not vert else 0.24), W * 0.88, H * (0.66 if not vert else 0.44)
    linear(c, skia.Rect.MakeXYWH(rx, ry, rw, rh), (0, ry), (0, ry + rh), [col((120, 118, 108), 0.9), col((70, 68, 64), 0.9), col((30, 30, 30), 0.95)], [0, 0.55, 1])
    for i in range(4): glow(c, rx + rw * (0.14 + 0.24 * i), ry + rh * 0.07, rw * 0.11, (255, 244, 220), 0.5, sx=2.2, sy=0.5)
    c.drawRect(skia.Rect.MakeXYWH(rx + rw * 0.1, ry + rh * 0.74, rw * 0.8, rh * 0.06), paint((20, 20, 22), 0.9, blur=3))     # a table edge
    fh = rh * 0.86; fx = rx + rw * (0.56 if not vert else 0.5); fb = ry + rh * 1.02
    lean = math.sin(t * 0.9) * fh * 0.004
    for off, a in ((ghost * fh * 0.13, 0.42 * min(1, ghost * 3)), (0, 1.0)):
        if a <= 0.003: continue
        ah = fh * 0.98; aw = ah * AVATAR.width() / AVATAR.height(); sw_ = math.sin(t * 0.8 + (0 if off == 0 else 2.0)) * ah * 0.006
        pp = skia.Paint(); pp.setAlphaf(0.9 * a)
        c.drawImageRect(AVATAR, skia.Rect.MakeWH(AVATAR.width(), AVATAR.height()), skia.Rect.MakeXYWH(fx - off - aw / 2 + sw_, fb - fh * 0.06 - ah, aw, ah), skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear), pp)
    # glass: mullions and what the corridor throws back
    n = 4 if not vert else 3
    for i in range(n + 1):
        x = rx + rw * i / n
        c.drawLine(x, ry - 8, x, ry + rh + 8, paint((4, 4, 5), 1, blur=1.2, stroke=W * 0.008))
    c.drawLine(rx, ry, rx + rw, ry, paint((4, 4, 5), 1, stroke=W * 0.008)); c.drawLine(rx, ry + rh, rx + rw, ry + rh, paint((4, 4, 5), 1, stroke=W * 0.008))
    c.save(); c.clipRect(skia.Rect.MakeXYWH(rx, ry, rw, rh), True)
    for i in range(3):
        x0 = rx + rw * (0.05 + 0.34 * i) + math.sin(t * 0.12 + i) * 20
        p = skia.Path(); p.moveTo(x0, ry + rh); p.lineTo(x0 + rw * 0.22, ry); p.lineTo(x0 + rw * 0.36, ry); p.lineTo(x0 + rw * 0.14, ry + rh); p.close()
        c.drawPath(p, paint((226, 234, 246), 0.10 * refl + 0.03, blur=18, blend=PLUS))
    for i in range(7):
        u = i / 6; x = rx + rw * (0.08 + 0.84 * u); y = ry + rh * (0.2 + 0.13 * u)
        glow(c, x, y, rw * (0.03 + 0.03 * u), (236, 240, 255), (0.22 + 0.2 * u) * refl, sx=2.6, sy=0.6)
    linear(c, skia.Rect.MakeXYWH(rx, ry, rw, rh), (rx, 0), (rx + rw, 0), [col((200, 214, 236), 0.16 * refl), col((200, 214, 236), 0.02), col((200, 214, 236), 0.2 * refl)], blend=PLUS)
    c.restore()
    linear(c, skia.Rect.MakeLTRB(0, ry + rh, W, H), (0, ry + rh), (0, H), [col((60, 62, 66), 0.3), col((0, 0, 0), 0)], blend=PLUS)
    vignette(c, W, H, 0.9, 0.3)
