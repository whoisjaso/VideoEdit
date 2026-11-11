"""Stick figures that move like people. One jointed rig, a handful of motions, drawn with the film's line.

A pose is a dict of joints in body units: x to the figure's right, y up, feet on y = 0, standing height = 1.
Poses blend joint by joint, so a walk can turn into a stand, and a boy can grow into the figure on the screen.
"""
import math
import skia
from gfx import *

HEAD_R = 0.124; NECK = 0.845; SHO = 0.80; HIP = 0.50; UARM = 0.185; FARM = 0.175; THIGH = 0.25; SHIN = 0.25; SW = 0.105; HW = 0.055
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
    k = clamp(k); out = {key: (lerp(a[key][0], b[key][0], k), lerp(a[key][1], b[key][1], k)) for key in KEYS}
    if "_facing" in a and k < 0.5: out["_facing"] = a["_facing"]
    return out

# ------------------------------------------------------------------ motions (ph = cycles; one cycle = two steps)
def walk_side(ph, facing=1, energy=1.0):
    s = math.sin(math.tau * ph); c2 = math.cos(math.tau * ph)
    sw = 26 * energy
    lf = (sw * s, sw * s - 6 - 34 * max(0, -c2) * (1 if s < 0 else 0.25))       # the knee folds as the leg swings through
    lb = (-sw * s, -sw * s - 6 - 34 * max(0, c2) * (1 if s > 0 else 0.25))
    return side(arm_f=(-20 * energy * s, -20 * energy * s + 22), arm_b=(20 * energy * s, 20 * energy * s + 22), leg_f=lf, leg_b=lb,
                lean=0.03 * energy, drop=0.012 + 0.014 * abs(c2), facing=facing)

def _ik(hip, foot, bend=1):
    """Two-bone leg: where the knee has to be for this hip and this foot. bend = +1 knee forward (+x), -1 back."""
    dx, dy = foot[0] - hip[0], foot[1] - hip[1]; d = min(math.hypot(dx, dy), THIGH + SHIN - 1e-4); d = max(d, 0.05)
    a = math.acos(clamp((THIGH ** 2 + d ** 2 - SHIN ** 2) / (2 * THIGH * d), -1, 1)); base = math.atan2(dy, dx)
    k1 = (hip[0] + THIGH * math.cos(base + a), hip[1] + THIGH * math.sin(base + a)); k2 = (hip[0] + THIGH * math.cos(base - a), hip[1] + THIGH * math.sin(base - a))
    return k1 if (k1[0] - k2[0]) * bend > 0 else k2

def walk_ik(dist, facing=1, stride=0.74, energy=1.0, nod=0.0, hands_lag=None):
    """A walk measured in distance, not time: a foot on the ground stays where it landed while the body travels over it.
    dist is in body heights. Knees come from the stride, the hips dip at double support, the arms answer the legs."""
    L = stride / 2; ph = dist / stride
    p = {}; feet = []
    for off in (0.0, 0.5):
        u = (ph + off) % 1.0
        if u < 0.62: fx = L * 0.56 - (u / 0.62) * L * 1.12; fy = 0.0
        else:
            v = (u - 0.62) / 0.38; e = v * v * (3 - 2 * v); fx = -L * 0.56 + L * 1.12 * e; fy = 0.075 * math.sin(math.pi * v) ** 0.9
        feet.append((fx * facing, fy))
    hy = HIP - 0.012 - 0.022 * (0.5 + 0.5 * math.cos(4 * math.pi * ph)) * energy
    lean = 0.04 * energy * facing; hip = (0.0, hy); neck = (lean, hy + (NECK - HIP)); sy = hy + (SHO - HIP)
    p["hip"] = p["hip_l"] = p["hip_r"] = hip; p["neck"] = neck; p["sh_l"] = p["sh_r"] = (lean * 0.9, sy)
    p["head"] = (neck[0] + 0.014 * facing, neck[1] + HEAD_R + 0.012 - 0.03 * nod - 0.004 * math.cos(4 * math.pi * ph + 0.9))
    p["ft_r"], p["ft_l"] = feet[0], feet[1]; p["kn_r"] = _ik(hip, feet[0], facing); p["kn_l"] = _ik(hip, feet[1], facing)
    sw = math.sin(2 * math.pi * (ph if hands_lag is None else hands_lag / stride) + 0.35)                 # arms answer the opposite leg, a beat late
    p["el_r"], p["ha_r"] = _limb(p["sh_r"], -24 * sw * energy * facing, UARM, (-24 * sw * energy + 24) * facing, FARM)
    p["el_l"], p["ha_l"] = _limb(p["sh_l"], 24 * sw * energy * facing, UARM, (24 * sw * energy + 24) * facing, FARM)
    p["_facing"] = facing
    return p

def walk_front(ph, energy=1.0, slouch=0.0, carry=False, pockets=False, smoke=False):
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
    if smoke:
        k = drag(ph / 0.8); ar = (lerp(ar[0], 122, k), lerp(ar[1], -68, k))
    p = front(arm_l=al, arm_r=ar, leg_l=ll, leg_r=lr, lean=-0.01 * s, drop=drop, sway=sway, sh_tilt=0.012 * s * energy,
              head=(0.004 * s, -0.035 * slouch), squash=(ql[0], ql[1], qr[0], qr[1]))
    if slouch: p["sh_l"] = (p["sh_l"][0] + 0.012, p["sh_l"][1] - 0.02 * slouch); p["sh_r"] = (p["sh_r"][0] - 0.012, p["sh_r"][1] - 0.02 * slouch)
    return p

def drag(t, period=5.6):
    """0..1: how far the cigarette hand is toward the mouth. Up, hold, down, rest."""
    c_ = t % period; return io_cubic(ramp(c_, 0.9, 1.7)) * (1 - io_cubic(ramp(c_, 2.6, 3.5)))

def stand(t, seed=0.0, pockets=False, carry=False, smoke=False):
    """Standing is not still: weight shifts, the chest breathes, the head drifts."""
    w = math.sin(t * 0.7 + seed); br = 0.004 * math.sin(t * 1.6 + seed)
    al, ar = ((-14, 18), (14, -18)) if pockets else ((-7 - 2 * w, -3), (7 - 2 * w, 3))
    if carry: ar = (6, 2)
    if smoke:
        k = drag(t + seed); ar = (lerp(10, 122, k), lerp(8, -68, k))
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
TANK = (214, 212, 205); DENIM = (58, 70, 96); BAND = (176, 176, 184); SNEAK = (216, 214, 208); GOLD = (236, 184, 72)
CHAR = (46, 48, 55); SHIRT = (226, 226, 222); TAN = (178, 150, 104); CLAY = (118, 82, 60); BOOT = (58, 40, 30)

def _strip(pts, widths):
    """A limb with thickness: a polygon that follows the joints."""
    L, R = [], []
    for i, (x, y) in enumerate(pts):
        a = pts[min(i + 1, len(pts) - 1)]; b = pts[max(i - 1, 0)]; dx, dy = a[0] - b[0], a[1] - b[1]; d = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / d, dx / d; L.append((x + nx * widths[i], y + ny * widths[i])); R.append((x - nx * widths[i], y - ny * widths[i]))
    return path_from(L + R[::-1])

BODY = (10, 10, 12); HEADC = (246, 245, 240); EDGE = (232, 230, 224)
FACES = {   # brow: degrees, + = inner ends down (anger), - = inner ends up (worry). lids: 1 = wide open. gaze: where the pupils sit.
    "cool":    dict(brow=6, lids=0.62, mouth="flat"),
    "drag":    dict(brow=4, lids=0.5, mouth="o"),
    "neutral": dict(brow=0, lids=0.9, mouth="flat"),
    "smile":   dict(brow=-4, lids=0.9, mouth="smile", raise_=0.3),
    "hurt":    dict(brow=-16, lids=0.85, mouth="frown", raise_=0.25),
    "tough":   dict(brow=20, lids=0.75, mouth="o"),
    "focus":   dict(brow=13, lids=0.7, mouth="flat"),
    "shifty":  dict(brow=8, lids=0.6, mouth="smirk"),
    "sad":     dict(brow=-22, lids=0.55, mouth="frown"),
    "wary":    dict(brow=12, lids=0.8, mouth="flat"),
}
def face_blend(a, b, k):
    A, B = FACES[a] if isinstance(a, str) else a, FACES[b] if isinstance(b, str) else b; k = clamp(k)
    out = {q: lerp(A.get(q, 0.0), B.get(q, 0.0), k) for q in ("brow", "lids", "raise_")}
    out["mouth"] = (B if k > 0.5 else A).get("mouth", "flat"); out["gaze"] = (B if k > 0.5 else A).get("gaze", (0, 0)); return out

def _face(c, hx, hy, r, f, look, a, t):
    """A face that reads at a glance: two eyes, two brows, a mouth. Blinks."""
    if isinstance(f, str): f = FACES[f]
    ol = max(1.5, r * 0.075); ox = look * 0.36 * r; gz = f.get("gaze", (0.0, 0.0))
    blink = 1.0 - 0.92 * max(0.0, 1 - abs(((t * 0.31 + 0.13) % 1.0) - 0.5) * 34)            # a quick blink about every three seconds
    lids = max(0.08, f.get("lids", 0.9) * blink)
    for sg in (-1, 1):
        ex, ey = hx + ox + sg * 0.37 * r * (1 - 0.25 * abs(look)), hy - 0.06 * r; rw, rh = 0.25 * r, 0.3 * r * lids
        eye = skia.Rect.MakeLTRB(ex - rw, ey - rh, ex + rw, ey + rh)
        c.drawOval(eye, paint((255, 255, 255), a)); c.drawOval(eye, paint(BODY, a, stroke=ol))
        c.save(); c.clipRect(eye, True)
        c.drawCircle(ex + (gz[0] + look * 0.5) * rw * 0.45, ey + gz[1] * rh * 0.4 + 0.02 * r, 0.115 * r, paint(BODY, a)); c.restore()
        if lids < 0.8: c.drawLine(ex - rw, ey - rh, ex + rw, ey - rh, paint(BODY, a, stroke=ol * 1.5))             # a heavy upper lid
        ba = math.radians(f.get("brow", 0.0)); by = ey - 0.3 * r - 0.17 * r - f.get("raise_", 0.0) * 0.12 * r
        bx_in, bx_out = ex - sg * 0.24 * r, ex + sg * 0.27 * r
        c.drawLine(bx_in, by + math.sin(ba) * 0.2 * r, bx_out, by - math.sin(ba) * 0.1 * r, paint(BODY, a, stroke=r * 0.105))
    mx, my = hx + ox * 0.9, hy + 0.52 * r; m = f.get("mouth", "flat"); mw = 0.24 * r
    if m == "o": c.drawOval(skia.Rect.MakeLTRB(mx - 0.1 * r, my - 0.11 * r, mx + 0.1 * r, my + 0.12 * r), paint((70, 26, 26), a)); c.drawOval(skia.Rect.MakeLTRB(mx - 0.1 * r, my - 0.11 * r, mx + 0.1 * r, my + 0.12 * r), paint(BODY, a, stroke=ol))
    else:
        dy = {"smile": 0.13, "frown": -0.12}.get(m, 0.0) * r; q = skia.Path(); q.moveTo(mx - mw, my - dy * 0.5 - (0.06 * r if m == "smirk" else 0)); q.quadTo(mx, my + dy, mx + mw, my - dy * 0.5 + (0.03 * r if m == "smirk" else 0))
        c.drawPath(q, paint(BODY, a, stroke=ol * 1.25))

def draw(c, pose, x, y, h, color=(238, 236, 230), a=1.0, weight=0.034, soft=0.0, glow=True, hat=False, tie=False, case=False, extra=None, legs=True,
         outfit=None, t=0.0, smoke=False, dim=1.0, trail=None, toon=False, face=None, look=0.0, edge=None):
    """outfit: None, "tank" (tank top, sagging baggy jeans, earrings, chain), "hat" (brimmed hat, shirt, boots), "suit".
    toon=True draws him in the house character style: a big white head with a bold outline, a solid black body, fists and
    oval shoes. face = an expression name from FACES (or None for the back of a head). edge = a thin light outline so the
    black body still reads on a dark plate."""
    if a <= 0.003: return
    if trail:
        for i, tp in enumerate(trail): draw(c, tp, x, y, h, BODY if toon else color, a * (0.2 - 0.07 * i), weight, soft + h * 0.004, False, legs=legs)
    if toon: color = BODY; weight = max(weight, 0.042)
    w = max(2.4, h * weight); ol = max(1.4, w * 0.45); ed = max(1.6, h * 0.007) if (toon and edge is not None) else 0.0
    P = lambda k: (x + pose[k][0] * h, y - pose[k][1] * h)
    C = lambda rgb: tuple(v * dim for v in rgb)
    def fill(path, rgb, outline=True):
        c.drawPath(path, paint(C(rgb), a, blur=soft))
        if outline: c.drawPath(path, paint(color, a, stroke=ol, blur=soft))
    hx, hy = P("head"); r = HEAD_R * h; nk = P("neck"); hp = P("hip"); sl, sr = P("sh_l"), P("sh_r")
    path = skia.Path()
    def limb(k0, k1, k2, w0, w1, edged=True):
        p0, p1, p2 = (P(k) if isinstance(k, str) else k for k in (k0, k1, k2))
        cx_, cy_ = 2 * p1[0] - (p0[0] + p2[0]) / 2, 2 * p1[1] - (p0[1] + p2[1]) / 2
        cx_, cy_ = lerp(p1[0], cx_, 0.72), lerp(p1[1], cy_, 0.72); pts = []; ws = []
        for i in range(11):
            u = i / 10; pts.append(((1 - u) ** 2 * p0[0] + 2 * u * (1 - u) * cx_ + u * u * p2[0], (1 - u) ** 2 * p0[1] + 2 * u * (1 - u) * cy_ + u * u * p2[1])); ws.append(lerp(w0, w1, u) / 2)
        for pas in ((1, 0) if (ed and edged) else (0,)):
            e_ = ed if pas else 0.0; cc_ = edge if pas else color
            c.drawPath(_strip(pts, [q + e_ for q in ws]), paint(cc_, a, blur=soft)); c.drawCircle(p0[0], p0[1], w0 / 2 + e_, paint(cc_, a, blur=soft)); c.drawCircle(p2[0], p2[1], w1 / 2 + e_, paint(cc_, a, blur=soft))
    fc = pose.get("_facing", 0)
    def foot(k):
        fx_, fy_ = P(k); d = 0.05 * h * (fc if fc else (1 if k == "ft_r" else -1) * 0.4); rw_, rh_ = (0.06 * h, 0.027 * h) if toon else (0.042 * h, 0.016 * h)
        ov = skia.Rect.MakeLTRB(fx_ + d - rw_, fy_ - rh_ * 1.35, fx_ + d + rw_, fy_ + rh_ * 0.65)
        if ed: c.drawOval(skia.Rect.MakeLTRB(ov.left() - ed, ov.top() - ed, ov.right() + ed, ov.bottom() + ed), paint(edge, a, blur=soft))
        c.drawOval(ov, paint(color, a, blur=soft))
    if glow and not toon:
        g = skia.Path(); g.moveTo(*nk); g.lineTo(*hp); g.addCircle(hx, hy, r)
        c.drawPath(g, paint(color, 0.2 * a, stroke=w * 3.2, blur=w * 2.2 + soft))
    # ---- legs
    if legs:
        if outfit in ("tank", "suit", "hat"):
            sag = 0.055 * h if outfit == "tank" else 0.0
            wl = (0.066, 0.062, 0.058) if outfit == "tank" else (0.04, 0.034, 0.03)
            rgb = DENIM if outfit == "tank" else CHAR if outfit == "suit" else (70, 62, 54)
            hl, hr = P("hip_l"), P("hip_r")
            if outfit == "tank": c.drawRect(skia.Rect.MakeLTRB(hl[0] - 0.062 * h, hp[1] - 0.012 * h, hr[0] + 0.062 * h, hp[1] + sag + 0.004 * h), paint(C(BAND), a, blur=soft))
            seat = path_from([(hl[0] - wl[0] * h, hl[1] + sag), (hr[0] + wl[0] * h, hr[1] + sag), (hr[0] + wl[0] * h * 0.6, hr[1] + sag + 0.11 * h), (hp[0], hp[1] + sag + (0.15 if outfit == "tank" else 0.08) * h), (hl[0] - wl[0] * h * 0.6, hl[1] + sag + 0.11 * h)])
            fill(seat, rgb, False)
            for hj, kn, ft in ((hl, P("kn_l"), P("ft_l")), (hr, P("kn_r"), P("ft_r"))):
                fill(_strip([(hj[0], hj[1] + sag), kn, ft], [wl[0] * h, wl[1] * h, wl[2] * h]), rgb)
                if outfit == "tank":
                    for q in (0.03, 0.055): c.drawLine(ft[0] - wl[2] * h, ft[1] - q * h, ft[0] + wl[2] * h, ft[1] - q * h + 0.008 * h, paint(color, 0.7 * a, stroke=ol, blur=soft))
                shoe = skia.Rect.MakeLTRB(ft[0] - 0.056 * h, ft[1] - 0.03 * h, ft[0] + 0.056 * h, ft[1] + 0.014 * h)
                if outfit == "hat": c.drawRect(skia.Rect.MakeLTRB(ft[0] - 0.036 * h, ft[1] - 0.075 * h, ft[0] + 0.045 * h, ft[1] + 0.01 * h), paint(C(BOOT), a, blur=soft))
                else: c.drawOval(shoe, paint(C(SNEAK if outfit == "tank" else (24, 22, 22)), a, blur=soft)); c.drawOval(shoe, paint(color, a, stroke=ol, blur=soft))
            if outfit == "hat": c.drawCircle(hp[0], hp[1] + 0.006 * h, 0.013 * h, paint(C(GOLD), a))
        else:
            limb("hip_l", "kn_l", "ft_l", w * 1.2, w * 0.9); limb("hip_r", "kn_r", "ft_r", w * 1.2, w * 0.9); foot("ft_l"); foot("ft_r")
            if not fc: limb("hip_l", P("hip"), "hip_r", w * 1.2, w * 1.2)
    # ---- torso
    if outfit == "tank":
        t_ = skia.Path(); bw = 0.082 * h; by = hp[1] + 0.03 * h
        t_.moveTo(nk[0] - 0.062 * h, nk[1] + 0.004 * h)
        t_.quadTo(sl[0] + 0.035 * h, sl[1] + 0.085 * h, nk[0] - 0.088 * h, sl[1] + 0.13 * h)
        t_.lineTo(hp[0] - bw, by); t_.lineTo(hp[0] + bw, by); t_.lineTo(nk[0] + 0.088 * h, sr[1] + 0.13 * h)
        t_.quadTo(sr[0] - 0.035 * h, sr[1] + 0.085 * h, nk[0] + 0.062 * h, nk[1] + 0.004 * h)
        t_.lineTo(nk[0] + 0.032 * h, nk[1] + 0.004 * h); t_.quadTo(nk[0], nk[1] + 0.12 * h, nk[0] - 0.032 * h, nk[1] + 0.004 * h); t_.close()
        limb("sh_l", (nk[0], nk[1] + 0.012 * h), "sh_r", w, w)
        fill(t_, TANK)
        ch = skia.Path(); ch.moveTo(nk[0] - 0.03 * h, nk[1] + 0.012 * h); ch.quadTo(nk[0], nk[1] + 0.105 * h, nk[0] + 0.03 * h, nk[1] + 0.012 * h)
        c.drawPath(ch, paint(C(GOLD), a, stroke=max(1.2, 0.008 * h), blur=soft))
    elif outfit in ("suit", "hat"):
        rgb = CHAR if outfit == "suit" else CLAY; j = skia.Path()
        j.moveTo(sl[0] - 0.012 * h, sl[1] - 0.004 * h); j.lineTo(sr[0] + 0.012 * h, sr[1] - 0.004 * h); j.lineTo(hp[0] + 0.09 * h, hp[1] + 0.045 * h); j.lineTo(hp[0] - 0.09 * h, hp[1] + 0.045 * h); j.close()
        fill(j, rgb)
        if outfit == "suit":
            v = path_from([(nk[0] - 0.036 * h, nk[1] + 0.002 * h), (nk[0] + 0.036 * h, nk[1] + 0.002 * h), (nk[0], nk[1] + 0.16 * h)]); fill(v, SHIRT, False)
            c.drawPath(path_from([(nk[0] - 0.036 * h, nk[1]), (nk[0], nk[1] + 0.16 * h), (nk[0] + 0.036 * h, nk[1])], False), paint(color, a, stroke=ol, blur=soft))
        else:
            c.drawLine(nk[0], nk[1] + 0.01 * h, nk[0], hp[1] + 0.04 * h, paint(color, 0.8 * a, stroke=ol, blur=soft))
        for sh_, el_, ha_ in ((sl, P("el_l"), P("ha_l")), (sr, P("el_r"), P("ha_r"))):
            pts = [sh_, el_, ha_] if outfit == "suit" else [sh_, ((sh_[0] + el_[0]) / 2, (sh_[1] + el_[1]) / 2 + 0.03 * h)]
            fill(_strip(pts, [0.034 * h, 0.03 * h, 0.026 * h][:len(pts)]), rgb)
        tie = tie or outfit == "suit"; hat = hat or outfit == "hat"
    else:
        mid = ((nk[0] + hp[0]) / 2 + (nk[0] - hp[0]) * 0.35, (nk[1] + hp[1]) / 2)
        if not fc: limb("sh_l", (nk[0], nk[1] + 0.012 * h), "sh_r", w, w)
        limb("neck", mid, "hip", w * 1.3, w * 1.25)
        if not fc: limb("sh_l", (nk[0], nk[1] + 0.012 * h), "sh_r", w, w, edged=False)
    # ---- arms
    if outfit != "suit": limb("sh_l", "el_l", "ha_l", w * 1.05, w * 0.8); limb("sh_r", "el_r", "ha_r", w * 1.05, w * 0.8)
    for k in ("ha_l", "ha_r"):                                    # fists
        hx_, hy_ = P(k); fr = w * (0.95 if toon else 0.62)
        if ed: c.drawCircle(hx_, hy_, fr + ed, paint(edge, a, blur=soft))
        c.drawCircle(hx_, hy_, fr, paint(color, a, blur=soft))
    # ---- head
    c.drawLine(nk[0], nk[1], hx, hy, paint(color, a, stroke=w * 0.95, blur=soft))
    if toon:
        if ed: c.drawCircle(hx, hy, r + ed + ol * 0.6, paint(edge, a, blur=soft))
        c.drawCircle(hx, hy, r, paint(HEADC if dim >= 0.7 else C(HEADC), a, blur=soft)); c.drawCircle(hx, hy, r, paint(BODY, a, stroke=max(2.0, r * 0.12), blur=soft))
        lk = look if not fc else 0.8 * fc
        if face is not None: _face(c, hx, hy, r, face, lk, a, t)
    else:
        c.drawCircle(hx, hy, r, paint(color, a, blur=soft))
    if hat:
        hp_ = skia.Path(); hp_.addOval(skia.Rect.MakeLTRB(hx - r * 1.75, hy - r * 0.98, hx + r * 1.75, hy - r * 0.56))
        hp_.addPath(path_from([(hx - r * 0.86, hy - r * 0.78), (hx - r * 0.7, hy - r * 1.62), (hx + r * 0.7, hy - r * 1.62), (hx + r * 0.86, hy - r * 0.78)]))
        if outfit == "hat": fill(hp_, TAN)
        else: path.addPath(hp_)
    if tie:
        path.moveTo(nk[0], nk[1] + w); path.lineTo(nk[0] - 0.016 * h, nk[1] + 0.1 * h); path.lineTo(nk[0], nk[1] + 0.135 * h); path.lineTo(nk[0] + 0.016 * h, nk[1] + 0.1 * h); path.close()
    if case:
        kx, ky = P("ha_r"); cs = skia.Path(); cs.addRect(skia.Rect.MakeXYWH(kx - 0.075 * h, ky + 0.02 * h, 0.15 * h, 0.105 * h))
        if toon: c.drawPath(cs, paint((92, 60, 36), a))
        path.addPath(cs); path.moveTo(kx - 0.03 * h, ky + 0.02 * h); path.lineTo(kx - 0.03 * h, ky); path.lineTo(kx + 0.03 * h, ky); path.lineTo(kx + 0.03 * h, ky + 0.02 * h)
    if extra is not None: path.addPath(extra)
    c.drawPath(path, paint(color, a, stroke=w if not toon else max(2.0, w * 0.55), blur=soft))
    if outfit == "tank":
        for sg in (-1, 1): c.drawCircle(hx + sg * (r + 0.006 * h), hy + r * 0.36, max(1.8, 0.016 * h), paint(C(GOLD), a)); c.drawCircle(hx + sg * (r + 0.006 * h), hy + r * 0.36, max(1.8, 0.016 * h), paint(BODY, a, stroke=max(1.0, ol * 0.6)))
    if smoke:
        kx, ky = P("ha_r"); tx_, ty_ = kx - 0.012 * h, ky - 0.055 * h
        c.drawLine(kx, ky - 0.006 * h, tx_, ty_, paint((236, 234, 228), a, stroke=max(1.8, 0.013 * h)))
        c.drawCircle(tx_, ty_, max(1.5, 0.01 * h) * (1 + 0.3 * math.sin(t * 5)), paint((255, 140, 60), a))
        for i in range(9):
            age = (t * 0.33 + i / 9) % 1.0
            sx = tx_ + (noise1(t * 0.5 + i * 3.1, 7 + i) * 0.05 + 0.03 * age) * h * (0.4 + age * 2.2); sy = ty_ - age * 0.42 * h
            c.drawCircle(sx, sy, (0.012 + 0.05 * age) * h, paint((206, 206, 212), 0.2 * a * (1 - age) ** 1.3, blur=max(2.0, 0.02 * h)))
