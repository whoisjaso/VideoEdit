"""Drawing helpers for the film: easing, type, grain, soft plates. Skia raster, no GPU."""
import math, random
import numpy as np, skia

WHITE = (245, 243, 238)
AMBER = (240, 168, 58)        # the one accent: observer moments only
BLACK = (6, 6, 7)

# ---------- easing ----------
def clamp(x, a=0.0, b=1.0): return a if x < a else b if x > b else x
def lerp(a, b, t): return a + (b - a) * t
def ramp(t, a, b): return clamp((t - a) / (b - a)) if b != a else (1.0 if t >= a else 0.0)
def out_quint(x): x = clamp(x); return 1 - (1 - x) ** 5
def in_cubic(x): x = clamp(x); return x ** 3
def io_sine(x): x = clamp(x); return 0.5 - 0.5 * math.cos(math.pi * x)
def io_cubic(x): x = clamp(x); return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2
def appear(t, t0, dur=0.55): return out_quint(ramp(t, t0, t0 + dur))
def vanish(t, t1, dur=0.35): return 1 - in_cubic(ramp(t, t1 - dur, t1))
def window(t, t0, t1, din=0.55, dout=0.35): return appear(t, t0, din) * vanish(t, t1, dout)

def col(rgb, a=1.0): return skia.Color(int(rgb[0]), int(rgb[1]), int(rgb[2]), int(clamp(a) * 255))
def mix(c1, c2, t): return tuple(lerp(c1[i], c2[i], t) for i in range(3))

def noise1(x, seed=0):
    """Smooth 1D value noise in [-1, 1]."""
    i = math.floor(x); f = x - i; f = f * f * (3 - 2 * f)
    def h(n):
        n = (int(n) * 374761393 + seed * 668265263) & 0xFFFFFFFF
        n = (n ^ (n >> 13)) * 1274126177 & 0xFFFFFFFF
        return ((n ^ (n >> 16)) & 0xFFFF) / 32767.5 - 1
    return lerp(h(i), h(i + 1), f)

# ---------- type ----------
_fm = skia.FontMgr()
_tf = {}
def typeface(weight=500, display=True, mono=False):
    key = (weight, display, mono)
    if key not in _tf:
        fam = "JetBrains Mono" if mono else ("Inter Display" if display else "Inter")
        _tf[key] = _fm.matchFamilyStyle(fam, skia.FontStyle(weight, 5, skia.FontStyle.kUpright_Slant))
    return _tf[key]

def font(size, weight=500, display=True, mono=False):
    f = skia.Font(typeface(weight, display, mono), size)
    f.setSubpixel(True); f.setEdging(skia.Font.Edging.kAntiAlias); f.setHinting(skia.FontHinting.kNone)
    return f

# House rule (Jason, Nov 11 2026): every on-screen title is ALL CAPS. Captions are speech and stay sentence case;
# the olaceo wordmark stays lowercase. Caps are set a little smaller and a little wider so layouts hold.
CAPS = True; CAPS_SCALE = 0.84; CAPS_TRACK = 0.035
BOUNDS = [None, None]          # left / right safe edge in px, set by the film; titles shrink to stay inside

def text_w(s, f, track=0.0):
    return f.measureText(s) + track * f.getSize() * max(0, len(s) - 1)

def draw_text(c, s, x, y, size, weight=500, color=WHITE, a=1.0, align="center", track=-0.012,
              blur=0.0, display=True, mono=False, caps=True, fit=None):
    """Baseline text. align: left / center / right. track in em. Sub-pixel placed.
    caps=True sets it as a title (ALL CAPS); fit = max width in px (defaults to the safe edges)."""
    if a <= 0.003 or not s: return 0
    if caps and CAPS:
        s = s.upper(); size = size * (CAPS_SCALE if not mono else 0.92); track = max(track, CAPS_TRACK if not mono else 0.04)
    for _ in range(2):
        f = font(size, weight, display, mono)
        gl = f.textToGlyphs(s); ws = f.getWidths(gl)
        xs = []; cx = 0.0
        for w in ws: xs.append(cx); cx += w + track * size
        tw = cx - track * size if ws else 0
        avail = fit
        if avail is None and BOUNDS[0] is not None and caps:
            L, R = BOUNDS
            avail = (R - x) if align == "left" else (x - L) if align == "right" else 2 * min(x - L, R - x)
        if avail and tw > avail > 20: size *= avail / tw
        else: break
    ox = x - tw / 2 if align == "center" else x - tw if align == "right" else x
    p = skia.Paint(AntiAlias=True, Color=col(color, a))
    if blur > 0.05: p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    b = skia.TextBlobBuilder(); b.allocRunPosH(f, gl, xs, 0)
    c.drawTextBlob(b.make(), ox, y, p)
    return tw

def layout_words(words, f, max_w, track=-0.012, line_h=1.2, align="center"):
    """Wrap words. Returns [(word, x, line_index)], n_lines with x relative to block centre/left."""
    sp = f.measureText(" ") * (1.45 if CAPS else 0.95)      # caps need a real word space
    lines = [[]]; cur = 0.0
    for w in words:
        ww = text_w(w, f, track)
        if lines[-1] and cur + sp + ww > max_w: lines.append([]); cur = 0.0
        if lines[-1]: cur += sp
        lines[-1].append((w, cur, ww)); cur += ww
    out = []
    for li, ln in enumerate(lines):
        tot = ln[-1][1] + ln[-1][2]
        off = -tot / 2 if align == "center" else 0.0 if align == "left" else -tot
        for w, x, ww in ln: out.append((w, x + off, li))
    return out, len(lines)

def draw_words(c, words, states, x, y, size, weight=500, max_w=1400, line_h=1.22, align="center",
               track=-0.012, rise=None, top=False):
    """Word-by-word type. states[i] = (alpha, colour, progress 0..1 of the entrance)."""
    if CAPS:
        words = [w.upper() for w in words]; size = size * CAPS_SCALE; track = max(track, CAPS_TRACK)
        longest = max(text_w(w, font(size, weight), track) for w in words)
        if longest > max_w: size *= max_w / longest
    f = font(size, weight); lay, n = layout_words(words, f, max_w, track, line_h, align)
    rise = size * 0.28 if rise is None else rise
    y0 = y if top else y - (n - 1) * size * line_h / 2
    for (w, wx, li), (a, colr, pr) in zip(lay, states):
        if a <= 0.003: continue
        draw_text(c, w, x + wx, y0 + li * size * line_h + (1 - pr) * rise, size, weight, colr, a,
                  align="left", track=track, blur=(1 - pr) * size * 0.06, caps=False)
    return n

def word_states(t, starts, color=WHITE, dim=None, din=0.42, t_out=None, dout=0.35):
    """Each word enters on its own start time (the frame its spoken word starts)."""
    out = []
    for s in starts:
        pr = out_quint(ramp(t, s, s + din)); a = pr
        if t_out is not None: a *= vanish(t, t_out, dout)
        out.append((a, color, pr))
    return out

# ---------- shapes ----------
def paint(color, a=1.0, blur=0.0, stroke=0.0, blend=None, cap=True):
    p = skia.Paint(AntiAlias=True, Color=col(color, a))
    if stroke > 0:
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke)
        if cap: p.setStrokeCap(skia.Paint.kRound_Cap); p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur > 0.05: p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if blend is not None: p.setBlendMode(blend)
    return p

def glow(c, x, y, r, color, a=1.0, blend=skia.BlendMode.kPlus, sx=1.0, sy=1.0):
    """Soft radial light (additive by default)."""
    if a <= 0.003 or r <= 0: return
    sh = skia.GradientShader.MakeRadial((0, 0), 1.0,
            [col(color, a), col(color, a * 0.42), col(color, a * 0.12), col(color, 0)], [0, 0.35, 0.7, 1.0])
    p = skia.Paint(AntiAlias=True, Shader=sh); p.setBlendMode(blend)
    c.save(); c.translate(x, y); c.scale(r * sx, r * sy); c.drawRect(skia.Rect.MakeLTRB(-1, -1, 1, 1), p); c.restore()

def linear(c, rect, p0, p1, colors, stops=None, blend=None):
    sh = skia.GradientShader.MakeLinear([p0, p1], colors, stops)
    p = skia.Paint(AntiAlias=True, Shader=sh)
    if blend is not None: p.setBlendMode(blend)
    c.drawRect(rect, p)

def vignette(c, W, H, a=0.85, inner=0.35):
    sh = skia.GradientShader.MakeRadial((W / 2, H / 2), math.hypot(W, H) / 2,
            [col((0, 0, 0), 0), col((0, 0, 0), 0), col((0, 0, 0), a)], [0, inner, 1.0])
    c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Shader=sh))

def rrect(c, x, y, w, h, r, p): c.drawRoundRect(skia.Rect.MakeXYWH(x, y, w, h), r, r, p)

def path_from(points, closed=True):
    p = skia.Path(); p.moveTo(*points[0])
    for q in points[1:]: p.lineTo(*q)
    if closed: p.close()
    return p

def person_path(cx, base_y, h, kind="plain", lean=0.0):
    """A defocus-friendly standing figure: no features, only an outline. h = full height."""
    u = h / 8.0                       # one head
    hw = 0.5 * u
    sh = {"plain": 1.05, "tank": 1.0, "suit": 1.18, "hat": 1.05, "kid": 0.9}[kind] * u
    top = base_y - h
    p = skia.Path()
    p.addOval(skia.Rect.MakeLTRB(cx - hw * 0.92 + lean, top, cx + hw * 0.92 + lean, top + u * 1.12))
    b = skia.Path()
    ny = top + u * 1.02; sy = top + u * 1.5; wy = top + u * 3.9; hy = top + u * 4.3
    b.moveTo(cx - hw * 0.42 + lean, ny)
    b.cubicTo(cx - hw * 0.5 + lean, sy - u * 0.2, cx - sh * 0.7, sy - u * 0.12, cx - sh, sy + u * 0.12)
    b.cubicTo(cx - sh * 1.12, sy + u * 0.9, cx - sh * 1.1, wy - u * 0.6, cx - sh * 0.98, hy + u * 0.3)   # arm outer
    b.lineTo(cx - sh * 0.72, hy + u * 0.3)
    b.lineTo(cx - sh * 0.66, base_y - u * 0.1); b.lineTo(cx - u * 0.06, base_y - u * 0.1)          # left leg
    b.lineTo(cx, hy + u * 0.5)
    b.lineTo(cx + u * 0.06, base_y - u * 0.1); b.lineTo(cx + sh * 0.66, base_y - u * 0.1)          # right leg
    b.lineTo(cx + sh * 0.72, hy + u * 0.3); b.lineTo(cx + sh * 0.98, hy + u * 0.3)
    b.cubicTo(cx + sh * 1.1, wy - u * 0.6, cx + sh * 1.12, sy + u * 0.9, cx + sh, sy + u * 0.12)
    b.cubicTo(cx + sh * 0.7, sy - u * 0.12, cx + hw * 0.5 + lean, sy - u * 0.2, cx + hw * 0.42 + lean, ny)
    b.close(); p.addPath(b)
    if kind == "hat":
        p.addOval(skia.Rect.MakeLTRB(cx - u * 1.25 + lean, top + u * 0.12, cx + u * 1.25 + lean, top + u * 0.42))
        p.addRoundRect(skia.Rect.MakeLTRB(cx - hw * 0.95 + lean, top - u * 0.28, cx + hw * 0.95 + lean, top + u * 0.3), u * 0.2, u * 0.2)
    if kind == "suit":
        p.addRoundRect(skia.Rect.MakeXYWH(cx + sh * 0.92, hy + u * 0.35, u * 1.25, u * 0.85), u * 0.08, u * 0.08)   # briefcase
        p.addRect(skia.Rect.MakeXYWH(cx + sh * 1.3, hy + u * 0.18, u * 0.5, u * 0.2))
    return p

def bust_path(cx, base_y, w, kind="plain"):
    """Head and shoulders from behind (seated viewer). w = shoulder width."""
    r = w * 0.2; p = skia.Path()
    hy = base_y - w * 0.66
    p.addOval(skia.Rect.MakeLTRB(cx - r * 0.95, hy - r * 1.15, cx + r * 0.95, hy + r * 1.1))
    b = skia.Path(); b.moveTo(cx - r * 0.55, hy + r * 0.8)
    b.cubicTo(cx - r * 0.6, hy + r * 1.6, cx - w * 0.5, hy + r * 1.5, cx - w * 0.5, base_y)
    b.lineTo(cx + w * 0.5, base_y)
    b.cubicTo(cx + w * 0.5, hy + r * 1.5, cx + r * 0.6, hy + r * 1.6, cx + r * 0.55, hy + r * 0.8); b.close()
    p.addPath(b)
    if kind == "hat":
        p.addOval(skia.Rect.MakeLTRB(cx - r * 2.1, hy - r * 0.75, cx + r * 2.1, hy - r * 0.3))
    return p

# ---------- grain ----------
class Grain:
    def __init__(self, W, H, n=8, seed=7):
        rng = np.random.default_rng(seed); self.tiles = []; self.W, self.H = W, H
        s = 640
        for _ in range(n):
            g = rng.normal(128, 46, (s, s)).clip(0, 255).astype(np.uint8)
            rgba = np.dstack([g, g, g, np.full_like(g, 255)])
            self.tiles.append(skia.Image.fromarray(np.ascontiguousarray(rgba)))
    def draw(self, c, frame, a_overlay=0.11, a_lift=0.045):
        rng = random.Random(frame // 2)          # new grain every 2 frames (30 Hz), like film
        im = self.tiles[rng.randrange(len(self.tiles))]
        m = skia.Matrix(); m.setTranslate(rng.randrange(640), rng.randrange(640))
        sh = im.makeShader(skia.TileMode.kRepeat, skia.TileMode.kRepeat, skia.SamplingOptions(), m)
        r = skia.Rect.MakeWH(self.W, self.H)
        p = skia.Paint(Shader=sh); p.setBlendMode(skia.BlendMode.kOverlay); p.setAlphaf(a_overlay); c.drawRect(r, p)
        p = skia.Paint(Shader=sh); p.setBlendMode(skia.BlendMode.kScreen); p.setAlphaf(a_lift); c.drawRect(r, p)
