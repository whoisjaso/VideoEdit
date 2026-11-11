"""Stick figures that move like people. One jointed rig, a handful of motions, drawn with the film's line.

A pose is a dict of joints in body units: x to the figure's right, y up, feet on y = 0, standing height = 1.
Poses blend joint by joint, so a walk can turn into a stand, and a boy can grow into the figure on the screen.
"""
import math
import skia
from gfx import *

HEAD_R = 0.072; NECK = 0.845; SHO = 0.80; HIP = 0.50; UARM = 0.165; FARM = 0.155; THIGH = 0.25; SHIN = 0.25; SW = 0.105; HW = 0.055
KEYS = ("head", "neck", "sh_l", "sh_r", "el_l", "el_r", "ha_l", "ha_r", "hip", "hip_l", "hip_r", "kn_l", "kn_r", "ft_l", "ft_r")

def _limb(o, a1, l1, a2, l2):
    """Two bones from origin o. Angles in degrees from straight down, positive swings to the figure's right (+x)."""
    j = (o[0] + l1 * math.sin(math.radians(a1)), o[1] - l1 * math.cos(math.radians(a1)))
    e = (j[0] + l2 * math.sin(math.radians(a2)), j[1] - l2 * math.cos(math.radians(a2)))
    return j, e

def front(arm_l=(-8, -4), arm_r=(8, 4), leg_l=(-4, -3), leg_r=(4, 3), lean=0.0, drop=0.0, head=(0.0, 0.0), sway=0.0, sh_tilt=0.0, squash=(1, 1, 1, 1)):
    """Facing the camera (or seen from behind: a stick figure is the same either way)."""
    hip = (sway, HIP - drop); neck = (sway + lean, NECK - drop); p = {"hip": hip, "neck": neck}
    p["head"] = (neck[0] + head[0], neck[1] + HEAD_R + 0.012 + head[1])
    p["sh_l"] = (neck[0] - SW, SHO - drop + sh_tilt); p["sh_r"] = (neck[0] + SW, SHO - drop - sh_tilt)
    p["hip_l"] = (hip[0] - HW, hip[1]); p["hip_r"] = (hip[0] + HW, hip[1])
    p["el_l"], p["ha_l"] = _limb(p["sh_l"], arm_l[0], UARM, arm_l[1], FARM)
    p["el_r"], p["ha_r"] = _limb(p["sh_r"], arm_r[0], UARM, arm_r[1], FARM)
    p["kn_l"], p["ft_l"] = _limb(p["hip_l"], leg_l[0], THIGH * squash[0], leg_l[1], SHIN * squash[1])
    p["kn_r"], p["ft_r"] = _limb(p["hip_r"], leg_r[0], THIGH * squash[2], leg_r[1], SHIN * squash[3])
    return p

def side(arm_f=(20, 35), arm_b=(-20, -5), leg_f=(22, 10), leg_b=(-20, -38), lean=0.03, drop=0.0, facing=1):
    """In profile, walking toward +x (facing=1) or -x."""
    hip = (0.0, HIP - drop); neck = (lean * facing, NECK - drop); p = {"hip": hip, "neck": neck, "hip_l": hip, "hip_r": hip, "sh_l": (neck[0], SHO - drop), "sh_r": (neck[0], SHO - drop)}
    p["head"] = (neck[0] + 0.012 * facing, neck[1] + HEAD_R + 0.012)
    f = facing
    p["el_r"], p["ha_r"] = _limb(p["sh_r"], arm_f[0] * f, UARM, arm_f[1] * f, FARM)
    p["el_l"], p["ha_l"] = _limb(p["sh_l"], arm_b[0] * f, UARM, arm_b[1] * f, FARM)
    p["kn_r"], p["ft_r"] = _limb(hip, leg_f[0] * f, THIGH, leg_f[1] * f, SHIN)
    p["kn_l"], p["ft_l"] = _limb(hip, leg_b[0] * f, THIGH, leg_b[1] * f, SHIN)
    return p

def blend(a, b, k):
    k = clamp(k); return {key: (lerp(a[key][0], b[key][0], k), lerp(a[key][1], b[key][1], k)) for key in KEYS}

# ------------------------------------------------------------------ motions (ph = cycles; one cycle = two steps)
def walk_side(ph, facing=1, energy=1.0):
    s = math.sin(math.tau * ph); c2 = math.cos(math.tau * ph)
    sw = 26 * energy
    lf = (sw * s, sw * s - 6 - 34 * max(0, -c2) * (1 if s < 0 else 0.25))       # the knee folds as the leg swings through
    lb = (-sw * s, -sw * s - 6 - 34 * max(0, c2) * (1 if s > 0 else 0.25))
    return side(arm_f=(-20 * energy * s, -20 * energy * s + 22), arm_b=(20 * energy * s, 20 * energy * s + 22), leg_f=lf, leg_b=lb,
                lean=0.03 * energy, drop=0.012 + 0.014 * abs(c2), facing=facing)

def walk_front(ph, energy=1.0, slouch=0.0, carry=False, pockets=False):
    """Walking toward the camera: knees lift and foreshorten, hips sway, arms counter-swing, the body bobs twice a cycle."""
    s = math.sin(math.tau * ph)
    lift_l = max(0.0, s); lift_r = max(0.0, -s)
    drop = 0.012 + 0.016 * abs(math.cos(math.tau * ph)) + 0.03 * slouch
    sway = 0.018 * s * energy
    def leg(lift, sg): return (sg * (5 + 9 * lift), sg * (3 - 6 * lift)), (1 - 0.22 * lift, 1 - 0.34 * lift)
    (ll, ql), (lr, qr) = leg(lift_l, -1), leg(lift_r, 1)
    al = (-9 - 7 * energy * lift_r, -6 + 16 * energy * lift_r); ar = (9 + 7 * energy * lift_l, 6 - 16 * energy * lift_l)
    if pockets: al, ar = (-14, 18), (14, -18)
    if carry: ar = (7, 3)
    p = front(arm_l=al, arm_r=ar, leg_l=ll, leg_r=lr, lean=-0.01 * s, drop=drop, sway=sway, sh_tilt=0.012 * s * energy,
              head=(0.004 * s, -0.035 * slouch), squash=(ql[0], ql[1], qr[0], qr[1]))
    if slouch: p["sh_l"] = (p["sh_l"][0] + 0.012, p["sh_l"][1] - 0.02 * slouch); p["sh_r"] = (p["sh_r"][0] - 0.012, p["sh_r"][1] - 0.02 * slouch)
    return p

def stand(t, seed=0.0, pockets=False, carry=False):
    """Standing is not still: weight shifts, the chest breathes, the head drifts."""
    w = math.sin(t * 0.7 + seed); br = 0.004 * math.sin(t * 1.6 + seed)
    al, ar = ((-14, 18), (14, -18)) if pockets else ((-7 - 2 * w, -3), (7 - 2 * w, 3))
    if carry: ar = (6, 2)
    return front(arm_l=al, arm_r=ar, leg_l=(-4 - 2 * w, -3 - 3 * max(0, w)), leg_r=(4 - 2 * w, 3 + 3 * max(0, -w)), sway=0.014 * w, drop=0.004 * abs(w) - br,
                 sh_tilt=0.008 * w, head=(0.012 * math.sin(t * 0.43 + seed * 2), 0.0), lean=0.006 * w)

def sit(t, seed=0.0, lean_in=0.0):
    """Seated, seen from behind a couch: legs hidden, a head that tilts, shoulders that settle."""
    w = math.sin(t * 0.5 + seed)
    p = front(arm_l=(-12, 10), arm_r=(12, -10), leg_l=(-70, -10), leg_r=(70, 10), drop=0.26, head=(0.02 * w, 0.006 * math.sin(t * 1.3 + seed) - 0.01 * lean_in), sh_tilt=0.01 * w, lean=0.01 * w)
    return p

def rapper(t, bpm=96.0):
    b = t * bpm / 60; bounce = 0.5 - 0.5 * math.cos(math.tau * b)
    return front(arm_l=(-118 - 26 * math.sin(math.tau * b / 2), -160 - 10 * bounce), arm_r=(58, 148), leg_l=(-9, -3 + 16 * bounce), leg_r=(9, 3 - 16 * bounce),
                 drop=0.035 * bounce, sway=0.02 * math.sin(math.tau * b / 2), head=(0.01 * math.sin(math.tau * b / 2), -0.012 * bounce), sh_tilt=0.02 * math.sin(math.tau * b / 2))

def athlete(t):
    d = t * 2.6; push = 0.5 - 0.5 * math.cos(math.tau * d)
    p = front(arm_l=(-28, -64), arm_r=(24 + 10 * push, 30 + 55 * (1 - push)), leg_l=(-20, 8), leg_r=(18, -6), drop=0.085 + 0.012 * push, lean=0.03, sway=0.012 * math.sin(math.tau * d / 2), head=(0.02, -0.01))
    ball = (p["ha_r"][0] + 0.01, max(0.045, p["ha_r"][1] - 0.05 - (p["ha_r"][1] - 0.09) * push))
    return p, ball

def dealer(t):
    look = math.sin(t * 2.4); reach = 0.5 - 0.5 * math.cos(min(math.tau, max(0.0, (t % 2.2) - 0.4) * 4.2))
    return front(arm_l=(-14, 18), arm_r=(12 + 44 * reach, -6 + 70 * reach), leg_l=(-5, -3), leg_r=(5, 3), head=(0.03 * look, -0.008), drop=0.012, sway=-0.01, sh_tilt=-0.012, lean=-0.008)

def cell(t):
    sag = 0.5 + 0.5 * math.sin(t * 0.8)
    return front(arm_l=(-36, -150), arm_r=(36, 150), leg_l=(-4, -3), leg_r=(4, 3), head=(0.0, -0.03 - 0.02 * sag), drop=0.015 + 0.01 * sag, lean=0.0)

def talker(t, seed=0.0, formal=1.0):
    """Talking with his hands: beats, a palm that opens, a nod."""
    g = noise1(t * 1.7 + seed, 3); g2 = noise1(t * 1.1 + seed, 4); nod = math.sin(t * 2.2 + seed)
    return front(arm_l=(-18 - 14 * max(0, g2), -62 - 46 * max(0, g2)), arm_r=(22 + 20 * (0.5 + 0.5 * g), 74 + 44 * g), leg_l=(-4, -3), leg_r=(4, 3),
                 head=(0.008 * g, -0.008 * max(0, nod)), sway=0.008 * g2, lean=0.01 * g, sh_tilt=0.006 * g)

# ------------------------------------------------------------------ drawing
def draw(c, pose, x, y, h, color=(238, 236, 230), a=1.0, weight=0.034, soft=0.0, glow=True, hat=False, tie=False, case=False, extra=None, legs=True):
    if a <= 0.003: return
    w = max(2.4, h * weight)
    P = lambda k: (x + pose[k][0] * h, y - pose[k][1] * h)
    path = skia.Path()
    def bone(*ks):
        path.moveTo(*P(ks[0]))
        for k in ks[1:]: path.lineTo(*P(k))
    bone("neck", "hip"); bone("sh_l", "neck", "sh_r"); bone("sh_l", "el_l", "ha_l"); bone("sh_r", "el_r", "ha_r")
    if legs: bone("hip_l", "hip", "hip_r"); bone("hip_l", "kn_l", "ft_l"); bone("hip_r", "kn_r", "ft_r")
    hx, hy = P("head"); r = HEAD_R * h
    path.addCircle(hx, hy, r - w * 0.5)
    if hat:
        path.moveTo(hx - r * 2.25, hy - r * 0.62); path.lineTo(hx + r * 2.25, hy - r * 0.62)
        path.moveTo(hx - r * 0.95, hy - r * 0.62); path.lineTo(hx - r * 0.8, hy - r * 1.75); path.lineTo(hx + r * 0.8, hy - r * 1.75); path.lineTo(hx + r * 0.95, hy - r * 0.62)
    if tie:
        nx, ny = P("neck"); path.moveTo(nx, ny + w); path.lineTo(nx - 0.016 * h, ny + 0.1 * h); path.lineTo(nx, ny + 0.135 * h); path.lineTo(nx + 0.016 * h, ny + 0.1 * h); path.close()
    if case:
        kx, ky = P("ha_r"); path.addRect(skia.Rect.MakeXYWH(kx - 0.075 * h, ky + 0.02 * h, 0.15 * h, 0.105 * h)); path.moveTo(kx - 0.03 * h, ky + 0.02 * h); path.lineTo(kx - 0.03 * h, ky); path.lineTo(kx + 0.03 * h, ky); path.lineTo(kx + 0.03 * h, ky + 0.02 * h)
    if extra is not None: path.addPath(extra)
    if glow: c.drawPath(path, paint(color, 0.22 * a, stroke=w * 3.2, blur=w * 2.2 + soft))
    c.drawPath(path, paint(color, a, stroke=w, blur=soft))
